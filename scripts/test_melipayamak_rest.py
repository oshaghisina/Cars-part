#!/usr/bin/env python3
"""
Test Melipayamak REST API with Bearer token
"""

import requests
import json

def test_rest_api():
    """Test Melipayamak REST API with Bearer token"""
    
    api_key = "59a3a4a7-b8fe-422c-be38-e07ebec590c6"
    phone_number = "+989335540052"
    message = "Test SMS via REST API"
    
    print(f"🔑 Testing REST API with key: {api_key[:8]}...")
    print(f"📱 Phone: {phone_number}")
    print(f"📝 Message: {message}")
    
    # Try different possible REST API endpoints
    endpoints = [
        "https://rest.payamak-panel.com/api/SendSMS/SendSMS",
        "https://api.melipayamak.com/api/send/sms",
        "https://rest.payamak-panel.com/api/SendSMS/SendSMS",
        "https://api.payamak-panel.com/send/sms",
        "https://rest.payamak-panel.com/api/SendSMS/SendSMS"
    ]
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }
    
    # Try different data formats
    data_formats = [
        {
            "to": phone_number,
            "text": message,
            "from": "5000"
        },
        {
            "phone_number": phone_number,
            "message": message,
            "sender": "5000"
        },
        {
            "recipient": phone_number,
            "content": message,
            "sender_number": "5000"
        },
        {
            "to": phone_number,
            "message": message,
            "from": "5000",
            "username": api_key,
            "password": api_key
        }
    ]
    
    for endpoint in endpoints:
        print(f"\n🌐 Testing endpoint: {endpoint}")
        
        for i, data in enumerate(data_formats):
            print(f"  📋 Data format {i+1}: {data}")
            
            try:
                response = requests.post(
                    endpoint,
                    json=data,
                    headers=headers,
                    timeout=10
                )
                
                print(f"  📊 Status: {response.status_code}")
                print(f"  📄 Response: {response.text[:200]}...")
                
                if response.status_code == 200:
                    try:
                        result = response.json()
                        print(f"  ✅ Success: {result}")
                        return endpoint, data, result
                    except:
                        print(f"  ✅ Success (non-JSON): {response.text}")
                        return endpoint, data, response.text
                        
            except requests.exceptions.RequestException as e:
                print(f"  ❌ Request error: {e}")
            except Exception as e:
                print(f"  ❌ Error: {e}")
    
    print("\n❌ All REST API attempts failed")
    return None, None, None

if __name__ == "__main__":
    test_rest_api()
