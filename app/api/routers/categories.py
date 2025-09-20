from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from pydantic import BaseModel

from app.db.database import get_db
from app.db.models import PartCategory, Part
from app.services.category_service import CategoryService

router = APIRouter()

# Pydantic Models
class PartCategoryResponse(BaseModel):
    id: int
    parent_id: Optional[int]
    name: str
    name_fa: Optional[str]
    name_cn: Optional[str]
    description: Optional[str]
    icon: Optional[str]
    color: Optional[str]
    level: int
    path: Optional[str]
    is_active: bool
    sort_order: int
    created_at: str
    updated_at: str
    children_count: Optional[int] = 0
    parts_count: Optional[int] = 0

class PartCategoryCreateRequest(BaseModel):
    parent_id: Optional[int] = None
    name: str
    name_fa: Optional[str] = None
    name_cn: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    is_active: bool = True
    sort_order: int = 0

class PartCategoryUpdateRequest(BaseModel):
    parent_id: Optional[int] = None
    name: Optional[str] = None
    name_fa: Optional[str] = None
    name_cn: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None

class CategoryTreeResponse(BaseModel):
    id: int
    name: str
    name_fa: Optional[str]
    name_cn: Optional[str]
    icon: Optional[str]
    color: Optional[str]
    level: int
    path: Optional[str]
    is_active: bool
    sort_order: int
    children: List['CategoryTreeResponse'] = []
    parts_count: int = 0

# Update forward references
CategoryTreeResponse.model_rebuild()

# Category CRUD Endpoints
@router.get("/", response_model=List[PartCategoryResponse])
async def list_categories(
    skip: int = 0,
    limit: int = 100,
    parent_id: Optional[int] = Query(None, description="Filter by parent category"),
    level: Optional[int] = Query(None, description="Filter by category level"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search in category name"),
    db: Session = Depends(get_db)
):
    """List all part categories with optional filtering."""
    category_service = CategoryService(db)
    categories = category_service.get_categories(
        skip=skip,
        limit=limit,
        parent_id=parent_id,
        level=level,
        is_active=is_active,
        search=search
    )
    
    # Get counts for each category
    category_ids = [cat.id for cat in categories]
    
    # Get children counts
    from sqlalchemy import func
    from app.db.models import PartCategory, Part
    children_counts = db.query(
        PartCategory.parent_id, 
        func.count(PartCategory.id).label('count')
    ).filter(
        PartCategory.parent_id.in_(category_ids)
    ).group_by(PartCategory.parent_id).all()
    
    children_count_map = {row.parent_id: row.count for row in children_counts}
    
    # Get parts counts
    parts_counts = db.query(
        Part.category_id,
        func.count(Part.id).label('count')
    ).filter(
        Part.category_id.in_(category_ids)
    ).group_by(Part.category_id).all()
    
    parts_count_map = {row.category_id: row.count for row in parts_counts}
    
    return [
        PartCategoryResponse(
            id=category.id,  # type: ignore[arg-type]
            parent_id=category.parent_id,  # type: ignore[arg-type]
            name=category.name,  # type: ignore[arg-type]
            name_fa=category.name_fa,  # type: ignore[arg-type]
            name_cn=category.name_cn,  # type: ignore[arg-type]
            description=category.description,  # type: ignore[arg-type]
            icon=category.icon,  # type: ignore[arg-type]
            color=category.color,  # type: ignore[arg-type]
            level=category.level,  # type: ignore[arg-type]
            path=category.path,  # type: ignore[arg-type]
            is_active=category.is_active,  # type: ignore[arg-type]
            sort_order=category.sort_order,  # type: ignore[arg-type]
            created_at=category.created_at.isoformat(),
            updated_at=category.updated_at.isoformat(),
            children_count=children_count_map.get(category.id, 0),  # type: ignore[arg-type]
            parts_count=parts_count_map.get(category.id, 0)  # type: ignore[arg-type]
        )
        for category in categories
    ]

@router.post("/", response_model=PartCategoryResponse)
async def create_category(
    request: PartCategoryCreateRequest,
    db: Session = Depends(get_db)
):
    """Create a new part category."""
    category_service = CategoryService(db)
    category = category_service.create_category(request.dict())
    
    if not category:
        raise HTTPException(status_code=400, detail="Failed to create category")
    
    return PartCategoryResponse(
        id=category.id,  # type: ignore[arg-type]
        parent_id=category.parent_id,  # type: ignore[arg-type]
        name=category.name,  # type: ignore[arg-type]
        name_fa=category.name_fa,  # type: ignore[arg-type]
        name_cn=category.name_cn,  # type: ignore[arg-type]
        description=category.description,  # type: ignore[arg-type]
        icon=category.icon,  # type: ignore[arg-type]
        color=category.color,  # type: ignore[arg-type]
        level=category.level,  # type: ignore[arg-type]
        path=category.path,  # type: ignore[arg-type]
        is_active=category.is_active,  # type: ignore[arg-type]
        sort_order=category.sort_order,  # type: ignore[arg-type]
        created_at=category.created_at.isoformat(),
        updated_at=category.updated_at.isoformat(),
        children_count=0,
        parts_count=0
    )

@router.get("/{category_id}", response_model=PartCategoryResponse)
async def get_category(category_id: int, db: Session = Depends(get_db)):
    """Get a specific part category by ID."""
    category_service = CategoryService(db)
    category = category_service.get_category_by_id(category_id)
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Get children count for this specific category
    children_count = db.query(
        func.count(PartCategory.id)
    ).filter(
        PartCategory.parent_id == category_id
    ).scalar() or 0
    
    # Get parts count for this specific category
    parts_count = db.query(
        func.count(Part.id)
    ).filter(
        Part.category_id == category_id
    ).scalar() or 0
    
    return PartCategoryResponse(
        id=category.id,  # type: ignore[arg-type]
        parent_id=category.parent_id,  # type: ignore[arg-type]
        name=category.name,  # type: ignore[arg-type]
        name_fa=category.name_fa,  # type: ignore[arg-type]
        name_cn=category.name_cn,  # type: ignore[arg-type]
        description=category.description,  # type: ignore[arg-type]
        icon=category.icon,  # type: ignore[arg-type]
        color=category.color,  # type: ignore[arg-type]
        level=category.level,  # type: ignore[arg-type]
        path=category.path,  # type: ignore[arg-type]
        is_active=category.is_active,  # type: ignore[arg-type]
        sort_order=category.sort_order,  # type: ignore[arg-type]
        created_at=category.created_at.isoformat(),
        updated_at=category.updated_at.isoformat(),
        children_count=children_count,
        parts_count=parts_count
    )

@router.put("/{category_id}", response_model=PartCategoryResponse)
async def update_category(
    category_id: int,
    request: PartCategoryUpdateRequest,
    db: Session = Depends(get_db)
):
    """Update an existing part category."""
    category_service = CategoryService(db)
    category = category_service.update_category(
        category_id, 
        request.dict(exclude_unset=True)
    )
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found or update failed")
    
    # Get children count for this specific category
    children_count = db.query(
        func.count(PartCategory.id)
    ).filter(
        PartCategory.parent_id == category_id
    ).scalar() or 0
    
    # Get parts count for this specific category
    parts_count = db.query(
        func.count(Part.id)
    ).filter(
        Part.category_id == category_id
    ).scalar() or 0
    
    return PartCategoryResponse(
        id=category.id,  # type: ignore[arg-type]
        parent_id=category.parent_id,  # type: ignore[arg-type]
        name=category.name,  # type: ignore[arg-type]
        name_fa=category.name_fa,  # type: ignore[arg-type]
        name_cn=category.name_cn,  # type: ignore[arg-type]
        description=category.description,  # type: ignore[arg-type]
        icon=category.icon,  # type: ignore[arg-type]
        color=category.color,  # type: ignore[arg-type]
        level=category.level,  # type: ignore[arg-type]
        path=category.path,  # type: ignore[arg-type]
        is_active=category.is_active,  # type: ignore[arg-type]
        sort_order=category.sort_order,  # type: ignore[arg-type]
        created_at=category.created_at.isoformat(),
        updated_at=category.updated_at.isoformat(),
        children_count=children_count,
        parts_count=parts_count
    )

@router.delete("/{category_id}")
async def delete_category(category_id: int, db: Session = Depends(get_db)):
    """Delete a part category (soft delete)."""
    category_service = CategoryService(db)
    success = category_service.delete_category(category_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return {"message": "Category deleted successfully"}

# Hierarchical Endpoints
@router.get("/tree", response_model=List[CategoryTreeResponse])
async def get_category_tree(
    include_inactive: bool = Query(False, description="Include inactive categories"),
    db: Session = Depends(get_db)
):
    """Get the complete category tree structure."""
    category_service = CategoryService(db)
    tree = category_service.get_category_tree(include_inactive=include_inactive)
    
    def build_tree_response(categories: List[PartCategory]) -> List[CategoryTreeResponse]:
        result = []
        for category in categories:
            category_data = CategoryTreeResponse(
                id=category.id,  # type: ignore[arg-type]
                name=category.name,  # type: ignore[arg-type]
                name_fa=category.name_fa,  # type: ignore[arg-type]
                name_cn=category.name_cn,  # type: ignore[arg-type]
                icon=category.icon,  # type: ignore[arg-type]
                color=category.color,  # type: ignore[arg-type]
                level=category.level,  # type: ignore[arg-type]
                path=category.path,  # type: ignore[arg-type]
                is_active=category.is_active,  # type: ignore[arg-type]
                sort_order=category.sort_order,  # type: ignore[arg-type]
                parts_count=0,  # Tree view doesn't need exact parts count
                children=build_tree_response(category.children) if category.children else []
            )
            result.append(category_data)
        return result
    
    return build_tree_response(tree)

@router.get("/{category_id}/children", response_model=List[PartCategoryResponse])
async def get_category_children(category_id: int, db: Session = Depends(get_db)):
    """Get all children of a specific category."""
    category_service = CategoryService(db)
    children = category_service.get_category_children(category_id)
    
    if not children:
        return []
    
    # Get category IDs for count queries
    category_ids = [child.id for child in children]
    
    # Get children counts
    children_counts = db.query(
        PartCategory.parent_id,
        func.count(PartCategory.id).label('count')
    ).filter(
        PartCategory.parent_id.in_(category_ids)
    ).group_by(PartCategory.parent_id).all()
    
    children_count_map = {row.parent_id: row.count for row in children_counts}
    
    # Get parts counts
    parts_counts = db.query(
        Part.category_id,
        func.count(Part.id).label('count')
    ).filter(
        Part.category_id.in_(category_ids)
    ).group_by(Part.category_id).all()
    
    parts_count_map = {row.category_id: row.count for row in parts_counts}
    
    return [
        PartCategoryResponse(
            id=category.id,  # type: ignore[arg-type]
            parent_id=category.parent_id,  # type: ignore[arg-type]
            name=category.name,  # type: ignore[arg-type]
            name_fa=category.name_fa,  # type: ignore[arg-type]
            name_cn=category.name_cn,  # type: ignore[arg-type]
            description=category.description,  # type: ignore[arg-type]
            icon=category.icon,  # type: ignore[arg-type]
            color=category.color,  # type: ignore[arg-type]
            level=category.level,  # type: ignore[arg-type]
            path=category.path,  # type: ignore[arg-type]
            is_active=category.is_active,  # type: ignore[arg-type]
            sort_order=category.sort_order,  # type: ignore[arg-type]
            created_at=category.created_at.isoformat(),
            updated_at=category.updated_at.isoformat(),
            children_count=children_count_map.get(category.id, 0),  # type: ignore[arg-type]
            parts_count=parts_count_map.get(category.id, 0)  # type: ignore[arg-type]
        )
        for category in children
    ]

@router.get("/{category_id}/path", response_model=List[PartCategoryResponse])
async def get_category_path(category_id: int, db: Session = Depends(get_db)):
    """Get the full path from root to a specific category."""
    category_service = CategoryService(db)
    path = category_service.get_category_path(category_id)
    
    if not path:
        return []
    
    # Get category IDs for count queries
    category_ids = [category.id for category in path]
    
    # Get children counts
    children_counts = db.query(
        PartCategory.parent_id,
        func.count(PartCategory.id).label('count')
    ).filter(
        PartCategory.parent_id.in_(category_ids)
    ).group_by(PartCategory.parent_id).all()
    
    children_count_map = {row.parent_id: row.count for row in children_counts}
    
    # Get parts counts
    parts_counts = db.query(
        Part.category_id,
        func.count(Part.id).label('count')
    ).filter(
        Part.category_id.in_(category_ids)
    ).group_by(Part.category_id).all()
    
    parts_count_map = {row.category_id: row.count for row in parts_counts}
    
    return [
        PartCategoryResponse(
            id=category.id,  # type: ignore[arg-type]
            parent_id=category.parent_id,  # type: ignore[arg-type]
            name=category.name,  # type: ignore[arg-type]
            name_fa=category.name_fa,  # type: ignore[arg-type]
            name_cn=category.name_cn,  # type: ignore[arg-type]
            description=category.description,  # type: ignore[arg-type]
            icon=category.icon,  # type: ignore[arg-type]
            color=category.color,  # type: ignore[arg-type]
            level=category.level,  # type: ignore[arg-type]
            path=category.path,  # type: ignore[arg-type]
            is_active=category.is_active,  # type: ignore[arg-type]
            sort_order=category.sort_order,  # type: ignore[arg-type]
            created_at=category.created_at.isoformat(),
            updated_at=category.updated_at.isoformat(),
            children_count=children_count_map.get(category.id, 0),  # type: ignore[arg-type]
            parts_count=parts_count_map.get(category.id, 0)  # type: ignore[arg-type]
        )
        for category in path
    ]

# Utility Endpoints
@router.get("/roots", response_model=List[PartCategoryResponse])
async def get_root_categories(
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db)
):
    """Get all root categories (level 0)."""
    category_service = CategoryService(db)
    roots = category_service.get_root_categories(is_active=is_active)
    
    if not roots:
        return []
    
    # Get category IDs for count queries
    category_ids = [category.id for category in roots]
    
    # Get children counts
    children_counts = db.query(
        PartCategory.parent_id,
        func.count(PartCategory.id).label('count')
    ).filter(
        PartCategory.parent_id.in_(category_ids)
    ).group_by(PartCategory.parent_id).all()
    
    children_count_map = {row.parent_id: row.count for row in children_counts}
    
    # Get parts counts
    parts_counts = db.query(
        Part.category_id,
        func.count(Part.id).label('count')
    ).filter(
        Part.category_id.in_(category_ids)
    ).group_by(Part.category_id).all()
    
    parts_count_map = {row.category_id: row.count for row in parts_counts}
    
    return [
        PartCategoryResponse(
            id=category.id,  # type: ignore[arg-type]
            parent_id=category.parent_id,  # type: ignore[arg-type]
            name=category.name,  # type: ignore[arg-type]
            name_fa=category.name_fa,  # type: ignore[arg-type]
            name_cn=category.name_cn,  # type: ignore[arg-type]
            description=category.description,  # type: ignore[arg-type]
            icon=category.icon,  # type: ignore[arg-type]
            color=category.color,  # type: ignore[arg-type]
            level=category.level,  # type: ignore[arg-type]
            path=category.path,  # type: ignore[arg-type]
            is_active=category.is_active,  # type: ignore[arg-type]
            sort_order=category.sort_order,  # type: ignore[arg-type]
            created_at=category.created_at.isoformat(),
            updated_at=category.updated_at.isoformat(),
            children_count=children_count_map.get(category.id, 0),  # type: ignore[arg-type]
            parts_count=parts_count_map.get(category.id, 0)  # type: ignore[arg-type]
        )
        for category in roots
    ]

@router.post("/{category_id}/move")
async def move_category(
    category_id: int,
    new_parent_id: Optional[int] = None,
    new_sort_order: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Move a category to a new parent or change sort order."""
    category_service = CategoryService(db)
    success = category_service.move_category(
        category_id, 
        new_parent_id=new_parent_id, 
        new_sort_order=new_sort_order
    )
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to move category")
    
    return {"message": "Category moved successfully"}
