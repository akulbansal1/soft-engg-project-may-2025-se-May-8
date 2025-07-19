from pydantic import BaseModel, Field
from typing import List, Optional

class SOSResponse(BaseModel):
    """Schema for SOS trigger response."""
    success: bool = Field(..., example=True, description="Whether the SOS messages were sent successfully")
    message: str = Field(..., example="Emergency SOS messages sent successfully", description="Response message")
    contacts_notified: int = Field(..., example=3, description="Number of emergency contacts notified")
    failed_notifications: List[str] = Field(default=[], example=[], description="List of phone numbers that failed to receive notification")

    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "message": "Some SOS messages failed to send",
                "contacts_notified": 2,
                "failed_notifications": ["+919876543210", "+919812345678"]
            }
        }
