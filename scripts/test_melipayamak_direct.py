#!/usr/bin/env python3
"""
Direct test of Melipayamak API to debug SMS issues
"""

import os
import sys

# Add the project root to Python path
sys.path.append('/Users/sinaoshaghi/Projects/China Car Parts')

def test_melipayamak_direct():
    """Test Melipayamak API directly"""
    
    try:
        from melipayamak import Api
        
        # Your API key
        api_key = "59a3a4a7-b8fe-422c-be38-e07ebec590c6"
        
        print(f"🔑 Testing Melipayamak API with key: {api_key[:8]}...")
        
        # Initialize API
        api = Api(username=api_key, password=api_key)
        print("✅ API initialized successfully")
        
        # Test SMS client
        sms_client = api.sms()
        print("✅ SMS client created successfully")
        
        # Test sending SMS
        phone_number = "+989335540052"
        message = "Test from direct API call"
        sender_number = "5000..."  # You might need to change this
        
        print(f"📱 Attempting to send SMS to {phone_number}")
        print(f"📝 Message: {message}")
        print(f"📤 From: {sender_number}")
        
        response = sms_client.send(
            to=phone_number,
            _from=sender_number,
            text=message
        )
        
        print(f"📊 Response: {response}")
        
        if response and response.get("Status") == "Success":
            print("🎉 SMS sent successfully!")
            print(f"Message ID: {response.get('Value', 'N/A')}")
        else:
            print("❌ SMS failed")
            print(f"Error: {response.get('Message', 'Unknown error') if response else 'No response'}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_melipayamak_direct()
