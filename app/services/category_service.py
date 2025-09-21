"""Category service for managing hierarchical part categories."""

from sqlalchemy.orm import Session, selectinload
from sqlalchemy import or_
from typing import List, Optional, Dict, Any
import logging

from app.db.models import PartCategory

logger = logging.getLogger(__name__)


class CategoryService:
    """Service for category-related operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_categories(
        self,
        skip: int = 0,
        limit: int = 100,
        parent_id: Optional[int] = None,
        level: Optional[int] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None
    ) -> List[PartCategory]:
        """Get categories with filtering options."""
        query = self.db.query(PartCategory)

        if parent_id is not None:
            query = query.filter(PartCategory.parent_id == parent_id)

        if level is not None:
            query = query.filter(PartCategory.level == level)

        if is_active is not None:
            query = query.filter(PartCategory.is_active == is_active)

        if search:
            search_filter = or_(
                PartCategory.name.ilike(f"%{search}%"),
                PartCategory.name_fa.ilike(f"%{search}%"),
                PartCategory.name_cn.ilike(f"%{search}%"),
                PartCategory.description.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)

        return query.options(
            selectinload(
                PartCategory.children), selectinload(
                PartCategory.parts)).order_by(
            PartCategory.sort_order, PartCategory.name).offset(skip).limit(limit).all()

    def get_category_by_id(self, category_id: int) -> Optional[PartCategory]:
        """Get category by ID."""
        return self.db.query(PartCategory).filter(
            PartCategory.id == category_id).first()

    def get_root_categories(
            self,
            is_active: Optional[bool] = None) -> List[PartCategory]:
        """Get all root categories (level 0)."""
        query = self.db.query(PartCategory).filter(
            PartCategory.parent_id.is_(None))

        if is_active is not None:
            query = query.filter(PartCategory.is_active == is_active)

        return query.order_by(PartCategory.sort_order, PartCategory.name).all()

    def get_category_children(self, category_id: int) -> List[PartCategory]:
        """Get all children of a specific category."""
        return self.db.query(PartCategory).filter(
            PartCategory.parent_id == category_id,
            PartCategory.is_active
        ).order_by(PartCategory.sort_order, PartCategory.name).all()

    # type: ignore[return]
    def get_category_path(self, category_id: int) -> List[PartCategory]:
        """Get the full path from root to a specific category."""
        path = []
        category = self.get_category_by_id(category_id)

        while category:
            path.insert(0, category)
            if category.parent_id:  # type: ignore[comparison-overlap]
                category = self.get_category_by_id(
                    category.parent_id)  # type: ignore[arg-type]
            else:
                break

        return path  # type: ignore[return-value]

    def get_category_tree(
            self,
            include_inactive: bool = False) -> List[PartCategory]:
        """Get the complete category tree structure."""
        query = self.db.query(PartCategory)

        if not include_inactive:
            query = query.filter(PartCategory.is_active)

        # Get all categories and build the tree
        all_categories = query.order_by(
            PartCategory.sort_order,
            PartCategory.name).all()

        # Create a dictionary for quick lookup
        category_dict = {cat.id: cat for cat in all_categories}

        # Build the tree structure
        root_categories = []
        for category in all_categories:
            if category.parent_id is None:  # type: ignore[comparison-overlap]
                root_categories.append(category)
            else:
                parent = category_dict.get(
                    category.parent_id)  # type: ignore[arg-type]
                if parent:
                    if not hasattr(parent, 'children'):
                        parent.children = []
                    parent.children.append(category)

        return root_categories

    def create_category(self,
                        category_data: Dict[str,
                                            Any]) -> Optional[PartCategory]:
        """Create a new category."""
        try:
            # Calculate level and path
            parent_id = category_data.get('parent_id')
            level = 0
            path = ""

            if parent_id:
                parent = self.get_category_by_id(parent_id)
                if parent:
                    level = parent.level + 1
                    # type: ignore[comparison-overlap]
                    path = (f"{parent.path}/{category_data['name']}"
                            if parent.path else f"/{category_data['name']}")
                else:
                    raise ValueError("Invalid parent_id")
            else:
                path = f"/{category_data['name']}"

            category_data['level'] = level
            category_data['path'] = path

            category = PartCategory(**category_data)
            self.db.add(category)
            self.db.commit()
            self.db.refresh(category)
            return category
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating category: {e}")
            return None

    def update_category(self,
                        category_id: int,
                        category_data: Dict[str,
                                            Any]) -> Optional[PartCategory]:
        """Update an existing category."""
        try:
            category = self.get_category_by_id(category_id)
            if not category:
                return None

            # Handle parent change
            if 'parent_id' in category_data:
                new_parent_id = category_data['parent_id']
                if new_parent_id != category.parent_id:
                    # Update level and path
                    if new_parent_id:
                        parent = self.get_category_by_id(new_parent_id)
                        if parent:
                            # type: ignore[assignment]  # type:
                            # ignore[assignment]
                            category.level = parent.level + 1
                            # type: ignore[assignment]  # type:
                            # ignore[assignment]
                            category.path = (f"{parent.path}/{category.name}"
                                             if parent.path else f"/{category.name}")
                        else:
                            raise ValueError("Invalid parent_id")
                    else:
                        category.level = 0  # type: ignore[assignment]
                        # type: ignore[assignment]  # type: ignore[assignment]
                        category.path = f"/{category.name}"

                    # Update paths for all descendants
                    self._update_descendant_paths(
                        category_id, category.path)  # type: ignore[arg-type]

            # Update other fields
            for key, value in category_data.items():
                if key != 'parent_id' and hasattr(category, key):
                    setattr(category, key, value)

            self.db.commit()
            self.db.refresh(category)
            return category
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating category: {e}")
            return None

    def delete_category(self, category_id: int) -> bool:
        """Delete a category (soft delete by setting is_active=False)."""
        try:
            category = self.get_category_by_id(category_id)
            if not category:
                return False

            # Soft delete the category and all its children
            self._soft_delete_category_and_children(
                category_id)  # type: ignore[arg-type]

            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting category: {e}")
            return False

    def move_category(
        self,
        category_id: int,
        new_parent_id: Optional[int] = None,
        new_sort_order: Optional[int] = None
    ) -> bool:
        """Move a category to a new parent or change sort order."""
        try:
            category = self.get_category_by_id(category_id)
            if not category:
                return False

            # Update parent if provided
            if new_parent_id is not None and new_parent_id != category.parent_id:
                # Validate parent
                if new_parent_id != 0:  # 0 means root level
                    parent = self.get_category_by_id(new_parent_id)
                    if not parent:
                        return False
                    # type: ignore[assignment]
                    category.parent_id = new_parent_id
                    category.level = parent.level + \
                        1  # type: ignore[assignment]
                    # type: ignore[assignment]
                    category.path = (f"{parent.path}/{category.name}"
                                     if parent.path else f"/{category.name}")
                else:
                    category.parent_id = None  # type: ignore[assignment]
                    category.level = 0  # type: ignore[assignment]
                    # type: ignore[assignment]
                    category.path = f"/{category.name}"

                # Update paths for all descendants
                self._update_descendant_paths(
                    category_id, category.path)  # type: ignore[arg-type]

            # Update sort order if provided
            if new_sort_order is not None:
                # type: ignore[assignment]
                category.sort_order = new_sort_order

            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error moving category: {e}")
            return False

    # type: ignore[arg-type]
    def _update_descendant_paths(self, category_id: int, parent_path: str):
        """Update paths for all descendants of a category."""
        children = self.get_category_children(category_id)
        for child in children:
            # type: ignore[assignment]
            child.path = f"{parent_path}/{child.name}"
            self._update_descendant_paths(
                child.id, child.path)  # type: ignore[arg-type]

    def _soft_delete_category_and_children(self, category_id: int):
        """Soft delete a category and all its children."""
        category = self.get_category_by_id(category_id)
        if category:
            category.is_active = False  # type: ignore[assignment]
            children = self.get_category_children(category_id)
            for child in children:
                self._soft_delete_category_and_children(
                    child.id)  # type: ignore[arg-type]

    def search_categories(
        self,
        query: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search categories by name or description."""
        categories = self.db.query(PartCategory).filter(
            PartCategory.is_active,
            or_(
                PartCategory.name.ilike(f"%{query}%"),
                PartCategory.name_fa.ilike(f"%{query}%"),
                PartCategory.name_cn.ilike(f"%{query}%"),
                PartCategory.description.ilike(f"%{query}%")
            )
        ).limit(limit).all()

        results = []
        for category in categories:
            results.append({
                "id": category.id,
                "name": category.name,
                "name_fa": category.name_fa,
                "name_cn": category.name_cn,
                "path": category.path,
                "level": category.level,
                "description": category.description
            })

        return results

    def get_category_stats(self) -> Dict[str, Any]:
        """Get category statistics."""
        total_categories = self.db.query(PartCategory).count()
        active_categories = self.db.query(PartCategory).filter(
            PartCategory.is_active).count()
        root_categories = self.db.query(PartCategory).filter(
            PartCategory.parent_id.is_(None),
            PartCategory.is_active
        ).count()

        # Get categories by level
        level_stats = {}
        for level in range(0, 5):  # Assuming max 5 levels
            count = self.db.query(PartCategory).filter(
                PartCategory.level == level,
                PartCategory.is_active
            ).count()
            if count > 0:
                level_stats[f"level_{level}"] = count

        return {
            "total_categories": total_categories,
            "active_categories": active_categories,
            "inactive_categories": total_categories - active_categories,
            "root_categories": root_categories,
            "level_distribution": level_stats
        }
