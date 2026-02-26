from fastapi import FastAPI, File, UploadFile, Form, HTTPException
import os
import uuid

from database import init_db, get_db_session, create_job, update_job, get_job, list_jobs

from crewai import Crew, Process
from agent import financial_analyst, verifier, investment_advisor, risk_assessor
from task import (
    analyze_financial_document,
    investment_analysis,
    risk_assessment,
    verification,
)

app = FastAPI(title="Financial Document Analyzer")
init_db()


@app.get("/")
async def root():
    return {"message": "Financial Document Analyzer API is running"}


@app.post("/analyze")
async def analyze(
    file: UploadFile = File(...),
    query: str = Form(default="Analyze this financial document for investment insights"),
):
    file_id = str(uuid.uuid4())
    os.makedirs("data", exist_ok=True)
    file_path = f"data/financial_document_{file_id}.pdf"

    db = get_db_session()
    task_id = str(uuid.uuid4())

    try:
        with open(file_path, "wb") as f:
            f.write(await file.read())

        query = (query or "Analyze this financial document for investment insights").strip()
        create_job(db, job_id=task_id, query=query, filename=file.filename)
        update_job(db, task_id, status="running")

        # ✅ Run directly — no threading, no Celery
        financial_crew = Crew(
            agents=[financial_analyst, verifier, investment_advisor, risk_assessor],
            tasks=[
                analyze_financial_document,
                verification,
                investment_analysis,
                risk_assessment,
            ],
            process=Process.sequential,
            verbose=True,
        )

        financial_crew.kickoff({"query": query, "path": file_path})

        result = {
            "verification": getattr(verification.output, "raw", None),
            "analysis": getattr(analyze_financial_document.output, "raw", None),
            "investment_analysis": getattr(investment_analysis.output, "raw", None),
            "risk_assessment": getattr(risk_assessment.output, "raw", None),
            "market_insights": getattr(analyze_financial_document.output, "raw", None),
        }

        update_job(db, task_id, status="finished", result=str(result))

        return {
            "task_id": task_id,
            "status": "finished",
            "result": result,
        }

    except Exception as e:
        update_job(db, task_id, status="failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        db.close()
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass


@app.get("/history")
def history(limit: int = 20):
    db = get_db_session()
    try:
        rows = list_jobs(db, limit=limit)
        return [
            {
                "task_id": r.job_id,
                "filename": r.filename,
                "query": r.query,
                "status": r.status,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in rows
        ]
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
