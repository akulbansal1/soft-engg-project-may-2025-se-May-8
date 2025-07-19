from pydantic import BaseModel, Field, field_validator
from typing import Optional
import re

class SMSVerificationRequest(BaseModel):
    """Schema for SMS verification initiation request. Used to request a verification code via SMS."""
    phone: str = Field(..., example="+1234567890", description="Phone number to send verification code to (E.164 format)")
    
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
    """Schema for SMS verification code submission. Used to verify the code received via SMS."""
    phone: str = Field(..., example="+1234567890", description="Phone number that received the verification code (E.164 format)")
    code: str = Field(..., min_length=4, max_length=8, example="123456", description="Verification code received via SMS (4-8 digits)")
    
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
    """Schema for SMS verification response. Indicates if the code was sent and when it expires."""
    success: bool = Field(..., example=True, description="Whether the operation was successful")
    message: str = Field(..., example="Verification code sent successfully", description="Response message")
    expires_in: Optional[int] = Field(None, example=600, description="Time in seconds until verification expires (optional)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Verification code sent successfully",
                "expires_in": 600
            }
        }

class SMSVerificationStatusResponse(BaseModel):
    """Schema for SMS verification status response. Indicates if the phone number is verified and expiry info."""
    verified: bool = Field(..., example=True, description="Whether the phone number is verified")
    message: str = Field(..., example="Phone number successfully verified", description="Response message")
    expires_at: Optional[str] = Field(None, example="2025-06-28T22:30:00Z", description="When the verification status expires (ISO 8601, optional)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "verified": True,
                "message": "Phone number successfully verified",
                "expires_at": "2025-06-28T22:30:00Z"
            }
        }
