"""Lead service for managing customer information."""

from typing import Dict, Optional

from sqlalchemy.orm import Session

from app.db.models import Lead


class LeadService:
    """Service for managing leads/customers."""

    def __init__(self, db: Session):
        self.db = db

    def get_or_create_lead(
        self,
        telegram_user_id: str,
        phone_number: str = None,
        first_name: str = None,
        last_name: str = None,
    ) -> Dict:
        """
        Get existing lead or create new one.

        Args:
            telegram_user_id: Telegram user ID
            phone_number: Phone number in E.164 format
            first_name: First name
            last_name: Last name

        Returns:
            Dictionary with lead information and status
        """
        # Check if lead already exists
        existing_lead = self.db.query(Lead).filter(Lead.telegram_user_id == telegram_user_id).first()

        if existing_lead:
            # Update existing lead if new information provided
            updated = False

            if phone_number and phone_number != existing_lead.phone_e164:
                existing_lead.phone_e164 = phone_number
                updated = True

            if first_name and first_name != existing_lead.first_name:
                existing_lead.first_name = first_name
                updated = True

            if last_name and last_name != existing_lead.last_name:
                existing_lead.last_name = last_name
                updated = True

            if updated:
                self.db.commit()

            return {
                "lead": existing_lead,
                "created": False,
                "updated": updated,
                "message": "اطلاعات شما به‌روزرسانی شد" if updated else "اطلاعات شما موجود است",
            }
        else:
            # Create new lead
            if not phone_number:
                return {
                    "lead": None,
                    "created": False,
                    "updated": False,
                    "message": "لطفاً شماره تماس خود را ارسال کنید",
                    "requires_contact": True,
                }

            new_lead = Lead(
                telegram_user_id=telegram_user_id,
                phone_e164=phone_number,
                first_name=first_name,
                last_name=last_name,
                consent=True,
            )

            self.db.add(new_lead)
            self.db.commit()
            self.db.refresh(new_lead)

            return {
                "lead": new_lead,
                "created": True,
                "updated": False,
                "message": "اطلاعات شما با موفقیت ثبت شد",
            }

    def get_lead_by_telegram_id(self, telegram_user_id: str) -> Optional[Lead]:
        """Get lead by Telegram user ID."""
        return self.db.query(Lead).filter(Lead.telegram_user_id == telegram_user_id).first()

    def update_lead_info(self, lead_id: int, **kwargs) -> Dict:
        """Update lead information."""
        lead = self.db.query(Lead).filter(Lead.id == lead_id).first()

        if not lead:
            return {"success": False, "message": "Lead not found"}

        for key, value in kwargs.items():
            if hasattr(lead, key) and value is not None:
                setattr(lead, key, value)

        self.db.commit()

        return {"success": True, "message": "Lead updated successfully", "lead": lead}
