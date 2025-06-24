from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

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
from src.core.config import settings

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
    response: Response,
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
        
         # If registration successful, issue session
        if result.success and result.user_id:
            session_data = UserService.issue_session(result.user_id)

            # Set session token as HTTP-only cookie
            response.set_cookie(
                key="session_token",
                value=session_data["session_token"],
                max_age=settings.COOKIE_EXPIRY.total_seconds(),  # 24 hours in seconds
                httponly=True,  # Prevents JavaScript access (XSS protection)
                secure=settings.COOKIE_SECURE,   # Set to True in production with HTTPS
                samesite="lax"  # CSRF protection
            )

            # Add session info to result without exposing token in response body
            result_dict = result.model_dump()
            result_dict["session_expires_at"] = session_data["expires_at"]

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
    response: Response,
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

            # Set session token as HTTP-only cookie
            response.set_cookie(
                key="session_token",
                value=session_data["session_token"],
                max_age=settings.COOKIE_EXPIRY.total_seconds(),
                httponly=True,  # Prevents JavaScript access (XSS protection)
                secure=settings.COOKIE_SECURE,   # Set to True in production with HTTPS
                samesite="lax"  # CSRF protection
            )

            # Add session info to result without exposing token in response body
            result_dict = result.model_dump()
            result_dict["session_expires_at"] = session_data["expires_at"]

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

@router.post("/logout")
def logout_user(
    response: Response,
    session_token: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    """
    User Logout
    Invalidates user session and clears cookie
    """
    if not session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No session token found"
        )
    
    # For now, we'll just clear the cookie
    success = UserService.logout_user_by_token(session_token)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to logout user"
        )
    
    # Clear the session cookie
    response.delete_cookie(
        key="session_token",
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax"
    )
    
    return {"message": "Logout successful"}

# Authentication dependency to get current user from session cookie
def get_current_user(
    session_token: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Dependency to get current authenticated user from session cookie
    """
    if not session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No session token provided"
        )
    
    user = UserService.get_user_by_session(db, session_token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session"
        )
    
    return UserResponse.model_validate(user)


# Protected endpoint example
@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: UserResponse = Depends(get_current_user)):
    """
    Get current authenticated user information
    """
    return current_user
