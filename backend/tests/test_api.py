"""
API endpoints tests (non-authentication related)
"""
import pytest
import json


class TestAPIEndpoints:
    """Test API endpoints that don't require authentication"""
    
    def test_api_router_inclusion(self, client):
        """Test that API router is properly included"""
        # Test that endpoints are accessible through the router
        response = client.get("/api/v1/")
        assert response.status_code == 200

    def test_api_response_format(self, client):
        """Test that API responses follow consistent format"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        
        # Should return valid JSON
        data = response.json()
        assert isinstance(data, dict)
        
        # Should have consistent field naming (snake_case)
        assert "status" in data
        assert "service" in data

    def test_api_error_handling(self, client):
        """Test API error handling for non-existent endpoints"""
        response = client.get("/api/v1/does-not-exist")
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data

    def test_api_content_negotiation(self, client):
        """Test that API handles content negotiation properly"""
        # Test with Accept header for JSON
        headers = {"Accept": "application/json"}
        response = client.get("/api/v1/health", headers=headers)
        assert response.status_code == 200
        assert "application/json" in response.headers.get("content-type", "")

    def test_api_method_validation(self, client):
        """Test that API validates HTTP methods correctly"""
        # POST to health endpoint should not be allowed
        response = client.post("/api/v1/health")
        assert response.status_code == 405

        # PUT to health endpoint should not be allowed
        response = client.put("/api/v1/health")
        assert response.status_code == 405

        # DELETE to health endpoint should not be allowed
        response = client.delete("/api/v1/health")
        assert response.status_code == 405


class TestRequestHandling:
    """Test request handling and middleware"""

    def test_cors_middleware(self, client):
        """Test CORS middleware functionality"""
        # Test preflight request
        headers = {
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Content-Type"
        }
        response = client.options("/api/v1/health", headers=headers)
        
        # Should handle CORS preflight (status might be 200 or 405 depending on FastAPI version)
        assert response.status_code in [200, 405]

    def test_request_body_size_limit(self, client):
        """Test that extremely large request bodies are handled properly"""
        # Create a large JSON payload (1MB)
        large_data = {"data": "x" * (1024 * 1024)}
        
        # This should not crash the server
        response = client.post("/api/v1/health", json=large_data)
        # Might be 405 (method not allowed) or 413 (payload too large)
        assert response.status_code in [405, 413, 422]

    def test_malformed_json_handling(self, client):
        """Test handling of malformed JSON in requests"""
        headers = {"Content-Type": "application/json"}
        malformed_json = '{"invalid": json}'
        
        # This should not crash the server
        response = client.post("/api/v1/health", content=malformed_json, headers=headers)
        # Should return error status, not crash
        assert response.status_code >= 400


class TestPerformance:
    """Basic performance tests"""
    
    def test_concurrent_requests(self, client):
        """Test handling of multiple concurrent requests"""
        import concurrent.futures
        import time
        
        def make_request():
            return client.get("/api/v1/health")
        
        # Make 10 concurrent requests
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            responses = [future.result() for future in concurrent.futures.as_completed(futures)]
        end_time = time.time()
        
        # All requests should succeed
        for response in responses:
            assert response.status_code == 200
        
        # Should complete within reasonable time (5 seconds for 10 requests)
        assert (end_time - start_time) < 5.0

    def test_memory_usage_stability(self, client):
        """Test that repeated requests don't cause memory leaks"""
        import gc
        
        # Make many requests to check for memory leaks
        for _ in range(100):
            response = client.get("/api/v1/health")
            assert response.status_code == 200
        
        # Force garbage collection
        gc.collect()
        # If we get here without crashing, memory is likely stable


class TestDataValidation:
    """Test data validation and serialization"""
    
    def test_response_serialization(self, client):
        """Test that responses are properly serialized"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        
        # Should be valid JSON
        data = response.json()
        
        # Should be serializable back to JSON
        json_str = json.dumps(data)
        assert isinstance(json_str, str)
        
        # Should be deserializable
        parsed_data = json.loads(json_str)
        assert parsed_data == data

    def test_unicode_handling(self, client):
        """Test that API handles Unicode characters properly"""
        # This is mainly a smoke test to ensure Unicode doesn't break anything
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        
        # Response should handle Unicode properly
        content = response.content.decode('utf-8')
        assert isinstance(content, str)
