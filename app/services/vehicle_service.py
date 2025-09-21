"""Vehicle service for managing brands, models, and trims."""

from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional, Dict, Any
import logging

from app.db.models import VehicleBrand, VehicleModel, VehicleTrim

logger = logging.getLogger(__name__)


class VehicleService:
    """Service for vehicle-related operations."""

    def __init__(self, db: Session):
        self.db = db

    # Brand operations
    def get_brands(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> List[VehicleBrand]:
        """Get brands with filtering options."""
        query = self.db.query(VehicleBrand)

        if is_active is not None:
            query = query.filter(VehicleBrand.is_active == is_active)

        if search:
            search_filter = or_(
                VehicleBrand.name.ilike(f"%{search}%"),
                VehicleBrand.name_fa.ilike(f"%{search}%"),
                VehicleBrand.name_cn.ilike(f"%{search}%"),
            )
            query = query.filter(search_filter)

        return (
            query.order_by(VehicleBrand.sort_order, VehicleBrand.name)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_brand_by_id(self, brand_id: int) -> Optional[VehicleBrand]:
        """Get brand by ID."""
        return self.db.query(VehicleBrand).filter(VehicleBrand.id == brand_id).first()

    def create_brand(self, brand_data: Dict[str, Any]) -> Optional[VehicleBrand]:
        """Create a new brand."""
        try:
            brand = VehicleBrand(**brand_data)
            self.db.add(brand)
            self.db.commit()
            self.db.refresh(brand)
            return brand
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating brand: {e}")
            return None

    def update_brand(self, brand_id: int, brand_data: Dict[str, Any]) -> Optional[VehicleBrand]:
        """Update an existing brand."""
        try:
            brand = self.get_brand_by_id(brand_id)
            if not brand:
                return None

            for key, value in brand_data.items():
                if hasattr(brand, key):
                    setattr(brand, key, value)

            self.db.commit()
            self.db.refresh(brand)
            return brand
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating brand: {e}")
            return None

    def delete_brand(self, brand_id: int) -> bool:
        """Delete a brand (soft delete by setting is_active=False)."""
        try:
            brand = self.get_brand_by_id(brand_id)
            if not brand:
                return False

            brand.is_active = False  # type: ignore[assignment]
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting brand: {e}")
            return False

    # Model operations
    def get_models(
        self,
        skip: int = 0,
        limit: int = 100,
        brand_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> List[VehicleModel]:
        """Get models with filtering options."""
        query = self.db.query(VehicleModel)

        if brand_id:
            query = query.filter(VehicleModel.brand_id == brand_id)

        if is_active is not None:
            query = query.filter(VehicleModel.is_active == is_active)

        if search:
            search_filter = or_(
                VehicleModel.name.ilike(f"%{search}%"),
                VehicleModel.name_fa.ilike(f"%{search}%"),
                VehicleModel.name_cn.ilike(f"%{search}%"),
            )
            query = query.filter(search_filter)

        return (
            query.order_by(VehicleModel.sort_order, VehicleModel.name)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_models_by_brand(self, brand_id: int) -> List[VehicleModel]:
        "Get all models for a specific brand." ""
        return (
            self.db.query(VehicleModel)
            .filter(VehicleModel.brand_id == brand_id, VehicleModel.is_active)
            .order_by(VehicleModel.sort_order, VehicleModel.name)
            .all()
        )

    def get_model_by_id(self, model_id: int) -> Optional[VehicleModel]:
        """Get model by ID."""
        return self.db.query(VehicleModel).filter(VehicleModel.id == model_id).first()

    def create_model(self, model_data: Dict[str, Any]) -> Optional[VehicleModel]:
        """Create a new model."""
        try:
            model = VehicleModel(**model_data)
            self.db.add(model)
            self.db.commit()
            self.db.refresh(model)
            return model
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating model: {e}")
            return None

    def update_model(self, model_id: int, model_data: Dict[str, Any]) -> Optional[VehicleModel]:
        """Update an existing model."""
        try:
            model = self.get_model_by_id(model_id)
            if not model:
                return None

            for key, value in model_data.items():
                if hasattr(model, key):
                    setattr(model, key, value)

            self.db.commit()
            self.db.refresh(model)
            return model
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating model: {e}")
            return None

    def delete_model(self, model_id: int) -> bool:
        """Delete a model (soft delete by setting is_active=False)."""
        try:
            model = self.get_model_by_id(model_id)
            if not model:
                return False

            model.is_active = False  # type: ignore[assignment]
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting model: {e}")
            return False

    # Trim operations
    def get_trims(
        self,
        skip: int = 0,
        limit: int = 100,
        model_id: Optional[int] = None,
        brand_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> List[VehicleTrim]:
        """Get trims with filtering options."""
        query = self.db.query(VehicleTrim)

        if model_id:
            query = query.filter(VehicleTrim.model_id == model_id)

        if brand_id:
            query = query.join(VehicleModel).filter(VehicleModel.brand_id == brand_id)

        if is_active is not None:
            query = query.filter(VehicleTrim.is_active == is_active)

        if search:
            search_filter = or_(
                VehicleTrim.name.ilike(f"%{search}%"),
                VehicleTrim.name_fa.ilike(f"%{search}%"),
                VehicleTrim.engine_type.ilike(f"%{search}%"),
            )
            query = query.filter(search_filter)

        return (
            query.order_by(VehicleTrim.sort_order, VehicleTrim.name).offset(skip).limit(limit).all()
        )

    def get_trims_by_model(self, model_id: int) -> List[VehicleTrim]:
        "Get all trims for a specific model." ""
        return (
            self.db.query(VehicleTrim)
            .filter(VehicleTrim.model_id == model_id, VehicleTrim.is_active)
            .order_by(VehicleTrim.sort_order, VehicleTrim.name)
            .all()
        )

    def get_trim_by_id(self, trim_id: int) -> Optional[VehicleTrim]:
        """Get trim by ID."""
        return self.db.query(VehicleTrim).filter(VehicleTrim.id == trim_id).first()

    def create_trim(self, trim_data: Dict[str, Any]) -> Optional[VehicleTrim]:
        """Create a new trim."""
        try:
            trim = VehicleTrim(**trim_data)
            self.db.add(trim)
            self.db.commit()
            self.db.refresh(trim)
            return trim
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating trim: {e}")
            return None

    def update_trim(self, trim_id: int, trim_data: Dict[str, Any]) -> Optional[VehicleTrim]:
        """Update an existing trim."""
        try:
            trim = self.get_trim_by_id(trim_id)
            if not trim:
                return None

            for key, value in trim_data.items():
                if hasattr(trim, key):
                    setattr(trim, key, value)

            self.db.commit()
            self.db.refresh(trim)
            return trim
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating trim: {e}")
            return None

    def delete_trim(self, trim_id: int) -> bool:
        """Delete a trim (soft delete by setting is_active=False)."""
        try:
            trim = self.get_trim_by_id(trim_id)
            if not trim:
                return False

            trim.is_active = False  # type: ignore[assignment]
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting trim: {e}")
            return False

    # Utility methods
    def get_brand_model_trim_tree(self) -> List[Dict[str, Any]]:
        """Get complete brand -> model -> trim hierarchy."""
        brands = self.db.query(VehicleBrand).filter(VehicleBrand.is_active).all()

        result = []
        for brand in brands:
            brand_data = {
                "id": brand.id,
                "name": brand.name,
                "name_fa": brand.name_fa,
                "name_cn": brand.name_cn,
                "logo_url": brand.logo_url,
                "models": [],
            }

            models = self.get_models_by_brand(int(brand.id))  # type: ignore[arg-type]
            for model in models:
                model_data = {
                    "id": model.id,
                    "name": model.name,
                    "name_fa": model.name_fa,
                    "name_cn": model.name_cn,
                    "generation": model.generation,
                    "body_type": model.body_type,
                    "trims": [],
                }

                trims = self.get_trims_by_model(int(model.id))  # type: ignore[arg-type]
                for trim in trims:
                    trim_data = {
                        "id": trim.id,
                        "name": trim.name,
                        "name_fa": trim.name_fa,
                        "engine_type": trim.engine_type,
                        "engine_code": trim.engine_code,
                        "year_from": trim.year_from,
                        "year_to": trim.year_to,
                    }
                    model_data["trims"].append(trim_data)

                brand_data["models"].append(model_data)

            result.append(brand_data)

        return result

    def search_vehicles(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search across brands, models, and trims."""
        results = []

        # Search brands
        brands = (
            self.db.query(VehicleBrand)
            .filter(
                VehicleBrand.is_active,
                or_(
                    VehicleBrand.name.ilike(f"%{query}%"), VehicleBrand.name_fa.ilike(f"%{query}%")
                ),
            )
            .limit(limit)
            .all()
        )

        for brand in brands:
            results.append(
                {
                    "type": "brand",
                    "id": brand.id,
                    "name": brand.name,
                    "name_fa": brand.name_fa,
                    "description": f"Brand: {brand.name}",
                }
            )

        # Search models
        models = (
            self.db.query(VehicleModel)
            .join(VehicleBrand)
            .filter(
                VehicleModel.is_active,
                VehicleBrand.is_active,
                or_(
                    VehicleModel.name.ilike(f"%{query}%"), VehicleModel.name_fa.ilike(f"%{query}%")
                ),
            )
            .limit(limit)
            .all()
        )

        for model in models:
            results.append(
                {
                    "type": "model",
                    "id": model.id,
                    "name": model.name,
                    "name_fa": model.name_fa,
                    "brand_name": model.brand.name,
                    "description": f"{model.brand.name} {model.name}",
                }
            )

        # Search trims
        trims = (
            self.db.query(VehicleTrim)
            .join(VehicleModel)
            .join(VehicleBrand)
            .filter(
                VehicleTrim.is_active,
                VehicleModel.is_active,
                VehicleBrand.is_active,
                or_(
                    VehicleTrim.name.ilike(f"%{query}%"),
                    VehicleTrim.name_fa.ilike(f"%{query}%"),
                    VehicleTrim.engine_type.ilike(f"%{query}%"),
                ),
            )
            .limit(limit)
            .all()
        )

        for trim in trims:
            results.append(
                {
                    "type": "trim",
                    "id": trim.id,
                    "name": trim.name,
                    "name_fa": trim.name_fa,
                    "brand_name": trim.model.brand.name,
                    "model_name": trim.model.name,
                    "engine_type": trim.engine_type,
                    "description": f"{trim.model.brand.name} {trim.model.name} {trim.name}",
                }
            )

        return results
