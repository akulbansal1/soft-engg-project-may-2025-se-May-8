"""
FastAPI Backend Celery Worker

This file is used to start Celery workers and beat scheduler.

Usage:
    # Start worker
    celery -A celery_worker worker --loglevel=info

    # Start beat scheduler
    celery -A celery_worker beat --loglevel=info
"""

from src.core.celery_app import celery_app

if __name__ == "__main__":
    celery_app.start()
