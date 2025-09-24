#!/usr/bin/env python3
"""
PDP Integration Test Script
Tests the PDP API endpoints and authentication integration
"""

import requests
import json
import sys
from typing import Dict, Any

# Configuration
API_BASE_URL = "http://localhost:8001/api/v1"
TEST_USER = {
    "username_or_email": "admin@chinacarparts.com",
    "password": "kCTK39E&T#K%"
}

def test_api_health() -> bool:
    """Test API health endpoint"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API Health Check: PASSED")
            return True
        else:
            print(f"❌ API Health Check: FAILED (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ API Health Check: FAILED (Error: {e})")
        return False

def test_user_login() -> tuple[bool, str]:
    """Test user login and get token"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/users/login",
            json=TEST_USER,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if "access_token" in data:
                print("✅ User Login: PASSED")
                return True, data["access_token"]
            else:
                print("❌ User Login: FAILED (No access token)")
                return False, ""
        else:
            print(f"❌ User Login: FAILED (Status: {response.status_code})")
            return False, ""
    except Exception as e:
        print(f"❌ User Login: FAILED (Error: {e})")
        return False, ""

def test_get_user_info(token: str) -> bool:
    """Test getting user information with token"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{API_BASE_URL}/users/me",
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ Get User Info: PASSED (User: {user_data.get('username', 'Unknown')})")
            return True
        else:
            print(f"❌ Get User Info: FAILED (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Get User Info: FAILED (Error: {e})")
        return False

def test_get_parts(token: str) -> bool:
    """Test getting parts list"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{API_BASE_URL}/parts",
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            parts_data = response.json()
            print(f"✅ Get Parts: PASSED ({len(parts_data)} parts found)")
            return True
        else:
            print(f"❌ Get Parts: FAILED (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Get Parts: FAILED (Error: {e})")
        return False

def test_get_part_by_id(token: str, part_id: int = 1) -> bool:
    """Test getting a specific part by ID"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{API_BASE_URL}/parts/{part_id}",
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            part_data = response.json()
            print(f"✅ Get Part by ID: PASSED (Part: {part_data.get('part_name', 'Unknown')})")
            return True
        elif response.status_code == 404:
            print(f"⚠️  Get Part by ID: PART NOT FOUND (ID: {part_id})")
            return True  # This is expected if no parts exist
        else:
            print(f"❌ Get Part by ID: FAILED (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Get Part by ID: FAILED (Error: {e})")
        return False

def test_categories(token: str) -> bool:
    """Test getting categories"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{API_BASE_URL}/parts/categories/list",
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            categories_data = response.json()
            print(f"✅ Get Categories: PASSED ({len(categories_data.get('categories', []))} categories)")
            return True
        else:
            print(f"❌ Get Categories: FAILED (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Get Categories: FAILED (Error: {e})")
        return False

def main():
    """Run all PDP integration tests"""
    print("🚀 Starting PDP Integration Tests...")
    print("=" * 50)
    
    # Test API health
    if not test_api_health():
        print("\n❌ API is not accessible. Please start the backend server.")
        sys.exit(1)
    
    # Test user login
    login_success, token = test_user_login()
    if not login_success:
        print("\n❌ Cannot proceed without authentication.")
        sys.exit(1)
    
    # Test authenticated endpoints
    print("\n🔐 Testing Authenticated Endpoints...")
    print("-" * 30)
    
    tests_passed = 0
    total_tests = 4
    
    if test_get_user_info(token):
        tests_passed += 1
    
    if test_get_parts(token):
        tests_passed += 1
    
    if test_get_part_by_id(token):
        tests_passed += 1
    
    if test_categories(token):
        tests_passed += 1
    
    # Summary
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! PDP integration is ready.")
        return True
    else:
        print("⚠️  Some tests failed. Check the backend server and database.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
