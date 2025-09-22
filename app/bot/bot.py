"""Main Telegram bot implementation."""

import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    BotCommand,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from app.bot.wizard_handlers import router as wizard_router
from app.core.config import settings
from app.db.database import SessionLocal
from app.services.bot_service import BotService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
AI_ENABLED = "ai_enabled"
on = "on"
off = "off"
orders = "orders"
search = "search"
confirm_part_ = "confirm_part_"
search_again = "search_again"


# FSM States
class OrderStates(StatesGroup):
    """States for order creation workflow."""

    waiting_for_confirmation = State()
    waiting_for_contact = State()
    order_created = State()


class SearchStates(StatesGroup):
    """States for search workflow."""

    waiting_for_search = State()
    showing_results = State()


# Initialize bot and dispatcher
try:
    bot = Bot(token=settings.telegram_bot_token)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
except Exception as e:
    print(f"⚠️  Bot initialization failed: {e}")
    print("⚠️  Please set a valid TELEGRAM_BOT_TOKEN in .env file")
    bot = None
    dp = None


if dp:

    async def setup_bot_commands():
        """Set up bot commands menu."""
        commands = [
            BotCommand(command="start", description="شروع استفاده از ربات"),
            BotCommand(command="help", description="راهنمای استفاده"),
            BotCommand(command="wizard", description="راهنمای گام به گام جستجو"),
            BotCommand(command="search", description="جستجوی قطعات"),
            BotCommand(command="orders", description="مشاهده سفارشات"),
            BotCommand(command="menu", description="منوی اصلی"),
            BotCommand(command="ai", description="تنظیمات جستجوی هوشمند"),
        ]
        await bot.set_my_commands(commands)

    @dp.message(Command("start"))
    async def cmd_start(message: Message):
        """Handle /start command."""
        welcome_text = """
🤖 **خوش آمدید به ربات قطعات خودرو چینی!**

با این ربات می‌توانید:
🔍 **جستجوی قطعات** - قطعات خودروهای چری، جک، بریلیانس و غیره
📋 **ثبت سفارش** - سفارش قطعات مورد نیاز
📊 **پیگیری سفارشات** - مشاهده وضعیت سفارشات
⚙️ **جستجوی هوشمند** - جستجوی پیشرفته با هوش مصنوعی

برای شروع، نام قطعه مورد نظر خود را ارسال کنید یا از منو استفاده کنید.
"""

        # Create main menu keyboard
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="🧙‍♂️ راهنمای گام به گام", callback_data="start_wizard"),
                    InlineKeyboardButton(text="🔍 جستجوی قطعات", callback_data="search_parts"),
                ],
                [
                    InlineKeyboardButton(text="📋 سفارشات من", callback_data="my_orders"),
                    InlineKeyboardButton(text="❓ راهنمای استفاده", callback_data="help"),
                ],
                [InlineKeyboardButton(text="⚙️ تنظیمات", callback_data="settings")],
            ]
        )

        await message.answer(welcome_text, reply_markup=keyboard, parse_mode="Markdown")

    @dp.callback_query(F.data == "start_wizard")
    async def callback_start_wizard(callback: CallbackQuery, state: FSMContext):
        """Handle wizard start from callback."""
        from app.bot.wizard_handlers import start_wizard_direct

        # Call wizard function directly with callback data
        await start_wizard_direct(callback, state)
        await callback.answer()

    @dp.message(Command("help"))
    async def cmd_help(message: Message):
        """Handle /help command."""
        help_text = """
📖 **راهنمای کامل استفاده از ربات**

🔍 **جستجوی قطعات:**
• نام قطعه مورد نظر خود را ارسال کنید
• مثال: لنت ترمز جلو تیگو ۸
• برای جستجوی چندین قطعه، هر قطعه را در یک خط جداگانه بنویسید

📋 **ثبت سفارش:**
• پس از یافتن قطعه، روی دکمه تأیید کلیک کنید
• شماره تماس خود را ارسال کنید
• سفارش شما ثبت خواهد شد

📊 **پیگیری سفارشات:**
• از دستور /orders استفاده کنید
• وضعیت سفارشات خود را مشاهده کنید

⚙️ **دستورات موجود:**
/start - شروع مجدد ربات
/help - نمایش این راهنما
/search - جستجوی قطعات
/orders - مشاهده سفارشات
/menu - منوی اصلی
/ai - تنظیمات جستجوی هوشمند

💡 **نکات مهم:**
• نام قطعه را دقیق و کامل بنویسید
• از نام مدل خودرو استفاده کنید
• برای جستجوی بهتر، نام برند را نیز ذکر کنید
• می‌توانید به فارسی یا انگلیسی جستجو کنید
"""

        # Create help menu keyboard
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="🔍 شروع جستجو", callback_data="search_parts"),
                    InlineKeyboardButton(text="📋 سفارشات من", callback_data="my_orders"),
                ],
                [InlineKeyboardButton(text="🏠 منوی اصلی", callback_data="main_menu")],
            ]
        )

        await message.answer(help_text, reply_markup=keyboard, parse_mode="Markdown")

    @dp.message(Command("ai"))
    async def cmd_ai(message: Message):
        """Handle /ai command for admin toggle."""

        # Check if user is admin
        if message.from_user.id not in settings.admin_telegram_ids_list:
            await message.answer("شما مجوز لازم برای این عملیات را ندارید.")
            return

        # Parse command arguments
        args = message.text.split()
        if len(args) != 2:
            await message.answer("استفاده: /ai on یا /ai off")
            return

        action = args[1].lower()
        if action == on:
            # Enable AI search
            from app.db.database import SessionLocal
            from app.services.settings_service import SettingsService

            db = SessionLocal()
            try:
                settings_service = SettingsService(db)
                settings_service.set_setting(AI_ENABLED, True)
                await message.answer("جستجوی هوش مصنوعی فعال شد ✅")
            except Exception as e:
                await message.answer("خطا در فعال‌سازی جستجوی هوش مصنوعی ❌")
                logger.error(f"Error enabling AI search: {e}")
            finally:
                db.close()

        elif action == off:
            # Disable AI search
            from app.db.database import SessionLocal
            from app.services.settings_service import SettingsService

            db = SessionLocal()
            try:
                settings_service = SettingsService(db)
                settings_service.set_setting(AI_ENABLED, False)
                await message.answer("جستجوی هوش مصنوعی غیرفعال شد ❌")
            except Exception as e:
                await message.answer("خطا در غیرفعال‌سازی جستجوی هوش مصنوعی ❌")
                logger.error(f"Error disabling AI search: {e}")
            finally:
                db.close()
        else:
            await message.answer("استفاده: /ai on یا /ai off")

    @dp.message(Command(orders))
    async def cmd_orders(message: Message):
        """Handle /orders command to check order status."""
        telegram_user_id = str(message.from_user.id)

        db = SessionLocal()
        try:
            bot_service = BotService(db)
            result = bot_service.get_order_status(telegram_user_id)

            if result["success"]:
                if result["orders"]:
                    # Show orders summary
                    await message.answer(result["message"])

                    for order in result["orders"][:5]:  # Show last 5 orders
                        status_text = f"📋 سفارش #{order['order_id']:05d}\n"
                        status_text += f"وضعیت: {order['status']}\n"
                        status_text += f"تاریخ: {order['created_at'].strftime('%Y-%m-%d %H:%M')}\n"
                        status_text += f"تعداد قطعات: {order['total_items']}\n"

                        if order["matched_items"] > 0:
                            status_text += f"قطعات یافت شده: " f"{order['matched_items']}/{order['total_items']}\n"

                        await message.answer(status_text)
                else:
                    await message.answer(result["message"])
            else:
                await message.answer(result["message"])

        except Exception as e:
            logger.error(f"Error checking orders: {e}")
            await message.answer("خطایی در بررسی سفارشات رخ داد.")
        finally:
            db.close()

    @dp.message(Command(search))
    async def cmd_search(message: Message, state: FSMContext):
        "Handle /search command." ""
        await state.set_state(SearchStates.waiting_for_search)
        await message.answer(
            "🔍 **جستجوی قطعات**\n\n"
            "لطفاً نام قطعه مورد نظر خود را ارسال کنید:\n\n"
            "مثال‌ها:\n"
            "• لنت ترمز جلو تیگو ۸\n"
            "• فیلتر روغن X22\n"
            "• لامپ چراغ عقب آریزو ۵",
            parse_mode="Markdown",
        )

    @dp.message(Command("menu"))
    async def cmd_menu(message: Message):
        """Handle /menu command."""
        menu_text = "🏠 **منوی اصلی**\n\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید:"

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="🔍 جستجوی قطعات", callback_data="search_parts"),
                    InlineKeyboardButton(text="📋 سفارشات من", callback_data="my_orders"),
                ],
                [
                    InlineKeyboardButton(text="❓ راهنمای استفاده", callback_data="help"),
                    InlineKeyboardButton(text="⚙️ تنظیمات", callback_data="settings"),
                ],
                [InlineKeyboardButton(text="📞 تماس با پشتیبانی", callback_data="support")],
            ]
        )

        await message.answer(menu_text, reply_markup=keyboard, parse_mode="Markdown")

    # Callback handlers for inline keyboards
    @dp.callback_query(lambda c: c.data == "search_parts")
    async def handle_search_parts(callback_query: CallbackQuery, state: FSMContext):
        await callback_query.answer()
        await state.set_state(SearchStates.waiting_for_search)
        await callback_query.message.answer("🔍 **جستجوی قطعات**\n\n" "لطفاً نام قطعه مورد نظر خود را ارسال کنید:")

    @dp.callback_query(lambda c: c.data == "my_orders")
    async def handle_my_orders(callback_query: CallbackQuery):
        await callback_query.answer()
        telegram_user_id = str(callback_query.from_user.id)

        db = SessionLocal()
        try:
            bot_service = BotService(db)
            result = bot_service.get_order_status(telegram_user_id)

            if result["success"]:
                if result["orders"]:
                    await callback_query.message.answer(result["message"])

                    for order in result["orders"][:3]:  # Show last 3 orders
                        status_text = f"📋 سفارش #{order['order_id']:05d}\n"
                        status_text += f"وضعیت: {order['status']}\n"
                        status_text += f"تاریخ: {order['created_at'].strftime('%Y-%m-%d %H:%M')}\n"
                        status_text += f"تعداد قطعات: {order['total_items']}\n"

                        if order["matched_items"] > 0:
                            status_text += f"قطعات یافت شده: " f"{order['matched_items']}/{order['total_items']}\n"

                        await callback_query.message.answer(status_text)
                else:
                    await callback_query.message.answer(result["message"])
            else:
                await callback_query.message.answer(result["message"])

        except Exception as e:
            logger.error(f"Error checking orders: {e}")
            await callback_query.message.answer("خطایی در بررسی سفارشات رخ داد.")
        finally:
            db.close()

    @dp.callback_query(lambda c: c.data == help)
    async def handle_help(callback_query: CallbackQuery):
        await callback_query.answer()
        help_text = """
📖 **راهنمای سریع**

🔍 **جستجو:** نام قطعه را بنویسید
📋 **سفارش:** پس از یافتن قطعه، تأیید کنید
📊 **پیگیری:** از /orders استفاده کنید

💡 **نکته:** نام مدل خودرو را هم بنویسید
"""
        await callback_query.message.answer(help_text)

    @dp.callback_query(lambda c: c.data == "settings")
    async def handle_settings(callback_query: CallbackQuery):
        await callback_query.answer()
        settings_text = "⚙️ **تنظیمات**\n\nدر حال حاضر تنظیمات خاصی موجود نیست."
        await callback_query.message.answer(settings_text)

    @dp.callback_query(lambda c: c.data == "support")
    async def handle_support(callback_query: CallbackQuery):
        await callback_query.answer()
        support_text = """
📞 **پشتیبانی**

برای ارتباط با پشتیبانی:
• تلفن: 021-12345678
• ایمیل: support@example.com
• تلگرام: @support_bot

ساعات کاری: 9 صبح تا 6 عصر
"""
        await callback_query.message.answer(support_text)

    @dp.callback_query(lambda c: c.data == "main_menu")
    async def handle_main_menu(callback_query: CallbackQuery):
        await callback_query.answer()
        welcome_text = """
🏠 **منوی اصلی**

لطفاً یکی از گزینه‌های زیر را انتخاب کنید:
"""

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="🔍 جستجوی قطعات", callback_data="search_parts"),
                    InlineKeyboardButton(text="📋 سفارشات من", callback_data="my_orders"),
                ],
                [
                    InlineKeyboardButton(text="❓ راهنمای استفاده", callback_data="help"),
                    InlineKeyboardButton(text="⚙️ تنظیمات", callback_data="settings"),
                ],
            ]
        )

        await callback_query.message.answer(welcome_text, reply_markup=keyboard, parse_mode="Markdown")

    @dp.message(lambda message: not message.text.startswith("/"))
    async def message_handler(message: Message):
        """Handle all other messages with part search."""
        query = message.text.strip()

        if not query:
            await message.answer("لطفاً نام قطعه یا مدل خودرو را وارد کنید.")
            return

        # Check if it's a multi-line query (bulk search)
        lines = [line.strip() for line in query.split("\n") if line.strip()]

        if len(lines) > 1:
            # Bulk search
            db = SessionLocal()
            try:
                bot_service = BotService(db)
                result = bot_service.search_multiple_parts(lines)

                if result["success"]:
                    # Send summary
                    await message.answer(result["message"])

                    # Send details for found parts
                    for item in result["results"]:
                        if "found" not in item:  # Found part
                            price_text = ""
                            if item["best_price"]:
                                price_text = f" - قیمت: {item['best_price']:,.0f} " f"{item['currency']}"

                            detail_text = (
                                f"✅ {item['query']}\n" f"{item['part_name']} {item['vehicle_model']}" f"{price_text}"
                            )
                            await message.answer(detail_text)
                        else:
                            # Not found
                            await message.answer(f"❌ {item['query']}: {item['message']}")
                else:
                    await message.answer(result["message"])

            except Exception as e:
                logger.error(f"Error in bulk search: {e}")
                await message.answer("خطایی در جستجو رخ داد. لطفاً دوباره تلاش کنید.")
            finally:
                db.close()
        else:
            # Single part search
            db = SessionLocal()
            try:
                bot_service = BotService(db)
                result = bot_service.search_and_confirm_part(query)

                if result["found"]:
                    # Send confirmation message with inline keyboard
                    part_data = result["part_data"]

                    # Create inline keyboard for confirmation
                    keyboard = InlineKeyboardMarkup(
                        inline_keyboard=[
                            [
                                InlineKeyboardButton(
                                    text="✅ بله، این همان قطعه است",
                                    callback_data=f"confirm_part_{part_data['id']}_{query}",
                                ),
                                InlineKeyboardButton(
                                    text="❌ خیر، جستجوی جدید",
                                    callback_data="search_again",
                                ),
                            ]
                        ]
                    )

                    await message.answer(result["message"], reply_markup=keyboard)

                    # Send additional details
                    detail_text = "📋 جزئیات:\n"
                    if part_data["oem_code"]:
                        detail_text += f"• کد OEM: {part_data['oem_code']}\n"
                    detail_text += f"• دسته‌بندی: {part_data['category']}\n"
                    if part_data["position"]:
                        detail_text += f"• موقعیت: {part_data['position']}\n"
                    if part_data["pack_size"]:
                        detail_text += f"• بسته‌بندی: {part_data['pack_size']} عدد\n"

                    await message.answer(detail_text)
                else:
                    await message.answer(result["message"])

            except Exception as e:
                logger.error(f"Error in part search: {e}")
                await message.answer("خطایی در جستجو رخ داد. لطفاً دوباره تلاش کنید.")
            finally:
                db.close()

    @dp.callback_query(lambda c: c.data.startswith(confirm_part_))
    async def handle_part_confirmation(callback_query: CallbackQuery):
        """Handle part confirmation callback."""
        await callback_query.answer()

        # Parse callback data: confirm_part_{part_id}_{query}
        data_parts = callback_query.data.split("_", 2)
        part_id = data_parts[2]
        original_query = data_parts[3] if len(data_parts) > 3 else ""

        telegram_user_id = str(callback_query.from_user.id)

        db = SessionLocal()
        try:
            bot_service = BotService(db)

            # Check if user has contact info
            lead_result = bot_service.handle_contact_capture(telegram_user_id)

            if not lead_result["lead"] or lead_result.get("requires_contact"):
                # Request contact
                contact_keyboard = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="📱 ارسال شماره تماس",
                                request_contact=True,
                                callback_data=f"send_contact_{part_id}_{original_query}",
                            )
                        ]
                    ]
                )

                await callback_query.message.answer(
                    "برای ثبت سفارش، لطفاً شماره تماس خود را ارسال کنید:",
                    reply_markup=contact_keyboard,
                )
            else:
                # Create order directly
                search_result = {
                    "found": True,
                    "part_data": {"id": int(part_id)},
                    "original_query": original_query,
                }

                order_result = bot_service.create_order_from_search_results(telegram_user_id, [search_result])

                if order_result["success"]:
                    await callback_query.message.answer(order_result["message"])
                    await callback_query.message.answer(
                        "تیم ما به زودی با شما تماس خواهد گرفت. " "برای پیگیری سفارش از دستور /orders استفاده کنید."
                    )
                else:
                    await callback_query.message.answer(order_result["message"])

        except Exception as e:
            logger.error(f"Error in part confirmation: {e}")
            await callback_query.message.answer("خطایی در ثبت سفارش رخ داد. لطفاً دوباره تلاش کنید.")
        finally:
            db.close()

    @dp.callback_query(lambda c: c.data == search_again)
    async def handle_search_again(callback_query: CallbackQuery):
        "Handle search again callback." ""
        await callback_query.answer()
        await callback_query.message.answer("لطفاً نام قطعه مورد نظر خود را وارد کنید:")

    @dp.message(lambda message: message.contact is not None)
    async def handle_contact(message: Message):
        """Handle contact sharing."""
        contact = message.contact
        telegram_user_id = str(message.from_user.id)

        db = SessionLocal()
        try:
            bot_service = BotService(db)

            # Handle contact capture
            result = bot_service.handle_contact_capture(
                telegram_user_id=telegram_user_id,
                phone_number=contact.phone_number,
                first_name=contact.first_name,
                last_name=contact.last_name,
            )

            if result["lead"]:
                await message.answer("✅ اطلاعات تماس شما ثبت شد!")
                await message.answer("حالا می‌توانید قطعات مورد نظر خود را جستجو کنید.")
            else:
                await message.answer("❌ خطا در ثبت اطلاعات تماس.")

        except Exception as e:
            logger.error(f"Error handling contact: {e}")
            await message.answer("خطایی در ثبت اطلاعات تماس رخ داد.")
        finally:
            db.close()


async def main():
    """Main bot function."""
    if bot is None or dp is None:
        logger.error("Bot not initialized. Please check your TELEGRAM_BOT_TOKEN.")
        return

    logger.info("Starting Telegram bot...")

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


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot startup error: {e}")
