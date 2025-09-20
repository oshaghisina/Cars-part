#!/usr/bin/env python3
"""
Test Bot Commands
Tests the bot commands and callbacks to ensure they work properly.
"""

import asyncio
import sys
import os
from unittest.mock import Mock, AsyncMock

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.bot.bot import dp
from app.bot.wizard_handlers import start_wizard
from aiogram.types import Message, User, Chat, CallbackQuery
from aiogram.fsm.context import FSMContext


def create_mock_user():
    """Create a mock user for testing."""
    return User(
        id=123456789,
        is_bot=False,
        first_name="Test",
        last_name="User",
        username="testuser"
    )


def create_mock_chat():
    """Create a mock chat for testing."""
    return Chat(
        id=123456789,
        type="private",
        first_name="Test",
        last_name="User",
        username="testuser"
    )


def create_mock_message(text="/help"):
    """Create a mock message for testing."""
    return Message(
        message_id=1,
        date=1234567890,
        chat=create_mock_chat(),
        from_user=create_mock_user(),
        content_type="text",
        text=text
    )


def create_mock_callback_query(data="help"):
    """Create a mock callback query for testing."""
    return CallbackQuery(
        id="test_callback_id",
        from_user=create_mock_user(),
        chat_instance="test_chat_instance",
        message=create_mock_message(),
        data=data
    )


async def test_help_command():
    """Test the help command."""
    print("🧪 Testing Help Command...")
    
    try:
        # Find the help command handler
        help_handler = None
        for handler in dp.message.handlers:
            if hasattr(handler, 'filters') and any('help' in str(f) for f in handler.filters):
                help_handler = handler
                break
        
        if not help_handler:
            print("   ❌ Help command handler not found")
            return False
        
        print("   ✅ Help command handler found")
        
        # Test that the handler exists and is callable
        if callable(help_handler.callback):
            print("   ✅ Help command handler is callable")
            return True
        else:
            print("   ❌ Help command handler is not callable")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing help command: {e}")
        return False


async def test_help_callback():
    """Test the help callback."""
    print("\n🧪 Testing Help Callback...")
    
    try:
        # Find the help callback handler
        help_callback_handler = None
        for handler in dp.callback_query.handlers:
            if hasattr(handler, 'filters') and any('help' in str(f) for f in handler.filters):
                help_callback_handler = handler
                break
        
        if not help_callback_handler:
            print("   ❌ Help callback handler not found")
            return False
        
        print("   ✅ Help callback handler found")
        
        # Test that the handler exists and is callable
        if callable(help_callback_handler.callback):
            print("   ✅ Help callback handler is callable")
            return True
        else:
            print("   ❌ Help callback handler is not callable")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing help callback: {e}")
        return False


async def test_wizard_command():
    """Test the wizard command."""
    print("\n🧪 Testing Wizard Command...")
    
    try:
        # Find the wizard command handler
        wizard_handler = None
        for handler in dp.message.handlers:
            if hasattr(handler, 'filters') and any('wizard' in str(f) for f in handler.filters):
                wizard_handler = handler
                break
        
        if not wizard_handler:
            print("   ❌ Wizard command handler not found")
            return False
        
        print("   ✅ Wizard command handler found")
        
        # Test that the handler exists and is callable
        if callable(wizard_handler.callback):
            print("   ✅ Wizard command handler is callable")
            return True
        else:
            print("   ❌ Wizard command handler is not callable")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing wizard command: {e}")
        return False


async def test_wizard_callback():
    """Test the wizard callback."""
    print("\n🧪 Testing Wizard Callback...")
    
    try:
        # Find the wizard callback handler
        wizard_callback_handler = None
        for handler in dp.callback_query.handlers:
            if hasattr(handler, 'filters') and any('start_wizard' in str(f) for f in handler.filters):
                wizard_callback_handler = handler
                break
        
        if not wizard_callback_handler:
            print("   ❌ Wizard callback handler not found")
            return False
        
        print("   ✅ Wizard callback handler found")
        
        # Test that the handler exists and is callable
        if callable(wizard_callback_handler.callback):
            print("   ✅ Wizard callback handler is callable")
            return True
        else:
            print("   ❌ Wizard callback handler is not callable")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing wizard callback: {e}")
        return False


async def test_wizard_handlers_import():
    """Test that wizard handlers can be imported."""
    print("\n🧪 Testing Wizard Handlers Import...")
    
    try:
        from app.bot.wizard_handlers import router as wizard_router
        print("   ✅ Wizard router imported successfully")
        
        # Test that the router has handlers
        if hasattr(wizard_router, 'handlers'):
            print(f"   ✅ Wizard router has {len(wizard_router.handlers)} handlers")
            return True
        else:
            print("   ❌ Wizard router has no handlers")
            return False
            
    except Exception as e:
        print(f"   ❌ Error importing wizard handlers: {e}")
        return False


async def main():
    """Run all bot command tests."""
    print("🤖 Bot Commands Test Suite")
    print("=" * 50)
    
    tests = [
        ("Help Command", test_help_command),
        ("Help Callback", test_help_callback),
        ("Wizard Command", test_wizard_command),
        ("Wizard Callback", test_wizard_callback),
        ("Wizard Handlers Import", test_wizard_handlers_import)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} Test...")
        try:
            result = await test_func()
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
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All bot command tests passed!")
        print("📱 The bot commands should work properly in Telegram!")
        return True
    else:
        print("⚠️  Some bot command tests failed.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
