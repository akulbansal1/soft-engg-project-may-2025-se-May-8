import random
import string
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from twilio.rest import Client
from twilio.base.exceptions import TwilioException
from fastapi import HTTPException, status

from src.core.config import settings
from src.utils.cache import Cache

class SMSService:
    """Service for SMS verification functionality using Twilio"""
    
    def __init__(self):
        """Initialize Twilio client"""
        if not all([settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN, settings.TWILIO_PHONE_NUMBER]):
            raise ValueError("Twilio credentials not properly configured. Please set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_PHONE_NUMBER")
        
        self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        self.from_phone = settings.TWILIO_PHONE_NUMBER
    
    @staticmethod
    def _generate_verification_code() -> str:
        """Generate a random verification code"""
        return ''.join(random.choices(string.digits, k=settings.SMS_VERIFICATION_CODE_LENGTH))
    
    @staticmethod
    def _get_verification_cache_key(phone: str) -> str:
        """Get cache key for verification code"""
        return f"sms_verification_code_{phone}"
    
    @staticmethod
    def _get_verified_status_cache_key(phone: str) -> str:
        """Get cache key for verified status"""
        return f"sms_verified_status_{phone}"
    
    def send_verification_code(self, phone: str) -> Dict[str, Any]:
        """
        Send SMS verification code to the given phone number
        
        Args:
            phone: Phone number to send verification code to
            
        Returns:
            Dict containing success status and message
            
        Raises:
            HTTPException: If SMS sending fails
        """
        try:
            cache_key = self._get_verification_cache_key(phone)
            existing_code_data = Cache.get(cache_key)
            
            if existing_code_data:
                existing_data = json.loads(existing_code_data)
                sent_at = datetime.fromisoformat(existing_data['sent_at'])
                if datetime.now() - sent_at < timedelta(minutes=1):
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail="Please wait before requesting another verification code"
                    )
            
            verification_code = self._generate_verification_code()
            
            message_body = f"Your verification code is: {verification_code}. This code will expire in 10 minutes."
            
            message = self.client.messages.create(
                body=message_body,
                from_=f"whatsapp:{self.from_phone}",
                to=f"whatsapp:{phone}"
            )
            
            verification_data = {
                'code': verification_code,
                'phone': phone,
                'sent_at': datetime.now().isoformat(),
                'attempts': 0,
                'message_sid': message.sid
            }
            
            Cache.set(
                cache_key,
                json.dumps(verification_data),
                expiry=settings.SMS_VERIFICATION_EXPIRY
            )
            
            return {
                'success': True,
                'message': 'Verification code sent successfully',
                'expires_in': settings.SMS_VERIFICATION_EXPIRY
            }
            
        except HTTPException:
            raise
        except TwilioException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to send WhatsApp message: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unexpected error sending WhatsApp message: {str(e)}"
            )
    
    def verify_code(self, phone: str, code: str) -> Dict[str, Any]:
        """
        Verify the SMS code for the given phone number
        
        Args:
            phone: Phone number that received the code
            code: Verification code to verify
            
        Returns:
            Dict containing verification status and message
            
        Raises:
            HTTPException: If verification fails
        """
        try:
            cache_key = self._get_verification_cache_key(phone)
            verification_data_json = Cache.get(cache_key)
            
            if not verification_data_json:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Verification code expired or not found. Please request a new code."
                )
            
            verification_data = json.loads(verification_data_json)
            
            if verification_data.get('attempts', 0) >= 3:
                Cache.delete(cache_key)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Too many failed attempts. Please request a new verification code."
                )
            
            if verification_data['code'] != code:
                verification_data['attempts'] = verification_data.get('attempts', 0) + 1
                Cache.set(
                    cache_key,
                    json.dumps(verification_data),
                    expiry=settings.SMS_VERIFICATION_EXPIRY
                )
                
                remaining_attempts = 3 - verification_data['attempts']
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid verification code. {remaining_attempts} attempts remaining."
                )
            
            verified_status = {
                'phone': phone,
                'verified_at': datetime.now().isoformat(),
                'expires_at': (datetime.now() + timedelta(seconds=settings.SMS_VERIFICATION_CACHE_EXPIRY)).isoformat()
            }
            
            verified_cache_key = self._get_verified_status_cache_key(phone)
            Cache.set(
                verified_cache_key,
                json.dumps(verified_status),
                expiry=settings.SMS_VERIFICATION_CACHE_EXPIRY
            )
            
            Cache.delete(cache_key)
            
            return {
                'success': True,
                'message': 'Phone number successfully verified',
                'expires_at': verified_status['expires_at']
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unexpected error during verification: {str(e)}"
            )
    
    def is_phone_verified(self, phone: str) -> bool:
        """
        Check if a phone number is currently verified
        
        Args:
            phone: Phone number to check
            
        Returns:
            Boolean indicating if phone is verified
        """
        try:
            verified_cache_key = self._get_verified_status_cache_key(phone)
            verified_data_json = Cache.get(verified_cache_key)
            
            if not verified_data_json:
                return False
            
            verified_data = json.loads(verified_data_json)
            expires_at = datetime.fromisoformat(verified_data['expires_at'])
            
            if datetime.now() > expires_at:
                Cache.delete(verified_cache_key)
                return False
            
            return True
            
        except Exception:
            return False
    
    def get_verification_status(self, phone: str) -> Dict[str, Any]:
        """
        Get detailed verification status for a phone number
        
        Args:
            phone: Phone number to check
            
        Returns:
            Dict containing verification status details
        """
        try:
            verified_cache_key = self._get_verified_status_cache_key(phone)
            verified_data_json = Cache.get(verified_cache_key)
            
            if not verified_data_json:
                return {
                    'verified': False,
                    'message': 'Phone number not verified',
                    'expires_at': None
                }
            
            verified_data = json.loads(verified_data_json)
            expires_at = datetime.fromisoformat(verified_data['expires_at'])
            
            if datetime.now() > expires_at:
                Cache.delete(verified_cache_key)
                return {
                    'verified': False,
                    'message': 'Phone verification has expired',
                    'expires_at': None
                }
            
            return {
                'verified': True,
                'message': 'Phone number is verified',
                'expires_at': verified_data['expires_at']
            }
            
        except Exception as e:
            return {
                'verified': False,
                'message': f'Error checking verification status: {str(e)}',
                'expires_at': None
            }
    
    def send_emergency_message(self, phone: str, user_name: str = "Someone") -> Dict[str, Any]:
        """
        Send emergency SOS message to a phone number
        
        Args:
            phone: Phone number to send emergency message to
            user_name: Name of the person in emergency (optional)
            
        Returns:
            Dict containing success status and message
            
        Raises:
            HTTPException: If SMS sending fails
        """
        try:
            message_body = f"🚨 EMERGENCY ALERT 🚨\n\n{user_name} has triggered an emergency SOS signal and may need immediate assistance. Please check on them or contact emergency services if necessary.\n\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            message = self.client.messages.create(
                body=message_body,
                from_=f"whatsapp:{self.from_phone}",
                to=f"whatsapp:{phone}"
            )
            
            return {
                'success': True,
                'message': f'Emergency alert sent to {phone}',
                'message_sid': message.sid
            }
            
        except TwilioException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to send emergency WhatsApp message to {phone}: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unexpected error sending emergency WhatsApp message to {phone}: {str(e)}"
            )

# Create a lazy singleton instance
_sms_service_instance = None

def get_sms_service() -> SMSService:
    """Get SMS service instance (lazy initialization)"""
    global _sms_service_instance
    if _sms_service_instance is None:
        _sms_service_instance = SMSService()
    return _sms_service_instance

# Legacy compatibility - use get_sms_service() for new code
def _get_legacy_sms_service():
    """Legacy compatibility function"""
    return get_sms_service()

# For backward compatibility with existing imports
class _SMSServiceProxy:
    """Proxy class for backward compatibility"""
    def __getattr__(self, name):
        return getattr(get_sms_service(), name)

sms_service = _SMSServiceProxy()
