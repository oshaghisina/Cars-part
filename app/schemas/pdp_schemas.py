"""
PDP (Product Detail Page) Pydantic Schemas
Defines data models for PDP API requests and responses.
"""

from typing import List, Optional, Dict, Any, Union
from datetime import datetime, date
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator, model_validator

# Base Models
class VehicleInfo(BaseModel):
    """Vehicle information for compatibility checking."""
    make: Optional[str] = Field(None, description="Vehicle manufacturer")
    model: Optional[str] = Field(None, description="Vehicle model")
    year: Optional[int] = Field(None, ge=1980, le=2030, description="Model year")
    trim: Optional[str] = Field(None, description="Vehicle trim/variant")
    engine_code: Optional[str] = Field(None, description="Engine code")
    vin: Optional[str] = Field(None, min_length=17, max_length=17, description="Vehicle VIN")
    license_plate: Optional[str] = Field(None, description="License plate number")

class PartImageResponse(BaseModel):
    """Part image response model."""
    id: int
    url: str = Field(..., description="Image URL")
    type: str = Field(..., description="Image type: main, thumbnail, detail, installation, 360")
    alt_text: Optional[str] = Field(None, description="Alt text for accessibility")
    sort_order: int = Field(0, description="Display order")
    
    class Config:
        from_attributes = True

class PartSpecificationResponse(BaseModel):
    """Part specification response model."""
    id: int
    name: str = Field(..., description="Specification name")
    value: str = Field(..., description="Specification value")
    unit: Optional[str] = Field(None, description="Unit of measurement")
    type: str = Field("text", description="Specification type: text, number, boolean, enum")
    is_required: bool = Field(False, description="Whether this specification is required")
    sort_order: int = Field(0, description="Display order")
    
    class Config:
        from_attributes = True

class PartPriceResponse(BaseModel):
    """Part pricing response model."""
    id: int
    seller_name: str = Field(..., description="Seller/supplier name")
    seller_url: Optional[str] = Field(None, description="Seller website URL")
    currency: str = Field("IRR", description="Currency code")
    price: float = Field(..., ge=0, description="Current price")
    original_price: Optional[float] = Field(None, description="Original price before discounts")
    min_order_qty: int = Field(1, ge=1, description="Minimum order quantity")
    available_qty: Optional[int] = Field(None, description="Available quantity")
    warranty: Optional[str] = Field(None, description="Warranty information")
    note: Optional[str] = Field(None, description="Additional notes")
    price_tier: str = Field("retail", description="Price tier: retail, pro, fleet")
    discount_percentage: Optional[float] = Field(None, description="Applied discount percentage")
    valid_from: Optional[date] = Field(None, description="Price valid from date")
    valid_to: Optional[date] = Field(None, description="Price valid until date")
    
    class Config:
        from_attributes = True

class PartCategoryResponse(BaseModel):
    """Part category response model."""
    id: int
    name: str = Field(..., description="Category name")
    name_fa: Optional[str] = Field(None, description="Persian name")
    icon: Optional[str] = Field(None, description="Category icon")
    color: Optional[str] = Field(None, description="Category color")
    path: Optional[str] = Field(None, description="Category path")
    
    class Config:
        from_attributes = True

class PartSummaryResponse(BaseModel):
    """Simplified part response for lists and search results."""
    id: int
    name: str = Field(..., description="Part name")
    brand: str = Field(..., description="Brand/OEM")
    category: str = Field(..., description="Part category")
    oem_code: Optional[str] = Field(None, description="OEM part number")
    vehicle_make: str = Field(..., description="Vehicle manufacturer")
    vehicle_model: str = Field(..., description="Vehicle model")
    price: Optional[Dict[str, Any]] = Field(None, description="Price information")
    image: Optional[Dict[str, str]] = Field(None, description="Main image")
    availability: str = Field("unknown", description="Availability status")
    
    class Config:
        from_attributes = True

class PartAlternativeResponse(BaseModel):
    """Alternative part response model."""
    id: int
    name: str = Field(..., description="Alternative part name")
    brand: str = Field(..., description="Alternative part brand")
    oem_code: Optional[str] = Field(None, description="OEM part number")
    compatibility_score: int = Field(0, ge=0, le=100, description="Compatibility score (0-100)")
    compatibility_notes: Optional[str] = Field(None, description="Compatibility notes")
    vehicle_make: str = Field(..., description="Vehicle manufacturer")
    vehicle_model: str = Field(..., description="Vehicle model")
    price: Optional[Dict[str, Any]] = Field(None, description="Price information")
    image: Optional[Dict[str, str]] = Field(None, description="Main image")
    availability: str = Field("unknown", description="Availability status")
    
    class Config:
        from_attributes = True

class PartCrossReferenceResponse(BaseModel):
    """Cross-reference response model."""
    part_id: int
    oem_references: List[Dict[str, Any]] = Field(default_factory=list, description="OEM cross-references")
    alternatives: List[PartAlternativeResponse] = Field(default_factory=list, description="Alternative parts")
    supersessions: List[Dict[str, Any]] = Field(default_factory=list, description="Superseded parts")
    compatibility_matrix: List[Dict[str, Any]] = Field(default_factory=list, description="Compatibility matrix")
    
    class Config:
        from_attributes = True

class PartReviewResponse(BaseModel):
    """Part review response model."""
    id: int
    user_name: str = Field(..., description="Reviewer name")
    user_avatar: Optional[str] = Field(None, description="Reviewer avatar URL")
    rating: int = Field(..., ge=1, le=5, description="Rating (1-5 stars)")
    title: str = Field(..., description="Review title")
    content: str = Field(..., description="Review content")
    verified_purchase: bool = Field(False, description="Whether this is a verified purchase")
    helpful_count: int = Field(0, description="Number of helpful votes")
    created_at: datetime = Field(..., description="Review creation date")
    
    class Config:
        from_attributes = True

class PartDetailResponse(BaseModel):
    """Comprehensive part detail response model."""
    # Basic Information
    id: int
    name: str = Field(..., description="Part name")
    brand: str = Field(..., description="Brand/OEM")
    category: str = Field(..., description="Part category")
    subcategory: Optional[str] = Field(None, description="Part subcategory")
    oem_code: Optional[str] = Field(None, description="OEM part number")
    alt_codes: List[str] = Field(default_factory=list, description="Alternative part codes")
    unit: str = Field("pcs", description="Unit of measurement")
    pack_size: int = Field(1, description="Package size")
    status: str = Field("active", description="Part status")
    
    # Vehicle Compatibility
    vehicle_make: str = Field(..., description="Vehicle manufacturer")
    vehicle_model: str = Field(..., description="Vehicle model")
    vehicle_trim: Optional[str] = Field(None, description="Vehicle trim")
    model_year_from: Optional[int] = Field(None, description="Compatible from year")
    model_year_to: Optional[int] = Field(None, description="Compatible to year")
    engine_code: Optional[str] = Field(None, description="Compatible engine code")
    position: Optional[str] = Field(None, description="Part position/location")
    compatibility_notes: Optional[str] = Field(None, description="Compatibility notes")
    
    # Timestamps
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    # Related Data (optional)
    category_details: Optional[PartCategoryResponse] = Field(None, description="Category details")
    specifications: Optional[List[PartSpecificationResponse]] = Field(None, description="Part specifications")
    images: Optional[List[PartImageResponse]] = Field(None, description="Part images")
    prices: Optional[List[PartPriceResponse]] = Field(None, description="Pricing information")
    alternatives: Optional[List[PartAlternativeResponse]] = Field(None, description="Alternative parts")
    cross_references: Optional[PartCrossReferenceResponse] = Field(None, description="Cross-references")
    reviews: Optional[List[PartReviewResponse]] = Field(None, description="Customer reviews")
    
    # Computed Fields
    avg_rating: Optional[float] = Field(None, ge=0, le=5, description="Average rating")
    review_count: Optional[int] = Field(None, ge=0, description="Number of reviews")
    best_price: Optional[float] = Field(None, description="Best available price")
    price_currency: str = Field("IRR", description="Price currency")
    in_stock: bool = Field(False, description="Whether the part is in stock")
    
    class Config:
        from_attributes = True

# Request Models
class PartCompatibilityRequest(BaseModel):
    """Request model for checking part compatibility."""
    vehicle: VehicleInfo = Field(..., description="Vehicle information")
    include_alternatives: bool = Field(True, description="Include alternative suggestions")
    
    @model_validator(mode='before')
    @classmethod
    def validate_vehicle_info(cls, values):
        """Validate that at least some vehicle information is provided."""
        if isinstance(values, dict):
            vehicle = values.get('vehicle')
            if not vehicle:
                raise ValueError("Vehicle information is required")
            
            # At least make or VIN should be provided
            if not any([vehicle.make, vehicle.vin]):
                raise ValueError("At least vehicle make or VIN must be provided")
        
        return values

class PartCompatibilityResponse(BaseModel):
    """Response model for part compatibility check."""
    part_id: int
    vehicle_info: VehicleInfo = Field(..., description="Vehicle information used for check")
    is_compatible: bool = Field(..., description="Whether the part is compatible")
    compatibility_level: str = Field(..., description="Compatibility level: direct, likely, possible, incompatible")
    confidence_score: int = Field(..., ge=0, le=100, description="Confidence score (0-100)")
    compatibility_notes: List[str] = Field(default_factory=list, description="Compatibility notes")
    alternative_suggestions: List[PartAlternativeResponse] = Field(default_factory=list, description="Alternative parts if not compatible")
    
    class Config:
        from_attributes = True

class PartSearchFilters(BaseModel):
    """Part search filters model."""
    query: Optional[str] = Field(None, description="Search query")
    category: Optional[str] = Field(None, description="Category filter")
    vehicle_make: Optional[str] = Field(None, description="Vehicle make filter")
    vehicle_model: Optional[str] = Field(None, description="Vehicle model filter")
    min_price: Optional[float] = Field(None, ge=0, description="Minimum price")
    max_price: Optional[float] = Field(None, ge=0, description="Maximum price")
    in_stock_only: bool = Field(False, description="Show only in-stock items")
    brands: Optional[List[str]] = Field(None, description="Brand filters")
    
    @field_validator('max_price')
    @classmethod
    def validate_price_range(cls, v, info):
        """Validate that max_price is greater than min_price."""
        if hasattr(info, 'data') and 'min_price' in info.data:
            min_price = info.data['min_price']
            if min_price is not None and v is not None and v < min_price:
                raise ValueError('max_price must be greater than min_price')
        return v

class PaginatedResponse(BaseModel):
    """Generic paginated response model."""
    items: List[Dict[str, Any]] = Field(..., description="List of items")
    total: int = Field(..., ge=0, description="Total number of items")
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, description="Items per page")
    total_pages: int = Field(..., ge=0, description="Total number of pages")
    
    class Config:
        from_attributes = True

# Cart and Shopping Models
class AddToCartRequest(BaseModel):
    """Request model for adding items to cart."""
    part_id: int = Field(..., description="Part ID")
    quantity: int = Field(1, ge=1, le=100, description="Quantity")
    price_id: Optional[int] = Field(None, description="Specific price/seller ID")
    
class CartItemResponse(BaseModel):
    """Cart item response model."""
    id: int
    part: PartSummaryResponse = Field(..., description="Part information")
    quantity: int = Field(..., description="Quantity")
    unit_price: float = Field(..., description="Unit price")
    total_price: float = Field(..., description="Total price")
    added_at: datetime = Field(..., description="Date added to cart")
    
    class Config:
        from_attributes = True

class CartResponse(BaseModel):
    """Shopping cart response model."""
    items: List[CartItemResponse] = Field(default_factory=list, description="Cart items")
    total_items: int = Field(0, description="Total number of items")
    subtotal: float = Field(0, description="Subtotal amount")
    tax_amount: float = Field(0, description="Tax amount")
    shipping_amount: float = Field(0, description="Shipping amount")
    total_amount: float = Field(0, description="Total amount")
    currency: str = Field("IRR", description="Currency")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True

# Analytics Models
class AnalyticsEventRequest(BaseModel):
    """Analytics event tracking request."""
    event_type: str = Field(..., description="Event type")
    part_id: Optional[int] = Field(None, description="Part ID")
    user_id: Optional[str] = Field(None, description="User ID")
    session_id: Optional[str] = Field(None, description="Session ID")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Event properties")
    timestamp: Optional[datetime] = Field(None, description="Event timestamp")

class AnalyticsEventResponse(BaseModel):
    """Analytics event response model."""
    event_id: str = Field(..., description="Unique event ID")
    status: str = Field("recorded", description="Processing status")
    timestamp: datetime = Field(..., description="Processing timestamp")
    
    class Config:
        from_attributes = True
