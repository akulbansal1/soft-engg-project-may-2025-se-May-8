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

def create_doctor():
    from src.db.database import SessionLocal
    from src.models.doctor import Doctor
    db = SessionLocal()
    doctor = Doctor(name="Dr. A. Kumar", location="Delhi")
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    db.close()
    return doctor.doctor_id

def test_appointment_crud():
    user_id = create_user()
    doctor_id = create_doctor()
    # Create appointment
    appointment_data = {
        "name": "Consultation",
        "date": "2025-07-03",
        "time": "14:30:00",
        "notes": "Eat healthy",
        "user_id": user_id,
        "doctor_id": doctor_id
    }
    response = client.post("/api/v1/appointments/", json=appointment_data)
    assert response.status_code == 200 or response.status_code == 201
    appointment = response.json()
    assert appointment["name"] == appointment_data["name"]
    assert appointment["user_id"] == user_id
    assert appointment["doctor_id"] == doctor_id
    appointment_id = appointment["id"]

    # Get all appointments for user
    response = client.get(f"/api/v1/appointments/user/{user_id}")
    assert response.status_code == 200
    appointments = response.json()
    assert any(a["id"] == appointment_id for a in appointments)

    # Get all appointments for doctor
    response = client.get(f"/api/v1/appointments/doctor/{doctor_id}")
    assert response.status_code == 200
    appointments = response.json()
    assert any(a["id"] == appointment_id for a in appointments)

    # Get appointment by id
    response = client.get(f"/api/v1/appointments/{appointment_id}")
    assert response.status_code == 200
    fetched = response.json()
    assert fetched["name"] == appointment_data["name"]

    # Update appointment
    update_data = {"notes": "Updated notes"}
    response = client.put(f"/api/v1/appointments/{appointment_id}", json=update_data)
    assert response.status_code == 200
    updated = response.json()
    assert updated["notes"] == "Updated notes"

    # Delete appointment
    response = client.delete(f"/api/v1/appointments/{appointment_id}")
    assert response.status_code == 200
    # Confirm deletion
    response = client.get(f"/api/v1/appointments/{appointment_id}")
    assert response.status_code == 404
