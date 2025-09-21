#!/usr/bin/env python3
"""
Production Setup Test Script
Tests all components of the production deployment.
"""

import requests
import os
import sys
import time
from datetime import datetime

def test_api_health(base_url):
    """Test API health endpoint."""
    print("🔍 Testing API Health...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ API Health: {data['status']}")
            return True
        else:
            print(f"   ❌ API Health failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ API Health error: {e}")
        return False

def test_database_connection(base_url):
    """Test database connectivity through API."""
    print("🔍 Testing Database Connection...")
    try:
        response = requests.get(f"{base_url}/api/v1/parts/", timeout=10)
        if response.status_code == 200:
            parts = response.json()
            print(f"   ✅ Database connected: {len(parts)} parts found")
            return True
        else:
            print(f"   ❌ Database test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Database test error: {e}")
        return False

def test_parts_management(base_url):
    """Test parts management functionality."""
    print("🔍 Testing Parts Management...")
    try:
        # Test list parts
        response = requests.get(f"{base_url}/api/v1/parts/", timeout=10)
        if response.status_code == 200:
            print("   ✅ Parts listing works")
        else:
            print(f"   ❌ Parts listing failed: {response.status_code}")
            return False
        
        # Test categories
        response = requests.get(f"{base_url}/api/v1/parts/categories/list", timeout=10)
        if response.status_code == 200:
            categories = response.json().get("categories", [])
            print(f"   ✅ Categories endpoint: {len(categories)} categories")
        else:
            print(f"   ❌ Categories endpoint failed: {response.status_code}")
            return False
        
        # Test vehicle makes
        response = requests.get(f"{base_url}/api/v1/parts/vehicle-makes/list", timeout=10)
        if response.status_code == 200:
            makes = response.json().get("vehicle_makes", [])
            print(f"   ✅ Vehicle makes endpoint: {len(makes)} makes")
        else:
            print(f"   ❌ Vehicle makes endpoint failed: {response.status_code}")
            return False
        
        return True
    except Exception as e:
        print(f"   ❌ Parts management test error: {e}")
        return False

def test_search_functionality(base_url):
    """Test search functionality."""
    print("🔍 Testing Search Functionality...")
    try:
        # Test single search
        response = requests.get(f"{base_url}/api/v1/parts/?search=brake", timeout=10)
        if response.status_code == 200:
            results = response.json()
            print(f"   ✅ Single search works: {len(results)} results")
        else:
            print(f"   ❌ Single search failed: {response.status_code}")
            return False
        
        # Test additional search terms
        response = requests.get(f"{base_url}/api/v1/parts/?search=filter", timeout=10)
        if response.status_code == 200:
            results = response.json()
            print(f"   ✅ Additional search works: {len(results)} results")
        else:
            print(f"   ❌ Additional search failed: {response.status_code}")
            return False
        
        return True
    except Exception as e:
        print(f"   ❌ Search functionality test error: {e}")
        return False

def test_orders_management(base_url):
    """Test orders management functionality."""
    print("🔍 Testing Orders Management...")
    try:
        # Test list orders
        response = requests.get(f"{base_url}/api/v1/orders/", timeout=10)
        if response.status_code == 200:
            orders = response.json()
            print(f"   ✅ Orders listing works: {len(orders)} orders")
        else:
            print(f"   ❌ Orders listing failed: {response.status_code}")
            return False
        
        return True
    except Exception as e:
        print(f"   ❌ Orders management test error: {e}")
        return False

def test_leads_management(base_url):
    """Test leads management functionality."""
    print("🔍 Testing Leads Management...")
    try:
        # Test list leads
        response = requests.get(f"{base_url}/api/v1/leads/", timeout=10)
        if response.status_code == 200:
            leads = response.json()
            print(f"   ✅ Leads listing works: {len(leads)} leads")
        else:
            print(f"   ❌ Leads listing failed: {response.status_code}")
            return False
        
        return True
    except Exception as e:
        print(f"   ❌ Leads management test error: {e}")
        return False

def test_frontend_access(base_url):
    """Test frontend accessibility."""
    print("🔍 Testing Frontend Access...")
    try:
        response = requests.get(base_url, timeout=10)
        if response.status_code == 200:
            print("   ✅ Frontend accessible")
            return True
        else:
            print(f"   ❌ Frontend access failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Frontend access error: {e}")
        return False

def test_ssl_certificate(base_url):
    """Test SSL certificate validity."""
    print("🔍 Testing SSL Certificate...")
    try:
        if base_url.startswith("https://"):
            response = requests.get(base_url, timeout=10, verify=True)
            print("   ✅ SSL certificate is valid")
            return True
        else:
            print("   ⚠️  Not using HTTPS - SSL test skipped")
            return True
    except requests.exceptions.SSLError as e:
        print(f"   ❌ SSL certificate error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ SSL test error: {e}")
        return False

def main():
    """Main test function."""
    print("🧪 China Car Parts Production Setup Test")
    print("=" * 50)
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Get base URL from environment or use default
    base_url = os.getenv("TEST_BASE_URL", "http://localhost:8001")
    
    if base_url.endswith("/"):
        base_url = base_url[:-1]
    
    print(f"🌐 Testing URL: {base_url}")
    print()
    
    # Run all tests
    tests = [
        ("API Health", lambda: test_api_health(base_url)),
        ("Database Connection", lambda: test_database_connection(base_url)),
        ("Parts Management", lambda: test_parts_management(base_url)),
        ("Search Functionality", lambda: test_search_functionality(base_url)),
        ("Orders Management", lambda: test_orders_management(base_url)),
        ("Leads Management", lambda: test_leads_management(base_url)),
        ("Frontend Access", lambda: test_frontend_access(base_url)),
        ("SSL Certificate", lambda: test_ssl_certificate(base_url)),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            print()
        except Exception as e:
            print(f"   ❌ Test failed with exception: {e}")
            results.append((test_name, False))
            print()
        
        # Small delay between tests
        time.sleep(0.5)
    
    # Summary
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print()
    print(f"🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your production setup is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
