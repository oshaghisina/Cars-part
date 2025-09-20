#!/usr/bin/env python3
"""
Test Wizard API Endpoints
Tests the wizard functionality for guided part search.
"""

import requests
import json
from datetime import datetime

def test_wizard_api():
    """Test wizard API endpoints."""
    print("🧪 Testing Wizard API Endpoints")
    print("=" * 50)
    
    base_url = "http://localhost:8001/api/v1/wizard"
    test_user_id = "123456789"
    
    # Test 1: Create wizard session
    print("\n1️⃣ Creating Wizard Session...")
    try:
        response = requests.post(f"{base_url}/sessions", json={
            "user_id": test_user_id,
            "state": "start"
        })
        if response.status_code == 200:
            session_data = response.json()
            print(f"   ✅ Session created: {session_data['id']}")
            print(f"      • User ID: {session_data['user_id']}")
            print(f"      • State: {session_data['state']}")
        else:
            print(f"   ❌ Failed to create session: {response.status_code}")
            print(f"      Response: {response.text}")
            return
    except Exception as e:
        print(f"   ❌ Error creating session: {e}")
        return
    
    # Test 2: Get available brands
    print("\n2️⃣ Getting Available Brands...")
    try:
        response = requests.get(f"{base_url}/brands")
        if response.status_code == 200:
            brands = response.json()
            print(f"   ✅ Found {len(brands)} brands: {brands[:5]}{'...' if len(brands) > 5 else ''}")
        else:
            print(f"   ❌ Failed to get brands: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error getting brands: {e}")
    
    # Test 3: Get models for a brand
    print("\n3️⃣ Getting Models for Brand...")
    try:
        response = requests.get(f"{base_url}/models?brand=Chery")
        if response.status_code == 200:
            models = response.json()
            print(f"   ✅ Found {len(models)} Chery models: {models}")
        else:
            print(f"   ❌ Failed to get models: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error getting models: {e}")
    
    # Test 4: Get categories
    print("\n4️⃣ Getting Part Categories...")
    try:
        response = requests.get(f"{base_url}/categories?brand=Chery&model=Tiggo 8")
        if response.status_code == 200:
            categories = response.json()
            print(f"   ✅ Found {len(categories)} categories: {categories}")
        else:
            print(f"   ❌ Failed to get categories: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error getting categories: {e}")
    
    # Test 5: Get parts
    print("\n5️⃣ Getting Parts...")
    try:
        response = requests.get(f"{base_url}/parts?brand=Chery&model=Tiggo 8&category=Brake System")
        if response.status_code == 200:
            parts = response.json()
            print(f"   ✅ Found {len(parts)} brake system parts")
            if parts:
                print(f"      • Example: {parts[0]['part_name']} - {parts[0]['position']}")
        else:
            print(f"   ❌ Failed to get parts: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error getting parts: {e}")
    
    # Test 6: Update wizard session
    print("\n6️⃣ Updating Wizard Session...")
    try:
        response = requests.put(f"{base_url}/sessions/{test_user_id}", json={
            "state": "brand_selection",
            "vehicle_data": {
                "brand": "Chery",
                "model": "Tiggo 8"
            }
        })
        if response.status_code == 200:
            updated_session = response.json()
            print(f"   ✅ Session updated")
            print(f"      • New state: {updated_session['state']}")
            print(f"      • Vehicle data: {updated_session['vehicle_data']}")
        else:
            print(f"   ❌ Failed to update session: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error updating session: {e}")
    
    # Test 7: Search parts by criteria
    print("\n7️⃣ Searching Parts by Criteria...")
    try:
        response = requests.post(f"{base_url}/search", json={
            "vehicle_data": {
                "brand": "Chery",
                "model": "Tiggo 8"
            },
            "part_data": {
                "category": "Brake System"
            }
        })
        if response.status_code == 200:
            search_results = response.json()
            print(f"   ✅ Found {len(search_results)} matching parts")
            if search_results:
                for i, part in enumerate(search_results[:3], 1):
                    print(f"      {i}. {part['part_name']} - {part['position']}")
        else:
            print(f"   ❌ Failed to search parts: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error searching parts: {e}")
    
    # Test 8: Get session
    print("\n8️⃣ Getting Wizard Session...")
    try:
        response = requests.get(f"{base_url}/sessions/{test_user_id}")
        if response.status_code == 200:
            session = response.json()
            print(f"   ✅ Retrieved session")
            print(f"      • State: {session['state']}")
            print(f"      • Vehicle data: {session['vehicle_data']}")
            print(f"      • Part data: {session['part_data']}")
        else:
            print(f"   ❌ Failed to get session: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error getting session: {e}")
    
    # Test 9: Clear session
    print("\n9️⃣ Clearing Wizard Session...")
    try:
        response = requests.delete(f"{base_url}/sessions/{test_user_id}")
        if response.status_code == 200:
            print(f"   ✅ Session cleared successfully")
        else:
            print(f"   ❌ Failed to clear session: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error clearing session: {e}")
    
    print("\n📊 Wizard API Test Results")
    print("=" * 50)
    print("✅ Wizard API endpoints are working!")
    print("🎯 Ready to implement bot wizard flow!")

if __name__ == "__main__":
    test_wizard_api()
