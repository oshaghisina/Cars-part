"""
Admin parts API endpoints (authentication required).
"""

# from typing import Optional  # Unused import

from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user
from app.db.database import get_db
from app.db.models import User
from app.schemas.parts_schemas import (  # ApiResponse,  # Unused import
    PartCreateIn,
    PartDetail,
    PartListItem,
    PartListResponse,
    PartUpdateIn,
    PriceIn,
    PriceOut,
    StockLevelIn,
    StockLevelOut,
)
from app.services.parts_enhanced_service import PartsEnhancedService

router = APIRouter()


def _serialize_part_list_item(part) -> PartListItem:
    """Convert ORM part instance to list response."""
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


@router.get("/", response_model=PartListResponse)
async def list_parts(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(20, ge=1, le=200, description="Items per page"),
    search: Optional[str] = Query(None, description="Search term"),
    status: Optional[str] = Query(None, description="Filter by status"),
    category: Optional[str] = Query(None, description="Filter by category name"),
    category_id: Optional[int] = Query(None, description="Filter by category id"),
    vehicle_make: Optional[str] = Query(None, description="Filter by vehicle make"),
    brand: Optional[str] = Query(None, description="Alias for vehicle make filter (brand)"),
    model: Optional[str] = Query(None, description="Filter by vehicle model"),
    vehicle_model: Optional[str] = Query(None, description="Alias for vehicle model filter"),
    trim: Optional[str] = Query(None, description="Filter by vehicle trim"),
    vehicle_trim: Optional[str] = Query(None, description="Alias for vehicle trim filter"),
    price_min: Optional[Decimal] = Query(None, description="Filter by minimum effective price"),
    price_max: Optional[Decimal] = Query(None, description="Filter by maximum effective price"),
    db: Session = Depends(get_db),
):
    """List parts for admin panel with pagination and filters."""
    try:
        parts_service = PartsEnhancedService(db)

        make_filter = vehicle_make or brand
        model_filter = vehicle_model or model
        trim_filter = vehicle_trim or trim

        skip = (page - 1) * limit

        parts, total = parts_service.get_parts_with_total(
            skip=skip,
            limit=limit,
            status=status,
            category=category,
            category_id=category_id,
            vehicle_make=make_filter,
            vehicle_model=model_filter,
            vehicle_trim=trim_filter,
            search=search,
            price_min=price_min,
            price_max=price_max,
        )

        items = [_serialize_part_list_item(part) for part in parts]

        return PartListResponse(
            items=items,
            total=total,
            page=page,
            per_page=limit,
        )

    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - defensive logging
        print(f"Error listing admin parts: {exc}")
        raise HTTPException(status_code=500, detail="Failed to list parts")


# TODO: Add authentication dependency
# @router.post("/", response_model=PartDetail)
# async def create_part(
#     request: PartCreateIn,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user),  # Add auth later
# ):
@router.post("/", response_model=PartDetail)
async def create_part(
    request: PartCreateIn,
    db: Session = Depends(get_db),
):
    """Create a new part."""
    try:
        parts_service = PartsEnhancedService(db)
        part_data = request.dict(exclude_unset=True)
        part = parts_service.create_part(part_data)

        if not part:
            raise HTTPException(status_code=400, detail="Failed to create part")

        # Get the full part with relationships
        full_part = parts_service.get_part_by_id(part.id)
        return _serialize_part_detail(full_part)

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating part: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{part_id}", response_model=PartDetail)
async def update_part(
    part_id: int,
    request: PartUpdateIn,
    db: Session = Depends(get_db),
):
    """Update an existing part."""
    try:
        parts_service = PartsEnhancedService(db)
        update_data = request.dict(exclude_unset=True)

        if not update_data:
            raise HTTPException(status_code=400, detail="No fields provided for update")

        part = parts_service.update_part(part_id, update_data)

        if not part:
            raise HTTPException(status_code=404, detail="Part not found")

        # Get the full part with relationships
        full_part = parts_service.get_part_by_id(part.id)
        return _serialize_part_detail(full_part)

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating part: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{part_id}/price", response_model=PriceOut)
async def set_part_price(
    part_id: int,
    request: PriceIn,
    db: Session = Depends(get_db),
):
    """Set or update price for a part."""
    try:
        parts_service = PartsEnhancedService(db)
        price_data = request.dict(exclude_unset=True)
        price = parts_service.set_part_price(part_id, price_data)

        if not price:
            raise HTTPException(status_code=400, detail="Failed to set price")

        return PriceOut(
            id=price.id,
            part_id=price.part_id,
            list_price=price.list_price,
            sale_price=price.sale_price,
            currency=price.currency,
            effective_price=price.sale_price or price.list_price,
            created_at=price.created_at,
            updated_at=price.updated_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error setting part price: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{part_id}/stock", response_model=StockLevelOut)
async def set_part_stock(
    part_id: int,
    request: StockLevelIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),  # ADD AUTHENTICATION
):
    """Set or update stock level for a part (Legacy endpoint - now requires authentication)."""
    try:
        # Use enhanced stock service for better version control
        from app.services.stock_service_enhanced import StockServiceEnhanced

        stock_service = StockServiceEnhanced(db)

        stock_data = request.dict(exclude_unset=True)
        stock = stock_service.set_part_stock_legacy(part_id, stock_data)

        if not stock:
            raise HTTPException(status_code=400, detail="Failed to set stock")

        in_stock = stock.current_stock - stock.reserved_quantity > 0
        return StockLevelOut(
            id=stock.id,
            part_id=stock.part_id,
            current_stock=stock.current_stock,
            reserved_quantity=stock.reserved_quantity,
            min_stock_level=stock.min_stock_level,
            in_stock=in_stock,
            created_at=stock.created_at,
            updated_at=stock.updated_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error setting part stock: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{part_id}", response_model=PartDetail)
async def get_part_detail(part_id: int, db: Session = Depends(get_db)):
    """Get detailed information for a specific part (admin view)."""
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
