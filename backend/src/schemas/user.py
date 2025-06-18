from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    """Base user schema with core fields"""
    name: str
    phone: int

class UserCreate(UserBase):
    """Schema for user registration"""
    is_active: bool = True  # Default to active when creating

class UserLogin(BaseModel):
    """Schema for user login"""
    phone: int

class UserResponse(UserBase):
    """Schema for user response data"""
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class UserSession(BaseModel):
    """Schema for user session data"""
    user_id: int
    session_token: str
    expires_at: datetime
    created_at: datetime

class UserUpdate(BaseModel):
    """Schema for updating user information"""
    name: Optional[str] = None
    phone: Optional[int] = None
    is_active: Optional[bool] = None
