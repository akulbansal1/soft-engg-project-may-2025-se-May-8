from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime, timedelta, time
from src.models.reminder import Reminder, ReminderType, ReminderStatus
from src.models.appointment import Appointment
from src.models.medicine import Medicine
from src.schemas.reminder import ReminderCreate, ReminderUpdate
from src.services.ai_service import AIService

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
        current_time = datetime.now()
        return db.query(Reminder).filter(
            Reminder.scheduled_time <= current_time,
            Reminder.status == ReminderStatus.PENDING,
            Reminder.is_active == True
        ).order_by(Reminder.scheduled_time.asc()).limit(limit).all()

    @staticmethod
    def get_upcoming_reminders(db: Session, user_id: int, hours_ahead: int = 24) -> List[Reminder]:
        """Get reminders scheduled within the next X hours for a user."""
        current_time = datetime.now()
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
        
        reminder.updated_at = datetime.now()
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
        reminder.updated_at = datetime.now()
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
        reminder.updated_at = datetime.now()
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
        reminder.updated_at = datetime.now()
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
        
        appointment_datetime = datetime.combine(appointment.date, appointment.time)
        
        reminders = []
        for offset in reminder_offsets:
            reminder_time = appointment_datetime - offset
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
        medicine: Medicine,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Reminder]:
        """Automatically create reminders for medicine based on frequency."""
        if not medicine:
            return []

        frequency_patterns = {
            "once daily": {
                "interval": timedelta(days=1),
                "times_per_day": [time(9, 0)]  # 9:00 AM
            },
            "twice daily": {
                "interval": timedelta(days=1),
                "times_per_day": [time(9, 0), time(21, 0)]  # 9 AM, 9 PM
            },
            "three times daily": {
                "interval": timedelta(days=1),
                "times_per_day": [time(8, 0), time(14, 0), time(20, 0)]  # 8 AM, 2 PM, 8 PM
            },
            "four times daily": {
                "interval": timedelta(days=1),
                "times_per_day": [time(8, 0), time(13, 0), time(18, 0), time(22, 0)]  # 8 AM, 1 PM, 6 PM, 10 PM
            },
            "every 8 hours": {
                "interval": timedelta(hours=8),
                "times_per_day": [time(8, 0), time(16, 0), time(0, 0)]  # 8 AM, 4 PM, midnight
            },
            "every 12 hours": {
                "interval": timedelta(days=1),
                "times_per_day": [time(9, 0), time(21, 0)]  # 9 AM, 9 PM
            },
            "weekly": {
                "interval": timedelta(days=7),
                "times_per_day": [time(10, 0)]  # 10:00 AM once a week
            },
        }
        
        frequency_lower = medicine.frequency.lower()
        pattern = None
        
        for key, freq_pattern in frequency_patterns.items():
            if key in frequency_lower:
                pattern = freq_pattern
                break
        
        # If no pattern matched, try AI parsing
        if not pattern:
            try:
                ai_result = AIService.parse_medicine_frequency(medicine)
                if ai_result and 'interval' in ai_result and 'times_per_interval' in ai_result:
                    interval_data = ai_result['interval']
                    times_data = ai_result['times_per_interval']
                    unit = interval_data['unit']
                    value = interval_data['value']
                    
                    # Create timedelta using dynamic kwargs - all units forced to be timedelta-compatible
                    interval_kwargs = {unit: value}
                    interval = timedelta(**interval_kwargs)
                    
                    times_per_day = []
                    for time_data in times_data:
                        times_per_day.append(time(time_data['hour'], time_data['minute']))
                    
                    pattern = {
                        "interval": interval,
                        "times_per_day": times_per_day
                    }
            except Exception as e:
                # Log error but continue with fallback
                print(f"AI frequency parsing failed: {e}")

        # Final fallback if both rule-based and AI parsing failed
        if not pattern:
            pattern = {
                "interval": timedelta(days=1),
                "times_per_day": [time(9, 0)]
            }
        
        start_date_only = start_date.date() if start_date else medicine.start_date
        end_date_only = end_date.date() if end_date else (medicine.end_date if medicine.end_date else start_date_only + timedelta(days=30))
        
        reminders = []
        current_date = start_date_only
        max_reminders = 200  
        count = 0
        
        while current_date <= end_date_only and count < max_reminders:
            for reminder_time in pattern["times_per_day"]:
                reminder_datetime = datetime.combine(current_date, reminder_time)
                
                if reminder_datetime > datetime.now():
                    reminder = ReminderService.create_medicine_reminder(
                        db, medicine.id, reminder_datetime
                    )
                    if reminder:
                        reminders.append(reminder)
                        count += 1
            
            if pattern["interval"].days >= 1:
                current_date += timedelta(days=pattern["interval"].days)
            else:
                current_date += timedelta(days=1)
        
        return reminders