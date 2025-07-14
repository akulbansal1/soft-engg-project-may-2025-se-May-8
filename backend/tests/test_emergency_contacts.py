"""
Emergency Contact API tests
"""
import pytest
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
