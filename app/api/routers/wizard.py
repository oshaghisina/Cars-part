"""Wizard API endpoints for guided part search flow."""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.wizard_service import WizardService

router = APIRouter()


class WizardSessionCreate(BaseModel):
    """Request model for creating wizard session."""

    user_id: str
    state: str = "start"


class WizardSessionUpdate(BaseModel):
    """Request model for updating wizard session."""

    state: Optional[str] = None
    vehicle_data: Optional[Dict[str, Any]] = None
    part_data: Optional[Dict[str, Any]] = None
    contact_data: Optional[Dict[str, Any]] = None


class WizardSessionResponse(BaseModel):
    """Response model for wizard session."""

    id: int
    user_id: str
    state: str
    vehicle_data: Dict[str, Any]
    part_data: Dict[str, Any]
    contact_data: Dict[str, Any]
    created_at: str
    updated_at: str


@router.post("/sessions", response_model=WizardSessionResponse)
async def create_wizard_session(request: WizardSessionCreate, db: Session = Depends(get_db)):
    """Create a new wizard session."""
    wizard_service = WizardService(db)

    # Check if session already exists
    existing_session = wizard_service.get_session(request.user_id)
    if existing_session:
        # Update existing session
        existing_session.state = request.state
        db.commit()
        db.refresh(existing_session)
        return WizardSessionResponse(
            id=existing_session.id,
            user_id=existing_session.user_id,
            state=existing_session.state,
            vehicle_data=existing_session.get_vehicle_data(),
            part_data=existing_session.get_part_data(),
            contact_data=existing_session.get_contact_data(),
            created_at=existing_session.created_at.isoformat(),
            updated_at=existing_session.updated_at.isoformat(),
        )

    # Create new session
    session = wizard_service.create_session(request.user_id, request.state)
    return WizardSessionResponse(
        id=session.id,
        user_id=session.user_id,
        state=session.state,
        vehicle_data=session.get_vehicle_data(),
        part_data=session.get_part_data(),
        contact_data=session.get_contact_data(),
        created_at=session.created_at.isoformat(),
        updated_at=session.updated_at.isoformat(),
    )


@router.get("/sessions/{user_id}", response_model=WizardSessionResponse)
async def get_wizard_session(user_id: str, db: Session = Depends(get_db)):
    """Get wizard session for user."""
    wizard_service = WizardService(db)
    session = wizard_service.get_session(user_id)

    if not session:
        raise HTTPException(status_code=404, detail="Wizard session not found")

    return WizardSessionResponse(
        id=session.id,
        user_id=session.user_id,
        state=session.state,
        vehicle_data=session.get_vehicle_data(),
        part_data=session.get_part_data(),
        contact_data=session.get_contact_data(),
        created_at=session.created_at.isoformat(),
        updated_at=session.updated_at.isoformat(),
    )


@router.put("/sessions/{user_id}", response_model=WizardSessionResponse)
async def update_wizard_session(user_id: str, request: WizardSessionUpdate, db: Session = Depends(get_db)):
    """Update wizard session."""
    wizard_service = WizardService(db)
    session = wizard_service.get_session(user_id)

    if not session:
        raise HTTPException(status_code=404, detail="Wizard session not found")

    # Update session data
    if request.state:
        session.state = request.state
    if request.vehicle_data is not None:
        session.set_vehicle_data(request.vehicle_data)
    if request.part_data is not None:
        session.set_part_data(request.part_data)
    if request.contact_data is not None:
        session.set_contact_data(request.contact_data)

    db.commit()
    db.refresh(session)

    return WizardSessionResponse(
        id=session.id,
        user_id=session.user_id,
        state=session.state,
        vehicle_data=session.get_vehicle_data(),
        part_data=session.get_part_data(),
        contact_data=session.get_contact_data(),
        created_at=session.created_at.isoformat(),
        updated_at=session.updated_at.isoformat(),
    )


@router.delete("/sessions/{user_id}")
async def clear_wizard_session(user_id: str, db: Session = Depends(get_db)):
    """Clear wizard session."""
    wizard_service = WizardService(db)
    success = wizard_service.clear_session(user_id)

    if not success:
        raise HTTPException(status_code=404, detail="Wizard session not found")

    return {"message": "Wizard session cleared successfully"}


@router.get("/brands", response_model=List[str])
async def get_available_brands(db: Session = Depends(get_db)):
    """Get list of available car brands."""
    wizard_service = WizardService(db)
    return wizard_service.get_available_brands()


@router.get("/models", response_model=List[str])
async def get_available_models(brand: str = Query(..., description="Car brand"), db: Session = Depends(get_db)):
    """Get list of available models for a brand."""
    wizard_service = WizardService(db)
    return wizard_service.get_available_models(brand)


@router.get("/categories", response_model=List[str])
async def get_available_categories(
    brand: Optional[str] = Query(None, description="Car brand"),
    model: Optional[str] = Query(None, description="Car model"),
    db: Session = Depends(get_db),
):
    """Get list of available part categories."""
    wizard_service = WizardService(db)
    return wizard_service.get_available_categories(brand, model)


@router.get("/parts", response_model=List[Dict[str, Any]])
async def get_available_parts(
    brand: Optional[str] = Query(None, description="Car brand"),
    model: Optional[str] = Query(None, description="Car model"),
    category: Optional[str] = Query(None, description="Part category"),
    db: Session = Depends(get_db),
):
    """Get list of available parts with optional filters."""
    wizard_service = WizardService(db)
    return wizard_service.get_available_parts(brand, model, category)


@router.post("/search", response_model=List[Dict[str, Any]])
async def search_parts_by_criteria(
    vehicle_data: Dict[str, Any],
    part_data: Dict[str, Any],
    db: Session = Depends(get_db),
):
    """Search parts based on collected wizard data."""
    wizard_service = WizardService(db)
    return wizard_service.search_parts_by_criteria(vehicle_data, part_data)
