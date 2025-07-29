import pytest
from src.models.user import User
from src.models.doctor import Doctor
from src.schemas.user import UserCreate
from src.services.user_service import UserService
from src.core.config import settings

class TestAppointments:

    def create_admin_session(self, client):
        client.cookies.set("session_token", settings.ADMIN_SESSION_TOKEN)
    
    def create_user(self, test_db):
        user = User(name="Test User", phone="1234567890")
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        return user.id

    def create_doctor(self, test_db):
        doctor = Doctor(name="Dr. A. Kumar", location="Delhi")
        test_db.add(doctor)
        test_db.commit()
        test_db.refresh(doctor)
        return doctor.id

    def test_create_appointment_valid_data(self, client, test_db):
        self.create_admin_session(client)
        
        user_id = self.create_user(test_db)
        doctor_id = self.create_doctor(test_db)
        
        appointment_data = {
            "name": "Consultation",
            "date": "2025-07-03",
            "time": "14:30:00",
            "notes": "Eat healthy",
            "user_id": user_id,
            "doctor_id": doctor_id
        }
        
        response = client.post("/api/v1/appointments/", json=appointment_data)
        assert response.status_code in [200, 201]
        appointment = response.json()
        assert appointment["name"] == appointment_data["name"]
        assert appointment["user_id"] == user_id
        assert appointment["doctor_id"] == doctor_id
        assert "id" in appointment

    def test_create_appointment_missing_required_fields(self, client, test_db):
        self.create_admin_session(client)
        
        user_id = self.create_user(test_db)
        doctor_id = self.create_doctor(test_db)
        
        incomplete_data = {
            "name": "Consultation",
            "user_id": user_id,
            "doctor_id": doctor_id
        }
        
        response = client.post("/api/v1/appointments/", json=incomplete_data)
        assert response.status_code == 422

    def test_create_appointment_unauthorized(self, client, test_db):
        user_id = self.create_user(test_db)
        doctor_id = self.create_doctor(test_db)
        
        appointment_data = {
            "name": "Consultation",
            "date": "2025-07-03",
            "time": "14:30:00",
            "notes": "Eat healthy",
            "user_id": user_id,
            "doctor_id": doctor_id
        }
        
        response = client.post("/api/v1/appointments/", json=appointment_data)
        assert response.status_code == 401

    def test_get_appointment_by_id_nonexistent(self, client, test_db):
        response = client.get("/api/v1/appointments/99999")
        assert response.status_code == 404

    def test_create_appointment_invalid_datetime(self, client, test_db):
        self.create_admin_session(client)
        
        user_id = self.create_user(test_db)
        doctor_id = self.create_doctor(test_db)
        
        invalid_data = {
            "name": "Consultation",
            "date": "invalid-date",
            "time": "25:30:00",
            "notes": "Test",
            "user_id": user_id,
            "doctor_id": doctor_id
        }
        
        response = client.post("/api/v1/appointments/", json=invalid_data)
        assert response.status_code == 422

    def test_update_appointment_valid_data(self, client, test_db):
        self.create_admin_session(client)
        
        user_id = self.create_user(test_db)
        doctor_id = self.create_doctor(test_db)
        
        appointment_data = {
            "name": "Consultation",
            "date": "2025-07-03",
            "time": "14:30:00",
            "notes": "Eat healthy",
            "user_id": user_id,
            "doctor_id": doctor_id
        }
        
        create_response = client.post("/api/v1/appointments/", json=appointment_data)
        appointment_id = create_response.json()["id"]
        
        update_data = {"notes": "Updated notes", "name": "Follow-up"}
        response = client.put(f"/api/v1/appointments/{appointment_id}", json=update_data)
        assert response.status_code == 200
        updated = response.json()
        assert updated["notes"] == "Updated notes"
        assert updated["name"] == "Follow-up"

    def test_delete_appointment_and_verify_gone(self, client, test_db):
        self.create_admin_session(client)
        
        user_id = self.create_user(test_db)
        doctor_id = self.create_doctor(test_db)
        
        appointment_data = {
            "name": "Consultation",
            "date": "2025-07-03",
            "time": "14:30:00",
            "notes": "Eat healthy",
            "user_id": user_id,
            "doctor_id": doctor_id
        }
        
        create_response = client.post("/api/v1/appointments/", json=appointment_data)
        appointment_id = create_response.json()["id"]
        
        delete_response = client.delete(f"/api/v1/appointments/{appointment_id}")
        assert delete_response.status_code == 200
        assert "message" in delete_response.json()
        
        verify_response = client.get(f"/api/v1/appointments/{appointment_id}")
        assert verify_response.status_code == 404

    def test_appointment_complete_workflow(self, client, test_db):
        self.create_admin_session(client)
        
        user_id = self.create_user(test_db)
        doctor_id = self.create_doctor(test_db)
        
        appointment_data = {
            "name": "Initial Consultation",
            "date": "2025-07-03",
            "time": "14:30:00",
            "notes": "First visit",
            "user_id": user_id,
            "doctor_id": doctor_id
        }
        
        create_response = client.post("/api/v1/appointments/", json=appointment_data)
        assert create_response.status_code in [200, 201]
        appointment_id = create_response.json()["id"]
        
        get_response = client.get(f"/api/v1/appointments/{appointment_id}")
        assert get_response.status_code == 200
        assert get_response.json()["name"] == "Initial Consultation"
        
        update_data = {"name": "Follow-up", "notes": "Updated visit"}
        update_response = client.put(f"/api/v1/appointments/{appointment_id}", json=update_data)
        assert update_response.status_code == 200
        
        verify_update = client.get(f"/api/v1/appointments/{appointment_id}")
        assert verify_update.json()["name"] == "Follow-up"
        assert verify_update.json()["notes"] == "Updated visit"
        
        delete_response = client.delete(f"/api/v1/appointments/{appointment_id}")
        assert delete_response.status_code == 200
        
        verify_delete = client.get(f"/api/v1/appointments/{appointment_id}")
        assert verify_delete.status_code == 404
