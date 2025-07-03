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

def test_medicine_crud():
    user_id = create_user()
    # Create medicine
    medicine_data = {
        "name": "Paracetamol",
        "dosage": "500mg",
        "frequency": "Once a day after dinner",
        "start_date": "2025-06-25",
        "end_date": "2025-07-05",
        "notes": "Take with food",
        "user_id": user_id,
        "doctor_id": None
    }
    response = client.post("/api/v1/medicines/", json=medicine_data)
    assert response.status_code == 200 or response.status_code == 201
    medicine = response.json()
    assert medicine["name"] == medicine_data["name"]
    assert medicine["user_id"] == user_id

    # Get all medicines for user
    response = client.get(f"/api/v1/medicines/user/{user_id}")
    assert response.status_code == 200
    medicines = response.json()
    assert len(medicines) == 1
    assert medicines[0]["name"] == medicine_data["name"]

    # Update medicine
    update_data = {"name": "Ibuprofen"}
    medicine_id = medicine["id"]
    response = client.put(f"/api/v1/medicines/{medicine_id}", json=update_data)
    assert response.status_code == 200
    updated = response.json()
    assert updated["name"] == "Ibuprofen"

    # Delete medicine
    response = client.delete(f"/api/v1/medicines/{medicine_id}")
    assert response.status_code == 200
    # Confirm deletion
    response = client.get(f"/api/v1/medicines/user/{user_id}")
    assert response.status_code == 200
    assert response.json() == []
