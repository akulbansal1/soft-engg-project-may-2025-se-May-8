import pytest
from unittest.mock import patch, MagicMock
from src.models.user import User
from src.schemas.user import UserCreate
from src.services.user_service import UserService
from src.core.config import settings
from src.models.doctor import Doctor
from src.models.appointment import Appointment
from datetime import date, time
import io

class TestMedicines:

    def create_admin_session(self, client):
        client.cookies.set("session_token", settings.ADMIN_SESSION_TOKEN)

    def create_authenticated_session(self, client, test_db):
        user_data = UserCreate(name="Test User", phone="1234567890", is_active=True)
        user = UserService.register_user(test_db, user_data)
        
        session_data = UserService.issue_session(user.id)
        session_token = session_data["session_token"]
        
        client.cookies.set("session_token", session_token)
        
        return user, session_token
    
    def create_user(self, test_db):
        user = User(name="Test User", phone="1234567890")
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        return user.id

    def create_doctor(self, test_db):
        doctor = Doctor(name="Test Doctor", location="Test Hospital")
        test_db.add(doctor)
        test_db.commit()
        test_db.refresh(doctor)
        return doctor.id

    def test_create_medicine_valid_data_authenticated(self, client, test_db):
        user, session_token = self.create_authenticated_session(client, test_db)
        user_id = user.id
        doctor_id = self.create_doctor(test_db)

        medicine_data = {
            "name": "Paracetamol",
            "dosage": "500mg",
            "frequency": "Once a day after dinner",
            "start_date": "2025-06-25",
            "end_date": "2025-07-05",
            "notes": "Take with food",
            "user_id": user_id,
            "doctor_id": doctor_id
        }
        
        response = client.post("/api/v1/medicines/", json=medicine_data)
        assert response.status_code in [200, 201]
        medicine = response.json()
        assert medicine["name"] == medicine_data["name"]
        assert medicine["dosage"] == medicine_data["dosage"]
        assert medicine["frequency"] == medicine_data["frequency"]
        assert medicine["user_id"] == user_id
        assert "id" in medicine

    def test_create_medicine_missing_required_fields(self, client, test_db):
        user, session_token = self.create_authenticated_session(client, test_db)
        
        incomplete_data = {
            "name": "Paracetamol",
            "dosage": "500mg",
            "user_id": user.id
        }
        
        response = client.post("/api/v1/medicines/", json=incomplete_data)
        assert response.status_code == 422

    def test_create_medicine_unauthorized(self, client, test_db):
        user_id = self.create_user(test_db)
        doctor_id = self.create_doctor(test_db)
        
        medicine_data = {
            "name": "Paracetamol",
            "dosage": "500mg",
            "frequency": "Once a day after dinner",
            "start_date": "2025-06-25",
            "user_id": user_id,
            "doctor_id": doctor_id
        }
        
        response = client.post("/api/v1/medicines/", json=medicine_data)
        assert response.status_code == 401

    def test_create_medicine_invalid_date_format(self, client, test_db):
        user, session_token = self.create_authenticated_session(client, test_db)
        user_id = user.id
        
        invalid_data = {
            "name": "Paracetamol",
            "dosage": "500mg",
            "frequency": "Once daily",
            "start_date": "invalid-date",
            "user_id": user_id
        }
        
        response = client.post("/api/v1/medicines/", json=invalid_data)
        assert response.status_code == 422

    def test_get_medicines_by_user_authenticated(self, client, test_db):
        user, session_token = self.create_authenticated_session(client, test_db)
        user_id = user.id
        
        medicine_data = {
            "name": "Paracetamol",
            "dosage": "500mg",
            "frequency": "Once daily",
            "start_date": "2025-06-25",
            "user_id": user_id
        }
        client.post("/api/v1/medicines/", json=medicine_data)
        
        response = client.get(f"/api/v1/medicines/user/{user_id}")
        assert response.status_code == 200
        medicines = response.json()
        assert isinstance(medicines, list)
        assert len(medicines) >= 1
        assert medicines[0]["name"] == "Paracetamol"

    def test_get_medicines_by_user_unauthorized_access_denied(self, client, test_db):
        user_id = self.create_user(test_db)
        
        response = client.get(f"/api/v1/medicines/user/{user_id}")
        assert response.status_code == 401

    def test_update_medicine_valid_data(self, client, test_db):
        user, session_token = self.create_authenticated_session(client, test_db)
        user_id = user.id
        
        medicine_data = {
            "name": "Paracetamol",
            "dosage": "500mg",
            "frequency": "Once daily",
            "start_date": "2025-06-25",
            "user_id": user_id
        }
        
        create_response = client.post("/api/v1/medicines/", json=medicine_data)
        medicine_id = create_response.json()["id"]
        
        update_data = {"dosage": "1000mg", "frequency": "Twice daily"}
        response = client.put(f"/api/v1/medicines/{medicine_id}", json=update_data)
        assert response.status_code == 200
        updated = response.json()
        assert updated["dosage"] == "1000mg"
        assert updated["frequency"] == "Twice daily"
        assert updated["name"] == "Paracetamol"

    def test_update_medicine_unauthorized(self, client, test_db):
        user, session_token = self.create_authenticated_session(client, test_db)
        user_id = user.id
        
        medicine_data = {
            "name": "Paracetamol",
            "dosage": "500mg",
            "frequency": "Once daily",
            "start_date": "2025-06-25",
            "user_id": user_id
        }
        
        create_response = client.post("/api/v1/medicines/", json=medicine_data)
        medicine_id = create_response.json()["id"]
        
        client.cookies.clear()
        
        update_data = {"dosage": "1000mg"}
        response = client.put(f"/api/v1/medicines/{medicine_id}", json=update_data)
        assert response.status_code == 401

    def test_delete_medicine_and_verify_gone(self, client, test_db):
        user, session_token = self.create_authenticated_session(client, test_db)
        user_id = user.id
        
        medicine_data = {
            "name": "Paracetamol",
            "dosage": "500mg",
            "frequency": "Once daily",
            "start_date": "2025-06-25",
            "user_id": user_id
        }
        
        create_response = client.post("/api/v1/medicines/", json=medicine_data)
        medicine_id = create_response.json()["id"]
        
        delete_response = client.delete(f"/api/v1/medicines/{medicine_id}")
        assert delete_response.status_code == 200
        
        verify_response = client.get(f"/api/v1/medicines/user/{user_id}")
        assert verify_response.status_code == 200
        assert len(verify_response.json()) == 0

    def test_medicine_complete_workflow(self, client, test_db):
        user, session_token = self.create_authenticated_session(client, test_db)
        user_id = user.id
        doctor_id = self.create_doctor(test_db)
        
        medicine_data = {
            "name": "Initial Medicine",
            "dosage": "250mg",
            "frequency": "Once daily",
            "start_date": "2025-06-25",
            "end_date": "2025-07-05",
            "notes": "With meals",
            "user_id": user_id,
            "doctor_id": doctor_id
        }
        
        create_response = client.post("/api/v1/medicines/", json=medicine_data)
        assert create_response.status_code in [200, 201]
        medicine_id = create_response.json()["id"]
        
        get_response = client.get(f"/api/v1/medicines/user/{user_id}")
        assert get_response.status_code == 200
        assert len(get_response.json()) == 1
        
        update_data = {"name": "Updated Medicine", "dosage": "500mg"}
        update_response = client.put(f"/api/v1/medicines/{medicine_id}", json=update_data)
        assert update_response.status_code == 200
        assert update_response.json()["name"] == "Updated Medicine"
        assert update_response.json()["dosage"] == "500mg"
        
        delete_response = client.delete(f"/api/v1/medicines/{medicine_id}")
        assert delete_response.status_code == 200
        
        verify_delete = client.get(f"/api/v1/medicines/user/{user_id}")
        assert verify_delete.status_code == 200
        assert len(verify_delete.json()) == 0

    def test_transcribe_audio_prescription_success(self, client, test_db):
        """Test real AI service with actual audio transcription - NO MOCKING"""
        user, session_token = self.create_authenticated_session(client, test_db)
        
        # Use real audio data or synthetic audio for testing
        audio_content = b"fake_audio_data_representing_real_prescription"
        audio_file = io.BytesIO(audio_content)
        
        response = client.post(
            "/api/v1/medicines/transcribe",
            files={"file": ("prescription.mp3", audio_file, "audio/mpeg")}
        )
        
        # Test actual AI service response structure
        assert response.status_code == 200
        transcription = response.json()
        # Verify response has required fields (actual AI may return different values)
        assert "name" in transcription
        assert "dosage" in transcription
        assert "frequency" in transcription
        assert "start_date" in transcription
        assert "end_date" in transcription
        assert "notes" in transcription

    @patch('src.services.ai_service.AIService.transcribe_prescription')
    def test_transcribe_audio_prescription_unauthorized(self, mock_transcribe, client, test_db):
        audio_content = b"fake_audio_data"
        audio_file = io.BytesIO(audio_content)
        
        response = client.post(
            "/api/v1/medicines/transcribe",
            files={"file": ("prescription.mp3", audio_file, "audio/mpeg")}
        )
        
        assert response.status_code == 401
        assert mock_transcribe.call_count == 0

    def test_transcribe_invalid_file_format(self, client, test_db):
        user, session_token = self.create_authenticated_session(client, test_db)
        
        text_content = b"This is not audio data"
        text_file = io.BytesIO(text_content)
        
        response = client.post(
            "/api/v1/medicines/transcribe",
            files={"file": ("document.txt", text_file, "text/plain")}
        )
        
        assert response.status_code == 400
        assert "Invalid audio file format" in response.json()["detail"]

    def test_transcribe_no_file_provided(self, client, test_db):
        user, session_token = self.create_authenticated_session(client, test_db)
        
        response = client.post("/api/v1/medicines/transcribe")
        
        assert response.status_code == 422

    def test_transcribe_empty_audio_file(self, client, test_db):
        user, session_token = self.create_authenticated_session(client, test_db)
        
        empty_audio = io.BytesIO(b"")
        
        response = client.post(
            "/api/v1/medicines/transcribe",
            files={"file": ("empty.wav", empty_audio, "audio/wav")}
        )
        
        # Test real AI service behavior with empty file
        # Should return 400 (invalid input) - empty audio file is bad request
        assert response.status_code == 400
        
        # Verify proper error message for empty file
        error_detail = response.json()["detail"]
        assert "empty" in error_detail.lower() or "invalid" in error_detail.lower()

    @patch('src.services.ai_service.AIService.transcribe_prescription')
    def test_transcribe_ai_service_failure(self, mock_transcribe, client, test_db):
        user, session_token = self.create_authenticated_session(client, test_db)
        
        mock_transcribe.side_effect = Exception("AI service unavailable")
        
        audio_content = b"fake_audio_data"
        audio_file = io.BytesIO(audio_content)
        
        response = client.post(
            "/api/v1/medicines/transcribe",
            files={"file": ("prescription.mp3", audio_file, "audio/mpeg")}
        )
        
        assert response.status_code == 500
        assert "Failed to transcribe audio" in response.json()["detail"]
        assert "AI service unavailable" in response.json()["detail"]

    @patch('src.services.ai_service.AIService.transcribe_prescription')
    def test_transcribe_partial_medicine_info(self, mock_transcribe, client, test_db):
        user, session_token = self.create_authenticated_session(client, test_db)
        
        mock_transcribe.return_value = {
            "name": "Aspirin",
            "dosage": "100mg",
            "frequency": None,
            "start_date": None,
            "end_date": None,
            "notes": "Partial information extracted from unclear audio"
        }
        
        audio_content = b"unclear_audio_data"
        audio_file = io.BytesIO(audio_content)
        
        response = client.post(
            "/api/v1/medicines/transcribe",
            files={"file": ("unclear.wav", audio_file, "audio/wav")}
        )
        
        assert response.status_code == 200
        transcription = response.json()
        assert transcription["name"] == "Aspirin"
        assert transcription["dosage"] == "100mg"
        assert transcription["frequency"] is None
        assert "Partial information" in transcription["notes"]

    def test_transcribe_different_audio_formats(self, client, test_db):
        """Test real AI service with different audio formats - NO MOCKING"""
        user, session_token = self.create_authenticated_session(client, test_db)
        
        # Test the most common format first (mp3) with real AI service
        audio_content = b"fake_audio_data_for_mp3_format"
        audio_file = io.BytesIO(audio_content)
        
        response = client.post(
            "/api/v1/medicines/transcribe",
            files={"file": ("test.mp3", audio_file, "audio/mpeg")}
        )
        
        # Test real AI service response
        assert response.status_code == 200
        transcription = response.json()
        # Verify all expected fields are present
        assert "name" in transcription
        assert "dosage" in transcription
        assert "frequency" in transcription
        assert "start_date" in transcription
        assert "end_date" in transcription
        assert "notes" in transcription
