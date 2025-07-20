from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional, List, Dict, Any

class PasskeyCredentialBase(BaseModel):
    """Base schema for PasskeyCredential."""
    credential_id: str = Field(..., example="cred-123", description="Unique credential identifier")
    public_key: str = Field(..., example="MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8A...", description="Public key for the credential")

class PasskeyCredentialCreate(PasskeyCredentialBase):
    """Schema for creating a new PasskeyCredential."""
    user_id: int = Field(..., example=1, description="User ID this credential belongs to")
    sign_count: int = Field(default=0, example=0, description="Initial signature counter")

class PasskeyCredentialUpdate(BaseModel):
    """Schema for updating a PasskeyCredential (partial update)."""
    sign_count: Optional[int] = Field(None, example=1, description="Updated signature counter (optional)")

class PasskeyCredentialResponse(PasskeyCredentialBase):
    """Schema for PasskeyCredential responses."""
    id: int = Field(..., example=1, description="Unique credential ID")
    user_id: int = Field(..., example=1, description="User ID this credential belongs to")
    sign_count: int = Field(..., example=0, description="Signature counter")
    created_at: datetime = Field(..., example="2025-07-01T10:00:00Z", description="Credential creation timestamp (ISO 8601)")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "credential_id": "cred-123",
                "public_key": "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8A...",
                "user_id": 1,
                "sign_count": 0,
                "created_at": "2025-07-01T10:00:00Z"
            }
        }

class PasskeyRegistrationRequest(BaseModel):
    """Request to start passkey registration."""
    user_phone: str = Field(..., example="+919876543210", description="User phone number for registration")
    user_name: str = Field(..., example="Amit Sharma", description="User name for registration")
    user_dob: Optional[date] = Field(None, example="1950-01-01", description="User date of birth (optional)")
    user_gender: Optional[str] = Field(None, example="Male", description="User gender (optional)")

class PasskeyLoginRequest(BaseModel):
    """Request to start passkey login."""
    credential_id: str = Field(None, example="cred-123", description="Credential ID for login (optional)")

class PasskeyVerificationResult(BaseModel):
    """Result of passkey verification."""
    user_id: Optional[int] = Field(None, example=1, description="User ID if login was successful (optional)")
    credential_id: Optional[str] = Field(None, example="cred-123", description="Credential ID used (optional)")
    session_expires_at: Optional[datetime] = Field(None, example="2025-07-01T12:00:00Z", description="Session expiration time if applicable (optional)")

# Schema for user object in WebAuthn challenge
class WebAuthnUser(BaseModel):
    """Schema for user information in WebAuthn challenges."""
    id: str = Field(..., example="MQ==", description="Base64-encoded user ID")
    name: str = Field(..., example="9876543210", description="User name (typically phone number)")
    display_name: str = Field(..., example="Test User", description="User display name")

# Schema for relying party object in WebAuthn challenge  
class WebAuthnRelyingParty(BaseModel):
    """Schema for relying party information in WebAuthn challenges."""
    name: str = Field(..., example="SE Project API", description="Relying party name")
    id: str = Field(..., example="localhost", description="Relying party identifier")

# Schema for public key credential parameters
class PublicKeyCredentialParameters(BaseModel):
    """Schema for public key credential parameters."""
    type: str = Field(..., example="public-key", description="Credential type")
    alg: int = Field(..., example=-7, description="Algorithm identifier")

# Schema for serialized WebAuthn challenge response
class SerializedWebAuthnChallenge(BaseModel):
    """Schema for serialized WebAuthn challenge data returned by _serialize_challenge_data method."""
    challenge: str = Field(..., example="pGr/DLUhVo1bgo4xQLfYO8J5HHVBiupt8XDDR/osCxApMawNrq2y27bTJMlLwslWVOmaZIVtvgkXUbOE9rjSIw==", description="Base64-encoded cryptographic challenge")
    user: WebAuthnUser = Field(..., description="User information for the challenge")
    rp: WebAuthnRelyingParty = Field(..., description="Relying party information")
    pubKeyCredParams: Optional[List[PublicKeyCredentialParameters]] = Field(None, example=[{"type": "public-key", "alg": -7}], description="Supported public key credential parameters")
    timeout: int = Field(..., example=300000, description="Challenge timeout in milliseconds")
    attestation: str = Field(..., example="none", description="Attestation preference")

    class Config:
        json_schema_extra = {
            "example": {
                "challenge": "pGr/DLUhVo1bgo4xQLfYO8J5HHVBiupt8XDDR/osCxApMawNrq2y27bTJMlLwslWVOmaZIVtvgkXUbOE9rjSIw==",
                "user": {
                    "id": "MQ==",
                    "name": "9876543210", 
                    "display_name": "Test User"
                },
                "rp": {
                    "name": "SE Project API",
                    "id": "localhost"
                },
                "pubKeyCredParams": [
                    {"type": "public-key", "alg": -7}
                ],
                "timeout": 300000,
                "attestation": "none"
            }
        }

## NOTE: Not used it 
class SignupChallenge(BaseModel):
    """Schema for WebAuthn registration challenge."""
    challenge: str = Field(..., example="abc123", description="Cryptographic challenge")
    user_id: int = Field(..., example=1, description="User ID for registration")
    rp: Dict[str, str] = Field(..., example={"name": "MyApp"}, description="Relying party information")
    user: Dict[str, str] = Field(..., example={"name": "Amit Sharma"}, description="User information")
    pubKeyCredParams: List[Dict[str, Any]] = Field(..., example=[{"type": "public-key", "alg": -7}], description="Supported public key parameters")
    timeout: int = Field(default=60000, example=60000, description="Timeout in milliseconds")
    attestation: str = Field(default="direct", example="direct", description="Attestation preference")

## NOTE: Might not need this, be ok with Dict[str, Any] for flexibility
class SignupResponse(BaseModel):
    """Schema for WebAuthn registration response."""
    credential_id: str = Field(..., example="cred-123", description="Generated credential ID")
    public_key: str = Field(..., example="MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8A...", description="Public key from authenticator")
    attestation_object: str = Field(..., example="attestation-object", description="Attestation object from authenticator")
    client_data_json: str = Field(..., example="client-data-json", description="Client data JSON")

## NOTE: Not used it
class LoginChallenge(BaseModel):
    """Schema for WebAuthn authentication challenge."""
    challenge: str = Field(..., example="xyz789", description="Cryptographic challenge")
    timeout: int = Field(default=60000, example=60000, description="Timeout in milliseconds")
    rpId: str = Field(..., example="myapp.com", description="Relying party identifier")
    userVerification: str = Field(default="preferred", example="preferred", description="User verification requirement")
    allowCredentials: Optional[List[Dict[str, Any]]] = Field(None, example=[{"id": "cred-123"}], description="Allowed credentials (optional)")

## NOTE: Might not need this, be ok with Dict[str, Any] for flexibility
class LoginResponse(BaseModel):
    """Schema for WebAuthn authentication response."""
    credential_id: str = Field(..., example="cred-123", description="Credential ID used for authentication")
    signature: str = Field(..., example="signature-data", description="Authentication signature")
    client_data: str = Field(..., example="client-data-json", description="Client data JSON")
    authenticator_data: str = Field(..., example="authenticator-data", description="Authenticator data")
    sign_count: int = Field(..., example=1, description="Updated signature counter")