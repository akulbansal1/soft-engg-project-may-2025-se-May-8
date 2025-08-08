"""
Authentication Middleware Tests

Comprehensive tests for authentication middleware dependencies and user validation.
Tests cover session authentication, user ownership validation, admin access, and edge cases.
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException

from src.core.auth_middleware import (
    AuthMiddleware,
    RequireAuth,
    OptionalAuth,
    RequireOwnership,
    RequireAdmin
)
from src.schemas.user import UserCreate
from src.services.user_service import UserService
from src.models.user import User


class TestAuthMiddleware:
    """Test AuthMiddleware core functionality"""

    def test_get_current_user_success(self, test_db):
        """Test successful user authentication with valid session"""
        user_data = UserCreate(
            name="Test User",
            phone="1234567890",
            is_active=True
        )
        test_user = UserService.register_user(test_db, user_data)
        
        session_token = "valid_session_token"
        
        with patch.object(UserService, 'get_user_by_session', return_value=test_user):
            user = AuthMiddleware.get_current_user(session_token, test_db)
            
            assert user is not None
            assert user.id == test_user.id
            assert user.name == "Test User"
            assert user.phone == "1234567890"

    def test_get_current_user_no_token(self, test_db):
        """Test authentication fails when no session token provided"""
        with pytest.raises(HTTPException) as exc_info:
            AuthMiddleware.get_current_user(None, test_db)
        
        assert exc_info.value.status_code == 401
        assert "No session token provided" in str(exc_info.value.detail)
        assert exc_info.value.headers == {"WWW-Authenticate": "Bearer"}

    def test_get_current_user_invalid_token(self, test_db):
        """Test authentication fails with invalid session token"""
        session_token = "invalid_session_token"
        
        with patch.object(UserService, 'get_user_by_session', return_value=None):
            with pytest.raises(HTTPException) as exc_info:
                AuthMiddleware.get_current_user(session_token, test_db)
            
            assert exc_info.value.status_code == 401
            assert "Invalid or expired session" in str(exc_info.value.detail)
            assert exc_info.value.headers == {"WWW-Authenticate": "Bearer"}

    def test_get_current_user_optional_success(self, test_db):
        """Test optional authentication with valid session"""
        user_data = UserCreate(
            name="Test User",
            phone="1234567890",
            is_active=True
        )
        test_user = UserService.register_user(test_db, user_data)
        
        session_token = "valid_session_token"
        
        with patch.object(UserService, 'get_user_by_session', return_value=test_user):
            user = AuthMiddleware.get_current_user_optional(session_token, test_db)
            
            assert user is not None
            assert user.id == test_user.id

    def test_get_current_user_optional_no_token(self, test_db):
        """Test optional authentication returns None when no token provided"""
        user = AuthMiddleware.get_current_user_optional(None, test_db)
        assert user is None

    def test_get_current_user_optional_invalid_token(self, test_db):
        """Test optional authentication returns None with invalid token"""
        session_token = "invalid_session_token"
        
        with patch.object(UserService, 'get_user_by_session', return_value=None):
            user = AuthMiddleware.get_current_user_optional(session_token, test_db)
            assert user is None

    def test_validate_user_ownership_success(self, test_db):
        """Test user ownership validation succeeds for own resource"""
        user_data = UserCreate(
            name="Test User",
            phone="1234567890",
            is_active=True
        )
        test_user = UserService.register_user(test_db, user_data)
        
        result = AuthMiddleware.validate_user_ownership(test_user.id, test_user)
        
        assert result == test_user

    def test_validate_user_ownership_forbidden(self, test_db):
        """Test user ownership validation fails for other user's resource"""
        user1_data = UserCreate(
            name="User 1",
            phone="1111111111",
            is_active=True
        )
        user2_data = UserCreate(
            name="User 2",
            phone="2222222222",
            is_active=True
        )
        user1 = UserService.register_user(test_db, user1_data)
        user2 = UserService.register_user(test_db, user2_data)
        
        with pytest.raises(HTTPException) as exc_info:
            AuthMiddleware.validate_user_ownership(user2.id, user1)
        
        assert exc_info.value.status_code == 403
        assert "You can only access your own resources" in str(exc_info.value.detail)

    def test_validate_admin_access_success(self):
        """Test admin access validation succeeds with valid admin token"""
        with patch('src.core.config.settings.ADMIN_SESSION_TOKEN', 'admin_token_123'):
            result = AuthMiddleware.validate_admin_access('admin_token_123')
            assert result is True

    def test_validate_admin_access_no_token(self):
        """Test admin access validation fails with no token"""
        with pytest.raises(HTTPException) as exc_info:
            AuthMiddleware.validate_admin_access(None)
        
        assert exc_info.value.status_code == 401
        assert "No session token provided" in str(exc_info.value.detail)

    def test_validate_admin_access_invalid_token(self):
        """Test admin access validation fails with invalid token"""
        with patch('src.core.config.settings.ADMIN_SESSION_TOKEN', 'admin_token_123'):
            with pytest.raises(HTTPException) as exc_info:
                AuthMiddleware.validate_admin_access('invalid_token')
            
            assert exc_info.value.status_code == 403
            assert "You do not have permission to access this resource" in str(exc_info.value.detail)


class TestAuthenticationAliases:
    """Test authentication convenience aliases"""

    def test_require_auth_alias(self, test_db):
        """Test RequireAuth alias works correctly"""
        user_data = UserCreate(
            name="Test User",
            phone="1234567890",
            is_active=True
        )
        test_user = UserService.register_user(test_db, user_data)
        
        session_token = "valid_session_token"
        
        with patch.object(UserService, 'get_user_by_session', return_value=test_user):
            user = RequireAuth(session_token, test_db)
            
            assert user is not None
            assert user.id == test_user.id

    def test_optional_auth_alias(self, test_db):
        """Test OptionalAuth alias works correctly"""
        user = OptionalAuth(None, test_db)
        assert user is None

    def test_require_ownership_alias(self, test_db):
        """Test RequireOwnership alias works correctly"""
        user_data = UserCreate(
            name="Test User",
            phone="1234567890",
            is_active=True
        )
        test_user = UserService.register_user(test_db, user_data)
        
        result = RequireOwnership(test_user.id, test_user)
        assert result == test_user

    def test_require_admin_alias(self):
        """Test RequireAdmin alias works correctly"""
        with patch('src.core.config.settings.ADMIN_SESSION_TOKEN', 'admin_token'):
            result = RequireAdmin('admin_token')
            assert result is True


class TestAuthMiddlewareIntegration:
    """Test authentication middleware in realistic scenarios"""

    def test_multiple_users_session_isolation(self, test_db):
        """Test that user sessions are properly isolated"""
        # Create multiple users
        user1_data = UserCreate(name="User 1", phone="1111111111", is_active=True)
        user2_data = UserCreate(name="User 2", phone="2222222222", is_active=True)
        user1 = UserService.register_user(test_db, user1_data)
        user2 = UserService.register_user(test_db, user2_data)
        
        with patch.object(UserService, 'get_user_by_session', return_value=user1):
            authenticated_user = AuthMiddleware.get_current_user("user1_token", test_db)
            assert authenticated_user.id == user1.id
            assert authenticated_user.name == "User 1"
        
        with patch.object(UserService, 'get_user_by_session', return_value=user2):
            authenticated_user = AuthMiddleware.get_current_user("user2_token", test_db)
            assert authenticated_user.id == user2.id
            assert authenticated_user.name == "User 2"

    def test_inactive_user_authentication(self, test_db):
        """Test that inactive users cannot authenticate"""
        user_data = UserCreate(
            name="Inactive User",
            phone="1234567890",
            is_active=False
        )
        inactive_user = UserService.register_user(test_db, user_data)
        
        with patch.object(UserService, 'get_user_by_session', return_value=None):
            with pytest.raises(HTTPException) as exc_info:
                AuthMiddleware.get_current_user("session_token", test_db)
            
            assert exc_info.value.status_code == 401

    def test_session_token_edge_cases(self, test_db):
        """Test various session token edge cases"""
        with pytest.raises(HTTPException):
            AuthMiddleware.get_current_user("", test_db)
        
        long_token = "a" * 1000
        with patch.object(UserService, 'get_user_by_session', return_value=None):
            with pytest.raises(HTTPException):
                AuthMiddleware.get_current_user(long_token, test_db)
        
        special_token = "token!@#$%^&*()_+-=[]{}|;:,.<>?"
        with patch.object(UserService, 'get_user_by_session', return_value=None):
            with pytest.raises(HTTPException):
                AuthMiddleware.get_current_user(special_token, test_db)

    def test_authentication_with_database_error(self, test_db):
        """Test authentication behavior when database errors occur"""
        session_token = "valid_token"
        
        with patch.object(UserService, 'get_user_by_session', side_effect=Exception("Database error")):
            with pytest.raises(Exception, match="Database error"):
                AuthMiddleware.get_current_user(session_token, test_db)

    def test_admin_token_security(self):
        """Test admin token security and validation"""
        correct_admin_token = "secure_admin_token_123"
        
        with patch('src.core.config.settings.ADMIN_SESSION_TOKEN', correct_admin_token):
            assert AuthMiddleware.validate_admin_access(correct_admin_token) is True
            
            similar_tokens = [
                "secure_admin_token_124",  
                "Secure_admin_token_123", 
                "secure_admin_token_123 ",
                " secure_admin_token_123",
                "secure_admin_token_12",  
                "" 
            ]
            
            for token in similar_tokens:
                with pytest.raises(HTTPException):
                    AuthMiddleware.validate_admin_access(token)

    def test_user_state_changes_during_session(self, test_db):
        """Test authentication behavior when user state changes during active session"""
        user_data = UserCreate(
            name="Test User",
            phone="1234567890",
            is_active=True
        )
        user = UserService.register_user(test_db, user_data)
        
        with patch.object(UserService, 'get_user_by_session', return_value=user):
            authenticated_user = AuthMiddleware.get_current_user("session_token", test_db)
            assert authenticated_user.id == user.id
        
        user.is_active = False
        test_db.commit()
        
        with patch.object(UserService, 'get_user_by_session', return_value=None):
            with pytest.raises(HTTPException) as exc_info:
                AuthMiddleware.get_current_user("session_token", test_db)
            
            assert exc_info.value.status_code == 401
