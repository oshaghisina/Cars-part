#!/usr/bin/env python3
"""
Debug script to identify OTP SMS issues.
"""

import asyncio
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.core.config import settings
from app.db.database import get_db
from app.services.sms_service import SMSService
from app.services.otp_service import OTPService


async def debug_otp_issue():
    """Debug OTP SMS configuration and functionality."""
    print("🔍 Debugging OTP SMS Issue")
    print("=" * 50)
    
    # Check configuration
    print(f"📋 Configuration:")
    print(f"  SMS Enabled: {settings.sms_enabled}")
    print(f"  Melipayamak Username: {settings.melipayamak_username}")
    print(f"  Melipayamak Password: {'*' * len(settings.melipayamak_password) if settings.melipayamak_password != 'CHANGEME' else 'CHANGEME'}")
    print(f"  SMS Sender Number: {settings.sms_sender_number}")
    print()
    
    # Test database connection
    print("🗄️  Database Connection:")
    try:
        db = next(get_db())
        print("  ✅ Database connection successful")
    except Exception as e:
        print(f"  ❌ Database connection failed: {e}")
        return
    print()
    
    # Test SMS service initialization
    print("📱 SMS Service:")
    try:
        sms_service = SMSService(db)
        if sms_service.api:
            print("  ✅ SMS service initialized successfully")
        else:
            print("  ❌ SMS service not initialized (API is None)")
            print("  💡 This is likely the cause of the 500 error")
    except Exception as e:
        print(f"  ❌ SMS service initialization failed: {e}")
        print(f"  💡 This is likely the cause of the 500 error")
    print()
    
    # Test OTP service
    print("🔐 OTP Service:")
    try:
        otp_service = OTPService(db)
        print("  ✅ OTP service initialized successfully")
        
        # Test OTP request (this will fail but show the error)
        print("  🧪 Testing OTP request...")
        result = await otp_service.request_otp("+989123456789", "login")
        print(f"  📊 OTP request result: {result}")
        
    except Exception as e:
        print(f"  ❌ OTP service test failed: {e}")
        import traceback
        traceback.print_exc()
    print()
    
    # Check dependencies
    print("📦 Dependencies:")
    try:
        import melipayamak
        print("  ✅ melipayamak package is installed")
    except ImportError:
        print("  ❌ melipayamak package is NOT installed")
        print("  💡 Install with: pip install melipayamak")
    print()
    
    print("🎯 Recommendations:")
    if settings.melipayamak_username == "CHANGEME":
        print("  1. Configure SMS credentials in environment variables")
        print("     - MELIPAYAMAK_USERNAME=your_username")
        print("     - MELIPAYAMAK_PASSWORD=your_password")
        print("     - SMS_SENDER_NUMBER=your_sender_number")
    else:
        print("  1. SMS credentials are configured")
    
    try:
        import melipayamak
        print("  2. melipayamak package is available")
    except ImportError:
        print("  2. Install melipayamak: pip install melipayamak")
    
    print("  3. Deploy the latest code to production server")
    print("  4. Check production server logs for detailed error messages")


if __name__ == "__main__":
    asyncio.run(debug_otp_issue())
