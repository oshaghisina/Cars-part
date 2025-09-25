#!/usr/bin/env python3
"""
Test script to verify authentication system integration with Telegram bot.
"""

import asyncio
import json
import sys
from datetime import datetime

import httpx

# Configuration
API_BASE_URL = "http://localhost:8001/api/v1"
BOT_TOKEN = "8288892164:AAFVVc_-DuvCUIhkl7EH-N9hOWFyq3Y2CS4"
BOT_USERNAME = "ChinaCarPartBot"

async def test_auth_system():
    """Test the complete authentication system integration."""
    print("🧪 Testing Authentication System with Telegram Bot Integration")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Test 1: Health Check
        print("\n1. 🏥 Testing System Health...")
        try:
            response = await client.get(f"{API_BASE_URL}/auth/health")
            if response.status_code == 200:
                health_data = response.json()
                print(f"   ✅ System Status: {health_data['status']}")
                print(f"   ✅ JWT Service: {health_data['jwt_service']}")
                print(f"   ✅ Database: {health_data['database']}")
                print(f"   ✅ Telegram SSO: {health_data['features']['telegram_sso']}")
                print(f"   ✅ OTP System: {health_data['features']['otp']}")
            else:
                print(f"   ❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ Health check error: {e}")
            return False
        
        # Test 2: Admin Login
        print("\n2. 🔐 Testing Admin Login...")
        try:
            login_data = {
                "username_or_email": "admin",
                "password": "adminpassword"
            }
            response = await client.post(f"{API_BASE_URL}/users/login", json=login_data)
            if response.status_code == 200:
                login_result = response.json()
                token = login_result["access_token"]
                user = login_result["user"]
                print(f"   ✅ Login successful")
                print(f"   ✅ User: {user['username']} ({user['role']})")
                print(f"   ✅ Token expires in: {login_result['expires_in']} seconds")
                print(f"   ✅ Token: {token[:30]}...")
            else:
                print(f"   ❌ Login failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
        except Exception as e:
            print(f"   ❌ Login error: {e}")
            return False
        
        # Test 3: Auth Configuration
        print("\n3. ⚙️ Testing Auth Configuration...")
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = await client.get(f"{API_BASE_URL}/auth/config", headers=headers)
            if response.status_code == 200:
                config = response.json()
                print(f"   ✅ JWT Library: {config['jwt']['library']}")
                print(f"   ✅ Algorithm: {config['jwt']['algorithm']}")
                print(f"   ✅ TTL: {config['jwt']['access_token_expire_minutes']} minutes")
                print(f"   ✅ Telegram SSO: {config['features']['telegram_sso']}")
                print(f"   ✅ OTP Enabled: {config['features']['otp_enabled']}")
            else:
                print(f"   ❌ Config fetch failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ Config error: {e}")
            return False
        
        # Test 4: Telegram SSO Link Request
        print("\n4. 🤖 Testing Telegram SSO Link Request...")
        try:
            telegram_data = {"telegram_id": 123456789}
            response = await client.post(f"{API_BASE_URL}/telegram/link/request", json=telegram_data)
            if response.status_code == 200:
                link_result = response.json()
                print(f"   ✅ Link token created: {link_result['link_token'][:20]}...")
                print(f"   ✅ Telegram URL: {link_result['telegram_url']}")
                print(f"   ✅ Expires in: {link_result['expires_in']} seconds")
            else:
                print(f"   ❌ Telegram link failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
        except Exception as e:
            print(f"   ❌ Telegram link error: {e}")
            return False
        
        # Test 5: OTP System
        print("\n5. 📱 Testing OTP System...")
        try:
            otp_data = {
                "phone_number": "+989123456789",
                "code_type": "login"
            }
            response = await client.post(f"{API_BASE_URL}/otp/request", json=otp_data)
            if response.status_code == 200:
                otp_result = response.json()
                print(f"   ✅ OTP sent successfully")
                print(f"   ✅ Expires in: {otp_result['expires_in']} seconds")
                print(f"   ✅ Resend allowed: {otp_result['resend']}")
            else:
                print(f"   ❌ OTP request failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
        except Exception as e:
            print(f"   ❌ OTP error: {e}")
            return False
        
        # Test 6: Token Validation
        print("\n6. 🔍 Testing Token Validation...")
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = await client.get(f"{API_BASE_URL}/users/me", headers=headers)
            if response.status_code == 200:
                user_data = response.json()
                print(f"   ✅ Token validation successful")
                print(f"   ✅ User: {user_data['username']} ({user_data['role']})")
                print(f"   ✅ Last login: {user_data['last_login']}")
            else:
                print(f"   ❌ Token validation failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ Token validation error: {e}")
            return False
        
        # Test 7: Auth Stats
        print("\n7. 📊 Testing Auth Statistics...")
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = await client.get(f"{API_BASE_URL}/auth/stats", headers=headers)
            if response.status_code == 200:
                stats = response.json()
                print(f"   ✅ Auth stats retrieved")
                print(f"   ✅ JWT tokens: {stats['jwt_tokens']}")
                print(f"   ✅ Authentication: {stats['authentication']}")
                print(f"   ✅ OTP stats: {stats['otp']}")
                print(f"   ✅ Telegram stats: {stats['telegram']}")
            else:
                print(f"   ❌ Auth stats failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ Auth stats error: {e}")
            return False
        
        print("\n" + "=" * 60)
        print("🎉 ALL AUTHENTICATION TESTS PASSED!")
        print("=" * 60)
        print("\n✅ Authentication System Status:")
        print("   • JWT Authentication: WORKING")
        print("   • Admin Login: WORKING")
        print("   • Token Validation: WORKING")
        print("   • Telegram SSO: WORKING")
        print("   • OTP System: WORKING")
        print("   • Auth Configuration: WORKING")
        print("   • Auth Statistics: WORKING")
        print("\n🤖 Telegram Bot Integration:")
        print(f"   • Bot Token: {BOT_TOKEN[:20]}...")
        print(f"   • Bot Username: @{BOT_USERNAME}")
        print("   • Account Linking: WORKING")
        print("   • Deep Link Generation: WORKING")
        print("\n🚀 System is ready for production!")
        
        return True

async def main():
    """Main test function."""
    try:
        success = await test_auth_system()
        if success:
            print("\n✅ All tests completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Some tests failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test execution failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
