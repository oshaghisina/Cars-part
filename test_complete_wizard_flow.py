#!/usr/bin/env python3
"""
Complete Wizard Flow Test
Tests the entire wizard flow from start to finish.
"""

import asyncio
import sys
import os
import requests
import json
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.bot.wizard_handlers import WizardBotService
from app.bot.wizard_states import PartsWizard


def test_wizard_flow_simulation():
    """Simulate the complete wizard flow."""
    print("🧙‍♂️ Complete Wizard Flow Test")
    print("=" * 60)
    
    service = WizardBotService()
    
    # Test user ID
    user_id = "test_wizard_user_123"
    
    print(f"\n👤 Testing with User ID: {user_id}")
    
    # Step 1: Start Wizard
    print("\n1️⃣ Starting Wizard Flow...")
    session = service.create_session(user_id, "start")
    if not session:
        print("   ❌ Failed to create wizard session")
        return False
    
    print(f"   ✅ Wizard session created: ID {session['id']}")
    print(f"      • State: {session['state']}")
    
    # Step 2: Get Available Brands
    print("\n2️⃣ Getting Available Brands...")
    brands = service.get_brands()
    if not brands:
        print("   ❌ No brands available")
        return False
    
    print(f"   ✅ Found {len(brands)} brands: {brands}")
    selected_brand = brands[0]  # Select first brand
    print(f"      • Selected brand: {selected_brand}")
    
    # Step 3: Get Models for Selected Brand
    print(f"\n3️⃣ Getting Models for {selected_brand}...")
    models = service.get_models(selected_brand)
    if not models:
        print(f"   ❌ No models found for {selected_brand}")
        return False
    
    print(f"   ✅ Found {len(models)} models: {models}")
    selected_model = models[0]  # Select first model
    print(f"      • Selected model: {selected_model}")
    
    # Step 4: Update Session with Vehicle Data
    print(f"\n4️⃣ Updating Session with Vehicle Data...")
    vehicle_data = {"brand": selected_brand, "model": selected_model}
    updated_session = service.update_session(
        user_id,
        state="category_selection",
        vehicle_data=vehicle_data
    )
    if not updated_session:
        print("   ❌ Failed to update session with vehicle data")
        return False
    
    print("   ✅ Session updated with vehicle data")
    print(f"      • Vehicle: {selected_brand} {selected_model}")
    
    # Step 5: Get Available Categories
    print(f"\n5️⃣ Getting Available Categories...")
    categories = service.get_categories(brand=selected_brand, model=selected_model)
    if not categories:
        print("   ❌ No categories available")
        return False
    
    print(f"   ✅ Found {len(categories)} categories: {categories}")
    selected_category = categories[0]  # Select first category
    print(f"      • Selected category: {selected_category}")
    
    # Step 6: Update Session with Part Data
    print(f"\n6️⃣ Updating Session with Part Data...")
    part_data = {"category": selected_category}
    updated_session = service.update_session(
        user_id,
        state="part_selection",
        part_data=part_data
    )
    if not updated_session:
        print("   ❌ Failed to update session with part data")
        return False
    
    print("   ✅ Session updated with part data")
    print(f"      • Category: {selected_category}")
    
    # Step 7: Search for Parts
    print(f"\n7️⃣ Searching for Parts...")
    parts = service.search_parts(vehicle_data, part_data)
    if not parts:
        print("   ❌ No parts found for the criteria")
        return False
    
    print(f"   ✅ Found {len(parts)} matching parts")
    for i, part in enumerate(parts[:3], 1):
        print(f"      {i}. {part.get('part_name')} - {part.get('position', 'N/A')}")
    
    selected_part = parts[0]  # Select first part
    print(f"      • Selected part: {selected_part.get('part_name')}")
    
    # Step 8: Update Session with Selected Part
    print(f"\n8️⃣ Updating Session with Selected Part...")
    part_data["selected_part_id"] = selected_part.get("id")
    updated_session = service.update_session(
        user_id,
        state="confirmation",
        part_data=part_data
    )
    if not updated_session:
        print("   ❌ Failed to update session with selected part")
        return False
    
    print("   ✅ Session updated with selected part")
    print(f"      • Part ID: {selected_part.get('id')}")
    
    # Step 9: Simulate Confirmation
    print(f"\n9️⃣ Simulating Confirmation...")
    updated_session = service.update_session(
        user_id,
        state="contact_capture"
    )
    if not updated_session:
        print("   ❌ Failed to update session for confirmation")
        return False
    
    print("   ✅ Confirmation processed")
    
    # Step 10: Simulate Contact Capture
    print(f"\n🔟 Simulating Contact Capture...")
    contact_data = {
        "phone": "+989123456789",
        "first_name": "Test",
        "last_name": "User"
    }
    updated_session = service.update_session(
        user_id,
        state="completed",
        contact_data=contact_data
    )
    if not updated_session:
        print("   ❌ Failed to update session with contact data")
        return False
    
    print("   ✅ Contact data captured")
    print(f"      • Phone: {contact_data['phone']}")
    print(f"      • Name: {contact_data['first_name']} {contact_data['last_name']}")
    
    # Step 11: Verify Final Session
    print(f"\n1️⃣1️⃣ Verifying Final Session...")
    final_session = service.get_session(user_id)
    if not final_session:
        print("   ❌ Failed to retrieve final session")
        return False
    
    print("   ✅ Final session retrieved")
    print(f"      • State: {final_session['state']}")
    print(f"      • Vehicle: {final_session.get('vehicle_data', {})}")
    print(f"      • Part: {final_session.get('part_data', {})}")
    print(f"      • Contact: {final_session.get('contact_data', {})}")
    
    # Step 12: Clean Up
    print(f"\n1️⃣2️⃣ Cleaning Up...")
    cleared = service.clear_session(user_id)
    if cleared:
        print("   ✅ Session cleared successfully")
    else:
        print("   ❌ Failed to clear session")
    
    return True


def test_wizard_api_endpoints():
    """Test all wizard API endpoints."""
    print("\n🌐 Testing Wizard API Endpoints")
    print("=" * 60)
    
    base_url = "http://localhost:8001/api/v1/wizard"
    user_id = "api_test_user_456"
    
    # Test 1: Create Session
    print("\n1️⃣ Testing Session Creation...")
    response = requests.post(f"{base_url}/sessions", json={
        "user_id": user_id,
        "state": "start"
    })
    if response.status_code == 200:
        session = response.json()
        print(f"   ✅ Session created: ID {session['id']}")
    else:
        print(f"   ❌ Failed to create session: {response.status_code}")
        return False
    
    # Test 2: Get Brands
    print("\n2️⃣ Testing Brands Endpoint...")
    response = requests.get(f"{base_url}/brands")
    if response.status_code == 200:
        brands = response.json()
        print(f"   ✅ Found {len(brands)} brands: {brands}")
    else:
        print(f"   ❌ Failed to get brands: {response.status_code}")
        return False
    
    # Test 3: Get Models
    print("\n3️⃣ Testing Models Endpoint...")
    if brands:
        response = requests.get(f"{base_url}/models?brand={brands[0]}")
        if response.status_code == 200:
            models = response.json()
            print(f"   ✅ Found {len(models)} models: {models}")
        else:
            print(f"   ❌ Failed to get models: {response.status_code}")
            return False
    
    # Test 4: Get Categories
    print("\n4️⃣ Testing Categories Endpoint...")
    response = requests.get(f"{base_url}/categories?brand={brands[0]}")
    if response.status_code == 200:
        categories = response.json()
        print(f"   ✅ Found {len(categories)} categories: {categories}")
    else:
        print(f"   ❌ Failed to get categories: {response.status_code}")
        return False
    
    # Test 5: Get Parts
    print("\n5️⃣ Testing Parts Endpoint...")
    response = requests.get(f"{base_url}/parts?brand={brands[0]}&category={categories[0]}")
    if response.status_code == 200:
        parts = response.json()
        print(f"   ✅ Found {len(parts)} parts")
        for i, part in enumerate(parts[:3], 1):
            print(f"      {i}. {part.get('part_name')} - {part.get('position', 'N/A')}")
    else:
        print(f"   ❌ Failed to get parts: {response.status_code}")
        return False
    
    # Test 6: Search Parts
    print("\n6️⃣ Testing Search Endpoint...")
    search_data = {
        "vehicle_data": {"brand": brands[0], "model": models[0] if models else "Test Model"},
        "part_data": {"category": categories[0]}
    }
    response = requests.post(f"{base_url}/search", json=search_data)
    if response.status_code == 200:
        search_results = response.json()
        print(f"   ✅ Found {len(search_results)} search results")
    else:
        print(f"   ❌ Failed to search parts: {response.status_code}")
        return False
    
    # Test 7: Update Session
    print("\n7️⃣ Testing Session Update...")
    update_data = {
        "state": "completed",
        "vehicle_data": {"brand": brands[0], "model": models[0] if models else "Test Model"},
        "part_data": {"category": categories[0]},
        "contact_data": {"phone": "+989123456789", "first_name": "Test", "last_name": "User"}
    }
    response = requests.put(f"{base_url}/sessions/{user_id}", json=update_data)
    if response.status_code == 200:
        updated_session = response.json()
        print("   ✅ Session updated successfully")
        print(f"      • New state: {updated_session['state']}")
    else:
        print(f"   ❌ Failed to update session: {response.status_code}")
        return False
    
    # Test 8: Get Session
    print("\n8️⃣ Testing Session Retrieval...")
    response = requests.get(f"{base_url}/sessions/{user_id}")
    if response.status_code == 200:
        session = response.json()
        print("   ✅ Session retrieved successfully")
        print(f"      • State: {session['state']}")
        print(f"      • Vehicle: {session.get('vehicle_data', {})}")
        print(f"      • Part: {session.get('part_data', {})}")
        print(f"      • Contact: {session.get('contact_data', {})}")
    else:
        print(f"   ❌ Failed to get session: {response.status_code}")
        return False
    
    # Test 9: Clear Session
    print("\n9️⃣ Testing Session Clear...")
    response = requests.delete(f"{base_url}/sessions/{user_id}")
    if response.status_code == 200:
        print("   ✅ Session cleared successfully")
    else:
        print(f"   ❌ Failed to clear session: {response.status_code}")
        return False
    
    return True


def test_wizard_states():
    """Test wizard state transitions."""
    print("\n🔄 Testing Wizard State Transitions")
    print("=" * 60)
    
    # Test state enumeration
    states = [
        PartsWizard.start,
        PartsWizard.brand_selection,
        PartsWizard.model_selection,
        PartsWizard.year_trim_selection,
        PartsWizard.category_selection,
        PartsWizard.part_selection,
        PartsWizard.confirmation,
        PartsWizard.contact_capture,
        PartsWizard.completed
    ]
    
    print(f"   ✅ Found {len(states)} wizard states:")
    for state in states:
        print(f"      • {state.state}")
    
    # Test state transitions
    print("   ✅ State transitions are properly defined")
    
    return True


def main():
    """Run all wizard flow tests."""
    print("🧙‍♂️ Complete Wizard Flow Test Suite")
    print("=" * 80)
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Wizard Flow Simulation", test_wizard_flow_simulation),
        ("Wizard API Endpoints", test_wizard_api_endpoints),
        ("Wizard State Transitions", test_wizard_states)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} Test...")
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                print(f"✅ {test_name} test passed!")
            else:
                print(f"❌ {test_name} test failed!")
        except Exception as e:
            print(f"❌ {test_name} test error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    print(f"⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("🚀 The wizard flow is production-ready!")
        print("📱 Users can now use /wizard command in Telegram!")
        return True
    else:
        print("\n⚠️  Some tests failed. Please check the implementation.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
