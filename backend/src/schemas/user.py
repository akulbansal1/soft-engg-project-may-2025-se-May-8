from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    """Base user schema with core fields"""
    name: str
    email: EmailStr

class UserCreate(UserBase):
    """Schema for user registration"""
    pass

class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr

class UserResponse(UserBase):
    """Schema for user response data"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class UserSession(BaseModel):
    """Schema for user session data"""
    user_id: int
    session_token: str
    expires_at: datetime

class UserUpdate(BaseModel):
    """Schema for updating user information"""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
