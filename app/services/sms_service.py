"""SMS service for handling Melipayamak SMS operations."""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.sms_models import SMSLog, SMSTemplate, StockAlert
from app.schemas.sms_schemas import SMSResponse

logger = logging.getLogger(__name__)


class SMSService:
    """Core SMS service for Melipayamak integration."""

    def __init__(self, db: Session):
        """Initialize SMS service with database session."""
        self.db = db
        self.api = None
        self._initialize_api()

    def _initialize_api(self):
        """Initialize Melipayamak API client."""
        try:
            if settings.sms_enabled and settings.melipayamak_username != "CHANGEME":
                from melipayamak import Api

                self.api = Api(
                    username=settings.melipayamak_username, password=settings.melipayamak_password
                )
                logger.info("SMS service initialized successfully")
            else:
                logger.warning("SMS service disabled or not configured")
        except Exception as e:
            logger.error(f"Failed to initialize SMS service: {e}")
            self.api = None

    async def send_sms(
        self,
        phone_number: str,
        message: str,
        template_id: Optional[int] = None,
        language: str = "fa",
    ) -> SMSResponse:
        """
        Send SMS message using Melipayamak API.

        Args:
            phone_number: Recipient phone number
            message: SMS message content
            template_id: Optional template ID for tracking
            language: Message language (fa/en)

        Returns:
            SMSResponse with status and details
        """
        # Validate phone number
        if not self._validate_phone_number(phone_number):
            return SMSResponse(
                success=False, message="Invalid phone number format", message_id=None, cost=0.0
            )

        # Create SMS log entry
        sms_log = SMSLog(
            recipient_phone=phone_number, content=message, template_id=template_id, status="pending"
        )
        self.db.add(sms_log)
        self.db.commit()

        try:
            if not self.api:
                if settings.app_env == "development" or settings.sms_fallback_in_production:
                    logger.warning(
                        "SMS service not initialized - "
                        "using fallback (dev or allowed in production)"
                    )
                    sms_log.status = "sent"
                    sms_log.sent_at = datetime.utcnow()
                    sms_log.provider = (
                        "development"
                        if settings.app_env == "development"
                        else "fallback"
                    )
                    sms_log.cost = 0.0
                    self.db.commit()
                    return SMSResponse(
                        success=True,
                        message=(
                            "SMS simulated in development mode"
                            if settings.app_env == "development"
                            else "SMS simulated (production fallback enabled)"
                        ),
                        message_id=sms_log.id,
                        cost=0.0,
                    )
                else:
                    logger.error("SMS service not initialized - check configuration")
                    sms_log.status = "failed"
                    sms_log.error_message = "SMS service not initialized"
                    self.db.commit()
                    return SMSResponse(
                        success=False,
                        message="SMS service not available",
                        message_id=None,
                        cost=0.0,
                    )

            # Send SMS via Melipayamak
            sms_client = self.api.sms()
            response = sms_client.send(
                to=phone_number, _from=settings.sms_sender_number, text=message
            )

            # Update SMS log with response
            # Melipayamak returns RetStatus: 1 for success, StrRetStatus: "Ok"
            if response and response.get("RetStatus") == 1:
                sms_log.status = "sent"
                sms_log.sent_at = datetime.utcnow()
                sms_log.external_id = response.get("Value", "")
                sms_log.cost = self._calculate_sms_cost(message)

                self.db.commit()

                return SMSResponse(
                    success=True,
                    message="SMS sent successfully",
                    message_id=sms_log.id,
                    cost=sms_log.cost,
                )
            else:
                error_msg = (
                    response.get("StrRetStatus", "Unknown error") if response else "No response"
                )
                sms_log.status = "failed"
                sms_log.error_message = error_msg
                self.db.commit()

                return SMSResponse(
                    success=False,
                    message=f"SMS sending failed: {error_msg}",
                    message_id=sms_log.id,
                    cost=0.0,
                )

        except Exception as e:
            logger.error(f"SMS sending error: {e}")
            sms_log.status = "failed"
            sms_log.error_message = str(e)
            self.db.commit()

            return SMSResponse(
                success=False,
                message=f"SMS sending error: {str(e)}",
                message_id=sms_log.id,
                cost=0.0,
            )

    async def send_template_sms(
        self, phone_number: str, template_name: str, variables: Dict[str, str], language: str = "fa"
    ) -> SMSResponse:
        """
        Send SMS using a predefined template.

        Args:
            phone_number: Recipient phone number
            template_name: Template name to use
            variables: Variables to replace in template
            language: Message language (fa/en)

        Returns:
            SMSResponse with status and details
        """
        # Get template
        template = (
            self.db.query(SMSTemplate)
            .filter(SMSTemplate.name == template_name, SMSTemplate.is_active)
            .first()
        )

        if not template:
            return SMSResponse(
                success=False,
                message=f"Template '{template_name}' not found",
                message_id=None,
                cost=0.0,
            )

        # Get template content based on language
        content = template.content_fa if language == "fa" else template.content_en
        if not content:
            return SMSResponse(
                success=False,
                message=f"Template content not available for language '{language}'",
                message_id=None,
                cost=0.0,
            )

        # Replace variables in template
        message = self._replace_template_variables(content, variables)

        # Send SMS
        return await self.send_sms(
            phone_number=phone_number, message=message, template_id=template.id, language=language
        )

    async def send_bulk_sms(
        self, phone_numbers: List[str], message: str, template_id: Optional[int] = None
    ) -> List[SMSResponse]:
        """
        Send SMS to multiple recipients.

        Args:
            phone_numbers: List of recipient phone numbers
            message: SMS message content
            template_id: Optional template ID for tracking

        Returns:
            List of SMSResponse objects
        """
        results = []

        # Rate limiting: send in batches to avoid overwhelming the API
        batch_size = 10
        for i in range(0, len(phone_numbers), batch_size):
            batch = phone_numbers[i:i + batch_size]

            # Send batch concurrently
            tasks = [self.send_sms(phone, message, template_id) for phone in batch]

            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            results.extend(batch_results)

            # Add delay between batches to respect rate limits
            if i + batch_size < len(phone_numbers):
                await asyncio.sleep(1)

        return results

    async def create_stock_alert(
        self, user_id: Optional[int], part_id: int, phone_number: str, email: Optional[str] = None
    ) -> bool:
        """
        Create a stock alert for a user.

        Args:
            user_id: User ID (optional)
            part_id: Part ID to monitor
            phone_number: Phone number for notifications
            email: Email for notifications (optional)

        Returns:
            True if alert created successfully
        """
        try:
            # Check if alert already exists
            existing_alert = (
                self.db.query(StockAlert)
                .filter(
                    StockAlert.part_id == part_id,
                    StockAlert.phone_number == phone_number,
                    StockAlert.is_active,
                )
                .first()
            )

            if existing_alert:
                return True  # Alert already exists

            # Create new stock alert
            stock_alert = StockAlert(
                user_id=user_id, part_id=part_id, phone_number=phone_number, email=email
            )

            self.db.add(stock_alert)
            self.db.commit()

            logger.info(f"Stock alert created for part {part_id}, phone {phone_number}")
            return True

        except Exception as e:
            logger.error(f"Failed to create stock alert: {e}")
            self.db.rollback()
            return False

    async def process_stock_alerts(self, part_id: int) -> int:
        """
        Process stock alerts for a part that's back in stock.

        Args:
            part_id: Part ID that's back in stock

        Returns:
            Number of alerts processed
        """
        try:
            # Get active stock alerts for this part
            alerts = (
                self.db.query(StockAlert)
                .filter(
                    StockAlert.part_id == part_id,
                    StockAlert.is_active,
                    StockAlert.is_notified is False,
                )
                .all()
            )

            if not alerts:
                return 0

            # Get part information
            from app.db.models import Part

            part = self.db.query(Part).filter(Part.id == part_id).first()
            if not part:
                return 0

            processed_count = 0

            for alert in alerts:
                try:
                    # Send stock alert SMS
                    variables = {
                        "part_name": part.part_name,
                        "brand": part.brand_oem,
                        "part_id": str(part.id),
                    }

                    response = await self.send_template_sms(
                        phone_number=alert.phone_number,
                        template_name="stock_alert",
                        variables=variables,
                        language="fa",
                    )

                    if response.success:
                        alert.is_notified = True
                        alert.notified_at = datetime.utcnow()
                        processed_count += 1

                        logger.info(f"Stock alert sent to {alert.phone_number} for part {part_id}")
                    else:
                        logger.error(f"Failed to send stock alert: {response.message}")

                except Exception as e:
                    logger.error(f"Error processing stock alert {alert.id}: {e}")

            self.db.commit()
            return processed_count

        except Exception as e:
            logger.error(f"Failed to process stock alerts: {e}")
            self.db.rollback()
            return 0

    def get_sms_analytics(
        self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
    ) -> Dict:
        """
        Get SMS analytics for the given date range.

        Args:
            start_date: Start date for analytics
            end_date: End date for analytics

        Returns:
            Dictionary with SMS analytics
        """
        try:
            query = self.db.query(SMSLog)

            if start_date:
                query = query.filter(SMSLog.created_at >= start_date)
            if end_date:
                query = query.filter(SMSLog.created_at <= end_date)

            logs = query.all()

            total_sent = len(logs)
            successful = len([log for log in logs if log.status == "sent"])
            failed = len([log for log in logs if log.status == "failed"])
            total_cost = sum(log.cost or 0 for log in logs)

            return {
                "total_sent": total_sent,
                "successful": successful,
                "failed": failed,
                "success_rate": (successful / total_sent * 100) if total_sent > 0 else 0,
                "total_cost": float(total_cost),
                "average_cost": float(total_cost / total_sent) if total_sent > 0 else 0,
            }

        except Exception as e:
            logger.error(f"Failed to get SMS analytics: {e}")
            return {
                "total_sent": 0,
                "successful": 0,
                "failed": 0,
                "success_rate": 0,
                "total_cost": 0.0,
                "average_cost": 0.0,
            }

    def _validate_phone_number(self, phone_number: str) -> bool:
        """Validate Iranian phone number format."""
        # Remove any non-digit characters
        cleaned = "".join(filter(str.isdigit, phone_number))

        # Iranian mobile numbers: 09xxxxxxxxx (11 digits)
        if len(cleaned) == 11 and cleaned.startswith("09"):
            return True

        # International format: +989xxxxxxxxx
        if len(cleaned) == 12 and cleaned.startswith("989"):
            return True

        return False

    def _replace_template_variables(self, template: str, variables: Dict[str, str]) -> str:
        """Replace variables in template string."""
        message = template
        for key, value in variables.items():
            message = message.replace(f"{{{key}}}", str(value))
        return message

    def _calculate_sms_cost(self, message: str) -> float:
        """Calculate SMS cost based on message length."""
        # Basic cost calculation (adjust based on Melipayamak pricing)
        message_length = len(message)
        if message_length <= 160:
            return 0.1  # 1 SMS
        else:
            # Calculate number of SMS parts
            sms_parts = (message_length - 1) // 153 + 1  # 153 chars per part after first
            return sms_parts * 0.1
