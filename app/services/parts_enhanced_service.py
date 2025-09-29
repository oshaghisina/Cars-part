"""
Enhanced parts service with stock and pricing integration.
"""

import logging
from decimal import Decimal
from typing import Dict, List, Optional, Tuple

from sqlalchemy import Numeric, cast, func, or_
from sqlalchemy.orm import Session, joinedload

from app.db.models import Part, PartCategory
from app.models.stock_models import PartPrice, StockLevel
from app.services.logging_enhancements import (
    PartsAuditLogger,
    PartsErrorLogger,
    log_database_operation,
)

logger = logging.getLogger(__name__)


class PartsEnhancedService:
    """Enhanced parts service with stock and pricing support."""

    def __init__(self, db: Session):
        self.db = db

    def _build_parts_query(
        self,
        *,
        status: Optional[str] = None,
        category: Optional[str] = None,
        category_id: Optional[int] = None,
        vehicle_make: Optional[str] = None,
        vehicle_model: Optional[str] = None,
        vehicle_trim: Optional[str] = None,
        search: Optional[str] = None,
        price_min: Optional[Decimal] = None,
        price_max: Optional[Decimal] = None,
    ):
        """Create a filtered SQLAlchemy query for parts with stock and pricing."""
        join_price = price_min is not None or price_max is not None

        query = self.db.query(Part)
        if join_price:
            query = query.outerjoin(PartPrice)

        query = query.options(joinedload(Part.stock_level), joinedload(Part.price_info))

        if status:
            query = query.filter(Part.status == status)
        if category:
            query = query.filter(Part.category == category)
        if category_id:
            query = query.filter(Part.category_id == category_id)
        if vehicle_make:
            query = query.filter(Part.vehicle_make == vehicle_make)
        if vehicle_model:
            query = query.filter(Part.vehicle_model == vehicle_model)
        if vehicle_trim:
            query = query.filter(Part.vehicle_trim == vehicle_trim)

        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Part.part_name.ilike(search_term),
                    Part.oem_code.ilike(search_term),
                    Part.vehicle_model.ilike(search_term),
                    Part.brand_oem.ilike(search_term),
                )
            )

        if join_price:
            price_expr = cast(
                func.nullif(func.coalesce(PartPrice.sale_price, PartPrice.list_price), ""),
                Numeric(12, 2),
            )

            if price_min is not None:
                query = query.filter(price_expr >= price_min)
            if price_max is not None:
                query = query.filter(price_expr <= price_max)

        return query

    @log_database_operation("parts", "SELECT")
    def get_parts_with_total(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        category: Optional[str] = None,
        category_id: Optional[int] = None,
        vehicle_make: Optional[str] = None,
        vehicle_model: Optional[str] = None,
        vehicle_trim: Optional[str] = None,
        search: Optional[str] = None,
        price_min: Optional[Decimal] = None,
        price_max: Optional[Decimal] = None,
    ) -> Tuple[List[Part], int]:
        """Get parts with stock and pricing info, plus total count."""
        try:
            # Get total count
            count_query = self._build_parts_query(
                status=status,
                category=category,
                category_id=category_id,
                vehicle_make=vehicle_make,
                vehicle_model=vehicle_model,
                vehicle_trim=vehicle_trim,
                search=search,
                price_min=price_min,
                price_max=price_max,
            )
            total = count_query.count()

            # Get paginated results
            query = self._build_parts_query(
                status=status,
                category=category,
                category_id=category_id,
                vehicle_make=vehicle_make,
                vehicle_model=vehicle_model,
                vehicle_trim=vehicle_trim,
                search=search,
                price_min=price_min,
                price_max=price_max,
            )
            parts = query.offset(skip).limit(limit).all()

            return parts, total

        except Exception as e:
            print(f"Error in get_parts_with_total: {e}")
            # Return empty results on error to prevent 500s
            return [], 0

    def get_part_by_id(self, part_id: int) -> Optional[Part]:
        """Get a single part with stock and pricing info."""
        try:
            return (
                self.db.query(Part)
                .options(joinedload(Part.stock_level), joinedload(Part.price_info))
                .filter(Part.id == part_id)
                .first()
            )
        except Exception as e:
            print(f"Error in get_part_by_id: {e}")
            return None

    @log_database_operation("parts", "INSERT")
    def create_part(self, part_data: Dict, user_id: Optional[int] = None) -> Optional[Part]:
        """Create a new part."""
        try:
            part = Part(**part_data)
            self.db.add(part)
            self.db.commit()
            self.db.refresh(part)

            # Log audit trail
            PartsAuditLogger.log_part_creation(part.id, part_data, user_id)
            logger.info(f"Created part {part.id}: {part.part_name}")

            return part
        except Exception as e:
            logger.error(f"Error creating part: {e}")
            PartsErrorLogger.log_database_error("create_part", "parts", e, part_data)
            self.db.rollback()
            return None

    def update_part(self, part_id: int, update_data: Dict) -> Optional[Part]:
        """Update an existing part."""
        try:
            part = self.db.query(Part).filter(Part.id == part_id).first()
            if not part:
                return None

            for key, value in update_data.items():
                if hasattr(part, key):
                    setattr(part, key, value)

            self.db.commit()
            self.db.refresh(part)
            return part
        except Exception as e:
            print(f"Error updating part: {e}")
            self.db.rollback()
            return None

    @log_database_operation("prices_new", "UPSERT")
    def set_part_price(
        self, part_id: int, price_data: Dict, user_id: Optional[int] = None
    ) -> Optional[PartPrice]:
        """Set or update price for a part."""
        try:
            # Check if price already exists
            existing_price = self.db.query(PartPrice).filter(PartPrice.part_id == part_id).first()

            if existing_price:
                # Update existing price

                for key, value in price_data.items():
                    if hasattr(existing_price, key):
                        setattr(existing_price, key, value)
                self.db.commit()
                self.db.refresh(existing_price)

                # Log audit trail
                PartsAuditLogger.log_price_update(part_id, price_data, user_id)
                effective_price = (
                    existing_price.sale_price
                    if existing_price.sale_price
                    else existing_price.list_price
                )
                logger.info(f"Updated price for part {part_id}: {effective_price}")

                return existing_price
            else:
                # Create new price
                price_data["part_id"] = part_id
                price = PartPrice(**price_data)
                self.db.add(price)
                self.db.commit()
                self.db.refresh(price)

                # Log audit trail
                PartsAuditLogger.log_price_update(part_id, price_data, user_id)
                effective_price = price.sale_price if price.sale_price else price.list_price
                logger.info(f"Created price for part {part_id}: {effective_price}")

                return price
        except Exception as e:
            logger.error(f"Error setting part price: {e}")
            PartsErrorLogger.log_database_error("set_part_price", "prices_new", e, price_data)
            self.db.rollback()
            return None

    def set_part_stock(self, part_id: int, stock_data: Dict) -> Optional[StockLevel]:
        """Set or update stock level for a part."""
        try:
            # Check if stock level already exists
            existing_stock = self.db.query(StockLevel).filter(StockLevel.part_id == part_id).first()

            if existing_stock:
                # Update existing stock level
                for key, value in stock_data.items():
                    if hasattr(existing_stock, key):
                        setattr(existing_stock, key, value)
                self.db.commit()
                self.db.refresh(existing_stock)
                return existing_stock
            else:
                # Create new stock level
                stock_data["part_id"] = part_id
                stock = StockLevel(**stock_data)
                self.db.add(stock)
                self.db.commit()
                self.db.refresh(stock)
                return stock
        except Exception as e:
            print(f"Error setting part stock: {e}")
            self.db.rollback()
            return None

    def get_categories(self) -> List[PartCategory]:
        """Get all categories."""
        try:
            return self.db.query(PartCategory).filter(PartCategory.is_active).all()
        except Exception as e:
            print(f"Error getting categories: {e}")
            return []
