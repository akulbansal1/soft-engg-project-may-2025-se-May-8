from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from typing import Optional, List, Dict, Any
from webauthn import generate_registration_options, verify_registration_response, generate_authentication_options, verify_authentication_response
from webauthn.helpers.structs import AuthenticatorSelectionCriteria, UserVerificationRequirement
import json

from src.services.user_service import UserService
from src.models.passkey import PasskeyCredential
from src.models.user import User
from src.schemas.passkey import (
    PasskeyCredentialCreate,
    PasskeyCredentialUpdate,
    SignupChallenge,
    SignupResponse,
    LoginChallenge,
    LoginResponse,
    PasskeyVerificationResult
)
from src.schemas.user import UserResponse, UserSession, UserCreate
from src.core.config import settings
from src.utils.cache import Cache

class PasskeyService:
    """Service class for PasskeyCredential operations"""



    @staticmethod
    def create_signup_challenge(db: Session, user_phone: int, user_name: str) -> Dict[str, Any]:
        """
        Create a WebAuthn registration challenge for a user
        """

        existing_user = UserService.get_user_by_phone(db, user_phone)
        user_id = existing_user.id if existing_user else None
         
        if not existing_user:
            # If user does not exist, create a new user
            user_data = UserCreate(
                name=user_name,
                phone=user_phone,
                is_active=False
            )
            user_id = UserService.register_user(db, user_data).id
        elif existing_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this phone number already exists and is active"
            )
        
        # Generate challenge using the model method
        challenge_data = generate_registration_options(
            rp_id= settings.FRONTEND_RP_ID,  # Replace with RP ID
            rp_name=settings.PROJECT_NAME,  # Replace with RP name  
            user_id=bytes(user_id),  # need to convert into bytes
            user_name=str(user_phone),  
            user_display_name=user_name,
            attestation="none",
            authenticator_selection=AuthenticatorSelectionCriteria(
                user_verification=UserVerificationRequirement.REQUIRED
            ),
            timeout= settings.CHALLENGE_TIMEOUT,
        )
        
        # Store challenge in session/cache for verification
        # Convert challenge_data to dict for JSON serialization
        challenge_dict = challenge_data.model_dump() if hasattr(challenge_data, 'model_dump') else challenge_data.__dict__
        Cache.set(f"webauthn_signup_challenge_{user_id}", json.dumps(challenge_dict, default=str), expiry=settings.CHALLENGE_CACHE_EXPIRY)
    
        return challenge_data

    @staticmethod
    def verify_signup_response(
        db: Session,
        user_phone: int,
        response_data: SignupResponse
    ) -> PasskeyVerificationResult:
        """
        Verify WebAuthn registration response and create credential
        """
        # Look for user with user_phone
        existing_user = UserService.get_user_by_phone(db, user_phone)

        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Retrieve challenge from cache
        challenge_data_json = Cache.get(f"webauthn_signup_challenge_{existing_user.id}")
        if not challenge_data_json:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Registration challenge expired or not found"
            )
        
        challenge_data = json.loads(challenge_data_json)

        # Verify the registration response
        response = verify_registration_response(
            credential=response_data,
            expected_challenge=challenge_data.get('challenge') if isinstance(challenge_data, dict) else challenge_data,
            expected_rp_id=settings.FRONTEND_RP_ID,  
            expected_origin=settings.FRONTEND_ORIGIN,
            require_user_verification=True  
        )
        
        # Check if credential_id already exists
        existing_credential = db.query(PasskeyCredential).filter(
            PasskeyCredential.credential_id == response.credential_id
        ).first()
        
        if existing_credential:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Credential already exists"
            )
        
        # Create new credential
        credential_data = PasskeyCredentialCreate(
            user_id=existing_user.id,
            credential_id=response.credential_id,
            public_key=response.public_key,
            sign_count=0
        )
        
        credential = PasskeyService.create_credential(db, credential_data)
        
        # Update user status to active
        UserService.activate_user(db, existing_user.id)

        # Clear the challenge from cache
        Cache.delete(f"webauthn_signup_challenge_{existing_user.id}")

        return PasskeyVerificationResult(
            user_id=existing_user.id,
            credential_id=credential.credential_id,
        )

    @staticmethod
    def create_login_challenge(
        db: Session, 
        credential_id: str
    ) -> Dict[str, Any]:
        """
        Create a WebAuthn authentication challenge
        """
        # If credential_id is provided, verify it exists
        credential = db.query(PasskeyCredential).filter(
            PasskeyCredential.credential_id == credential_id
        ).first()
        if not credential:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Credential not found"
            )
        
        # Generate challenge using the model method
        challenge_data = generate_authentication_options(
            rp_id=settings.FRONTEND_RP_ID, 
            user_verification="required",
            timeout=settings.CHALLENGE_TIMEOUT,
            allow_credentials=[{
                "type": "public-key",
                "id": credential.credential_id,
            }],
        )

        # Store challenge in session/cache for verification
        # Convert challenge_data to dict for JSON serialization
        challenge_dict = challenge_data.model_dump() if hasattr(challenge_data, 'model_dump') else challenge_data.__dict__
        Cache.set(f"webauthn_login_challenge_{credential.user_id}", json.dumps(challenge_dict, default=str), expiry=settings.CHALLENGE_CACHE_EXPIRY)     
        
        return challenge_data

    @staticmethod
    def verify_login_response(
        db: Session,
        credential_id: str,
        response_data: LoginResponse
    ) -> PasskeyVerificationResult:
        """
        Verify WebAuthn authentication response
        """
        # Find the credential
        credential = db.query(PasskeyCredential).filter(
            PasskeyCredential.credential_id == credential_id
        ).first()
        
        if not credential:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credential not found"
            )

        # Retrieve challenge from cache
        challenge_data_json = Cache.get(f"webauthn_login_challenge_{credential.user_id}")
        if not challenge_data_json:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Login challenge expired or not found"
            )
        
        challenge_data = json.loads(challenge_data_json)

        # If verification is successful, update sign count
        try:
            # Verify the response
            response = verify_authentication_response(
                credential=response_data,
                expected_challenge=challenge_data.get('challenge') if isinstance(challenge_data, dict) else challenge_data,
                expected_rp_id=settings.FRONTEND_RP_ID,  
                expected_origin=settings.FRONTEND_ORIGIN,
                require_user_verification=True,
                credential_public_key= credential.public_key,
                credential_current_sign_count= credential.sign_count
            )
        
            # Clear the challenge from cache
            Cache.delete(f"webauthn_login_challenge_{credential.user_id}")

            ## NOTE: Might have to think about the sign_count logic here
            # Update sign count in database
            credential.sign_count = response_data.sign_count
            db.commit()

            return PasskeyVerificationResult(
                user_id=credential.user_id,
                credential_id=credential.credential_id,
            )
        except Exception as e:
            # If verification fails, return an error
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Authentication failed: {str(e)}"
            )
        
    # Internal method to create a credential
    @staticmethod
    def create_credential(
        db: Session, 
        credential_data: PasskeyCredentialCreate
    ) -> PasskeyCredential:
        """
        Create a new passkey credential for a user
        """

        # Check is passkey credential already exists
        existing_credential = db.query(PasskeyCredential).filter(
            PasskeyCredential.credential_id == credential_data.credential_id
        ).first()
        if existing_credential:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Credential already exists"
            )
        
        # Create the credential object
        credential = PasskeyCredential(**credential_data.model_dump())
        
        try:
            db.add(credential)
            db.commit()
            db.refresh(credential)
            return credential
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Credential already exists"
            )

    @staticmethod
    def get_user_credentials(db: Session, user_id: int) -> List[PasskeyCredential]:
        """
        Get all credentials for a user
        """
        return db.query(PasskeyCredential).filter(
            PasskeyCredential.user_id == user_id
        ).all()

    @staticmethod
    def get_credential_by_id(db: Session, credential_id: str) -> Optional[PasskeyCredential]:
        """
        Get a credential by its ID
        """
        return db.query(PasskeyCredential).filter(
            PasskeyCredential.credential_id == credential_id
        ).first()

    @staticmethod
    def delete_credential(db: Session, credential_id: str, user_id: int) -> bool:
        """
        Delete a credential (user can only delete their own)
        """
        credential = db.query(PasskeyCredential).filter(
            PasskeyCredential.credential_id == credential_id,
            PasskeyCredential.user_id == user_id
        ).first()
        
        if not credential:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Credential not found"
            )
        
        db.delete(credential)
        db.commit()
        return True

    @staticmethod
    def update_credential(
        db: Session, 
        credential_id: str, 
        user_id: int, 
        update_data: PasskeyCredentialUpdate
    ) -> PasskeyCredential:
        """
        Update a credential (user can only update their own)
        """
        credential = db.query(PasskeyCredential).filter(
            PasskeyCredential.credential_id == credential_id,
            PasskeyCredential.user_id == user_id
        ).first()
        
        if not credential:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Credential not found"
            )
        
        # Update fields
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(credential, field, value)
        
        db.commit()
        db.refresh(credential)
        return credential