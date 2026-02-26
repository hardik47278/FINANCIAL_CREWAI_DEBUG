from fastapi import FastAPI, File, UploadFile, Form, HTTPException
import os
import uuid
import celery_app

from celery.result import AsyncResult
from celery_app import celery_app
from job import run_financial_analysis  # Celery task

from database import (
    init_db,
    get_db_session,
    create_job,
    get_job,
    update_job,
    list_jobs,
)

app = FastAPI(title="Financial Document Analyzer")

# create SQLite tables
init_db()


@app.get("/")
async def root():
    return {"message": "Financial Document Analyzer API is running"}


@app.post("/analyze")
async def analyze_financial_document_api(
    file: UploadFile = File(...),
    query: str = Form(default="Analyze this financial document for investment insights"),
):
    file_id = str(uuid.uuid4())
    os.makedirs("data", exist_ok=True)
    file_path = f"data/financial_document_{file_id}.pdf"

    db = get_db_session()
    try:
        # Save uploaded file (keep it until Celery finishes)
        with open(file_path, "wb") as f:
            f.write(await file.read())

        query = (query or "Analyze this financial document for investment insights").strip()

        task = run_financial_analysis.delay(query, file_path)  # enqueue Celery task

        # Save job record to SQLite
        create_job(db, job_id=task.id, query=query, filename=file.filename)

        return {
            "status": "queued",
            "task_id": task.id,
            "query": query,
            "file_processed": file.filename,
        }

    except Exception as e:
        # cleanup file if enqueue fails
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Failed to enqueue task: {str(e)}")

    finally:
        db.close()


@app.get("/result/{task_id}")
def get_result(task_id: str):
    db = get_db_session()
    try:
        res = AsyncResult(task_id, app=celery_app)

        status_map = {
            "PENDING": "queued",
            "RECEIVED": "queued",
            "STARTED": "running",
            "SUCCESS": "finished",
            "FAILURE": "failed",
            "RETRY": "retrying",
            "REVOKED": "revoked",
        }
        status = status_map.get(res.status, str(res.status).lower())

        # Update DB record if exists
        job_row = get_job(db, task_id)

        result_text = None
        error_text = None

        if res.successful():
            result_text = res.result  # ✅ CHANGED (removed str())
            update_job(db, task_id, status="finished", result=str(result_text))  # keep DB as text (unchanged behavior)
        elif res.failed():
            error_text = str(res.result)
            update_job(db, task_id, status="failed", error=error_text)
        else:
            # keep status updated while running/queued
            if status in ("queued", "running", "retrying", "revoked"):
                update_job(db, task_id, status=status)

        return {
            "task_id": task_id,
            "status": status,
            "result": result_text if res.successful() else None,
            "error": error_text if res.failed() else None,
        }

    finally:
        db.close()


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
                "updated_at": r.updated_at.isoformat() if r.updated_at else None,
            }
            for r in rows
        ]
    finally:
        db.close()


@app.get("/debug")
def debug():
    import main
    return {
        "main_file": main.file,
        "cwd": os.getcwd(),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
