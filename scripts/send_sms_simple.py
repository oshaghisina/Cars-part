#!/usr/bin/env python3
"""
Simple SMS Sending Script - Send SMS to a phone number
Usage: python send_sms_simple.py <phone_number> [message]
"""

import requests
import json
import sys

API_BASE_URL = "http://localhost:8001"

def send_sms(phone_number, message="Test SMS from China Car Parts API"):
    """Send SMS to a phone number"""
    
    data = {
        "phone_number": phone_number,
        "message": message,
        "language": "fa"
    }
    
    try:
        print(f"📱 Sending SMS to {phone_number}...")
        print(f"Message: {message}")
        
        response = requests.post(
            f"{API_BASE_URL}/api/v1/sms/send",
            json=data
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SMS processed successfully!")
            print(f"Response: {json.dumps(result, indent=2)}")
            
            if result.get("success"):
                print("🎉 SMS was sent successfully!")
            else:
                print("⚠️  SMS was processed but not sent (service not configured)")
                print("   This is normal in test mode.")
        else:
            print("❌ Failed to send SMS")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python send_sms_simple.py <phone_number> [message]")
        print("Examples:")
        print("  python send_sms_simple.py +989335540052")
        print("  python send_sms_simple.py +989335540052 'Hello from China Car Parts!'")
        sys.exit(1)
    
    phone_number = sys.argv[1]
    message = sys.argv[2] if len(sys.argv) > 2 else "Test SMS from China Car Parts API"
    
    send_sms(phone_number, message)

if __name__ == "__main__":
    main()
