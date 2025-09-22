#!/usr/bin/env python3
"""
Test sending a message to the bot to verify it's working.
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
os.environ["APP_ENV"] = "development"
os.environ["DEBUG"] = "true"
os.environ["DATABASE_URL"] = "sqlite:///./data/app.db"

from aiogram import Bot
from app.core.config import settings

async def test_bot_message():
    """Test sending a message to the bot."""
    print("🤖 Testing Bot Message Sending")
    print("=" * 35)
    
    try:
        bot = Bot(token=settings.telegram_bot_token)
        
        # Get bot info
        bot_info = await bot.get_me()
        print(f"✅ Bot: @{bot_info.username} ({bot_info.first_name})")
        
        # Test sending a message to yourself (admin)
        admin_id = settings.admin_telegram_ids_list[0]
        print(f"📤 Sending test message to admin ID: {admin_id}")
        
        test_message = """
🤖 **Bot Test Message**

✅ Your Telegram bot is working correctly!

**Bot Information:**
• Username: @Carspartbot
• Name: Carspart
• Status: Online and Ready

**Available Commands:**
• /start - Start using the bot
• /search - Search for parts
• /orders - View your orders
• /help - Get help

**Next Steps:**
1. Try sending /start to the bot
2. Test searching for parts
3. Use the admin panel at http://localhost:8001

The bot is now fully functional! 🎉
        """
        
        await bot.send_message(
            chat_id=admin_id,
            text=test_message,
            parse_mode="Markdown"
        )
        
        print("✅ Test message sent successfully!")
        print("Check your Telegram for the test message.")
        
        await bot.session.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed to send test message: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_bot_message())
