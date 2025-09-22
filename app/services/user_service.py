"""User management service with authentication and authorization."""

import logging
import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from app.db.models import User
from app.schemas.user_schemas import UserCreate, UserUpdate

logger = logging.getLogger(__name__)


class UserService:
    """Service for user management operations."""

    def __init__(self, db: Session):
        self.db = db

    # User CRUD Operations
    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user."""
        # Check if username or email already exists
        existing_user = (
            self.db.query(User)
            .filter(or_(User.username == user_data.username, User.email == user_data.email))
            .first()
        )

        if existing_user:
            # type: ignore[comparison-overlap]
            if existing_user.username == user_data.username:
                raise ValueError("Username already exists")
            # type: ignore[comparison-overlap]
            if existing_user.email == user_data.email:
                raise ValueError("Email already exists")

        # Create user
        user = User(
            username=user_data.username,
            email=user_data.email,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            phone=user_data.phone,
            timezone=user_data.timezone,
            language=user_data.language,
            preferences=user_data.preferences or {},
        )

        # Set password
        user.set_password(user_data.password)

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        # Role is set directly in the User model

        logger.info(f"User created: {user.username} (ID: {user.id})")
        return user

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return self.db.query(User).filter(User.id == user_id).first()

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        return self.db.query(User).filter(User.username == username).first()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self.db.query(User).filter(User.email == email).first()

    async def get_users(
        self, skip: int = 0, limit: int = 100, search: Optional[str] = None
    ) -> List[User]:
        """Get users with pagination and search."""
        query = self.db.query(User)

        if search:
            search_filter = or_(
                User.username.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
                User.first_name.ilike(f"%{search}%"),
                User.last_name.ilike(f"%{search}%"),
            )
            query = query.filter(search_filter)

        return query.offset(skip).limit(limit).all()

    async def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Update user information."""
        user = await self.get_user_by_id(user_id)
        if not user:
            return None

        # Update fields
        if user_data.username is not None:
            # Check if username is already taken by another user
            existing_user = (
                self.db.query(User)
                .filter(and_(User.username == user_data.username, User.id != user_id))
                .first()
            )
            if existing_user:
                raise ValueError("Username already exists")
            user.username = user_data.username  # type: ignore[assignment]

        if user_data.email is not None:
            # Check if email is already taken by another user
            existing_user = (
                self.db.query(User)
                .filter(and_(User.email == user_data.email, User.id != user_id))
                .first()
            )
            if existing_user:
                raise ValueError("Email already exists")
            user.email = user_data.email  # type: ignore[assignment]

        if user_data.first_name is not None:
            user.first_name = user_data.first_name  # type: ignore[assignment]

        if user_data.last_name is not None:
            user.last_name = user_data.last_name  # type: ignore[assignment]

        if user_data.phone is not None:
            user.phone = user_data.phone  # type: ignore[assignment]

        if user_data.is_active is not None:
            user.is_active = user_data.is_active  # type: ignore[assignment]

        if user_data.timezone is not None:
            user.timezone = user_data.timezone  # type: ignore[assignment]

        if user_data.language is not None:
            user.language = user_data.language  # type: ignore[assignment]

        if user_data.preferences is not None:
            # type: ignore[assignment]
            user.preferences = user_data.preferences

        user.updated_at = func.now()  # type: ignore[assignment]

        self.db.commit()
        self.db.refresh(user)

        logger.info(f"User updated: {user.username} (ID: {user.id})")
        return user

    async def delete_user(self, user_id: int) -> bool:
        """Delete user (soft delete by deactivating)."""
        user = await self.get_user_by_id(user_id)
        if not user:
            return False

        # Don't allow deletion of system users
        if user.has_role("super_admin"):
            raise ValueError("Cannot delete super admin user")

        user.is_active = False  # type: ignore[assignment]
        user.updated_at = func.now()  # type: ignore[assignment]

        self.db.commit()

        logger.info(f"User deactivated: {user.username} (ID: {user.id})")
        return True

    async def change_password(self, user_id: int, current_password: str, new_password: str) -> bool:
        """Change user password."""
        user = await self.get_user_by_id(user_id)
        if not user:
            return False

        if not user.check_password(current_password):
            raise ValueError("Current password is incorrect")

        user.set_password(new_password)
        user.updated_at = func.now()  # type: ignore[assignment]

        self.db.commit()

        logger.info(f"Password changed for user: {user.username} (ID: {user.id})")
        return True

    # Authentication Operations
    async def authenticate_user(
        self,
        username_or_email: str,
        password: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Optional[User]:
        """Authenticate user with username/email and password."""
        # Find user by username or email
        user = (
            self.db.query(User)
            .filter(or_(User.username == username_or_email, User.email == username_or_email))
            .first()
        )

        if not user:
            logger.warning(f"Authentication failed: User not found - {username_or_email}")
            return None

        # Check if account is locked
        if user.is_locked():
            logger.warning(f"Authentication failed: Account locked - {user.username}")
            return None

        # Check if account is active
        if not user.is_active:  # type: ignore[comparison-overlap]
            logger.warning(f"Authentication failed: Account inactive - {user.username}")
            return None

        # Verify password
        if not user.check_password(password):
            user.increment_login_attempts()
            self.db.commit()
            logger.warning(f"Authentication failed: Invalid password - {user.username}")
            return None

        # Reset login attempts on successful login
        user.reset_login_attempts()
        user.last_login = func.now()  # type: ignore[assignment]
        self.db.commit()

        logger.info(f"User authenticated successfully: {user.username}")
        return user

    async def create_session(
        self,
        user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        expires_hours: int = 24,
    ):
        """Create a new user session with basic tracking."""
        # Generate session token
        session_token = secrets.token_urlsafe(32)

        # Create session data (could be stored in database or cache)
        session_data = {
            "session_token": session_token,
            "user_id": user.id,
            "username": user.username,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "created_at": func.now(),
            "expires_at": func.now() + timedelta(hours=expires_hours),
            "is_active": True,
        }

        # In a real implementation, you would store this in a UserSession table
        # For now, we'll log it and return the token
        logger.info(f"Session created for user: {user.username} (IP: {ip_address})")

        # Update user's last login
        user.last_login = func.now()  # type: ignore[assignment]
        self.db.commit()

        return session_data

    # Note: Session and activity logging methods removed - models not
    # implemented yet

    # Utility Methods
    async def get_user_statistics(self) -> Dict[str, Any]:
        """Get user statistics."""
        total_users = self.db.query(User).count()
        active_users = self.db.query(User).filter(User.is_active).count()
        verified_users = self.db.query(User).filter(User.is_verified).count()

        # Users by role (simplified)
        role_stats = (
            self.db.query(User.role, func.count(User.id).label("user_count"))
            .group_by(User.role)
            .all()
        )

        # Recent activity
        recent_logins = (
            self.db.query(User)
            .filter(User.last_login >= datetime.utcnow() - timedelta(days=7))
            .count()
        )

        return {
            "total_users": total_users,
            "active_users": active_users,
            "verified_users": verified_users,
            "recent_logins": recent_logins,
            "role_distribution": {role.role: role.user_count for role in role_stats},
        }

    # Note: Session cleanup method removed - session models not implemented yet
