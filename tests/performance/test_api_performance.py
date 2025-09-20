"""
Performance tests for API endpoints
"""

import pytest
import time
import statistics
from concurrent.futures import ThreadPoolExecutor
from fastapi.testclient import TestClient


class TestAPIPerformance:
    """API performance test suite"""

    def test_health_endpoint_performance(self, client: TestClient, benchmark):
        """Test health endpoint response time."""
        def health_check():
            response = client.get("/health")
            assert response.status_code == 200
            return response.elapsed.total_seconds()
        
        result = benchmark(health_check)
        assert result < 0.1  # Should respond in less than 100ms

    def test_api_health_performance(self, client: TestClient, benchmark):
        """Test API health endpoint response time."""
        def api_health_check():
            response = client.get("/api/v1/health")
            assert response.status_code == 200
            return response.elapsed.total_seconds()
        
        result = benchmark(api_health_check)
        assert result < 0.2  # Should respond in less than 200ms

    def test_concurrent_requests(self, client: TestClient):
        """Test API performance under concurrent load."""
        def make_request():
            start_time = time.time()
            response = client.get("/health")
            end_time = time.time()
            return {
                'status_code': response.status_code,
                'response_time': end_time - start_time
            }

        # Make 50 concurrent requests
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(50)]
            results = [future.result() for future in futures]

        # Analyze results
        response_times = [r['response_time'] for r in results]
        status_codes = [r['status_code'] for r in results]

        # All requests should succeed
        assert all(code == 200 for code in status_codes)

        # Performance assertions
        avg_response_time = statistics.mean(response_times)
        max_response_time = max(response_times)
        p95_response_time = sorted(response_times)[int(len(response_times) * 0.95)]

        assert avg_response_time < 0.5  # Average response time < 500ms
        assert max_response_time < 1.0  # Max response time < 1s
        assert p95_response_time < 0.8  # 95th percentile < 800ms

    def test_memory_usage(self, client: TestClient):
        """Test API memory usage during requests."""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Make 100 requests
        for _ in range(100):
            response = client.get("/health")
            assert response.status_code == 200

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Memory increase should be reasonable (< 50MB)
        assert memory_increase < 50

    @pytest.mark.parametrize("endpoint", [
        "/health",
        "/api/v1/health",
        "/docs",
        "/api/v1/parts/",
        "/api/v1/categories/",
    ])
    def test_endpoint_performance(self, client: TestClient, endpoint, benchmark):
        """Test individual endpoint performance."""
        def endpoint_test():
            response = client.get(endpoint)
            return response.status_code, response.elapsed.total_seconds()
        
        status_code, response_time = benchmark(endpoint_test)
        
        # Endpoint should respond successfully
        assert status_code in [200, 404]  # 404 is acceptable for some endpoints
        
        # Response time should be reasonable
        assert response_time < 2.0  # All endpoints should respond within 2 seconds
