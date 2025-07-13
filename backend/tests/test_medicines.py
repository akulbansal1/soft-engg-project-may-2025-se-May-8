"""
Medicine API tests
"""
import pytest
from src.models.user import User


class TestMedicines:
    """Test medicine CRUD operations"""
    
    def create_user(self, test_db):
        """Helper to create a user for testing"""
        user = User(name="Test User", phone="1234567890")
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        return user.id

    def test_medicine_crud(self, client, test_db):
        """Test medicine CRUD operations"""
        user_id = self.create_user(test_db)
        
        # Create medicine
        medicine_data = {
            "name": "Paracetamol",
            "dosage": "500mg",
            "frequency": "Once a day after dinner",
            "start_date": "2025-06-25",
            "end_date": "2025-07-05",
            "notes": "Take with food",
            "user_id": user_id,
        }
        response = client.post("/api/v1/medicines/", json=medicine_data)
        print(response.json())  # Debugging line to see the response
        assert response.status_code == 200 or response.status_code == 201
        medicine = response.json()
        assert medicine["name"] == medicine_data["name"]
        assert medicine["user_id"] == user_id
        medicine_id = medicine["id"]

        # Get all medicines for user
        response = client.get(f"/api/v1/medicines/user/{user_id}")
        assert response.status_code == 200
        medicines = response.json()
        assert len(medicines) == 1
        assert medicines[0]["name"] == medicine_data["name"]

        # Update medicine
        update_data = {"name": "Ibuprofen"}
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
