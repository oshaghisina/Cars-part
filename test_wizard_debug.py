#!/usr/bin/env python3
"""Test script to debug wizard functionality."""

import requests
import json

def test_wizard_api():
    """Test wizard API endpoints."""
    base_url = "http://localhost:8001/api/v1/wizard"
    
    print("🧪 Testing Wizard API Debug")
    print("=" * 50)
    
    # Test 1: Get brands
    print("\n1️⃣ Testing brands endpoint...")
    try:
        response = requests.get(f"{base_url}/brands")
        if response.status_code == 200:
            brands = response.json()
            print(f"   ✅ Brands: {brands}")
        else:
            print(f"   ❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Create session
    print("\n2️⃣ Testing session creation...")
    try:
        response = requests.post(f"{base_url}/sessions", json={
            "user_id": "debug_test_user",
            "state": "start"
        })
        if response.status_code == 200:
            session = response.json()
            print(f"   ✅ Session created: {session}")
        else:
            print(f"   ❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Update session with brand
    print("\n3️⃣ Testing session update with brand...")
    try:
        response = requests.put(f"{base_url}/sessions/debug_test_user", json={
            "state": "model_selection",
            "vehicle_data": {"brand": "Chery"}
        })
        if response.status_code == 200:
            session = response.json()
            print(f"   ✅ Session updated: {session}")
        else:
            print(f"   ❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Get models for Chery
    print("\n4️⃣ Testing models for Chery...")
    try:
        response = requests.get(f"{base_url}/models?brand=Chery")
        if response.status_code == 200:
            models = response.json()
            print(f"   ✅ Models for Chery: {models}")
        else:
            print(f"   ❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 5: Clean up
    print("\n5️⃣ Cleaning up test session...")
    try:
        response = requests.delete(f"{base_url}/sessions/debug_test_user")
        if response.status_code == 200:
            print(f"   ✅ Session deleted")
        else:
            print(f"   ❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n📊 Wizard API Debug Complete!")
    print("=" * 50)

if __name__ == "__main__":
    test_wizard_api()
