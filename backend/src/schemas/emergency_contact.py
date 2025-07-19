from pydantic import BaseModel, Field
from typing import Optional

class EmergencyContactBase(BaseModel):
    """Base schema for EmergencyContact (shared fields)."""
    name: str = Field(..., example="John Doe", description="Name of the emergency contact")
    relation: Optional[str] = Field(None, example="Brother", description="Relation to the user (optional)")
    phone: int = Field(..., example=9876543210, description="Phone number of the emergency contact")

class EmergencyContactCreate(EmergencyContactBase):
    """Schema for creating a new emergency contact."""
    user_id: int = Field(..., example=1, description="ID of the user this contact belongs to")

class EmergencyContactUpdate(BaseModel):
    """Schema for updating an emergency contact (partial update)."""
    name: Optional[str] = Field(None, example="John Doe", description="Name of the emergency contact (optional)")
    relation: Optional[str] = Field(None, example="Brother", description="Relation to the user (optional)")
    phone: Optional[str] = Field(None, example="9876543210", description="Phone number (optional)")

class EmergencyContactResponse(EmergencyContactBase):
    """Schema for returning emergency contact data to the client."""
    id: int = Field(..., example=1, description="Unique emergency contact ID")
    user_id: int = Field(..., example=1, description="ID of the user this contact belongs to")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "John Doe",
                "relation": "Brother",
                "phone": 9876543210,
                "user_id": 1
            }
        }
