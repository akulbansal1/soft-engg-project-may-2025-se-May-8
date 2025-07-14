from pydantic import BaseModel, Field, field_validator
from typing import Optional
import re

class SMSVerificationRequest(BaseModel):
    """Schema for SMS verification initiation request"""
    phone: str = Field(..., description="Phone number to send verification code to")
    
    @field_validator('phone')
    @classmethod
    def validate_phone_number(cls, v):
        """Validate phone number format"""
        # Remove any non-digit characters except + at the beginning
        cleaned_phone = re.sub(r'[^\d+]', '', v)
        
        # Check if it starts with + (international format)
        if cleaned_phone.startswith('+'):
            # Remove the + and check if remaining are all digits
            digits_only = cleaned_phone[1:]
            if not digits_only.isdigit():
                raise ValueError("Invalid phone number format")
            # International numbers should be 7-15 digits after country code
            if not (7 <= len(digits_only) <= 15):
                raise ValueError("Phone number should contain 7-15 digits after country code")
        else:
            # Domestic format - should be all digits
            if not cleaned_phone.isdigit():
                raise ValueError("Phone number should contain only digits")
            # Domestic numbers should be 10-15 digits
            if not (10 <= len(cleaned_phone) <= 15):
                raise ValueError("Phone number should contain 10-15 digits")
        
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "phone": "+1234567890"
            }
        }

class SMSVerificationCodeRequest(BaseModel):
    """Schema for SMS verification code submission"""
    phone: str = Field(..., description="Phone number that received the verification code")
    code: str = Field(..., min_length=4, max_length=8, description="Verification code received via SMS")
    
    @field_validator('phone')
    @classmethod
    def validate_phone_number(cls, v):
        """Validate phone number format - same as SMSVerificationRequest"""
        # Remove any non-digit characters except + at the beginning
        cleaned_phone = re.sub(r'[^\d+]', '', v)
        
        # Check if it starts with + (international format)
        if cleaned_phone.startswith('+'):
            # Remove the + and check if remaining are all digits
            digits_only = cleaned_phone[1:]
            if not digits_only.isdigit():
                raise ValueError("Invalid phone number format")
            # International numbers should be 7-15 digits after country code
            if not (7 <= len(digits_only) <= 15):
                raise ValueError("Phone number should contain 7-15 digits after country code")
        else:
            # Domestic format - should be all digits
            if not cleaned_phone.isdigit():
                raise ValueError("Phone number should contain only digits")
            # Domestic numbers should be 10-15 digits
            if not (10 <= len(cleaned_phone) <= 15):
                raise ValueError("Phone number should contain 10-15 digits")
        
        return v
    
    @field_validator('code')
    @classmethod
    def validate_code(cls, v):
        """Ensure code contains only digits"""
        if not v.isdigit():
            raise ValueError("Verification code should contain only digits")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "phone": "+1234567890",
                "code": "123456"
            }
        }

class SMSVerificationResponse(BaseModel):
    """Schema for SMS verification response"""
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Response message")
    expires_in: Optional[int] = Field(None, description="Time in seconds until verification expires")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Verification code sent successfully",
                "expires_in": 600
            }
        }

class SMSVerificationStatusResponse(BaseModel):
    """Schema for SMS verification status response"""
    verified: bool = Field(..., description="Whether the phone number is verified")
    message: str = Field(..., description="Response message")
    expires_at: Optional[str] = Field(None, description="When the verification status expires")
    
    class Config:
        json_schema_extra = {
            "example": {
                "verified": True,
                "message": "Phone number successfully verified",
                "expires_at": "2025-06-28T22:30:00Z"
            }
        }
