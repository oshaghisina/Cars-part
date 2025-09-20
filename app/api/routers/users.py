"""User management API endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.user_service import UserService
from app.schemas.user_schemas import (
    UserCreate, UserUpdate, UserResponse, UserSummary, UserLogin,
    UserStatistics, LoginResponse, UserListResponse, 
    PasswordChange, BulkUserCreate, BulkRoleAssignment
)
from app.core.auth import create_access_token, verify_token, get_current_user
from app.db.models import User
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()


@router.options("/login")
async def login_options():
    """Handle OPTIONS request for login endpoint."""
    return {"message": "OK"}


@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: UserLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    """Authenticate user and create session."""
    user_service = UserService(db)
    
    # Get client IP and user agent
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    # Authenticate user
    user = await user_service.authenticate_user(
        login_data.username_or_email,
        login_data.password,
        ip_address,
        user_agent
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username/email or password"
        )
    
    # Create session (placeholder - session management not fully implemented)
    await user_service.create_session(user, ip_address, user_agent)
    
    # Create JWT token
    access_token = create_access_token(
        data={
            "sub": user.username,
            "user_id": user.id,
            "role": user.role
        }
    )
    
    # Update last login time
    from datetime import datetime
    user.last_login = datetime.utcnow()  # type: ignore[assignment]
    db.commit()
    
    return LoginResponse(
        access_token=access_token,
        expires_in=86400,  # 24 hours
        user=UserResponse.from_orm(user)
    )


@router.post("/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Logout user and invalidate session."""
    # Verify token and get user
    token_data = verify_token(credentials.credentials)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    # For JWT, we can't invalidate the token itself
    # Session invalidation would be handled by client-side token removal
    
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information."""
    return UserResponse.from_orm(current_user)


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user information."""
    user_service = UserService(db)
    
    updated_user = await user_service.update_user(int(current_user.id), user_update)  # type: ignore[arg-type]
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Activity logging not implemented yet
    
    return UserResponse.from_orm(updated_user)


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user password."""
    user_service = UserService(db)
    
    success = await user_service.change_password(
        int(current_user.id),  # type: ignore[arg-type]
        password_data.current_password,
        password_data.new_password
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to change password"
        )
    
    # Activity logging not implemented yet
    
    return {"message": "Password changed successfully"}


@router.get("/", response_model=UserListResponse)
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get users with pagination and search."""
    # Check permission
    if not current_user.has_permission("users.read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    user_service = UserService(db)
    users = await user_service.get_users(skip, limit, search)
    
    # Get total count
    total = db.query(User).count()
    if search:
        from sqlalchemy import or_
        total = db.query(User).filter(
            or_(
                User.username.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
                User.first_name.ilike(f"%{search}%"),
                User.last_name.ilike(f"%{search}%")
            )
        ).count()
    
    return UserListResponse(
        users=[UserSummary.from_orm(user) for user in users],
        total=total,
        page=skip // limit + 1,
        limit=limit,
        total_pages=(total + limit - 1) // limit
    )


@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new user."""
    # Check permission
    if not current_user.has_permission("users.create"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    user_service = UserService(db)
    
    try:
        user = await user_service.create_user(user_data)
        
        # Activity logging not implemented yet
        
        return UserResponse.from_orm(user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user by ID."""
    # Check permission
    if not current_user.has_permission("users.read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    user_service = UserService(db)
    user = await user_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse.from_orm(user)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user information."""
    # Check permission
    if not current_user.has_permission("users.update"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    user_service = UserService(db)
    
    try:
        updated_user = await user_service.update_user(user_id, user_update)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Activity logging not implemented yet
        
        return UserResponse.from_orm(updated_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete user (soft delete)."""
    # Check permission
    if not current_user.has_permission("users.delete"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    # Don't allow users to delete themselves
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    user_service = UserService(db)
    
    try:
        success = await user_service.delete_user(user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Activity logging not implemented yet
        
        return {"message": "User deleted successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


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
#     return {"message": f"Role '{role_name}' assigned successfully"}


# @router.delete("/{user_id}/roles/{role_name}")
# async def remove_role_from_user(
#     user_id: int,
#     role_name: str,
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     """Remove role from user."""
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
#         return {"message": f"Role '{role_name}' removed successfully"}
#     except ValueError as e:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=str(e)
#         )


# Activity logging endpoint removed - activity models not implemented yet


@router.get("/statistics/overview", response_model=UserStatistics)
async def get_user_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user statistics."""
    # Check permission
    if not current_user.has_permission("users.read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    user_service = UserService(db)
    stats = await user_service.get_user_statistics()
    
    return UserStatistics(**stats)


@router.post("/bulk", response_model=List[UserResponse])
async def create_users_bulk(
    bulk_data: BulkUserCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create multiple users at once."""
    # Check permission
    if not current_user.has_permission("users.create"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
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
    
    return [UserResponse.from_orm(user) for user in created_users]


# Bulk role assignment endpoint temporarily disabled - BulkRoleAssignment schema not available
