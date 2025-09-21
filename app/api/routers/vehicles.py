from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.db.database import get_db
from app.db.models import VehicleBrand, VehicleModel, VehicleTrim
from app.services.vehicle_service import VehicleService

router = APIRouter()

# Pydantic Models


class VehicleBrandResponse(BaseModel):
    id: int
    name: str
    name_fa: Optional[str]
    name_cn: Optional[str]
    logo_url: Optional[str]
    country: Optional[str]
    website: Optional[str]
    description: Optional[str]
    is_active: bool
    sort_order: int
    created_at: str
    updated_at: str
    models_count: Optional[int] = 0


class VehicleBrandCreateRequest(BaseModel):
    name: str
    name_fa: Optional[str] = None
    name_cn: Optional[str] = None
    logo_url: Optional[str] = None
    country: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = True
    sort_order: int = 0


class VehicleModelResponse(BaseModel):
    id: int
    brand_id: int
    brand_name: Optional[str]
    name: str
    name_fa: Optional[str]
    name_cn: Optional[str]
    generation: Optional[str]
    body_type: Optional[str]
    description: Optional[str]
    image_url: Optional[str]
    is_active: bool
    sort_order: int
    created_at: str
    updated_at: str
    trims_count: Optional[int] = 0


class VehicleModelCreateRequest(BaseModel):
    brand_id: int
    name: str
    name_fa: Optional[str] = None
    name_cn: Optional[str] = None
    generation: Optional[str] = None
    body_type: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    is_active: bool = True
    sort_order: int = 0


class VehicleTrimResponse(BaseModel):
    id: int
    model_id: int
    model_name: Optional[str]
    name: str
    name_fa: Optional[str]
    trim_code: Optional[str]
    engine_type: Optional[str]
    engine_code: Optional[str]
    transmission: Optional[str]
    drivetrain: Optional[str]
    fuel_type: Optional[str]
    year_from: Optional[int]
    year_to: Optional[int]
    specifications: Optional[dict]
    is_active: bool
    sort_order: int
    created_at: str
    updated_at: str


class VehicleTrimCreateRequest(BaseModel):
    model_id: int
    name: str
    name_fa: Optional[str] = None
    trim_code: Optional[str] = None
    engine_type: Optional[str] = None
    engine_code: Optional[str] = None
    transmission: Optional[str] = None
    drivetrain: Optional[str] = None
    fuel_type: Optional[str] = None
    year_from: Optional[int] = None
    year_to: Optional[int] = None
    specifications: Optional[dict] = None
    is_active: bool = True
    sort_order: int = 0


# Brand Endpoints


@router.get("/brands", response_model=List[VehicleBrandResponse])
async def list_brands(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search in brand name"),
    db: Session = Depends(get_db),
):
    """List all vehicle brands with optional filtering."""
    vehicle_service = VehicleService(db)
    brands = vehicle_service.get_brands(
        skip=skip, limit=limit, is_active=is_active, search=search
    )

    return [
        VehicleBrandResponse(
            id=brand.id,
            name=brand.name,
            name_fa=brand.name_fa,
            name_cn=brand.name_cn,
            logo_url=brand.logo_url,
            country=brand.country,
            website=brand.website,
            description=brand.description,
            is_active=brand.is_active,
            sort_order=brand.sort_order,
            created_at=brand.created_at.isoformat(),
            updated_at=brand.updated_at.isoformat(),
            models_count=len(brand.models) if hasattr(brand, "models") else 0,
        )
        for brand in brands
    ]


@router.post("/brands", response_model=VehicleBrandResponse)
async def create_brand(
    request: VehicleBrandCreateRequest, db: Session = Depends(get_db)
):
    """Create a new vehicle brand."""
    vehicle_service = VehicleService(db)
    brand = vehicle_service.create_brand(request.dict())

    if not brand:
        raise HTTPException(status_code=400, detail="Failed to create brand")

    return VehicleBrandResponse(
        id=brand.id,
        name=brand.name,
        name_fa=brand.name_fa,
        name_cn=brand.name_cn,
        logo_url=brand.logo_url,
        country=brand.country,
        website=brand.website,
        description=brand.description,
        is_active=brand.is_active,
        sort_order=brand.sort_order,
        created_at=brand.created_at.isoformat(),
        updated_at=brand.updated_at.isoformat(),
        models_count=0,
    )


@router.get("/brands/{brand_id}", response_model=VehicleBrandResponse)
async def get_brand(brand_id: int, db: Session = Depends(get_db)):
    """Get a specific vehicle brand by ID."""
    vehicle_service = VehicleService(db)
    brand = vehicle_service.get_brand_by_id(brand_id)

    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    return VehicleBrandResponse(
        id=brand.id,
        name=brand.name,
        name_fa=brand.name_fa,
        name_cn=brand.name_cn,
        logo_url=brand.logo_url,
        country=brand.country,
        website=brand.website,
        description=brand.description,
        is_active=brand.is_active,
        sort_order=brand.sort_order,
        created_at=brand.created_at.isoformat(),
        updated_at=brand.updated_at.isoformat(),
        models_count=len(brand.models),
    )


# Model Endpoints


@router.get("/models", response_model=List[VehicleModelResponse])
async def list_models(
    skip: int = 0,
    limit: int = 100,
    brand_id: Optional[int] = Query(None, description="Filter by brand ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search in model name"),
    db: Session = Depends(get_db),
):
    """List all vehicle models with optional filtering."""
    vehicle_service = VehicleService(db)
    models = vehicle_service.get_models(
        skip=skip, limit=limit, brand_id=brand_id, is_active=is_active, search=search
    )

    return [
        VehicleModelResponse(
            id=model.id,
            brand_id=model.brand_id,
            brand_name=model.brand.name if model.brand else None,
            name=model.name,
            name_fa=model.name_fa,
            name_cn=model.name_cn,
            generation=model.generation,
            body_type=model.body_type,
            description=model.description,
            image_url=model.image_url,
            is_active=model.is_active,
            sort_order=model.sort_order,
            created_at=model.created_at.isoformat(),
            updated_at=model.updated_at.isoformat(),
            trims_count=len(model.trims) if hasattr(model, "trims") else 0,
        )
        for model in models
    ]


@router.post("/models", response_model=VehicleModelResponse)
async def create_model(
    request: VehicleModelCreateRequest, db: Session = Depends(get_db)
):
    """Create a new vehicle model."""
    vehicle_service = VehicleService(db)
    model = vehicle_service.create_model(request.dict())

    if not model:
        raise HTTPException(status_code=400, detail="Failed to create model")

    return VehicleModelResponse(
        id=model.id,
        brand_id=model.brand_id,
        brand_name=model.brand.name if model.brand else None,
        name=model.name,
        name_fa=model.name_fa,
        name_cn=model.name_cn,
        generation=model.generation,
        body_type=model.body_type,
        description=model.description,
        image_url=model.image_url,
        is_active=model.is_active,
        sort_order=model.sort_order,
        created_at=model.created_at.isoformat(),
        updated_at=model.updated_at.isoformat(),
        trims_count=0,
    )


# Trim Endpoints


@router.get("/trims", response_model=List[VehicleTrimResponse])
async def list_trims(
    skip: int = 0,
    limit: int = 100,
    model_id: Optional[int] = Query(None, description="Filter by model ID"),
    brand_id: Optional[int] = Query(None, description="Filter by brand ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search in trim name"),
    db: Session = Depends(get_db),
):
    """List all vehicle trims with optional filtering."""
    vehicle_service = VehicleService(db)
    trims = vehicle_service.get_trims(
        skip=skip,
        limit=limit,
        model_id=model_id,
        brand_id=brand_id,
        is_active=is_active,
        search=search,
    )

    return [
        VehicleTrimResponse(
            id=trim.id,
            model_id=trim.model_id,
            model_name=trim.model.name if trim.model else None,
            name=trim.name,
            name_fa=trim.name_fa,
            trim_code=trim.trim_code,
            engine_type=trim.engine_type,
            engine_code=trim.engine_code,
            transmission=trim.transmission,
            drivetrain=trim.drivetrain,
            fuel_type=trim.fuel_type,
            year_from=trim.year_from,
            year_to=trim.year_to,
            specifications=trim.specifications,
            is_active=trim.is_active,
            sort_order=trim.sort_order,
            created_at=trim.created_at.isoformat(),
            updated_at=trim.updated_at.isoformat(),
        )
        for trim in trims
    ]


@router.post("/trims", response_model=VehicleTrimResponse)
async def create_trim(request: VehicleTrimCreateRequest, db: Session = Depends(get_db)):
    """Create a new vehicle trim."""
    vehicle_service = VehicleService(db)
    trim = vehicle_service.create_trim(request.dict())

    if not trim:
        raise HTTPException(status_code=400, detail="Failed to create trim")

    return VehicleTrimResponse(
        id=trim.id,
        model_id=trim.model_id,
        model_name=trim.model.name if trim.model else None,
        name=trim.name,
        name_fa=trim.name_fa,
        trim_code=trim.trim_code,
        engine_type=trim.engine_type,
        engine_code=trim.engine_code,
        transmission=trim.transmission,
        drivetrain=trim.drivetrain,
        fuel_type=trim.fuel_type,
        year_from=trim.year_from,
        year_to=trim.year_to,
        specifications=trim.specifications,
        is_active=trim.is_active,
        sort_order=trim.sort_order,
        created_at=trim.created_at.isoformat(),
        updated_at=trim.updated_at.isoformat(),
    )


# Hierarchical Data Endpoints


@router.get("/brands/{brand_id}/models", response_model=List[VehicleModelResponse])
async def get_brand_models(brand_id: int, db: Session = Depends(get_db)):
    """Get all models for a specific brand."""
    vehicle_service = VehicleService(db)
    models = vehicle_service.get_models_by_brand(brand_id)

    return [
        VehicleModelResponse(
            id=model.id,
            brand_id=model.brand_id,
            brand_name=model.brand.name if model.brand else None,
            name=model.name,
            name_fa=model.name_fa,
            name_cn=model.name_cn,
            generation=model.generation,
            body_type=model.body_type,
            description=model.description,
            image_url=model.image_url,
            is_active=model.is_active,
            sort_order=model.sort_order,
            created_at=model.created_at.isoformat(),
            updated_at=model.updated_at.isoformat(),
            trims_count=len(model.trims),
        )
        for model in models
    ]


@router.get("/models/{model_id}/trims", response_model=List[VehicleTrimResponse])
async def get_model_trims(model_id: int, db: Session = Depends(get_db)):
    """Get all trims for a specific model."""
    vehicle_service = VehicleService(db)
    trims = vehicle_service.get_trims_by_model(model_id)

    return [
        VehicleTrimResponse(
            id=trim.id,
            model_id=trim.model_id,
            model_name=trim.model.name if trim.model else None,
            name=trim.name,
            name_fa=trim.name_fa,
            trim_code=trim.trim_code,
            engine_type=trim.engine_type,
            engine_code=trim.engine_code,
            transmission=trim.transmission,
            drivetrain=trim.drivetrain,
            fuel_type=trim.fuel_type,
            year_from=trim.year_from,
            year_to=trim.year_to,
            specifications=trim.specifications,
            is_active=trim.is_active,
            sort_order=trim.sort_order,
            created_at=trim.created_at.isoformat(),
            updated_at=trim.updated_at.isoformat(),
        )
        for trim in trims
    ]
