"""
Tests for SMS verification endpoints in the authentication API. All SMS service calls are mocked to prevent real messages being sent.
"""
import pytest
from unittest.mock import patch, MagicMock


@pytest.fixture(autouse=True)
def mock_sms_service_imports():
    """Auto-mock SMS service imports to prevent real SMS operations"""
    with patch('src.services.sms_service.sms_service') as mock_proxy, \
         patch('src.services.sms_service.get_sms_service') as mock_get_sms, \
         patch('src.api.auth.sms_service', create=True) as mock_auth_sms:
        
        mock_sms_service = MagicMock()
        mock_sms_service.send_verification_code.return_value = {'success': True, 'message': 'Sent', 'expires_in': 600}
        mock_sms_service.verify_code.return_value = {'success': True, 'message': 'Verified', 'expires_at': None}
        mock_sms_service.get_verification_status.return_value = {'verified': True, 'message': 'Status', 'expires_at': None}
        mock_sms_service.send_emergency_message.return_value = {'success': True}
        mock_sms_service.is_phone_verified.return_value = True
        
        mock_proxy.return_value = mock_sms_service
        mock_get_sms.return_value = mock_sms_service
        mock_auth_sms.return_value = mock_sms_service
        
        for attr in ['send_verification_code', 'verify_code', 'get_verification_status', 'send_emergency_message', 'is_phone_verified']:
            setattr(mock_proxy, attr, getattr(mock_sms_service, attr))
        
        yield mock_sms_service


class TestSMSVerificationAPI:
    """Test SMS verification API endpoints"""

    def test_send_sms_verification_success(self, client, mock_sms_service_imports):
        """Test successful SMS verification code sending"""
        request_data = {"phone": "+1234567890"}
        
        mock_sms_service_imports.send_verification_code.return_value = {
            'success': True,
            'message': 'Verification code sent successfully',
            'expires_in': 600
        }
        
        response = client.post("/api/v1/auth/sms/send", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "sent successfully" in data["message"]
        assert data["expires_in"] == 600
        
        mock_sms_service_imports.send_verification_code.assert_called_once_with("+1234567890")

    def test_send_sms_verification_invalid_phone(self, client):
        """Test SMS verification with invalid phone number"""
        request_data = {"phone": "invalid_phone"}
        
        response = client.post("/api/v1/auth/sms/send", json=request_data)
        
        assert response.status_code == 422  
        data = response.json()
        assert "detail" in data

    def test_send_sms_verification_service_error(self, client, mock_sms_service_imports):
        """Test SMS verification when service fails"""
        request_data = {"phone": "+1234567890"}
        
        mock_sms_service_imports.send_verification_code.side_effect = Exception("Service unavailable")
        
        response = client.post("/api/v1/auth/sms/send", json=request_data)
        
        assert response.status_code == 500
        data = response.json()
        assert "Failed to send verification code" in data["detail"]

    def test_verify_sms_code_success(self, client, mock_sms_service_imports):
        """Test successful SMS code verification"""
        request_data = {
            "phone": "+1234567890",
            "code": "123456"
        }
        
        mock_sms_service_imports.verify_code.return_value = {
            'success': True,
            'message': 'Phone number successfully verified',
            'expires_at': '2025-07-30T12:00:00Z'
        }
        
        response = client.post("/api/v1/auth/sms/verify", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["verified"] is True
        assert "successfully verified" in data["message"]
        assert data["expires_at"] == '2025-07-30T12:00:00Z'
        
        mock_sms_service_imports.verify_code.assert_called_once_with("+1234567890", "123456")

    def test_verify_sms_code_invalid_code(self, client, mock_sms_service_imports):
        """Test SMS verification with invalid code"""
        request_data = {
            "phone": "+1234567890",
            "code": "980070"
        }
        
        from fastapi import HTTPException
        mock_sms_service_imports.verify_code.side_effect = HTTPException(
            status_code=400, 
            detail="Invalid verification code"
        )
        
        response = client.post("/api/v1/auth/sms/verify", json=request_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "Invalid verification code" in data["detail"]

    def test_verify_sms_code_missing_fields(self, client):
        """Test SMS verification with missing required fields"""
        request_data = {"phone": "+1234567890"}
        
        response = client.post("/api/v1/auth/sms/verify", json=request_data)
        
        assert response.status_code == 422 
        data = response.json()
        assert "detail" in data

    def test_get_sms_verification_status_verified(self, client, mock_sms_service_imports):
        """Test getting SMS verification status for verified phone"""
        phone = "+1234567890"
        
        mock_sms_service_imports.get_verification_status.return_value = {
            'verified': True,
            'message': 'Phone number is verified',
            'expires_at': '2025-07-30T12:00:00Z'
        }
        
        response = client.get(f"/api/v1/auth/sms/status/{phone}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["verified"] is True
        assert "is verified" in data["message"]
        assert data["expires_at"] == '2025-07-30T12:00:00Z'
        
        mock_sms_service_imports.get_verification_status.assert_called_once_with(phone)

    def test_get_sms_verification_status_not_verified(self, client, mock_sms_service_imports):
        """Test getting SMS verification status for unverified phone"""
        phone = "+1234567890"
        
        mock_sms_service_imports.get_verification_status.return_value = {
            'verified': False,
            'message': 'Phone number not verified',
            'expires_at': None
        }
        
        response = client.get(f"/api/v1/auth/sms/status/{phone}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["verified"] is False
        assert "not verified" in data["message"]
        assert data["expires_at"] is None

    def test_get_sms_verification_status_service_error(self, client, mock_sms_service_imports):
        """Test getting SMS verification status when service fails"""
        phone = "+1234567890"
        
        mock_sms_service_imports.get_verification_status.side_effect = Exception("Service error")
        
        response = client.get(f"/api/v1/auth/sms/status/{phone}")
        
        assert response.status_code == 500
        data = response.json()
        assert "Failed to get verification status" in data["detail"]


class TestSMSAPIValidation:
    """Test SMS API request validation"""

    def test_phone_number_validation_formats(self, client, mock_sms_service_imports):
        """Test various phone number format validations"""
        valid_phones = [
            "+1234567890",
            "+44123456789",
            "1234567890"
        ]
        
        for phone in valid_phones:
            request_data = {"phone": phone}
            
            mock_sms_service_imports.send_verification_code.return_value = {
                'success': True, 
                'message': 'Sent', 
                'expires_in': 600
            }
            
            response = client.post("/api/v1/auth/sms/send", json=request_data)
            assert response.status_code == 200, f"Valid phone {phone} should work"
            
            mock_sms_service_imports.send_verification_code.reset_mock()

    def test_phone_number_validation_invalid(self, client):
        """Test invalid phone number format validation"""
        invalid_phones = [
            "abc123",
            "+",
            "123",  
            "+123456789012345678",
            ""
        ]
        
        for phone in invalid_phones:
            request_data = {"phone": phone}
            
            response = client.post("/api/v1/auth/sms/send", json=request_data)
            assert response.status_code == 422, f"Invalid phone {phone} should fail validation"

    def test_verification_code_validation(self, client):
        """Test verification code format validation"""
        request_data = {
            "phone": "+1234567890",
            "code": ""
        }
        
        response = client.post("/api/v1/auth/sms/verify", json=request_data)
        assert response.status_code == 422 


class TestSMSAPIRateLimit:
    """Test SMS API rate limiting and error handling"""

    def test_sms_send_rate_limit(self, client, mock_sms_service_imports):
        """Test SMS send rate limiting"""
        request_data = {"phone": "+1234567890"}
        
        from fastapi import HTTPException
        mock_sms_service_imports.send_verification_code.side_effect = HTTPException(
            status_code=429, 
            detail="Please wait before requesting another verification code"
        )
        
        response = client.post("/api/v1/auth/sms/send", json=request_data)
        
        assert response.status_code == 429
        data = response.json()
        assert "wait before requesting" in data["detail"]

    def test_sms_verify_attempts_limit(self, client, mock_sms_service_imports):
        """Test SMS verification attempts limit"""
        request_data = {
            "phone": "+1234567890",
            "code": "898979"
        }
        
        from fastapi import HTTPException
        mock_sms_service_imports.verify_code.side_effect = HTTPException(
            status_code=400,
            detail="Too many failed attempts. Please request a new verification code."
        )
        
        response = client.post("/api/v1/auth/sms/verify", json=request_data)
        assert response.status_code == 400
        data = response.json()
        assert "Too many failed attempts" in data["detail"]
