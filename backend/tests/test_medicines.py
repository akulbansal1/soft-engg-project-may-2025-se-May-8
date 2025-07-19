"""
Medicine API tests
"""
import pytest
from src.models.user import User
from src.schemas.user import UserCreate
from src.services.user_service import UserService
from src.core.config import settings
from src.models.doctor import Doctor
from src.models.appointment import Appointment
from datetime import date, time

## TODO: Add more tests for the Medicine API
## TODO: Add unit tests for the Medicine service
class TestMedicines:
    """Test medicine CRUD operations"""

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

    def create_doctor(self, test_db):
        """Helper to create a doctor for testing"""
        doctor = Doctor(name="Test Doctor", location="Test Hospital")
        test_db.add(doctor)
        test_db.commit()
        test_db.refresh(doctor)
        return doctor.id

    def create_appointment(self, test_db, user_id, doctor_id):
        """Helper to create an appointment for testing"""
        appointment = Appointment(
            user_id=user_id,
            doctor_id=doctor_id,
            name="Test Appointment",
            date=date(2025, 7, 19),
            time=time(10, 0),
            notes="Test appointment notes"
        )
        test_db.add(appointment)
        test_db.commit()
        test_db.refresh(appointment)
        return appointment.id

    def test_medicine_crud(self, client, test_db):
        """Test medicine CRUD operations"""
        # Set up authenticated session for document creation (RequireAuth)
        user, session_token = self.create_authenticated_session(client, test_db)
        user_id = user.id
        doctor_id = self.create_doctor(test_db)
        appointment_id = self.create_appointment(test_db, user_id, doctor_id)

        # Create medicine with doctor_id and appointment_id
        medicine_data = {
            "name": "Paracetamol",
            "dosage": "500mg",
            "frequency": "Once a day after dinner",
            "start_date": "2025-06-25",
            "end_date": "2025-07-05",
            "notes": "Take with food",
            "user_id": user_id,
            "doctor_id": doctor_id,
            "appointment_id": appointment_id
        }
        response = client.post("/api/v1/medicines/", json=medicine_data)
        assert response.status_code == 200 or response.status_code == 201
        medicine = response.json()
        assert medicine["name"] == medicine_data["name"]
        assert medicine["user_id"] == user_id
        assert medicine["doctor_id"] == doctor_id
        assert medicine["appointment_id"] == appointment_id
        medicine_id = medicine["id"]

        # Get all medicines for user
        response = client.get(f"/api/v1/medicines/user/{user_id}")
        assert response.status_code == 200
        medicines = response.json()
        assert len(medicines) == 1

        # Update medicine (should not update doctor_id or appointment_id)
        update_data = {"name": "Ibuprofen"}
        response = client.put(f"/api/v1/medicines/{medicine_id}", json=update_data)
        assert response.status_code == 200
        updated = response.json()
        assert updated["name"] == "Ibuprofen"
        assert updated["doctor_id"] == doctor_id
        assert updated["appointment_id"] == appointment_id

        # Delete medicine
        response = client.delete(f"/api/v1/medicines/{medicine_id}")
        assert response.status_code == 200
        # Confirm deletion
        response = client.get(f"/api/v1/medicines/user/{user_id}")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_medicine_without_appointment(self, client, test_db):
        user, session_token = self.create_authenticated_session(client, test_db)
        user_id = user.id
        doctor_id = self.create_doctor(test_db)
        medicine_data = {
            "name": "Aspirin",
            "dosage": "100mg",
            "frequency": "Twice a day",
            "start_date": "2025-07-01",
            "end_date": "2025-07-10",
            "notes": "Take with water",
            "user_id": user_id,
            "doctor_id": doctor_id
        }
        response = client.post("/api/v1/medicines/", json=medicine_data)
        assert response.status_code == 200 or response.status_code == 201
        medicine = response.json()
        assert medicine["name"] == medicine_data["name"]
        assert medicine["doctor_id"] == doctor_id
        assert medicine["user_id"] == user_id
        assert medicine.get("appointment_id") is None
