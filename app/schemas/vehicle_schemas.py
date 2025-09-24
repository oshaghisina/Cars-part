"""
Vehicle Management Pydantic Schemas
Defines data models for vehicle API requests and responses.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator

# Base Models
class VehicleBrandResponse(BaseModel):
    """Vehicle brand response model."""
    id: int
    name: str = Field(..., description="Brand name")
    name_fa: Optional[str] = Field(None, description="Persian name")
    name_cn: Optional[str] = Field(None, description="Chinese name")
    country: Optional[str] = Field(None, description="Country of origin")
    logo_url: Optional[str] = Field(None, description="Brand logo URL")
    website: Optional[str] = Field(None, description="Official website")
    description: Optional[str] = Field(None, description="Brand description")
    is_active: bool = Field(True, description="Whether brand is active")
    model_count: int = Field(0, description="Number of models")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    class Config:
        from_attributes = True

class VehicleModelResponse(BaseModel):
    """Vehicle model response model."""
    id: int
    brand_id: int
    brand_name: str = Field(..., description="Brand name")
    name: str = Field(..., description="Model name")
    name_fa: Optional[str] = Field(None, description="Persian name")
    name_cn: Optional[str] = Field(None, description="Chinese name")
    generation: Optional[str] = Field(None, description="Model generation")
    body_type: Optional[str] = Field(None, description="Body type (SUV, Sedan, etc.)")
    description: Optional[str] = Field(None, description="Model description")
    image_url: Optional[str] = Field(None, description="Model image URL")
    is_active: bool = Field(True, description="Whether model is active")
    trim_count: int = Field(0, description="Number of trims")
    year_range: Dict[str, Optional[int]] = Field(default_factory=dict, description="Year range")
    available_engines: List[str] = Field(default_factory=list, description="Available engine types")
    available_transmissions: List[str] = Field(default_factory=list, description="Available transmissions")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    class Config:
        from_attributes = True

class VehicleTrimResponse(BaseModel):
    """Vehicle trim response model."""
    id: int
    model_id: int
    brand_name: str = Field(..., description="Brand name")
    model_name: str = Field(..., description="Model name")
    name: str = Field(..., description="Trim name")
    name_fa: Optional[str] = Field(None, description="Persian name")
    trim_code: Optional[str] = Field(None, description="Internal trim code")
    engine_type: Optional[str] = Field(None, description="Engine type")
    engine_code: Optional[str] = Field(None, description="Engine code")
    transmission: Optional[str] = Field(None, description="Transmission type")
    drivetrain: Optional[str] = Field(None, description="Drivetrain type")
    fuel_type: Optional[str] = Field(None, description="Fuel type")
    year_from: Optional[int] = Field(None, description="Production start year")
    year_to: Optional[int] = Field(None, description="Production end year")
    specifications: Optional[Dict[str, Any]] = Field(None, description="Additional specifications")
    is_active: bool = Field(True, description="Whether trim is active")
    full_name: str = Field(..., description="Full vehicle name")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    class Config:
        from_attributes = True

# Request Models
class VehicleSearchRequest(BaseModel):
    """Vehicle search request model."""
    make: Optional[str] = Field(None, description="Vehicle make/brand")
    model: Optional[str] = Field(None, description="Vehicle model")
    year: Optional[int] = Field(None, ge=1980, le=2030, description="Model year")
    engine_code: Optional[str] = Field(None, description="Engine code")
    body_type: Optional[str] = Field(None, description="Body type")
    fuel_type: Optional[str] = Field(None, description="Fuel type")
    transmission: Optional[str] = Field(None, description="Transmission type")
    limit: Optional[int] = Field(50, ge=1, le=100, description="Maximum results")
    
    @validator('year')
    def validate_year(cls, v):
        if v is not None and (v < 1980 or v > 2030):
            raise ValueError('Year must be between 1980 and 2030')
        return v

class VehicleSearchResult(BaseModel):
    """Individual vehicle search result."""
    trim_id: int
    make: str = Field(..., description="Vehicle make")
    make_fa: Optional[str] = Field(None, description="Persian make")
    model: str = Field(..., description="Vehicle model")
    model_fa: Optional[str] = Field(None, description="Persian model")
    trim: str = Field(..., description="Vehicle trim")
    trim_fa: Optional[str] = Field(None, description="Persian trim")
    year_from: Optional[int] = Field(None, description="Production start year")
    year_to: Optional[int] = Field(None, description="Production end year")
    engine_type: Optional[str] = Field(None, description="Engine type")
    engine_code: Optional[str] = Field(None, description="Engine code")
    transmission: Optional[str] = Field(None, description="Transmission")
    drivetrain: Optional[str] = Field(None, description="Drivetrain")
    fuel_type: Optional[str] = Field(None, description="Fuel type")
    body_type: Optional[str] = Field(None, description="Body type")
    full_name: str = Field(..., description="Full vehicle name")
    compatibility_score: int = Field(0, ge=0, le=100, description="Compatibility score")

class VehicleSearchResponse(BaseModel):
    """Vehicle search response model."""
    results: List[VehicleSearchResult] = Field(..., description="Search results")
    total_found: int = Field(..., description="Total results found")
    search_criteria: Dict[str, Any] = Field(..., description="Search criteria used")
    
    class Config:
        from_attributes = True

class VINDecodeRequest(BaseModel):
    """VIN decode request model."""
    vin: str = Field(..., min_length=17, max_length=17, description="17-character VIN")
    
    @validator('vin')
    def validate_vin(cls, v):
        v = v.upper().strip()
        if len(v) != 17:
            raise ValueError('VIN must be exactly 17 characters')
        
        # Check for invalid characters
        invalid_chars = set(v) & {'I', 'O', 'Q'}
        if invalid_chars:
            raise ValueError(f'VIN contains invalid characters: {", ".join(invalid_chars)}')
        
        return v

class VehicleMatchFromVIN(BaseModel):
    """Vehicle match from VIN decoding."""
    trim_id: int
    make: str = Field(..., description="Vehicle make")
    model: str = Field(..., description="Vehicle model")
    trim: str = Field(..., description="Vehicle trim")
    year: Optional[int] = Field(None, description="Model year")
    engine_code: Optional[str] = Field(None, description="Engine code")
    confidence: float = Field(..., ge=0, le=1, description="Match confidence (0-1)")

class VINDecodeResponse(BaseModel):
    """VIN decode response model."""
    vin: str = Field(..., description="Input VIN")
    is_valid: bool = Field(..., description="Whether VIN is valid")
    manufacturer: Optional[str] = Field(None, description="Manufacturer name")
    model_year: Optional[int] = Field(None, description="Model year")
    wmi: str = Field(..., description="World Manufacturer Identifier")
    vds: str = Field(..., description="Vehicle Descriptor Section")
    vis: str = Field(..., description="Vehicle Identifier Section")
    country_of_origin: Optional[str] = Field(None, description="Country of origin")
    matching_vehicles: List[VehicleMatchFromVIN] = Field(default_factory=list, description="Matching vehicles")
    decoded_at: datetime = Field(..., description="Decode timestamp")
    
    class Config:
        from_attributes = True

class VehicleCompatibilityRequest(BaseModel):
    """Vehicle compatibility check request."""
    trim_id: Optional[int] = Field(None, description="Specific trim ID")
    make: Optional[str] = Field(None, description="Vehicle make")
    model: Optional[str] = Field(None, description="Vehicle model")
    trim: Optional[str] = Field(None, description="Vehicle trim")
    year: Optional[int] = Field(None, description="Model year")
    engine_code: Optional[str] = Field(None, description="Engine code")
    
    @validator('trim_id', 'make')
    def validate_vehicle_identification(cls, v, values):
        """Ensure either trim_id or make is provided."""
        if not v and not values.get('trim_id') and not values.get('make'):
            raise ValueError('Either trim_id or make must be provided')
        return v

class CompatiblePart(BaseModel):
    """Compatible part information."""
    part_id: int
    part_name: str = Field(..., description="Part name")
    category: str = Field(..., description="Part category")
    oem_code: Optional[str] = Field(None, description="OEM part number")
    compatibility_level: str = Field(..., description="Compatibility level: exact, likely, possible")
    confidence_score: int = Field(..., ge=0, le=100, description="Confidence score")

class VehicleCompatibilityResponse(BaseModel):
    """Vehicle compatibility response model."""
    vehicle: Dict[str, Any] = Field(..., description="Vehicle information")
    compatible_parts: List[CompatiblePart] = Field(default_factory=list, description="Compatible parts")
    total_found: int = Field(..., description="Total compatible parts found")
    checked_at: datetime = Field(..., description="Check timestamp")
    
    class Config:
        from_attributes = True

# Additional utility models
class VehicleOption(BaseModel):
    """Simple vehicle option for dropdowns."""
    id: int
    name: str = Field(..., description="Display name")
    value: str = Field(..., description="Value")
    group: Optional[str] = Field(None, description="Option group")

class VehicleHierarchy(BaseModel):
    """Vehicle hierarchy for cascading selects."""
    brands: List[VehicleOption] = Field(default_factory=list)
    models: Dict[int, List[VehicleOption]] = Field(default_factory=dict)
    trims: Dict[int, List[VehicleOption]] = Field(default_factory=dict)

class VehicleStats(BaseModel):
    """Vehicle database statistics."""
    total_brands: int = Field(..., description="Total number of brands")
    active_brands: int = Field(..., description="Active brands count")
    total_models: int = Field(..., description="Total number of models")
    active_models: int = Field(..., description="Active models count")
    total_trims: int = Field(..., description="Total number of trims")
    active_trims: int = Field(..., description="Active trims count")
    top_brands: List[Dict[str, Any]] = Field(default_factory=list, description="Top brands by model count")
    year_distribution: List[Dict[str, Any]] = Field(default_factory=list, description="Year distribution")

# License plate recognition models
class LicensePlateRequest(BaseModel):
    """License plate recognition request."""
    plate_number: str = Field(..., description="License plate number")
    country: str = Field("IR", description="Country code")
    
class LicensePlateResponse(BaseModel):
    """License plate recognition response."""
    plate_number: str = Field(..., description="Input plate number")
    country: str = Field(..., description="Country code")
    is_valid: bool = Field(..., description="Whether plate format is valid")
    region: Optional[str] = Field(None, description="Vehicle registration region")
    vehicle_type: Optional[str] = Field(None, description="Vehicle type if determinable")
    matching_vehicles: List[VehicleSearchResult] = Field(default_factory=list, description="Potential matches")
    confidence: float = Field(0, ge=0, le=1, description="Recognition confidence")
