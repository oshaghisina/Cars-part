"""Wizard service for managing guided part search flow."""

from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from app.db.models import Part, WizardSession


class WizardService:
    """Service for managing wizard sessions and flow logic."""

    def __init__(self, db: Session):
        self.db = db

    def create_session(self, user_id: str, state: str = "start") -> WizardSession:
        """Create a new wizard session."""
        session = WizardSession(user_id=user_id, state=state)
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_session(self, user_id: str) -> Optional[WizardSession]:
        """Get existing wizard session for user."""
        return self.db.query(WizardSession).filter(WizardSession.user_id == user_id).first()

    def update_session_state(self, user_id: str, state: str) -> bool:
        """Update wizard session state."""
        session = self.get_session(user_id)
        if session:
            session.state = state
            self.db.commit()
            return True
        return False

    def update_vehicle_data(self, user_id: str, vehicle_data: Dict[str, Any]) -> bool:
        """Update vehicle data in wizard session."""
        session = self.get_session(user_id)
        if session:
            session.set_vehicle_data(vehicle_data)
            self.db.commit()
            return True
        return False

    def update_part_data(self, user_id: str, part_data: Dict[str, Any]) -> bool:
        """Update part data in wizard session."""
        session = self.get_session(user_id)
        if session:
            session.set_part_data(part_data)
            self.db.commit()
            return True
        return False

    def update_contact_data(self, user_id: str, contact_data: Dict[str, Any]) -> bool:
        """Update contact data in wizard session."""
        session = self.get_session(user_id)
        if session:
            session.set_contact_data(contact_data)
            self.db.commit()
            return True
        return False

    def complete_session(self, user_id: str) -> bool:
        """Mark wizard session as completed."""
        return self.update_session_state(user_id, "completed")

    def get_available_brands(self) -> List[str]:
        """Get list of available car brands."""
        brands = self.db.query(Part.brand_oem).distinct().all()
        return [brand[0] for brand in brands if brand[0]]

    def get_available_models(self, brand: str) -> List[str]:
        """Get list of available models for a brand."""
        models = self.db.query(Part.vehicle_model).filter(Part.brand_oem == brand).distinct().all()
        return [model[0] for model in models if model[0]]

    def get_available_categories(self, brand: str = None, model: str = None) -> List[str]:
        """Get list of available part categories."""
        query = self.db.query(Part.category).distinct()

        if brand:
            query = query.filter(Part.brand_oem == brand)
        if model:
            query = query.filter(Part.vehicle_model == model)

        categories = query.all()
        return [category[0] for category in categories if category[0]]

    def get_available_parts(
        self, brand: str = None, model: str = None, category: str = None
    ) -> List[Dict[str, Any]]:
        """Get list of available parts with optional filters."""
        query = self.db.query(Part)

        if brand:
            query = query.filter(Part.brand_oem == brand)
        if model:
            query = query.filter(Part.vehicle_model == model)
        if category:
            query = query.filter(Part.category == category)

        parts = query.all()
        return [
            {
                "id": part.id,
                "part_name": part.part_name,
                "brand_oem": part.brand_oem,
                "vehicle_model": part.vehicle_model,
                "category": part.category,
                "subcategory": part.subcategory,
                "position": part.position,
                "oem_code": part.oem_code,
            }
            for part in parts
        ]

    def search_parts_by_criteria(
        self, vehicle_data: Dict[str, Any], part_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Search parts based on collected wizard data."""
        query = self.db.query(Part)

        # Apply vehicle filters
        if vehicle_data.get("brand"):
            query = query.filter(Part.brand_oem == vehicle_data["brand"])
        if vehicle_data.get("model"):
            query = query.filter(Part.vehicle_model == vehicle_data["model"])
        if vehicle_data.get("year"):
            query = query.filter(
                Part.model_year_from <= vehicle_data["year"],
                Part.model_year_to >= vehicle_data["year"],
            )

        # Apply part filters
        if part_data.get("category"):
            query = query.filter(Part.category == part_data["category"])
        if part_data.get("subcategory"):
            query = query.filter(Part.subcategory == part_data["subcategory"])
        if part_data.get("part_name"):
            query = query.filter(Part.part_name.ilike(f"%{part_data['part_name']}%"))

        parts = query.all()
        return [
            {
                "id": part.id,
                "part_name": part.part_name,
                "brand_oem": part.brand_oem,
                "vehicle_model": part.vehicle_model,
                "category": part.category,
                "subcategory": part.subcategory,
                "position": part.position,
                "oem_code": part.oem_code,
                "unit": part.unit,
                "pack_size": part.pack_size,
            }
            for part in parts
        ]

    def clear_session(self, user_id: str) -> bool:
        """Clear wizard session data."""
        session = self.get_session(user_id)
        if session:
            self.db.delete(session)
            self.db.commit()
            return True
        return False
