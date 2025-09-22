#!/usr/bin/env python3
"""
Test script to verify Telegram bot setup with real token.
This script will test the bot token and show you how to configure it properly.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set environment variables for testing
os.environ["TELEGRAM_BOT_TOKEN"] = "8288892164:AAFVVc_-DuvCUIhkl7EH-N9hOWFyq3Y2CS4"
os.environ["ADMIN_TELEGRAM_IDS"] = "176007160"
os.environ["APP_ENV"] = "development"
os.environ["DEBUG"] = "true"
os.environ["DATABASE_URL"] = "sqlite:///./data/app.db"

from app.core.config import settings
from app.bot.bot import bot, dp

async def test_bot_setup():
    """Test the bot setup and configuration."""
    print("🤖 Testing Telegram Bot Setup")
    print("=" * 40)
    
    # Test configuration
    print(f"✅ Bot Token: {settings.telegram_bot_token[:10]}...")
    print(f"✅ Admin IDs: {settings.admin_telegram_ids_list}")
    print(f"✅ App Environment: {settings.app_env}")
    print(f"✅ Debug Mode: {settings.debug}")
    print(f"✅ Database: {settings.database_url}")
    
    if bot is None:
        print("❌ Bot initialization failed!")
        return False
    
    try:
        # Test bot connection
        print("\n🔍 Testing bot connection...")
        bot_info = await bot.get_me()
        print(f"✅ Bot connected successfully!")
        print(f"   Bot Username: @{bot_info.username}")
        print(f"   Bot Name: {bot_info.first_name}")
        print(f"   Bot ID: {bot_info.id}")
        
        # Test bot commands setup
        print("\n🔧 Testing bot commands setup...")
        from app.bot.bot import setup_bot_commands
        await setup_bot_commands()
        print("✅ Bot commands set up successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Bot connection failed: {e}")
        return False
    finally:
        if bot:
            await bot.session.close()

async def main():
    """Main test function."""
    print("Starting Telegram Bot Setup Test...")
    print("This will test your bot token and configuration.")
    print()
    
    success = await test_bot_setup()
    
    if success:
        print("\n🎉 Bot setup test completed successfully!")
        print("\nNext steps:")
        print("1. Your bot is ready to use!")
        print("2. Start the bot with: python -m app.bot.bot")
        print("3. Test it on Telegram by messaging your bot")
        print("4. Admin panel is available at: http://localhost:8001")
    else:
        print("\n❌ Bot setup test failed!")
        print("Please check your token and configuration.")

if __name__ == "__main__":
    asyncio.run(main())
