from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from enum import Enum

class TimeUnit(str, Enum):
    """Enum for time units compatible with timedelta for reminders."""
    DAYS = "days"
    HOURS = "hours"
    MINUTES = "minutes"
    WEEKS = "weeks"

class MedicineBase(BaseModel):
    """Base schema for medicine details."""
    name: str = Field(..., example="Paracetamol", description="Name of the medicine")
    dosage: str = Field(..., example="500mg", description="Dosage information")
    frequency: str = Field(..., example="Once a day after dinner", description="Frequency of intake")
    start_date: date = Field(..., example="2025-06-25", description="Start date of the medicine course")
    end_date: Optional[date] = Field(None, example="2025-07-05", description="End date of the medicine course (optional)")
    notes: Optional[str] = Field(None, example="Take with food", description="Additional notes or instructions (optional)")

class MedicineCreate(MedicineBase):
    """Schema for creating a new medicine record."""
    user_id: int = Field(..., example=1, description="ID of the user taking the medicine")
    doctor_id: Optional[int] = Field(None, example=1, description="ID of the doctor who issued the medicine (optional)")
    appointment_id: Optional[int] = Field(None, example=1, description="ID of the appointment associated with the medicine (optional)")

class MedicineUpdate(BaseModel):
    """Schema for updating a medicine record (partial update)."""
    name: Optional[str] = Field(None, example="Paracetamol", description="Name of the medicine (optional)")
    dosage: Optional[str] = Field(None, example="500mg", description="Dosage information (optional)")
    frequency: Optional[str] = Field(None, example="Once a day after dinner", description="Frequency of intake (optional)")
    start_date: Optional[date] = Field(None, example="2025-06-25", description="Start date (optional)")
    end_date: Optional[date] = Field(None, example="2025-07-05", description="End date (optional)")
    notes: Optional[str] = Field(None, example="Take with food", description="Additional notes (optional)")

class MedicineResponse(MedicineBase):
    """Schema for returning medicine data to the client."""
    id: int = Field(..., example=1, description="Unique medicine ID")
    user_id: int = Field(..., example=1, description="ID of the user taking the medicine")
    doctor_id: Optional[int] = Field(None, example=1, description="ID of the doctor who issued the medicine (optional)")
    appointment_id: Optional[int] = Field(None, example=1, description="ID of the appointment associated (optional)")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Paracetamol",
                "dosage": "500mg",
                "frequency": "Once a day after dinner",
                "start_date": "2025-06-25",
                "end_date": "2025-07-05",
                "notes": "Take with food",
                "user_id": 1,
                "doctor_id": 2,
                "appointment_id": 3
            }
        }
class MedicineTranscriptionResponse(BaseModel):
    """Schema for AI-generated medicine transcription from audio."""
    name: Optional[str] = Field(None, description="Name of the medicine (optional)")
    dosage: Optional[str] = Field(None, description="Dosage information (optional)")
    frequency: Optional[str] = Field(None, description="Frequency of intake (optional)")
    # For constrained generation, Gemini requires datetime, and does not support date directly
    start_date: Optional[datetime] = Field(None, description="Start date of the medicine course (ISO 8601 datetime, optional)")
    end_date: Optional[datetime] = Field(None, description="End date of the medicine course (ISO 8601 datetime, optional)")
    notes: Optional[str] = Field(None, description="Additional notes or instructions (optional)")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Paracetamol",
                "dosage": "500mg",
                "frequency": "Once a day after dinner",
                "start_date": "2025-06-25T08:00:00Z",
                "end_date": "2025-07-05T08:00:00Z",
                "notes": "Take with food"
            }
        }

class FrequencyInterval(BaseModel):
    """Schema for a single time interval in a frequency pattern."""
    unit: TimeUnit = Field(..., description="Time unit for the interval")
    value: int = Field(..., description="Numeric value for the interval")
    
class FrequencyScheduleTime(BaseModel):
    """Schema for a specific time in the schedule."""
    hour: int = Field(..., ge=0, le=23, description="Hour in 24-hour format (0-23)")
    minute: int = Field(..., ge=0, le=59, description="Minute (0-59)")

class FrequencyPatternResponse(BaseModel):
    """Schema for AI-generated frequency pattern from text."""
    interval: FrequencyInterval = Field(..., description="Time interval between doses")
    times_per_interval: List[FrequencyScheduleTime] = Field(..., description="Specific times during each interval")
    
    class Config:
        json_schema_extra = {
            "example": {
                "interval": {"unit": "days", "value": 1},
                "times_per_interval": [
                    {"hour": 9, "minute": 0},
                    {"hour": 21, "minute": 0}
                ]
            }
        }
