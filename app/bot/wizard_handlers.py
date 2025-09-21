"""Wizard bot handlers for guided part search flow."""

import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from typing import List, Dict, Any
import requests
from app.bot.wizard_states import PartsWizard

logger = logging.getLogger(__name__)

router = Router()

# API base URL
API_BASE = "http://localhost:8001/api/v1"


class WizardBotService:
    """Service for bot wizard operations."""

    def __init__(self):
        self.api_base = API_BASE

    def create_session(self, user_id: str,
                       state: str = "start") -> Dict[str, Any]:
        """Create wizard session."""
        try:
            response = requests.post(f"{self.api_base}/wizard/sessions", json={
                "user_id": user_id,
                "state": state
            })
            if response.status_code == 200:
                return response.json()
            return {}
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            return {}

    def get_session(self, user_id: str) -> Dict[str, Any]:
        """Get wizard session."""
        try:
            response = requests.get(
                f"{self.api_base}/wizard/sessions/{user_id}")
            if response.status_code == 200:
                return response.json()
            return {}
        except Exception as e:
            logger.error(f"Error getting session: {e}")
            return {}

    def update_session(self, user_id: str, **kwargs) -> Dict[str, Any]:
        """Update wizard session."""
        try:
            response = requests.put(
                f"{self.api_base}/wizard/sessions/{user_id}", json=kwargs)
            if response.status_code == 200:
                return response.json()
            return {}
        except Exception as e:
            logger.error(f"Error updating session: {e}")
            return {}

    def get_brands(self) -> List[str]:
        """Get available brands."""
        try:
            response = requests.get(f"{self.api_base}/wizard/brands")
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            logger.error(f"Error getting brands: {e}")
            return []

    def get_models(self, brand: str) -> List[str]:
        """Get available models for brand."""
        try:
            response = requests.get(
                f"{self.api_base}/wizard/models?brand={brand}")
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            logger.error(f"Error getting models: {e}")
            return []

    def get_categories(
            self,
            brand: str | None = None,
            model: str | None = None) -> List[str]:
        """Get available categories."""
        try:
            params = {}
            if brand:
                params['brand'] = brand
            if model:
                params['model'] = model

            url = f"{self.api_base}/wizard/categories"
            if params:
                url += "?" + "&".join([f"{k}={v}" for k, v in params.items()])

            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            logger.error(f"Error getting categories: {e}")
            return []

    def get_parts(self, brand: str | None = None, model: str |
                  None = None, category: str | None = None) -> List[Dict[str, Any]]:
        """Get available parts."""
        try:
            params = {}
            if brand:
                params['brand'] = brand
            if model:
                params['model'] = model
            if category:
                params['category'] = category

            url = f"{self.api_base}/wizard/parts"
            if params:
                url += "?" + "&".join([f"{k}={v}" for k, v in params.items()])

            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            logger.error(f"Error getting parts: {e}")
            return []

    def search_parts(self,
                     vehicle_data: Dict[str,
                                        Any],
                     part_data: Dict[str,
                                     Any]) -> List[Dict[str,
                                                        Any]]:
        """Search parts by criteria."""
        try:
            response = requests.post(f"{self.api_base}/wizard/search", json={
                "vehicle_data": vehicle_data,
                "part_data": part_data
            })
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            logger.error(f"Error searching parts: {e}")
            return []

    def clear_session(self, user_id: str) -> bool:
        """Clear wizard session."""
        try:
            response = requests.delete(
                f"{self.api_base}/wizard/sessions/{user_id}")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error clearing session: {e}")
            return False


# Initialize service
wizard_service = WizardBotService()


async def safe_edit_message(
        callback: CallbackQuery,
        text: str,
        reply_markup: InlineKeyboardMarkup | None = None,
        parse_mode: str | None = None):
    """Safely edit message, fallback to sending new message if edit fails."""
    try:
        # Try to edit the message
        if hasattr(callback.message, 'edit_text'):
            edit_method = getattr(callback.message, 'edit_text', None)
            if edit_method and callable(edit_method):
                # Type ignore for dynamic method call
                # type: ignore
                await edit_method(text, reply_markup=reply_markup, parse_mode=parse_mode)
        else:
            # Fallback to sending new message
            await callback.message.answer(text, reply_markup=reply_markup, parse_mode=parse_mode)
    except (TelegramBadRequest, AttributeError):
        # If edit fails, send a new message
        await callback.message.answer(text, reply_markup=reply_markup, parse_mode=parse_mode)


def create_inline_keyboard(
        items: List[str],
        prefix: str,
        callback_data: str) -> InlineKeyboardMarkup:
    """Create inline keyboard from items."""
    buttons = []
    for item in items:
        buttons.append([InlineKeyboardButton(
            text=item,
            callback_data=f"{prefix}:{item}"
        )])

    # Add navigation buttons
    buttons.append([InlineKeyboardButton(
        text="🔙 بازگشت", callback_data="back")])
    buttons.append([InlineKeyboardButton(
        text="❌ لغو", callback_data="cancel")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.message(Command("wizard"), StateFilter(default_state))
async def start_wizard(message: Message, state: FSMContext):
    """Start wizard flow."""
    user_id = str(message.from_user.id)

    # Create wizard session
    session = wizard_service.create_session(user_id, "start")

    if not session:
        await message.answer("❌ خطا در شروع روند راهنمایی. لطفاً دوباره تلاش کنید.")
        return

    # Get available brands
    brands = wizard_service.get_brands()

    if not brands:
        await message.answer("❌ هیچ برند خودرویی یافت نشد.")
        return

    keyboard = create_inline_keyboard(brands, "brand", "brand")

    await message.answer(
        "🚗 **راهنمای جستجوی قطعات خودرو**\n\n"
        "لطفاً برند خودروی خود را انتخاب کنید:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


async def start_wizard_direct(callback: CallbackQuery, state: FSMContext):
    """Start wizard flow from callback."""
    user_id = str(callback.from_user.id)

    # Create wizard session
    session = wizard_service.create_session(user_id, "start")

    if not session:
        await callback.message.answer("❌ خطا در شروع روند راهنمایی. لطفاً دوباره تلاش کنید.")
        return

    # Get available brands
    brands = wizard_service.get_brands()

    if not brands:
        await callback.message.answer("❌ هیچ برند خودرویی یافت نشد.")
        return

    keyboard = create_inline_keyboard(brands, "brand", "brand")

    await callback.message.answer(
        "🚗 **راهنمای جستجوی قطعات خودرو**\n\n"
        "لطفاً برند خودروی خود را انتخاب کنید:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

    await state.set_state(PartsWizard.brand_selection)


@router.callback_query(F.data.startswith("brand:"))
async def handle_brand_selection(callback: CallbackQuery, state: FSMContext):
    """Handle brand selection."""
    brand = callback.data.split(":", 1)[1]
    user_id = str(callback.from_user.id)

    # Update session with brand
    session = wizard_service.update_session(
        user_id,
        state="model_selection",
        vehicle_data={"brand": brand}
    )

    if not session:
        await callback.answer("❌ خطا در ذخیره انتخاب")
        return

    # Get available models for brand
    models = wizard_service.get_models(brand)

    if not models:
        await safe_edit_message(
            callback,
            f"❌ برای برند {brand} هیچ مدلی یافت نشد.",
            reply_markup=None
        )
        return

    keyboard = create_inline_keyboard(models, "model", "model")

    await safe_edit_message(
        callback,
        f"🚗 **برند انتخاب شده: {brand}**\n\n"
        "لطفاً مدل خودروی خود را انتخاب کنید:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

    await state.set_state(PartsWizard.model_selection)
    await callback.answer()


@router.callback_query(F.data.startswith("model:"),
                       StateFilter(PartsWizard.model_selection))
async def handle_model_selection(callback: CallbackQuery, state: FSMContext):
    """Handle model selection."""
    model = callback.data.split(":", 1)[1]
    user_id = str(callback.from_user.id)

    # Get current session
    session = wizard_service.get_session(user_id)
    if not session:
        await callback.answer("❌ جلسه یافت نشد")
        return

    vehicle_data = session.get("vehicle_data", {})
    vehicle_data["model"] = model

    # Update session with model
    updated_session = wizard_service.update_session(
        user_id,
        state="category_selection",
        vehicle_data=vehicle_data
    )

    if not updated_session:
        await callback.answer("❌ خطا در ذخیره انتخاب")
        return

    # Get available categories
    categories = wizard_service.get_categories(
        brand=vehicle_data.get("brand"),
        model=model
    )

    if not categories:
        await safe_edit_message(
            callback,
            f"❌ برای {vehicle_data.get('brand')} {model} هیچ دسته‌بندی قطعه‌ای یافت نشد.",
            reply_markup=None
        )
        return

    keyboard = create_inline_keyboard(categories, "category", "category")

    await safe_edit_message(
        callback,
        f"🚗 **خودرو: {vehicle_data.get('brand')} {model}**\n\n"
        "لطفاً نوع قطعه مورد نظر خود را انتخاب کنید:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

    await state.set_state(PartsWizard.category_selection)
    await callback.answer()


@router.callback_query(F.data.startswith("category:"),
                       StateFilter(PartsWizard.category_selection))
async def handle_category_selection(
        callback: CallbackQuery,
        state: FSMContext):
    """Handle category selection."""
    category = callback.data.split(":", 1)[1]
    user_id = str(callback.from_user.id)

    # Get current session
    session = wizard_service.get_session(user_id)
    if not session:
        await callback.answer("❌ جلسه یافت نشد")
        return

    vehicle_data = session.get("vehicle_data", {})
    part_data = {"category": category}

    # Update session with category
    updated_session = wizard_service.update_session(
        user_id,
        state="part_selection",
        part_data=part_data
    )

    if not updated_session:
        await callback.answer("❌ خطا در ذخیره انتخاب")
        return

    # Search for parts
    parts = wizard_service.search_parts(vehicle_data, part_data)

    if not parts:
        await safe_edit_message(
            callback,
            f"❌ برای {vehicle_data.get('brand')} {vehicle_data.get('model')} "
            f"در دسته‌بندی {category} هیچ قطعه‌ای یافت نشد.",
            reply_markup=None
        )
        return

    # Create parts keyboard (limit to 10 parts)
    parts_display = parts[:10]
    buttons = []

    for part in parts_display:
        part_name = part.get("part_name", "نامشخص")
        position = part.get("position", "")
        display_text = f"{part_name}"
        if position:
            display_text += f" ({position})"

        buttons.append([InlineKeyboardButton(
            text=display_text,
            callback_data=f"part:{part.get('id')}"
        )])

    # Add navigation buttons
    buttons.append([InlineKeyboardButton(
        text="🔙 بازگشت", callback_data="back")])
    buttons.append([InlineKeyboardButton(
        text="❌ لغو", callback_data="cancel")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    await safe_edit_message(
        callback,
        f"🚗 **خودرو: {vehicle_data.get('brand')} {vehicle_data.get('model')}**\n"
        f"🔧 **دسته‌بندی: {category}**\n\n"
        "لطفاً قطعه مورد نظر خود را انتخاب کنید:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

    await state.set_state(PartsWizard.part_selection)
    await callback.answer()


@router.callback_query(F.data.startswith("part:"),
                       StateFilter(PartsWizard.part_selection))
async def handle_part_selection(callback: CallbackQuery, state: FSMContext):
    """Handle part selection."""
    part_id = callback.data.split(":", 1)[1]
    user_id = str(callback.from_user.id)

    # Get current session
    session = wizard_service.get_session(user_id)
    if not session:
        await callback.answer("❌ جلسه یافت نشد")
        return

    vehicle_data = session.get("vehicle_data", {})
    part_data = session.get("part_data", {})
    part_data["selected_part_id"] = part_id

    # Update session with selected part
    updated_session = wizard_service.update_session(
        user_id,
        state="confirmation",
        part_data=part_data
    )

    if not updated_session:
        await callback.answer("❌ خطا در ذخیره انتخاب")
        return

    # Create confirmation keyboard
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ تأیید و ادامه", callback_data="confirm")],
        [InlineKeyboardButton(text="🔙 بازگشت", callback_data="back")],
        [InlineKeyboardButton(text="❌ لغو", callback_data="cancel")]
    ])

    await safe_edit_message(
        callback,
        f"🚗 **خودرو: {vehicle_data.get('brand')} {vehicle_data.get('model')}**\n"
        f"🔧 **دسته‌بندی: {part_data.get('category')}**\n"
        f"⚙️ **قطعه انتخاب شده: {part_id}**\n\n"
        "آیا می‌خواهید ادامه دهید؟",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

    await state.set_state(PartsWizard.confirmation)
    await callback.answer()


@router.callback_query(F.data == "confirm",
                       StateFilter(PartsWizard.confirmation))
async def handle_confirmation(callback: CallbackQuery, state: FSMContext):
    """Handle confirmation."""
    user_id = str(callback.from_user.id)

    # Get current session
    session = wizard_service.get_session(user_id)
    if not session:
        await callback.answer("❌ جلسه یافت نشد")
        return

    vehicle_data = session.get("vehicle_data", {})
    part_data = session.get("part_data", {})

    # Create contact capture keyboard
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📱 ارسال شماره تلفن", callback_data="request_contact")],
        [InlineKeyboardButton(text="🔙 بازگشت", callback_data="back")],
        [InlineKeyboardButton(text="❌ لغو", callback_data="cancel")]
    ])

    await safe_edit_message(
        callback,
        f"🚗 **خودرو: {vehicle_data.get('brand')} {vehicle_data.get('model')}**\n"
        f"🔧 **دسته‌بندی: {part_data.get('category')}**\n"
        f"⚙️ **قطعه: {part_data.get('selected_part_id')}**\n\n"
        "برای دریافت قیمت و اطلاعات بیشتر، لطفاً شماره تلفن خود را ارسال کنید:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

    await state.set_state(PartsWizard.contact_capture)
    await callback.answer()


@router.callback_query(F.data == "request_contact",
                       StateFilter(PartsWizard.contact_capture))
async def handle_contact_request(callback: CallbackQuery, state: FSMContext):
    """Handle contact request."""
    await safe_edit_message(
        callback,
        "📱 لطفاً شماره تلفن خود را با استفاده از دکمه زیر ارسال کنید:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📱 ارسال شماره تلفن", callback_data="send_contact")],
            [InlineKeyboardButton(text="🔙 بازگشت", callback_data="back")],
            [InlineKeyboardButton(text="❌ لغو", callback_data="cancel")]
        ])
    )
    await callback.answer()


@router.message(F.contact, StateFilter(PartsWizard.contact_capture))
async def handle_contact_received(message: Message, state: FSMContext):
    """Handle received contact."""
    user_id = str(message.from_user.id)
    contact = message.contact

    # Get current session
    session = wizard_service.get_session(user_id)
    if not session:
        await message.answer("❌ جلسه یافت نشد")
        return

    # Update session with contact data
    contact_data = {
        "phone": contact.phone_number,
        "first_name": contact.first_name,
        "last_name": contact.last_name
    }

    updated_session = wizard_service.update_session(
        user_id,
        state="completed",
        contact_data=contact_data
    )

    if not updated_session:
        await message.answer("❌ خطا در ذخیره اطلاعات تماس")
        return

    vehicle_data = session.get("vehicle_data", {})
    part_data = session.get("part_data", {})

    await message.answer(
        f"✅ **درخواست شما ثبت شد!**\n\n"
        f"🚗 **خودرو: {vehicle_data.get('brand')} {vehicle_data.get('model')}**\n"
        f"🔧 **دسته‌بندی: {part_data.get('category')}**\n"
        f"⚙️ **قطعه: {part_data.get('selected_part_id')}**\n"
        f"📱 **شماره تماس: {contact.phone_number}**\n\n"
        "کارشناسان ما به زودی با شما تماس خواهند گرفت.\n"
        "متشکریم! 🙏",
        parse_mode="Markdown"
    )

    await state.clear()


@router.callback_query(F.data == "back")
async def handle_back(callback: CallbackQuery, state: FSMContext):
    """Handle back navigation."""
    current_state = await state.get_state()
    user_id = str(callback.from_user.id)

    # Get current session
    session = wizard_service.get_session(user_id)
    if not session:
        await callback.answer("❌ جلسه یافت نشد")
        return

    if current_state == PartsWizard.model_selection.state:
        # Go back to brand selection
        brands = wizard_service.get_brands()
        if brands:
            keyboard = create_inline_keyboard(brands, "brand", "brand")
            await safe_edit_message(
                callback,
                "🚗 **راهنمای جستجوی قطعات خودرو**\n\n"
                "لطفاً برند خودروی خود را انتخاب کنید:",
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            await state.set_state(PartsWizard.brand_selection)

    elif current_state == PartsWizard.category_selection.state:
        # Go back to model selection
        vehicle_data = session.get("vehicle_data", {})
        brand = vehicle_data.get("brand")
        if brand:
            models = wizard_service.get_models(brand)
            if models:
                keyboard = create_inline_keyboard(models, "model", "model")
                await safe_edit_message(
                    callback,
                    f"🚗 **برند انتخاب شده: {brand}**\n\n"
                    "لطفاً مدل خودروی خود را انتخاب کنید:",
                    reply_markup=keyboard,
                    parse_mode="Markdown"
                )
                await state.set_state(PartsWizard.model_selection)

    elif current_state == PartsWizard.part_selection.state:
        # Go back to category selection
        vehicle_data = session.get("vehicle_data", {})
        categories = wizard_service.get_categories(
            brand=vehicle_data.get("brand"),
            model=vehicle_data.get("model")
        )
        if categories:
            keyboard = create_inline_keyboard(
                categories, "category", "category")
            await safe_edit_message(
                callback,
                f"🚗 **خودرو: {vehicle_data.get('brand')} {vehicle_data.get('model')}**\n\n"
                "لطفاً نوع قطعه مورد نظر خود را انتخاب کنید:",
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            await state.set_state(PartsWizard.category_selection)

    elif current_state == PartsWizard.confirmation.state:
        # Go back to part selection
        vehicle_data = session.get("vehicle_data", {})
        part_data = session.get("part_data", {})
        parts = wizard_service.search_parts(vehicle_data, part_data)

        if parts:
            parts_display = parts[:10]
            buttons = []

            for part in parts_display:
                part_name = part.get("part_name", "نامشخص")
                position = part.get("position", "")
                display_text = f"{part_name}"
                if position:
                    display_text += f" ({position})"

                buttons.append([InlineKeyboardButton(
                    text=display_text,
                    callback_data=f"part:{part.get('id')}"
                )])

            buttons.append([InlineKeyboardButton(
                text="🔙 بازگشت", callback_data="back")])
            buttons.append([InlineKeyboardButton(
                text="❌ لغو", callback_data="cancel")])

            keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

            await safe_edit_message(
                callback,
                f"🚗 **خودرو: {vehicle_data.get('brand')} {vehicle_data.get('model')}**\n"
                f"🔧 **دسته‌بندی: {part_data.get('category')}**\n\n"
                "لطفاً قطعه مورد نظر خود را انتخاب کنید:",
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            await state.set_state(PartsWizard.part_selection)

    elif current_state == PartsWizard.contact_capture.state:
        # Go back to confirmation
        vehicle_data = session.get("vehicle_data", {})
        part_data = session.get("part_data", {})

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ تأیید و ادامه", callback_data="confirm")],
            [InlineKeyboardButton(text="🔙 بازگشت", callback_data="back")],
            [InlineKeyboardButton(text="❌ لغو", callback_data="cancel")]
        ])

        await safe_edit_message(
            callback,
            f"🚗 **خودرو: {vehicle_data.get('brand')} {vehicle_data.get('model')}**\n"
            f"🔧 **دسته‌بندی: {part_data.get('category')}**\n"
            f"⚙️ **قطعه انتخاب شده: {part_data.get('selected_part_id')}**\n\n"
            "آیا می‌خواهید ادامه دهید؟",
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
        await state.set_state(PartsWizard.confirmation)

    await callback.answer()


@router.callback_query(F.data == "cancel")
async def handle_cancel(callback: CallbackQuery, state: FSMContext):
    """Handle cancellation."""
    user_id = str(callback.from_user.id)

    # Clear session
    wizard_service.clear_session(user_id)

    await safe_edit_message(
        callback,
        "❌ **روند راهنمایی لغو شد.**\n\n"
        "برای شروع مجدد از دستور /wizard استفاده کنید.",
        parse_mode="Markdown"
    )

    await state.clear()
    await callback.answer()


@router.message(StateFilter(PartsWizard))
async def handle_unknown_message(message: Message, state: FSMContext):
    """Handle unknown messages during wizard flow."""
    await message.answer(
        "❓ لطفاً از دکمه‌های موجود استفاده کنید یا برای لغو از /cancel استفاده کنید."
    )
