#!/usr/bin/env python3
"""
Simple SMS Sending Script - Send a test SMS to a phone number
Usage: python send_test_sms.py <phone_number> [message]
"""

import requests
import json
import sys

API_BASE_URL = "http://localhost:8001"

def send_sms(phone_number, message=None, template_name="welcome_message"):
    """Send SMS to a phone number"""
    
    if message:
        # Send custom message
        data = {
            "phone_number": phone_number,
            "message": message,
            "template_name": None
        }
    else:
        # Send template message
        data = {
            "phone_number": phone_number,
            "template_name": template_name,
            "variables": {}
        }
    
    try:
        print(f"📱 Sending SMS to {phone_number}...")
        print(f"Message: {message or f'Template: {template_name}'}")
        
        response = requests.post(
            f"{API_BASE_URL}/api/v1/sms/send",
            json=data
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SMS sent successfully!")
            print(f"Response: {json.dumps(result, indent=2)}")
        else:
            print("❌ Failed to send SMS")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python send_test_sms.py <phone_number> [message]")
        print("Examples:")
        print("  python send_test_sms.py +989123456789")
        print("  python send_test_sms.py +989123456789 'Hello from China Car Parts!'")
        sys.exit(1)
    
    phone_number = sys.argv[1]
    message = sys.argv[2] if len(sys.argv) > 2 else None
    
    send_sms(phone_number, message)

if __name__ == "__main__":
    main()
