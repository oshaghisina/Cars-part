#!/usr/bin/env python3
"""
Test the production bot to verify it's working correctly.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set environment variables
os.environ["TELEGRAM_BOT_TOKEN"] = "8288892164:AAFVVc_-DuvCUIhkl7EH-N9hOWFyq3Y2CS4"
os.environ["ADMIN_TELEGRAM_IDS"] = "176007160"
os.environ["APP_ENV"] = "production"
os.environ["DEBUG"] = "false"
os.environ["DATABASE_URL"] = "postgresql://admin:secure_password@localhost:5432/china_car_parts"

from aiogram import Bot
from app.core.config import settings

async def test_production_bot():
    """Test the production bot."""
    print("🤖 Testing Production Bot")
    print("=" * 30)
    
    try:
        bot = Bot(token=settings.telegram_bot_token)
        
        # Get bot info
        bot_info = await bot.get_me()
        print(f"✅ Bot: @{bot_info.username} ({bot_info.first_name})")
        print(f"✅ Bot ID: {bot_info.id}")
        
        # Test sending a message to yourself (admin)
        admin_id = settings.admin_telegram_ids_list[0]
        print(f"📤 Sending test message to admin ID: {admin_id}")
        
        test_message = """
🚀 **Production Bot Test Message**

✅ Your production Telegram bot is working correctly!

**Production Information:**
• Server: 5.223.59.155
• Bot Username: @Carspartbot
• Status: Online and Ready
• Environment: Production

**Available Commands:**
• /start - Start using the bot
• /search - Search for parts
• /orders - View your orders
• /help - Get help

**Production URLs:**
• API: https://5.223.59.155
• Admin Panel: https://5.223.59.155

The production bot is now fully functional! 🎉
        """
        
        await bot.send_message(
            chat_id=admin_id,
            text=test_message,
            parse_mode="Markdown"
        )
        
        print("✅ Production test message sent successfully!")
        print("Check your Telegram for the production test message.")
        
        await bot.session.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed to send production test message: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_production_bot())
