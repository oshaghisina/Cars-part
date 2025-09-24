#!/usr/bin/env python3
"""
SMS Testing Script - Test SMS functionality with different scenarios
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8001"
TEST_PHONE_NUMBER = "+989123456789"  # Replace with your test phone number

def test_sms_endpoints():
    """Test all SMS-related endpoints"""
    print("🧪 Testing SMS Endpoints")
    print("=" * 50)
    
    # Test 1: List SMS Templates
    print("\n1️⃣ Testing SMS Templates...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/sms/templates")
        if response.status_code == 200:
            templates = response.json()
            print(f"✅ Found {len(templates)} SMS templates")
            for template in templates:
                print(f"   - {template['name']}: {template['template_type']}")
        else:
            print(f"❌ Failed to get templates: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting templates: {e}")
    
    # Test 2: Send Phone Verification SMS
    print(f"\n2️⃣ Testing Phone Verification SMS to {TEST_PHONE_NUMBER}...")
    try:
        verification_data = {
            "phone_number": TEST_PHONE_NUMBER,
            "template_name": "phone_verification",
            "variables": {
                "verification_code": "123456"
            }
        }
        response = requests.post(
            f"{API_BASE_URL}/api/v1/sms/verify-phone",
            json=verification_data
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Verification SMS sent: {result}")
        else:
            print(f"❌ Failed to send verification SMS: {response.text}")
    except Exception as e:
        print(f"❌ Error sending verification SMS: {e}")
    
    # Test 3: Send Order Confirmation SMS
    print(f"\n3️⃣ Testing Order Confirmation SMS to {TEST_PHONE_NUMBER}...")
    try:
        order_data = {
            "phone_number": TEST_PHONE_NUMBER,
            "template_name": "order_confirmation",
            "variables": {
                "order_id": "ORD-2024-001",
                "total_amount": "1,250,000",
                "delivery_time": "2-3 business days"
            }
        }
        response = requests.post(
            f"{API_BASE_URL}/api/v1/sms/send",
            json=order_data
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Order confirmation SMS sent: {result}")
        else:
            print(f"❌ Failed to send order SMS: {response.text}")
    except Exception as e:
        print(f"❌ Error sending order SMS: {e}")
    
    # Test 4: Send Stock Alert SMS
    print(f"\n4️⃣ Testing Stock Alert SMS to {TEST_PHONE_NUMBER}...")
    try:
        stock_data = {
            "phone_number": TEST_PHONE_NUMBER,
            "template_name": "stock_alert",
            "variables": {
                "part_name": "Brake Pad Set",
                "brand": "Brembo",
                "product_url": "https://chinaautoparts.com/part/14"
            }
        }
        response = requests.post(
            f"{API_BASE_URL}/api/v1/sms/send",
            json=stock_data
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Stock alert SMS sent: {result}")
        else:
            print(f"❌ Failed to send stock alert: {response.text}")
    except Exception as e:
        print(f"❌ Error sending stock alert: {e}")
    
    # Test 5: Create Stock Alert Subscription
    print(f"\n5️⃣ Testing Stock Alert Subscription for {TEST_PHONE_NUMBER}...")
    try:
        subscription_data = {
            "phone_number": TEST_PHONE_NUMBER,
            "part_id": 14,
            "user_id": None  # Guest user
        }
        response = requests.post(
            f"{API_BASE_URL}/api/v1/sms/stock-alerts",
            json=subscription_data
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Stock alert subscription created: {result}")
        else:
            print(f"❌ Failed to create subscription: {response.text}")
    except Exception as e:
        print(f"❌ Error creating subscription: {e}")
    
    # Test 6: Get SMS Analytics
    print(f"\n6️⃣ Testing SMS Analytics...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/sms/analytics")
        if response.status_code == 200:
            analytics = response.json()
            print(f"✅ SMS Analytics: {analytics}")
        else:
            print(f"❌ Failed to get analytics: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting analytics: {e}")

def test_custom_sms():
    """Test sending a custom SMS message"""
    print(f"\n🎯 Testing Custom SMS to {TEST_PHONE_NUMBER}...")
    
    custom_data = {
        "phone_number": TEST_PHONE_NUMBER,
        "message": "This is a test SMS from China Car Parts API! 🚗",
        "template_name": None  # Custom message
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/sms/send",
            json=custom_data
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Custom SMS sent: {result}")
        else:
            print(f"❌ Failed to send custom SMS: {response.text}")
    except Exception as e:
        print(f"❌ Error sending custom SMS: {e}")

def main():
    """Main testing function"""
    global TEST_PHONE_NUMBER
    
    print("📱 SMS Testing Script")
    print("=" * 50)
    print(f"API Base URL: {API_BASE_URL}")
    print(f"Test Phone Number: {TEST_PHONE_NUMBER}")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if phone number is provided as argument
    if len(sys.argv) > 1:
        TEST_PHONE_NUMBER = sys.argv[1]
        print(f"Using provided phone number: {TEST_PHONE_NUMBER}")
    
    # Run tests
    test_sms_endpoints()
    test_custom_sms()
    
    print("\n" + "=" * 50)
    print("🏁 SMS Testing Complete!")
    print("\n📝 Notes:")
    print("- SMS service is currently in 'test mode' (not sending real SMS)")
    print("- To enable real SMS sending, configure Melipayamak credentials")
    print("- Check the SMS logs in the database for sent messages")
    print("- Use the admin panel to view SMS analytics and logs")

if __name__ == "__main__":
    main()
