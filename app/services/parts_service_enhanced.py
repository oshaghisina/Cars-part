"""Enhanced parts service with version control, cache integration, and rollback capabilities."""

import asyncio
from typing import Dict, List, Optional, Tuple

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.core.cache import cache_service
from app.core.decorators import performance_monitor, retry_on_failure, transactional
from app.core.events import event_bus
from app.db.models import Part
from app.models.stock_models import PartVersion


class PartsServiceEnhanced:
    """Enhanced parts service with version control and cache integration."""

    def __init__(self, db: Session):
        self.db = db

    @transactional
    @performance_monitor("update_part_with_version")
    @retry_on_failure(max_retries=3)
    def update_part_with_version(
        self,
        part_id: int,
        update_data: Dict,
        expected_version: int,
        updated_by: str = "system",
        change_reason: str = None,
    ) -> Optional[Part]:
        """Update part with optimistic locking and version control."""
        try:
            # Get current part with lock
            part = (
                self.db.query(Part)
                .filter(and_(Part.id == part_id, Part.current_version == expected_version))
                .with_for_update()
                .first()
            )

            if not part:
                # Check if part exists but version mismatch
                existing_part = self.db.query(Part).filter(Part.id == part_id).first()

                if existing_part:
                    raise ValueError(
                        f"Version mismatch. Expected: {expected_version}, "
                        f"Current: {existing_part.current_version}. Please refresh and try again."
                    )
                else:
                    raise ValueError(f"Part not found with id {part_id}")

            # Store old values for version history
            old_values = self._extract_part_values(part)

            # Update part fields
            for key, value in update_data.items():
                if hasattr(part, key) and key not in ["id", "current_version", "created_at"]:
                    setattr(part, key, value)

            # Increment version and update metadata
            part.current_version += 1
            part.last_updated_by = updated_by

            # Create version history entry
            changes = self._calculate_changes(old_values, update_data)
            if changes:
                version_entry = PartVersion(
                    part_id=part.id,
                    version=part.current_version,
                    changes=changes,
                    changed_by=updated_by,
                    change_reason=change_reason,
                )
                self.db.add(version_entry)

            self.db.commit()
            self.db.refresh(part)

            # Invalidate cache
            cache_service.invalidate_part(part_id)

            # Emit event (sync version)
            try:
                try:
                    loop = asyncio.get_running_loop()
                    loop.create_task(
                        event_bus.emit(
                            "part_updated",
                            {
                                "part_id": part_id,
                                "changes": changes,
                                "updated_by": updated_by,
                                "new_version": part.current_version,
                                "change_reason": change_reason,
                            },
                        )
                    )
                except RuntimeError:
                    asyncio.run(
                        event_bus.emit(
                            "part_updated",
                            {
                                "part_id": part_id,
                                "changes": changes,
                                "updated_by": updated_by,
                                "new_version": part.current_version,
                                "change_reason": change_reason,
                            },
                        )
                    )
            except Exception as e:
                print(f"Event emission failed: {e}")

            return part

        except Exception as e:
            self.db.rollback()
            print(f"Error updating part with version: {e}")
            raise e

    @transactional
    @performance_monitor("update_part_legacy")
    def update_part_legacy(self, part_id: int, update_data: Dict) -> Optional[Part]:
        """Legacy part update method - maintains backward compatibility."""
        try:
            part = self.db.query(Part).filter(Part.id == part_id).first()
            if not part:
                return None

            # Store old values for version history
            old_values = self._extract_part_values(part)

            # Update part fields
            for key, value in update_data.items():
                if hasattr(part, key) and key not in ["id", "current_version", "created_at"]:
                    setattr(part, key, value)

            # Increment version and update metadata
            part.current_version += 1
            part.last_updated_by = "legacy_api"

            # Create version history entry
            changes = self._calculate_changes(old_values, update_data)
            if changes:
                version_entry = PartVersion(
                    part_id=part.id,
                    version=part.current_version,
                    changes=changes,
                    changed_by="legacy_api",
                    change_reason="Legacy API update",
                )
                self.db.add(version_entry)

            self.db.commit()
            self.db.refresh(part)

            # Invalidate cache
            cache_service.invalidate_part(part_id)

            return part

        except Exception as e:
            print(f"Error updating part (legacy): {e}")
            self.db.rollback()
            return None

    def get_part_with_version(self, part_id: int) -> Optional[Tuple[Part, int]]:
        """Get part with current version number."""
        try:
            part = self.db.query(Part).filter(Part.id == part_id).first()
            if part:
                return part, part.current_version
            return None, 0
        except Exception as e:
            print(f"Error getting part with version: {e}")
            return None, 0

    def get_part_history(self, part_id: int, limit: int = 10) -> List[PartVersion]:
        """Get part change history."""
        try:
            history = (
                self.db.query(PartVersion)
                .filter(PartVersion.part_id == part_id)
                .order_by(PartVersion.created_at.desc())
                .limit(limit)
                .all()
            )

            return history
        except Exception as e:
            print(f"Error getting part history: {e}")
            return []

    def get_part_by_version(self, part_id: int, version: int) -> Optional[Part]:
        """Get part at a specific version."""
        try:
            # Get the part
            part = self.db.query(Part).filter(Part.id == part_id).first()
            if not part:
                return None

            # Get version history entry
            version_entry = (
                self.db.query(PartVersion)
                .filter(and_(PartVersion.part_id == part_id, PartVersion.version == version))
                .first()
            )

            if not version_entry:
                return part  # Return current if version not found

            # Apply changes from version history
            part_copy = self._apply_version_changes(part, version_entry.changes)
            return part_copy

        except Exception as e:
            print(f"Error getting part by version: {e}")
            return None

    def rollback_part_to_version(
        self, part_id: int, target_version: int, rolled_back_by: str = "system"
    ) -> bool:
        """Rollback part to a specific version."""
        try:
            # Get current part
            current_part = self.db.query(Part).filter(Part.id == part_id).first()
            if not current_part:
                return False

            # Get target version
            target_part = self.get_part_by_version(part_id, target_version)
            if not target_part:
                return False

            # Store current values for history
            old_values = self._extract_part_values(current_part)

            # Restore values from target version
            for field in [
                "part_name",
                "brand_oem",
                "vehicle_make",
                "vehicle_model",
                "vehicle_trim",
                "model_year_from",
                "model_year_to",
                "engine_code",
                "position",
                "category",
                "subcategory",
                "oem_code",
                "alt_codes",
                "dimensions_specs",
                "compatibility_notes",
                "unit",
                "pack_size",
                "status",
            ]:
                if hasattr(target_part, field):
                    setattr(current_part, field, getattr(target_part, field))

            current_part.current_version += 1
            current_part.last_updated_by = rolled_back_by

            # Create rollback history entry
            rollback_changes = {
                "action": "rollback",
                "from_version": current_part.current_version - 1,
                "to_version": target_version,
                "old_values": old_values,
                "new_values": self._extract_part_values(current_part),
            }

            version_entry = PartVersion(
                part_id=current_part.id,
                version=current_part.current_version,
                changes=rollback_changes,
                changed_by=rolled_back_by,
                change_reason=f"Rollback to version {target_version}",
            )
            self.db.add(version_entry)

            self.db.commit()

            # Invalidate cache
            cache_service.invalidate_part(part_id)

            # Emit event (sync version)
            try:
                try:
                    loop = asyncio.get_running_loop()
                    loop.create_task(
                        event_bus.emit(
                            "part_updated",
                            {
                                "part_id": part_id,
                                "action": "rollback",
                                "from_version": current_part.current_version - 1,
                                "to_version": target_version,
                                "rolled_back_by": rolled_back_by,
                            },
                        )
                    )
                except RuntimeError:
                    asyncio.run(
                        event_bus.emit(
                            "part_updated",
                            {
                                "part_id": part_id,
                                "action": "rollback",
                                "from_version": current_part.current_version - 1,
                                "to_version": target_version,
                                "rolled_back_by": rolled_back_by,
                            },
                        )
                    )
            except Exception as e:
                print(f"Event emission failed: {e}")

            return True

        except Exception as e:
            print(f"Error rolling back part: {e}")
            self.db.rollback()
            return False

    def get_part_detail_cached(self, part_id: int) -> Optional[Dict]:
        """Get part detail with cache integration."""
        try:
            # Try cache first
            cached_data = cache_service.get_part_detail(part_id)
            if cached_data:
                return cached_data

            # Fallback to database
            part = self.db.query(Part).filter(Part.id == part_id).first()
            if not part:
                return None

            # Convert to dict
            part_data = self._part_to_dict(part)

            # Cache the result
            cache_service.set_part_detail(part_id, part_data)

            return part_data

        except Exception as e:
            print(f"Error getting cached part detail: {e}")
            return None

    def _extract_part_values(self, part: Part) -> Dict:
        """Extract part values for version history."""
        return {
            "part_name": part.part_name,
            "brand_oem": part.brand_oem,
            "vehicle_make": part.vehicle_make,
            "vehicle_model": part.vehicle_model,
            "vehicle_trim": part.vehicle_trim,
            "model_year_from": part.model_year_from,
            "model_year_to": part.model_year_to,
            "engine_code": part.engine_code,
            "position": part.position,
            "category": part.category,
            "subcategory": part.subcategory,
            "oem_code": part.oem_code,
            "alt_codes": part.alt_codes,
            "dimensions_specs": part.dimensions_specs,
            "compatibility_notes": part.compatibility_notes,
            "unit": part.unit,
            "pack_size": part.pack_size,
            "status": part.status,
        }

    def _calculate_changes(self, old_values: Dict, new_values: Dict) -> Dict:
        """Calculate field-level changes for version history."""
        changes = {}
        for key, new_value in new_values.items():
            if key in old_values and old_values[key] != new_value:
                changes[key] = {"old": old_values[key], "new": new_value}
        return changes

    def _apply_version_changes(self, part: Part, changes: Dict) -> Part:
        """Apply changes from version history to create a historical view."""
        # Create a copy of the part
        part_copy = Part()
        for attr in dir(part):
            if not attr.startswith("_") and not callable(getattr(part, attr)):
                setattr(part_copy, attr, getattr(part, attr))

        # Apply changes
        for field, change_data in changes.items():
            if hasattr(part_copy, field) and "old" in change_data:
                setattr(part_copy, field, change_data["old"])

        return part_copy

    def _part_to_dict(self, part: Part) -> Dict:
        """Convert part to dictionary for caching."""
        return {
            "id": part.id,
            "part_name": part.part_name,
            "brand_oem": part.brand_oem,
            "vehicle_make": part.vehicle_make,
            "vehicle_model": part.vehicle_model,
            "vehicle_trim": part.vehicle_trim,
            "model_year_from": part.model_year_from,
            "model_year_to": part.model_year_to,
            "engine_code": part.engine_code,
            "position": part.position,
            "category": part.category,
            "subcategory": part.subcategory,
            "oem_code": part.oem_code,
            "alt_codes": part.alt_codes,
            "dimensions_specs": part.dimensions_specs,
            "compatibility_notes": part.compatibility_notes,
            "unit": part.unit,
            "pack_size": part.pack_size,
            "status": part.status,
            "created_at": part.created_at.isoformat() if part.created_at else None,
            "updated_at": part.updated_at.isoformat() if part.updated_at else None,
            "current_version": part.current_version,
            "last_updated_by": part.last_updated_by,
        }
