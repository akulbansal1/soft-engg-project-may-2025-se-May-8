from pydantic import BaseModel, Field
from typing import Optional

class EmergencyContactBase(BaseModel):
    """Base schema for EmergencyContact (shared fields)"""
    name: str = Field(..., example="John Doe")
    relation: Optional[str] = Field(None, example="Brother")
    phone: int = Field(..., example=9876543210)

class EmergencyContactCreate(EmergencyContactBase):
    """Schema for creating a new emergency contact"""
    user_id: int = Field(..., example=1)

class EmergencyContactUpdate(BaseModel):
    """Schema for updating an emergency contact"""
    name: Optional[str] = None
    relation: Optional[str] = None
    phone: Optional[int] = None

class EmergencyContactResponse(EmergencyContactBase):
    """Schema for returning emergency contact data to the client"""
    id: int
    user_id: int

    class Config:
        from_attributes = True
