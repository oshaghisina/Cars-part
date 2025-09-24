#!/usr/bin/env python3
"""
Test Melipayamak API with correct credentials
"""

import os
import sys

# Add the project root to Python path
sys.path.append('/Users/sinaoshaghi/Projects/China Car Parts')

def test_correct_credentials():
    """Test Melipayamak API with correct username and password"""
    
    try:
        from melipayamak import Api
        
        # Correct credentials
        username = "9335540052"  # Phone number as username
        password = "59a3a4a7-b8fe-422c-be38-e07ebec590c6"  # API key as password
        
        print(f"🔑 Testing with correct credentials:")
        print(f"   Username: {username}")
        print(f"   Password: {password[:8]}...")
        
        # Initialize API
        api = Api(username=username, password=password)
        sms_client = api.sms()
        
        # Test get_credit first
        try:
            print("\n💰 Getting credit balance...")
            credit = sms_client.get_credit()
            print(f"Credit Response: {credit}")
            
            if credit.get("RetStatus") == 1:
                print("✅ Authentication successful!")
                print(f"💰 Available credit: {credit.get('Value', 'N/A')}")
            else:
                print(f"❌ Authentication failed: {credit.get('StrRetStatus', 'Unknown error')}")
                return
                
        except Exception as e:
            print(f"Credit error: {e}")
            return
        
        # Test get_numbers (sender numbers)
        try:
            print("\n📤 Getting sender numbers...")
            numbers = sms_client.get_numbers()
            print(f"Numbers Response: {numbers}")
            
            # Extract available sender numbers
            if numbers.get("MyBase", {}).get("RetStatus") == 1:
                available_numbers = numbers.get("Data", [])
                print(f"Available sender numbers: {available_numbers}")
                
                if available_numbers:
                    sender_number = available_numbers[0].get("Number", "5000")
                    print(f"Using sender number: {sender_number}")
                else:
                    print("No sender numbers available, using default")
                    sender_number = "5000"
            else:
                print("Could not get sender numbers, using default")
                sender_number = "5000"
                
        except Exception as e:
            print(f"Numbers error: {e}")
            sender_number = "5000"
        
        # Test sending SMS
        phone_number = "+989335540052"
        message = "Test SMS with correct credentials!"
        
        print(f"\n📱 Sending SMS to {phone_number}")
        print(f"📝 Message: {message}")
        print(f"📤 From: {sender_number}")
        
        response = sms_client.send(
            to=phone_number,
            _from=sender_number,
            text=message
        )
        
        print(f"📊 Response: {response}")
        
        if response and response.get("RetStatus") == 1:
            print("🎉 SMS sent successfully!")
            print(f"Message ID: {response.get('Value', 'N/A')}")
        else:
            error = response.get("StrRetStatus", "Unknown error") if response else "No response"
            print(f"❌ SMS failed: {error}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_correct_credentials()
