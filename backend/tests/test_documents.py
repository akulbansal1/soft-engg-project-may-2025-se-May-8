import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

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

def test_document_crud():
    user_id = create_user()
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

    # Get all documents for user
    response = client.get(f"/api/v1/documents/user/{user_id}")
    assert response.status_code == 200
    documents = response.json()
    assert len(documents) == 1
    assert documents[0]["name"] == document_data["name"]

    # Update document
    update_data = {"name": "UpdatedPrescription.pdf"}
    document_id = document["id"]
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
