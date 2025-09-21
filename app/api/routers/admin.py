"""Admin API endpoints."""

from typing import Dict
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.database import get_db
from app.core.auth import get_current_user
from app.db.models import User
from app.services.settings_service import SettingsService
from app.services.user_service import UserService
from app.schemas.admin_schemas import (
    SettingsResponse,
    AdminUserResponse,
    AdminUserListResponse,
    AdminUserCreate,
    SystemStatusResponse,
)
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/settings", response_model=SettingsResponse)
async def get_settings(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Get system settings."""
    # Check if user is admin
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    settings_service = SettingsService(db)
    settings = settings_service.get_settings()

    return SettingsResponse(settings=settings, total=len(settings))


@router.put("/settings")
async def update_settings(
    settings: Dict[str, str],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update system settings."""
    # Check if user is admin
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    settings_service = SettingsService(db)
    updated_settings = settings_service.set_settings(settings, int(current_user.id))

    logger.info(f"Settings updated by user {current_user.username}: {list(settings.keys())}")

    return {"message": "Settings updated successfully", "updated": updated_settings}


@router.get("/users", response_model=AdminUserListResponse)
async def list_admin_users(
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all admin users."""
    # Check if user is admin
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    # Get total count
    total = db.query(func.count(User.id)).scalar()

    # Get paginated users
    skip = (page - 1) * limit
    users = db.query(User).offset(skip).limit(limit).all()

    user_responses = [
        AdminUserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
            last_login=user.last_login,
        )
        for user in users
    ]

    total_pages = (total + limit - 1) // limit

    return AdminUserListResponse(
        users=user_responses, total=total, page=page, limit=limit, total_pages=total_pages
    )


@router.post("/users", response_model=AdminUserResponse)
async def create_admin_user(
    user_data: AdminUserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new admin user."""
    # Check if user is super_admin
    if current_user.role != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Super admin access required"
        )

    user_service = UserService(db)

    try:
        # Create user using the existing user creation logic
        from app.schemas.user_schemas import UserCreate

        user_create = UserCreate(
            username=user_data.username,
            email=user_data.email,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            password=user_data.password,
            role=user_data.role,
        )

        new_user = await user_service.create_user(user_create)

        return AdminUserResponse(
            id=new_user.id,
            username=new_user.username,
            email=new_user.email,
            first_name=new_user.first_name,
            last_name=new_user.last_name,
            role=new_user.role,
            is_active=new_user.is_active,
            created_at=new_user.created_at,
            last_login=new_user.last_login,
        )

    except Exception as e:
        logger.error(f"Error creating admin user: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/status", response_model=SystemStatusResponse)
async def get_system_status(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Get system status and statistics."""
    # Check if user is admin
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    # Get basic statistics
    from app.db.models import Part, Order

    total_users = db.query(func.count(User.id)).scalar()
    total_parts = db.query(func.count(Part.id)).scalar()
    total_orders = db.query(func.count(Order.id)).scalar()

    # Check database status
    try:
        db.execute("SELECT 1")
        database_status = "connected"
    except Exception:
        database_status = "disconnected"

    return SystemStatusResponse(
        status="healthy",
        version="1.0.0",
        environment="development",  # Could be from settings
        database_status=database_status,
        total_users=total_users,
        total_parts=total_parts,
        total_orders=total_orders,
        last_backup=None,  # TODO: Implement backup tracking
    )
