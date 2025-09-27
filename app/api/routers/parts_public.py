"""
Public parts API endpoints (no authentication required).
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.parts_schemas import PartDetail, PartListItem  # PartListResponse unused
from app.services.parts_enhanced_service import PartsEnhancedService

router = APIRouter()


def _serialize_part_list_item(part) -> PartListItem:
    """Convert ORM part instance to list item response."""
    price_out = None
    if part.price_info:
        price_out = {
            "id": part.price_info.id,
            "part_id": part.price_info.part_id,
            "list_price": part.price_info.list_price,
            "sale_price": part.price_info.sale_price,
            "currency": part.price_info.currency,
            "effective_price": part.price_info.sale_price or part.price_info.list_price,
            "created_at": part.price_info.created_at,
            "updated_at": part.price_info.updated_at,
        }

    stock_out = None
    if part.stock_level:
        in_stock = part.stock_level.current_stock - part.stock_level.reserved_quantity > 0
        stock_out = {
            "id": part.stock_level.id,
            "part_id": part.stock_level.part_id,
            "current_stock": part.stock_level.current_stock,
            "reserved_quantity": part.stock_level.reserved_quantity,
            "min_stock_level": part.stock_level.min_stock_level,
            "in_stock": in_stock,
            "created_at": part.stock_level.created_at,
            "updated_at": part.stock_level.updated_at,
        }

    return PartListItem(
        id=part.id,
        part_name=part.part_name,
        brand_oem=part.brand_oem,
        vehicle_make=part.vehicle_make,
        vehicle_model=part.vehicle_model,
        category=part.category,
        oem_code=part.oem_code,
        status=part.status,
        price=price_out,
        stock=stock_out,
    )


def _serialize_part_detail(part) -> PartDetail:
    """Convert ORM part instance to detail response."""
    price_out = None
    if part.price_info:
        price_out = {
            "id": part.price_info.id,
            "part_id": part.price_info.part_id,
            "list_price": part.price_info.list_price,
            "sale_price": part.price_info.sale_price,
            "currency": part.price_info.currency,
            "effective_price": part.price_info.sale_price or part.price_info.list_price,
            "created_at": part.price_info.created_at,
            "updated_at": part.price_info.updated_at,
        }

    stock_out = None
    if part.stock_level:
        in_stock = part.stock_level.current_stock - part.stock_level.reserved_quantity > 0
        stock_out = {
            "id": part.stock_level.id,
            "part_id": part.stock_level.part_id,
            "current_stock": part.stock_level.current_stock,
            "reserved_quantity": part.stock_level.reserved_quantity,
            "min_stock_level": part.stock_level.min_stock_level,
            "in_stock": in_stock,
            "created_at": part.stock_level.created_at,
            "updated_at": part.stock_level.updated_at,
        }

    return PartDetail(
        id=part.id,
        part_name=part.part_name,
        brand_oem=part.brand_oem,
        vehicle_make=part.vehicle_make,
        vehicle_model=part.vehicle_model,
        vehicle_trim=part.vehicle_trim,
        category=part.category,
        subcategory=part.subcategory,
        category_id=part.category_id,
        oem_code=part.oem_code,
        alt_codes=part.alt_codes,
        position=part.position,
        unit=part.unit,
        pack_size=part.pack_size,
        status=part.status,
        price=price_out,
        stock=stock_out,
        created_at=part.created_at,
        updated_at=part.updated_at,
    )


@router.get("/", response_model=List[PartListItem])
async def list_parts(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of items to return"),
    status: Optional[str] = Query(None, description="Filter by status"),
    category: Optional[str] = Query(None, description="Filter by category name"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    vehicle_make: Optional[str] = Query(None, description="Filter by vehicle make"),
    search: Optional[str] = Query(
        None, description="Search in part name, OEM code, or vehicle model"
    ),
    db: Session = Depends(get_db),
):
    """Get list of parts with pricing and stock information."""
    try:
        parts_service = PartsEnhancedService(db)
        parts, total = parts_service.get_parts_with_total(
            skip=skip,
            limit=limit,
            status=status,
            category=category,
            category_id=category_id,
            vehicle_make=vehicle_make,
            search=search,
        )

        return [_serialize_part_list_item(part) for part in parts]

    except Exception as e:
        print(f"Error in list_parts: {e}")
        # Return empty list on error to prevent 500s
        return []


@router.get("/{part_id}", response_model=PartDetail)
async def get_part_detail(part_id: int, db: Session = Depends(get_db)):
    """Get detailed information for a specific part."""
    try:
        parts_service = PartsEnhancedService(db)
        part = parts_service.get_part_by_id(part_id)

        if not part:
            raise HTTPException(status_code=404, detail="Part not found")

        return _serialize_part_detail(part)

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_part_detail: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/categories/", response_model=List[dict])
async def list_categories(db: Session = Depends(get_db)):
    """Get list of categories."""
    try:
        parts_service = PartsEnhancedService(db)
        categories = parts_service.get_categories()

        return [
            {
                "id": cat.id,
                "name": cat.name,
                "name_fa": cat.name_fa,
                "name_cn": cat.name_cn,
                "parent_id": cat.parent_id,
                "level": cat.level,
                "path": cat.path,
                "is_active": cat.is_active,
                "sort_order": cat.sort_order,
                "created_at": cat.created_at.isoformat(),
                "updated_at": cat.updated_at.isoformat(),
            }
            for cat in categories
        ]

    except Exception as e:
        print(f"Error in list_categories: {e}")
        # Return empty list on error to prevent 500s
        return []
