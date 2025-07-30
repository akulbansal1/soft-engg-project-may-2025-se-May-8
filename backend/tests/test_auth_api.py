"""
API endpoint tests for authentication-related endpoints with realistic mock WebAuthn data.
This file contains comprehensive tests for passkey registration, login, and session management.
"""
import pytest
import json
import base64
import concurrent.futures
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from src.schemas.user import UserCreate
from src.schemas.passkey import PasskeyCredentialCreate, PasskeyVerificationResult
from src.services.user_service import UserService
from src.services.passkey_service import PasskeyService


class TestPasskeyRegistrationAPI:
    """Test passkey registration API endpoints"""

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
            # Mock properly structured SerializedWebAuthnChallenge
            from src.schemas.passkey import SerializedWebAuthnChallenge, WebAuthnUser, WebAuthnRelyingParty
            mock_challenge_data = SerializedWebAuthnChallenge(
                challenge=base64.b64encode(b"test_challenge").decode(),
                user=WebAuthnUser(id="test_user_id", name="Test User", display_name="Test User"),
                rp=WebAuthnRelyingParty(id="localhost", name="Test RP"),
                timeout=60000,
                attestation="direct"
            )
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
            # Mock properly structured SerializedWebAuthnChallenge
            from src.schemas.passkey import SerializedWebAuthnChallenge, WebAuthnUser, WebAuthnRelyingParty, PublicKeyCredentialParameters
            mock_challenge_data = SerializedWebAuthnChallenge(
                challenge=base64.b64encode(b"test_challenge").decode(),
                user=WebAuthnUser(id="test_user_id", name="Alice Cooper", display_name="Alice Cooper"),
                rp=WebAuthnRelyingParty(id="localhost", name="Test RP"),
                pubKeyCredParams=[PublicKeyCredentialParameters(type="public-key", alg=-7)],
                timeout=60000,
                attestation="direct"
            )
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
            # Mock properly structured SerializedWebAuthnChallenge
            from src.schemas.passkey import SerializedWebAuthnChallenge, WebAuthnUser, WebAuthnRelyingParty, PublicKeyCredentialParameters
            mock_challenge_data = SerializedWebAuthnChallenge(
                challenge=base64.b64encode(b"test_challenge").decode(),
                user=WebAuthnUser(id="test_user_id", name="Bob Builder", display_name="Bob Builder"),
                rp=WebAuthnRelyingParty(id="localhost", name="Test RP"),
                pubKeyCredParams=[PublicKeyCredentialParameters(type="public-key", alg=-7)],
                timeout=60000,
                attestation="direct"
            )
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

    def test_create_login_challenge_credential_not_found(self, client, test_db):
        """Test creating login challenge fails for non-existent credential"""
        request_data = {
            "credential_id": "non_existent_credential"
        }

        response = client.post("/api/v1/auth/passkey/login/challenge", json=request_data)

        assert response.status_code == 404
        data = response.json()
        assert "Not found" in data["detail"]

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
            # Mock properly structured SerializedWebAuthnChallenge
            from src.schemas.passkey import SerializedWebAuthnChallenge, WebAuthnUser, WebAuthnRelyingParty
            mock_challenge_data = SerializedWebAuthnChallenge(
                challenge="simple_challenge",
                user=WebAuthnUser(id="test_user_id", name="Very long name", display_name="Very long name"),
                rp=WebAuthnRelyingParty(id="localhost", name="Test RP"),
                timeout=60000,
                attestation="direct"
            )
            mock_challenge.return_value = mock_challenge_data
            
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
                # Mock properly structured SerializedWebAuthnChallenge
                from src.schemas.passkey import SerializedWebAuthnChallenge, WebAuthnUser, WebAuthnRelyingParty
                mock_challenge_data = SerializedWebAuthnChallenge(
                    challenge="simple_challenge",
                    user=WebAuthnUser(id="test_user_id", name="Test User", display_name="Test User"),
                    rp=WebAuthnRelyingParty(id="localhost", name="Test RP"),
                    timeout=60000,
                    attestation="direct"
                )
                mock_challenge.return_value = mock_challenge_data
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


class TestPasskey:
    """Integration test for complete passkey flow using real WebAuthn data from webauthn.io"""
    
    def test_passkey_registration_challenge(self, client, test_db):
        """Test creation of passkey registration challenge"""
        from unittest.mock import patch
        from src.core.config import settings
        
        # Disable SMS verification for this test
        with patch.object(settings, 'SMS_VERIFICATION_ENABLED', False):
            registration_request = {
                "user_phone": "1234567890",
                "user_name": "Test User"
            }
            
            response = client.post(
                "/api/v1/auth/passkey/register/challenge", 
                json=registration_request
            )
            
            assert response.status_code == 200
            challenge_data = response.json()
            
            # Verify challenge structure matches expected WebAuthn format
            assert "challenge" in challenge_data
            assert "user" in challenge_data
            assert "rp" in challenge_data
            assert "timeout" in challenge_data
            assert "attestation" in challenge_data
            
            # Verify user data
            assert challenge_data["user"]["name"] == "1234567890"
            assert challenge_data["user"]["display_name"] == "Test User"
            
            # Verify RP data
            assert challenge_data["rp"]["id"] == settings.FRONTEND_RP_ID
            assert challenge_data["rp"]["name"] == settings.PROJECT_NAME

    def test_passkey_login_challenge(self, client, test_db):
        """Test creation of passkey login challenge"""
        from unittest.mock import patch
        from src.services.passkey_service import PasskeyService
        from src.schemas.passkey import PasskeyCredentialCreate
        from src.services.user_service import UserService
        from src.schemas.user import UserCreate
        
        # Create a test user and credential first
        user_data = UserCreate(name="Test User", phone="1234567890", is_active=True)
        user = UserService.register_user(test_db, user_data)
        
        credential_data = PasskeyCredentialCreate(
            user_id=user.id,
            credential_id="VzS8YaNMjy5pAxbP5ZkHwgNh_BU",
            public_key="pQECAyYgASFYIEDsSmzjh/bJJQtlYhdUXXrsT6Dj+KAFqRI4AYZWb/WvIlggu77P4mo/mU9rs5huAi3Yf7vjfl68EqR518ZnTpxaUg4",
            sign_count=0
        )
        PasskeyService.create_credential(test_db, credential_data)
        
        login_request = {
            "credential_id": "VzS8YaNMjy5pAxbP5ZkHwgNh_BU"
        }
        
        response = client.post(
            "/api/v1/auth/passkey/login/challenge",
            json=login_request
        )
        
        challenge_data = response.json()
        print(challenge_data)
        
        assert response.status_code == 200
        # Verify challenge structure
        assert "challenge" in challenge_data
        assert "timeout" in challenge_data

    def test_passkey_registration_verification_with_real_webauthn_data(self, client, test_db):
        """
        Test passkey registration verification using real WebAuthn data from webauthn.io
        This is the main integration test that checks if our API can handle real WebAuthn responses
        """
        from unittest.mock import patch
        from src.core.config import settings
        from src.utils.cache import Cache
        from src.services.user_service import UserService
        from src.schemas.user import UserCreate
        import json
        import base64
        
        # Disable SMS verification 
        with patch.object(settings, 'SMS_VERIFICATION_ENABLED', False):
            
            # Step 1: Mock the entire registration challenge creation to return consistent data
            user_phone = "1234567890"
            user_name = user_phone 

            # Step 1: Set up - create user and credential as if registration was successful
            user_data = UserCreate(name="Test User", phone="1234567890", is_active=True)
            user = UserService.register_user(test_db, user_data)

            webauthn_io_user_id = "d2ViYXV0aG5pby0xMjM0NTY3ODkw" 
            
            # Return the exact challenge structure from webauthn.io
            from src.schemas.passkey import SerializedWebAuthnChallenge, WebAuthnUser, WebAuthnRelyingParty
            mock_challenge_data = SerializedWebAuthnChallenge(
                challenge="sd4ELR7g9xod_8NfMZjAXXoC4vxn8ChLvKV0UWbm-ou5da1pcI0rSrMQXzapY6pq8Lel6kR5UkA5NKd2iWMGlQ",
                user=WebAuthnUser(
                    id=webauthn_io_user_id,
                    name=user_phone,
                    display_name=user_phone 
                ),
                rp=WebAuthnRelyingParty(
                    id="webauthn.io",
                    name="webauthn.io"
                ),
                timeout=60000,
                attestation="none"
            )

            # Step 2: Set up the cache manually with the exact challenge data that matches webauthn.io
            real_challenge_data = {
                "challenge": "sd4ELR7g9xod_8NfMZjAXXoC4vxn8ChLvKV0UWbm-ou5da1pcI0rSrMQXzapY6pq8Lel6kR5UkA5NKd2iWMGlQ",
                "user": {
                    "id": webauthn_io_user_id,
                    "name": user_phone,
                    "display_name": user_phone
                },
                "rp": {
                    "name": "webauthn.io",
                    "id": "webauthn.io"
                },
                "timeout": 60000,
                "attestation": "none"
            }
            
            # Step 2: Set up the cache manually with the exact challenge data that matches webauthn.io
            real_challenge_data = {
                "challenge": "sd4ELR7g9xod_8NfMZjAXXoC4vxn8ChLvKV0UWbm-ou5da1pcI0rSrMQXzapY6pq8Lel6kR5UkA5NKd2iWMGlQ",
                "user": {
                    "id": webauthn_io_user_id,
                    "name": user_phone,
                    "display_name": user_phone
                },
                "rp": {
                    "name": "webauthn.io",
                    "id": "webauthn.io"
                },
                "timeout": 60000,
                "attestation": "none"
            }
            
            # Set the challenge in cache with our test user ID
            Cache.set(
                f"webauthn_signup_challenge_{user.id}", 
                json.dumps(real_challenge_data), 
                expiry=settings.CHALLENGE_CACHE_EXPIRY
            )
            
            # Step 3: Create the registration verification request using real webauthn.io data
            verification_request = {
                "user_phone": user_phone,
                "user_name": user_name
            }
            
            # Real WebAuthn registration response from webauthn.io
            signup_response = {
                "credential_id": "VzS8YaNMjy5pAxbP5ZkHwgNh_BU",
                "public_key": "MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEQOxKbOOH9sklC2ViF1RdeuxPoOP4oAWpEjgBhlZv9a+7vs/iaj+ZT2uzmG4CLdh/u+N+XrwSpHnXxmdOnFpSDg",
                "attestation_object": "o2NmbXRkbm9uZWdhdHRTdG10oGhhdXRoRGF0YViYdKbqkhPJnC90siSSsyDPQCYqlMGpUKA5fyklC2CEHvBdAAAAAPv8MAcVTk7MjAtuAgVX170AFFc0vGGjTI8uaQMWz-WZB8IDYfwVpQECAyYgASFYIEDsSmzjh_bJJQtlYhdUXXrsT6Dj-KAFqRI4AYZWb_WvIlggu77P4mo_mU9rs5huAi3Yf7vjfl68EqR518ZnTpxaUg4",
                "client_data_json": "eyJ0eXBlIjoid2ViYXV0aG4uY3JlYXRlIiwiY2hhbGxlbmdlIjoic2Q0RUxSN2c5eG9kXzhOZk1aakFYWG9DNHZ4bjhDaEx2S1YwVVdibS1vdTVkYTFwY0kwclNyTVFYemFwWTZwcThMZWw2a1I1VWtBNU5LZDJpV01HbFEiLCJvcmlnaW4iOiJodHRwczovL3dlYmF1dGhuLmlvIiwiY3Jvc3NPcmlnaW4iOmZhbHNlLCJvdGhlcl9rZXlzX2Nhbl9iZV9hZGRlZF9oZXJlIjoiZG8gbm90IGNvbXBhcmUgY2xpZW50RGF0YUpTT04gYWdhaW5zdCBhIHRlbXBsYXRlLiBTZWUgaHR0cHM6Ly9nb28uZ2wveWFiUGV4In0"
            }
            
            # Step 4: Now test the real verification with proper setup
            with patch.object(settings, 'FRONTEND_ORIGIN', 'https://webauthn.io'), \
                    patch.object(settings, 'FRONTEND_RP_ID', 'webauthn.io'):

                request_payload = {
                    "request": verification_request,   # PasskeyRegistrationRequest
                    "response_data": signup_response   # SignupResponse
                }
                
                response = client.post(
                    "/api/v1/auth/passkey/register/verify",
                    json=request_payload  # Send as JSON with nested structure
                )
                
                print(f"Registration verification status: {response.status_code}")
                if response.status_code != 200:
                    print(f"Error response: {response.json()}")
                
                assert response.status_code == 200
                result = response.json()
                assert result["credential_id"] == "VzS8YaNMjy5pAxbP5ZkHwgNh_BU"
                assert result["user_id"] == user.id
                
                # Verify session cookie was set
                cookies = response.headers.get('set-cookie', '')
                assert 'session_token' in cookies
            
    def test_passkey_login_verification_with_real_webauthn_data(self, client, test_db):
        """
        Test passkey login verification using real WebAuthn data from webauthn.io
        This test assumes registration was successful and tests the login flow
        """
        from unittest.mock import patch
        from src.core.config import settings
        from src.utils.cache import Cache
        from src.services.passkey_service import PasskeyService
        from src.schemas.passkey import PasskeyCredentialCreate
        from src.services.user_service import UserService
        from src.schemas.user import UserCreate
        import json
        
        # Step 1: Set up - create user and credential as if registration was successful
        user_data = UserCreate(name="Test User", phone="1234567890", is_active=True)
        user = UserService.register_user(test_db, user_data)
        
        # Create credential with the same ID from webauthn.io data
        credential_data = PasskeyCredentialCreate(
            user_id=user.id,
            credential_id="VzS8YaNMjy5pAxbP5ZkHwgNh_BU",
            public_key="pQECAyYgASFYIEDsSmzjh/bJJQtlYhdUXXrsT6Dj+KAFqRI4AYZWb/WvIlggu77P4mo/mU9rs5huAi3Yf7vjfl68EqR518ZnTpxaUg4",
            sign_count=0
        )
        PasskeyService.create_credential(test_db, credential_data)
        
        # Step 2: Set up login challenge cache with real challenge from webauthn.io
        real_login_challenge = {
            "challenge": "s6n4h43vaPdzE997a6IRiHNqlTKoKFyPQmbu9_I_cUFRRhICzGnqdP0W-ElTZsZ3ncDrkoNcILi_-ObQjSU2LQ",
            "timeout": 60000,
            "rpId": "webauthn.io"
        }

        Cache.set(
            f"webauthn_login_challenge_{user.id}",
            json.dumps(real_login_challenge),
            expiry=settings.CHALLENGE_CACHE_EXPIRY
        )
        
        # Step 3: Create login verification request
        login_request = {
            "credential_id": "VzS8YaNMjy5pAxbP5ZkHwgNh_BU"
        }
        
        # Real WebAuthn login response from webauthn.io
        login_response_data = {
            "credential_id": "VzS8YaNMjy5pAxbP5ZkHwgNh_BU",
            "signature": "MEQCIFEx1k41KogfFnHmos4fq3XS8nHH5PWgVUyPtOtLJ7XhAiB53LZ0AUc0xTgLIpDAmKhSkfYr928pzyBtuhlzwVpDTg",
            "client_data_json": "eyJ0eXBlIjoid2ViYXV0aG4uZ2V0IiwiY2hhbGxlbmdlIjoiczZuNGg0M3ZhUGR6RTk5N2E2SVJpSE5xbFRLb0tGeVBRbWJ1OV9JX2NVRlJSaElDekducWRQMFctRWxUWnNaM25jRHJrb05jSUxpXy1PYlFqU1UyTFEiLCJvcmlnaW4iOiJodHRwczovL3dlYmF1dGhuLmlvIiwiY3Jvc3NPcmlnaW4iOmZhbHNlfQ",
            "authenticator_data": "dKbqkhPJnC90siSSsyDPQCYqlMGpUKA5fyklC2CEHvAdAAAAAA==",
            "sign_count": 1
        }
        
        # Step 4: Test the real login verification
        with patch.object(settings, 'FRONTEND_ORIGIN', 'https://webauthn.io'), \
             patch.object(settings, 'FRONTEND_RP_ID', 'webauthn.io'):
            

            request_payload = {
                "request": login_request,           # PasskeyLoginRequest
                "response_data": login_response_data # LoginResponse (or similar)
            }
            
            response = client.post(
                "/api/v1/auth/passkey/login/verify",
                json=request_payload  # Send as JSON with nested structure
            )
            
            print(f"Login verification status: {response.status_code}")
            if response.status_code != 200:
                print(f"Error response: {response.json()}")


            assert response.status_code == 200
            result = response.json()
            assert "user_id" in result
            assert "credential_id" in result
            assert result["user_id"] == user.id
            
            # Verify session cookie was set
            cookies = response.headers.get('set-cookie', '')
            assert 'session_token' in cookies
