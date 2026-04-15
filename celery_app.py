from celery import Celery
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "financial_analyzer",
    broker=REDIS_URL,#celery sends task to redis  ## fastapi - send task->redis quene ->celery worker picks up
    backend=REDIS_URL,#stores task
    include=["job"],   # load from job.py 
)
