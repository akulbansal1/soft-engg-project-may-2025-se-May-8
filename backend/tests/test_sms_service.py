"""
Tests for SMS verification service
"""
import pytest
import json
import os
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from src.services.sms_service import SMSService
from src.core.config import settings
from fastapi import HTTPException

@pytest.fixture(autouse=True)
def enable_sms_verification():
    """Enable SMS verification for SMS service tests"""
    original_value = os.environ.get("SMS_VERIFICATION_ENABLED")
    os.environ["SMS_VERIFICATION_ENABLED"] = "True"
    
    # Force reload of settings to pick up the new environment variable
    from src.core.config import Settings
    global settings
    settings = Settings()
    
    yield
    
    # Restore original value
    if original_value is not None:
        os.environ["SMS_VERIFICATION_ENABLED"] = original_value
    else:
        os.environ.pop("SMS_VERIFICATION_ENABLED", None)

class TestSMSService:
    """Test SMS verification service"""

    def setup_method(self):
        """Setup for each test method"""
        # Mock Twilio configuration
        self.original_twilio_sid = settings.TWILIO_ACCOUNT_SID
        self.original_twilio_token = settings.TWILIO_AUTH_TOKEN
        self.original_twilio_phone = settings.TWILIO_PHONE_NUMBER
        
        settings.TWILIO_ACCOUNT_SID = "test_account_sid"
        settings.TWILIO_AUTH_TOKEN = "test_auth_token"
        settings.TWILIO_PHONE_NUMBER = "+1234567890"

    def teardown_method(self):
        """Cleanup after each test method"""
        # Restore original settings
        settings.TWILIO_ACCOUNT_SID = self.original_twilio_sid
        settings.TWILIO_AUTH_TOKEN = self.original_twilio_token
        settings.TWILIO_PHONE_NUMBER = self.original_twilio_phone

    @patch('src.services.sms_service.Client')
    @patch('src.utils.cache.Cache.get')
    @patch('src.utils.cache.Cache.set')
    def test_send_verification_code_success(self, mock_cache_set, mock_cache_get, mock_twilio_client):
        """Test successful SMS verification code sending"""
        # Mock cache to show no existing code
        mock_cache_get.return_value = None
        
        # Mock Twilio client
        mock_client_instance = MagicMock()
        mock_message = MagicMock()
        mock_message.sid = "test_message_sid"
        mock_client_instance.messages.create.return_value = mock_message
        mock_twilio_client.return_value = mock_client_instance
        
        # Create SMS service instance
        sms_service = SMSService()
        
        # Test sending verification code
        result = sms_service.send_verification_code("+1234567890")
        
        # Assertions
        assert result['success'] is True
        assert "sent successfully" in result['message']
        assert result['expires_in'] == settings.SMS_VERIFICATION_EXPIRY
        
        # Verify Twilio was called
        mock_client_instance.messages.create.assert_called_once()
        
        # Verify cache was set
        mock_cache_set.assert_called_once()

    @patch('src.services.sms_service.Client')
    @patch('src.utils.cache.Cache.get')
    def test_send_verification_code_rate_limit(self, mock_cache_get, mock_twilio_client):
        """Test rate limiting for SMS verification codes"""
        # Mock cache to show recent code was sent
        recent_time = datetime.now() - timedelta(seconds=30)  # 30 seconds ago
        existing_data = {
            'code': '123456',
            'sent_at': recent_time.isoformat(),
            'attempts': 0
        }
        mock_cache_get.return_value = json.dumps(existing_data)
        
        # Mock Twilio client
        mock_twilio_client.return_value = MagicMock()
        
        # Create SMS service instance
        sms_service = SMSService()
        
        # Test rate limiting
        with pytest.raises(HTTPException) as exc_info:
            sms_service.send_verification_code("+1234567890")
        
        assert exc_info.value.status_code == 429
        assert "wait before requesting" in str(exc_info.value.detail)

    @patch('src.utils.cache.Cache.get')
    @patch('src.utils.cache.Cache.set')
    @patch('src.utils.cache.Cache.delete')
    def test_verify_code_success(self, mock_cache_delete, mock_cache_set, mock_cache_get):
        """Test successful code verification"""
        # Mock cache to return valid verification data
        verification_data = {
            'code': '123456',
            'phone': '+1234567890',
            'sent_at': datetime.now().isoformat(),
            'attempts': 0
        }
        mock_cache_get.return_value = json.dumps(verification_data)
        
        # Create SMS service instance with mocked Twilio
        with patch('src.services.sms_service.Client'):
            sms_service = SMSService()
        
        # Test code verification
        result = sms_service.verify_code("+1234567890", "123456")
        
        # Assertions
        assert result['success'] is True
        assert "successfully verified" in result['message']
        assert 'expires_at' in result
        
        # Verify cache operations
        mock_cache_set.assert_called()  # Setting verified status
        mock_cache_delete.assert_called()  # Deleting verification code

    @patch('src.utils.cache.Cache.get')
    @patch('src.utils.cache.Cache.set')
    def test_verify_code_invalid(self, mock_cache_set, mock_cache_get):
        """Test verification with invalid code"""
        # Mock cache to return valid verification data
        verification_data = {
            'code': '123456',
            'phone': '+1234567890',
            'sent_at': datetime.now().isoformat(),
            'attempts': 0
        }
        mock_cache_get.return_value = json.dumps(verification_data)
        
        # Create SMS service instance with mocked Twilio
        with patch('src.services.sms_service.Client'):
            sms_service = SMSService()
        
        # Test invalid code verification
        with pytest.raises(HTTPException) as exc_info:
            sms_service.verify_code("+1234567890", "654321")
        
        assert exc_info.value.status_code == 400
        assert "Invalid verification code" in str(exc_info.value.detail)
        
        # Verify attempt counter was updated
        mock_cache_set.assert_called()

    @patch('src.utils.cache.Cache.get')
    def test_verify_code_expired(self, mock_cache_get):
        """Test verification with expired code"""
        # Mock cache to return None (expired)
        mock_cache_get.return_value = None
        
        # Create SMS service instance with mocked Twilio
        with patch('src.services.sms_service.Client'):
            sms_service = SMSService()
        
        # Test expired code verification
        with pytest.raises(HTTPException) as exc_info:
            sms_service.verify_code("+1234567890", "123456")
        
        assert exc_info.value.status_code == 400
        assert "expired or not found" in str(exc_info.value.detail)

    @patch('src.utils.cache.Cache.get')
    def test_is_phone_verified_true(self, mock_cache_get):
        """Test checking verified phone status - verified"""
        # Mock cache to return valid verified status
        future_time = datetime.now() + timedelta(hours=1)
        verified_data = {
            'phone': '+1234567890',
            'verified_at': datetime.now().isoformat(),
            'expires_at': future_time.isoformat()
        }
        mock_cache_get.return_value = json.dumps(verified_data)
        
        # Create SMS service instance with mocked Twilio
        with patch('src.services.sms_service.Client'):
            sms_service = SMSService()
        
        # Test phone verification status
        result = sms_service.is_phone_verified("+1234567890")
        
        assert result is True

    @patch('src.utils.cache.Cache.get')
    def test_is_phone_verified_false(self, mock_cache_get):
        """Test checking verified phone status - not verified"""
        # Mock cache to return None
        mock_cache_get.return_value = None
        
        # Create SMS service instance with mocked Twilio
        with patch('src.services.sms_service.Client'):
            sms_service = SMSService()
        
        # Test phone verification status
        result = sms_service.is_phone_verified("+1234567890")
        
        assert result is False

    @patch('src.utils.cache.Cache.get')
    @patch('src.utils.cache.Cache.delete')
    def test_is_phone_verified_expired(self, mock_cache_delete, mock_cache_get):
        """Test checking verified phone status - expired"""
        # Mock cache to return expired verified status
        past_time = datetime.now() - timedelta(hours=1)
        verified_data = {
            'phone': '+1234567890',
            'verified_at': datetime.now().isoformat(),
            'expires_at': past_time.isoformat()
        }
        mock_cache_get.return_value = json.dumps(verified_data)
        
        # Create SMS service instance with mocked Twilio
        with patch('src.services.sms_service.Client'):
            sms_service = SMSService()
        
        # Test phone verification status
        result = sms_service.is_phone_verified("+1234567890")
        
        assert result is False
        # Verify expired status was cleaned up
        mock_cache_delete.assert_called()

    def test_sms_service_initialization_missing_config(self):
        """Test SMS service initialization with missing Twilio configuration"""
        # Use patch to mock missing settings at the SMS service level
        with patch('src.services.sms_service.settings') as mock_settings:
            mock_settings.TWILIO_ACCOUNT_SID = None
            mock_settings.TWILIO_AUTH_TOKEN = None  
            mock_settings.TWILIO_PHONE_NUMBER = None
            
            # Test initialization failure
            with pytest.raises(ValueError) as exc_info:
                SMSService()
            
            assert "Twilio credentials not properly configured" in str(exc_info.value)
