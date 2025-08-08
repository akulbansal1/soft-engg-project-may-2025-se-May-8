import pytest
from unittest.mock import patch, MagicMock
from src.models.user import User
from src.schemas.user import UserCreate
from src.services.user_service import UserService
from src.core.config import settings

class TestEmergencyContacts:

    def create_admin_session(self, client):
        client.cookies.set("session_token", settings.ADMIN_SESSION_TOKEN)

    def create_authenticated_session(self, client, test_db):
        user_data = UserCreate(name="Test User", phone="1234567890", is_active=True)
        user = UserService.register_user(test_db, user_data)
        
        session_data = UserService.issue_session(user.id)
        session_token = session_data["session_token"]
        
        client.cookies.set("session_token", session_token)
        
        return user, session_token
    
    def create_user(self, test_db):
        user = User(name="Test User", phone="1234567890")
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        return user.id

    def test_create_emergency_contact_valid_data(self, client, test_db):
        user, session_token = self.create_authenticated_session(client, test_db)
        user_id = user.id
    
        contact_data = {
            "name": "Jane Doe",
            "relation": "Sister",
            "phone": "+919876543210",
            "user_id": user_id
        }
        
        response = client.post("/api/v1/emergency-contacts/", json=contact_data)
        assert response.status_code in [200, 201]
        contact = response.json()
        assert contact["name"] == contact_data["name"]
        assert contact["relation"] == contact_data["relation"]
        assert contact["phone"] == contact_data["phone"]
        assert contact["user_id"] == user_id
        assert "id" in contact

    def test_create_emergency_contact_missing_required_fields(self, client, test_db):
        user, session_token = self.create_authenticated_session(client, test_db)
        
        incomplete_data = {
            "name": "Jane Doe",
            "relation": "Sister",
            "user_id": user.id
        }
        
        response = client.post("/api/v1/emergency-contacts/", json=incomplete_data)
        assert response.status_code == 422

    def test_create_emergency_contact_unauthorized(self, client, test_db):
        user_id = self.create_user(test_db)
        
        contact_data = {
            "name": "Jane Doe",
            "relation": "Sister", 
            "phone": "+919876543210",
            "user_id": user_id
        }
        
        response = client.post("/api/v1/emergency-contacts/", json=contact_data)
        assert response.status_code == 401

    def test_create_emergency_contact_max_limit_exceeded(self, client, test_db):
        user, session_token = self.create_authenticated_session(client, test_db)
        user_id = user.id
        
        for i in range(5):
            contact_data = {
                "name": f"Contact {i+1}",
                "relation": "Family",
                "phone": f"+91987654321{i}",
                "user_id": user_id
            }
            response = client.post("/api/v1/emergency-contacts/", json=contact_data)
            assert response.status_code in [200, 201]
        
        contact_data = {
            "name": "Contact 6",
            "relation": "Friend",
            "phone": "+919876543215",
            "user_id": user_id
        }
        response = client.post("/api/v1/emergency-contacts/", json=contact_data)
        assert response.status_code == 400
        assert "Maximum of 5 emergency contacts allowed" in response.json()["detail"]

    def test_get_emergency_contacts_by_user(self, client, test_db):
        user, session_token = self.create_authenticated_session(client, test_db)
        user_id = user.id
        
        contact_data = {
            "name": "Jane Doe",
            "relation": "Sister",
            "phone": "+919876543210",
            "user_id": user_id
        }
        client.post("/api/v1/emergency-contacts/", json=contact_data)
        
        response = client.get(f"/api/v1/emergency-contacts/user/{user_id}")
        assert response.status_code == 200
        contacts = response.json()
        assert isinstance(contacts, list)
        assert len(contacts) == 1
        assert contacts[0]["name"] == "Jane Doe"

    def test_update_emergency_contact_valid_data(self, client, test_db):
        user, session_token = self.create_authenticated_session(client, test_db)
        user_id = user.id
        
        contact_data = {
            "name": "Jane Doe",
            "relation": "Sister",
            "phone": "+919876543210",
            "user_id": user_id
        }
        
        create_response = client.post("/api/v1/emergency-contacts/", json=contact_data)
        contact_id = create_response.json()["id"]
        
        update_data = {"name": "Jane Smith", "relation": "Cousin"}
        response = client.put(f"/api/v1/emergency-contacts/{contact_id}", json=update_data)
        assert response.status_code == 200
        updated = response.json()
        assert updated["name"] == "Jane Smith"
        assert updated["relation"] == "Cousin"
        assert updated["phone"] == "+919876543210"

    def test_delete_emergency_contact_and_verify_gone(self, client, test_db):
        user, session_token = self.create_authenticated_session(client, test_db)
        user_id = user.id
        
        contact_data = {
            "name": "Jane Doe",
            "relation": "Sister",
            "phone": "+919876543210",
            "user_id": user_id
        }
        
        create_response = client.post("/api/v1/emergency-contacts/", json=contact_data)
        contact_id = create_response.json()["id"]
        
        delete_response = client.delete(f"/api/v1/emergency-contacts/{contact_id}")
        assert delete_response.status_code == 200
        assert "message" in delete_response.json()
        
        verify_response = client.get(f"/api/v1/emergency-contacts/user/{user_id}")
        assert verify_response.status_code == 200
        assert len(verify_response.json()) == 0

    @patch('src.services.sms_service.SMSService.send_emergency_message')
    def test_sos_trigger_successful(self, mock_send_emergency, client, test_db):
        user, session_token = self.create_authenticated_session(client, test_db)
        user_id = user.id
        
        contact1_data = {
            "name": "Emergency Contact 1",
            "relation": "Family",
            "phone": "+919876543210",
            "user_id": user_id
        }
        contact2_data = {
            "name": "Emergency Contact 2", 
            "relation": "Friend",
            "phone": "+918765432109",
            "user_id": user_id
        }
        
        client.post("/api/v1/emergency-contacts/", json=contact1_data)
        client.post("/api/v1/emergency-contacts/", json=contact2_data)
        
        mock_send_emergency.return_value = {
            'success': True,
            'message': 'Emergency alert sent via WhatsApp',
            'message_sid': 'test_sid'
        }
        
        sos_data = {"location": "Home", "message": "Help needed!"}
        response = client.post(f"/api/v1/users/{user_id}/sos/trigger", json=sos_data)
        
        assert response.status_code == 200
        sos_response = response.json()
        assert sos_response["success"] is True
        assert sos_response["contacts_notified"] == 2
        assert len(sos_response["failed_notifications"]) == 0
        assert "Emergency SOS triggered!" in sos_response["message"]
        
        assert mock_send_emergency.call_count == 2

    def test_sos_trigger_no_emergency_contacts(self, client, test_db):
        user, session_token = self.create_authenticated_session(client, test_db)
        user_id = user.id
        
        sos_data = {"location": "Home", "message": "Help needed!"}
        response = client.post(f"/api/v1/users/{user_id}/sos/trigger", json=sos_data)
        
        assert response.status_code == 400
        error_response = response.json()
        assert "No emergency contacts found" in error_response["detail"]

    @patch('src.services.sms_service.SMSService.send_emergency_message')
    def test_sos_trigger_sms_service_fails(self, mock_send_emergency, client, test_db):
        user, session_token = self.create_authenticated_session(client, test_db)
        user_id = user.id
        
        contact_data = {
            "name": "Emergency Contact",
            "relation": "Family",
            "phone": "+919876543210",
            "user_id": user_id
        }
        client.post("/api/v1/emergency-contacts/", json=contact_data)
        
        mock_send_emergency.side_effect = Exception("SMS service unavailable")
        
        sos_data = {"location": "Home", "message": "Help needed!"}
        response = client.post(f"/api/v1/users/{user_id}/sos/trigger", json=sos_data)
        
        assert response.status_code == 200
        sos_response = response.json()
        assert sos_response["success"] is False
        assert sos_response["contacts_notified"] == 0
        assert len(sos_response["failed_notifications"]) == 1
        assert "Failed to send SOS messages" in sos_response["message"]
