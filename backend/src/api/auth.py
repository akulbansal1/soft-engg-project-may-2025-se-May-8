from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from src.db.database import get_db
from src.services.user_service import UserService
from src.services.passkey_service import PasskeyService
from src.schemas.user import UserCreate, UserUpdate, UserResponse, UserLogin, UserSession
from src.schemas.passkey import (
    PasskeyCredentialResponse, 
    SignupResponse, 
    LoginResponse,
    PasskeyRegistrationRequest,
    PasskeyLoginRequest,
    PasskeyVerificationResult
)
from src.utils.cache import Cache

router = APIRouter(prefix="/auth", tags=["🔐 Authentication"])

@router.post("/passkey/register/challenge", response_model=Dict[str, Any])
def create_passkey_registration_challenge(
    request: PasskeyRegistrationRequest, 
    db: Session = Depends(get_db)
):
    """
    Create WebAuthn registration challenge for passkey setup
    Step 1 of passkey registration
    """
    try:
        # Create registration challenge
        challenge_data = PasskeyService.create_signup_challenge(db, request.user_phone, request.user_name)
        return {
            "challenge": challenge_data,
            "message": "Registration challenge created"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create challenge: {str(e)}"
        )

@router.post("/passkey/register/verify", response_model=PasskeyVerificationResult)
def verify_passkey_registration(
    request: PasskeyRegistrationRequest,
    response_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Verify WebAuthn registration response and create passkey credential
    Step 2 of passkey registration
    """
    try:
        result = PasskeyService.verify_signup_response(
            db, request.user_phone, response_data
        )
        
         # If login successful, issue session
        if result.success and result.user_id:
            session_data = UserService.issue_session(result.user_id)

            result_dict = result.model_dump()
            ##NOTE: Add session as a cookie to the response

            return PasskeyVerificationResult(**result_dict)
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify registration: {str(e)}"
        )

@router.post("/passkey/login/challenge", response_model=Dict[str, Any])
def create_passkey_login_challenge(
    request: PasskeyLoginRequest,
    db: Session = Depends(get_db)
):
    """
    Create WebAuthn authentication challenge for passkey login
    Step 1 of passkey authentication
    """
    try:
        challenge_data = PasskeyService.create_login_challenge(
            db, request.credential_id
        )
        return challenge_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create challenge: {str(e)}"
        )

@router.post("/passkey/login/verify", response_model=PasskeyVerificationResult)
def verify_passkey_login(
    request: PasskeyLoginRequest,
    response_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Verify WebAuthn authentication response for passkey login
    Step 2 of passkey authentication
    """
    try:
        result = PasskeyService.verify_login_response(
            db, request.credential_id, response_data
        )
        
        # If login successful, issue session
        if result.success and result.user_id:
            session_data = UserService.issue_session(result.user_id)
            result_dict = result.model_dump()

            ##NOTE: Add session as a cookie to the response

            return PasskeyVerificationResult(**result_dict)
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify login: {str(e)}"
        )

@router.get("/passkey/user/{user_id}", response_model=List[PasskeyCredentialResponse])
def get_user_passkeys(user_id: int, db: Session = Depends(get_db)):
    """
    Get all passkey credentials for a user
    """
    try:
        credentials = PasskeyService.get_user_credentials(db, user_id)
        return [PasskeyCredentialResponse.model_validate(cred) for cred in credentials]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get credentials: {str(e)}"
        )

@router.delete("/passkey/{credential_id}")
def delete_passkey_credential(
    credential_id: str, 
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a passkey credential (user can only delete their own)
    """
    try:
        success = PasskeyService.delete_credential(db, credential_id, user_id)
        return {"message": "Credential deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete credential: {str(e)}"
        )


## Logout

## NOTE: Remove the session from cookie somehow & implement this method
# @router.post("/logout")
# def logout_user(user_id: int,):
#     """
#     User Logout
#     Invalidates user session
#     """
#     success = UserService.logout_user(user_id, session_token)
#     if not success:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Failed to logout user"
#         )
    
#     return {"message": "Logout successful"}
