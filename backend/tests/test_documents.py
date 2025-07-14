"""
Document API tests
"""
import pytest
from src.models.user import User
from src.schemas.user import UserCreate
from src.services.user_service import UserService
from src.core.config import settings


class TestDocuments:
    """Test document CRUD operations"""

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

    def test_document_crud(self, client, test_db):
        """Test document CRUD operations"""
        # Set up authenticated session for document creation (RequireAuth)
        user, session_token = self.create_authenticated_session(client, test_db)
        user_id = user.id
        
        # Create document
        document_data = {
            "name": "Prescription.pdf",
            "file_url": "https://example.com/file.pdf",
            "user_id": user_id
        }
        response = client.post("/api/v1/documents/", json=document_data)
        assert response.status_code == 200 or response.status_code == 201
        document = response.json()
        assert document["name"] == document_data["name"]
        assert document["user_id"] == user_id
        document_id = document["id"]

        # Get all documents for user
        response = client.get(f"/api/v1/documents/user/{user_id}")
        assert response.status_code == 200
        documents = response.json()
        assert len(documents) == 1
        assert documents[0]["name"] == document_data["name"]

        # Update document
        update_data = {"name": "UpdatedPrescription.pdf"}
        response = client.put(f"/api/v1/documents/{document_id}", json=update_data)
        assert response.status_code == 200
        updated = response.json()
        assert updated["name"] == "UpdatedPrescription.pdf"

        # Delete document
        response = client.delete(f"/api/v1/documents/{document_id}")
        assert response.status_code == 200
        
        # Confirm deletion
        response = client.get(f"/api/v1/documents/user/{user_id}")
        assert response.status_code == 200
        assert response.json() == []
