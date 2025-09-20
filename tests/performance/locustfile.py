"""
Locust load testing configuration for China Car Parts API
"""

from locust import HttpUser, task, between
import json
import random


class APIUser(HttpUser):
    """Simulated user behavior for load testing"""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between requests
    
    def on_start(self):
        """Called when a user starts"""
        self.login()
    
    def login(self):
        """Simulate user login"""
        login_data = {
            "username_or_email": "admin",
            "password": "test_password"  # Use test password
        }
        
        response = self.client.post(
            "/api/v1/users/login",
            json=login_data,
            catch_response=True
        )
        
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
            response.success()
        else:
            response.failure(f"Login failed: {response.status_code}")
            self.token = None
    
    @task(3)
    def health_check(self):
        """Check API health (most frequent)"""
        response = self.client.get("/health")
        if response.status_code != 200:
            response.failure(f"Health check failed: {response.status_code}")
    
    @task(2)
    def api_health_check(self):
        """Check API health endpoint"""
        response = self.client.get("/api/v1/health")
        if response.status_code != 200:
            response.failure(f"API health check failed: {response.status_code}")
    
    @task(2)
    def get_parts(self):
        """Get parts list"""
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        
        response = self.client.get("/api/v1/parts/", headers=headers)
        if response.status_code not in [200, 401]:  # 401 is acceptable if not logged in
            response.failure(f"Get parts failed: {response.status_code}")
    
    @task(2)
    def get_categories(self):
        """Get categories list"""
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        
        response = self.client.get("/api/v1/categories/", headers=headers)
        if response.status_code not in [200, 401]:
            response.failure(f"Get categories failed: {response.status_code}")
    
    @task(1)
    def get_orders(self):
        """Get orders list"""
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        
        response = self.client.get("/api/v1/orders/", headers=headers)
        if response.status_code not in [200, 401]:
            response.failure(f"Get orders failed: {response.status_code}")
    
    @task(1)
    def get_vehicles(self):
        """Get vehicle data"""
        vehicle_types = ["brands", "models", "trims"]
        vehicle_type = random.choice(vehicle_types)
        
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        
        response = self.client.get(f"/api/v1/vehicles/{vehicle_type}", headers=headers)
        if response.status_code not in [200, 401]:
            response.failure(f"Get vehicles failed: {response.status_code}")
    
    @task(1)
    def search_parts(self):
        """Search for parts"""
        search_terms = ["brake", "engine", "filter", "oil", "belt", "spark"]
        search_term = random.choice(search_terms)
        
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        
        response = self.client.get(
            f"/api/v1/search/?q={search_term}&limit=10",
            headers=headers
        )
        if response.status_code not in [200, 401]:
            response.failure(f"Search parts failed: {response.status_code}")
    
    @task(1)
    def get_documentation(self):
        """Access API documentation"""
        response = self.client.get("/docs")
        if response.status_code != 200:
            response.failure(f"Get docs failed: {response.status_code}")


class HeavyUser(APIUser):
    """Heavy user with more intensive operations"""
    
    weight = 1  # Lower weight, fewer heavy users
    
    @task(3)
    def bulk_operations(self):
        """Simulate bulk operations"""
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        
        # Simulate bulk search
        response = self.client.get(
            "/api/v1/search/?q=test&limit=50",
            headers=headers
        )
        if response.status_code not in [200, 401]:
            response.failure(f"Bulk search failed: {response.status_code}")
    
    @task(2)
    def analytics_data(self):
        """Access analytics data"""
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        
        response = self.client.get("/api/v1/analytics/dashboard", headers=headers)
        if response.status_code not in [200, 401]:
            response.failure(f"Analytics failed: {response.status_code}")


# Load test scenarios
class QuickTest(HttpUser):
    """Quick test scenario for CI/CD"""
    wait_time = between(0.1, 0.5)
    
    @task
    def quick_health_check(self):
        response = self.client.get("/health")
        if response.status_code != 200:
            response.failure(f"Quick health check failed: {response.status_code}")


class StressTest(HttpUser):
    """Stress test scenario"""
    wait_time = between(0.01, 0.1)  # Very fast requests
    
    @task
    def rapid_requests(self):
        response = self.client.get("/health")
        if response.status_code != 200:
            response.failure(f"Rapid request failed: {response.status_code}")
