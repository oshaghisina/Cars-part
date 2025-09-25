#!/usr/bin/env python3
"""
Minimal test for Telegram SSO API.
"""

import requests
import json

def test_telegram_minimal():
    """Test Telegram API with minimal request."""
    print("🧪 Testing Telegram SSO API (Minimal)...\n")
    
    try:
        # Test with minimal data
        response = requests.post('http://localhost:8001/api/v1/telegram/link/request', json={
            'telegram_id': 176007160
        })
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Success!")
            print(f"Message: {data.get('message')}")
        else:
            print("❌ Failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_telegram_minimal()
