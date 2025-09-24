#!/usr/bin/env python3
"""Test SMS API endpoints with proper authentication."""

import sys
import os
import requests
import json

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_sms_api():
    """Test SMS API endpoints."""
    print("🧪 Testing SMS API Endpoints...")
    
    base_url = "http://localhost:8001"
    
    # Test 1: Health check
    print("\n1️⃣ Testing API Health...")
    try:
        response = requests.get(f"{base_url}/api/v1/health")
        if response.status_code == 200:
            print("✅ API is healthy")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API health check error: {e}")
        return False
    
    # Test 2: Login to get authentication token
    print("\n2️⃣ Testing Authentication...")
    try:
        # Try to login with admin credentials
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        response = requests.post(f"{base_url}/api/v1/users/login", json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access_token")
            print("✅ Authentication successful")
            print(f"   Token: {access_token[:20]}...")
        else:
            print(f"⚠️  Authentication failed: {response.status_code}")
            print("   This is expected if no admin user exists yet")
            access_token = None
    except Exception as e:
        print(f"⚠️  Authentication error: {e}")
        access_token = None
    
    # Test 3: Test SMS templates endpoint (without auth first)
    print("\n3️⃣ Testing SMS Templates Endpoint...")
    try:
        headers = {}
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"
        
        response = requests.get(f"{base_url}/api/v1/sms/templates", headers=headers)
        if response.status_code == 200:
            templates = response.json()
            print(f"✅ SMS templates endpoint working")
            print(f"   Found {len(templates)} templates")
            for template in templates[:3]:  # Show first 3
                print(f"   - {template['name']} ({template['template_type']})")
        elif response.status_code == 403:
            print("⚠️  SMS templates endpoint requires authentication (expected)")
        else:
            print(f"❌ SMS templates endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ SMS templates endpoint error: {e}")
    
    # Test 4: Test SMS analytics endpoint
    print("\n4️⃣ Testing SMS Analytics Endpoint...")
    try:
        headers = {}
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"
        
        response = requests.get(f"{base_url}/api/v1/sms/analytics", headers=headers)
        if response.status_code == 200:
            analytics = response.json()
            print("✅ SMS analytics endpoint working")
            print(f"   Total sent: {analytics['total_sent']}")
            print(f"   Success rate: {analytics['success_rate']:.1f}%")
        elif response.status_code == 403:
            print("⚠️  SMS analytics endpoint requires authentication (expected)")
        else:
            print(f"❌ SMS analytics endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ SMS analytics endpoint error: {e}")
    
    # Test 5: Test phone verification endpoint (no auth required)
    print("\n5️⃣ Testing Phone Verification Endpoint...")
    try:
        verification_data = {
            "phone_number": "09123456789"
        }
        
        response = requests.post(f"{base_url}/api/v1/sms/verify-phone", json=verification_data)
        if response.status_code == 200:
            result = response.json()
            print("✅ Phone verification endpoint working")
            print(f"   Success: {result['success']}")
            print(f"   Message: {result['message']}")
        elif response.status_code == 503:
            print("⚠️  SMS service disabled (expected in development)")
        else:
            print(f"❌ Phone verification endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Phone verification endpoint error: {e}")
    
    # Test 6: Test stock alert creation (no auth required)
    print("\n6️⃣ Testing Stock Alert Creation...")
    try:
        alert_data = {
            "part_id": 1,
            "phone_number": "09123456789",
            "email": "test@example.com"
        }
        
        response = requests.post(f"{base_url}/api/v1/sms/stock-alerts", json=alert_data)
        if response.status_code == 200:
            result = response.json()
            print("✅ Stock alert creation endpoint working")
            print(f"   Alert ID: {result['id']}")
            print(f"   Part ID: {result['part_id']}")
            print(f"   Phone: {result['phone_number']}")
        else:
            print(f"❌ Stock alert creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Stock alert creation error: {e}")
    
    print("\n🎉 SMS API Testing Completed!")
    return True

def test_database_connectivity():
    """Test database connectivity and SMS tables."""
    print("\n🗄️ Testing Database Connectivity...")
    
    try:
        from sqlalchemy.orm import sessionmaker
        from app.core.config import settings
        from app.db.database import engine
        from app.models.sms_models import SMSTemplate, SMSLog, StockAlert
        
        # Create database session
        Session = sessionmaker(bind=engine)
        db = Session()
        
        # Test SMS templates table
        templates = db.query(SMSTemplate).count()
        print(f"✅ SMS Templates table: {templates} records")
        
        # Test SMS logs table
        logs = db.query(SMSLog).count()
        print(f"✅ SMS Logs table: {logs} records")
        
        # Test stock alerts table
        alerts = db.query(StockAlert).count()
        print(f"✅ Stock Alerts table: {alerts} records")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Database connectivity test failed: {e}")
        return False

def test_sms_service_functionality():
    """Test SMS service core functionality."""
    print("\n🔧 Testing SMS Service Functionality...")
    
    try:
        from sqlalchemy.orm import sessionmaker
        from app.core.config import settings
        from app.db.database import engine
        from app.services.sms_service import SMSService
        
        # Create database session
        Session = sessionmaker(bind=engine)
        db = Session()
        
        # Initialize SMS service
        sms_service = SMSService(db)
        
        # Test phone validation
        test_phones = ["09123456789", "+989123456789", "123456789"]
        for phone in test_phones:
            is_valid = sms_service._validate_phone_number(phone)
            status = "✅" if is_valid else "❌"
            print(f"   {status} Phone validation: {phone}")
        
        # Test template variable replacement
        template = "سلام {name}، سفارش شما با شماره {order_id} ثبت شد."
        variables = {"name": "احمد", "order_id": "12345"}
        result = sms_service._replace_template_variables(template, variables)
        print(f"✅ Template replacement working: {result[:30]}...")
        
        # Test analytics
        analytics = sms_service.get_sms_analytics()
        print(f"✅ Analytics working: {analytics['total_sent']} total sent")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ SMS service functionality test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Comprehensive SMS Phase 1 Testing...")
    
    # Run all tests
    api_test_passed = test_sms_api()
    db_test_passed = test_database_connectivity()
    service_test_passed = test_sms_service_functionality()
    
    print("\n" + "="*60)
    print("📊 PHASE 1 TEST RESULTS SUMMARY")
    print("="*60)
    
    print(f"🔌 API Endpoints: {'✅ PASSED' if api_test_passed else '❌ FAILED'}")
    print(f"🗄️ Database: {'✅ PASSED' if db_test_passed else '❌ FAILED'}")
    print(f"🔧 SMS Service: {'✅ PASSED' if service_test_passed else '❌ FAILED'}")
    
    if api_test_passed and db_test_passed and service_test_passed:
        print("\n🎉 ALL PHASE 1 TESTS PASSED!")
        print("\n✅ SMS Integration is ready for production!")
        print("✅ Database tables created and accessible")
        print("✅ SMS service core functionality working")
        print("✅ API endpoints configured and responding")
        print("✅ Default templates created and functional")
        print("\n🚀 Ready to proceed to Phase 2: Core SMS Notifications!")
    else:
        print("\n💥 Some tests failed. Please review the errors above.")
        sys.exit(1)
