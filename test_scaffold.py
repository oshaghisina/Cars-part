#!/usr/bin/env python3
"""
Test script to verify the scaffold is working correctly.
"""

import sys
import os

def test_imports():
    """Test that all modules can be imported."""
    print("🧪 Testing imports...")
    
    try:
        # Test core config
        from app.core.config import settings
        print("✅ Core config imports successfully")
        
        # Test database
        from app.db.database import engine, Base
        print("✅ Database imports successfully")
        
        # Test models
        from app.db.models import Part, Price, Lead, Order
        print("✅ Database models import successfully")
        
        # Test API
        from app.api.main import app
        print("✅ FastAPI app imports successfully")
        
        # Test bot (with graceful error handling)
        from app.bot.bot import bot, dp
        print("✅ Telegram bot imports successfully")
        
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_config():
    """Test configuration loading."""
    print("\n🔧 Testing configuration...")
    
    try:
        from app.core.config import settings
        
        print(f"✅ App environment: {settings.app_env}")
        print(f"✅ Debug mode: {settings.debug}")
        print(f"✅ Database URL: {settings.database_url}")
        print(f"✅ AI enabled: {settings.ai_enabled}")
        print(f"✅ Admin IDs: {settings.admin_telegram_ids_list}")
        
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_fastapi():
    """Test FastAPI application."""
    print("\n🚀 Testing FastAPI...")
    
    try:
        from app.api.main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        # Test health endpoint
        response = client.get("/health")
        if response.status_code == 200:
            print("✅ Health endpoint working")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
        
        # Test root endpoint
        response = client.get("/")
        if response.status_code == 200:
            print("✅ Root endpoint working")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ FastAPI test failed: {e}")
        return False

def test_bot():
    """Test bot initialization."""
    print("\n🤖 Testing Telegram bot...")
    
    try:
        from app.bot.bot import bot, dp
        
        if bot is None:
            print("⚠️  Bot not initialized (invalid token - expected)")
            print("✅ Bot handles invalid token gracefully")
            return True
        else:
            print("✅ Bot initialized successfully")
            return True
    except Exception as e:
        print(f"❌ Bot test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🎯 Chinese Auto Parts Price Bot - Scaffold Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_config,
        test_fastapi,
        test_bot
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Scaffold is ready for development.")
        print("\n📋 Next steps:")
        print("1. Set a valid TELEGRAM_BOT_TOKEN in .env file")
        print("2. Run: uvicorn app.api.main:app --reload")
        print("3. Run: python -m app.bot.bot")
        print("4. Visit: http://localhost:8000/docs")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
