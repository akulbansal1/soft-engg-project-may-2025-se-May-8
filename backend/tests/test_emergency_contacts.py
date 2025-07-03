import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# Helper to create a user directly (simulate registration)
def create_user():
    from src.db.database import SessionLocal
    from src.models.user import User
    db = SessionLocal()
    user = User(name="Test User", phone=1234567890)
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user.id

def test_emergency_contact_crud():
    user_id = create_user()
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

    # Get all contacts for user
    response = client.get(f"/api/v1/emergency-contacts/user/{user_id}")
    assert response.status_code == 200
    contacts = response.json()
    assert len(contacts) == 1
    assert contacts[0]["name"] == contact_data["name"]

    # Update contact
    update_data = {"name": "Jane Smith"}
    contact_id = contact["id"]
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
