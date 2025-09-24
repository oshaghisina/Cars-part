"""
Enhanced Vehicle API Router
Provides comprehensive vehicle data for fitment checking, VIN decoding, and vehicle selection.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc

from app.db.database import get_db
from app.db.models import VehicleBrand, VehicleModel, VehicleTrim
from app.schemas.vehicle_schemas import (
    VehicleBrandResponse, VehicleModelResponse, VehicleTrimResponse,
    VehicleSearchRequest, VehicleSearchResponse, VINDecodeRequest,
    VINDecodeResponse, VehicleCompatibilityRequest, VehicleCompatibilityResponse
)

router = APIRouter(prefix="/vehicles-enhanced", tags=["Enhanced Vehicles"])

@router.get("/brands", response_model=List[VehicleBrandResponse])
async def get_vehicle_brands(
    country: Optional[str] = Query(None, description="Filter by country"),
    search: Optional[str] = Query(None, description="Search brands by name"),
    active_only: bool = Query(True, description="Show only active brands"),
    db: Session = Depends(get_db)
):
    """Get all vehicle brands with filtering options."""
    
    query = db.query(VehicleBrand).options(
        joinedload(VehicleBrand.models)
    )
    
    if active_only:
        query = query.filter(VehicleBrand.is_active == True)
    
    if country:
        query = query.filter(VehicleBrand.country.ilike(f"%{country}%"))
    
    if search:
        query = query.filter(
            or_(
                VehicleBrand.name.ilike(f"%{search}%"),
                VehicleBrand.name_fa.ilike(f"%{search}%"),
                VehicleBrand.name_cn.ilike(f"%{search}%")
            )
        )
    
    brands = query.order_by(VehicleBrand.sort_order, VehicleBrand.name).all()
    
    result = []
    for brand in brands:
        brand_data = {
            "id": brand.id,
            "name": brand.name,
            "name_fa": brand.name_fa,
            "name_cn": brand.name_cn,
            "country": brand.country,
            "logo_url": brand.logo_url,
            "website": brand.website,
            "description": brand.description,
            "is_active": brand.is_active,
            "model_count": len(brand.models),
            "created_at": brand.created_at
        }
        result.append(brand_data)
    
    return result

@router.get("/brands/{brand_id}/models", response_model=List[VehicleModelResponse])
async def get_brand_models(
    brand_id: int = Path(..., description="Brand ID"),
    search: Optional[str] = Query(None, description="Search models by name"),
    body_type: Optional[str] = Query(None, description="Filter by body type"),
    active_only: bool = Query(True, description="Show only active models"),
    db: Session = Depends(get_db)
):
    """Get all models for a specific brand."""
    
    # Check if brand exists
    brand = db.query(VehicleBrand).filter(VehicleBrand.id == brand_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    
    query = db.query(VehicleModel).filter(
        VehicleModel.brand_id == brand_id
    ).options(
        joinedload(VehicleModel.brand),
        joinedload(VehicleModel.trims)
    )
    
    if active_only:
        query = query.filter(VehicleModel.is_active == True)
    
    if search:
        query = query.filter(
            or_(
                VehicleModel.name.ilike(f"%{search}%"),
                VehicleModel.name_fa.ilike(f"%{search}%"),
                VehicleModel.name_cn.ilike(f"%{search}%")
            )
        )
    
    if body_type:
        query = query.filter(VehicleModel.body_type.ilike(f"%{body_type}%"))
    
    models = query.order_by(VehicleModel.sort_order, VehicleModel.name).all()
    
    result = []
    for model in models:
        model_data = {
            "id": model.id,
            "brand_id": model.brand_id,
            "brand_name": model.brand.name,
            "name": model.name,
            "name_fa": model.name_fa,
            "name_cn": model.name_cn,
            "generation": model.generation,
            "body_type": model.body_type,
            "description": model.description,
            "image_url": model.image_url,
            "is_active": model.is_active,
            "trim_count": len(model.trims),
            "year_range": {
                "from": min([t.year_from for t in model.trims if t.year_from]) if model.trims else None,
                "to": max([t.year_to for t in model.trims if t.year_to]) if model.trims else None
            },
            "available_engines": list(set([t.engine_type for t in model.trims if t.engine_type])),
            "available_transmissions": list(set([t.transmission for t in model.trims if t.transmission])),
            "created_at": model.created_at
        }
        result.append(model_data)
    
    return result

@router.get("/models/{model_id}/trims", response_model=List[VehicleTrimResponse])
async def get_model_trims(
    model_id: int = Path(..., description="Model ID"),
    year: Optional[int] = Query(None, description="Filter by year"),
    engine_type: Optional[str] = Query(None, description="Filter by engine type"),
    fuel_type: Optional[str] = Query(None, description="Filter by fuel type"),
    transmission: Optional[str] = Query(None, description="Filter by transmission"),
    active_only: bool = Query(True, description="Show only active trims"),
    db: Session = Depends(get_db)
):
    """Get all trims for a specific model."""
    
    # Check if model exists
    model = db.query(VehicleModel).filter(VehicleModel.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    query = db.query(VehicleTrim).filter(
        VehicleTrim.model_id == model_id
    ).options(
        joinedload(VehicleTrim.model).joinedload(VehicleModel.brand)
    )
    
    if active_only:
        query = query.filter(VehicleTrim.is_active == True)
    
    if year:
        query = query.filter(
            and_(
                or_(VehicleTrim.year_from.is_(None), VehicleTrim.year_from <= year),
                or_(VehicleTrim.year_to.is_(None), VehicleTrim.year_to >= year)
            )
        )
    
    if engine_type:
        query = query.filter(VehicleTrim.engine_type.ilike(f"%{engine_type}%"))
    
    if fuel_type:
        query = query.filter(VehicleTrim.fuel_type.ilike(f"%{fuel_type}%"))
    
    if transmission:
        query = query.filter(VehicleTrim.transmission.ilike(f"%{transmission}%"))
    
    trims = query.order_by(VehicleTrim.sort_order, VehicleTrim.name).all()
    
    result = []
    for trim in trims:
        trim_data = {
            "id": trim.id,
            "model_id": trim.model_id,
            "brand_name": trim.model.brand.name,
            "model_name": trim.model.name,
            "name": trim.name,
            "name_fa": trim.name_fa,
            "trim_code": trim.trim_code,
            "engine_type": trim.engine_type,
            "engine_code": trim.engine_code,
            "transmission": trim.transmission,
            "drivetrain": trim.drivetrain,
            "fuel_type": trim.fuel_type,
            "year_from": trim.year_from,
            "year_to": trim.year_to,
            "specifications": trim.specifications,
            "is_active": trim.is_active,
            "full_name": f"{trim.model.brand.name} {trim.model.name} {trim.name}",
            "created_at": trim.created_at
        }
        result.append(trim_data)
    
    return result

@router.post("/search", response_model=VehicleSearchResponse)
async def search_vehicles(
    search_request: VehicleSearchRequest,
    db: Session = Depends(get_db)
):
    """Advanced vehicle search with multiple criteria."""
    
    # Start with base query
    query = db.query(VehicleTrim).options(
        joinedload(VehicleTrim.model).joinedload(VehicleModel.brand)
    ).filter(VehicleTrim.is_active == True)
    
    # Apply filters
    if search_request.make:
        query = query.filter(
            VehicleTrim.model.has(
                VehicleModel.brand.has(
                    or_(
                        VehicleBrand.name.ilike(f"%{search_request.make}%"),
                        VehicleBrand.name_fa.ilike(f"%{search_request.make}%"),
                        VehicleBrand.name_cn.ilike(f"%{search_request.make}%")
                    )
                )
            )
        )
    
    if search_request.model:
        query = query.filter(
            VehicleTrim.model.has(
                or_(
                    VehicleModel.name.ilike(f"%{search_request.model}%"),
                    VehicleModel.name_fa.ilike(f"%{search_request.model}%"),
                    VehicleModel.name_cn.ilike(f"%{search_request.model}%")
                )
            )
        )
    
    if search_request.year:
        query = query.filter(
            and_(
                or_(VehicleTrim.year_from.is_(None), VehicleTrim.year_from <= search_request.year),
                or_(VehicleTrim.year_to.is_(None), VehicleTrim.year_to >= search_request.year)
            )
        )
    
    if search_request.engine_code:
        query = query.filter(VehicleTrim.engine_code.ilike(f"%{search_request.engine_code}%"))
    
    if search_request.body_type:
        query = query.filter(
            VehicleTrim.model.has(VehicleModel.body_type.ilike(f"%{search_request.body_type}%"))
        )
    
    if search_request.fuel_type:
        query = query.filter(VehicleTrim.fuel_type.ilike(f"%{search_request.fuel_type}%"))
    
    # Execute query
    vehicles = query.limit(search_request.limit or 50).all()
    
    # Format results
    results = []
    for vehicle in vehicles:
        result = {
            "trim_id": vehicle.id,
            "make": vehicle.model.brand.name,
            "make_fa": vehicle.model.brand.name_fa,
            "model": vehicle.model.name,
            "model_fa": vehicle.model.name_fa,
            "trim": vehicle.name,
            "trim_fa": vehicle.name_fa,
            "year_from": vehicle.year_from,
            "year_to": vehicle.year_to,
            "engine_type": vehicle.engine_type,
            "engine_code": vehicle.engine_code,
            "transmission": vehicle.transmission,
            "drivetrain": vehicle.drivetrain,
            "fuel_type": vehicle.fuel_type,
            "body_type": vehicle.model.body_type,
            "full_name": f"{vehicle.model.brand.name} {vehicle.model.name} {vehicle.name}",
            "compatibility_score": 100  # Base score, can be enhanced with ML
        }
        results.append(result)
    
    return {
        "results": results,
        "total_found": len(results),
        "search_criteria": search_request.dict()
    }

@router.post("/decode-vin", response_model=VINDecodeResponse)
async def decode_vin(
    vin_request: VINDecodeRequest,
    db: Session = Depends(get_db)
):
    """Decode VIN to extract vehicle information."""
    
    vin = vin_request.vin.upper().strip()
    
    # Basic VIN validation
    if len(vin) != 17:
        raise HTTPException(status_code=400, detail="VIN must be exactly 17 characters")
    
    # VIN character validation
    invalid_chars = set(vin) & {'I', 'O', 'Q'}
    if invalid_chars:
        raise HTTPException(
            status_code=400, 
            detail=f"VIN contains invalid characters: {', '.join(invalid_chars)}"
        )
    
    # Extract basic information from VIN
    wmi = vin[:3]  # World Manufacturer Identifier
    vds = vin[3:9]  # Vehicle Descriptor Section
    vis = vin[9:]  # Vehicle Identifier Section
    
    # Model year from 10th character
    year_codes = {
        'A': 2010, 'B': 2011, 'C': 2012, 'D': 2013, 'E': 2014, 'F': 2015,
        'G': 2016, 'H': 2017, 'J': 2018, 'K': 2019, 'L': 2020, 'M': 2021,
        'N': 2022, 'P': 2023, 'R': 2024, 'S': 2025, 'T': 2026, 'V': 2027,
        'W': 2028, 'X': 2029, 'Y': 2030, 'Z': 2031,
        '1': 2001, '2': 2002, '3': 2003, '4': 2004, '5': 2005,
        '6': 2006, '7': 2007, '8': 2008, '9': 2009
    }
    
    model_year = year_codes.get(vin[9])
    
    # Chinese manufacturer mapping
    chinese_wmi = {
        'LFV': 'FAW-Volkswagen',
        'LSV': 'SAIC-Volkswagen',
        'LDC': 'Dongfeng Citroën',
        'LEN': 'Dongfeng Nissan',
        'LHG': 'Guangzhou Honda',
        'LBV': 'BMW Brilliance',
        'LFM': 'FAW Mazda',
        'LVS': 'Changan Ford',
        'LJ1': 'JAC',
        'LZE': 'MG',
        'L6T': 'Geely',
        'LME': 'Chery',
        'LVG': 'Great Wall',
        'LYV': 'BYD'
    }
    
    manufacturer = chinese_wmi.get(wmi, f"Unknown ({wmi})")
    
    # Try to find matching vehicles in database
    matching_vehicles = []
    if model_year:
        vehicles = db.query(VehicleTrim).options(
            joinedload(VehicleTrim.model).joinedload(VehicleModel.brand)
        ).filter(
            and_(
                or_(VehicleTrim.year_from.is_(None), VehicleTrim.year_from <= model_year),
                or_(VehicleTrim.year_to.is_(None), VehicleTrim.year_to >= model_year)
            )
        ).limit(10).all()
        
        for vehicle in vehicles:
            if (manufacturer.lower() in vehicle.model.brand.name.lower() or
                wmi in vehicle.model.brand.name.upper()):
                matching_vehicles.append({
                    "trim_id": vehicle.id,
                    "make": vehicle.model.brand.name,
                    "model": vehicle.model.name,
                    "trim": vehicle.name,
                    "year": model_year,
                    "engine_code": vehicle.engine_code,
                    "confidence": 0.8  # High confidence for exact matches
                })
    
    return {
        "vin": vin,
        "is_valid": True,
        "manufacturer": manufacturer,
        "model_year": model_year,
        "wmi": wmi,
        "vds": vds,
        "vis": vis,
        "country_of_origin": "China" if wmi.startswith('L') else "Unknown",
        "matching_vehicles": matching_vehicles,
        "decoded_at": func.now()
    }

@router.post("/check-compatibility", response_model=VehicleCompatibilityResponse)
async def check_vehicle_compatibility(
    compatibility_request: VehicleCompatibilityRequest,
    db: Session = Depends(get_db)
):
    """Check compatibility between vehicle and parts."""
    
    from app.db.models import Part
    
    # Get vehicle information
    vehicle = None
    if compatibility_request.trim_id:
        vehicle = db.query(VehicleTrim).options(
            joinedload(VehicleTrim.model).joinedload(VehicleModel.brand)
        ).filter(VehicleTrim.id == compatibility_request.trim_id).first()
        
        if not vehicle:
            raise HTTPException(status_code=404, detail="Vehicle trim not found")
    
    # Find compatible parts
    compatible_parts = []
    
    if vehicle:
        # Query parts that match vehicle criteria
        parts_query = db.query(Part).filter(Part.status == "active")
        
        # Exact matches
        exact_matches = parts_query.filter(
            and_(
                Part.vehicle_make == vehicle.model.brand.name,
                Part.vehicle_model == vehicle.model.name,
                or_(
                    Part.vehicle_trim.is_(None),
                    Part.vehicle_trim == vehicle.name
                ),
                or_(
                    Part.engine_code.is_(None),
                    Part.engine_code == vehicle.engine_code
                )
            )
        ).limit(20).all()
        
        for part in exact_matches:
            compatible_parts.append({
                "part_id": part.id,
                "part_name": part.part_name,
                "category": part.category,
                "oem_code": part.oem_code,
                "compatibility_level": "exact",
                "confidence_score": 95
            })
        
        # Close matches (same make/model, different trim)
        if len(compatible_parts) < 10:
            close_matches = parts_query.filter(
                and_(
                    Part.vehicle_make == vehicle.model.brand.name,
                    Part.vehicle_model == vehicle.model.name,
                    Part.id.notin_([p["part_id"] for p in compatible_parts])
                )
            ).limit(10 - len(compatible_parts)).all()
            
            for part in close_matches:
                compatible_parts.append({
                    "part_id": part.id,
                    "part_name": part.part_name,
                    "category": part.category,
                    "oem_code": part.oem_code,
                    "compatibility_level": "likely",
                    "confidence_score": 75
                })
    
    return {
        "vehicle": {
            "trim_id": vehicle.id if vehicle else None,
            "make": vehicle.model.brand.name if vehicle else compatibility_request.make,
            "model": vehicle.model.name if vehicle else compatibility_request.model,
            "trim": vehicle.name if vehicle else compatibility_request.trim,
            "year": compatibility_request.year,
            "engine_code": vehicle.engine_code if vehicle else compatibility_request.engine_code
        },
        "compatible_parts": compatible_parts,
        "total_found": len(compatible_parts),
        "checked_at": func.now()
    }

@router.get("/stats")
async def get_vehicle_stats(db: Session = Depends(get_db)):
    """Get vehicle database statistics."""
    
    stats = {
        "total_brands": db.query(VehicleBrand).count(),
        "active_brands": db.query(VehicleBrand).filter(VehicleBrand.is_active == True).count(),
        "total_models": db.query(VehicleModel).count(),
        "active_models": db.query(VehicleModel).filter(VehicleModel.is_active == True).count(),
        "total_trims": db.query(VehicleTrim).count(),
        "active_trims": db.query(VehicleTrim).filter(VehicleTrim.is_active == True).count()
    }
    
    # Top brands by model count
    top_brands = db.query(
        VehicleBrand.name,
        func.count(VehicleModel.id).label('model_count')
    ).join(VehicleModel).group_by(VehicleBrand.id).order_by(
        func.count(VehicleModel.id).desc()
    ).limit(5).all()
    
    stats["top_brands"] = [
        {"brand": brand, "model_count": count}
        for brand, count in top_brands
    ]
    
    # Year distribution
    year_distribution = db.query(
        VehicleTrim.year_from,
        func.count(VehicleTrim.id).label('trim_count')
    ).filter(
        VehicleTrim.year_from.isnot(None)
    ).group_by(VehicleTrim.year_from).order_by(VehicleTrim.year_from).all()
    
    stats["year_distribution"] = [
        {"year": year, "trim_count": count}
        for year, count in year_distribution if year
    ]
    
    return stats
