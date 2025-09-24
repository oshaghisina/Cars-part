"""
Enhanced PDP (Product Detail Page) API Router
Provides comprehensive endpoints for product data, compatibility, alternatives,
and related features.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func

from app.db.database import get_db
from app.db.models import (
    Part, Price, PartSpecification, PartImage, User
)
from app.schemas.pdp_schemas import (
    PartDetailResponse, PartSpecificationResponse,
    PartImageResponse, PartAlternativeResponse, PartCompatibilityRequest,
    PartCompatibilityResponse, PartPriceResponse,
    PartCrossReferenceResponse, PaginatedResponse
)
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/pdp", tags=["Product Detail Page"])


@router.get("/parts/{part_id}", response_model=PartDetailResponse)
async def get_part_detail(
    part_id: int = Path(..., description="Part ID"),
    include_specifications: bool = Query(True, description="Include part specifications"),
    include_images: bool = Query(True, description="Include part images"),
    include_prices: bool = Query(True, description="Include pricing information"),
    include_alternatives: bool = Query(False, description="Include alternative parts"),
    include_cross_references: bool = Query(False, description="Include cross-references"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Get comprehensive part details for PDP.
    Includes specifications, images, pricing, and optional related data.
    """
    # Build query with eager loading for performance
    query = db.query(Part).options(
        joinedload(
            Part.category_obj),
        joinedload(
            Part.specifications) if include_specifications else joinedload(
                Part.specifications).load_only('id'),
        joinedload(
                    Part.images) if include_images else joinedload(
                        Part.images).load_only('id'),
        joinedload(
                            Part.prices) if include_prices else joinedload(
                                Part.prices).load_only('id'))

    part = query.filter(Part.id == part_id, Part.status == "active").first()

    if not part:
        raise HTTPException(status_code=404, detail="Part not found")

    # Build response
    response_data = {
        "id": part.id,
        "name": part.part_name,
        "brand": part.brand_oem,
        "category": part.category,
        "subcategory": part.subcategory,
        "oem_code": part.oem_code,
        "alt_codes": part.alt_codes.split(',') if part.alt_codes else [],
        "unit": part.unit,
        "pack_size": part.pack_size,
        "status": part.status,
        "vehicle_make": part.vehicle_make,
        "vehicle_model": part.vehicle_model,
        "vehicle_trim": part.vehicle_trim,
        "model_year_from": part.model_year_from,
        "model_year_to": part.model_year_to,
        "engine_code": part.engine_code,
        "position": part.position,
        "compatibility_notes": part.compatibility_notes,
        "created_at": part.created_at,
        "updated_at": part.updated_at
    }

    # Add category details
    if part.category_obj:
        response_data["category_details"] = {
            "id": part.category_obj.id,
            "name": part.category_obj.name,
            "name_fa": part.category_obj.name_fa,
            "icon": part.category_obj.icon,
            "color": part.category_obj.color,
            "path": part.category_obj.path
        }

    # Add specifications
    if include_specifications and part.specifications:
        response_data["specifications"] = [
            {
                "id": spec.id,
                "name": spec.spec_name,
                "value": spec.spec_value,
                "unit": spec.spec_unit,
                "type": spec.spec_type,
                "is_required": spec.is_required,
                "sort_order": spec.sort_order
            }
            for spec in sorted(part.specifications, key=lambda x: x.sort_order)
        ]

    # Add images
    if include_images and part.images:
        response_data["images"] = [
            {
                "id": img.id,
                "url": img.image_url,
                "type": img.image_type,
                "alt_text": img.alt_text,
                "sort_order": img.sort_order,
                "is_active": img.is_active
            }
            for img in sorted(part.images, key=lambda x: x.sort_order)
            if img.is_active
        ]

    # Add pricing (with user-specific pricing if authenticated)
    if include_prices and part.prices:
        prices = []
        for price in part.prices:
            # Check if price is valid
            today = datetime.now().date()
            if price.valid_from and price.valid_from > today:
                continue
            if price.valid_to and price.valid_to < today:
                continue

            price_data = {
                "id": price.id,
                "seller_name": price.seller_name,
                "seller_url": price.seller_url,
                "currency": price.currency,
                "price": float(price.price),
                "min_order_qty": price.min_order_qty,
                "available_qty": price.available_qty,
                "warranty": price.warranty,
                "valid_from": price.valid_from,
                "valid_to": price.valid_to,
                "note": price.note
            }

            # Apply user-specific pricing logic
            if current_user:
                if current_user.role in ["pro", "fleet"]:
                    # Apply pro discount
                    price_data["original_price"] = price_data["price"]
                    price_data["price"] = price_data["price"] * 0.9  # 10% pro discount
                    price_data["price_tier"] = "pro"
                else:
                    price_data["price_tier"] = "retail"
            else:
                price_data["price_tier"] = "retail"

            prices.append(price_data)

        response_data["prices"] = sorted(prices, key=lambda x: x["price"])

    # Add alternatives if requested
    if include_alternatives:
        alternatives = await get_part_alternatives_internal(db, part_id, limit=10)
        response_data["alternatives"] = alternatives

    # Add cross-references if requested
    if include_cross_references:
        cross_refs = await get_part_cross_references_internal(db, part_id)
        response_data["cross_references"] = cross_refs

    return response_data


@router.get("/parts/{part_id}/alternatives", response_model=List[PartAlternativeResponse])
async def get_part_alternatives(
    part_id: int = Path(..., description="Part ID"),
    limit: int = Query(20, ge=1, le=100,
                       description="Maximum number of alternatives"),
    sort_by: str = Query("compatibility",
                         description="Sort by: compatibility, price, availability"),
    db: Session = Depends(get_db)
):
    """Get alternative parts for a given part."""
    return await get_part_alternatives_internal(db, part_id, limit, sort_by)


async def get_part_alternatives_internal(
    db: Session,
    part_id: int,
    limit: int = 20,
    sort_by: str = "compatibility"
) -> List[Dict[str, Any]]:
    """Internal function to get part alternatives."""

    # Get the source part
    source_part = db.query(Part).filter(Part.id == part_id).first()
    if not source_part:
        return []

    # Find alternatives based on:
    # 1. Same vehicle make/model but different brands
    # 2. Same OEM code
    # 3. Same category and similar specifications

    alternatives_query = db.query(Part).filter(
        Part.id != part_id,
        Part.status == "active",
        or_(
            # Same vehicle, different brand
            and_(
                Part.vehicle_make == source_part.vehicle_make,
                Part.vehicle_model == source_part.vehicle_model,
                Part.category == source_part.category,
                Part.brand_oem != source_part.brand_oem
            ),
            # Same OEM code
            and_(
                Part.oem_code.isnot(None),
                Part.oem_code == source_part.oem_code
            ),
            # Similar alt codes
            and_(
                Part.alt_codes.isnot(None),
                source_part.oem_code.isnot(None),
                Part.alt_codes.contains(source_part.oem_code)
            )
        )
    ).options(
        joinedload(Part.prices),
        joinedload(Part.images)
    )

    # Apply sorting
    if sort_by == "price":
        alternatives_query = alternatives_query.join(Price).order_by(Price.price.asc())
    elif sort_by == "availability":
        alternatives_query = alternatives_query.join(Price).order_by(
            Price.available_qty.desc().nullslast()
        )
    else:  # compatibility
        alternatives_query = alternatives_query.order_by(
            # Prioritize same vehicle make/model
            func.case(
                (Part.vehicle_make == source_part.vehicle_make, 1),
                else_=2
            ),
            # Then by same OEM code
            func.case(
                (Part.oem_code == source_part.oem_code, 1),
                else_=2
            )
        )

    alternatives = alternatives_query.limit(limit).all()

    result = []
    for alt in alternatives:
        # Calculate compatibility score
        compatibility_score = 0
        if alt.vehicle_make == source_part.vehicle_make:
            compatibility_score += 30
        if alt.vehicle_model == source_part.vehicle_model:
            compatibility_score += 30
        if alt.oem_code == source_part.oem_code:
            compatibility_score += 40

        # Get best price
        best_price = None
        if alt.prices:
            valid_prices = [
                p for p in alt.prices
                if (not p.valid_from or p.valid_from <= datetime.now().date()) and
                   (not p.valid_to or p.valid_to >= datetime.now().date())
            ]
            if valid_prices:
                best_price = min(valid_prices, key=lambda x: x.price)

        # Get main image
        main_image = None
        if alt.images:
            main_images = [img for img in alt.images if img.image_type == "main" and img.is_active]
            if main_images:
                main_image = sorted(main_images, key=lambda x: x.sort_order)[0]

        result.append({
            "id": alt.id,
            "name": alt.part_name,
            "brand": alt.brand_oem,
            "oem_code": alt.oem_code,
            "compatibility_score": compatibility_score,
            "compatibility_notes": alt.compatibility_notes,
            "vehicle_make": alt.vehicle_make,
            "vehicle_model": alt.vehicle_model,
            "price": {
                "amount": float(best_price.price) if best_price else None,
                "currency": best_price.currency if best_price else "IRR",
                "seller": best_price.seller_name if best_price else None,
                "min_order_qty": best_price.min_order_qty if best_price else 1
            } if best_price else None,
            "image": {
                "url": main_image.image_url,
                "alt_text": main_image.alt_text
            } if main_image else None,
            "availability": ("in_stock" if best_price and best_price.available_qty
                             and best_price.available_qty > 0 else "out_of_stock")
        })

    return result


@router.get("/parts/{part_id}/cross-references", response_model=PartCrossReferenceResponse)
async def get_part_cross_references(
    part_id: int = Path(..., description="Part ID"),
    db: Session = Depends(get_db)
):
    """Get cross-reference information for a part."""
    return await get_part_cross_references_internal(db, part_id)


async def get_part_cross_references_internal(db: Session, part_id: int) -> Dict[str, Any]:
    """Internal function to get part cross-references."""

    part = db.query(Part).filter(Part.id == part_id).first()
    if not part:
        return {}

    # OEM References - parts with same OEM code from different brands
    oem_references = []
    if part.oem_code:
        oem_refs = db.query(Part).filter(
            Part.oem_code == part.oem_code,
            Part.id != part_id,
            Part.status == "active"
        ).options(joinedload(Part.prices)).limit(20).all()

        for ref in oem_refs:
            best_price = None
            if ref.prices:
                valid_prices = [
                    p for p in ref.prices
                    if (not p.valid_from or p.valid_from <= datetime.now().date()) and
                       (not p.valid_to or p.valid_to >= datetime.now().date())
                ]
                if valid_prices:
                    best_price = min(valid_prices, key=lambda x: x.price)

            oem_references.append({
                "id": ref.id,
                "name": ref.part_name,
                "brand": ref.brand_oem,
                "oem_code": ref.oem_code,
                "vehicle_make": ref.vehicle_make,
                "vehicle_model": ref.vehicle_model,
                "price": float(best_price.price) if best_price else None,
                "currency": best_price.currency if best_price else "IRR",
                "availability": ("in_stock" if best_price and best_price.available_qty
                                 and best_price.available_qty > 0 else "unknown")
            })

    # Supersessions - newer versions of this part
    supersessions = []
    if part.alt_codes:
        alt_codes = [code.strip() for code in part.alt_codes.split(',')]
        supersession_parts = db.query(Part).filter(
            or_(*[Part.oem_code.in_(alt_codes) for _ in alt_codes]),
            Part.id != part_id,
            Part.status == "active",
            # Only consider newer parts
            Part.created_at > part.created_at
        ).options(joinedload(Part.prices)).limit(10).all()

        for sup in supersession_parts:
            best_price = None
            if sup.prices:
                valid_prices = [
                    p for p in sup.prices
                    if (not p.valid_from or p.valid_from <= datetime.now().date()) and
                       (not p.valid_to or p.valid_to >= datetime.now().date())
                ]
                if valid_prices:
                    best_price = min(valid_prices, key=lambda x: x.price)

            supersessions.append({
                "id": sup.id,
                "name": sup.part_name,
                "brand": sup.brand_oem,
                "oem_code": sup.oem_code,
                "superseded_codes": [part.oem_code] if part.oem_code else [],
                "improvements": "Updated version with enhanced specifications",
                "price": float(best_price.price) if best_price else None,
                "currency": best_price.currency if best_price else "IRR",
                "availability": ("in_stock" if best_price and best_price.available_qty
                                 and best_price.available_qty > 0 else "unknown")
            })

    # Compatibility Matrix - parts for different vehicle variations
    compatibility_matrix = []
    related_parts = db.query(Part).filter(
        Part.category == part.category,
        Part.vehicle_make == part.vehicle_make,
        Part.part_name.contains(part.part_name.split()[0] if part.part_name else ""),
        Part.id != part_id,
        Part.status == "active"
    ).limit(15).all()

    for rel in related_parts:
        compatibility_matrix.append({
            "vehicle_make": rel.vehicle_make,
            "vehicle_model": rel.vehicle_model,
            "vehicle_trim": rel.vehicle_trim,
            "year_from": rel.model_year_from,
            "year_to": rel.model_year_to,
            "engine_code": rel.engine_code,
            "part_id": rel.id,
            "part_name": rel.part_name,
            "oem_code": rel.oem_code,
            "compatibility": "direct" if rel.oem_code == part.oem_code else "alternative"
        })

    return {
        "part_id": part_id,
        "oem_references": oem_references,
        "alternatives": await get_part_alternatives_internal(db, part_id, limit=10),
        "supersessions": supersessions,
        "compatibility_matrix": compatibility_matrix
    }


@router.post("/parts/{part_id}/check-compatibility", response_model=PartCompatibilityResponse)
async def check_part_compatibility(
    vehicle_info: PartCompatibilityRequest,
    part_id: int = Path(..., description="Part ID"),
    db: Session = Depends(get_db)
):
    """Check if a part is compatible with a specific vehicle."""

    part = db.query(Part).filter(Part.id == part_id, Part.status == "active").first()
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")

    compatibility_result = {
        "part_id": part_id,
        "vehicle_info": vehicle_info.dict(),
        "is_compatible": False,
        "compatibility_level": "unknown",
        "confidence_score": 0,
        "compatibility_notes": [],
        "alternative_suggestions": []
    }

    score = 0
    notes = []

    # Check vehicle make compatibility
    if vehicle_info.make and part.vehicle_make:
        if part.vehicle_make.lower() == vehicle_info.make.lower():
            score += 30
            notes.append("Exact vehicle make match")
        else:
            notes.append(
                f"Different vehicle make: part is for {part.vehicle_make}, "
                f"vehicle is {vehicle_info.make}")

    # Check vehicle model compatibility
    if vehicle_info.model and part.vehicle_model:
        if part.vehicle_model.lower() == vehicle_info.model.lower():
            score += 25
            notes.append("Exact vehicle model match")
        else:
            notes.append(
                f"Different vehicle model: part is for {
                    part.vehicle_model}, vehicle is {
                    vehicle_info.model}")

    # Check year compatibility
    if vehicle_info.year:
        if part.model_year_from and part.model_year_to:
            if part.model_year_from <= vehicle_info.year <= part.model_year_to:
                score += 20
                notes.append(
                    f"Year {
                        vehicle_info.year} is within compatibility range {
                        part.model_year_from}-{
                        part.model_year_to}")
            else:
                notes.append(
                    f"Year {
                        vehicle_info.year} is outside compatibility range {
                        part.model_year_from}-{
                        part.model_year_to}")
        elif part.model_year_from and vehicle_info.year >= part.model_year_from:
            score += 15
            notes.append(
                f"Year {
                    vehicle_info.year} is after part introduction year {
                    part.model_year_from}")

    # Check engine code compatibility
    if vehicle_info.engine_code and part.engine_code:
        if part.engine_code.lower() == vehicle_info.engine_code.lower():
            score += 15
            notes.append("Exact engine code match")
        else:
            notes.append(
                f"Different engine code: part is for {
                    part.engine_code}, vehicle has {
                    vehicle_info.engine_code}")

    # Check trim compatibility
    if vehicle_info.trim and part.vehicle_trim:
        if part.vehicle_trim.lower() == vehicle_info.trim.lower():
            score += 10
            notes.append("Exact trim match")
        else:
            notes.append(
                f"Different trim: part is for {
                    part.vehicle_trim}, vehicle is {
                    vehicle_info.trim}")

    # Determine compatibility level
    if score >= 70:
        compatibility_result["is_compatible"] = True
        compatibility_result["compatibility_level"] = "direct"
    elif score >= 50:
        compatibility_result["is_compatible"] = True
        compatibility_result["compatibility_level"] = "likely"
    elif score >= 30:
        compatibility_result["compatibility_level"] = "possible"
        # Find alternatives
        alternatives = await get_part_alternatives_internal(db, part_id, limit=5)
        compatibility_result["alternative_suggestions"] = alternatives[:3]
    else:
        compatibility_result["compatibility_level"] = "incompatible"
        # Find alternatives
        alternatives = await get_part_alternatives_internal(db, part_id, limit=5)
        compatibility_result["alternative_suggestions"] = alternatives[:5]

    compatibility_result["confidence_score"] = score
    compatibility_result["compatibility_notes"] = notes

    if part.compatibility_notes:
        compatibility_result["compatibility_notes"].append(
            f"Manufacturer notes: {part.compatibility_notes}")

    return compatibility_result


@router.get("/parts/{part_id}/specifications", response_model=List[PartSpecificationResponse])
async def get_part_specifications(
    part_id: int = Path(..., description="Part ID"),
    db: Session = Depends(get_db)
):
    """Get detailed specifications for a part."""

    specifications = db.query(PartSpecification).filter(
        PartSpecification.part_id == part_id
    ).order_by(PartSpecification.sort_order).all()

    return [
        {
            "id": spec.id,
            "name": spec.spec_name,
            "value": spec.spec_value,
            "unit": spec.spec_unit,
            "type": spec.spec_type,
            "is_required": spec.is_required,
            "sort_order": spec.sort_order
        }
        for spec in specifications
    ]


@router.get("/parts/{part_id}/images", response_model=List[PartImageResponse])
async def get_part_images(
    part_id: int = Path(..., description="Part ID"),
    image_type: Optional[str] = Query(None, description="Filter by image type"),
    db: Session = Depends(get_db)
):
    """Get images for a part."""

    query = db.query(PartImage).filter(
        PartImage.part_id == part_id,
        PartImage.is_active
    )

    if image_type:
        query = query.filter(PartImage.image_type == image_type)

    images = query.order_by(PartImage.sort_order).all()

    return [
        {
            "id": img.id,
            "url": img.image_url,
            "type": img.image_type,
            "alt_text": img.alt_text,
            "sort_order": img.sort_order
        }
        for img in images
    ]


@router.get("/parts/{part_id}/pricing", response_model=List[PartPriceResponse])
async def get_part_pricing(
    part_id: int = Path(..., description="Part ID"),
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get pricing information for a part."""

    # Get valid prices
    today = datetime.now().date()
    prices = db.query(Price).filter(
        Price.part_id == part_id,
        or_(Price.valid_from.is_(None), Price.valid_from <= today),
        or_(Price.valid_to.is_(None), Price.valid_to >= today)
    ).order_by(Price.price).all()

    result = []
    for price in prices:
        price_data = {
            "id": price.id,
            "seller_name": price.seller_name,
            "seller_url": price.seller_url,
            "currency": price.currency,
            "price": float(price.price),
            "original_price": float(price.price),
            "min_order_qty": price.min_order_qty,
            "available_qty": price.available_qty,
            "warranty": price.warranty,
            "note": price.note,
            "price_tier": "retail"
        }

        # Apply user-specific pricing
        if current_user and current_user.role in ["pro", "fleet"]:
            discount = 0.1 if current_user.role == "pro" else 0.15  # 10% for pro, 15% for fleet
            price_data["price"] = price_data["price"] * (1 - discount)
            price_data["price_tier"] = current_user.role
            price_data["discount_percentage"] = discount * 100

        result.append(price_data)

    return result


@router.get("/search", response_model=PaginatedResponse)
async def search_parts(
    query: str = Query(..., description="Search query"),
    category: Optional[str] = Query(None, description="Filter by category"),
    vehicle_make: Optional[str] = Query(None, description="Filter by vehicle make"),
    vehicle_model: Optional[str] = Query(None, description="Filter by vehicle model"),
    min_price: Optional[float] = Query(None, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, description="Maximum price filter"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: str = Query("relevance",
                         description="Sort by: relevance, price_asc, price_desc, name"),
    db: Session = Depends(get_db)
):
    """Search parts with comprehensive filtering and sorting."""

    # Base query
    query_obj = db.query(Part).filter(Part.status == "active")

    # Text search
    if query:
        search_filter = or_(
            Part.part_name.contains(query),
            Part.oem_code.contains(query),
            Part.alt_codes.contains(query),
            Part.brand_oem.contains(query)
        )
        query_obj = query_obj.filter(search_filter)

    # Category filter
    if category:
        query_obj = query_obj.filter(Part.category.ilike(f"%{category}%"))

    # Vehicle filters
    if vehicle_make:
        query_obj = query_obj.filter(Part.vehicle_make.ilike(f"%{vehicle_make}%"))

    if vehicle_model:
        query_obj = query_obj.filter(Part.vehicle_model.ilike(f"%{vehicle_model}%"))

    # Price filters
    if min_price is not None or max_price is not None:
        query_obj = query_obj.join(Price)
        if min_price is not None:
            query_obj = query_obj.filter(Price.price >= min_price)
        if max_price is not None:
            query_obj = query_obj.filter(Price.price <= max_price)

    # Sorting
    if sort_by == "price_asc":
        query_obj = query_obj.join(Price).order_by(Price.price.asc())
    elif sort_by == "price_desc":
        query_obj = query_obj.join(Price).order_by(Price.price.desc())
    elif sort_by == "name":
        query_obj = query_obj.order_by(Part.part_name.asc())
    else:  # relevance
        # Sort by text relevance and recency
        query_obj = query_obj.order_by(
            Part.updated_at.desc(),
            Part.part_name
        )

    # Pagination
    total = query_obj.count()
    offset = (page - 1) * page_size
    parts = query_obj.offset(offset).limit(page_size).options(
        joinedload(Part.prices),
        joinedload(Part.images),
        joinedload(Part.category_obj)
    ).all()

    # Format results
    items = []
    for part in parts:
        # Get best price
        best_price = None
        if part.prices:
            today = datetime.now().date()
            valid_prices = [
                p for p in part.prices
                if (not p.valid_from or p.valid_from <= today) and
                   (not p.valid_to or p.valid_to >= today)
            ]
            if valid_prices:
                best_price = min(valid_prices, key=lambda x: x.price)

        # Get main image
        main_image = None
        if part.images:
            main_images = [img for img in part.images if img.image_type == "main" and img.is_active]
            if main_images:
                main_image = sorted(main_images, key=lambda x: x.sort_order)[0]

        items.append({
            "id": part.id,
            "name": part.part_name,
            "brand": part.brand_oem,
            "category": part.category,
            "oem_code": part.oem_code,
            "vehicle_make": part.vehicle_make,
            "vehicle_model": part.vehicle_model,
            "price": {
                "amount": float(best_price.price) if best_price else None,
                "currency": best_price.currency if best_price else "IRR",
                "seller": best_price.seller_name if best_price else None
            } if best_price else None,
            "image": {
                "url": main_image.image_url,
                "alt_text": main_image.alt_text
            } if main_image else None,
            "availability": ("in_stock" if best_price and best_price.available_qty
                             and best_price.available_qty > 0 else "out_of_stock")
        })

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }
