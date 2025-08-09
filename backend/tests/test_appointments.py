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
        assert response.status_code == 200 or response.status_code == 201
        appointment = response.json()

        assert appointment["name"] == appointment_data["name"]
        assert appointment["user_id"] == user_id
        assert appointment["doctor_id"] == doctor_id
        assert appointment["date"] == appointment_data["date"]
        assert appointment["time"] == appointment_data["time"]        
        appointment_id = appointment["id"]

        response = client.get(f"/api/v1/appointments/user/{user_id}")
        assert response.status_code == 200
        appointments = response.json()
        assert any(a["id"] == appointment_id for a in appointments)

        response = client.get(f"/api/v1/appointments/doctor/{doctor_id}")
        assert response.status_code == 200
        appointments = response.json()
        assert any(a["id"] == appointment_id for a in appointments)

        response = client.get(f"/api/v1/appointments/{appointment_id}")
        assert response.status_code == 200
        fetched = response.json()
        assert fetched["name"] == appointment_data["name"]

        update_data = {"notes": "Updated notes"}
        response = client.put(f"/api/v1/appointments/{appointment_id}", json=update_data)
        assert response.status_code == 200
        updated = response.json()
        assert updated["notes"] == "Updated notes"

        response = client.delete(f"/api/v1/appointments/{appointment_id}")
        assert response.status_code == 200
        
        response = client.get(f"/api/v1/appointments/{appointment_id}")
        assert response.status_code == 404

    def test_appointment_reminder_creation(self, client, test_db):
        """Test that reminders are created for appointments"""
        from datetime import datetime, timedelta
        
        self.create_admin_session(client)
        
        user_id = self.create_user(test_db)
        doctor_id = self.create_doctor(test_db)
        
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
        
        reminders = ReminderService.auto_create_appointment_reminders(
            test_db, 
            appointment_id, 
            [timedelta(hours=48), timedelta(hours=2), timedelta(minutes=30)]
        )
        
        assert len(reminders) >= 1, "At least one reminder should be created for future appointment"
        
        db_reminders = test_db.query(Reminder).filter_by(
            user_id=user_id, 
            related_id=appointment_id
        ).all()
        
        assert len(db_reminders) >= 1, "Reminders should be saved in database"
        
        for reminder in db_reminders:
            assert reminder.user_id == user_id
            assert reminder.related_id == appointment_id
            assert "appointment" in reminder.title.lower()
            assert reminder.scheduled_time is not None

    def test_appointment_with_medicines_endpoint(self, client, test_db):
        """Test appointment endpoints with medicines relationship, including cache behavior"""
        from src.models.medicine import Medicine
        from src.utils.cache import Cache
        from datetime import date, timedelta
        
        self.create_admin_session(client)
        
        user_id = self.create_user(test_db)
        doctor_id = self.create_doctor(test_db)
        
        appointment_data = {
            "name": "Medicine Consultation",
            "date": "2025-07-15",
            "time": "10:00:00",
            "notes": "Prescription needed",
            "user_id": user_id,
            "doctor_id": doctor_id
        }
        response = client.post("/api/v1/appointments/", json=appointment_data)
        assert response.status_code == 200 or response.status_code == 201
        appointment = response.json()
        appointment_id = appointment["id"]
        
        medicine1 = Medicine(
            user_id=user_id,
            appointment_id=appointment_id,
            doctor_id=doctor_id,
            name="Paracetamol",
            dosage="500mg",
            frequency="Twice daily",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=7),
            notes="Take after meals"
        )
        medicine2 = Medicine(
            user_id=user_id,
            appointment_id=appointment_id,
            doctor_id=doctor_id,
            name="Vitamin D",
            dosage="1000 IU",
            frequency="Once daily",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            notes="Take with breakfast"
        )
        
        test_db.add(medicine1)
        test_db.add(medicine2)
        test_db.commit()
        test_db.refresh(medicine1)
        test_db.refresh(medicine2)
        
        Cache.delete(f"appointments_user_{user_id}")
        Cache.delete(f"appointments_doctor_{doctor_id}")
        
        response = client.get(f"/api/v1/appointments/user/{user_id}")
        assert response.status_code == 200
        appointments = response.json()
        
        target_appointment = None
        for apt in appointments:
            if apt["id"] == appointment_id:
                target_appointment = apt
                break
        
        assert target_appointment is not None, "Appointment should be found in user appointments"
        assert target_appointment["name"] == "Medicine Consultation"
        assert target_appointment["medicines"] is not None, "Medicines should not be None"
        assert len(target_appointment["medicines"]) == 2, "Should have 2 medicines"
        assert medicine1.id in target_appointment["medicines"], "Medicine 1 ID should be in the list"
        assert medicine2.id in target_appointment["medicines"], "Medicine 2 ID should be in the list"
        
        for medicine_id in target_appointment["medicines"]:
            assert isinstance(medicine_id, int), f"Medicine ID should be an integer, got {type(medicine_id)}"
        
        Cache.delete(f"appointments_doctor_{doctor_id}")
        response = client.get(f"/api/v1/appointments/doctor/{doctor_id}")
        assert response.status_code == 200
        appointments = response.json()
        
        target_appointment = None
        for apt in appointments:
            if apt["id"] == appointment_id:
                target_appointment = apt
                break
        
        assert target_appointment is not None, "Appointment should be found in doctor appointments"
        assert target_appointment["medicines"] is not None, "Medicines should not be None"
        assert len(target_appointment["medicines"]) == 2, "Should have 2 medicines"
        assert medicine1.id in target_appointment["medicines"], "Medicine 1 ID should be in the list"
        assert medicine2.id in target_appointment["medicines"], "Medicine 2 ID should be in the list"
        
        response = client.get(f"/api/v1/appointments/user/{user_id}")
        assert response.status_code == 200
        cached_appointments = response.json()
        
        cached_target = None
        for apt in cached_appointments:
            if apt["id"] == appointment_id:
                cached_target = apt
                break
        
        assert cached_target is not None, "Cached appointment should be found"
        assert cached_target["medicines"] == target_appointment["medicines"], "Cached response should match non-cached"
        
        appointment_data_no_med = {
            "name": "Simple Consultation",
            "date": "2025-07-16",
            "time": "11:00:00",
            "notes": "No medication needed",
            "user_id": user_id,
            "doctor_id": doctor_id
        }
        response = client.post("/api/v1/appointments/", json=appointment_data_no_med)
        assert response.status_code == 200 or response.status_code == 201
        no_med_appointment = response.json()
        no_med_appointment_id = no_med_appointment["id"]
        
        Cache.delete(f"appointments_user_{user_id}")
        response = client.get(f"/api/v1/appointments/user/{user_id}")
        assert response.status_code == 200
        appointments = response.json()
        
        no_med_target = None
        for apt in appointments:
            if apt["id"] == no_med_appointment_id:
                no_med_target = apt
                break
        
        assert no_med_target is not None, "Appointment without medicines should be found"
        assert no_med_target["medicines"] is None or no_med_target["medicines"] == [], "Appointment without medicines should have None or empty medicines list"

    def test_cache_invalidation_with_medicines(self, client, test_db):
        """Test that cache invalidation works properly when medicines are involved"""
        from src.models.medicine import Medicine
        from src.utils.cache import Cache
        from datetime import date, timedelta
        
        self.create_admin_session(client)
        
        user_id = self.create_user(test_db)
        doctor_id = self.create_doctor(test_db)
        
        # Create appointment
        appointment_data = {
            "name": "Cache Test Consultation",
            "date": "2025-07-20",
            "time": "14:00:00",
            "notes": "Testing cache behavior",
            "user_id": user_id,
            "doctor_id": doctor_id
        }
        response = client.post("/api/v1/appointments/", json=appointment_data)
        assert response.status_code == 200 or response.status_code == 201
        appointment = response.json()
        appointment_id = appointment["id"]
        
        Cache.delete(f"appointments_user_{user_id}")
        response = client.get(f"/api/v1/appointments/user/{user_id}")
        assert response.status_code == 200
        appointments = response.json()
        target_appointment = next((apt for apt in appointments if apt["id"] == appointment_id), None)
        assert target_appointment is not None
        assert target_appointment["medicines"] is None or target_appointment["medicines"] == []
        
        medicine = Medicine(
            user_id=user_id,
            appointment_id=appointment_id,
            doctor_id=doctor_id,
            name="Test Medicine",
            dosage="250mg",
            frequency="Once daily",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=5),
            notes="Test notes"
        )
        test_db.add(medicine)
        test_db.commit()
        test_db.refresh(medicine)
        
        response = client.get(f"/api/v1/appointments/user/{user_id}")
        assert response.status_code == 200
        cached_appointments = response.json()
        cached_target = next((apt for apt in cached_appointments if apt["id"] == appointment_id), None)
        assert cached_target is not None
        assert cached_target["medicines"] is None or cached_target["medicines"] == []
        
        Cache.delete(f"appointments_user_{user_id}")
        response = client.get(f"/api/v1/appointments/user/{user_id}")
        assert response.status_code == 200
        fresh_appointments = response.json()
        fresh_target = next((apt for apt in fresh_appointments if apt["id"] == appointment_id), None)
        assert fresh_target is not None
        assert fresh_target["medicines"] is not None
        assert len(fresh_target["medicines"]) == 1
        assert medicine.id in fresh_target["medicines"]
