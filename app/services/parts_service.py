from datetime import datetime
from typing import Dict, List, Optional

import pandas as pd
from sqlalchemy import distinct, func, or_
from sqlalchemy.orm import Session

from app.db.models import Part, Price, Synonym


class PartsService:
    def __init__(self, db: Session):
        self.db = db

    def get_parts(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        category: Optional[str] = None,
        vehicle_make: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[Part]:
        """Get parts with filtering and search capabilities."""
        query = self.db.query(Part)

        # Apply filters
        if status:
            query = query.filter(Part.status == status)
        if category:
            query = query.filter(Part.category == category)
        if vehicle_make:
            query = query.filter(Part.vehicle_make == vehicle_make)

        # Apply search
        if search:
            search_term = f"%{search.lower()}%"
            query = query.filter(
                or_(
                    Part.part_name.ilike(search_term),
                    Part.oem_code.ilike(search_term),
                    Part.vehicle_model.ilike(search_term),
                    Part.brand_oem.ilike(search_term),
                )
            )

        return query.offset(skip).limit(limit).all()

    def get_part_by_id(self, part_id: int) -> Optional[Part]:
        """Get a specific part by ID."""
        return self.db.query(Part).filter(Part.id == part_id).first()

    def create_part(self, part_data: Dict) -> Optional[Part]:
        """Create a new part."""
        try:
            part = Part(
                part_name=part_data["part_name"],
                brand_oem=part_data["brand_oem"],
                vehicle_make=part_data["vehicle_make"],
                vehicle_model=part_data["vehicle_model"],
                vehicle_trim=part_data.get("vehicle_trim"),
                oem_code=part_data.get("oem_code"),
                category=part_data["category"],
                subcategory=part_data.get("subcategory"),
                position=part_data.get("position"),
                unit=part_data.get("unit", "pcs"),
                pack_size=part_data.get("pack_size"),
                status=part_data.get("status", "active"),
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )

            self.db.add(part)
            self.db.commit()
            self.db.refresh(part)
            return part
        except Exception as e:
            self.db.rollback()
            print(f"Error creating part: {e}")
            return None

    def update_part(self, part_id: int, update_data: Dict) -> Optional[Part]:
        """Update an existing part."""
        try:
            part = self.get_part_by_id(part_id)
            if not part:
                return None

            # Update fields
            for field, value in update_data.items():
                if hasattr(part, field):
                    setattr(part, field, value)

            part.updated_at = datetime.now()
            self.db.commit()
            self.db.refresh(part)
            return part
        except Exception as e:
            self.db.rollback()
            print(f"Error updating part: {e}")
            return None

    def delete_part(self, part_id: int) -> bool:
        """Delete a part (soft delete by setting status to inactive)."""
        try:
            part = self.get_part_by_id(part_id)
            if not part:
                return False

            # Soft delete by setting status to inactive
            part.status = "inactive"
            part.updated_at = datetime.now()
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            print(f"Error deleting part: {e}")
            return False

    def get_part_prices(self, part_id: int) -> List[Price]:
        """Get all prices for a specific part."""
        return self.db.query(Price).filter(Price.part_id == part_id).all()

    def get_part_synonyms(self, part_id: int) -> List[Synonym]:
        """Get all synonyms for a specific part."""
        return self.db.query(Synonym).filter(Synonym.part_id == part_id).all()

    def bulk_import_parts(self, df: pd.DataFrame) -> Dict:
        """Bulk import parts from DataFrame."""
        imported = 0
        errors = 0
        details = []

        # Required columns mapping
        required_columns = {
            "part_name": "Part Name",
            "brand_oem": "Brand OEM",
            "vehicle_make": "Vehicle Make",
            "vehicle_model": "Vehicle Model",
            "category": "Category",
        }

        # Check for required columns
        missing_columns = []
        for col, display_name in required_columns.items():
            if col not in df.columns:
                missing_columns.append(display_name)

        if missing_columns:
            return {
                "imported": 0,
                "errors": 1,
                "details": [f"Missing required columns: {', '.join(missing_columns)}"],
            }

        for index, row in df.iterrows():
            try:
                # Prepare part data
                part_data = {
                    "part_name": str(row["part_name"]).strip(),
                    "brand_oem": str(row["brand_oem"]).strip(),
                    "vehicle_make": str(row["vehicle_make"]).strip(),
                    "vehicle_model": str(row["vehicle_model"]).strip(),
                    "vehicle_trim": str(row.get("vehicle_trim", "")).strip()
                    if pd.notna(row.get("vehicle_trim"))
                    else None,
                    "oem_code": str(row.get("oem_code", "")).strip() if pd.notna(row.get("oem_code")) else None,
                    "category": str(row["category"]).strip(),
                    "subcategory": str(row.get("subcategory", "")).strip()
                    if pd.notna(row.get("subcategory"))
                    else None,
                    "position": str(row.get("position", "")).strip() if pd.notna(row.get("position")) else None,
                    "unit": str(row.get("unit", "pcs")).strip(),
                    "pack_size": int(row["pack_size"]) if pd.notna(row.get("pack_size")) else None,
                    "status": "active",
                }

                # Create part
                part = self.create_part(part_data)
                if part:
                    imported += 1
                    details.append(f"Row {index + 2}: Part '{part.part_name}' created successfully")
                else:
                    errors += 1
                    details.append(
                        f"Row {
                            index +
                            2}: Failed to create part '{
                            part_data['part_name']}'")

            except Exception as e:
                errors += 1
                details.append(f"Row {index + 2}: Error - {str(e)}")

        return {"imported": imported, "errors": errors, "details": details}

    def get_categories(self) -> List[str]:
        """Get all unique categories."""
        categories = (
            self.db.query(
                distinct(
                    Part.category)).filter(
                Part.category.isnot(None),
                Part.status == "active").all())
        return [cat[0] for cat in categories if cat[0]]

    def get_vehicle_makes(self) -> List[str]:
        """Get all unique vehicle makes."""
        makes = (
            self.db.query(distinct(Part.vehicle_make))
            .filter(Part.vehicle_make.isnot(None), Part.status == "active")
            .all()
        )
        return [make[0] for make in makes if make[0]]

    def get_parts_stats(self) -> Dict:
        """Get parts statistics."""
        total_parts = self.db.query(Part).count()
        active_parts = self.db.query(Part).filter(Part.status == "active").count()
        inactive_parts = self.db.query(Part).filter(Part.status == "inactive").count()

        # Count by category
        category_stats = (
            self.db.query(Part.category, func.count(Part.id).label("count"))
            .filter(Part.status == "active")
            .group_by(Part.category)
            .all()
        )

        # Count by vehicle make
        make_stats = (
            self.db.query(Part.vehicle_make, func.count(Part.id).label("count"))
            .filter(Part.status == "active")
            .group_by(Part.vehicle_make)
            .all()
        )

        return {
            "total_parts": total_parts,
            "active_parts": active_parts,
            "inactive_parts": inactive_parts,
            "category_stats": [{"category": cat, "count": count} for cat, count in category_stats],
            "make_stats": [{"make": make, "count": count} for make, count in make_stats],
        }
