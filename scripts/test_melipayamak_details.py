#!/usr/bin/env python3
"""
Test Melipayamak API to get detailed information
"""

import os
import sys

# Add the project root to Python path
sys.path.append('/Users/sinaoshaghi/Projects/China Car Parts')

def test_api_details():
    """Test API key and get detailed information"""
    
    try:
        from melipayamak import Api
        
        # Your API key
        api_key = "59a3a4a7-b8fe-422c-be38-e07ebec590c6"
        
        print(f"🔑 Testing API key: {api_key[:8]}...")
        
        # Initialize API
        api = Api(username=api_key, password=api_key)
        sms_client = api.sms()
        
        # Test get_credit
        try:
            print("\n💰 Getting credit balance...")
            credit = sms_client.get_credit()
            print(f"Credit Response: {credit}")
        except Exception as e:
            print(f"Credit error: {e}")
        
        # Test get_numbers (sender numbers)
        try:
            print("\n📤 Getting sender numbers...")
            numbers = sms_client.get_numbers()
            print(f"Numbers Response: {numbers}")
        except Exception as e:
            print(f"Numbers error: {e}")
        
        # Test get_base_price
        try:
            print("\n💵 Getting base price...")
            price = sms_client.get_base_price()
            print(f"Price Response: {price}")
        except Exception as e:
            print(f"Price error: {e}")
        
        # Test get_data
        try:
            print("\n📊 Getting account data...")
            data = sms_client.get_data()
            print(f"Data Response: {data}")
        except Exception as e:
            print(f"Data error: {e}")
        
        # Test get_messages
        try:
            print("\n📨 Getting recent messages...")
            messages = sms_client.get_messages()
            print(f"Messages Response: {messages}")
        except Exception as e:
            print(f"Messages error: {e}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api_details()
