"""
API endpoint tests for authentication-related endpoints with realistic mock WebAuthn data.
This file contains comprehensive tests for passkey registration, login, and session management.
"""
import pytest
import json
import base64
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from src.schemas.user import UserCreate
from src.schemas.passkey import PasskeyCredentialCreate, PasskeyVerificationResult
from src.services.user_service import UserService
from src.services.passkey_service import PasskeyService


class TestPasskeyRegistrationAPI:
    """Test passkey registration API endpoints"""

    def test_create_registration_challenge_new_user(self, client, test_db):
        """Test creating registration challenge for new user"""
        request_data = {
            "user_phone": "1234567890",
            "user_name": "Test User"
        }
        
        with patch('src.services.passkey_service.PasskeyService.create_signup_challenge') as mock_challenge:
            # Mock WebAuthn challenge response as dictionary
            mock_challenge_data = {
                "challenge": base64.b64encode(b"test_challenge").decode(),
                "user": {"id": "test_user_id", "name": "Test User"},
                "rp": {"id": "localhost", "name": "Test RP"},
                "pubKeyCredParams": [{"type": "public-key", "alg": -7}],
                "timeout": 60000,
                "attestation": "direct"
            }
            mock_challenge.return_value = mock_challenge_data
            
            response = client.post("/api/v1/auth/passkey/register/challenge", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert "challenge" in data

    def test_create_registration_challenge_existing_inactive_user(self, client, test_db):
        """Test creating registration challenge for existing inactive user"""
        # Create inactive user first
        user_data = UserCreate(name="Test User", phone="1234567890", is_active=False)
        UserService.register_user(test_db, user_data)
        
        request_data = {
            "user_phone": "1234567890",
            "user_name": "Test User"
        }
        
        with patch('src.services.passkey_service.PasskeyService.create_signup_challenge') as mock_challenge:
            mock_challenge_data = {
                "challenge": base64.b64encode(b"test_challenge").decode(),
                "user": {"id": "test_user_id", "name": "Test User"},
                "rp": {"id": "localhost", "name": "Test RP"}
            }
            mock_challenge.return_value = mock_challenge_data
            
            response = client.post("/api/v1/auth/passkey/register/challenge", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert "challenge" in data

    def test_create_registration_challenge_existing_active_user(self, client, test_db):
        """Test creating registration challenge fails for existing active user"""
        # Create active user first
        user_data = UserCreate(name="Test User", phone="1234567890", is_active=True)
        UserService.register_user(test_db, user_data)
        
        request_data = {
            "user_phone": "1234567890",
            "user_name": "Test User"
        }
        
        response = client.post("/api/v1/auth/passkey/register/challenge", json=request_data)
        
        # Should fail because user is already active
        assert response.status_code >= 400

    def test_create_registration_challenge_with_optional_fields(self, client):
        """Test creating registration challenge with optional DOB and gender fields"""
        request_data = {
            "user_phone": "9999999999",
            "user_name": "Alice Cooper",
            "user_dob": "1990-03-15",
            "user_gender": "Female"
        }
        
        with patch('src.services.passkey_service.PasskeyService.create_signup_challenge') as mock_challenge:
            # Mock WebAuthn challenge response as dictionary
            mock_challenge_data = {
                "challenge": base64.b64encode(b"test_challenge").decode(),
                "user": {"id": "test_user_id", "name": "Alice Cooper"},
                "rp": {"id": "localhost", "name": "Test RP"},
                "pubKeyCredParams": [{"type": "public-key", "alg": -7}],
                "timeout": 60000,
                "attestation": "direct"
            }
            mock_challenge.return_value = mock_challenge_data
            
            response = client.post("/api/v1/auth/passkey/register/challenge", json=request_data)
            
            assert response.status_code == 200
            assert "challenge" in response.json()
            
            # Verify the service was called with the optional fields
            from datetime import date
            mock_challenge.assert_called_once()
            call_args = mock_challenge.call_args
            # Check positional arguments
            assert call_args[0][1] == "9999999999"  # user_phone
            assert call_args[0][2] == "Alice Cooper"  # user_name
            assert call_args[0][3] == date(1990, 3, 15)  # user_dob
            assert call_args[0][4] == "Female"  # user_gender

    def test_create_registration_challenge_minimal_fields_only(self, client):
        """Test creating registration challenge with only required fields"""
        request_data = {
            "user_phone": "8888888888",
            "user_name": "Bob Builder"
        }
        
        with patch('src.services.passkey_service.PasskeyService.create_signup_challenge') as mock_challenge:
            mock_challenge_data = {
                "challenge": base64.b64encode(b"test_challenge").decode(),
                "user": {"id": "test_user_id", "name": "Bob Builder"},
                "rp": {"id": "localhost", "name": "Test RP"},
                "pubKeyCredParams": [{"type": "public-key", "alg": -7}],
                "timeout": 60000,
                "attestation": "direct"
            }
            mock_challenge.return_value = mock_challenge_data
            
            response = client.post("/api/v1/auth/passkey/register/challenge", json=request_data)
            
            assert response.status_code == 200
            assert "challenge" in response.json()
            
            # Verify the service was called with None for optional fields
            mock_challenge.assert_called_once()
            call_args = mock_challenge.call_args
            # Check positional arguments
            assert call_args[0][1] == "8888888888"  # user_phone
            assert call_args[0][2] == "Bob Builder"  # user_name
            assert call_args[0][3] is None  # user_dob
            assert call_args[0][4] is None  # user_gender

    def test_verify_registration_response_success(self, client, test_db):
        """Test successful registration verification"""
        # Create inactive user first
        user_data = UserCreate(name="Test User", phone="1234567890", is_active=False)
        user = UserService.register_user(test_db, user_data)

        request_data = {
            "user_phone": "1234567890",
            "user_name": "Test User"
        }

        response_data = {
            "credential_id": "test_credential_id",
            "public_key": "test_public_key", 
            "attestation_object": base64.b64encode(b"test_attestation").decode(),
            "client_data_json": base64.b64encode(b'{"type":"webauthn.create"}').decode()
        }

        with patch('src.services.passkey_service.PasskeyService.verify_signup_response') as mock_verify:
            # Mock successful verification result
            mock_result = PasskeyVerificationResult(      
                user_id=user.id,
                credential_id="test_credential_id",
            )
            mock_verify.return_value = mock_result

            with patch('src.services.user_service.UserService.issue_session') as mock_session:
                # Mock session creation
                session_data = {
                    "user_id": user.id,
                    "session_token": "test_session_token",
                    "expires_at": (datetime.now() + timedelta(hours=24)).isoformat()
                }
                mock_session.return_value = session_data

                # FastAPI expects multiple body parameters as nested JSON
                full_request = {
                    "request": request_data,
                    "response_data": response_data
                }
                response = client.post(
                    "/api/v1/auth/passkey/register/verify",
                    json=full_request
                )

                assert response.status_code >= 200
                data = response.json()
                assert data["user_id"] == user.id
                assert data["credential_id"] == "test_credential_id"
                assert "session_expires_at" in data

                # Check session cookie was set
                assert "session_token" in response.headers['set-cookie']

    def test_verify_registration_response_user_not_found(self, client, test_db):
        """Test registration verification fails for non-existent user"""
        request_data = {
            "user_phone": "9999999999",
            "user_name": "Non-existent User"
        }

        response_data = {
            "credential_id": "test_credential_id",
            "public_key": "test_public_key",
            "attestation_object": base64.b64encode(b"test_attestation").decode(),
            "client_data_json": base64.b64encode(b'{"type":"webauthn.create"}').decode()
        }

        # FastAPI expects multiple body parameters as nested JSON
        full_request = {
            "request": request_data,
            "response_data": response_data
        }
        response = client.post(
            "/api/v1/auth/passkey/register/verify",
            json=full_request
        )

        # Should return an error (likely 404 or 422)
        assert response.status_code >= 400


class TestPasskeyLoginAPI:
    """Test passkey login API endpoints"""

    def setup_user_with_credential(self, test_db):
        """Helper to create user with passkey credential"""
        # Create active user
        user_data = UserCreate(name="Test User", phone="1234567890", is_active=True)
        user = UserService.register_user(test_db, user_data)
        
        # Create credential
        credential_data = PasskeyCredentialCreate(
            user_id=user.id,
            credential_id="test_credential_id",
            public_key="test_public_key",
            sign_count=0
        )
        credential = PasskeyService.create_credential(test_db, credential_data)
        
        return user, credential

    def test_create_login_challenge_success(self, client, test_db):
        """Test creating login challenge for existing credential"""
        user, credential = self.setup_user_with_credential(test_db)

        request_data = {
            "credential_id": credential.credential_id
        }

        with patch('src.services.passkey_service.PasskeyService.create_login_challenge') as mock_challenge:
            # Mock challenge response as a dictionary (not MagicMock)
            mock_challenge_data = {
                "challenge": base64.b64encode(b"test_challenge").decode(),
                "allowCredentials": [{"id": credential.credential_id, "type": "public-key"}],
                "rpId": "localhost",
                "userVerification": "preferred",
                "timeout": 60000
            }
            mock_challenge.return_value = mock_challenge_data

            response = client.post("/api/v1/auth/passkey/login/challenge", json=request_data)

            assert response.status_code == 200
            data = response.json()
            assert "challenge" in data
            assert data["challenge"] == mock_challenge_data["challenge"]

    def test_create_login_challenge_credential_not_found(self, client, test_db):
        """Test creating login challenge fails for non-existent credential"""
        request_data = {
            "credential_id": "non_existent_credential"
        }

        response = client.post("/api/v1/auth/passkey/login/challenge", json=request_data)

        assert response.status_code == 404
        data = response.json()
        assert "Not found" in data["detail"]

    def test_verify_login_response_success(self, client, test_db):
        """Test successful login verification"""
        user, credential = self.setup_user_with_credential(test_db)

        request_data = {
            "credential_id": credential.credential_id
        }

        response_data = {
            "credential_id": credential.credential_id,
            "signature": base64.b64encode(b"test_signature").decode(),
            "client_data": base64.b64encode(b'{"type":"webauthn.get"}').decode(),
            "authenticator_data": base64.b64encode(b"test_auth_data").decode(),
            "sign_count": 1
        }

        with patch('src.services.passkey_service.PasskeyService.verify_login_response') as mock_verify:
            # Mock successful verification result
            mock_result = PasskeyVerificationResult(
                user_id=user.id,
                credential_id=credential.credential_id,
            )
            mock_verify.return_value = mock_result

            with patch('src.services.user_service.UserService.issue_session') as mock_session:
                # Mock session creation
                session_data = {
                    "user_id": user.id,
                    "session_token": "test_session_token",
                    "expires_at": (datetime.now() + timedelta(hours=24)).isoformat()
                }
                mock_session.return_value = session_data

                # FastAPI expects multiple body parameters as nested JSON
                full_request = {
                    "request": request_data,
                    "response_data": response_data
                }
                response = client.post(
                    "/api/v1/auth/passkey/login/verify",
                    json=full_request
                )

                assert response.status_code == 200
                data = response.json()
                assert data["user_id"] == user.id

    def test_verify_login_response_credential_not_found(self, client, test_db):
        """Test login verification fails for non-existent credential"""
        request_data = {
            "credential_id": "non_existent_credential"
        }

        response_data = {
            "credential_id": "non_existent_credential",
            "signature": base64.b64encode(b"test_signature").decode(),
            "client_data": base64.b64encode(b'{"type":"webauthn.get"}').decode(),
            "authenticator_data": base64.b64encode(b"test_auth_data").decode(),
            "sign_count": 1
        }

        # FastAPI expects multiple body parameters as nested JSON
        full_request = {
            "request": request_data,
            "response_data": response_data
        }
        response = client.post(
            "/api/v1/auth/passkey/login/verify",
            json=full_request
        )

        assert response.status_code >= 400


class TestAuthenticatedEndpoints:
    """Test endpoints that require authentication"""

    def create_authenticated_session(self, client, test_db):
        """Helper to create an authenticated session"""
        user_data = UserCreate(name="Test User", phone="1234567890", is_active=True)
        user = UserService.register_user(test_db, user_data)
        
        session_data = UserService.issue_session(user.id)
        session_token = session_data["session_token"]
        
        # Set session cookie in the client
        client.cookies.set("session_token", session_token)
        
        return user, session_token

    def test_logout_success(self, client, test_db):
        """Test successful logout"""
        user, session_token = self.create_authenticated_session(client, test_db)

        with patch('src.services.user_service.UserService.logout_user_by_token') as mock_logout:
           
            mock_logout.return_value = True
            
            response = client.post("/api/v1/auth/logout")

            assert response.status_code == 200
            data = response.json()
            assert data["message"] == "Logout successful"

            # Cookie should be cleared (empty value)
            assert "session_token=""" in response.headers['set-cookie']

    def test_logout_no_session_token(self, client, test_db):
        """Test logout fails without session token"""
        response = client.post("/api/v1/auth/logout")

        assert response.status_code == 401
        data = response.json()
        assert "No session token provided" in data["detail"]

    def test_get_current_user_info_success(self, client, test_db):
        """Test getting current user info with valid session"""
        user, session_token = self.create_authenticated_session(client, test_db)

        response = client.get("/api/v1/auth/me")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user.id
        assert data["name"] == user.name
        assert data["phone"] == user.phone

    def test_get_current_user_info_no_auth(self, client, test_db):
        """Test getting current user info fails without authentication"""
        response = client.get("/api/v1/auth/me")

        assert response.status_code == 401
        data = response.json()
        assert "No session token provided" in data["detail"]

    def test_get_user_passkeys_success(self, client, test_db):
        """Test getting user's passkey credentials"""
        user, session_token = self.create_authenticated_session(client, test_db)

        # Create some credentials for the user
        credential_data = PasskeyCredentialCreate(
            user_id=user.id,
            credential_id="test_credential_1",
            public_key="test_public_key_1",
            sign_count=0
        )
        credential = PasskeyService.create_credential(test_db, credential_data)

        response = client.get(f"/api/v1/auth/passkey/user/{user.id}")

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert data[0]["credential_id"] == "test_credential_1"
        assert data[0]["user_id"] == user.id

    def test_get_user_passkeys_wrong_user(self, client, test_db):
        """Test getting another user's passkeys fails"""
        user, session_token = self.create_authenticated_session(client, test_db)

        # Try to access another user's credentials
        other_user_id = user.id + 1
        response = client.get(f"/api/v1/auth/passkey/user/{other_user_id}")

        assert response.status_code == 403  # Should be forbidden due to ownership check
        data = response.json()
        assert "You can only access your own resources" in data["detail"]


class TestUsersAPI:
    """Test user management API endpoints"""

    def create_authenticated_session(self, client, test_db):
        """Helper to create an authenticated session"""
        user_data = UserCreate(name="Test User", phone="1234567890", is_active=True)
        user = UserService.register_user(test_db, user_data)
        
        session_data = UserService.issue_session(user.id)
        session_token = session_data["session_token"]
        
        # Set session cookie in the client
        client.cookies.set("session_token", session_token)
        
        return user, session_token

    def test_get_all_users_authenticated(self, client, test_db):
        """Test getting all users with authentication"""
        user, session_token = self.create_authenticated_session(client, test_db)

        # Create additional users
        for i in range(3):
            user_data = UserCreate(name=f"User {i}", phone=f"123456789{i+1}", is_active=True)
            UserService.register_user(test_db, user_data)

        response = client.get("/api/v1/users/")

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 4  # Original user + 3 new users
        assert all("id" in user for user in data)
        assert all("name" in user for user in data)

    def test_get_all_users_unauthenticated(self, client, test_db):
        """Test getting all users fails without authentication"""
        response = client.get("/api/v1/users/")

        assert response.status_code == 401
        data = response.json()
        assert "No session token provided" in data["detail"]

    def test_get_user_by_id_own_user(self, client, test_db):
        """Test getting user by ID for own user"""
        user, session_token = self.create_authenticated_session(client, test_db)

        response = client.get(f"/api/v1/users/{user.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user.id
        assert data["name"] == user.name
        assert data["phone"] == user.phone

    def test_get_user_by_id_other_user(self, client, test_db):
        """Test getting user by ID for another user fails"""
        user, session_token = self.create_authenticated_session(client, test_db)

        # Create another user
        other_user_data = UserCreate(name="Other User", phone="9876543210", is_active=True)
        other_user = UserService.register_user(test_db, other_user_data)

        response = client.get(f"/api/v1/users/{other_user.id}")

        assert response.status_code == 403  # Should be forbidden due to ownership check
        data = response.json()
        assert "You can only access your own resources" in data["detail"]


class TestAPIErrorHandling:
    """Test API error handling and edge cases"""

    def test_invalid_json_payload(self, client):
        """Test handling of invalid JSON payloads"""
        headers = {"Content-Type": "application/json"}
        malformed_json = '{"invalid": json}'

        response = client.post("/api/v1/auth/passkey/register/challenge", 
                             content=malformed_json, headers=headers)

        # Should return error status, not crash
        assert response.status_code >= 400

    def test_missing_required_fields(self, client):
        """Test handling of missing required fields"""
        incomplete_data = {
            "user_phone": "1234567890"
            # Missing user_name
        }

        response = client.post("/api/v1/auth/passkey/register/challenge", json=incomplete_data)

        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "detail" in data

    def test_invalid_phone_number_format(self, client):
        """Test handling of invalid phone number format"""
        invalid_data = {
            "user_phone": "not_a_number",
            "user_name": "Test User"
        }

        response = client.post("/api/v1/auth/passkey/register/challenge", json=invalid_data)

        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "detail" in data

    def test_extremely_long_user_name(self, client):
        """Test handling of extremely long user names"""
        with patch('src.services.passkey_service.PasskeyService.create_signup_challenge') as mock_challenge:
            # Mock simple challenge to avoid the serialization issue
            mock_challenge.return_value = {"challenge": "simple_challenge"}
            
            long_name_data = {
                "user_phone": "1234567890",
                "user_name": "A" * 1000  # Reasonable length
            }
            
            response = client.post("/api/v1/auth/passkey/register/challenge", json=long_name_data)
            
            # Should either succeed or fail gracefully, but not crash
            assert response.status_code in [200, 400, 422]

    def test_concurrent_registration_attempts(self, client, test_db):
        """Test handling of concurrent registration attempts for same user"""
        import concurrent.futures

        request_data = {
            "user_phone": "1234567890",
            "user_name": "Test User"
        }

        def make_registration_request():
            with patch('src.services.passkey_service.PasskeyService.create_signup_challenge') as mock_challenge:
                mock_challenge.return_value = {"challenge": "simple_challenge"}
                return client.post("/api/v1/auth/passkey/register/challenge", json=request_data)

        # Make concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(make_registration_request) for _ in range(3)]
            responses = [future.result() for future in concurrent.futures.as_completed(futures)]

        # At least one should succeed, others might fail gracefully
        success_count = sum(1 for r in responses if r.status_code == 200)
        assert success_count >= 1

        # No response should crash (5xx errors)
        for response in responses:
            assert response.status_code < 500
