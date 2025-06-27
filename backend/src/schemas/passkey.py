from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any

class PasskeyCredentialBase(BaseModel):
    """Base schema for PasskeyCredential"""
    credential_id: str = Field(..., description="Unique credential identifier")
    public_key: str = Field(..., description="Public key for the credential")

class PasskeyCredentialCreate(PasskeyCredentialBase):
    """Schema for creating a new PasskeyCredential"""
    user_id: int = Field(..., description="User ID this credential belongs to")
    sign_count: int = Field(default=0, description="Initial signature counter")

class PasskeyCredentialUpdate(BaseModel):
    """Schema for updating a PasskeyCredential"""
    sign_count: Optional[int] = Field(None, description="Updated signature counter")

class PasskeyCredentialResponse(PasskeyCredentialBase):
    """Schema for PasskeyCredential responses"""
    id: int
    user_id: int
    sign_count: int
    created_at: datetime

    class Config:
        from_attributes = True

# WebAuthn Challenge and Response schemas
class SignupChallenge(BaseModel):
    """Schema for WebAuthn registration challenge"""
    challenge: str = Field(..., description="Cryptographic challenge")
    user_id: int = Field(..., description="User ID for registration")
    rp: Dict[str, str] = Field(..., description="Relying party information")
    user: Dict[str, str] = Field(..., description="User information")
    pubKeyCredParams: List[Dict[str, Any]] = Field(..., description="Supported public key parameters")
    timeout: int = Field(default=60000, description="Timeout in milliseconds")
    attestation: str = Field(default="direct", description="Attestation preference")

## NOTE: Might not need this, be ok with Dict[str, Any] for flexibility
class SignupResponse(BaseModel):
    """Schema for WebAuthn registration response"""
    credential_id: str = Field(..., description="Generated credential ID")
    public_key: str = Field(..., description="Public key from authenticator")
    attestation_object: str = Field(..., description="Attestation object from authenticator")
    client_data_json: str = Field(..., description="Client data JSON")

class LoginChallenge(BaseModel):
    """Schema for WebAuthn authentication challenge"""
    challenge: str = Field(..., description="Cryptographic challenge")
    timeout: int = Field(default=60000, description="Timeout in milliseconds")
    rpId: str = Field(..., description="Relying party identifier")
    userVerification: str = Field(default="preferred", description="User verification requirement")
    allowCredentials: Optional[List[Dict[str, Any]]] = Field(None, description="Allowed credentials")

class LoginResponse(BaseModel):
    """Schema for WebAuthn authentication response"""
    credential_id: str = Field(..., description="Credential ID used for authentication")
    signature: str = Field(..., description="Authentication signature")
    client_data: str = Field(..., description="Client data JSON")
    authenticator_data: str = Field(..., description="Authenticator data")
    sign_count: int = Field(..., description="Updated signature counter")

class PasskeyRegistrationRequest(BaseModel):
    """Request to start passkey registration"""
    user_phone: int = Field(..., description="User phone number for registration")
    user_name: str = Field(..., description="User name for registration")

class PasskeyLoginRequest(BaseModel):
    """Request to start passkey login"""
    credential_id: str = Field(None, description="Credential ID for login (optional)")

class PasskeyVerificationResult(BaseModel):
    """Result of passkey verification"""
    user_id: Optional[int] = Field(None, description="User ID if login was successful")
    credential_id: Optional[str] = Field(None, description="Credential ID used")
    session_expires_at: Optional[datetime] = Field(None, description="Session expiration time if applicable")