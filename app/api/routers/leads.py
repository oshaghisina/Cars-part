"""Leads API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.db.database import get_db
from app.db.models import Lead
from app.services.lead_service import LeadService

router = APIRouter()


class LeadResponse(BaseModel):
    """Response model for lead data."""
    id: int
    telegram_user_id: str
    first_name: Optional[str]
    last_name: Optional[str]
    phone_e164: str
    city: Optional[str]
    notes: Optional[str]
    consent: bool
    created_at: str
    updated_at: str


class LeadCreateRequest(BaseModel):
    """Request model for creating/updating a lead."""
    telegram_user_id: str
    phone_e164: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    city: Optional[str] = None
    notes: Optional[str] = None
    consent: bool = True


@router.get("/", response_model=List[LeadResponse])
async def list_leads(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all leads with pagination."""
    leads = db.query(Lead).offset(skip).limit(limit).all()
    
    return [
        LeadResponse(
            id=lead.id,
            telegram_user_id=lead.telegram_user_id,
            first_name=lead.first_name,
            last_name=lead.last_name,
            phone_e164=lead.phone_e164,
            city=lead.city,
            notes=lead.notes,
            consent=lead.consent,
            created_at=lead.created_at.isoformat(),
            updated_at=lead.updated_at.isoformat()
        )
        for lead in leads
    ]


@router.post("/", response_model=LeadResponse)
async def create_lead(
    request: LeadCreateRequest,
    db: Session = Depends(get_db)
):
    """Create or update a lead."""
    lead_service = LeadService(db)
    
    result = lead_service.get_or_create_lead(
        telegram_user_id=request.telegram_user_id,
        phone_number=request.phone_e164,
        first_name=request.first_name,
        last_name=request.last_name
    )
    
    if not result["lead"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    lead = result["lead"]
    return LeadResponse(
        id=lead.id,
        telegram_user_id=lead.telegram_user_id,
        first_name=lead.first_name,
        last_name=lead.last_name,
        phone_e164=lead.phone_e164,
        city=lead.city,
        notes=lead.notes,
        consent=lead.consent,
        created_at=lead.created_at.isoformat(),
        updated_at=lead.updated_at.isoformat()
    )


@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(lead_id: int, db: Session = Depends(get_db)):
    """Get lead by ID."""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    return LeadResponse(
        id=lead.id,
        telegram_user_id=lead.telegram_user_id,
        first_name=lead.first_name,
        last_name=lead.last_name,
        phone_e164=lead.phone_e164,
        city=lead.city,
        notes=lead.notes,
        consent=lead.consent,
        created_at=lead.created_at.isoformat(),
        updated_at=lead.updated_at.isoformat()
    )


@router.put("/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: int,
    request: LeadCreateRequest,
    db: Session = Depends(get_db)
):
    """Update lead by ID."""
    lead_service = LeadService(db)
    
    result = lead_service.update_lead_info(
        lead_id=lead_id,
        phone_e164=request.phone_e164,
        first_name=request.first_name,
        last_name=request.last_name,
        city=request.city,
        notes=request.notes
    )
    
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["message"])
    
    lead = result["lead"]
    return LeadResponse(
        id=lead.id,
        telegram_user_id=lead.telegram_user_id,
        first_name=lead.first_name,
        last_name=lead.last_name,
        phone_e164=lead.phone_e164,
        city=lead.city,
        notes=lead.notes,
        consent=lead.consent,
        created_at=lead.created_at.isoformat(),
        updated_at=lead.updated_at.isoformat()
    )
