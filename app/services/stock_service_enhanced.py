"""Enhanced stock service with optimistic locking, version control, and cache integration."""

import asyncio
from typing import Dict, List, Optional, Tuple

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.core.cache import cache_service
from app.core.decorators import performance_monitor, retry_on_failure, transactional
from app.core.events import event_bus
from app.models.stock_models import StockLevel, StockVersion
from app.db.models import Part


class StockServiceEnhanced:
    """Enhanced stock service with optimistic locking and version control."""

    def __init__(self, db: Session):
        self.db = db

    @transactional
    @performance_monitor("set_part_stock_with_version")
    @retry_on_failure(max_retries=3)
    def set_part_stock_with_version(
        self, part_id: int, stock_data: Dict, expected_version: int, updated_by: str = "system"
    ) -> Optional[StockLevel]:
        """Set stock with optimistic locking and version control."""
        try:
            # Get current stock level with lock
            stock = (
                self.db.query(StockLevel)
                .filter(and_(StockLevel.part_id == part_id, StockLevel.version == expected_version))
                .with_for_update()
                .first()
            )

            if not stock:
                # Check if stock exists but version mismatch
                existing_stock = (
                    self.db.query(StockLevel).filter(StockLevel.part_id == part_id).first()
                )

                if existing_stock:
                    raise ValueError(
                        f"Version mismatch. Expected: {expected_version}, "
                        f"Current: {existing_stock.version}. Please refresh and try again."
                    )
                else:
                    raise ValueError(f"Stock level not found for part {part_id}")

            # Store old values for version history
            old_values = {
                "current_stock": stock.current_stock,
                "reserved_quantity": stock.reserved_quantity,
                "min_stock_level": stock.min_stock_level,
            }

            # Update stock level
            for key, value in stock_data.items():
                if hasattr(stock, key) and key not in ["id", "part_id", "version", "created_at"]:
                    setattr(stock, key, value)

            # Increment version and update metadata
            stock.version += 1
            stock.updated_by = updated_by
            stock.lock_timestamp = func.now()

            # Create version history entry
            changes = self._calculate_changes(old_values, stock_data)
            if changes:
                version_entry = StockVersion(
                    stock_id=stock.id, version=stock.version, changes=changes, changed_by=updated_by
                )
                self.db.add(version_entry)

            # Update part's current version
            part = self.db.query(Part).filter(Part.id == part_id).first()
            if part:
                part.current_version += 1
                part.last_updated_by = updated_by

            self.db.commit()
            self.db.refresh(stock)

            # Invalidate cache
            cache_service.invalidate_stock(part_id)

            # Emit event (sync version)
            try:
                # Use asyncio.run if no event loop is running
                try:
                    loop = asyncio.get_running_loop()
                    loop.create_task(
                        event_bus.emit(
                            "stock_updated",
                            {
                                "part_id": part_id,
                                "stock_changes": changes,
                                "updated_by": updated_by,
                                "new_version": stock.version,
                            },
                        )
                    )
                except RuntimeError:
                    # No event loop running, create one
                    asyncio.run(
                        event_bus.emit(
                            "stock_updated",
                            {
                                "part_id": part_id,
                                "stock_changes": changes,
                                "updated_by": updated_by,
                                "new_version": stock.version,
                            },
                        )
                    )
            except Exception as e:
                print(f"Event emission failed: {e}")

            return stock

        except Exception as e:
            self.db.rollback()
            print(f"Error setting stock with version: {e}")
            raise e

    @transactional
    @performance_monitor("set_part_stock_legacy")
    def set_part_stock_legacy(self, part_id: int, stock_data: Dict) -> Optional[StockLevel]:
        """Legacy stock update method - maintains backward compatibility."""
        try:
            # Check if stock level already exists
            existing_stock = self.db.query(StockLevel).filter(StockLevel.part_id == part_id).first()

            if existing_stock:
                # Update existing stock level
                for key, value in stock_data.items():
                    if hasattr(existing_stock, key):
                        setattr(existing_stock, key, value)

                # Update version tracking (increment version)
                existing_stock.version += 1
                existing_stock.updated_by = "legacy_api"
                existing_stock.lock_timestamp = func.now()

                self.db.commit()
                self.db.refresh(existing_stock)

                # Invalidate cache
                cache_service.invalidate_stock(part_id)

                return existing_stock
            else:
                # Create new stock level
                stock_data["part_id"] = part_id
                stock_data["version"] = 1
                stock_data["updated_by"] = "legacy_api"
                stock = StockLevel(**stock_data)
                self.db.add(stock)
                self.db.commit()
                self.db.refresh(stock)

                # Invalidate cache
                cache_service.invalidate_stock(part_id)

                return stock

        except Exception as e:
            print(f"Error setting part stock (legacy): {e}")
            self.db.rollback()
            return None

    def get_stock_with_version(self, part_id: int) -> Optional[Tuple[StockLevel, int]]:
        """Get stock level with current version number."""
        try:
            stock = self.db.query(StockLevel).filter(StockLevel.part_id == part_id).first()
            if stock:
                return stock, stock.version
            return None, 0
        except Exception as e:
            print(f"Error getting stock with version: {e}")
            return None, 0

    def get_stock_history(self, part_id: int, limit: int = 10) -> List[StockVersion]:
        """Get stock change history for a part."""
        try:
            # First get the stock level
            stock = self.db.query(StockLevel).filter(StockLevel.part_id == part_id).first()
            if not stock:
                return []

            # Get version history
            history = (
                self.db.query(StockVersion)
                .filter(StockVersion.stock_id == stock.id)
                .order_by(StockVersion.created_at.desc())
                .limit(limit)
                .all()
            )

            return history
        except Exception as e:
            print(f"Error getting stock history: {e}")
            return []

    def get_stock_by_version(self, part_id: int, version: int) -> Optional[StockLevel]:
        """Get stock level at a specific version."""
        try:
            stock = (
                self.db.query(StockLevel)
                .filter(and_(StockLevel.part_id == part_id, StockLevel.version == version))
                .first()
            )
            return stock
        except Exception as e:
            print(f"Error getting stock by version: {e}")
            return None

    def rollback_stock_to_version(
        self, part_id: int, target_version: int, rolled_back_by: str = "system"
    ) -> bool:
        """Rollback stock to a specific version."""
        try:
            # Get current stock
            current_stock = self.db.query(StockLevel).filter(StockLevel.part_id == part_id).first()
            if not current_stock:
                return False

            # Get target version
            target_stock = self.get_stock_by_version(part_id, target_version)
            if not target_stock:
                return False

            # Store current values for history
            old_values = {
                "current_stock": current_stock.current_stock,
                "reserved_quantity": current_stock.reserved_quantity,
                "min_stock_level": current_stock.min_stock_level,
            }

            # Restore values from target version
            current_stock.current_stock = target_stock.current_stock
            current_stock.reserved_quantity = target_stock.reserved_quantity
            current_stock.min_stock_level = target_stock.min_stock_level
            current_stock.version += 1
            current_stock.updated_by = rolled_back_by
            current_stock.lock_timestamp = func.now()

            # Create rollback history entry
            rollback_changes = {
                "action": "rollback",
                "from_version": current_stock.version - 1,
                "to_version": target_version,
                "old_values": old_values,
                "new_values": {
                    "current_stock": target_stock.current_stock,
                    "reserved_quantity": target_stock.reserved_quantity,
                    "min_stock_level": target_stock.min_stock_level,
                },
            }

            version_entry = StockVersion(
                stock_id=current_stock.id,
                version=current_stock.version,
                changes=rollback_changes,
                changed_by=rolled_back_by,
            )
            self.db.add(version_entry)

            self.db.commit()

            # Invalidate cache
            cache_service.invalidate_stock(part_id)

            # Emit event (sync version)
            try:
                try:
                    loop = asyncio.get_running_loop()
                    loop.create_task(
                        event_bus.emit(
                            "stock_updated",
                            {
                                "part_id": part_id,
                                "action": "rollback",
                                "from_version": current_stock.version - 1,
                                "to_version": target_version,
                                "rolled_back_by": rolled_back_by,
                            },
                        )
                    )
                except RuntimeError:
                    asyncio.run(
                        event_bus.emit(
                            "stock_updated",
                            {
                                "part_id": part_id,
                                "action": "rollback",
                                "from_version": current_stock.version - 1,
                                "to_version": target_version,
                                "rolled_back_by": rolled_back_by,
                            },
                        )
                    )
            except Exception as e:
                print(f"Event emission failed: {e}")

            return True

        except Exception as e:
            print(f"Error rolling back stock: {e}")
            self.db.rollback()
            return False

    def _calculate_changes(self, old_values: Dict, new_values: Dict) -> Dict:
        """Calculate field-level changes for version history."""
        changes = {}
        for key, new_value in new_values.items():
            if key in old_values and old_values[key] != new_value:
                changes[key] = {"old": old_values[key], "new": new_value}
        return changes

    def get_stock_statistics(self) -> Dict:
        """Get stock statistics and health metrics."""
        try:
            # Total parts with stock
            total_parts = self.db.query(StockLevel).count()

            # Low stock parts
            low_stock = (
                self.db.query(StockLevel)
                .filter(StockLevel.current_stock <= StockLevel.min_stock_level)
                .count()
            )

            # Out of stock parts
            out_of_stock = self.db.query(StockLevel).filter(StockLevel.current_stock == 0).count()

            # Recently updated (last 24 hours)
            from datetime import datetime, timedelta

            recent_cutoff = datetime.now() - timedelta(hours=24)
            recently_updated = (
                self.db.query(StockLevel).filter(StockLevel.updated_at >= recent_cutoff).count()
            )

            return {
                "total_parts": total_parts,
                "low_stock_parts": low_stock,
                "out_of_stock_parts": out_of_stock,
                "recently_updated": recently_updated,
                "low_stock_percentage": ((low_stock / total_parts * 100) if total_parts > 0 else 0),
                "out_of_stock_percentage": (
                    (out_of_stock / total_parts * 100) if total_parts > 0 else 0
                ),
            }
        except Exception as e:
            print(f"Error getting stock statistics: {e}")
            return {}
