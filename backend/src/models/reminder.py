from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Enum, Boolean
from sqlalchemy.orm import relationship
from src.db.database import Base
import enum
from datetime import datetime

class ReminderType(enum.Enum):
    """Enum for reminder types."""
    APPOINTMENT = "appointment"
    MEDICINE = "medicine"

class ReminderStatus(enum.Enum):
    """Enum for reminder status."""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Reminder(Base):
    """
    Reminder Model
    Fields: id, user_id, reminder_type, related_id, title, message, 
            scheduled_time, status, created_at, updated_at, is_active
    """
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    reminder_type = Column(Enum(ReminderType), nullable=False, index=True)
    related_id = Column(Integer, nullable=False, index=True)  # appointment_id or medicine_id
    title = Column(String, nullable=False)
    message = Column(Text, nullable=True)
    scheduled_time = Column(DateTime, nullable=False, index=True)
    status = Column(Enum(ReminderStatus), default=ReminderStatus.PENDING, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False, index=True)

    # Relationships
    user = relationship("User", backref="reminders")

    def __repr__(self):
        return f"<Reminder(id={self.id}, user_id={self.user_id}, type={self.reminder_type.value}, status={self.status.value})>"
