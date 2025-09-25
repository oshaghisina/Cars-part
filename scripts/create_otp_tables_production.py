#!/usr/bin/env python3
"""
Create OTP-related tables for production server.
This script creates the necessary tables for OTP functionality.
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, project_root)

from app.db.database import engine, Base
from app.models.otp_models import OTPCode, RateLimit, PhoneVerification
from app.models.telegram_models import TelegramUser, TelegramLinkToken, TelegramBotSession, TelegramDeepLink
from app.models.sms_models import SMSLog, SMSTemplate, StockAlert

def create_otp_tables():
    """Create OTP-related tables."""
    print("🔧 Creating OTP-related tables...")
    
    # Show database configuration
    from app.core.config import settings
    print(f"📊 Database URL: {settings.database_url}")
    print(f"🌍 Environment: {settings.app_env}")
    print()
    
    try:
        # Check if tables already exist
        from sqlalchemy import inspect
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        print("🔍 Checking existing tables...")
        required_tables = [
            'otp_codes', 'rate_limits', 'phone_verifications',
            'telegram_users', 'telegram_link_tokens', 'telegram_bot_sessions', 
            'telegram_deep_links', 'sms_logs', 'sms_templates', 'stock_alerts'
        ]
        
        missing_tables = [table for table in required_tables if table not in existing_tables]
        
        if not missing_tables:
            print("✅ All required tables already exist!")
            return True
            
        print(f"📋 Missing tables: {', '.join(missing_tables)}")
        print()
        
        # Create all tables
        print("🏗️  Creating missing tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ OTP tables created successfully!")
        
        # Verify tables were created
        inspector = inspect(engine)
        new_tables = inspector.get_table_names()
        created_tables = [table for table in required_tables if table in new_tables]
        
        print(f"\n📋 Successfully created/verified tables:")
        for table in created_tables:
            print(f"  ✅ {table}")
        
        print("\n🎯 Next steps:")
        print("  1. Test OTP functionality")
        print("  2. Run: curl -X GET http://your-server/api/v1/otp/health")
        print("  3. Test OTP request endpoint")
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = create_otp_tables()
    sys.exit(0 if success else 1)
