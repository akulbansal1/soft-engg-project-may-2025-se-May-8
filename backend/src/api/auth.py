from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie, Path
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from src.db.database import get_db
from src.services.user_service import UserService
from src.services.passkey_service import PasskeyService
from src.schemas.user import  UserResponse, UserSession
from src.schemas.passkey import (
    PasskeyCredentialResponse, 
    SignupResponse, 
    LoginResponse,
    PasskeyRegistrationRequest,
    PasskeyLoginRequest,
    PasskeyVerificationResult
)
from src.schemas.sms import (
    SMSVerificationRequest,
    SMSVerificationCodeRequest, 
    SMSVerificationResponse,
    SMSVerificationStatusResponse
)
from src.core.config import settings
from src.core.auth_middleware import RequireOwnership, RequireAuth

router = APIRouter(
    prefix="/auth", 
    tags=["🔐 Authentication"],
    responses={
        400: {"description": "Bad Request - Invalid input data"},
        401: {"description": "Unauthorized - Authentication required"},
        403: {"description": "Forbidden - Insufficient permissions"},
        500: {"description": "Internal Server Error"}
    }
)

# SMS Verification Endpoints

@router.post(
    "/sms/send", 
    response_model=SMSVerificationResponse,
    status_code=status.HTTP_200_OK,
    summary="Send SMS verification code",
    description="Send a verification code to the provided phone number. This is step 1 of the SMS verification process.",
    responses={
        200: {"description": "Verification code sent successfully"},
        400: {"description": "Invalid phone number format"},
        500: {"description": "Failed to send verification code"}
    }
)
def send_sms_verification(
    request: SMSVerificationRequest,
    db: Session = Depends(get_db)
):
    """
    **Send SMS verification code to phone number**
    
    - **phone**: Valid phone number (international format recommended: +1234567890)
    - Returns verification response with success status and expiry time
    - Code expires in 10 minutes
    """
    try:
        from src.services.sms_service import sms_service
        result = sms_service.send_verification_code(request.phone)
        
        return SMSVerificationResponse(
            success=result['success'],
            message=result['message'],
            expires_in=result.get('expires_in')
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send verification code: {str(e)}"
        )

@router.post(
    "/sms/verify", 
    response_model=SMSVerificationStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Verify SMS code",
    description="Verify the SMS code received on the phone number. This is step 2 of the SMS verification process.",
    responses={
        200: {"description": "Code verification result"},
        400: {"description": "Invalid code or phone number"},
        500: {"description": "Failed to verify code"}
    }
)
def verify_sms_code(
    request: SMSVerificationCodeRequest,
    db: Session = Depends(get_db)
):
    """
    **Verify SMS code for phone number**
    
    - **phone**: Phone number that received the verification code
    - **code**: 4-8 digit verification code from SMS
    - Returns verification status and expiry information
    """
    try:
        from src.services.sms_service import sms_service
        result = sms_service.verify_code(request.phone, request.code)
        
        return SMSVerificationStatusResponse(
            verified=result['success'],
            message=result['message'],
            expires_at=result.get('expires_at')
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify code: {str(e)}"
        )

@router.get(
    "/sms/status/{phone}", 
    response_model=SMSVerificationStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Get SMS verification status",
    description="Check the current verification status for a phone number.",
    responses={
        200: {"description": "Verification status retrieved"},
        500: {"description": "Failed to get verification status"}
    }
)
def get_sms_verification_status(
    phone: str = Path(..., description="Phone number to check verification status for"),
    db: Session = Depends(get_db)
):
    """
    **Get SMS verification status for a phone number**
    
    - **phone**: Phone number to check status for
    - Returns current verification status and expiry time
    """
    try:
        from src.services.sms_service import sms_service
        result = sms_service.get_verification_status(phone)
        
        return SMSVerificationStatusResponse(
            verified=result['verified'],
            message=result['message'],
            expires_at=result.get('expires_at')
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get verification status: {str(e)}"
        )

# Passkey Registration and Login Endpoints

@router.post(
    "/passkey/register/challenge", 
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Create passkey registration challenge",
    description="Generate a WebAuthn registration challenge for passkey setup. This is step 1 of passkey registration.",
    responses={
        200: {"description": "Registration challenge created successfully"},
        400: {"description": "Invalid user data"},
        500: {"description": "Failed to create challenge"}
    }
)
def create_passkey_registration_challenge(
    request: PasskeyRegistrationRequest, 
    db: Session = Depends(get_db)
):
    """
    **Create WebAuthn registration challenge for passkey setup**
    
    - **user_phone**: Phone number for the user account
    - **user_name**: Display name for the user
    - **user_dob**: Date of birth (optional)
    - **user_gender**: Gender (optional)
    - Returns WebAuthn challenge data for frontend
    """
    try:
        # Create registration challenge
        challenge_data = PasskeyService.create_signup_challenge(
            db, 
            request.user_phone, 
            request.user_name, 
            request.user_dob, 
            request.user_gender
        )

        return challenge_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create challenge: {str(e)}"
        )

@router.post(
    "/passkey/register/verify", 
    response_model=PasskeyVerificationResult,
    status_code=status.HTTP_200_OK,
    summary="Verify passkey registration",
    description="Verify WebAuthn registration response and create passkey credential. This is step 2 of passkey registration. Sets session cookie on success.",
    responses={
        200: {"description": "Registration verified successfully, user created"},
        400: {"description": "Invalid registration response"},
        500: {"description": "Failed to verify registration"}
    }
)
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
        if result and result.user_id:
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

@router.post(
    "/passkey/login/challenge", 
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Create passkey login challenge",
    description="Generate a WebAuthn authentication challenge for passkey login. This is step 1 of passkey authentication.",
    responses={
        200: {"description": "Login challenge created successfully"},
        400: {"description": "Invalid credential ID"},
        404: {"description": "Credential not found"},
        500: {"description": "Failed to create challenge"}
    }
)
def create_passkey_login_challenge(
    request: PasskeyLoginRequest,
    db: Session = Depends(get_db)
):
    """
    **Create WebAuthn authentication challenge for passkey login**
    
    - **credential_id**: Specific credential ID to use (optional)
    - Returns WebAuthn challenge data for frontend authentication
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

@router.post(
    "/passkey/login/verify", 
    response_model=PasskeyVerificationResult,
    status_code=status.HTTP_200_OK,
    summary="Verify passkey login",
    description="Verify WebAuthn authentication response for passkey login. This is step 2 of passkey authentication. Sets session cookie on success.",
    responses={
        200: {"description": "Login verified successfully, session created"},
        400: {"description": "Invalid login response"},
        401: {"description": "Authentication failed"},
        500: {"description": "Failed to verify login"}
    }
)
def verify_passkey_login(
    request: PasskeyLoginRequest,
    response_data: Dict[str, Any],
    response: Response,
    db: Session = Depends(get_db)
):
    """
    **Verify WebAuthn authentication response for passkey login**
    
    - **request**: Same login request from challenge step
    - **response_data**: WebAuthn assertion response from frontend
    - Authenticates user with passkey
    - Sets HTTP-only session cookie on success
    - Returns user ID and session expiry
    """
    try:
        result = PasskeyService.verify_login_response(
            db, request.credential_id, response_data
        )
        
        # If login successful, issue session
        if result and result.user_id:
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

@router.get(
    "/passkey/user/{user_id}", 
    response_model=List[PasskeyCredentialResponse],
    status_code=status.HTTP_200_OK,
    summary="Get user passkeys",
    description="Retrieve all passkey credentials for a specific user. Requires authentication and ownership.",
    responses={
        200: {"description": "List of user's passkey credentials"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized to access this user's data"},
        404: {"description": "User not found"}
    }
)
def get_user_passkeys(
    user_id: int = Path(..., description="User ID to get passkeys for"), 
    current_user = Depends(RequireOwnership), 
    db: Session = Depends(get_db)
):
    """
    **Get all passkey credentials for a user**
    
    - **user_id**: ID of the user to get passkeys for
    - Requires authentication and ownership verification
    - Returns list of passkey credentials with metadata
    """
    try:
        credentials = PasskeyService.get_user_credentials(db, user_id)
        return [PasskeyCredentialResponse.model_validate(cred) for cred in credentials]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get credentials: {str(e)}"
        )

@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="User logout",
    description="Logout user by invalidating session and clearing session cookie.",
    responses={
        200: {"description": "Logout successful", "content": {"application/json": {"example": {"message": "Logout successful"}}}},
        400: {"description": "Failed to logout"},
        401: {"description": "Not authenticated"}
    }
)
def logout_user(
    response: Response,
    session_token: Optional[str] = Cookie(None, description="Session token from HTTP-only cookie"),
    current_user = Depends(RequireAuth),
    db: Session = Depends(get_db)
):
    """
    **User Logout**
    
    - Invalidates current user session
    - Clears session cookie from browser
    - Requires valid authentication
    """
    
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

@router.get(
    "/me", 
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user info",
    description="Get information about the currently authenticated user.",
    responses={
        200: {"description": "Current user information"},
        401: {"description": "Not authenticated"}
    }
)
def get_current_user_info(current_user = Depends(RequireAuth)):
    """
    **Get current authenticated user information**
    
    - Returns user profile data for authenticated user
    - Includes user ID, name, phone, and account status
    """
    return UserResponse.model_validate(current_user)


## ADMIN ENDPOINT