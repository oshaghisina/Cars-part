#!/usr/bin/env python3
"""
Test Melipayamak API to get account information
"""

import os
import sys

# Add the project root to Python path
sys.path.append('/Users/sinaoshaghi/Projects/China Car Parts')

def test_api_info():
    """Test API key and get account information"""
    
    try:
        from melipayamak import Api
        
        # Your API key
        api_key = "59a3a4a7-b8fe-422c-be38-e07ebec590c6"
        
        print(f"🔑 Testing API key: {api_key[:8]}...")
        
        # Initialize API
        api = Api(username=api_key, password=api_key)
        print("✅ API initialized successfully")
        
        # Try to get account information
        try:
            print("\n📊 Trying to get account information...")
            # Some Melipayamak APIs have a getInfo or getCredit method
            if hasattr(api, 'getInfo'):
                info = api.getInfo()
                print(f"Account Info: {info}")
            elif hasattr(api, 'getCredit'):
                credit = api.getCredit()
                print(f"Account Credit: {credit}")
            else:
                print("No account info methods available")
        except Exception as e:
            print(f"Could not get account info: {e}")
        
        # Try to get sender numbers
        try:
            print("\n📤 Trying to get sender numbers...")
            if hasattr(api, 'getSenders'):
                senders = api.getSenders()
                print(f"Available Senders: {senders}")
            else:
                print("No getSenders method available")
        except Exception as e:
            print(f"Could not get senders: {e}")
        
        # Try to get credit balance
        try:
            print("\n💰 Trying to get credit balance...")
            if hasattr(api, 'getCredit'):
                credit = api.getCredit()
                print(f"Credit Balance: {credit}")
            else:
                print("No getCredit method available")
        except Exception as e:
            print(f"Could not get credit: {e}")
        
        # List all available methods
        print(f"\n🔍 Available methods in API object:")
        methods = [method for method in dir(api) if not method.startswith('_')]
        for method in methods:
            print(f"  - {method}")
            
        # List all available methods in SMS client
        sms_client = api.sms()
        print(f"\n📱 Available methods in SMS client:")
        sms_methods = [method for method in dir(sms_client) if not method.startswith('_')]
        for method in sms_methods:
            print(f"  - {method}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api_info()
