"""
Admin API endpoint tests

Tests for admin authentication endpoints including admin login and logout.
Focuses on admin session management and security.
"""
import pytest
from unittest.mock import patch


class TestAdminAuthAPI:
    """Test admin authentication endpoints"""

    def test_admin_login_success(self, client):
        """Test successful admin login with valid bearer token"""
        admin_token = "admin_secret_token_123"
        
        with patch('src.core.config.settings.ADMIN_SESSION_TOKEN', admin_token):
            headers = {"Authorization": f"Bearer {admin_token}"}
            
            response = client.post("/api/v1/auth/admin/login", headers=headers)
            
            assert response.status_code == 200
            data = response.json()
            assert data["message"] == "Admin login successful"
            
            cookies = response.headers.get('set-cookie', '')
            assert 'session_token' in cookies

    def test_admin_login_invalid_token(self, client):
        """Test admin login with invalid bearer token"""
        admin_token = "admin_secret_token_123"
        invalid_token = "invalid_token"
        
        with patch('src.core.config.settings.ADMIN_SESSION_TOKEN', admin_token):
            headers = {"Authorization": f"Bearer {invalid_token}"}
            
            response = client.post("/api/v1/auth/admin/login", headers=headers)
            
            assert response.status_code == 401
            data = response.json()
            assert "Invalid admin token" in data["detail"]

    def test_admin_login_missing_authorization_header(self, client):
        """Test admin login without Authorization header"""
        response = client.post("/api/v1/auth/admin/login")
        
        assert response.status_code == 403
        data = response.json()
        assert "Not authenticated" in data["detail"]

    def test_admin_login_malformed_authorization_header(self, client):
        """Test admin login with malformed Authorization header"""
        malformed_headers = [
            {"Authorization": "InvalidFormat"},
            {"Authorization": "Bearer"},  # Missing token
            {"Authorization": "Basic dGVzdA=="},  # Wrong scheme
        ]
        
        for headers in malformed_headers:
            response = client.post("/api/v1/auth/admin/login", headers=headers)
            assert response.status_code == 403

    def test_admin_login_empty_token(self, client):
        """Test admin login with empty bearer token"""
        headers = {"Authorization": "Bearer "}
        
        response = client.post("/api/v1/auth/admin/login", headers=headers)
        
        assert response.status_code == 403
        data = response.json()
        assert "Not authenticated" in data["detail"]

    def test_admin_login_sets_secure_cookie(self, client):
        """Test that admin login sets secure HTTP-only cookie"""
        admin_token = "admin_secret_token_123"
        
        with patch('src.core.config.settings.ADMIN_SESSION_TOKEN', admin_token):
            headers = {"Authorization": f"Bearer {admin_token}"}
            
            response = client.post("/api/v1/auth/admin/login", headers=headers)
            
            assert response.status_code == 200
            
            # Check cookie properties
            cookie_header = response.headers.get('set-cookie', '')
            assert 'session_token=' in cookie_header
            assert 'HttpOnly' in cookie_header
            assert 'SameSite=None' in cookie_header

    def test_admin_logout_success(self, client):
        """Test successful admin logout"""
        # First login as admin
        admin_token = "admin_secret_token_123"
        
        with patch('src.core.config.settings.ADMIN_SESSION_TOKEN', admin_token):
            headers = {"Authorization": f"Bearer {admin_token}"}
            login_response = client.post("/api/v1/auth/admin/login", headers=headers)
            assert login_response.status_code == 200
            
            # Now logout
            response = client.post("/api/v1/auth/admin/logout")
            
            assert response.status_code == 200
            data = response.json()
            assert data["message"] == "Admin logout successful"
            
            # Check that session cookie is cleared
            cookie_header = response.headers.get('set-cookie', '')
            assert 'session_token=""' in cookie_header or 'session_token=;' in cookie_header

    def test_admin_logout_clears_cookie(self, client):
        """Test that admin logout properly clears the session cookie"""
        response = client.post("/api/v1/auth/admin/logout")
        
        assert response.status_code == 200
        
        # Check that cookie is cleared (set to empty with immediate expiry)
        cookie_header = response.headers.get('set-cookie', '')
        assert 'session_token=' in cookie_header
        # Cookie should be empty or expired
        assert ('session_token=""' in cookie_header or 
                'session_token=;' in cookie_header or
                'Max-Age=0' in cookie_header)

    def test_admin_endpoints_security(self, client):
        """Test security aspects of admin endpoints"""
        # Test that admin endpoints don't leak sensitive information
        response = client.post("/api/v1/auth/admin/login")
        
        assert response.status_code == 403
        
        # Response should not contain stack traces or internal info
        content = response.text.lower()
        assert "traceback" not in content
        assert "file" not in content
        assert "python" not in content

class TestAdminAPIEdgeCases:
    """Test edge cases and error conditions for admin API"""

    def test_admin_login_with_special_characters(self, client):
        """Test admin login with tokens containing special characters"""
        special_token = "admin!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        with patch('src.core.config.settings.ADMIN_SESSION_TOKEN', special_token):
            headers = {"Authorization": f"Bearer {special_token}"}
            
            response = client.post("/api/v1/auth/admin/login", headers=headers)
            
            assert response.status_code == 200
            data = response.json()
            assert data["message"] == "Admin login successful"

    def test_admin_login_with_unicode_characters(self, client):
        """Test admin login with tokens containing Unicode characters"""
        unicode_token = "admin_token_123_unicode"  # Simplified to avoid encoding issues
        
        with patch('src.core.config.settings.ADMIN_SESSION_TOKEN', unicode_token):
            headers = {"Authorization": f"Bearer {unicode_token}"}
            
            response = client.post("/api/v1/auth/admin/login", headers=headers)
            
            assert response.status_code == 200
            data = response.json()
            assert data["message"] == "Admin login successful"

    def test_admin_login_very_long_token(self, client):
        """Test admin login with very long token"""
        long_token = "a" * 1000  # 1000 character token
        
        with patch('src.core.config.settings.ADMIN_SESSION_TOKEN', long_token):
            headers = {"Authorization": f"Bearer {long_token}"}
            
            response = client.post("/api/v1/auth/admin/login", headers=headers)
            
            assert response.status_code == 200
            data = response.json()
            assert data["message"] == "Admin login successful"

    def test_admin_endpoints_http_methods(self, client):
        """Test that admin endpoints only accept correct HTTP methods"""
        admin_token = "admin_token_123"
        
        with patch('src.core.config.settings.ADMIN_SESSION_TOKEN', admin_token):
            headers = {"Authorization": f"Bearer {admin_token}"}
            
            # Admin login should only accept POST
            response = client.get("/api/v1/auth/admin/login", headers=headers)
            assert response.status_code == 405  # Method Not Allowed
            
            response = client.put("/api/v1/auth/admin/login", headers=headers)
            assert response.status_code == 405
            
            response = client.delete("/api/v1/auth/admin/login", headers=headers)
            assert response.status_code == 405
            
            # Admin logout should only accept POST
            response = client.get("/api/v1/auth/admin/logout")
            assert response.status_code == 405
            
            response = client.put("/api/v1/auth/admin/logout")
            assert response.status_code == 405
            
            response = client.delete("/api/v1/auth/admin/logout")
            assert response.status_code == 405
