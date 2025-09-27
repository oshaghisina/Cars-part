from io import BytesIO
from typing import List, Optional

import pandas as pd
from fastapi import APIRouter, Depends, File, HTTPException, Query, Response, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.parts_service import PartsService

router = APIRouter()


def _serialize_part(part) -> "PartResponse":
    """Convert ORM part instance into response model."""
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
        created_at=part.created_at.isoformat() if part.created_at else "",
        updated_at=part.updated_at.isoformat() if part.updated_at else "",
    )


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


class PartUpdateRequest(BaseModel):
    part_name: Optional[str] = None
    brand_oem: Optional[str] = None
    vehicle_make: Optional[str] = None
    vehicle_model: Optional[str] = None
    vehicle_trim: Optional[str] = None
    oem_code: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    position: Optional[str] = None
    unit: Optional[str] = None
    pack_size: Optional[int] = None
    status: Optional[str] = None


@router.get("/", response_model=List[PartResponse])
async def list_parts(
    response: Response,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = Query(None, description="Filter by status"),
    category: Optional[str] = Query(None, description="Filter by category"),
    vehicle_make: Optional[str] = Query(None, description="Filter by vehicle make"),
    search: Optional[str] = Query(
        None, description="Search in part name, OEM code, or vehicle model"
    ),
    db: Session = Depends(get_db),
):
    parts_service = PartsService(db)
    parts, total = parts_service.get_parts_with_total(
        skip=skip,
        limit=limit,
        status=status,
        category=category,
        vehicle_make=vehicle_make,
        search=search,
    )

    response.headers["X-Total-Count"] = str(total)

    return [_serialize_part(part) for part in parts]


@router.post("/", response_model=PartResponse)
async def create_part(request: PartCreateRequest, db: Session = Depends(get_db)):
    parts_service = PartsService(db)
    part = parts_service.create_part(request.dict())

    if not part:
        raise HTTPException(status_code=400, detail="Failed to create part")

    return _serialize_part(part)


@router.get("/{part_id}", response_model=PartResponse)
async def get_part(part_id: int, db: Session = Depends(get_db)):
    parts_service = PartsService(db)
    part = parts_service.get_part_by_id(part_id)

    if not part:
        raise HTTPException(status_code=404, detail="Part not found")

    return _serialize_part(part)


@router.put("/{part_id}", response_model=PartResponse)
async def update_part(
    part_id: int,
    request: PartUpdateRequest,
    db: Session = Depends(get_db),
):
    parts_service = PartsService(db)

    update_data = request.dict(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    part = parts_service.update_part(part_id, update_data)

    if not part:
        raise HTTPException(status_code=404, detail="Part not found")

    return _serialize_part(part)


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


@router.get("/search", response_model=List[PartResponse])
async def search_parts(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results"),
    db: Session = Depends(get_db),
):
    parts_service = PartsService(db)
    parts = parts_service.search_parts(q, limit=limit)
    return [_serialize_part(part) for part in parts]


@router.post("/bulk-import")
async def bulk_import_parts(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Uploaded file must have a filename")

    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    try:
        lower_name = file.filename.lower()
        if lower_name.endswith(".csv"):
            dataframe = pd.read_csv(BytesIO(contents))
        elif lower_name.endswith((".xlsx", ".xls")):
            dataframe = pd.read_excel(BytesIO(contents))
        else:
            raise HTTPException(
                status_code=400,
                detail="Unsupported file format. Please upload a CSV or Excel file.",
            )
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=400, detail=f"Failed to process file: {exc}") from exc

    parts_service = PartsService(db)
    return parts_service.bulk_import_parts(dataframe)
