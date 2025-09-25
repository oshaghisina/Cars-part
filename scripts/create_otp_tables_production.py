#!/usr/bin/env python3
"""
Create OTP-related tables for production server.
This script creates the necessary tables for OTP functionality.
"""

import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from app.db.database import engine, Base
from app.models.otp_models import OTPCode, RateLimit, PhoneVerification
from app.models.telegram_models import TelegramUser, TelegramLinkToken, TelegramBotSession, TelegramDeepLink
from app.models.sms_models import SMSLog, SMSTemplate, StockAlert

def create_otp_tables():
    """Create OTP-related tables."""
    print("🔧 Creating OTP-related tables...")
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ OTP tables created successfully!")
        
        # List created tables
        print("\n📋 Created tables:")
        print("  - otp_codes")
        print("  - rate_limits") 
        print("  - phone_verifications")
        print("  - telegram_users")
        print("  - telegram_link_tokens")
        print("  - telegram_bot_sessions")
        print("  - telegram_deep_links")
        print("  - sms_logs")
        print("  - sms_templates")
        print("  - stock_alerts")
        
        print("\n🎯 Next steps:")
        print("  1. Deploy this script to production server")
        print("  2. Run: python scripts/create_otp_tables_production.py")
        print("  3. Test OTP functionality")
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = create_otp_tables()
    sys.exit(0 if success else 1)
