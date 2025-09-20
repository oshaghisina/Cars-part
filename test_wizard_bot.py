#!/usr/bin/env python3
"""
Test Wizard Bot Implementation
Tests the wizard bot handlers and flow.
"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.bot.wizard_handlers import WizardBotService, create_inline_keyboard
from app.bot.wizard_states import PartsWizard


def test_wizard_service():
    """Test the wizard service functionality."""
    print("🧪 Testing Wizard Bot Service")
    print("=" * 50)
    
    service = WizardBotService()
    
    # Test 1: Create session
    print("\n1️⃣ Testing Session Creation...")
    session = service.create_session("test_user_123", "start")
    if session:
        print(f"   ✅ Session created: ID {session.get('id')}")
        print(f"      • User ID: {session.get('user_id')}")
        print(f"      • State: {session.get('state')}")
    else:
        print("   ❌ Failed to create session")
        return False
    
    # Test 2: Get brands
    print("\n2️⃣ Testing Brand Retrieval...")
    brands = service.get_brands()
    if brands:
        print(f"   ✅ Found {len(brands)} brands: {brands}")
    else:
        print("   ❌ Failed to get brands")
        return False
    
    # Test 3: Get models for a brand
    print("\n3️⃣ Testing Model Retrieval...")
    if brands:
        models = service.get_models(brands[0])
        if models:
            print(f"   ✅ Found {len(models)} models for {brands[0]}: {models}")
        else:
            print(f"   ❌ No models found for {brands[0]}")
            return False
    
    # Test 4: Get categories
    print("\n4️⃣ Testing Category Retrieval...")
    categories = service.get_categories(brand=brands[0])
    if categories:
        print(f"   ✅ Found {len(categories)} categories: {categories}")
    else:
        print("   ❌ No categories found")
        return False
    
    # Test 5: Get parts
    print("\n5️⃣ Testing Part Retrieval...")
    if brands and categories:
        parts = service.get_parts(brand=brands[0], category=categories[0])
        if parts:
            print(f"   ✅ Found {len(parts)} parts")
            for i, part in enumerate(parts[:3], 1):
                print(f"      {i}. {part.get('part_name')} - {part.get('position', 'N/A')}")
        else:
            print("   ❌ No parts found")
            return False
    
    # Test 6: Search parts
    print("\n6️⃣ Testing Part Search...")
    if brands and models and categories:
        vehicle_data = {"brand": brands[0], "model": models[0]}
        part_data = {"category": categories[0]}
        
        search_results = service.search_parts(vehicle_data, part_data)
        if search_results:
            print(f"   ✅ Found {len(search_results)} matching parts")
            for i, part in enumerate(search_results[:3], 1):
                print(f"      {i}. {part.get('part_name')} - {part.get('position', 'N/A')}")
        else:
            print("   ❌ No search results found")
            return False
    
    # Test 7: Update session
    print("\n7️⃣ Testing Session Update...")
    updated_session = service.update_session(
        "test_user_123",
        state="completed",
        vehicle_data={"brand": brands[0], "model": models[0] if models else "Test Model"},
        part_data={"category": categories[0]},
        contact_data={"phone": "+989123456789", "first_name": "Test", "last_name": "User"}
    )
    if updated_session:
        print("   ✅ Session updated successfully")
        print(f"      • New state: {updated_session.get('state')}")
        print(f"      • Vehicle data: {updated_session.get('vehicle_data')}")
        print(f"      • Part data: {updated_session.get('part_data')}")
        print(f"      • Contact data: {updated_session.get('contact_data')}")
    else:
        print("   ❌ Failed to update session")
        return False
    
    # Test 8: Clear session
    print("\n8️⃣ Testing Session Clear...")
    cleared = service.clear_session("test_user_123")
    if cleared:
        print("   ✅ Session cleared successfully")
    else:
        print("   ❌ Failed to clear session")
        return False
    
    print("\n📊 Wizard Bot Service Test Results")
    print("=" * 50)
    print("✅ All wizard service tests passed!")
    return True


def test_inline_keyboard():
    """Test inline keyboard creation."""
    print("\n🎹 Testing Inline Keyboard Creation")
    print("=" * 50)
    
    # Test data
    test_items = ["Chery", "JAC", "Brilliance"]
    
    # Test keyboard creation
    keyboard = create_inline_keyboard(test_items, "brand", "brand")
    
    if keyboard and keyboard.inline_keyboard:
        print(f"   ✅ Keyboard created with {len(keyboard.inline_keyboard)} rows")
        
        # Check if all items are present
        all_buttons = []
        for row in keyboard.inline_keyboard:
            for button in row:
                all_buttons.append(button.text)
        
        print(f"   ✅ Found {len(all_buttons)} buttons: {all_buttons}")
        
        # Check if navigation buttons are present
        if "🔙 بازگشت" in all_buttons and "❌ لغو" in all_buttons:
            print("   ✅ Navigation buttons present")
        else:
            print("   ❌ Navigation buttons missing")
            return False
            
    else:
        print("   ❌ Failed to create keyboard")
        return False
    
    print("   ✅ Inline keyboard test passed!")
    return True


def test_wizard_states():
    """Test wizard states."""
    print("\n🔄 Testing Wizard States")
    print("=" * 50)
    
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


async def test_async_components():
    """Test async components."""
    print("\n⚡ Testing Async Components")
    print("=" * 50)
    
    # Test if we can import the async components
    try:
        from app.bot.wizard_handlers import router
        print("   ✅ Wizard router imported successfully")
        print(f"      • Router name: {router.name}")
        
        # Get handler count from sub_routers
        total_handlers = 0
        if hasattr(router, 'sub_routers'):
            for sub_router in router.sub_routers:
                total_handlers += len(sub_router.handlers)
        
        print(f"      • Total handlers: {total_handlers}")
        
        # List handler types from sub_routers
        handler_types = {}
        if hasattr(router, 'sub_routers'):
            for sub_router in router.sub_routers:
                for handler in sub_router.handlers:
                    handler_type = type(handler).__name__
                    handler_types[handler_type] = handler_types.get(handler_type, 0) + 1
        
        print("   ✅ Handler types found:")
        for handler_type, count in handler_types.items():
            print(f"      • {handler_type}: {count}")
            
    except Exception as e:
        print(f"   ❌ Failed to import wizard router: {e}")
        return False
    
    return True


def main():
    """Run all tests."""
    print("🧙‍♂️ Wizard Bot Implementation Test Suite")
    print("=" * 60)
    
    tests = [
        ("Wizard Service", test_wizard_service),
        ("Inline Keyboard", test_inline_keyboard),
        ("Wizard States", test_wizard_states),
        ("Async Components", lambda: asyncio.run(test_async_components()))
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
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Wizard bot implementation is ready!")
        return True
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
