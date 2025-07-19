"""
Emergency Contact API tests
"""
import pytest
from unittest.mock import patch, MagicMock
from src.models.user import User
from src.schemas.user import UserCreate
from src.services.user_service import UserService
from src.core.config import settings

## TODO: Add more tests for the Emergency Contact API
## TODO: Add unit tests for the Emergency Contact service
class TestEmergencyContacts:
    """Test emergency contact CRUD operations"""

    def create_admin_session(self, client):
        """Helper to create an admin session"""
        client.cookies.set("session_token", settings.ADMIN_SESSION_TOKEN)

    def create_authenticated_session(self, client, test_db):
        """Helper to create a regular authenticated session"""
        user_data = UserCreate(name="Test User", phone="1234567890", is_active=True)
        user = UserService.register_user(test_db, user_data)
        
        session_data = UserService.issue_session(user.id)
        session_token = session_data["session_token"]
        
        # Set session cookie in the client
        client.cookies.set("session_token", session_token)
        
        return user, session_token
    
    def create_user(self, test_db):
        """Helper to create a user for testing"""
        user = User(name="Test User", phone="1234567890")
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        return user.id

    def test_emergency_contact_crud(self, client, test_db):
        """Test emergency contact CRUD operations"""
        # Set up authenticated session for document creation (RequireAuth)
        user, session_token = self.create_authenticated_session(client, test_db)
        user_id = user.id
    
        # Create contact
        contact_data = {
            "name": "Jane Doe",
            "relation": "Sister",
            "phone": "9876543210",
            "user_id": user_id
        }
        response = client.post("/api/v1/emergency-contacts/", json=contact_data)
        assert response.status_code == 200 or response.status_code == 201
        contact = response.json()
        assert contact["name"] == contact_data["name"]
        assert contact["user_id"] == user_id
        contact_id = contact["id"]

        # Get all contacts for user
        response = client.get(f"/api/v1/emergency-contacts/user/{user_id}")
        assert response.status_code == 200
        contacts = response.json()
        assert len(contacts) == 1
        assert contacts[0]["name"] == contact_data["name"]

        # Update contact
        update_data = {"name": "Jane Smith"}
        response = client.put(f"/api/v1/emergency-contacts/{contact_id}", json=update_data)
        assert response.status_code == 200
        updated = response.json()
        assert updated["name"] == "Jane Smith"

        # Delete contact
        response = client.delete(f"/api/v1/emergency-contacts/{contact_id}")
        assert response.status_code == 200
        
        # Confirm deletion
        response = client.get(f"/api/v1/emergency-contacts/user/{user_id}")
        assert response.status_code == 200
        assert response.json() == []

    @patch('src.services.sms_service.SMSService.send_emergency_message')
    def test_sos_trigger(self, mock_send_emergency, client, test_db):
        """Test SOS trigger endpoint"""
        # Set up authenticated session
        user, session_token = self.create_authenticated_session(client, test_db)
        user_id = user.id
        
        # Create emergency contacts
        contact1_data = {
            "name": "Emergency Contact 1",
            "relation": "Family",
            "phone": "+1234567890",
            "user_id": user_id
        }
        contact2_data = {
            "name": "Emergency Contact 2", 
            "relation": "Friend",
            "phone": "+0987654321",
            "user_id": user_id
        }
        
        # Create contacts
        client.post("/api/v1/emergency-contacts/", json=contact1_data)
        client.post("/api/v1/emergency-contacts/", json=contact2_data)
        
        # Mock the SMS service to return success
        mock_send_emergency.return_value = {
            'success': True,
            'message': 'Emergency alert sent via WhatsApp to +1234567890',
            'message_sid': 'test_sid'
        }
        
        # Trigger SOS
        response = client.post(f"/api/v1/users/{user_id}/sos/trigger")
        
        # Verify response
        assert response.status_code == 200
        sos_response = response.json()
        assert sos_response["success"] is True
        assert sos_response["contacts_notified"] == 2
        assert len(sos_response["failed_notifications"]) == 0
        assert "Emergency SOS triggered!" in sos_response["message"]
        
        # Verify SMS service was called twice (once for each contact)
        assert mock_send_emergency.call_count == 2

    def test_sos_trigger_no_contacts(self, client, test_db):
        """Test SOS trigger with no emergency contacts"""
        # Set up authenticated session
        user, session_token = self.create_authenticated_session(client, test_db)
        user_id = user.id
        
        # Trigger SOS without any emergency contacts
        response = client.post(f"/api/v1/users/{user_id}/sos/trigger")
        
        # Should return 400 error
        assert response.status_code == 400
        error_response = response.json()
        assert "No emergency contacts found" in error_response["detail"]
