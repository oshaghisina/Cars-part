#!/usr/bin/env python3
"""
Smoke Test for Parts & Inventory Integration (Phase 1)
=====================================================

This script validates the end-to-end integration between:
- Backend API (public read + admin write endpoints)
- Database schema (parts, prices, stock_levels)
- Frontend display (real price/stock data)

Usage:
    python scripts/smoke_test_parts_integration.py [--verbose] [--create-test-data]

Requirements:
    - Backend server running on localhost:8001
    - Web portal running on localhost:5174
    - Admin panel running on localhost:5173
"""

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Add project root to Python path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from app.db.database import engine
from app.services.parts_enhanced_service import PartsEnhancedService
from app.schemas.parts_schemas import PartCreateIn, PriceIn, StockLevelIn
from sqlalchemy.orm import sessionmaker

# Configuration
BACKEND_BASE_URL = "http://localhost:8001"
WEB_PORTAL_URL = "http://localhost:5174"
ADMIN_PANEL_URL = "http://localhost:5173"

# Test data
TEST_PART_DATA = {
    "part_name": "Smoke Test Brake Pad",
    "brand_oem": "TestBrand",
    "vehicle_make": "TestMake",
    "vehicle_model": "TestModel",
    "vehicle_trim": "2023",
    "category": "Brake System",  # Required field
    "oem_code": "SMOKE-TEST-001",
    "status": "active"
}

TEST_PRICE_DATA = {
    "list_price": "450000",
    "sale_price": "400000",
    "currency": "IRR"
}

TEST_STOCK_DATA = {
    "current_stock": 25,
    "reserved_quantity": 5,
    "min_stock_level": 10
}

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

class SmokeTestResult:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.errors = []
        self.start_time = datetime.now()
    
    def add_result(self, test_name: str, success: bool, message: str = "", error: Optional[Exception] = None):
        if success:
            self.passed += 1
            print(f"{Colors.GREEN}✓{Colors.END} {test_name}: {message}")
        else:
            self.failed += 1
            error_msg = str(error) if error else message
            self.errors.append(f"{test_name}: {error_msg}")
            print(f"{Colors.RED}✗{Colors.END} {test_name}: {error_msg}")
    
    def skip(self, test_name: str, reason: str):
        self.skipped += 1
        print(f"{Colors.YELLOW}⊘{Colors.END} {test_name}: {reason}")
    
    def summary(self):
        total = self.passed + self.failed + self.skipped
        duration = datetime.now() - self.start_time
        
        print(f"\n{Colors.BOLD}Smoke Test Summary{Colors.END}")
        print(f"{'='*50}")
        print(f"Total Tests: {total}")
        print(f"{Colors.GREEN}Passed: {self.passed}{Colors.END}")
        print(f"{Colors.RED}Failed: {self.failed}{Colors.END}")
        print(f"{Colors.YELLOW}Skipped: {self.skipped}{Colors.END}")
        print(f"Duration: {duration.total_seconds():.2f}s")
        
        if self.errors:
            print(f"\n{Colors.RED}Errors:{Colors.END}")
            for error in self.errors:
                print(f"  - {error}")
        
        return self.failed == 0

def create_http_session():
    """Create HTTP session with retry strategy."""
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def test_backend_health(session: requests.Session, result: SmokeTestResult):
    """Test backend API health."""
    try:
        response = session.get(f"{BACKEND_BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            result.add_result("Backend Health", True, "API is responding")
        else:
            result.add_result("Backend Health", False, f"HTTP {response.status_code}")
    except Exception as e:
        result.add_result("Backend Health", False, error=e)

def test_database_schema(result: SmokeTestResult):
    """Test database schema for required tables."""
    try:
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        required_tables = ['parts', 'stock_levels', 'prices_new', 'part_categories']
        missing_tables = [table for table in required_tables if table not in tables]
        
        if not missing_tables:
            result.add_result("Database Schema", True, "All required tables exist")
        else:
            result.add_result("Database Schema", False, f"Missing tables: {missing_tables}")
    except Exception as e:
        result.add_result("Database Schema", False, error=e)

def test_public_api_endpoints(session: requests.Session, result: SmokeTestResult):
    """Test public API endpoints."""
    endpoints = [
        ("/api/v1/parts/", "GET", "List Parts"),
        ("/api/v1/parts/categories/", "GET", "List Categories"),
    ]
    
    for endpoint, method, name in endpoints:
        try:
            if method == "GET":
                response = session.get(f"{BACKEND_BASE_URL}{endpoint}", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    result.add_result(f"Public API - {name}", True, f"Returned {len(data) if isinstance(data, list) else 'data'}")
                else:
                    result.add_result(f"Public API - {name}", False, f"HTTP {response.status_code}")
        except Exception as e:
            result.add_result(f"Public API - {name}", False, error=e)

def test_admin_api_endpoints(session: requests.Session, result: SmokeTestResult):
    """Test admin API endpoints (without auth for now)."""
    # Note: These will likely return 401 without proper auth, but we can test the endpoints exist
    endpoints = [
        ("/api/v1/admin/parts/", "POST", "Create Part"),
        ("/api/v1/admin/parts/1/price", "PUT", "Set Price"),
        ("/api/v1/admin/parts/1/stock", "PUT", "Set Stock"),
    ]
    
    for endpoint, method, name in endpoints:
        try:
            if method == "POST":
                response = session.post(f"{BACKEND_BASE_URL}{endpoint}", 
                                      json=TEST_PART_DATA, timeout=10)
            elif method == "PUT":
                if "price" in endpoint:
                    response = session.put(f"{BACKEND_BASE_URL}{endpoint}", 
                                         json=TEST_PRICE_DATA, timeout=10)
                else:
                    response = session.put(f"{BACKEND_BASE_URL}{endpoint}", 
                                         json=TEST_STOCK_DATA, timeout=10)
            
            # We expect 401 (unauthorized) or 422 (validation error) - both indicate endpoint exists
            if response.status_code in [401, 422]:
                result.add_result(f"Admin API - {name}", True, f"Endpoint exists (HTTP {response.status_code})")
            elif response.status_code == 200:
                result.add_result(f"Admin API - {name}", True, "Endpoint working")
            else:
                result.add_result(f"Admin API - {name}", False, f"HTTP {response.status_code}")
        except Exception as e:
            result.add_result(f"Admin API - {name}", False, error=e)

def test_database_operations(result: SmokeTestResult):
    """Test database operations directly."""
    try:
        Session = sessionmaker(bind=engine)
        db = Session()
        
        # Test creating a part
        parts_service = PartsEnhancedService(db)
        part = parts_service.create_part(TEST_PART_DATA)
        
        if part:
            result.add_result("Database - Create Part", True, f"Created part ID {part.id}")
            
            # Test setting price
            price = parts_service.set_part_price(part.id, TEST_PRICE_DATA)
            if price:
                effective_price = price.sale_price if price.sale_price else price.list_price
                result.add_result("Database - Set Price", True, f"Price: {effective_price}")
            else:
                result.add_result("Database - Set Price", False, "Failed to set price")
            
            # Test setting stock
            stock = parts_service.set_part_stock(part.id, TEST_STOCK_DATA)
            if stock:
                result.add_result("Database - Set Stock", True, f"Stock: {stock.current_stock}")
            else:
                result.add_result("Database - Set Stock", False, "Failed to set stock")
            
            # Test retrieving part with relationships
            retrieved_part = parts_service.get_part_by_id(part.id)
            if retrieved_part and retrieved_part.price_info and retrieved_part.stock_level:
                result.add_result("Database - Retrieve with Relations", True, 
                                f"Part has price and stock data")
            else:
                result.add_result("Database - Retrieve with Relations", False, 
                                "Missing price or stock data")
            
            # Cleanup - delete test part
            db.delete(part)
            db.commit()
            result.add_result("Database - Cleanup", True, "Test data cleaned up")
            
        else:
            result.add_result("Database - Create Part", False, "Failed to create part")
        
        db.close()
        
    except Exception as e:
        result.add_result("Database Operations", False, error=e)

def test_frontend_accessibility(session: requests.Session, result: SmokeTestResult):
    """Test frontend accessibility."""
    try:
        # Test web portal
        response = session.get(WEB_PORTAL_URL, timeout=10)
        if response.status_code == 200:
            result.add_result("Frontend - Web Portal", True, "Web portal accessible")
        else:
            result.add_result("Frontend - Web Portal", False, f"HTTP {response.status_code}")
    except Exception as e:
        result.add_result("Frontend - Web Portal", False, error=e)
    
    try:
        # Test admin panel
        response = session.get(ADMIN_PANEL_URL, timeout=10)
        if response.status_code == 200:
            result.add_result("Frontend - Admin Panel", True, "Admin panel accessible")
        else:
            result.add_result("Frontend - Admin Panel", False, f"HTTP {response.status_code}")
    except Exception as e:
        result.add_result("Frontend - Admin Panel", False, error=e)

def test_api_response_structure(session: requests.Session, result: SmokeTestResult):
    """Test API response structure includes price and stock data."""
    try:
        response = session.get(f"{BACKEND_BASE_URL}/api/v1/parts/", timeout=10)
        if response.status_code == 200:
            parts = response.json()
            if parts:
                part = parts[0]
                has_price = 'price' in part
                has_stock = 'stock' in part
                
                if has_price and has_stock:
                    result.add_result("API Response Structure", True, 
                                    "Parts include price and stock data")
                else:
                    missing = []
                    if not has_price: missing.append('price')
                    if not has_stock: missing.append('stock')
                    result.add_result("API Response Structure", False, 
                                    f"Missing fields: {missing}")
            else:
                result.add_result("API Response Structure", False, "No parts found")
        else:
            result.add_result("API Response Structure", False, f"HTTP {response.status_code}")
    except Exception as e:
        result.add_result("API Response Structure", False, error=e)

def main():
    parser = argparse.ArgumentParser(description="Smoke test for Parts & Inventory Integration")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--create-test-data", action="store_true", help="Create test data")
    args = parser.parse_args()
    
    print(f"{Colors.BOLD}{Colors.BLUE}Parts & Inventory Integration Smoke Test{Colors.END}")
    print(f"{Colors.BLUE}{'='*50}{Colors.END}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    result = SmokeTestResult()
    session = create_http_session()
    
    # Run tests
    print(f"{Colors.BOLD}Backend Tests{Colors.END}")
    test_backend_health(session, result)
    test_database_schema(result)
    test_public_api_endpoints(session, result)
    test_admin_api_endpoints(session, result)
    test_database_operations(result)
    test_api_response_structure(session, result)
    
    print(f"\n{Colors.BOLD}Frontend Tests{Colors.END}")
    test_frontend_accessibility(session, result)
    
    # Summary
    success = result.summary()
    
    if success:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 All tests passed! Integration is working correctly.{Colors.END}")
        sys.exit(0)
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}❌ Some tests failed. Check the errors above.{Colors.END}")
        sys.exit(1)

if __name__ == "__main__":
    main()
