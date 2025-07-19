from pydantic import BaseModel, Field
from typing import Optional, List
import datetime

class AppointmentBase(BaseModel):
    """Base schema for appointment details."""
    name: str = Field(..., example="Consultation", description="Appointment name")
    date: datetime.date = Field(..., example="2025-07-03", description="Appointment date (YYYY-MM-DD)")
    time: datetime.time = Field(..., example="14:30:00", description="Appointment time (HH:MM:SS)")
    notes: Optional[str] = Field(None, example="Eat healthy", description="Additional notes (optional)")

class AppointmentCreate(AppointmentBase):
    """Schema for creating a new appointment."""
    user_id: int = Field(..., example=1, description="User ID for the appointment")
    doctor_id: int = Field(..., example=1, description="Doctor ID for the appointment")

class AppointmentUpdate(BaseModel):
    """Schema for updating an appointment (partial update)."""
    name: Optional[str] = Field(None, example="Consultation", description="Appointment name (optional)")
    date: Optional[datetime.date] = Field(None, example="2025-07-03", description="Appointment date (optional)")
    time: Optional[datetime.time] = Field(None, example="14:30:00", description="Appointment time (optional)")
    notes: Optional[str] = Field(None, example="Eat healthy", description="Additional notes (optional)")
    user_id: Optional[int] = Field(None, example=1, description="User ID (optional)")
    doctor_id: Optional[int] = Field(None, example=1, description="Doctor ID (optional)")

class AppointmentResponse(AppointmentBase):
    """Schema for returning appointment data to the client."""
    id: int = Field(..., example=1, description="Unique appointment ID")
    user_id: int = Field(..., example=1, description="User ID for the appointment")
    doctor_id: int = Field(..., example=1, description="Doctor ID for the appointment")
    medicines: Optional[List[int]] = Field(None, description="List of medicine IDs for this appointment (optional)")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Consultation",
                "date": "2025-07-03",
                "time": "14:30:00",
                "notes": "Eat healthy",
                "user_id": 1,
                "doctor_id": 2,
                "medicines": [10, 11]
            }
        }
