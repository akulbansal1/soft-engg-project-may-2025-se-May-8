from pydantic import BaseModel, Field
from typing import Optional
import datetime
from enum import Enum

class ReminderType(str, Enum):
    """Enum for reminder types."""
    APPOINTMENT = "appointment"
    MEDICINE = "medicine"

class ReminderStatus(str, Enum):
    """Enum for reminder status."""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ReminderBase(BaseModel):
    """Base schema for reminder details."""
    reminder_type: ReminderType = Field(..., example="appointment", description="Type of reminder (appointment or medicine)")
    related_id: int = Field(..., example=1, description="ID of the related appointment or medicine")
    title: str = Field(..., example="Appointment Reminder", description="Reminder title")
    message: Optional[str] = Field(None, example="You have an appointment with Dr. Smith at 2:00 PM", description="Reminder message")
    scheduled_time: datetime.datetime = Field(..., example="2025-07-27T14:00:00", description="When the reminder should be sent")

class ReminderCreate(ReminderBase):
    """Schema for creating a new reminder."""
    user_id: int = Field(..., example=1, description="User ID for the reminder")

class ReminderUpdate(BaseModel):
    """Schema for updating a reminder (partial update)."""
    title: Optional[str] = Field(None, example="Updated Reminder", description="Reminder title (optional)")
    message: Optional[str] = Field(None, example="Updated message", description="Reminder message (optional)")
    scheduled_time: Optional[datetime.datetime] = Field(None, example="2025-07-27T15:00:00", description="Scheduled time (optional)")
    status: Optional[ReminderStatus] = Field(None, example="sent", description="Reminder status (optional)")
    is_active: Optional[bool] = Field(None, example=True, description="Whether reminder is active (optional)")

class ReminderResponse(ReminderBase):
    """Schema for returning reminder data to the client."""
    id: int = Field(..., example=1, description="Unique reminder ID")
    user_id: int = Field(..., example=1, description="User ID for the reminder")
    status: ReminderStatus = Field(..., example="pending", description="Current status of the reminder")
    created_at: datetime.datetime = Field(..., example="2025-07-27T12:00:00", description="When the reminder was created")
    updated_at: datetime.datetime = Field(..., example="2025-07-27T12:00:00", description="When the reminder was last updated")
    is_active: bool = Field(..., example=True, description="Whether the reminder is active")

    class Config:
        from_attributes = True

class ReminderListResponse(BaseModel):
    """Schema for returning a list of reminders."""
    reminders: list[ReminderResponse]
    total: int = Field(..., example=10, description="Total number of reminders")
    
class DueRemindersResponse(BaseModel):
    """Schema for returning due reminders."""
    due_reminders: list[ReminderResponse]
    count: int = Field(..., example=5, description="Number of due reminders")
