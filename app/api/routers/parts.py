from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.parts_service import PartsService

router = APIRouter()


class PartResponse(BaseModel):
    id: int
    part_name: str
    brand_oem: str
    vehicle_make: str
    vehicle_model: str
    vehicle_trim: Optional[str]
    oem_code: Optional[str]
    category: str
    subcategory: Optional[str]
    position: Optional[str]
    unit: str
    pack_size: Optional[int]
    status: str
    created_at: str
    updated_at: str


class PartCreateRequest(BaseModel):
    part_name: str
    brand_oem: str
    vehicle_make: str
    vehicle_model: str
    vehicle_trim: Optional[str] = None
    oem_code: Optional[str] = None
    category: str
    subcategory: Optional[str] = None
    position: Optional[str] = None
    unit: str = "pcs"
    pack_size: Optional[int] = None
    status: str = "active"


@router.get("/", response_model=List[PartResponse])
async def list_parts(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = Query(None, description="Filter by status"),
    category: Optional[str] = Query(None, description="Filter by category"),
    vehicle_make: Optional[str] = Query(None, description="Filter by vehicle make"),
    search: Optional[str] = Query(None, description="Search in part name, OEM code, or vehicle model"),
    db: Session = Depends(get_db),
):
    parts_service = PartsService(db)
    parts = parts_service.get_parts(
        skip=skip,
        limit=limit,
        status=status,
        category=category,
        vehicle_make=vehicle_make,
        search=search,
    )

    return [
        PartResponse(
            id=part.id,
            part_name=part.part_name,
            brand_oem=part.brand_oem,
            vehicle_make=part.vehicle_make,
            vehicle_model=part.vehicle_model,
            vehicle_trim=part.vehicle_trim,
            oem_code=part.oem_code,
            category=part.category,
            subcategory=part.subcategory,
            position=part.position,
            unit=part.unit,
            pack_size=part.pack_size,
            status=part.status,
            created_at=part.created_at.isoformat(),
            updated_at=part.updated_at.isoformat(),
        )
        for part in parts
    ]


@router.post("/", response_model=PartResponse)
async def create_part(request: PartCreateRequest, db: Session = Depends(get_db)):
    parts_service = PartsService(db)
    part = parts_service.create_part(request.dict())

    if not part:
        raise HTTPException(status_code=400, detail="Failed to create part")

    return PartResponse(
        id=part.id,
        part_name=part.part_name,
        brand_oem=part.brand_oem,
        vehicle_make=part.vehicle_make,
        vehicle_model=part.vehicle_model,
        vehicle_trim=part.vehicle_trim,
        oem_code=part.oem_code,
        category=part.category,
        subcategory=part.subcategory,
        position=part.position,
        unit=part.unit,
        pack_size=part.pack_size,
        status=part.status,
        created_at=part.created_at.isoformat(),
        updated_at=part.updated_at.isoformat(),
    )


@router.get("/{part_id}", response_model=PartResponse)
async def get_part(part_id: int, db: Session = Depends(get_db)):
    parts_service = PartsService(db)
    part = parts_service.get_part_by_id(part_id)

    if not part:
        raise HTTPException(status_code=404, detail="Part not found")

    return PartResponse(
        id=part.id,
        part_name=part.part_name,
        brand_oem=part.brand_oem,
        vehicle_make=part.vehicle_make,
        vehicle_model=part.vehicle_model,
        vehicle_trim=part.vehicle_trim,
        oem_code=part.oem_code,
        category=part.category,
        subcategory=part.subcategory,
        position=part.position,
        unit=part.unit,
        pack_size=part.pack_size,
        status=part.status,
        created_at=part.created_at.isoformat(),
        updated_at=part.updated_at.isoformat(),
    )


@router.delete("/{part_id}")
async def delete_part(part_id: int, db: Session = Depends(get_db)):
    parts_service = PartsService(db)
    success = parts_service.delete_part(part_id)

    if not success:
        raise HTTPException(status_code=404, detail="Part not found")

    return {"message": "Part deleted successfully"}


@router.get("/categories/list")
async def get_categories(db: Session = Depends(get_db)):
    parts_service = PartsService(db)
    categories = parts_service.get_categories()
    return {"categories": categories}


@router.get("/vehicle-makes/list")
async def get_vehicle_makes(db: Session = Depends(get_db)):
    parts_service = PartsService(db)
    makes = parts_service.get_vehicle_makes()
    return {"vehicle_makes": makes}
