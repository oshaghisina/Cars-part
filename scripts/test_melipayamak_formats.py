#!/usr/bin/env python3
"""
Test different formats for Melipayamak API
"""

import os
import sys

# Add the project root to Python path
sys.path.append('/Users/sinaoshaghi/Projects/China Car Parts')

def test_different_formats():
    """Test different phone number and sender formats"""
    
    try:
        from melipayamak import Api
        
        # Your API key
        api_key = "59a3a4a7-b8fe-422c-be38-e07ebec590c6"
        
        print(f"🔑 Testing different formats with API key: {api_key[:8]}...")
        
        # Initialize API
        api = Api(username=api_key, password=api_key)
        sms_client = api.sms()
        
        # Test different phone number formats
        phone_formats = [
            "+989335540052",  # International format
            "989335540052",   # Without +
            "09335540052",    # Iranian format
            "9335540052"      # Without leading 0
        ]
        
        # Test different sender numbers
        sender_formats = [
            "5000",           # Short format
            "50004000",       # Common format
            "10008663",       # Another common format
            "30008663",       # Another format
            "2000500666"      # Another format
        ]
        
        message = "Test SMS"
        
        for phone in phone_formats:
            for sender in sender_formats:
                print(f"\n📱 Testing: {phone} from {sender}")
                
                try:
                    response = sms_client.send(
                        to=phone,
                        _from=sender,
                        text=message
                    )
                    
                    print(f"📊 Response: {response}")
                    
                    if response and response.get("Status") == "Success":
                        print("🎉 SUCCESS!")
                        return phone, sender, response
                    else:
                        error = response.get("StrRetStatus", "Unknown") if response else "No response"
                        print(f"❌ Failed: {error}")
                        
                except Exception as e:
                    print(f"❌ Exception: {e}")
                    
        print("\n❌ All format combinations failed")
        return None, None, None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None, None, None

if __name__ == "__main__":
    test_different_formats()
