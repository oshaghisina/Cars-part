"""User management API endpoints."""

import logging
import secrets
import string
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.auth import create_access_token, get_current_user, verify_token
from app.db.database import get_db
from app.db.models import User
from app.schemas.user_schemas import (
    BulkUserCreate,
    LoginResponse,
    PasswordChange,
    UserCreate,
    UserListResponse,
    UserLogin,
    UserResponse,
    UserStatistics,
    UserSummary,
    UserUpdate,
)
from app.services.user_service import UserService


# Compatibility helper for Pydantic v2/v1 schema creation from ORM objects
def to_model(model_cls, obj):
    """Create a Pydantic model from an ORM object in a version-safe way."""
    if hasattr(model_cls, "model_validate"):
        # Pydantic v2
        return model_cls.model_validate(obj, from_attributes=True)
    # Fallback for Pydantic v1
    return model_cls.from_orm(obj)


logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()


@router.options("/login")
async def login_options():
    """Handle OPTIONS request for login endpoint."""
    return {"message": "OK"}


@router.post("/login", response_model=LoginResponse)
async def login(login_data: UserLogin, request: Request, db: Session = Depends(get_db)):
    """Authenticate user and create session."""
    user_service = UserService(db)

    # Get client IP and user agent
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    # Authenticate user
    user = await user_service.authenticate_user(
        login_data.username_or_email, login_data.password, ip_address, user_agent
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username/email or password",
        )

    # Create session (placeholder - session management not fully implemented)
    await user_service.create_session(user, ip_address, user_agent)

    # Create JWT token with canonical claims (sub=user_id as integer)
    access_token = create_access_token(
        data={"sub": user.id, "user_id": user.id, "username": user.username, "role": user.role}
    )

    # Update last login time
    from datetime import datetime

    user.last_login = datetime.utcnow()  # type: ignore[assignment]
    db.commit()

    # Get TTL from configuration (convert minutes to seconds)
    from app.core.config import settings

    expires_in_seconds = settings.jwt_access_token_expire_minutes * 60

    return LoginResponse(
        access_token=access_token,
        expires_in=expires_in_seconds,
        user=to_model(UserResponse, user),
    )


@router.post("/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Logout user and invalidate session."""
    # Verify token and get user
    token_data = verify_token(credentials.credentials)
    if not token_data:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    # For JWT, we can't invalidate the token itself
    # Session invalidation would be handled by client-side token removal

    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return to_model(UserResponse, current_user)


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update current user information."""
    user_service = UserService(db)

    # type: ignore[arg-type]
    updated_user = await user_service.update_user(int(current_user.id), user_update)
    if not updated_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Activity logging not implemented yet

    return to_model(UserResponse, updated_user)


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Change user password."""
    user_service = UserService(db)

    success = await user_service.change_password(
        int(current_user.id),  # type: ignore[arg-type]
        password_data.current_password,
        password_data.new_password,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to change password"
        )

    # Activity logging not implemented yet

    return {"message": "Password changed successfully"}


@router.get("/", response_model=UserListResponse)
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get users with pagination and search."""
    # Check permission
    if not current_user.has_permission("users.read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
        )

    user_service = UserService(db)
    users = await user_service.get_users(skip, limit, search)

    # Get total count
    total = db.query(User).count()
    if search:
        from sqlalchemy import or_

        total = (
            db.query(User)
            .filter(
                or_(
                    User.username.ilike(f"%{search}%"),
                    User.email.ilike(f"%{search}%"),
                    User.first_name.ilike(f"%{search}%"),
                    User.last_name.ilike(f"%{search}%"),
                )
            )
            .count()
        )

    return UserListResponse(
        users=[to_model(UserSummary, user) for user in users],
        total=total,
        page=skip // limit + 1,
        limit=limit,
        total_pages=(total + limit - 1) // limit,
    )


@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new user."""
    # Check permission
    if not current_user.has_permission("users.create"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
        )

    user_service = UserService(db)

    try:
        user = await user_service.create_user(user_data)

        # Activity logging not implemented yet

        return to_model(UserResponse, user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get user by ID."""
    # Check permission
    if not current_user.has_permission("users.read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
        )

    user_service = UserService(db)
    user = await user_service.get_user_by_id(user_id)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return to_model(UserResponse, user)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update user information."""
    # Check permission
    if not current_user.has_permission("users.update"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
        )

    user_service = UserService(db)

    try:
        updated_user = await user_service.update_user(user_id, user_update)
        if not updated_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        # Activity logging not implemented yet

        return to_model(UserResponse, updated_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete user (soft delete)."""
    # Check permission
    if not current_user.has_permission("users.delete"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
        )

    # Don't allow users to delete themselves
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account",
        )

    user_service = UserService(db)

    try:
        success = await user_service.delete_user(user_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        # Activity logging not implemented yet

        return {"message": "User deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# Role assignment endpoints temporarily disabled - methods not implemented in UserService
# @router.post("/{user_id}/roles/{role_name}")
# async def assign_role_to_user(
#     user_id: int,
#     role_name: str,
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     """Assign role to user."""
#     # Check permission
#     if not current_user.has_permission("users.update"):
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Insufficient permissions"
#         )
#
#     user_service = UserService(db)
#
#     success = await user_service.assign_role_to_user(user_id, role_name)
#     if not success:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Failed to assign role"
#         )
#
#     # Activity logging not implemented yet
#
#     return {"message": f"Role '{role_name}' assigned successfully}


# @router.delete(/{user_id}/roles/{role_name})
# async def remove_role_from_user(
#     user_id: int,
#     role_name: str,
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     Remove role from user.""
#     # Check permission
#     if not current_user.has_permission("users.update"):
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Insufficient permissions"
#         )
#
#     user_service = UserService(db)
#
#     try:
#         success = await user_service.remove_role_from_user(user_id, role_name)
#         if not success:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Failed to remove role"
#             )
#
#         # Activity logging not implemented yet
#
#         return {"message": f"Role '{role_name}' removed successfully}
#     except ValueError as e:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=str(e)
#         )


# Activity logging endpoint removed - activity models not implemented yet


@router.get("/statistics/overview", response_model=UserStatistics)
async def get_user_statistics(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Get user statistics.
    """
    # Check permission
    if not current_user.has_permission("users.read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
        )

    user_service = UserService(db)
    stats = await user_service.get_user_statistics()

    return UserStatistics(**stats)


@router.post("/bulk", response_model=List[UserResponse])
async def create_users_bulk(
    bulk_data: BulkUserCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create multiple users at once."""
    # Check permission
    if not current_user.has_permission("users.create"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
        )

    user_service = UserService(db)
    created_users = []

    for user_data in bulk_data.users:
        try:
            user = await user_service.create_user(user_data)
            created_users.append(user)
        except ValueError as e:
            logger.error(f"Failed to create user {user_data.username}: {e}")
            continue

    # Activity logging not implemented yet

    return [to_model(UserResponse, user) for user in created_users]


# Bulk role assignment endpoint temporarily disabled - BulkRoleAssignment
# schema not available


@router.get("/utils/generate-password")
async def generate_random_password(
    length: int = Query(12, ge=8, le=32, description="Password length (8-32 characters)"),
    include_symbols: bool = Query(True, description="Include special symbols"),
    current_user: User = Depends(get_current_user),
):
    """Generate a random password for user creation."""
    # Check if user has permission to create users
    if not current_user.has_permission("users.create"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
        )

    # Define character sets
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits
    symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?" if include_symbols else ""

    # Ensure at least one character from each required set
    password_chars = [
        secrets.choice(lowercase),
        secrets.choice(uppercase),
        secrets.choice(digits),
    ]

    if include_symbols:
        password_chars.append(secrets.choice(symbols))

    # Fill the rest with random characters
    all_chars = lowercase + uppercase + digits + symbols
    for _ in range(length - len(password_chars)):
        password_chars.append(secrets.choice(all_chars))

    # Shuffle the password characters
    secrets.SystemRandom().shuffle(password_chars)

    password = "".join(password_chars)

    return {
        "password": password,
        "length": len(password),
        "includes_symbols": include_symbols,
        "strength": "strong" if length >= 12 and include_symbols else "medium",
    }
