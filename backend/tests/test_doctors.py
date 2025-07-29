import pytest
from src.schemas.user import UserCreate
from src.services.user_service import UserService
from src.core.config import settings

class TestDoctors:

    def create_admin_session(self, client):
        client.cookies.set("session_token", settings.ADMIN_SESSION_TOKEN)

    def create_authenticated_session(self, client, test_db):
        user_data = UserCreate(name="Test User", phone="1234567890", is_active=True)
        user = UserService.register_user(test_db, user_data)
        
        session_data = UserService.issue_session(user.id)
        session_token = session_data["session_token"]
        
        client.cookies.set("session_token", session_token)
        
        return user, session_token

    def test_create_doctor_admin_authorized(self, client, test_db):
        self.create_admin_session(client)
        
        doctor_data = {
            "name": "Dr. A. Kumar",
            "location": "Delhi"
        }
        
        response = client.post("/api/v1/doctors/", json=doctor_data)
        assert response.status_code in [200, 201]
        doctor = response.json()
        assert doctor["name"] == doctor_data["name"]
        assert doctor["location"] == doctor_data["location"]
        assert "id" in doctor

    def test_create_doctor_missing_required_fields(self, client, test_db):
        self.create_admin_session(client)
        
        incomplete_data = {
            "name": "Dr. A. Kumar"
        }
        
        response = client.post("/api/v1/doctors/", json=incomplete_data)
        assert response.status_code == 422

    def test_create_doctor_patient_unauthorized(self, client, test_db):
        user, session_token = self.create_authenticated_session(client, test_db)
        
        doctor_data = {
            "name": "Dr. A. Kumar",
            "location": "Delhi"
        }
        
        response = client.post("/api/v1/doctors/", json=doctor_data)
        assert response.status_code == 401

    def test_create_doctor_no_authentication(self, client, test_db):
        doctor_data = {
            "name": "Dr. A. Kumar",
            "location": "Delhi"
        }
        
        response = client.post("/api/v1/doctors/", json=doctor_data)
        assert response.status_code == 401

    def test_get_all_doctors_authenticated_users_only(self, client, test_db):
        self.create_admin_session(client)
        
        doctor_data = {
            "name": "Dr. A. Kumar",
            "location": "Delhi"
        }
        client.post("/api/v1/doctors/", json=doctor_data)
        
        user, session_token = self.create_authenticated_session(client, test_db)
        
        response = client.get("/api/v1/doctors/")
        assert response.status_code == 200
        doctors = response.json()
        assert isinstance(doctors, list)
        assert len(doctors) >= 1

    def test_get_all_doctors_unauthenticated_denied(self, client, test_db):
        response = client.get("/api/v1/doctors/")
        assert response.status_code == 401

    def test_get_doctor_by_id_authenticated_users_only(self, client, test_db):
        self.create_admin_session(client)
        
        doctor_data = {
            "name": "Dr. A. Kumar",
            "location": "Delhi"
        }
        create_response = client.post("/api/v1/doctors/", json=doctor_data)
        doctor_id = create_response.json()["id"]
        
        user, session_token = self.create_authenticated_session(client, test_db)
        
        response = client.get(f"/api/v1/doctors/{doctor_id}")
        assert response.status_code == 200
        doctor = response.json()
        assert doctor["name"] == "Dr. A. Kumar"
        assert doctor["id"] == doctor_id

    def test_get_doctor_by_id_nonexistent(self, client, test_db):
        response = client.get("/api/v1/doctors/99999")
        assert response.status_code == 404

    def test_update_doctor_admin_authorized(self, client, test_db):
        self.create_admin_session(client)
        
        doctor_data = {
            "name": "Dr. A. Kumar",
            "location": "Delhi"
        }
        create_response = client.post("/api/v1/doctors/", json=doctor_data)
        doctor_id = create_response.json()["id"]
        
        update_data = {"location": "Mumbai", "name": "Dr. Amit Kumar"}
        response = client.put(f"/api/v1/doctors/{doctor_id}", json=update_data)
        assert response.status_code == 200
        updated = response.json()
        assert updated["location"] == "Mumbai"
        assert updated["name"] == "Dr. Amit Kumar"

    def test_update_doctor_patient_unauthorized(self, client, test_db):
        self.create_admin_session(client)
        
        doctor_data = {
            "name": "Dr. A. Kumar",
            "location": "Delhi"
        }
        create_response = client.post("/api/v1/doctors/", json=doctor_data)
        doctor_id = create_response.json()["id"]
        
        user, session_token = self.create_authenticated_session(client, test_db)
        
        update_data = {"location": "Mumbai"}
        response = client.put(f"/api/v1/doctors/{doctor_id}", json=update_data)
        assert response.status_code == 401

    def test_delete_doctor_patient_unauthorized(self, client, test_db):
        self.create_admin_session(client)
        
        doctor_data = {
            "name": "Dr. A. Kumar",
            "location": "Delhi"
        }
        create_response = client.post("/api/v1/doctors/", json=doctor_data)
        doctor_id = create_response.json()["id"]
        
        user, session_token = self.create_authenticated_session(client, test_db)
        
        response = client.delete(f"/api/v1/doctors/{doctor_id}")
        assert response.status_code == 401

    def test_doctor_complete_admin_workflow(self, client, test_db):
        self.create_admin_session(client)
        
        doctor_data = {
            "name": "Dr. Initial Name",
            "location": "Delhi"
        }
        
        create_response = client.post("/api/v1/doctors/", json=doctor_data)
        assert create_response.status_code in [200, 201]
        doctor_id = create_response.json()["id"]
        
        get_response = client.get(f"/api/v1/doctors/{doctor_id}")
        assert get_response.status_code == 200
        assert get_response.json()["name"] == "Dr. Initial Name"
        
        update_data = {"name": "Dr. Updated Name", "location": "Mumbai"}
        update_response = client.put(f"/api/v1/doctors/{doctor_id}", json=update_data)
        assert update_response.status_code == 200
        assert update_response.json()["name"] == "Dr. Updated Name"
        assert update_response.json()["location"] == "Mumbai"
        
        delete_response = client.delete(f"/api/v1/doctors/{doctor_id}")
        assert delete_response.status_code == 200
        
        verify_delete = client.get(f"/api/v1/doctors/{doctor_id}")
        assert verify_delete.status_code == 404
