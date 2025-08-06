from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.services.reminder_scheduler import reminder_scheduler
import logging

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting application...")
    try:
        reminder_scheduler.start()
        logger.info("Reminder scheduler started with application")
    except Exception as e:
        logger.error(f"Failed to start reminder scheduler: {str(e)}")
    
    yield 
    
    # Shutdown
    logger.info("Shutting down application...")
    try:
        reminder_scheduler.stop()
        logger.info("Reminder scheduler stopped with application")
    except Exception as e:
        logger.error(f"Error stopping reminder scheduler: {str(e)}")
