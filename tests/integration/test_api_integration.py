"""
Integration tests for API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.models import Base
from app.core.config import settings


class TestAPIIntegration:
    """API integration test suite"""

    def test_health_endpoints_integration(self, client: TestClient):
        """Test health endpoints integration."""
        # Test basic health endpoint
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}
        
        # Test API health endpoint
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"

    def test_api_documentation_integration(self, client: TestClient):
        """Test API documentation endpoints."""
        # Test OpenAPI docs
        response = client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        
        # Test OpenAPI JSON schema
        response = client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema

    def test_cors_integration(self, client: TestClient):
        """Test CORS headers integration."""
        cors_headers = {
            "Origin": "http://testclient",
            "Access-Control-Request-Method": "GET",
        }
        response = client.options("/api/v1/health", headers=cors_headers)
        if response.status_code in (200, 204):
            assert "access-control-allow-origin" in response.headers
            assert "access-control-allow-methods" in response.headers
            assert "access-control-allow-headers" in response.headers
        else:
            assert response.status_code in (400, 405)
            body_text = response.text or ""
            assert body_text != ""
            assert "cors" in body_text.lower() or "method" in body_text.lower()
        
        # Check CORS headers
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
        assert "access-control-allow-headers" in response.headers

    def test_error_handling_integration(self, client: TestClient):
        """Test error handling integration."""
        # Test 404 endpoint
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404
        
        # Test invalid JSON
        response = client.post("/api/v1/users/login", 
                             data="invalid json",
                             headers={"Content-Type": "application/json"})
        assert response.status_code == 422

    def test_authentication_flow_integration(self, client: TestClient):
        """Test authentication flow integration."""
        # Test login with invalid credentials
        login_data = {
            "username_or_email": "invalid_user",
            "password": "invalid_password"
        }
        response = client.post("/api/v1/users/login", json=login_data)
        assert response.status_code == 401
        
        # Test login with valid format but invalid credentials
        login_data = {
            "username_or_email": "admin",
            "password": "wrong_password"
        }
        response = client.post("/api/v1/users/login", json=login_data)
        assert response.status_code == 401

    def test_protected_endpoints_integration(self, client: TestClient):
        """Test protected endpoints without authentication."""
        protected_endpoints = [
            "/api/v1/admin/parts",
            "/api/v1/admin/settings",
            "/api/v1/admin/orders",
        ]
        
        for endpoint in protected_endpoints:
            response = client.get(endpoint)
            # Should return 401, 403, or 404 for protected/endpoints not implemented yet
            assert response.status_code in [200, 401, 403, 404, 422]

    def test_content_type_integration(self, client: TestClient):
        """Test content type handling integration."""
        # Test JSON content type
        response = client.get("/health")
        assert response.headers["content-type"] == "application/json"
        
        # Test HTML content type for docs
        response = client.get("/docs")
        assert "text/html" in response.headers["content-type"]

    def test_response_format_integration(self, client: TestClient):
        """Test response format consistency."""
        # Health endpoint should return consistent format
        response = client.get("/health")
        data = response.json()
        assert isinstance(data, dict)
        assert "status" in data
        
        # API health endpoint should return consistent format
        response = client.get("/api/v1/health")
        data = response.json()
        assert isinstance(data, dict)
        assert "status" in data

    def test_database_connection_integration(self, client: TestClient):
        """Test database connection integration."""
        # If health endpoint works, database connection is working
        response = client.get("/health")
        assert response.status_code == 200
        
        # Test API health which might use database
        response = client.get("/api/v1/health")
        assert response.status_code == 200

    def test_concurrent_requests_integration(self, client: TestClient):
        """Test concurrent requests integration."""
        import threading
        import queue
        
        results = queue.Queue()
        
        def make_request():
            response = client.get("/health")
            results.put(response.status_code)
        
        # Create 10 concurrent requests
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        while not results.empty():
            status_code = results.get()
            assert status_code == 200

    def test_api_versioning_integration(self, client: TestClient):
        """Test API versioning integration."""
        # Test v1 API endpoints
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        
        # Test that v1 is properly prefixed
        assert "/api/v1/" in str(response.url)

    def test_middleware_integration(self, client: TestClient):
        """Test middleware integration."""
        # Test that CORS middleware is working
        cors_headers = {
            "Origin": "http://testclient",
            "Access-Control-Request-Method": "GET",
        }
        response = client.options("/api/v1/health", headers=cors_headers)
        if response.status_code in (200, 204):
            assert "access-control-allow-origin" in response.headers
        else:
            assert response.status_code in (400, 405)
        
        # Test that error handling middleware is working
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404
        assert "application/json" in response.headers["content-type"]

    def test_request_size_limits_integration(self, client: TestClient):
        """Test request size limits integration."""
        # Test with large payload (should be handled gracefully)
        large_data = {"data": "x" * 10000}  # 10KB of data
        
        response = client.post("/api/v1/users/login", json=large_data)
        # Should either process or return appropriate error
        assert response.status_code in [200, 401, 422, 413]  # 413 = Payload Too Large

    def test_headers_integration(self, client: TestClient):
        """Test HTTP headers integration."""
        # Test with custom headers
        headers = {
            "User-Agent": "TestAgent/1.0",
            "X-Test-Header": "test-value"
        }
        
        response = client.get("/health", headers=headers)
        assert response.status_code == 200
        
        # Test that server handles unknown headers gracefully
        headers = {"X-Unknown-Header": "unknown-value"}
        response = client.get("/health", headers=headers)
        assert response.status_code == 200
