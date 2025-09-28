"""
Pydantic schemas for parts, pricing, and stock management.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# Stock Management Schemas
class StockLevelIn(BaseModel):
    """Input schema for stock level updates."""

    current_stock: int = Field(ge=0, description="Current stock quantity")
    reserved_quantity: int = Field(default=0, ge=0, description="Reserved quantity")
    min_stock_level: int = Field(default=0, ge=0, description="Minimum stock level for alerts")


class StockLevelOut(BaseModel):
    """Output schema for stock level information."""

    id: int
    part_id: int
    current_stock: int
    reserved_quantity: int
    min_stock_level: int
    in_stock: bool = Field(description="Derived: current_stock - reserved_quantity > 0")
    created_at: datetime
    updated_at: datetime


# Pricing Schemas
class PriceIn(BaseModel):
    """Input schema for price updates."""

    list_price: str = Field(description="List price as string to avoid precision issues")
    sale_price: Optional[str] = Field(default=None, description="Sale price if different from list")
    currency: str = Field(default="IRR", description="Currency code")


class PriceOut(BaseModel):
    """Output schema for price information."""

    id: int
    part_id: int
    list_price: str
    sale_price: Optional[str]
    currency: str
    effective_price: str = Field(description="Sale price if available, otherwise list price")
    created_at: datetime
    updated_at: datetime


# Part Schemas
class PartListItem(BaseModel):
    """Minimal part information for list views."""

    id: int
    part_name: str
    brand_oem: str
    vehicle_make: str
    vehicle_model: str
    category: str
    oem_code: Optional[str]
    status: str
    price: Optional[PriceOut] = Field(default=None, description="Pricing information")
    stock: Optional[StockLevelOut] = Field(default=None, description="Stock information")


class PartDetail(BaseModel):
    """Full part information for detail views."""

    id: int
    part_name: str
    brand_oem: str
    vehicle_make: str
    vehicle_model: str
    vehicle_trim: Optional[str]
    category: str
    subcategory: Optional[str]
    category_id: Optional[int]
    oem_code: Optional[str]
    alt_codes: Optional[str]
    position: Optional[str]
    unit: str
    pack_size: Optional[int]
    status: str
    price: Optional[PriceOut] = Field(default=None, description="Pricing information")
    stock: Optional[StockLevelOut] = Field(default=None, description="Stock information")
    created_at: datetime
    updated_at: datetime


class PartCreateIn(BaseModel):
    """Input schema for part creation."""

    part_name: str = Field(description="Part name")
    brand_oem: str = Field(description="Brand/OEM")
    vehicle_make: str = Field(description="Vehicle make")
    vehicle_model: str = Field(description="Vehicle model")
    vehicle_trim: Optional[str] = Field(default=None, description="Vehicle trim")
    category: str = Field(description="Category name")
    category_id: Optional[int] = Field(
        default=None, description="Category ID if using normalized categories"
    )
    oem_code: Optional[str] = Field(default=None, description="OEM code")
    alt_codes: Optional[str] = Field(default=None, description="Alternative codes")
    position: Optional[str] = Field(default=None, description="Position")
    unit: str = Field(default="pcs", description="Unit of measurement")
    pack_size: Optional[int] = Field(default=None, description="Pack size")
    status: str = Field(default="active", description="Status")


class PartUpdateIn(BaseModel):
    """Input schema for part updates."""

    part_name: Optional[str] = None
    brand_oem: Optional[str] = None
    vehicle_make: Optional[str] = None
    vehicle_model: Optional[str] = None
    vehicle_trim: Optional[str] = None
    category: Optional[str] = None
    category_id: Optional[int] = None
    oem_code: Optional[str] = None
    alt_codes: Optional[str] = None
    position: Optional[str] = None
    unit: Optional[str] = None
    pack_size: Optional[int] = None
    status: Optional[str] = None


# Category Schemas
class CategoryOut(BaseModel):
    """Output schema for categories."""

    id: int
    name: str
    name_fa: Optional[str]
    name_cn: Optional[str]
    parent_id: Optional[int]
    level: int
    path: Optional[str]
    is_active: bool
    sort_order: int
    created_at: datetime
    updated_at: datetime


# Response Schemas
class PartListResponse(BaseModel):
    """Response schema for parts list."""

    items: List[PartListItem]
    total: int
    page: int
    per_page: int


class ApiResponse(BaseModel):
    """Generic API response wrapper."""

    success: bool
    message: str
    data: Optional[dict] = None
