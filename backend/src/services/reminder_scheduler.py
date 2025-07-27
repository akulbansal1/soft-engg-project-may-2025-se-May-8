import time
import threading
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from src.db.database import get_db
from src.services.reminder_service import ReminderService
from src.services.sms_service import sms_service
from src.models.reminder import Reminder
from src.core.config import settings
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('reminder_scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ReminderScheduler:
    def __init__(self) -> None:
        self.running: bool = False
        self.thread: Optional[threading.Thread] = None
    
    def send_notification(self, reminder: Reminder) -> bool:
        try:
            user_phone: Optional[str] = reminder.user.phone if reminder.user else None
            
            if not user_phone:
                logger.error(f"No phone number for reminder {reminder.id}")
                return False
                
            result: Dict[str, Any] = sms_service.send_reminder_sms(user_phone, reminder.message)
            
            if result.get('success'):
                logger.info(f"SMS sent successfully for reminder {reminder.id}")
                return True
            else:
                logger.error(f"Failed to send SMS for reminder {reminder.id}: {result.get('message')}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending notification for reminder {reminder.id}: {str(e)}")
            return False
    
    def process_due_reminders(self) -> None:
        logger.info("Checking for due reminders...")
        
        db_gen = get_db()
        db: Session = next(db_gen)
        
        try:
            due_reminders = ReminderService.get_due_reminders(db, limit=100)
            
            if not due_reminders:
                logger.debug("No due reminders found")
                return
                
            logger.info(f"Found {len(due_reminders)} due reminders")
            
            for reminder in due_reminders:
                try:
                    logger.info(f"Processing reminder {reminder.id} for user {reminder.user_id}")
                    
                    if self.send_notification(reminder):
                        ReminderService.mark_reminder_as_sent(db, reminder.id)
                        logger.info(f"Reminder {reminder.id} marked as sent")
                    else:
                        ReminderService.mark_reminder_as_failed(db, reminder.id)
                        logger.error(f"Reminder {reminder.id} marked as failed")
                        
                except Exception as e:
                    logger.error(f"Error processing reminder {reminder.id}: {str(e)}")
                    ReminderService.mark_reminder_as_failed(db, reminder.id)
        
        except Exception as e:
            logger.error(f"Error in reminder processing: {str(e)}")
        finally:
            db.close()
    
    def cleanup_old_reminders(self) -> None:
        logger.info("Running reminder cleanup...")
        
        db_gen = get_db()
        db: Session = next(db_gen)
        
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=settings.REMINDER_CLEANUP_DAYS)
            logger.info(f"Would clean up reminders older than {cutoff_date}")
            
        except Exception as e:
            logger.error(f"Error in reminder cleanup: {str(e)}")
        finally:
            db.close()
    
    def start(self) -> None:
        if self.running:
            logger.warning("Scheduler is already running")
            return
        
        logger.info("Starting reminder scheduler...")
        
        self.running = True
        
        def run_scheduler() -> None:
            last_cleanup = datetime.utcnow()
            check_interval_seconds = settings.REMINDER_CHECK_INTERVAL_MINUTES * 60
            
            while self.running:
                try:
                    self.process_due_reminders()
                    
                    now = datetime.utcnow()
                    if (now - last_cleanup).days >= 1 and now.hour == settings.REMINDER_CLEANUP_HOUR:
                        self.cleanup_old_reminders()
                        last_cleanup = now
                    
                except Exception as e:
                    logger.error(f"Error in scheduler loop: {str(e)}")
                
                for _ in range(check_interval_seconds):
                    if not self.running:
                        break
                    time.sleep(1)
        
        self.thread = threading.Thread(target=run_scheduler)
        self.thread.daemon = True
        self.thread.start()
        
        logger.info("Reminder scheduler started successfully")
    
    def stop(self) -> None:
        if not self.running:
            logger.warning("Scheduler is not running")
            return
        
        logger.info("Stopping reminder scheduler...")
        self.running = False
        
        if self.thread:
            self.thread.join(timeout=10)
        
        logger.info("Reminder scheduler stopped")

reminder_scheduler = ReminderScheduler()

def start_reminder_scheduler() -> None:
    reminder_scheduler.start()

def stop_reminder_scheduler() -> None:
    reminder_scheduler.stop()

if __name__ == "__main__":
    try:
        reminder_scheduler.start()
        logger.info("Reminder scheduler service started. Press Ctrl+C to stop.")
        
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Shutdown signal received")
        reminder_scheduler.stop()
        logger.info("Reminder scheduler service stopped")
