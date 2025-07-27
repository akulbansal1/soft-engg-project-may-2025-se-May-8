from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime, timedelta
from src.models.reminder import Reminder, ReminderType, ReminderStatus
from src.models.appointment import Appointment
from src.models.medicine import Medicine
from src.schemas.reminder import ReminderCreate, ReminderUpdate

class ReminderService:
    """Service class for Reminder CRUD operations and scheduling."""

    @staticmethod
    def create_reminder(db: Session, reminder_in: ReminderCreate) -> Reminder:
        """Create a new reminder record."""
        reminder = Reminder(**reminder_in.model_dump())
        db.add(reminder)
        db.commit()
        db.refresh(reminder)
        return reminder

    @staticmethod
    def get_reminder(db: Session, reminder_id: int) -> Optional[Reminder]:
        """Get a reminder by ID."""
        return db.query(Reminder).filter(Reminder.id == reminder_id).first()

    @staticmethod
    def get_reminders_by_user(db: Session, user_id: int, include_inactive: bool = False) -> List[Reminder]:
        """Get all reminders for a user."""
        query = db.query(Reminder).filter(Reminder.user_id == user_id)
        if not include_inactive:
            query = query.filter(Reminder.is_active == True)
        return query.order_by(Reminder.scheduled_time.desc()).all()

    @staticmethod
    def get_pending_reminders_by_user(db: Session, user_id: int) -> List[Reminder]:
        """Get all pending reminders for a user."""
        return db.query(Reminder).filter(
            Reminder.user_id == user_id,
            Reminder.status == ReminderStatus.PENDING,
            Reminder.is_active == True
        ).order_by(Reminder.scheduled_time.asc()).all()

    @staticmethod
    def get_due_reminders(db: Session, limit: int = 100) -> List[Reminder]:
        """Get all reminders that are due (scheduled time has passed and status is pending)."""
        current_time = datetime.utcnow()
        return db.query(Reminder).filter(
            Reminder.scheduled_time <= current_time,
            Reminder.status == ReminderStatus.PENDING,
            Reminder.is_active == True
        ).order_by(Reminder.scheduled_time.asc()).limit(limit).all()

    @staticmethod
    def get_upcoming_reminders(db: Session, user_id: int, hours_ahead: int = 24) -> List[Reminder]:
        """Get reminders scheduled within the next X hours for a user."""
        current_time = datetime.utcnow()
        future_time = current_time + timedelta(hours=hours_ahead)
        
        return db.query(Reminder).filter(
            Reminder.user_id == user_id,
            Reminder.scheduled_time.between(current_time, future_time),
            Reminder.status == ReminderStatus.PENDING,
            Reminder.is_active == True
        ).order_by(Reminder.scheduled_time.asc()).all()

    @staticmethod
    def update_reminder(db: Session, reminder_id: int, reminder_in: ReminderUpdate) -> Optional[Reminder]:
        """Update a reminder record."""
        reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
        if not reminder:
            return None
        
        for field, value in reminder_in.model_dump(exclude_unset=True).items():
            setattr(reminder, field, value)
        
        reminder.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(reminder)
        return reminder

    @staticmethod
    def delete_reminder(db: Session, reminder_id: int) -> bool:
        """Delete a reminder record."""
        reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
        if not reminder:
            return False
        db.delete(reminder)
        db.commit()
        return True

    @staticmethod
    def mark_reminder_as_sent(db: Session, reminder_id: int) -> Optional[Reminder]:
        """Mark a reminder as sent."""
        reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
        if not reminder:
            return None
        
        reminder.status = ReminderStatus.SENT
        reminder.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(reminder)
        return reminder

    @staticmethod
    def mark_reminder_as_failed(db: Session, reminder_id: int) -> Optional[Reminder]:
        """Mark a reminder as failed."""
        reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
        if not reminder:
            return None
        
        reminder.status = ReminderStatus.FAILED
        reminder.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(reminder)
        return reminder

    @staticmethod
    def cancel_reminder(db: Session, reminder_id: int) -> Optional[Reminder]:
        """Cancel a reminder."""
        reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
        if not reminder:
            return None
        
        reminder.status = ReminderStatus.CANCELLED
        reminder.is_active = False
        reminder.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(reminder)
        return reminder

    @staticmethod
    def create_appointment_reminder(
        db: Session, 
        appointment_id: int, 
        reminder_time: datetime,
        custom_message: Optional[str] = None
    ) -> Optional[Reminder]:
        """Create a reminder for an appointment."""
        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appointment:
            return None
        
        title = f"Appointment Reminder: {appointment.name}"
        message = custom_message or f"You have an appointment '{appointment.name}' scheduled for {appointment.date} at {appointment.time}"
        
        reminder_data = ReminderCreate(
            user_id=appointment.user_id,
            reminder_type=ReminderType.APPOINTMENT,
            related_id=appointment_id,
            title=title,
            message=message,
            scheduled_time=reminder_time
        )
        
        return ReminderService.create_reminder(db, reminder_data)

    @staticmethod
    def create_medicine_reminder(
        db: Session, 
        medicine_id: int, 
        reminder_time: datetime,
        custom_message: Optional[str] = None
    ) -> Optional[Reminder]:
        """Create a reminder for medicine."""
        medicine = db.query(Medicine).filter(Medicine.id == medicine_id).first()
        if not medicine:
            return None
        
        title = f"Medicine Reminder: {medicine.name}"
        message = custom_message or f"Time to take your medicine '{medicine.name}' - Dosage: {medicine.dosage}, Frequency: {medicine.frequency}"
        
        reminder_data = ReminderCreate(
            user_id=medicine.user_id,
            reminder_type=ReminderType.MEDICINE,
            related_id=medicine_id,
            title=title,
            message=message,
            scheduled_time=reminder_time
        )
        
        return ReminderService.create_reminder(db, reminder_data)

    @staticmethod
    def auto_create_appointment_reminders(
        db: Session, 
        appointment_id: int, 
        reminder_offsets: List[timedelta] = None
    ) -> List[Reminder]:
        """Automatically create multiple reminders for an appointment."""
        if reminder_offsets is None:
            # Default: remind 48 hours, 2 hour, and 30 minutes before
            reminder_offsets = [
                timedelta(hours=48),
                timedelta(hours=2),
                timedelta(minutes=30)
            ]
        
        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appointment:
            return []
        
        # Combine appointment date and time
        appointment_datetime = datetime.combine(appointment.date, appointment.time)
        
        reminders = []
        for offset in reminder_offsets:
            reminder_time = appointment_datetime - offset
            # Only create reminder if it's in the future
            if reminder_time > datetime.now():
                reminder = ReminderService.create_appointment_reminder(
                    db, appointment_id, reminder_time
                )
                if reminder:
                    reminders.append(reminder)
        
        return reminders

    @staticmethod
    def auto_create_medicine_reminders(
        db: Session, 
        medicine_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Reminder]:
        """Automatically create reminders for medicine based on frequency."""
        medicine = db.query(Medicine).filter(Medicine.id == medicine_id).first()
        if not medicine:
            return []

        ## TODO: Implement frequency parsing using genAI
     
        # Parse frequency to determine how often to remind
        # This is a simplified implementation - you might want to make this more sophisticated
        frequency_map = {
            "once daily": timedelta(days=1),
            "twice daily": timedelta(hours=12),
            "three times daily": timedelta(hours=8),
            "four times daily": timedelta(hours=6),
            "every 8 hours": timedelta(hours=8),
            "every 12 hours": timedelta(hours=12),
            "weekly": timedelta(days=7),
        }
        
        frequency_lower = medicine.frequency.lower()
        reminder_interval = None
        
        for key, interval in frequency_map.items():
            if key in frequency_lower:
                reminder_interval = interval
                break
        
        if not reminder_interval:
            # Default to daily if frequency not recognized
            reminder_interval = timedelta(days=1)
        
        # Use provided dates or medicine dates
        start = start_date or datetime.combine(medicine.start_date, datetime.min.time())
        end = end_date or (datetime.combine(medicine.end_date, datetime.max.time()) if medicine.end_date else start + timedelta(days=30))
        
        reminders = []
        current_time = start
        
        # Limit to prevent creating too many reminders
        max_reminders = 100
        count = 0
        
        while current_time <= end and count < max_reminders:
            if current_time > datetime.now():  # Only create future reminders
                reminder = ReminderService.create_medicine_reminder(
                    db, medicine_id, current_time
                )
                if reminder:
                    reminders.append(reminder)
            
            current_time += reminder_interval
            count += 1
        
        return reminders
