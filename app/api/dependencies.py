"""
FastAPI dependencies for authentication and authorization.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import jwt

from app.db.database import get_db
from app.db.models import User
from app.core.config import settings

# Security scheme
security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get current user from JWT token.
    Returns None if no token or invalid token (for optional authentication).
    """
    if not credentials:
        return None

    try:
        # Decode JWT token
        payload = jwt.decode(
            credentials.credentials,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )

        user_id = payload.get("sub")
        if user_id is None:
            return None

        # Get user from database
        user = db.query(User).filter(User.id == int(user_id)).first()
        if user is None:
            return None

        # Check if user is active
        if not user.is_active:
            return None

        # Check if account is locked
        if user.is_locked():
            return None

        return user

    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
    except Exception:
        return None


def get_current_active_user(
    current_user: Optional[User] = Depends(get_current_user)
) -> User:
    """
    Get current user and require authentication.
    Raises HTTPException if user is not authenticated.
    """
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user


def require_role(required_role: str):
    """
    Dependency factory to require specific user role.
    """
    def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if not current_user.has_role(required_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation requires {required_role} role"
            )
        return current_user
    return role_checker


def require_permission(required_permission: str):
    """
    Dependency factory to require specific permission.
    """
    def permission_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if not current_user.has_permission(required_permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation requires {required_permission} permission"
            )
        return current_user
    return permission_checker


# Common role dependencies
require_admin = require_role("admin")
require_manager = require_role("manager")
require_super_admin = require_role("super_admin")

# Common permission dependencies
require_parts_write = require_permission("parts.create")
require_users_write = require_permission("users.create")
require_orders_write = require_permission("orders.create")
