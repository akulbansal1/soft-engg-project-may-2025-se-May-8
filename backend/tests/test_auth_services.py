"""
Authentication Services Tests

Comprehensive tests for UserService and PasskeyService authentication functionality.
Tests cover user registration, login, logout, session management, and passkey operations.
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from src.services.user_service import UserService
from src.services.passkey_service import PasskeyService
from src.schemas.user import UserCreate, UserLogin
from src.schemas.passkey import (
    PasskeyCredentialCreate,
    SignupResponse,
    LoginResponse,
    PasskeyRegistrationRequest,
    PasskeyLoginRequest
)
from src.models.user import User
from src.models.passkey import PasskeyCredential


class TestUserService:
    """Test UserService authentication methods"""

    def test_register_user_success(self, test_db):
        """Test successful user registration"""
        from datetime import date
        user_data = UserCreate(
            name="Test User",
            phone="1234567890",
            dob=date(1995, 6, 15),
            gender="Female",
            is_active=True
        )
        
        user = UserService.register_user(test_db, user_data)
        
        assert user.id is not None
        assert user.name == "Test User"
        assert user.phone == "1234567890"
        assert user.dob == date(1995, 6, 15)
        assert user.gender == "Female"
        assert user.is_active is True
        assert user.created_at is not None

    def test_register_user_duplicate_phone(self, test_db):
        """Test registration fails with duplicate phone number"""
        user_data = UserCreate(
            name="Test User",
            phone="1234567890",
            is_active=True
        )
        
        # Create first user
        UserService.register_user(test_db, user_data)
        
        # Try to create duplicate user
        with pytest.raises(ValueError, match="User with this phone number already exists"):
            UserService.register_user(test_db, user_data)

    def test_register_user_with_optional_fields(self, test_db):
        """Test user registration with optional DOB and gender fields"""
        # Test with no optional fields
        user_data_no_optional = UserCreate(
            name="User Without Optional Fields",
            phone="1111111111",
            is_active=True
        )
        
        user_no_optional = UserService.register_user(test_db, user_data_no_optional)
        
        assert user_no_optional.id is not None
        assert user_no_optional.name == "User Without Optional Fields"
        assert user_no_optional.phone == "1111111111"
        assert user_no_optional.dob is None
        assert user_no_optional.gender is None
        assert user_no_optional.is_active is True

        # Test with only DOB
        from datetime import date
        user_data_with_dob = UserCreate(
            name="User With DOB",
            phone="2222222222",
            dob=date(1985, 12, 25),
            is_active=True
        )
        
        user_with_dob = UserService.register_user(test_db, user_data_with_dob)
        
        assert user_with_dob.dob == date(1985, 12, 25)
        assert user_with_dob.gender is None

        # Test with only gender
        user_data_with_gender = UserCreate(
            name="User With Gender",
            phone="3333333333",
            gender="Non-binary",
            is_active=True
        )
        
        user_with_gender = UserService.register_user(test_db, user_data_with_gender)
        
        assert user_with_gender.dob is None
        assert user_with_gender.gender == "Non-binary"

    def test_login_user_success(self, test_db):
        """Test successful user login"""
        # Create a user
        user_data = UserCreate(
            name="Test User",
            phone="1234567890",
            is_active=True
        )
        created_user = UserService.register_user(test_db, user_data)
        
        # Login user
        login_data = UserLogin(phone="1234567890")
        logged_in_user = UserService.login_user(test_db, login_data)
        
        assert logged_in_user is not None
        assert logged_in_user.id == created_user.id
        assert logged_in_user.phone == "1234567890"

    def test_login_user_not_found(self, test_db):
        """Test login fails for non-existent user"""
        login_data = UserLogin(phone="9999999999")
        user = UserService.login_user(test_db, login_data)
        
        assert user is None

    def test_login_user_inactive(self, test_db):
        """Test login fails for inactive user"""
        # Create inactive user
        user_data = UserCreate(
            name="Test User",
            phone="1234567890",
            is_active=False
        )
        UserService.register_user(test_db, user_data)
        
        # Try to login
        login_data = UserLogin(phone="1234567890")
        user = UserService.login_user(test_db, login_data)
        
        assert user is None

    def test_issue_session(self):
        """Test session token generation"""
        user_id = 123
        
        with patch('src.utils.cache.Cache.set') as mock_cache_set:
            session_data = UserService.issue_session(user_id)
            
            assert "session_token" in session_data
            assert "expires_at" in session_data
            assert isinstance(session_data["expires_at"], str)
            
            # Verify cache was called
            mock_cache_set.assert_called_once()

    def test_validate_session_success(self, test_db):
        """Test successful session validation"""
        session_token = "session_test_token_123"
        user_id = 123
        session_data = {
            "user_id": user_id,
            "expires_at": (datetime.now() + timedelta(hours=1)).isoformat()
        }
        
        with patch('src.utils.cache.Cache.get', return_value=json.dumps(session_data)):
            result = UserService.validate_session(test_db, session_token)
            assert result == user_id

    def test_validate_session_expired(self, test_db):
        """Test session validation fails for expired session"""
        session_token = "session_test_token_123"
        session_data = {
            "user_id": 123,
            "expires_at": (datetime.now() - timedelta(hours=1)).isoformat()
        }
        
        with patch('src.utils.cache.Cache.get', return_value=json.dumps(session_data)):
            with patch('src.utils.cache.Cache.delete') as mock_delete:
                result = UserService.validate_session(test_db, session_token)
                assert result is None
                mock_delete.assert_called_once_with(f"session_{session_token}")

    def test_validate_session_not_found(self, test_db):
        """Test session validation fails for non-existent session"""
        session_token = "session_invalid_token"
        
        with patch('src.utils.cache.Cache.get', return_value=None):
            result = UserService.validate_session(test_db, session_token)
            assert result is None

    def test_get_user_by_session_success(self, test_db):
        """Test getting user by valid session token"""
        # Create a user
        user_data = UserCreate(
            name="Test User",
            phone="1234567890",
            is_active=True
        )
        created_user = UserService.register_user(test_db, user_data)
        
        session_token = "session_test_token_123"
        
        with patch.object(UserService, 'validate_session', return_value=created_user.id):
            user = UserService.get_user_by_session(test_db, session_token)
            
            assert user is not None
            assert user.id == created_user.id
            assert user.name == "Test User"

    def test_get_user_by_session_invalid_token(self, test_db):
        """Test getting user by invalid session token"""
        session_token = "session_invalid_token"
        
        with patch.object(UserService, 'validate_session', return_value=None):
            user = UserService.get_user_by_session(test_db, session_token)
            assert user is None

    def test_logout_user_success(self, test_db):
        """Test successful user logout"""
        user_id = 123
        session_token = "session_test_token_123"
        
        # Mock user for session validation
        mock_user = MagicMock()
        mock_user.id = user_id
        
        with patch('src.utils.cache.Cache.delete') as mock_delete:
            with patch.object(UserService, 'get_user_by_session', return_value=mock_user):
                result = UserService.logout_user(test_db, user_id, session_token)
                
                assert result is True
                mock_delete.assert_called_once_with(f"session_{session_token}")

    def test_logout_user_by_token_success(self):
        """Test successful logout by token only"""
        session_token = "session_test_token_123"
        
        with patch('src.utils.cache.Cache.delete') as mock_delete:
            result = UserService.logout_user_by_token(session_token)
            
            assert result is True
            mock_delete.assert_called_once_with(f"session_{session_token}")

    def test_activate_user_success(self, test_db):
        """Test successful user activation"""
        # Create inactive user
        user_data = UserCreate(
            name="Test User",
            phone="1234567890",
            is_active=False
        )
        created_user = UserService.register_user(test_db, user_data)
        
        # Activate user
        result = UserService.activate_user(test_db, created_user.id)
        
        assert result is True
        test_db.refresh(created_user)
        assert created_user.is_active is True

    def test_activate_user_not_found(self, test_db):
        """Test user activation fails for non-existent user"""
        result = UserService.activate_user(test_db, 99999)
        assert result is False

    def test_get_user_by_phone_success(self, test_db):
        """Test getting user by phone number"""
        user_data = UserCreate(
            name="Test User",
            phone="1234567890",
            is_active=True
        )
        created_user = UserService.register_user(test_db, user_data)
        
        found_user = UserService.get_user_by_phone(test_db, "1234567890")
        
        assert found_user is not None
        assert found_user.id == created_user.id
        assert found_user.phone == "1234567890"

    def test_get_user_by_phone_not_found(self, test_db):
        """Test getting user by non-existent phone number"""
        user = UserService.get_user_by_phone(test_db, "9999999999")
        assert user is None

    def test_get_user_by_id_success(self, test_db):
        """Test getting user by ID"""
        user_data = UserCreate(
            name="Test User",
            phone="1234567890",
            is_active=True
        )
        created_user = UserService.register_user(test_db, user_data)
        
        found_user = UserService.get_user_by_id(test_db, created_user.id)
        
        assert found_user is not None
        assert found_user.id == created_user.id
        assert found_user.phone == "1234567890"

    def test_get_user_by_id_not_found(self, test_db):
        """Test getting user by non-existent ID"""
        user = UserService.get_user_by_id(test_db, 99999)
        assert user is None


class TestPasskeyService:
    """Test PasskeyService authentication methods"""

    def test_create_signup_challenge_new_user(self, test_db):
        """Test creating signup challenge for new user"""
        user_phone = "9876543210"
        user_name = "Test User"
        
        # Create mock serialized challenge response
        from src.schemas.passkey import SerializedWebAuthnChallenge, WebAuthnUser, WebAuthnRelyingParty
        mock_serialized_challenge = SerializedWebAuthnChallenge(
            challenge="test_challenge_base64",
            user=WebAuthnUser(id="dGVzdF9pZA==", name=user_phone, display_name=user_name),
            rp=WebAuthnRelyingParty(name="Test RP", id="test.local"),
            timeout=300000,
            attestation="none"
        )
        
        with patch('src.services.passkey_service.generate_registration_options') as mock_gen_options:
            with patch('src.services.passkey_service.PasskeyService._serialize_challenge_data', return_value=mock_serialized_challenge) as mock_serialize:
                with patch('src.utils.cache.Cache.set') as mock_cache_set:
                    mock_challenge_data = MagicMock()
                    mock_gen_options.return_value = mock_challenge_data
                    
                    result = PasskeyService.create_signup_challenge(test_db, user_phone, user_name)
                    
                    # Verify user was created
                    user = UserService.get_user_by_phone(test_db, user_phone)
                    assert user is not None
                    assert user.name == user_name
                    assert user.phone == user_phone
                    assert user.is_active is False  # Should be inactive until passkey registration
                    
                    # Verify the result is the mocked serialized challenge
                    assert result == mock_serialized_challenge
                    assert result.challenge == "test_challenge_base64"
                    assert result.user.name == user_phone
                    assert result.user.display_name == user_name
                mock_gen_options.assert_called_once()
                mock_cache_set.assert_called_once()
                assert result == PasskeyService._serialize_challenge_data(mock_challenge_data)

    def test_create_signup_challenge_existing_inactive_user(self, test_db):
        """Test creating signup challenge for existing inactive user"""
        # Create inactive user
        user_data = UserCreate(
            name="Test User",
            phone="8888888888",
            is_active=False
        )
        created_user = UserService.register_user(test_db, user_data)
        
        # Create mock serialized challenge response
        from src.schemas.passkey import SerializedWebAuthnChallenge, WebAuthnUser, WebAuthnRelyingParty
        mock_serialized_challenge = SerializedWebAuthnChallenge(
            challenge="test_challenge_base64",
            user=WebAuthnUser(id="dGVzdF9pZA==", name="8888888888", display_name="Test User"),
            rp=WebAuthnRelyingParty(name="Test RP", id="test.local"),
            timeout=300000,
            attestation="none"
        )
        
        with patch('src.services.passkey_service.generate_registration_options') as mock_gen_options:
            with patch('src.services.passkey_service.PasskeyService._serialize_challenge_data', return_value=mock_serialized_challenge):
                with patch('src.utils.cache.Cache.set'):
                    mock_challenge_data = MagicMock()
                    mock_gen_options.return_value = mock_challenge_data
                    
                    result = PasskeyService.create_signup_challenge(test_db, "8888888888", "Test User")
                    
                    # Should use existing user and return serialized challenge
                    assert result == mock_serialized_challenge
                    mock_gen_options.assert_called_once()

    def test_create_signup_challenge_existing_active_user(self, test_db):
        """Test creating signup challenge fails for existing active user"""
        # Create active user
        user_data = UserCreate(
            name="Test User",
            phone="7777777777",
            is_active=True
        )
        UserService.register_user(test_db, user_data)
        
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            PasskeyService.create_signup_challenge(test_db, "7777777777", "Test User")
        
        assert exc_info.value.status_code == 400
        assert "already exists and is active" in str(exc_info.value.detail)

    def test_create_signup_challenge_with_optional_fields(self, test_db):
        """Test creating signup challenge for new user with optional DOB and gender fields"""
        from datetime import date
        user_phone = "5555555555"
        user_name = "Jane Doe"
        user_dob = date(1992, 5, 20)
        user_gender = "Female"
        
        # Create mock serialized challenge response
        from src.schemas.passkey import SerializedWebAuthnChallenge, WebAuthnUser, WebAuthnRelyingParty
        mock_serialized_challenge = SerializedWebAuthnChallenge(
            challenge="test_challenge_base64",
            user=WebAuthnUser(id="dGVzdF9pZA==", name=user_phone, display_name=user_name),
            rp=WebAuthnRelyingParty(name="Test RP", id="test.local"),
            timeout=300000,
            attestation="none"
        )
        
        with patch('src.services.passkey_service.generate_registration_options') as mock_gen_options:
            with patch('src.services.passkey_service.PasskeyService._serialize_challenge_data', return_value=mock_serialized_challenge):
                with patch('src.utils.cache.Cache.set') as mock_cache_set:
                    mock_challenge_data = MagicMock()
                    mock_gen_options.return_value = mock_challenge_data
                    
                    result = PasskeyService.create_signup_challenge(
                        test_db, user_phone, user_name, user_dob, user_gender
                    )
                    
                    # Verify user was created with optional fields
                    user = UserService.get_user_by_phone(test_db, user_phone)
                    assert user is not None
                    assert user.name == user_name
                    assert user.phone == user_phone
                    assert user.dob == user_dob
                    assert user.gender == user_gender
                    assert user.is_active is False  # Should be inactive until passkey registration
                    
                    # Verify the result is the mocked serialized challenge
                    assert result == mock_serialized_challenge
                    mock_gen_options.assert_called_once()
                    mock_cache_set.assert_called_once()

    def test_create_signup_challenge_with_partial_optional_fields(self, test_db):
        """Test creating signup challenge with only some optional fields"""
        from datetime import date
        user_phone = "6666666666"
        user_name = "John Smith"
        user_dob = date(1985, 8, 15)
        
        # Create mock serialized challenge response
        from src.schemas.passkey import SerializedWebAuthnChallenge, WebAuthnUser, WebAuthnRelyingParty
        mock_serialized_challenge = SerializedWebAuthnChallenge(
            challenge="test_challenge_base64",
            user=WebAuthnUser(id="dGVzdF9pZA==", name=user_phone, display_name=user_name),
            rp=WebAuthnRelyingParty(name="Test RP", id="test.local"),
            timeout=300000,
            attestation="none"
        )
        
        with patch('src.services.passkey_service.generate_registration_options') as mock_gen_options:
            with patch('src.services.passkey_service.PasskeyService._serialize_challenge_data', return_value=mock_serialized_challenge):
                with patch('src.utils.cache.Cache.set'):
                    mock_challenge_data = MagicMock()
                    mock_gen_options.return_value = mock_challenge_data
                    
                    # Test with only DOB, no gender
                    result = PasskeyService.create_signup_challenge(
                        test_db, user_phone, user_name, user_dob, None
                    )
                    
                    # Verify user was created with partial optional fields
                    user = UserService.get_user_by_phone(test_db, user_phone)
                    assert user is not None
                    assert user.name == user_name
                    assert user.phone == user_phone
                    assert user.dob == user_dob
                    assert user.gender is None
                    assert user.is_active is False
                    
                    # Verify the result is the mocked serialized challenge
                    assert result == mock_serialized_challenge

    def test_create_login_challenge_success(self, test_db):
        """Test creating login challenge for existing credential"""
        # Create user and credential
        user_data = UserCreate(
            name="Test User",
            phone="5555555555",
            is_active=True
        )
        user = UserService.register_user(test_db, user_data)
        
        credential_data = PasskeyCredentialCreate(
            user_id=user.id,
            credential_id="test_credential_id",
            public_key="test_public_key",
            sign_count=0
        )
        credential = PasskeyService.create_credential(test_db, credential_data)
        
        # Create mock serialized challenge response
        from src.schemas.passkey import SerializedWebAuthnChallenge, WebAuthnUser, WebAuthnRelyingParty
        mock_serialized_challenge = SerializedWebAuthnChallenge(
            challenge="test_challenge_base64",
            user=WebAuthnUser(id="dGVzdF9pZA==", name="5555555555", display_name="Test User"),
            rp=WebAuthnRelyingParty(name="Test RP", id="test.local"),
            timeout=300000,
            attestation="none"
        )
        
        with patch('src.services.passkey_service.generate_authentication_options') as mock_gen_options:
            with patch('src.services.passkey_service.PasskeyService._serialize_challenge_data', return_value=mock_serialized_challenge):
                with patch('src.utils.cache.Cache.set') as mock_cache_set:
                    mock_challenge_data = MagicMock()
                    mock_gen_options.return_value = mock_challenge_data
                    
                    result = PasskeyService.create_login_challenge(test_db, credential.credential_id)
                    
                    assert result == mock_serialized_challenge
                    mock_gen_options.assert_called_once()
                    mock_cache_set.assert_called_once()

    def test_create_login_challenge_credential_not_found(self, test_db):
        """Test creating login challenge fails for non-existent credential"""
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            PasskeyService.create_login_challenge(test_db, "non_existent_credential")
        
        assert exc_info.value.status_code == 404
        assert "Credential not found" in str(exc_info.value.detail)

    def test_create_credential_success(self, test_db):
        """Test successful credential creation"""
        # Create user first
        user_data = UserCreate(
            name="Test User",
            phone="1234567890",
            is_active=True
        )
        user = UserService.register_user(test_db, user_data)
        
        credential_data = PasskeyCredentialCreate(
            user_id=user.id,
            credential_id="test_credential_id",
            public_key="test_public_key",
            sign_count=0
        )
        
        credential = PasskeyService.create_credential(test_db, credential_data)
        
        assert credential.id is not None
        assert credential.user_id == user.id
        assert credential.credential_id == "test_credential_id"
        assert credential.public_key == "test_public_key"
        assert credential.sign_count == 0

    def test_create_credential_duplicate(self, test_db):
        """Test credential creation fails for duplicate credential_id"""
        # Create user first
        user_data = UserCreate(
            name="Test User",
            phone="1234567890",
            is_active=True
        )
        user = UserService.register_user(test_db, user_data)
        
        credential_data = PasskeyCredentialCreate(
            user_id=user.id,
            credential_id="test_credential_id",
            public_key="test_public_key",
            sign_count=0
        )
        
        # Create first credential
        PasskeyService.create_credential(test_db, credential_data)
        
        # Try to create duplicate
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            PasskeyService.create_credential(test_db, credential_data)
        
        assert exc_info.value.status_code == 409
        assert "Credential already exists" in str(exc_info.value.detail)

    def test_get_user_credentials(self, test_db):
        """Test getting all credentials for a user"""
        # Create user
        user_data = UserCreate(
            name="Test User",
            phone="1234567890",
            is_active=True
        )
        user = UserService.register_user(test_db, user_data)
        
        # Create multiple credentials
        for i in range(3):
            credential_data = PasskeyCredentialCreate(
                user_id=user.id,
                credential_id=f"test_credential_id_{i}",
                public_key=f"test_public_key_{i}",
                sign_count=0
            )
            PasskeyService.create_credential(test_db, credential_data)
        
        credentials = PasskeyService.get_user_credentials(test_db, user.id)
        
        assert len(credentials) == 3
        for i, cred in enumerate(credentials):
            assert cred.user_id == user.id
            assert cred.credential_id == f"test_credential_id_{i}"

    def test_get_credential_by_id_success(self, test_db):
        """Test getting credential by ID"""
        # Create user and credential
        user_data = UserCreate(
            name="Test User",
            phone="1234567890",
            is_active=True
        )
        user = UserService.register_user(test_db, user_data)
        
        credential_data = PasskeyCredentialCreate(
            user_id=user.id,
            credential_id="test_credential_id",
            public_key="test_public_key",
            sign_count=0
        )
        created_credential = PasskeyService.create_credential(test_db, credential_data)
        
        found_credential = PasskeyService.get_credential_by_id(test_db, "test_credential_id")
        
        assert found_credential is not None
        assert found_credential.id == created_credential.id
        assert found_credential.credential_id == "test_credential_id"

    def test_get_credential_by_id_not_found(self, test_db):
        """Test getting credential by non-existent ID"""
        credential = PasskeyService.get_credential_by_id(test_db, "non_existent_credential")
        assert credential is None

    @patch('src.services.passkey_service.verify_registration_response')
    def test_verify_signup_response_success(self, mock_verify_reg, test_db):
        """Test successful signup response verification"""
        # Create user
        user_data = UserCreate(
            name="Test User",
            phone="1234567890",
            is_active=False
        )
        user = UserService.register_user(test_db, user_data)
        
        # Mock verification response
        mock_response = MagicMock()
        mock_response.credential_id = "test_credential_id"
        mock_response.credential_public_key = "test_public_key"
        mock_verify_reg.return_value = mock_response
        
        # Mock cache with challenge data
        challenge_data = "test_challenge_data"
        with patch('src.utils.cache.Cache.get', return_value=json.dumps(challenge_data)):
            with patch('src.utils.cache.Cache.delete') as mock_cache_delete:
                response_data = SignupResponse(
                    credential_id="test_credential_id",
                    public_key="test_public_key",
                    attestation_object="test_attestation",
                    client_data_json="test_client_data"
                )
                
                result = PasskeyService.verify_signup_response(test_db, "1234567890", response_data)
                
                assert result.user_id == user.id
                assert result.credential_id == "test_credential_id"

                # Verify user was activated
                test_db.refresh(user)
                assert user.is_active is True
                
                # Verify cache was cleared
                mock_cache_delete.assert_called_once()

    def test_verify_signup_response_user_not_found(self, test_db):
        """Test signup response verification fails for non-existent user"""
        response_data = SignupResponse(
            credential_id="test_credential_id",
            public_key="test_public_key",
            attestation_object="test_attestation",
            client_data_json="test_client_data"
        )
        
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            PasskeyService.verify_signup_response(test_db, "9999999999", response_data)
        
        assert exc_info.value.status_code == 404
        assert "User not found" in str(exc_info.value.detail)

    def test_verify_signup_response_challenge_expired(self, test_db):
        """Test signup response verification fails for expired challenge"""
        # Create user
        user_data = UserCreate(
            name="Test User",
            phone="1234567890",
            is_active=False
        )
        UserService.register_user(test_db, user_data)
        
        response_data = SignupResponse(
            credential_id="test_credential_id",
            public_key="test_public_key",
            attestation_object="test_attestation",
            client_data_json="test_client_data"
        )
        
        # Mock cache with no challenge data (expired)
        with patch('src.utils.cache.Cache.get', return_value=None):
            from fastapi import HTTPException
            with pytest.raises(HTTPException) as exc_info:
                PasskeyService.verify_signup_response(test_db, "1234567890", response_data)
            
            assert exc_info.value.status_code == 400
            assert "Registration challenge expired" in str(exc_info.value.detail)

    @patch('src.services.passkey_service.verify_authentication_response')
    def test_verify_login_response_success(self, mock_verify_auth, test_db):
        """Test successful login response verification"""
        # Create user and credential
        user_data = UserCreate(
            name="Test User",
            phone="1234567890",
            is_active=True
        )
        user = UserService.register_user(test_db, user_data)
        
        credential_data = PasskeyCredentialCreate(
            user_id=user.id,
            credential_id="test_credential_id",
            public_key="test_public_key",
            sign_count=0
        )
        credential = PasskeyService.create_credential(test_db, credential_data)
        
        # Mock verification response
        mock_verify_auth.return_value = True
        
        # Mock cache with challenge data
        challenge_data = "test_challenge_data"
        with patch('src.utils.cache.Cache.get', return_value=json.dumps(challenge_data)):
            with patch('src.utils.cache.Cache.delete') as mock_cache_delete:
                response_data = LoginResponse(
                    credential_id="test_credential_id",
                    signature="test_signature",
                    client_data="test_client_data",
                    authenticator_data="test_auth_data",
                    sign_count=1
                )
                
                result = PasskeyService.verify_login_response(test_db, "test_credential_id", response_data)
                
           
                assert result.user_id == user.id
                assert result.credential_id == "test_credential_id"
                
                # Verify cache was cleared
                mock_cache_delete.assert_called_once()

    def test_verify_login_response_credential_not_found(self, test_db):
        """Test login response verification fails for non-existent credential"""
        response_data = LoginResponse(
            credential_id="non_existent_credential",
            signature="test_signature",
            client_data="test_client_data",
            authenticator_data="test_auth_data",
            sign_count=1
        )

        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
                PasskeyService.verify_login_response(test_db, "non_existent_credential", response_data)

                assert exc_info.value.status_code == 404
                assert "Credential not found" in str(exc_info.value.detail)
    

    def test_verify_login_response_challenge_expired(self, test_db):
        """Test login response verification fails for expired challenge"""
        # Create user and credential
        user_data = UserCreate(
            name="Test User",
            phone="1234567890",
            is_active=True
        )
        user = UserService.register_user(test_db, user_data)
        
        credential_data = PasskeyCredentialCreate(
            user_id=user.id,
            credential_id="test_credential_id",
            public_key="test_public_key",
            sign_count=0
        )
        credential = PasskeyService.create_credential(test_db, credential_data)
        
        response_data = LoginResponse(
            credential_id="test_credential_id",
            signature="test_signature",
            client_data="test_client_data",
            authenticator_data="test_auth_data",
            sign_count=1
        )
        
        # Mock cache with no challenge data (expired)
        with patch('src.utils.cache.Cache.get', return_value=None):
            from fastapi import HTTPException
            with pytest.raises(HTTPException) as exc_info:
                PasskeyService.verify_login_response(test_db, "test_credential_id", response_data)
            
            assert exc_info.value.status_code == 400
            assert "Login challenge expired" in str(exc_info.value.detail)
