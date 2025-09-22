"""Development Telegram bot implementation with graceful error handling."""

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from app.bot.wizard_handlers import router as wizard_router
from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize bot and dispatcher with development mode
bot = None
dp = None


def initialize_bot():
    """Initialize bot with development mode support."""
    global bot, dp

    token = settings.telegram_bot_token

    # Check if token is valid (basic validation)
    if not token or token == "CHANGEME_YOUR_PRODUCTION_BOT_TOKEN" or len(token) < 10 or ":" not in token:
        logger.warning("⚠️  Invalid or missing TELEGRAM_BOT_TOKEN")
        logger.warning("⚠️  Bot will run in development mode (no actual Telegram connection)")
        logger.warning("⚠️  To enable full bot functionality, set a valid TELEGRAM_BOT_TOKEN")

        # Create a mock bot for development
        bot = None
        dp = None
        return False

    try:
        bot = Bot(token=token)
        storage = MemoryStorage()
        dp = Dispatcher(storage=storage)

        # Test the token by trying to get bot info
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            bot_info = loop.run_until_complete(bot.get_me())
            loop.close()
            logger.info(f"✅ Bot initialized successfully: @{bot_info.username}")
            return True
        except Exception as token_error:
            logger.warning(f"⚠️  Token validation failed: {token_error}")
            logger.warning("⚠️  Bot will run in development mode")
            bot = None
            dp = None
            return False

    except Exception as e:
        logger.error(f"❌ Bot initialization failed: {e}")
        logger.warning("⚠️  Bot will run in development mode")
        bot = None
        dp = None
        return False


# Initialize bot
bot_initialized = initialize_bot()


async def main():
    """Main bot function with development mode support."""
    if not bot_initialized:
        logger.info("🤖 Bot running in DEVELOPMENT MODE")
        logger.info("📱 API endpoints are fully functional")
        logger.info("🌐 Admin panel available at http://localhost:8001")
        logger.info("🔧 To enable Telegram bot, set a valid TELEGRAM_BOT_TOKEN")

        # Keep the process running for development
        try:
            while True:
                await asyncio.sleep(60)
                logger.info("🔄 Development bot heartbeat...")
        except KeyboardInterrupt:
            logger.info("🛑 Development bot stopped by user")
        return

    logger.info("🚀 Starting Telegram bot...")

    try:
        # Set up bot commands menu
        await setup_bot_commands()
        logger.info("Bot commands menu set up successfully")

        # Include wizard router
        dp.include_router(wizard_router)
        logger.info("Wizard router included successfully")

        # Delete webhook if exists
        await bot.delete_webhook(drop_pending_updates=True)

        # Get bot info
        bot_info = await bot.get_me()
        logger.info(f"Bot @{bot_info.username} is running")

        # Start polling
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Bot error: {e}")
    finally:
        if bot:
            await bot.session.close()


async def setup_bot_commands():
    """Set up bot commands menu."""
    commands = [
        BotCommand(command="start", description="شروع کار با ربات"),
        BotCommand(command="search", description="جستجوی قطعه"),
        BotCommand(command="orders", description="مشاهده سفارشات"),
        BotCommand(command="help", description="راهنما"),
    ]
    await bot.set_my_commands(commands)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot startup error: {e}")
