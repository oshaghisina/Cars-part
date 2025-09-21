"""Authentication and authorization core module."""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.user_service import UserService
from app.schemas.user_schemas import TokenData
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Configuration
SECRET_KEY = settings.jwt_secret_key
ALGORITHM = settings.jwt_algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.jwt_access_token_expire_minutes

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token security
security = HTTPBearer()


def create_access_token(
        data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def verify_token(token: str) -> Optional[TokenData]:
    """Verify JWT token and return token data."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        role: str = payload.get("role", "user")

        if username is None or user_id is None:
            return None

        return TokenData(
            username=username,
            user_id=user_id,
            role=role
        )
    except JWTError:
        return None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token = credentials.credentials
        token_data = verify_token(token)

        if token_data is None:
            raise credentials_exception

        user_service = UserService(db)
        user = await user_service.get_user_by_id(token_data.user_id)

        if user is None:
            raise credentials_exception

        return user

    except Exception as e:
        logger.error(f"Error getting current user: {e}"")
        raise credentials_exception


async def get_current_active_user(current_user=Depends(get_current_user)):
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


def require_permission(permission: str):
    """Decorator to require specific permission."""
    async def permission_dependency(
            current_user=Depends(get_current_active_user)):
        if not current_user.has_permission(permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {permission}""
            )
        return current_user

    return permission_dependency


def require_role(role: str):
    """Decorator to require specific role."""
    async def role_dependency(current_user=Depends(get_current_active_user)):
        if not current_user.has_role(role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required role: {role}""
            )
        return current_user

    return role_dependency


def require_admin(current_user=Depends(get_current_active_user)):
    """Require admin role."""
    if not (current_user.has_role("admin")
            or current_user.has_role("super_admin")):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def require_super_admin(current_user=Depends(get_current_active_user)):
    """Require super admin role."""
    if not current_user.has_role("super_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required"
        )
    return current_user


class PermissionChecker:
    """Permission checker class for dependency injection."""

    def __init__(self, required_permission: str):
        self.required_permission = required_permission

    def __call__(self, current_user=Depends(get_current_active_user)):
        if not current_user.has_permission(self.required_permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {self.required_permission}")
        return current_user


class RoleChecker:
    """Role checker class for dependency injection."""

    def __init__(self, required_role: str):
        self.required_role = required_role

    def __call__(self, current_user=Depends(get_current_active_user)):
        if not current_user.has_role(self.required_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required role: {self.required_role}")
        return current_user


# Common permission checkers
users_read = PermissionChecker("users.read")
users_create = PermissionChecker("users.create")
users_update = PermissionChecker("users.update")
users_delete = PermissionChecker("users.delete")

roles_read = PermissionChecker("roles.read")
roles_create = PermissionChecker("roles.create")
roles_update = PermissionChecker("roles.update")
roles_delete = PermissionChecker("roles.delete")

parts_read = PermissionChecker("parts.read")
parts_create = PermissionChecker("parts.create")
parts_update = PermissionChecker("parts.update")
parts_delete = PermissionChecker("parts.delete")

orders_read = PermissionChecker("orders.read")
orders_create = PermissionChecker("orders.create")
orders_update = PermissionChecker("orders.update")
orders_delete = PermissionChecker("orders.delete")

leads_read = PermissionChecker("leads.read")
leads_create = PermissionChecker("leads.create")
leads_update = PermissionChecker("leads.update")
leads_delete = PermissionChecker("leads.delete")

# Common role checkers
admin_required = RoleChecker("admin")
super_admin_required = RoleChecker("super_admin")


async def get_user_permissions(current_user=Depends(get_current_user)) -> list:
    """Get all permissions for current user."""
    permissions = set()

    for role in current_user.roles:
        for role_permission in role.permissions:
            permissions.add(role_permission.permission.name)

    return list(permissions)


async def get_user_roles(current_user=Depends(get_current_user)) -> list:
    """Get all roles for current user."""
    return [role.name for role in current_user.roles]


def check_resource_access(
        user_id: int,
        resource_user_id: int,
        current_user=Depends(get_current_user)) -> bool:
    """Check if user can access a resource (either owner or admin)."""
    # Users can access their own resources
    if user_id == resource_user_id:
        return True

    # Admins can access all resources
    if current_user.has_role("admin") or current_user.has_role("super_admin"):
        return True

    return False


async def validate_user_access(
    resource_user_id: int,
    current_user=Depends(get_current_user)
):
    """Validate user access to a resource."""
    if not check_resource_access(
            current_user.id,
            resource_user_id,
            current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this resource"
        )
    return current_user
