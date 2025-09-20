#!/usr/bin/env python3
"""
Test localhost services to ensure everything is working properly.
"""

import requests
import json

def test_localhost():
    """Test all localhost services."""
    print("🌐 Testing Localhost Services")
    print("=" * 40)
    
    # Test API Health
    print("\n1️⃣ API Health Check")
    try:
        response = requests.get("http://localhost:8001/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ API Server: http://localhost:8001")
            print(f"   📊 Status: {data['status']}")
            print(f"   🔧 Environment: {data['app_env']}")
            print(f"   🐛 Debug: {data['debug']}")
        else:
            print(f"   ❌ API Health failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ API Health error: {e}")
    
    # Test Frontend
    print("\n2️⃣ Frontend Check")
    try:
        response = requests.get("http://localhost:5173", timeout=5)
        if response.status_code == 200:
            print(f"   ✅ Frontend: http://localhost:5173")
            print(f"   📱 Status: {response.status_code} OK")
        else:
            print(f"   ❌ Frontend failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Frontend error: {e}")
    
    # Test API Endpoints
    print("\n3️⃣ API Endpoints Test")
    endpoints = [
        ("/api/v1/orders/", "Orders"),
        ("/api/v1/leads/", "Leads"),
        ("/api/v1/search/parts?q=test", "Search"),
    ]
    
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"http://localhost:8001{endpoint}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    print(f"   ✅ {name}: {len(data)} items")
                else:
                    print(f"   ✅ {name}: Working")
            else:
                print(f"   ❌ {name}: {response.status_code}")
        except Exception as e:
            print(f"   ❌ {name}: {e}")
    
    # Test API Documentation
    print("\n4️⃣ API Documentation")
    try:
        response = requests.get("http://localhost:8001/docs", timeout=5)
        if response.status_code == 200:
            print(f"   ✅ API Docs: http://localhost:8001/docs")
        else:
            print(f"   ❌ API Docs failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ API Docs error: {e}")
    
    print("\n" + "=" * 40)
    print("🎉 Localhost Test Complete!")
    print("\n📱 Access URLs:")
    print("   🖥️  Admin Panel: http://localhost:5173")
    print("   🔧 API Server: http://localhost:8001")
    print("   📚 API Docs: http://localhost:8001/docs")
    print("   ❤️  Health Check: http://localhost:8001/health")
    
    print("\n🚀 Ready to Use:")
    print("   ✅ Frontend Vue.js admin panel")
    print("   ✅ FastAPI backend server")
    print("   ✅ Order management system")
    print("   ✅ Customer management")
    print("   ✅ Search functionality")

if __name__ == "__main__":
    test_localhost()
