#!/usr/bin/env python3
"""
Test bot connection directly.
"""

import os
import asyncio
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set environment variables
os.environ["TELEGRAM_BOT_TOKEN"] = "8288892164:AAFVVc_-DuvCUIhkl7EH-N9hOWFyq3Y2CS4"
os.environ["ADMIN_TELEGRAM_IDS"] = "176007160"
os.environ["APP_ENV"] = "development"
os.environ["DEBUG"] = "true"
os.environ["DATABASE_URL"] = "sqlite:///./data/app.db"

from app.core.config import settings
from aiogram import Bot

async def test_bot():
    """Test bot connection."""
    print("🤖 Testing Bot Connection")
    print("=" * 30)
    
    print(f"Token: {settings.telegram_bot_token[:10]}...")
    print(f"Admin IDs: {settings.admin_telegram_ids_list}")
    print(f"App Env: {settings.app_env}")
    print(f"Debug: {settings.debug}")
    
    try:
        bot = Bot(token=settings.telegram_bot_token)
        bot_info = await bot.get_me()
        print(f"\n✅ Bot connected successfully!")
        print(f"   Username: @{bot_info.username}")
        print(f"   Name: {bot_info.first_name}")
        print(f"   ID: {bot_info.id}")
        
        # Test setting commands
        from aiogram.types import BotCommand
        commands = [
            BotCommand(command="start", description="شروع کار با ربات"),
            BotCommand(command="search", description="جستجوی قطعه"),
            BotCommand(command="orders", description="مشاهده سفارشات"),
            BotCommand(command="help", description="راهنما"),
        ]
        await bot.set_my_commands(commands)
        print("✅ Bot commands set successfully!")
        
        await bot.session.close()
        return True
        
    except Exception as e:
        print(f"❌ Bot connection failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_bot())
