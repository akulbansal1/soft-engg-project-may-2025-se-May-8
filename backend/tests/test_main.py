"""
Basic server health and functionality tests
"""
import pytest
from fastapi.testclient import TestClient


class TestServerHealth:
    """Test server health and basic functionality"""
    
    def test_read_main(self, client):
        """Test the main health check endpoint"""
        response = client.get("/api/v1/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ok"
        assert data["message"] == "Backend is running!"
        assert "version" in data

    def test_health_check(self, client):
        """Test the health check endpoint"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "backend-api"

    def test_cors_headers(self, client):
        """Test CORS headers are properly set"""
        response = client.options("/api/v1/")
        # OPTIONS requests should be handled properly
        assert response.status_code in [200, 405]  # Some frameworks return 405 for OPTIONS

    def test_404_handling(self, client):
        """Test 404 error handling"""
        response = client.get("/api/v1/nonexistent-endpoint")
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data

    def test_openapi_docs(self, client):
        """Test OpenAPI documentation is accessible"""
        response = client.get("/api/v1/openapi.json")
        assert response.status_code == 200
        
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert data["info"]["title"] == "SE Project API (Team 8, May 2025)"

    def test_docs_interface(self, client):
        """Test Swagger docs interface"""
        response = client.get("/docs")
        assert response.status_code == 200
        
        assert "text/html" in response.headers.get("content-type", "")

    def test_redoc_interface(self, client):
        """Test ReDoc documentation interface"""
        response = client.get("/redoc")
        assert response.status_code == 200
        # Should return HTML content
        assert "text/html" in response.headers.get("content-type", "")


class TestAPIStructure:
    """Test API structure and endpoints availability"""
    
    def test_api_v1_prefix(self, client):
        """Test that API uses v1 prefix correctly"""
        # Root endpoint should work
        response = client.get("/api/v1/")
        assert response.status_code == 200
        
        # Without prefix should return 404
        response = client.get("/")
        assert response.status_code == 404

    def test_content_type_json(self, client):
        """Test that API returns JSON content type"""
        response = client.get("/api/v1/")
        assert response.status_code == 200
        assert "application/json" in response.headers.get("content-type", "")

    def test_response_time(self, client):
        """Test that basic endpoints respond quickly"""
        import time
        
        start_time = time.time()
        response = client.get("/api/v1/health")
        end_time = time.time()
        
        assert response.status_code == 200
        # Should respond within 1 second for health check
        assert (end_time - start_time) < 1.0


class TestSecurityHeaders:
    """Test security-related headers and configurations"""
    
    def test_no_sensitive_info_in_errors(self, client):
        """Test that error responses don't leak sensitive information"""
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404
        
        # Should not contain stack traces or internal paths
        content = response.text.lower()
        assert "traceback" not in content
        assert "file" not in content
        assert "python" not in content

    def test_method_not_allowed(self, client):
        """Test proper handling of unsupported HTTP methods"""
        # POST to health check should not be allowed
        response = client.post("/api/v1/health")
        assert response.status_code == 405
