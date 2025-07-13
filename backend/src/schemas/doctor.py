from pydantic import BaseModel, Field
from typing import Optional

class DoctorBase(BaseModel):
    name: str = Field(..., example="Dr. A. Kumar", description="Doctor's name")
    location: str = Field(..., example="Delhi", description="Doctor's location")

class DoctorCreate(DoctorBase):
    pass

class DoctorUpdate(BaseModel):
    name: Optional[str] = Field(None, example="Dr. A. Kumar")
    location: Optional[str] = Field(None, example="Delhi")

class DoctorResponse(DoctorBase):
    id: int = Field(..., example=1)

    class Config:
        from_attributes = True
