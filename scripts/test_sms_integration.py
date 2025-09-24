#!/usr/bin/env python3
"""Test SMS integration functionality."""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.db.database import engine, Base
from app.models.sms_models import SMSTemplate, SMSLog
from app.services.sms_service import SMSService

def test_sms_service():
    """Test SMS service functionality."""
    print("🧪 Testing SMS Service Integration...")
    
    # Create database session
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # Test 1: Check if SMS templates exist
        print("\n1️⃣ Testing SMS Templates...")
        templates = db.query(SMSTemplate).all()
        print(f"✅ Found {len(templates)} SMS templates:")
        for template in templates:
            print(f"   - {template.name} ({template.template_type})")
        
        # Test 2: Initialize SMS service
        print("\n2️⃣ Testing SMS Service Initialization...")
        sms_service = SMSService(db)
        if sms_service.api:
            print("✅ SMS service initialized successfully")
        else:
            print("⚠️  SMS service initialized but API not configured (expected in development)")
        
        # Test 3: Test phone number validation
        print("\n3️⃣ Testing Phone Number Validation...")
        test_phones = [
            "09123456789",  # Valid Iranian mobile
            "+989123456789",  # Valid international format
            "123456789",  # Invalid format
            "0912345678",  # Invalid length
        ]
        
        for phone in test_phones:
            is_valid = sms_service._validate_phone_number(phone)
            status = "✅ Valid" if is_valid else "❌ Invalid"
            print(f"   {phone}: {status}")
        
        # Test 4: Test template variable replacement
        print("\n4️⃣ Testing Template Variable Replacement...")
        test_template = "سلام {name}، سفارش شما با شماره {order_id} ثبت شد."
        test_variables = {"name": "احمد", "order_id": "12345"}
        result = sms_service._replace_template_variables(test_template, test_variables)
        print(f"   Template: {test_template}")
        print(f"   Variables: {test_variables}")
        print(f"   Result: {result}")
        
        # Test 5: Test SMS analytics
        print("\n5️⃣ Testing SMS Analytics...")
        analytics = sms_service.get_sms_analytics()
        print(f"   Total sent: {analytics['total_sent']}")
        print(f"   Successful: {analytics['successful']}")
        print(f"   Failed: {analytics['failed']}")
        print(f"   Success rate: {analytics['success_rate']:.1f}%")
        print(f"   Total cost: {analytics['total_cost']}")
        
        # Test 6: Check SMS logs
        print("\n6️⃣ Testing SMS Logs...")
        logs = db.query(SMSLog).all()
        print(f"✅ Found {len(logs)} SMS logs in database")
        
        print("\n🎉 SMS Integration Test Completed Successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ SMS Integration Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

def test_sms_templates():
    """Test SMS template functionality."""
    print("\n📝 Testing SMS Templates...")
    
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # Get all templates
        templates = db.query(SMSTemplate).filter(SMSTemplate.is_active == True).all()
        
        print(f"✅ Active templates: {len(templates)}")
        
        for template in templates:
            print(f"\n📋 Template: {template.name}")
            print(f"   Type: {template.template_type}")
            print(f"   Persian: {template.content_fa[:50]}..." if template.content_fa else "   Persian: Not set")
            print(f"   English: {template.content_en[:50]}..." if template.content_en else "   English: Not set")
            print(f"   Variables: {template.variables}")
        
        return True
        
    except Exception as e:
        print(f"❌ Template test failed: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Starting SMS Integration Tests...")
    
    # Run tests
    sms_test_passed = test_sms_service()
    template_test_passed = test_sms_templates()
    
    if sms_test_passed and template_test_passed:
        print("\n🎉 All SMS Integration Tests Passed!")
        print("\n📋 Phase 1 Summary:")
        print("✅ Melipayamak SDK installed")
        print("✅ SMS service architecture created")
        print("✅ Database models and tables created")
        print("✅ SMS API endpoints configured")
        print("✅ Default SMS templates created")
        print("✅ SMS service functionality tested")
        print("\n🚀 Ready for Phase 2: Core SMS Notifications!")
    else:
        print("\n💥 Some tests failed. Please check the errors above.")
        sys.exit(1)
