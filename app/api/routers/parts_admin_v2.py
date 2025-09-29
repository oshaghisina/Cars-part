"""V2 Admin API endpoints with version control, authentication, and enhanced features."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_active_user
from app.db.models import User

# from app.models.stock_models import StockLevel, PartVersion, StockVersion  # Unused imports
from app.services.parts_service_enhanced import PartsServiceEnhanced
from app.services.stock_service_enhanced import StockServiceEnhanced


router = APIRouter(prefix="/admin/v2", tags=["Admin V2"])


# Pydantic models for V2 API
class StockUpdateV2(BaseModel):
    """Stock update request with version control."""

    current_stock: int = Field(..., ge=0, description="Current stock quantity")
    reserved_quantity: int = Field(..., ge=0, description="Reserved quantity")
    min_stock_level: int = Field(..., ge=0, description="Minimum stock level")
    expected_version: int = Field(
        ..., ge=1, description="Expected current version for optimistic locking"
    )


class PartUpdateV2(BaseModel):
    """Part update request with version control."""

    part_name: Optional[str] = Field(None, description="Part name")
    brand_oem: Optional[str] = Field(None, description="Brand/OEM")
    vehicle_make: Optional[str] = Field(None, description="Vehicle make")
    vehicle_model: Optional[str] = Field(None, description="Vehicle model")
    vehicle_trim: Optional[str] = Field(None, description="Vehicle trim")
    model_year_from: Optional[int] = Field(None, ge=1900, le=2030, description="Model year from")
    model_year_to: Optional[int] = Field(None, ge=1900, le=2030, description="Model year to")
    engine_code: Optional[str] = Field(None, description="Engine code")
    position: Optional[str] = Field(None, description="Position")
    category: Optional[str] = Field(None, description="Category")
    subcategory: Optional[str] = Field(None, description="Subcategory")
    oem_code: Optional[str] = Field(None, description="OEM code")
    alt_codes: Optional[str] = Field(None, description="Alternative codes")
    dimensions_specs: Optional[str] = Field(None, description="Dimensions and specifications")
    compatibility_notes: Optional[str] = Field(None, description="Compatibility notes")
    unit: Optional[str] = Field(None, description="Unit")
    pack_size: Optional[int] = Field(None, ge=1, description="Pack size")
    status: Optional[str] = Field(None, description="Status")
    expected_version: int = Field(
        ..., ge=1, description="Expected current version for optimistic locking"
    )
    change_reason: Optional[str] = Field(None, description="Reason for the change")


class StockLevelV2(BaseModel):
    """Enhanced stock level response with version info."""

    id: int
    part_id: int
    current_stock: int
    reserved_quantity: int
    min_stock_level: int
    version: int
    updated_by: Optional[str]
    lock_timestamp: Optional[str]
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class PartV2(BaseModel):
    """Enhanced part response with version info."""

    id: int
    part_name: str
    brand_oem: str
    vehicle_make: str
    vehicle_model: str
    vehicle_trim: Optional[str]
    model_year_from: Optional[int]
    model_year_to: Optional[int]
    engine_code: Optional[str]
    position: Optional[str]
    category: str
    subcategory: Optional[str]
    oem_code: Optional[str]
    alt_codes: Optional[str]
    dimensions_specs: Optional[str]
    compatibility_notes: Optional[str]
    unit: str
    pack_size: Optional[int]
    status: str
    current_version: int
    last_updated_by: Optional[str]
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class VersionHistoryItem(BaseModel):
    """Version history item."""

    id: int
    version: int
    changes: dict
    changed_by: Optional[str]
    change_reason: Optional[str]
    created_at: str

    class Config:
        from_attributes = True


class RollbackRequest(BaseModel):
    """Rollback request."""

    target_version: int = Field(..., ge=1, description="Target version to rollback to")
    reason: Optional[str] = Field(None, description="Reason for rollback")


# Stock endpoints
@router.put("/parts/{part_id}/stock", response_model=StockLevelV2)
async def update_stock_v2(
    part_id: int,
    stock_data: StockUpdateV2,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update stock with version control and authentication."""
    stock_service = StockServiceEnhanced(db)

    try:
        stock = stock_service.set_part_stock_with_version(
            part_id=part_id,
            stock_data=stock_data.dict(exclude={"expected_version"}),
            expected_version=stock_data.expected_version,
            updated_by=current_user.username,
        )

        if not stock:
            raise HTTPException(status_code=404, detail="Stock level not found")

        return stock

    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/parts/{part_id}/stock", response_model=StockLevelV2)
async def get_stock_v2(
    part_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get stock level with version information."""
    stock_service = StockServiceEnhanced(db)

    stock, _ = stock_service.get_stock_with_version(part_id)
    if not stock:
        raise HTTPException(status_code=404, detail="Stock level not found")

    return stock


@router.get("/parts/{part_id}/stock/history", response_model=List[VersionHistoryItem])
async def get_stock_history(
    part_id: int,
    limit: int = Query(10, ge=1, le=50, description="Number of history items to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get stock change history."""
    stock_service = StockServiceEnhanced(db)

    history = stock_service.get_stock_history(part_id, limit)
    return history


@router.post("/parts/{part_id}/stock/rollback")
async def rollback_stock(
    part_id: int,
    rollback_request: RollbackRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Rollback stock to a specific version."""
    stock_service = StockServiceEnhanced(db)

    success = stock_service.rollback_stock_to_version(
        part_id=part_id,
        target_version=rollback_request.target_version,
        rolled_back_by=str(current_user.username),
    )

    if not success:
        raise HTTPException(status_code=400, detail="Rollback failed")

    return {"message": f"Stock rolled back to version {rollback_request.target_version}"}


# Part endpoints
@router.put("/parts/{part_id}", response_model=PartV2)
async def update_part_v2(
    part_id: int,
    part_data: PartUpdateV2,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update part with version control and authentication."""
    parts_service = PartsServiceEnhanced(db)

    try:
        part = parts_service.update_part_with_version(
            part_id=part_id,
            update_data=part_data.dict(exclude={"expected_version", "change_reason"}),
            expected_version=part_data.expected_version,
            updated_by=current_user.username,
            change_reason=part_data.change_reason,
        )

        if not part:
            raise HTTPException(status_code=404, detail="Part not found")

        return part

    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/parts/{part_id}", response_model=PartV2)
async def get_part_v2(
    part_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get part with version information."""
    parts_service = PartsServiceEnhanced(db)

    part, _ = parts_service.get_part_with_version(part_id)
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")

    return part


@router.get("/parts/{part_id}/history", response_model=List[VersionHistoryItem])
async def get_part_history(
    part_id: int,
    limit: int = Query(10, ge=1, le=50, description="Number of history items to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get part change history."""
    parts_service = PartsServiceEnhanced(db)

    history = parts_service.get_part_history(part_id, limit)
    return history


@router.post("/parts/{part_id}/rollback")
async def rollback_part(
    part_id: int,
    rollback_request: RollbackRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Rollback part to a specific version."""
    parts_service = PartsServiceEnhanced(db)

    success = parts_service.rollback_part_to_version(
        part_id=part_id,
        target_version=rollback_request.target_version,
        rolled_back_by=str(current_user.username),
    )

    if not success:
        raise HTTPException(status_code=400, detail="Rollback failed")

    return {"message": f"Part rolled back to version {rollback_request.target_version}"}


# Statistics endpoints
@router.get("/statistics/stock")
async def get_stock_statistics(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    """Get stock statistics and health metrics."""
    stock_service = StockServiceEnhanced(db)

    stats = stock_service.get_stock_statistics()
    return stats


# Cache management endpoints
@router.post("/cache/invalidate/part/{part_id}")
async def invalidate_part_cache(
    part_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Manually invalidate part cache."""
    from app.core.cache import cache_service

    success = cache_service.invalidate_part(part_id)
    if not success:
        raise HTTPException(status_code=500, detail="Cache invalidation failed")

    return {"message": f"Cache invalidated for part {part_id}"}


@router.post("/cache/clear")
async def clear_all_cache(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    """Clear all cache data."""
    from app.core.cache import cache_service

    success = cache_service.clear_all()
    if not success:
        raise HTTPException(status_code=500, detail="Cache clear failed")

    return {"message": "All cache data cleared"}


@router.get("/cache/stats")
async def get_cache_statistics(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    """Get cache statistics."""
    from app.core.cache import cache_service

    stats = cache_service.get_cache_stats()
    return stats
