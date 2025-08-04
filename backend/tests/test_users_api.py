"""
User API endpoint tests

Tests for user management endpoints including user listing, profile access, and SOS functionality.
Focuses on authentication, authorization, and business logic testing.
All SMS service calls are mocked to prevent real messages being sent.

SAFETY: This file uses comprehensive mocking to ensure NO real SMS/WhatsApp 
emergency messages are sent to the phone numbers in tests. The core SMS service 
functionality is tested separately in test_sms_service.py.
"""
import pytest
from unittest.mock import patch, MagicMock
from src.schemas.user import UserCreate
from src.services.user_service import UserService


@pytest.fixture(autouse=True)
def mock_sms_services():
    """Auto-mock all SMS services to prevent real messages being sent during tests"""
    # Mock both the get_sms_service function and the singleton instance
    with patch('src.services.sms_service.get_sms_service') as mock_get_sms, \
         patch('src.api.users.get_sms_service') as mock_api_get_sms, \
         patch('src.services.sms_service._sms_service_instance') as mock_instance:
        
        # Create a mock SMS service
        mock_sms_service = MagicMock()
        mock_sms_service.send_emergency_message.return_value = {'success': True}
        mock_sms_service.is_phone_verified.return_value = True
        
        mock_get_sms.return_value = mock_sms_service
        mock_api_get_sms.return_value = mock_sms_service
        
        mock_instance = None
        
        yield mock_sms_service


class TestUserListingAPI:
    """Test user listing and profile access endpoints"""

    def create_authenticated_user(self, client, test_db, name="Test User", phone="1234567890"):
        """Helper to create an authenticated user session"""
        user_data = UserCreate(name=name, phone=phone, is_active=True)
        user = UserService.register_user(test_db, user_data)
        
        session_data = UserService.issue_session(user.id)
        session_token = session_data["session_token"]
        
        client.cookies.set("session_token", session_token)
        
        return user, session_token

    def test_get_users_authenticated(self, client, test_db):
        """Test getting user list with authentication"""
        user, session_token = self.create_authenticated_user(client, test_db)
        
        user2_data = UserCreate(name="User 2", phone="2222222222", is_active=True)
        user3_data = UserCreate(name="User 3", phone="3333333333", is_active=True)
        UserService.register_user(test_db, user2_data)
        UserService.register_user(test_db, user3_data)
        
        response = client.get("/api/v1/users/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 3  
        
        for user_data in data:
            assert "id" in user_data
            assert "name" in user_data
            assert "phone" in user_data
            assert "is_active" in user_data

    def test_get_users_pagination(self, client, test_db):
        """Test user listing with pagination parameters"""
        user, session_token = self.create_authenticated_user(client, test_db)
        
        response = client.get("/api/v1/users/?skip=0&limit=2")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 2

    def test_get_users_unauthenticated(self, client, test_db):
        """Test getting user list without authentication"""
        response = client.get("/api/v1/users/")
        
        assert response.status_code == 401
        data = response.json()
        assert "No session token provided" in data["detail"]

    def test_get_user_by_id_own_user(self, client, test_db):
        """Test getting own user profile"""
        user, session_token = self.create_authenticated_user(client, test_db)
        
        response = client.get(f"/api/v1/users/{user.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user.id
        assert data["name"] == user.name
        assert data["phone"] == user.phone
        assert data["is_active"] == user.is_active

    def test_get_user_by_id_other_user_forbidden(self, client, test_db):
        """Test getting another user's profile (should be forbidden)"""
        user1, session_token = self.create_authenticated_user(client, test_db, "User 1", "1111111111")
        
        user2_data = UserCreate(name="User 2", phone="2222222222", is_active=True)
        user2 = UserService.register_user(test_db, user2_data)
        
        response = client.get(f"/api/v1/users/{user2.id}")
        
        assert response.status_code == 403
        data = response.json()
        assert "You can only access your own resources" in data["detail"]

    def test_get_user_by_id_unauthenticated(self, client, test_db):
        """Test getting user profile without authentication"""
        user_data = UserCreate(name="Test User", phone="1234567890", is_active=True)
        user = UserService.register_user(test_db, user_data)
        
        response = client.get(f"/api/v1/users/{user.id}")
        
        assert response.status_code == 401
        data = response.json()
        assert "No session token provided" in data["detail"]


class TestSOSAPI:
    """Test SOS emergency alert functionality"""

    def create_authenticated_user(self, client, test_db, name="Test User", phone="1234567890"):
        """Helper to create an authenticated user session"""
        user_data = UserCreate(name=name, phone=phone, is_active=True)
        user = UserService.register_user(test_db, user_data)
        
        session_data = UserService.issue_session(user.id)
        session_token = session_data["session_token"]
        
        client.cookies.set("session_token", session_token)
        
        return user, session_token

    def test_trigger_sos_success(self, client, test_db, mock_sms_services):
        """Test successful SOS trigger with emergency contacts"""
        user, session_token = self.create_authenticated_user(client, test_db)
        
        mock_contacts = [
            MagicMock(phone="+1234567890", name="Contact 1"),
            MagicMock(phone="+0987654321", name="Contact 2")
        ]
        
        request_data = {
            "location": "123 Emergency St, City, State"
        }
        
        with patch('src.services.emergency_contact_service.EmergencyContactService.get_contacts_by_user') as mock_get_contacts:
            mock_get_contacts.return_value = mock_contacts
            
            mock_sms_services.send_emergency_message.return_value = {'success': True}
            
            response = client.post(f"/api/v1/users/{user.id}/sos/trigger", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["contacts_notified"] == 2
            assert "Emergency SOS triggered" in data["message"]
            assert data["failed_notifications"] == []
            
            assert mock_sms_services.send_emergency_message.call_count == 2

    def test_trigger_sos_no_contacts(self, client, test_db, mock_sms_services):
        """Test SOS trigger when user has no emergency contacts"""
        user, session_token = self.create_authenticated_user(client, test_db)
        
        request_data = {
            "location": "123 Emergency St, City, State"
        }
        
        with patch('src.services.emergency_contact_service.EmergencyContactService.get_contacts_by_user') as mock_get_contacts:
            mock_get_contacts.return_value = []  
            
            response = client.post(f"/api/v1/users/{user.id}/sos/trigger", json=request_data)
            
            assert response.status_code == 400
            data = response.json()
            assert "No emergency contacts found" in data["detail"]
            
            mock_sms_services.send_emergency_message.assert_not_called()

    def test_trigger_sos_partial_failure(self, client, test_db, mock_sms_services):
        """Test SOS trigger with some failed notifications"""
        user, session_token = self.create_authenticated_user(client, test_db)
        
        mock_contacts = [
            MagicMock(phone="+1234567890", name="Contact 1"),
            MagicMock(phone="+0987654321", name="Contact 2"),
            MagicMock(phone="+1111111111", name="Contact 3")
        ]
        
        request_data = {
            "location": "123 Emergency St, City, State"
        }
        
        def mock_send_emergency_message(phone, user_name, location=None):
            if phone == "+1111111111":
                raise Exception("SMS service error")
            return {'success': True}
        
        with patch('src.services.emergency_contact_service.EmergencyContactService.get_contacts_by_user') as mock_get_contacts:
            mock_get_contacts.return_value = mock_contacts
            
            mock_sms_services.send_emergency_message.side_effect = mock_send_emergency_message
            
            response = client.post(f"/api/v1/users/{user.id}/sos/trigger", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True  
            assert data["contacts_notified"] == 2
            assert len(data["failed_notifications"]) == 1
            assert "+1111111111" in data["failed_notifications"]
            assert "failed" in data["message"]
            
            assert mock_sms_services.send_emergency_message.call_count == 3

    def test_trigger_sos_all_failed(self, client, test_db, mock_sms_services):
        """Test SOS trigger when all notifications fail"""
        user, session_token = self.create_authenticated_user(client, test_db)
        
        mock_contacts = [
            MagicMock(phone="+1234567890", name="Contact 1"),
            MagicMock(phone="+0987654321", name="Contact 2")
        ]
        
        request_data = {
            "location": "123 Emergency St, City, State"
        }
        
        def mock_send_emergency_message(phone, user_name, location=None):
            raise Exception("SMS service error")
        
        with patch('src.services.emergency_contact_service.EmergencyContactService.get_contacts_by_user') as mock_get_contacts:
            mock_get_contacts.return_value = mock_contacts
            
            mock_sms_services.send_emergency_message.side_effect = mock_send_emergency_message
            
            response = client.post(f"/api/v1/users/{user.id}/sos/trigger", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is False
            assert data["contacts_notified"] == 0
            assert len(data["failed_notifications"]) == 2
            assert "Failed to send SOS messages" in data["message"]
            
            assert mock_sms_services.send_emergency_message.call_count == 2

    def test_trigger_sos_wrong_user(self, client, test_db, mock_sms_services):
        """Test SOS trigger for another user (should be forbidden)"""
        user1, session_token = self.create_authenticated_user(client, test_db, "User 1", "1111111111")
        
        user2_data = UserCreate(name="User 2", phone="2222222222", is_active=True)
        user2 = UserService.register_user(test_db, user2_data)
        
        request_data = {
            "location": "123 Emergency St, City, State"
        }
        
        response = client.post(f"/api/v1/users/{user2.id}/sos/trigger", json=request_data)
        
        assert response.status_code == 403
        data = response.json()
        assert "You can only access your own resources" in data["detail"]

    def test_trigger_sos_unauthenticated(self, client, test_db, mock_sms_services):
        """Test SOS trigger without authentication"""
        user_data = UserCreate(name="Test User", phone="1234567890", is_active=True)
        user = UserService.register_user(test_db, user_data)
        
        request_data = {
            "location": "123 Emergency St, City, State"
        }
        
        response = client.post(f"/api/v1/users/{user.id}/sos/trigger", json=request_data)
        
        assert response.status_code == 401
        data = response.json()
        assert "No session token provided" in data["detail"]

    def test_trigger_sos_missing_location(self, client, test_db, mock_sms_services):
        """Test SOS trigger without location (should still work)"""
        user, session_token = self.create_authenticated_user(client, test_db)
        
        mock_contacts = [
            MagicMock(phone="+1234567890", name="Contact 1")
        ]
        
        request_data = {}  
        
        with patch('src.services.emergency_contact_service.EmergencyContactService.get_contacts_by_user') as mock_get_contacts:
          
            mock_get_contacts.return_value = mock_contacts

            mock_sms_services.send_emergency_message.return_value = {'success': True}
            
            response = client.post(f"/api/v1/users/{user.id}/sos/trigger", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["contacts_notified"] == 1
            
            mock_sms_services.send_emergency_message.assert_called_once()
            call_args = mock_sms_services.send_emergency_message.call_args
            assert call_args[1]["location"] is None


class TestUserAPIValidation:
    """Test user API request validation and edge cases"""

    def test_invalid_user_id_format(self, client, test_db):
        """Test user endpoints with invalid user ID format"""
        user_data = UserCreate(name="Test User", phone="1234567890", is_active=True)
        user = UserService.register_user(test_db, user_data)
        
        session_data = UserService.issue_session(user.id)
        session_token = session_data["session_token"]
        client.cookies.set("session_token", session_token)
        
        response = client.get("/api/v1/users/invalid_id")
        assert response.status_code == 422  

    def test_negative_user_id(self, client, test_db):
        """Test user endpoints with negative user ID"""
        user_data = UserCreate(name="Test User", phone="1234567890", is_active=True)
        user = UserService.register_user(test_db, user_data)
        
        session_data = UserService.issue_session(user.id)
        session_token = session_data["session_token"]
        client.cookies.set("session_token", session_token)
        
        response = client.get("/api/v1/users/-1")
        assert response.status_code == 403  
