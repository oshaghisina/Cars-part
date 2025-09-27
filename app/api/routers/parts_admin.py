"""
Admin parts API endpoints (authentication required).
"""

# from typing import Optional  # Unused import

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.parts_schemas import (
    # ApiResponse,  # Unused import
    PartCreateIn,
    PartDetail,
    PartUpdateIn,
    PriceIn,
    PriceOut,
    StockLevelIn,
    StockLevelOut,
)
from app.services.parts_enhanced_service import PartsEnhancedService

router = APIRouter()


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
):
    """Set or update stock level for a part."""
    try:
        parts_service = PartsEnhancedService(db)
        stock_data = request.dict(exclude_unset=True)
        stock = parts_service.set_part_stock(part_id, stock_data)

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
