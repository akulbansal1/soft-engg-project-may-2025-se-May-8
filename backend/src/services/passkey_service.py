from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from typing import Optional, List, Dict, Any
from datetime import date
from webauthn import generate_registration_options, verify_registration_response, generate_authentication_options, verify_authentication_response, base64url_to_bytes
from webauthn.helpers.structs import AuthenticatorSelectionCriteria, UserVerificationRequirement, RegistrationCredential, AuthenticatorAttestationResponse, AuthenticationCredential, AuthenticatorAssertionResponse
import json
import base64

from src.services.user_service import UserService
from src.services.sms_service import sms_service

from src.models.passkey import PasskeyCredential
from src.models.user import User
from src.schemas.passkey import (
    PasskeyCredentialCreate,
    PasskeyCredentialUpdate,
    SignupResponse,
    LoginResponse,
    PasskeyVerificationResult,
    SerializedWebAuthnChallenge
)
from src.schemas.user import UserResponse, UserSession, UserCreate
from src.core.config import settings
from src.utils.cache import Cache

class PasskeyService:
    """Service class for PasskeyCredential operations"""

    @staticmethod
    def _serialize_challenge_data(challenge_data) -> SerializedWebAuthnChallenge:
        """
        Convert WebAuthn challenge data to JSON-serializable format
        Extracts relevant fields for both registration and authentication challenges
        For registration: challenge, user, rp, pubKeyCredParams, timeout, attestation
        For authentication: challenge, timeout, rpId (as rp), allowCredentials
        Handles base64 encoding of binary data
        """
        if hasattr(challenge_data, 'model_dump'):
            data_dict = challenge_data.model_dump()
        elif hasattr(challenge_data, '__dict__'):
            data_dict = challenge_data.__dict__
        else:
            data_dict = challenge_data

        # Fields that may be present in either registration or authentication challenges
        possible_fields = [
            'challenge', 'user', 'rp', 'pubKeyCredParams', 'timeout', 'attestation',
            'allowCredentials', 'rpId', 'userVerification'
        ]
        
        def convert_bytes(obj):
            if isinstance(obj, bytes):
                return base64.b64encode(obj).decode('utf-8')
            elif hasattr(obj, 'model_dump'):
                return convert_bytes(obj.model_dump())
            elif hasattr(obj, '__dict__'):
                return convert_bytes(obj.__dict__)
            elif isinstance(obj, dict):
                return {k: convert_bytes(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_bytes(item) for item in obj]
            else:
                return obj
        
        result = {}
        for field in possible_fields:
            if field in data_dict:
                result[field] = convert_bytes(data_dict[field])
                
        if 'rpId' in result and 'rp' not in result:
            result['rp'] = {'id': result.pop('rpId')}

        return SerializedWebAuthnChallenge(**result)

    @staticmethod
    def create_signup_challenge(db: Session, user_phone: str, user_name: str, user_dob: Optional[date] = None, user_gender: Optional[str] = None) -> SerializedWebAuthnChallenge:
        """
        Create a WebAuthn registration challenge for a user
        Requires SMS verification before proceeding
        """
        if settings.SMS_VERIFICATION_ENABLED and not sms_service.is_phone_verified(user_phone):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number must be verified via SMS before passkey registration. Please verify your phone number first."
            )

        existing_user = UserService.get_user_by_phone(db, user_phone)
        user_id = existing_user.id if existing_user else None
         
        if not existing_user:
            user_data = UserCreate(
                name=user_name,
                phone=user_phone,
                dob=user_dob,
                gender=user_gender,
                is_active=False
            )
            user_id = UserService.register_user(db, user_data).id
        elif existing_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this phone number already exists and is active"
            )
        
        challenge_data = generate_registration_options(
            rp_id=settings.FRONTEND_RP_ID,
            rp_name=settings.PROJECT_NAME,
            user_id=str(user_id).encode('utf-8'),
            user_name=user_phone,
            user_display_name=user_name,
            attestation="none",
            authenticator_selection=AuthenticatorSelectionCriteria(
                user_verification=UserVerificationRequirement.REQUIRED
            ),
            timeout=settings.CHALLENGE_TIMEOUT,
        )
        
        challenge_dict = PasskeyService._serialize_challenge_data(challenge_data)
        Cache.set(f"webauthn_signup_challenge_{user_id}", json.dumps(challenge_dict.model_dump()), expiry=settings.CHALLENGE_CACHE_EXPIRY)
    
        return challenge_dict

    @staticmethod
    def verify_signup_response(
        db: Session,
        user_phone: str,
        response_data: SignupResponse
    ) -> PasskeyVerificationResult:
        """
        Verify WebAuthn registration response and create credential
        """
        existing_user = UserService.get_user_by_phone(db, user_phone)

        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        challenge_data_json = Cache.get(f"webauthn_signup_challenge_{existing_user.id}")
        if not challenge_data_json:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Registration challenge expired or not found"
            )
        
        challenge_data = json.loads(challenge_data_json)
        raw_credential_id = base64.urlsafe_b64decode(response_data.credential_id + '=' * (-len(response_data.credential_id) % 4))
        expected_challenge =  challenge_data.get('challenge') if isinstance(challenge_data, dict) else challenge_data

        response = verify_registration_response(
            credential=RegistrationCredential(
                id=response_data.credential_id,
                raw_id=raw_credential_id,
                response=AuthenticatorAttestationResponse(
                    client_data_json=base64.urlsafe_b64decode(response_data.client_data_json + '=' * (-len(response_data.client_data_json) % 4)),
                    attestation_object=base64.urlsafe_b64decode(response_data.attestation_object + '=' * (-len(response_data.attestation_object) % 4))
                )
            ),
            expected_challenge=base64.urlsafe_b64decode(expected_challenge + '=' * (-len(expected_challenge) % 4)),
            expected_rp_id=settings.FRONTEND_RP_ID,
            expected_origin=settings.FRONTEND_ORIGIN,
            require_user_verification=True
        )

        response_credential_id = base64.urlsafe_b64encode(response.credential_id).decode('utf-8').rstrip('=')
        response_public_key = base64.b64encode(response.credential_public_key).decode('utf-8') 

        existing_credential = db.query(PasskeyCredential).filter(
            PasskeyCredential.credential_id == response_credential_id
        ).first()
        
        if existing_credential:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Credential already exists"
            )
        
        if response_credential_id != response_data.credential_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Credential ID from response does not match expected format"
            )
      
        credential_data = PasskeyCredentialCreate(
            user_id=existing_user.id,
            credential_id=str(response_credential_id),
            public_key=str(response_public_key),
            sign_count=0
        )
        
        credential = PasskeyService.create_credential(db, credential_data)
        
        UserService.activate_user(db, existing_user.id)

        Cache.delete(f"webauthn_signup_challenge_{existing_user.id}")

        return PasskeyVerificationResult(
            user_id=existing_user.id,
            credential_id=credential.credential_id,
        )

    @staticmethod
    def create_login_challenge(
        db: Session, 
        credential_id: str
    ) -> SerializedWebAuthnChallenge:
        """
        Create a WebAuthn authentication challenge
        """
        credential = db.query(PasskeyCredential).filter(
            PasskeyCredential.credential_id == credential_id
        ).first()
        if not credential:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Credential not found"
            )
 
        challenge_data = generate_authentication_options(
            rp_id=settings.FRONTEND_RP_ID, 
            user_verification="required",
            timeout=settings.CHALLENGE_TIMEOUT,
            allow_credentials=[{
                "type": "public-key",
                "id": credential.credential_id,
            }],
        )

        challenge_dict = PasskeyService._serialize_challenge_data(challenge_data)
        Cache.set(f"webauthn_login_challenge_{credential.user_id}", json.dumps(challenge_dict.model_dump()), expiry=settings.CHALLENGE_CACHE_EXPIRY)     
        
        return challenge_dict

    @staticmethod
    def verify_login_response(
        db: Session,
        credential_id: str,
        response_data: LoginResponse
    ) -> PasskeyVerificationResult:
        """
        Verify WebAuthn authentication response
        """
        
        credential = db.query(PasskeyCredential).filter(
            PasskeyCredential.credential_id == credential_id
        ).first()
        
        if not credential:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credential not found"
            )

        challenge_data_json = Cache.get(f"webauthn_login_challenge_{credential.user_id}")
        if not challenge_data_json:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Login challenge expired or not found"
            )
        
        challenge_data = json.loads(challenge_data_json)
        raw_credential_id = base64.urlsafe_b64decode(response_data.credential_id + '=' * (-len(response_data.credential_id) % 4))
        expected_challenge =  challenge_data.get('challenge') if isinstance(challenge_data, dict) else challenge_data

        response = verify_authentication_response(
            credential=AuthenticationCredential(
                id=response_data.credential_id,
                raw_id=raw_credential_id,
                response=AuthenticatorAssertionResponse(
                    client_data_json=base64.urlsafe_b64decode(response_data.client_data_json + '=' * (-len(response_data.client_data_json) % 4)),
                    authenticator_data=base64.urlsafe_b64decode(response_data.authenticator_data + '=' * (-len(response_data.authenticator_data) % 4)),
                    signature=base64.urlsafe_b64decode(response_data.signature + '=' * (-len(response_data.signature) % 4))
                )
            ),
            expected_challenge=base64.urlsafe_b64decode(expected_challenge + '=' * (-len(expected_challenge) % 4)),
            expected_rp_id=settings.FRONTEND_RP_ID,  
            expected_origin=settings.FRONTEND_ORIGIN,
            credential_public_key=base64.urlsafe_b64decode(credential.public_key + '=' * (-len(credential.public_key) % 4)), 
            credential_current_sign_count=credential.sign_count,
            require_user_verification=True
        )
    
        Cache.delete(f"webauthn_login_challenge_{credential.user_id}")

        ## NOTE: Might have to think about the sign_count logic here
        credential.sign_count = response.new_sign_count
        db.commit()

        return PasskeyVerificationResult(
            user_id=credential.user_id,
            credential_id=credential.credential_id,
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

        existing_credential = db.query(PasskeyCredential).filter(
            PasskeyCredential.credential_id == credential_data.credential_id
        ).first()
        if existing_credential:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Credential already exists"
            )
        
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
      
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(credential, field, value)
        
        db.commit()
        db.refresh(credential)
        return credential