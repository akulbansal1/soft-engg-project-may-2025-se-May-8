from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional
from pydantic import Field

class UserBase(BaseModel):
    """Base user schema with core fields for registration and profile."""
    name: str = Field(..., example="Amit Sharma", description="Full name of the user")
    phone: str = Field(..., example="+919876543210", description="User's phone number in international format")
    dob: Optional[date] = Field(None, example="1950-01-01", description="Date of birth (optional)")
    gender: Optional[str] = Field(None, example="Male", description="Gender (optional)")

class UserCreate(UserBase):
    """Schema for user registration."""
    is_active: bool = Field(default=True, example=True, description="Whether the user is active (default: True)")

class UserLogin(BaseModel):
    """Schema for user login."""
    phone: str = Field(..., example="+919876543210", description="User's phone number for login")

class UserResponse(UserBase):
    """Schema for user response data returned to client."""
    id: int = Field(..., example=1, description="Unique user ID")
    is_active: bool = Field(..., example=True, description="Whether the user is active")
    created_at: datetime = Field(..., example="2025-07-01T10:00:00Z", description="User creation timestamp (ISO 8601)")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Amit Sharma",
                "phone": "+919876543210",
                "dob": "1950-01-01",
                "gender": "Male",
                "is_active": True,
                "created_at": "2025-07-01T10:00:00Z"
            }
        }

class UserSession(BaseModel):
    """Schema for user session data."""
    user_id: int = Field(..., example=1, description="User ID for the session")
    session_token: str = Field(..., example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...", description="Session token (JWT or similar)")
    expires_at: datetime = Field(..., example="2025-07-01T12:00:00Z", description="Session expiration timestamp (ISO 8601)")
    created_at: datetime = Field(..., example="2025-07-01T10:00:00Z", description="Session creation timestamp (ISO 8601)")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "session_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "expires_at": "2025-07-01T12:00:00Z",
                "created_at": "2025-07-01T10:00:00Z"
            }
        }

class UserUpdate(BaseModel):
    """Schema for updating user information (partial update)."""
    name: Optional[str] = Field(None, example="Amit Sharma", description="Full name of the user")
    phone: Optional[str] = Field(None, example="+919876543210", description="User's phone number")
    dob: Optional[date] = Field(None, example="1950-01-01", description="Date of birth (optional)")
    gender: Optional[str] = Field(None, example="Male", description="Gender (optional)")
    is_active: Optional[bool] = Field(None, example=True, description="Whether the user is active")
