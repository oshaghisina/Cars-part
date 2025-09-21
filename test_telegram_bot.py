#!/usr/bin/env python3
"""
🤖 Telegram Bot Test Script
This script tests if your Telegram bot is working correctly
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.core.config import settings
from app.bot.bot import bot, dp
# from app.bot.utils import send_message_to_admin

async def test_bot_connection():
    """Test if the bot can connect to Telegram"""
    print("🤖 Testing Telegram Bot Connection...")
    print("=" * 40)
    
    try:
        # Test bot connection
        bot_info = await bot.get_me()
        print(f"✅ Bot connected successfully!")
        print(f"   Bot Name: {bot_info.first_name}")
        print(f"   Bot Username: @{bot_info.username}")
        print(f"   Bot ID: {bot_info.id}")
        
        return True
    except Exception as e:
        print(f"❌ Bot connection failed: {e}")
        return False

async def test_admin_message():
    """Test sending a message to admin"""
    print("\n📱 Testing Admin Message...")
    print("=" * 40)
    
    try:
        # Send test message to admin
        admin_ids = settings.admin_telegram_ids
        if not admin_ids:
            print("❌ No admin Telegram IDs configured")
            return False
            
        for admin_id in admin_ids:
            await bot.send_message(
                chat_id=admin_id,
                text=f"🧪 Test message from China Car Parts Bot!\n"
                     f"✅ Bot is working correctly!\n"
                     f"🕐 Time: {asyncio.get_event_loop().time()}"
            )
            print(f"✅ Test message sent to admin {admin_id}")
        
        return True
    except Exception as e:
        print(f"❌ Failed to send admin message: {e}")
        return False

async def test_bot_commands():
    """Test bot commands"""
    print("\n⚙️ Testing Bot Commands...")
    print("=" * 40)
    
    try:
        # Get bot commands
        commands = await bot.get_my_commands()
        print(f"✅ Bot has {len(commands)} commands configured:")
        for cmd in commands:
            print(f"   /{cmd.command} - {cmd.description}")
        
        return True
    except Exception as e:
        print(f"❌ Failed to get bot commands: {e}")
        return False

async def main():
    """Main test function"""
    print("🚀 China Car Parts Bot Test")
    print("=" * 50)
    
    # Check configuration
    print(f"📋 Configuration:")
    print(f"   Bot Token: {'✅ Set' if settings.telegram_bot_token else '❌ Not set'}")
    print(f"   Admin IDs: {settings.admin_telegram_ids}")
    print(f"   Debug Mode: {settings.debug}")
    print()
    
    # Test bot connection
    if not await test_bot_connection():
        print("\n❌ Bot test failed - check your token and internet connection")
        return False
    
    # Test admin message
    if not await test_admin_message():
        print("\n⚠️ Admin message test failed - check admin IDs")
    
    # Test bot commands
    if not await test_bot_commands():
        print("\n⚠️ Bot commands test failed")
    
    print("\n🎉 Bot test completed!")
    print("\n📱 Next steps:")
    print("1. Send /start to your bot in Telegram")
    print("2. Try the available commands")
    print("3. Check the admin panel for bot activity")
    
    return True

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏹️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        sys.exit(1)