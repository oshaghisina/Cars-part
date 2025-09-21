"""Bot service for handling Telegram bot business logic."""

from typing import List, Dict
from sqlalchemy.orm import Session
from app.services.search import SearchService
from app.services.ai_service import AIService
from app.services.lead_service import LeadService
from app.services.order_service import OrderService
from app.bot.utils import format_part_confirmation
from app.core.config import settings


class BotService:
    """Service for bot-specific business logic."""

    def __init__(self, db: Session):
        self.db = db
        self.search_service = SearchService(db)
        self.ai_service = AIService(db)
        self.lead_service = LeadService(db)
        self.order_service = OrderService(db)

    def search_and_confirm_part(self, query: str) -> Dict:
        """
        Search for a part and prepare confirmation message.

        Args:
            query: User search query

        Returns:
            Dictionary with search results and confirmation message
        """
        # Try AI-enhanced search first if available
        if settings.ai_enabled and self.ai_service.is_available():
            try:
                ai_result = self.ai_service.intelligent_search(query, limit=1)
                if ai_result["success"] and ai_result["parts"]:
                    return self._format_ai_search_result(ai_result)
            except Exception as e:
                print(f"AI search failed, falling back to basic search: {e}")

        # Fallback to basic search
        results = self.search_service.search_parts(query, limit=1)

        if not results:
            return {
                "found": False,
                "message": (
                    "متأسفانه قطعه مورد نظر یافت نشد. "
                    "لطفاً نام دقیق‌تر قطعه یا مدل خودرو را وارد کنید."
                ),
                "suggestions": [],
            }

        best_result = results[0]
        formatted_result = self.search_service.format_search_result(best_result)

        # Create confirmation message in Persian
        part_name = formatted_result["part_name"]
        vehicle_model = formatted_result["vehicle_model"]

        confirmation_message = format_part_confirmation(part_name, vehicle_model)

        # Add price information if available
        if formatted_result["prices"]:
            best_price = formatted_result["best_price"]
            currency = formatted_result["prices"][0]["currency"]
            confirmation_message += f"\n\n💰 بهترین قیمت: {best_price:,.0f} {currency}"

        return {
            "found": True,
            "message": confirmation_message,
            "part_data": formatted_result,
            "search_score": best_result["score"],
        }

    def search_multiple_parts(self, queries: List[str]) -> Dict:
        """
        Search for multiple parts and prepare summary.

        Args:
            queries: List of search queries

        Returns:
            Dictionary with bulk search results
        """
        if len(queries) > 10:  # Bulk limit
            return {
                "success": False,
                "message": (
                    "تعداد قطعات بیش از حد مجاز است (حداکثر ۱۰ قطعه). "
                    "لطفاً لیست را کوتاه‌تر کنید."
                ),
            }

        results_summary = []
        found_count = 0

        for i, query in enumerate(queries, 1):
            query = query.strip()
            if not query:
                continue

            part_result = self.search_and_confirm_part(query)

            if part_result["found"]:
                found_count += 1
                part_data = part_result["part_data"]
                results_summary.append(
                    {
                        "query": query,
                        "part_name": part_data["part_name"],
                        "vehicle_model": part_data["vehicle_model"],
                        "best_price": part_data["best_price"],
                        "currency": part_data["prices"][0]["currency"]
                        if part_data["prices"]
                        else None,
                    }
                )
            else:
                results_summary.append(
                    {"query": query, "found": False, "message": part_result["message"]}
                )

        # Create summary message
        if found_count == 0:
            summary_message = "متأسفانه هیچ قطعه‌ای یافت نشد."
        elif found_count == len([q for q in queries if q.strip()]):
            summary_message = f"✅ تمام {found_count} قطعه یافت شد."
        else:
            summary_message = (
                f"✅ {found_count} از " f"{len([q for q in queries if q.strip()])} قطعه یافت شد."
            )

        return {
            "success": True,
            "message": summary_message,
            "found_count": found_count,
            "total_queries": len([q for q in queries if q.strip()]),
            "results": results_summary,
        }

    def handle_contact_capture(
        self,
        telegram_user_id: str,
        phone_number: str = None,
        first_name: str = None,
        last_name: str = None,
    ) -> Dict:
        """
        Handle contact capture and lead creation/update.

        Args:
            telegram_user_id: Telegram user ID
            phone_number: Phone number
            first_name: First name
            last_name: Last name

        Returns:
            Dictionary with lead information and next steps
        """
        result = self.lead_service.get_or_create_lead(
            telegram_user_id=telegram_user_id,
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
        )

        return result

    def create_order_from_search_results(
        self, telegram_user_id: str, search_results: List[Dict]
    ) -> Dict:
        """
        Create order from confirmed search results.

        Args:
            telegram_user_id: Telegram user ID
            search_results: List of confirmed search results

        Returns:
            Dictionary with order creation result
        """
        # Get or create lead
        lead_result = self.lead_service.get_or_create_lead(telegram_user_id)

        if not lead_result["lead"]:
            return {
                "success": False,
                "message": lead_result["message"],
                "requires_contact": lead_result.get("requires_contact", False),
            }

        # Prepare order items
        order_items = []
        for result in search_results:
            if result["found"]:
                part_data = result["part_data"]
                order_items.append(
                    {
                        "query_text": result.get("original_query", ""),
                        "matched_part_id": part_data["id"],
                        "qty": 1,
                        "unit": "pcs",
                        "notes": f"Part: {part_data['part_name']} - {part_data['vehicle_model']}",
                    }
                )

        if not order_items:
            return {"success": False, "message": "هیچ قطعه معتبری برای ثبت سفارش یافت نشد."}

        # Create order
        order_result = self.order_service.create_order(
            lead_id=lead_result["lead"].id, order_items=order_items
        )

        return order_result

    def get_order_status(self, telegram_user_id: str, order_id: int = None) -> Dict:
        """
        Get order status for a user.

        Args:
            telegram_user_id: Telegram user ID
            order_id: Optional specific order ID

        Returns:
            Dictionary with order status information
        """
        lead = self.lead_service.get_lead_by_telegram_id(telegram_user_id)

        if not lead:
            return {
                "success": False,
                "message": "اطلاعات شما یافت نشد. لطفاً ابتدا سفارشی ثبت کنید.",
            }

        if order_id:
            # Get specific order
            order = self.order_service.get_order_by_id(order_id)
            if not order or order.lead_id != lead.id:
                return {"success": False, "message": "سفارش مورد نظر یافت نشد."}

            summary = self.order_service.get_order_summary(order)
            return {
                "success": True,
                "order": summary,
                "message": f"وضعیت سفارش #{order.id:05d}: {order.status}",
            }
        else:
            # Get all orders
            orders = self.order_service.get_orders_by_lead(lead.id)

            if not orders:
                return {"success": True, "orders": [], "message": "هنوز سفارشی ثبت نکرده‌اید."}

            summaries = [self.order_service.get_order_summary(order) for order in orders]

            return {
                "success": True,
                "orders": summaries,
                "message": f"شما {len(orders)} سفارش دارید.",
            }

    def _format_ai_search_result(self, ai_result: Dict) -> Dict:
        """Format AI search result for bot response."""
        if not ai_result["success"] or not ai_result["parts"]:
            return {
                "found": False,
                "message": (
                    "متأسفانه قطعه مورد نظر یافت نشد. "
                    "لطفاً نام دقیق‌تر قطعه یا مدل خودرو را وارد کنید."
                ),
                "suggestions": ai_result.get("suggestions", []),
            }

        best_part = ai_result["parts"][0]
        query_analysis = ai_result.get("query_analysis", {})
        suggestions = ai_result.get("suggestions", [])

        # Create enhanced confirmation message
        part_name = best_part["part_name"]
        vehicle_model = best_part["vehicle_model"]
        search_type = ai_result.get("search_type", "ai")

        confirmation_message = "🔍 **نتایج جستجوی هوشمند**\n\n"
        confirmation_message += f"**{part_name}** ({vehicle_model})\n"
        confirmation_message += f"برند: {best_part['brand_oem']}\n"

        if best_part.get("oem_code"):
            confirmation_message += f"کد OEM: {best_part['oem_code']}\n"

        confirmation_message += f"دسته بندی: {best_part['category']}\n"

        if best_part.get("best_price"):
            confirmation_message += (
                f"💰 قیمت: {best_part['best_price']:,} " f"{best_part['prices'][0]['currency']}\n"
            )

        # Add AI insights
        if query_analysis:
            confirmation_message += "\n🤖 **تحلیل هوشمند:**\n"
            if query_analysis.get("car_brand"):
                confirmation_message += f"• برند تشخیص داده شده: {query_analysis['car_brand']}\n"
            if query_analysis.get("part_type"):
                confirmation_message += f"• نوع قطعه: {query_analysis['part_type']}\n"
            if query_analysis.get("position"):
                confirmation_message += f"• موقعیت: {query_analysis['position']}\n"

        # Add suggestions if available
        if suggestions:
            confirmation_message += "\n💡 **پیشنهادات هوشمند:**\n"
            for i, suggestion in enumerate(suggestions[:2], 1):
                confirmation_message += f"{i}. {suggestion}\n"

        return {
            "found": True,
            "parts": ai_result["parts"],
            "message": confirmation_message,
            "suggestions": suggestions,
            "search_type": search_type,
            "query_analysis": query_analysis,
        }
