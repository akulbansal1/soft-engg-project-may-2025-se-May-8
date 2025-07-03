from pydantic import BaseModel, Field
from typing import Optional, List
import datetime

class AppointmentBase(BaseModel):
    name: str = Field(..., example="Consultation", description="Appointment name")
    date: datetime.date = Field(..., example="2025-07-03", description="Appointment date")
    time: datetime.time = Field(..., example="14:30:00", description="Appointment time")
    notes: Optional[str] = Field(None, example="Eat healthy", description="Additional notes")

class AppointmentCreate(AppointmentBase):
    user_id: int = Field(..., example=1, description="User ID")
    doctor_id: int = Field(..., example=1, description="Doctor ID")

class AppointmentUpdate(BaseModel):
    name: Optional[str] = Field(None, example="Consultation")
    date: Optional[datetime.date] = Field(None, example="2025-07-03")
    time: Optional[datetime.time] = Field(None, example="14:30:00")
    notes: Optional[str] = Field(None, example="Eat healthy")
    user_id: Optional[int] = Field(None, example=1)
    doctor_id: Optional[int] = Field(None, example=1)

class AppointmentResponse(AppointmentBase):
    id: int = Field(..., example=1)
    user_id: int = Field(..., example=1)
    doctor_id: int = Field(..., example=1)
    medicines: Optional[List[int]] = Field(None, description="List of medicine IDs for this appointment")

    class Config:
        from_attributes = True
