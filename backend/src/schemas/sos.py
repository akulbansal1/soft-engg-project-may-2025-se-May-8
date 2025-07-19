from pydantic import BaseModel, Field
from typing import List, Optional

class SOSResponse(BaseModel):
    """Schema for SOS trigger response"""
    success: bool = Field(..., description="Whether the SOS messages were sent successfully")
    message: str = Field(..., description="Response message")
    contacts_notified: int = Field(..., description="Number of emergency contacts notified")
    failed_notifications: List[str] = Field(default=[], description="List of phone numbers that failed to receive notification")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Emergency SOS messages sent successfully",
                "contacts_notified": 3,
                "failed_notifications": []
            }
        }
