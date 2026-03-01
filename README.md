# 🚀 Financial Document Analyzer  

## Multi-Agent AI Financial Analysis System  

An asynchronous, production-style financial document analysis system built with **FastAPI, CrewAI, Celery, Redis, and SQLite**.

Upload financial PDFs (earnings reports, quarterly filings, annual reports) and receive structured AI-powered investment insights including:

- 📊 Financial metrics  
- 💼 Investment recommendations  
- ⚠️ Risk analysis  

All generated through a **4-agent CrewAI pipeline running asynchronously**.

---

## 📂 Repository

🔗 GitHub:  
https://github.com/hardik47278/FINANCIAL_CREWAI_DEBUG.git  

---

# 🏗️ Architecture Overview

```
User uploads PDF  
        ↓
FastAPI (main.py)
        ↓
Redis Queue
        ↓
Celery Worker
        ↓
CrewAI 4-Agent Pipeline
        ↓
SQLite Database (analysis.db)
```

---

# ⚙️ How It Works

## 1️⃣ User Upload

- User uploads financial PDF at `http://localhost:8000`
- FastAPI receives request

---

## 2️⃣ Job Creation & Task Queueing

FastAPI:

- Saves file locally  
- Creates job record in SQLite  
- Generates unique `job_id`  
- Pushes task to Redis via `.delay()`  
- Immediately returns `job_id`

✅ Non-blocking API  
✅ Background AI processing  
✅ Scalable architecture  

---

## 3️⃣ Background Processing (Celery Worker)

- Worker pulls task from Redis  
- Updates job status (`queued → running`)  
- Executes CrewAI pipeline  
- Saves final result to SQLite  

---

# 📁 File Structure

| File            | Description                             |
|-----------------|-----------------------------------------|
| `agent.py`      | CrewAI agent definitions                |
| `task.py`       | CrewAI task definitions                 |
| `tools.py`      | Custom CrewAI tools                     |
| `main.py`       | FastAPI app with Celery & Redis         |
| `simplemain.py` | FastAPI app without Celery              |
| `database.py`   | SQLAlchemy database models              |
| `job.py`        | Async job handling                      |
| `celery_app.py` | Celery configuration                    |

---

# 🛠️ Setup & Installation

## 1️⃣ Clone Repository

```bash
git clone https://github.com/hardik47278/FINANCIAL_CREWAI_DEBUG.git
cd FINANCIAL_CREWAI_DEBUG
```

---

## 2️⃣ Create Virtual Environment (Python 3.11 Required)

```bash
python -m venv venv
or 
python -m venv venv311
venv\Scripts\activate
```

---

## 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4️⃣ Set Environment Variables

Create `.env` file:

```
OPENAI_API_KEY=your_api_key_here
```

---

# 🔴 Redis Setup

## Option 1: Using Docker

```bash
docker run -p 6379:6379 redis
```

## Option 2: Install Redis Locally

Install Redis and ensure it runs on port `6379`.

---

# ▶️ Run With Celery

### Start Celery Worker

```bash
celery -A celery_app.celery_app worker --loglevel=info --pool=solo
```

### Start FastAPI Server

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

---

# ▶️ Run Without Celery (Simple Mode)

```bash
uvicorn simplemain:app --host 0.0.0.0 --port 8001 --reload
```

---

# 📊 Run an Analysis

1. Open `http://localhost:8000/docs`  
2. Expand `POST /analyze`  
3. Click **Try it out**  
4. Upload financial PDF  
5. Click **Execute**  
6. Monitor worker logs in terminal  

---

# 🐞 Bugs Found & Fixed

## 🔧 1️⃣ Environment Issues

- Python version conflicts  
- CrewAI compatibility problems  

✅ Fixed by using:

- Python 3.11  
- `crewai==0.130.0`  
- `crewai-tools==0.47.1`  

---

## 🔧 2️⃣ Code & Import Errors

Issues Fixed:

- Incorrect CrewAI imports  
- Wrong agent assignments  
- Tool subclass not extending `BaseTool`  
- Missing LLM initialization  
- Incorrect PDF loader imports  
- Missing context passing between agents  

### Key Fixes

```python
from crewai import Agent, LLM
```

- Converted tools into proper `BaseTool` subclasses  
- Corrected tool instantiation format:

```python
[FinancialDocumentTool()]
```

- Increased `max_iter` for better reasoning depth  
- Fixed task-to-agent mapping  
- Added context passing across tasks  

---

# 🎯 Prompt Engineering Improvements

Original prompts caused hallucinations and inconsistent outputs.

### Improvements Made:

- Forced document-only reasoning  
- Enforced JSON-only responses  
- Required “Not Found” if data missing  
- Structured concise bullet-point outputs  
- Added verification layer for financial keywords  

---

# 💡 Final Result

✔ Production-style async architecture  
✔ Clean separation of API, workers, agents, and database  
✔ Scalable & non-blocking design  
✔ Strong prompt engineering discipline  
✔ Real-world debugging experience  

---

