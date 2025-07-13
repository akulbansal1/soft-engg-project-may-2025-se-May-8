"""
Doctor API tests
"""
import pytest


class TestDoctors:
    """Test doctor CRUD operations"""

    def test_doctor_crud(self, client, test_db):
        """Test doctor CRUD operations"""
        # Create doctor
        doctor_data = {
            "name": "Dr. A. Kumar",
            "location": "Delhi"
        }
        response = client.post("/api/v1/doctors/", json=doctor_data)
        assert response.status_code == 200 or response.status_code == 201
        doctor = response.json()
        assert doctor["name"] == doctor_data["name"]
        assert doctor["location"] == doctor_data["location"]
        doctor_id = doctor["id"]

        # Get all doctors
        response = client.get("/api/v1/doctors/")
        assert response.status_code == 200
        doctors = response.json()
        assert any(d["id"] == doctor_id for d in doctors)

        # Get doctor by id
        response = client.get(f"/api/v1/doctors/{doctor_id}")
        assert response.status_code == 200
        fetched = response.json()
        assert fetched["name"] == doctor_data["name"]

        # Update doctor
        update_data = {"location": "Mumbai"}
        response = client.put(f"/api/v1/doctors/{doctor_id}", json=update_data)
        assert response.status_code == 200
        updated = response.json()
        assert updated["location"] == "Mumbai"

        # Delete doctor
        response = client.delete(f"/api/v1/doctors/{doctor_id}")
        assert response.status_code == 200
        
        # Confirm deletion
        response = client.get(f"/api/v1/doctors/{doctor_id}")
        assert response.status_code == 404
