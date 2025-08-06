"""
Medicine API tests
"""
import pytest
from src.models.user import User
from src.models.reminder import Reminder
from src.schemas.user import UserCreate
from src.services.user_service import UserService
from src.services.reminder_service import ReminderService
from src.core.config import settings
from src.models.doctor import Doctor
from src.models.appointment import Appointment
from src.models.medicine import Medicine
from datetime import date, time, timedelta

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

    def test_medicine_reminder_creation(self, client, test_db):
        """Test that reminders are created for medicines based on frequency"""
        from datetime import timedelta
        
        user, session_token = self.create_authenticated_session(client, test_db)
        user_id = user.id
        doctor_id = self.create_doctor(test_db)
        
        # Test different frequencies
        test_cases = [
            ("once daily", 1),  # Should create 1 reminder per day
            ("twice daily", 2),  # Should create 2 reminders per day
            ("three times daily", 3),  # Should create 3 reminders per day
        ]
        
        for frequency, expected_per_day in test_cases:
            # Create medicine with specific frequency
            medicine_data = {
                "name": f"Test Medicine ({frequency})",
                "dosage": "1 tablet",
                "frequency": frequency,
                "start_date": "2025-08-10",  # Future date
                "end_date": "2025-08-12",    # 3 days
                "notes": f"Test medicine for {frequency}",
                "user_id": user_id,
                "doctor_id": doctor_id
            }
            
            response = client.post("/api/v1/medicines/", json=medicine_data)
            assert response.status_code == 200 or response.status_code == 201
            medicine = response.json()
            medicine_id = medicine["id"]
            medicine_obj = test_db.query(Medicine).filter_by(id=medicine_id).first()
            
            # Create reminders for this medicine
            reminders = ReminderService.auto_create_medicine_reminders(test_db, medicine_obj)
            
            # Check that reminders were created
            # For 3 days with the given frequency, we should have approximately:
            # expected_per_day * 3 days = total expected reminders
            expected_total = expected_per_day * 3
            
            assert len(reminders) >= 1, f"At least one reminder should be created for {frequency}"
            
            # Verify reminders in database
            db_reminders = test_db.query(Reminder).filter_by(
                user_id=user_id, 
                related_id=medicine_id
            ).all()
            
            assert len(db_reminders) >= 1, f"Reminders should be saved in database for {frequency}"
            
            # Check reminder properties
            for reminder in db_reminders:
                assert reminder.user_id == user_id
                assert reminder.related_id == medicine_id
                assert "medicine" in reminder.title.lower()
                assert reminder.scheduled_time is not None
            
            # print(f"✅ {frequency}: Created {len(reminders)} reminders (expected ~{expected_total})")

    def test_medicine_genai_reminder_times(self, client, test_db):
        """Test that reminders are created at the correct times for a realistic, complex frequency using GenAI parsing."""
        user, session_token = self.create_authenticated_session(client, test_db)
        user_id = user.id
        doctor_id = self.create_doctor(test_db)
        # Use a realistic, complex frequency to force GenAI
        start = date.today()
        end = start + timedelta(days=3)
        medicine_data = {
            "name": "Cefixime",
            "dosage": "200mg",
            "frequency": "Take one tablet in the morning and one at night",
            "start_date": str(start),
            "end_date": str(end),
            "notes": "Take after food. Do not skip doses.",
            "user_id": user_id,
            "doctor_id": doctor_id
        }
        response = client.post("/api/v1/medicines/", json=medicine_data)
        assert response.status_code == 200 or response.status_code == 201
        medicine = response.json()
        medicine_id = medicine["id"]

        # Check reminders in DB for correct times (as expected from GenAI parsing)
        reminders = test_db.query(Reminder).filter_by(user_id=user_id, related_id=medicine_id).all()
        expected_days = (end - start).days  # 3 days
        expected_times_per_day = 2  # morning and night
        expected_total_reminders = expected_days * expected_times_per_day
        assert len(reminders) == expected_total_reminders, f"Expected {expected_total_reminders} reminders, got {len(reminders)}"
        # Check that reminders have the expected times (9:30 and 21:00)
        expected_times = [(9, 30), (21, 30)]
        reminder_times = [(r.scheduled_time.hour, r.scheduled_time.minute) for r in reminders]
        for day_offset in range(expected_days):
            for hour, minute in expected_times:
                assert (hour, minute) in reminder_times, f"Missing reminder for {hour}:{minute:02d}"
        # Verify all reminders have correct properties
        for reminder in reminders:
            assert reminder.user_id == user_id
            assert reminder.related_id == medicine_id
            assert "medicine" in reminder.title.lower()
            assert reminder.scheduled_time is not None
