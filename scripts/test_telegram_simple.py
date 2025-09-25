#!/usr/bin/env python3
"""
Simple test for Telegram SSO without API calls.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.config import settings
from app.db.database import SessionLocal
from app.services.telegram_service import TelegramService
from app.models.telegram_models import TelegramUser

def test_telegram_simple():
    """Test Telegram service without API calls."""
    print("🧪 Testing Telegram SSO Service (Simple)...\n")
    
    try:
        # Test database connection
        print("1. Testing database connection...")
        db = SessionLocal()
        print("   ✅ Database connection successful")
        
        # Test Telegram service initialization
        print("\n2. Testing Telegram service initialization...")
        telegram_service = TelegramService(db)
        print("   ✅ Telegram service initialized")
        
        # Test Telegram user creation without API call
        print("\n3. Testing Telegram user creation (no API)...")
        telegram_user = telegram_service.get_or_create_telegram_user(
            telegram_id=176007160,
            user_info={
                "username": "test_user",
                "first_name": "Test",
                "last_name": "User",
                "language_code": "en"
            }
        )
        print(f"   ✅ Telegram user created: ID {telegram_user.id}")
        
        # Test link token creation
        print("\n4. Testing link token creation...")
        link_token = telegram_service.create_link_token(
            telegram_user=telegram_user,
            action="link_account"
        )
        print(f"   ✅ Link token created: {link_token.token[:20]}...")
        
        # Test stats
        print("\n5. Testing stats...")
        stats = telegram_service.get_telegram_stats()
        print(f"   ✅ Stats: {stats}")
        
        db.close()
        print("\n🎉 All Telegram service tests passed!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_telegram_simple()
