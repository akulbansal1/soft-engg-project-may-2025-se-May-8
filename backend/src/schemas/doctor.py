from pydantic import BaseModel, Field
from typing import Optional

class DoctorBase(BaseModel):
    """Base schema for doctor details."""
    name: str = Field(..., example="Dr. A. Kumar", description="Doctor's name")
    location: str = Field(..., example="Delhi", description="Doctor's location")

class DoctorCreate(DoctorBase):
    """Schema for creating a new doctor record."""

class DoctorUpdate(BaseModel):
    """Schema for updating a doctor record (partial update)."""
    name: Optional[str] = Field(None, example="Dr. A. Kumar", description="Doctor's name (optional)")
    location: Optional[str] = Field(None, example="Delhi", description="Doctor's location (optional)")

class DoctorResponse(DoctorBase):
    """Schema for returning doctor data to the client."""
    id: int = Field(..., example=1, description="Unique doctor ID")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Dr. A. Kumar",
                "location": "Delhi"
            }
        }
