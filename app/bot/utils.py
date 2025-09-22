"""Bot utility functions."""

from app.core.config import settings


def is_admin(user_id: int) -> bool:
    """Check if user is admin."""
    return user_id in settings.admin_telegram_ids_list


def format_part_confirmation(part_name: str, vehicle_model: str) -> str:
    """Format part confirmation message in Persian."""
    return f"آیا شما به دنبال {part_name} {vehicle_model} هستید؟"


def format_order_confirmation(order_id: int) -> str:
    """Format order confirmation message in Persian."""
    return f"سفارش شما با موفقیت ثبت شد.\nشماره سفارش: #ORD-{order_id}\n" f"تیم ما به زودی با شما تماس خواهد گرفت."


def validate_bulk_query(lines: list) -> tuple[bool, str]:
    """Validate bulk query format and limits."""
    if not lines:
        return False, "لیست قطعات خالی است."

    if len(lines) > settings.bulk_limit_default:
        return False, (
            f"تعداد قطعات بیش از حد مجاز است " f"({settings.bulk_limit_default}). " f"لطفاً لیست را کوتاه‌تر کنید."
        )

    # Filter out empty lines
    valid_lines = [line.strip() for line in lines if line.strip()]

    if not valid_lines:
        return False, "هیچ قطعه معتبری در لیست یافت نشد."

    return True, ""
