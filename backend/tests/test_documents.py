"""
Document API tests
"""
import pytest
import io
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from src.models.user import User
from src.schemas.user import UserCreate
from src.services.user_service import UserService
from src.core.config import settings

## TODO: Add more tests for the Document API
## TODO: Add unit tests for the Document service
class TestDocuments:
    """Test document CRUD operations"""

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

    def test_document_crud(self, client, test_db):
        """Test document CRUD operations"""
        # Set up authenticated session for document creation (RequireAuth)
        user, session_token = self.create_authenticated_session(client, test_db)
        user_id = user.id
        
        # Create document
        document_data = {
            "name": "Prescription.pdf",
            "file_url": "https://example.com/file.pdf",
            "user_id": user_id
        }
        response = client.post("/api/v1/documents/", json=document_data)
        assert response.status_code == 200 or response.status_code == 201
        document = response.json()
        assert document["name"] == document_data["name"]
        assert document["user_id"] == user_id
        document_id = document["id"]

        # Get all documents for user
        response = client.get(f"/api/v1/documents/user/{user_id}")
        assert response.status_code == 200
        documents = response.json()
        assert len(documents) == 1
        assert documents[0]["name"] == document_data["name"]

        # Update document
        update_data = {"name": "UpdatedPrescription.pdf"}
        response = client.put(f"/api/v1/documents/{document_id}", json=update_data)
        assert response.status_code == 200
        updated = response.json()
        assert updated["name"] == "UpdatedPrescription.pdf"

        # Delete document
        response = client.delete(f"/api/v1/documents/{document_id}")
        assert response.status_code == 200
        
        # Confirm deletion
        response = client.get(f"/api/v1/documents/user/{user_id}")
        assert response.status_code == 200
        assert response.json() == []

    # Upload endpoint tests
    def create_test_file(self, filename: str = "test_document.txt", content: str = "This is a test document for upload."):
        """Create a test file in memory for upload testing"""
        return io.BytesIO(content.encode('utf-8'))

    def test_upload_without_authentication(self, client, test_db):
        """Test upload endpoint without authentication (should fail)"""
        test_file = self.create_test_file()
        files = {"file": ("test.txt", test_file, "text/plain")}
        
        response = client.post("/api/v1/documents/upload", files=files)
        assert response.status_code == 401
        assert "No session token provided" in response.json()["detail"] or "Authentication required" in response.json()["detail"]

    def test_upload_with_invalid_session(self, client, test_db):
        """Test upload endpoint with invalid session token"""
        test_file = self.create_test_file()
        files = {"file": ("test.txt", test_file, "text/plain")}
        
        # Set invalid session token
        client.cookies.set("session_token", "invalid_token_12345")
        
        response = client.post("/api/v1/documents/upload", files=files)
        assert response.status_code == 401
        assert "Invalid or expired session" in response.json()["detail"]

    def test_upload_no_file(self, client, test_db):
        """Test upload endpoint without providing a file"""
        user, session_token = self.create_authenticated_session(client, test_db)
        
        response = client.post("/api/v1/documents/upload")
        assert response.status_code == 422  # Validation error for missing file

    def test_upload_invalid_file_type(self, client, test_db):
        """Test upload with unsupported file type"""
        user, session_token = self.create_authenticated_session(client, test_db)
        
        test_file = self.create_test_file()
        files = {"file": ("malware.exe", test_file, "application/x-executable")}
        
        response = client.post("/api/v1/documents/upload", files=files)
        assert response.status_code == 400
        assert "File type not allowed" in response.json()["detail"]

    def test_upload_no_filename(self, client, test_db):
        """Test upload with no filename"""
        user, session_token = self.create_authenticated_session(client, test_db)
        
        test_file = self.create_test_file()
        files = {"file": ("", test_file, "text/plain")}  # Empty filename
        
        response = client.post("/api/v1/documents/upload", files=files)
        assert response.status_code == 422  # FastAPI validation error for missing filename

    @patch('src.api.documents.upload_file_to_s3')
    def test_upload_successful_pdf(self, mock_upload, client, test_db):
        """Test successful PDF upload"""
        user, session_token = self.create_authenticated_session(client, test_db)
        
        # Mock the S3 upload to return a URL
        mock_upload.return_value = "https://test-bucket.s3.amazonaws.com/uuid-generated-filename.pdf"
        
        test_file = self.create_test_file(content="PDF content here")
        files = {"file": ("document.pdf", test_file, "application/pdf")}
        
        response = client.post("/api/v1/documents/upload", files=files)
        assert response.status_code == 200
        
        data = response.json()
        assert data["filename"] == "document.pdf"
        assert data["file_url"] == "https://test-bucket.s3.amazonaws.com/uuid-generated-filename.pdf"
        assert data["message"] == "File uploaded successfully"
        
        # Verify the upload function was called
        mock_upload.assert_called_once()

    @patch('src.api.documents.upload_file_to_s3')
    def test_upload_successful_image(self, mock_upload, client, test_db):
        """Test successful image upload"""
        user, session_token = self.create_authenticated_session(client, test_db)
        
        # Mock the S3 upload to return a URL
        mock_upload.return_value = "https://test-bucket.s3.amazonaws.com/uuid-generated-filename.jpg"
        
        test_file = self.create_test_file(content="JPEG image data")
        files = {"file": ("photo.jpg", test_file, "image/jpeg")}
        
        response = client.post("/api/v1/documents/upload", files=files)
        assert response.status_code == 200
        
        data = response.json()
        assert data["filename"] == "photo.jpg"
        assert data["file_url"] == "https://test-bucket.s3.amazonaws.com/uuid-generated-filename.jpg"

    @patch('src.api.documents.upload_file_to_s3')
    def test_upload_s3_credentials_error(self, mock_upload, client, test_db):
        """Test upload when S3 credentials are not configured"""
        user, session_token = self.create_authenticated_session(client, test_db)
        
        # Mock S3 upload to raise credentials error
        mock_upload.side_effect = HTTPException(
            status_code=500, 
            detail="AWS credentials not configured"
        )
        
        test_file = self.create_test_file()
        files = {"file": ("document.pdf", test_file, "application/pdf")}
        
        response = client.post("/api/v1/documents/upload", files=files)
        assert response.status_code == 500
        assert "AWS credentials not configured" in response.json()["detail"]

    @patch('src.api.documents.upload_file_to_s3')
    def test_upload_s3_client_error(self, mock_upload, client, test_db):
        """Test upload when S3 upload fails"""
        user, session_token = self.create_authenticated_session(client, test_db)
        
        # Mock S3 upload to raise client error
        mock_upload.side_effect = HTTPException(
            status_code=500, 
            detail="Failed to upload file to S3: Access Denied"
        )
        
        test_file = self.create_test_file()
        files = {"file": ("document.pdf", test_file, "application/pdf")}
        
        response = client.post("/api/v1/documents/upload", files=files)
        assert response.status_code == 500
        assert "Failed to upload file to S3" in response.json()["detail"]

    def test_upload_supported_file_types(self, client, test_db):
        """Test that all supported file types are accepted"""
        user, session_token = self.create_authenticated_session(client, test_db)
        
        supported_files = [
            ("document.pdf", "application/pdf"),
            ("document.doc", "application/msword"),
            ("document.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
            ("text.txt", "text/plain"),
            ("photo.jpg", "image/jpeg"),
            ("photo.jpeg", "image/jpeg"),
            ("photo.png", "image/png"),
            ("data.csv", "text/csv"),
            ("spreadsheet.xls", "application/vnd.ms-excel"),
            ("spreadsheet.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
        ]
        
        with patch('src.api.documents.upload_file_to_s3') as mock_upload:
            mock_upload.return_value = "https://test-bucket.s3.amazonaws.com/test-file"
            
            for filename, content_type in supported_files:
                test_file = self.create_test_file()
                files = {"file": (filename, test_file, content_type)}
                
                response = client.post("/api/v1/documents/upload", files=files)
                assert response.status_code == 200, f"Failed for file type: {filename}"

    @patch('src.api.documents.upload_file_to_s3')
    def test_upload_file_size_validation(self, mock_upload, client, test_db):
        """Test file size validation (this test simulates the validation logic)"""
        user, session_token = self.create_authenticated_session(client, test_db)
        
        # Mock the upload function
        mock_upload.return_value = "https://test-bucket.s3.amazonaws.com/test-file.pdf"
        
        # Create a normal sized file (should pass)
        normal_content = "A" * 1024  # 1KB file
        test_file = io.BytesIO(normal_content.encode('utf-8'))
        files = {"file": ("normal.pdf", test_file, "application/pdf")}
        
        response = client.post("/api/v1/documents/upload", files=files)
        assert response.status_code == 200

    def test_upload_unsupported_file_types(self, client, test_db):
        """Test that unsupported file types are rejected"""
        user, session_token = self.create_authenticated_session(client, test_db)
        
        unsupported_files = [
            ("script.py", "text/x-python"),
            ("archive.zip", "application/zip"),
            ("executable.exe", "application/x-executable"),
            ("video.mp4", "video/mp4"),
            ("audio.mp3", "audio/mpeg"),
        ]
        
        for filename, content_type in unsupported_files:
            test_file = self.create_test_file()
            files = {"file": (filename, test_file, content_type)}
            
            response = client.post("/api/v1/documents/upload", files=files)
            assert response.status_code == 400, f"Should have failed for file type: {filename}"
            assert "File type not allowed" in response.json()["detail"]
