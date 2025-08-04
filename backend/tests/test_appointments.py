"""
Appointment API tests
"""
import pytest
from src.models.user import User
from src.models.doctor import Doctor
from src.models.reminder import Reminder
from src.schemas.user import UserCreate
from src.services.user_service import UserService
from src.services.reminder_service import ReminderService
from src.core.config import settings

## TODO: Add more tests for the appointment API
## TODO: Add unit tests for the appointmnet service 
class TestAppointments:
    """Test appointment CRUD operations"""

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
        doctor = Doctor(name="Dr. A. Kumar", location="Delhi")
        test_db.add(doctor)
        test_db.commit()
        test_db.refresh(doctor)
        return doctor.id

    def test_appointment_crud(self, client, test_db):
        """Test appointment CRUD operations"""
        # Set up admin authentication for CRUD operations
        self.create_admin_session(client)
        
        user_id = self.create_user(test_db)
        doctor_id = self.create_doctor(test_db)
        
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

    def test_appointment_reminder_creation(self, client, test_db):
        """Test that reminders are created for appointments"""
        from datetime import datetime, timedelta
        
        # Set up admin authentication
        self.create_admin_session(client)
        
        user_id = self.create_user(test_db)
        doctor_id = self.create_doctor(test_db)
        
        # Create appointment with future date
        future_date = datetime.now() + timedelta(days=2)
        appointment_data = {
            "name": "Future Consultation",
            "date": future_date.strftime("%Y-%m-%d"),
            "time": "14:30:00",
            "notes": "Test appointment for reminders",
            "user_id": user_id,
            "doctor_id": doctor_id
        }
        
        response = client.post("/api/v1/appointments/", json=appointment_data)
        assert response.status_code == 200 or response.status_code == 201
        appointment = response.json()
        appointment_id = appointment["id"]
        
        # Create reminders for this appointment
        reminders = ReminderService.auto_create_appointment_reminders(
            test_db, 
            appointment_id, 
            [timedelta(hours=48), timedelta(hours=2), timedelta(minutes=30)]
        )
        
        # Check that reminders were created (should be 3 default reminders)
        assert len(reminders) >= 1, "At least one reminder should be created for future appointment"
        
        # Verify reminders in database
        db_reminders = test_db.query(Reminder).filter_by(
            user_id=user_id, 
            related_id=appointment_id
        ).all()
        
        assert len(db_reminders) >= 1, "Reminders should be saved in database"
        
        # Check reminder properties
        for reminder in db_reminders:
            assert reminder.user_id == user_id
            assert reminder.related_id == appointment_id
            assert "appointment" in reminder.title.lower()
            assert reminder.scheduled_time is not None
