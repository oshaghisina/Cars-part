"""
Telegram SSO models for bot integration and account linking.
"""

import secrets
from datetime import datetime, timedelta

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base

# Import User model for relationships
try:
    from app.db.models import User
except ImportError:
    # Fallback for when User model is not available
    User = None


class TelegramUser(Base):
    """Telegram user information linked to platform accounts."""

    __tablename__ = "telegram_users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, nullable=False, unique=True, index=True)
    username = Column(String(255), nullable=True, index=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    language_code = Column(String(10), nullable=True)
    is_bot = Column(Boolean, default=False, nullable=False)
    is_premium = Column(Boolean, default=False, nullable=False)

    # Account linking
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    is_linked = Column(Boolean, default=False, nullable=False)
    linked_at = Column(DateTime, nullable=True)

    # Metadata
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    last_activity = Column(DateTime, nullable=True)

    # Relationships
    # user = relationship("User", back_populates="telegram_user")
    link_tokens = relationship(
        "TelegramLinkToken", back_populates="telegram_user", cascade="all, delete-orphan"
    )

    # Indexes
    __table_args__ = (
        Index("idx_telegram_username", "username"),
        Index("idx_telegram_linked", "is_linked"),
    )

    def is_active(self) -> bool:
        """Check if Telegram user is active (linked and recent activity)."""
        if not self.is_linked:
            return False
        if not self.last_activity:
            return False
        return datetime.utcnow() - self.last_activity < timedelta(days=30)

    def update_activity(self):
        """Update last activity timestamp."""
        self.last_activity = func.now()
        self.updated_at = func.now()


class TelegramLinkToken(Base):
    """Secure tokens for linking Telegram accounts to platform accounts."""

    __tablename__ = "telegram_link_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(255), nullable=False, unique=True, index=True)
    token_hash = Column(String(255), nullable=False, index=True)

    # Token metadata
    telegram_user_id = Column(Integer, ForeignKey("telegram_users.id"), nullable=False, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id"), nullable=True, index=True
    )  # For existing users

    # Token lifecycle
    expires_at = Column(DateTime, nullable=False, index=True)
    is_used = Column(Boolean, default=False, nullable=False)
    used_at = Column(DateTime, nullable=True)

    # Security
    nonce = Column(String(64), nullable=False)  # Replay protection
    ip_address = Column(String(45), nullable=True)  # IP tracking
    user_agent = Column(Text, nullable=True)  # User agent tracking

    # Token type and purpose
    token_type = Column(String(20), nullable=False, default="link")  # link, login, verify
    action = Column(
        String(50), nullable=False, default="link_account"
    )  # link_account, login, verify_phone

    # Metadata
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # Relationships
    telegram_user = relationship("TelegramUser", back_populates="link_tokens")
    # user = relationship("User")

    # Indexes
    __table_args__ = (
        Index("idx_link_token_expires", "expires_at"),
        Index("idx_link_token_type", "token_type"),
        Index("idx_link_token_used", "is_used"),
    )

    def is_expired(self) -> bool:
        """Check if token is expired."""
        return datetime.utcnow() > self.expires_at

    def can_use(self) -> bool:
        """Check if token can be used."""
        return not self.is_used and not self.is_expired()

    def mark_used(self):
        """Mark token as used."""
        self.is_used = True
        self.used_at = func.now()
        self.updated_at = func.now()

    @staticmethod
    def generate_token() -> str:
        """Generate a secure random token."""
        return secrets.token_urlsafe(32)

    @staticmethod
    def generate_nonce() -> str:
        """Generate a cryptographic nonce."""
        return secrets.token_hex(32)


class TelegramBotSession(Base):
    """Bot session data for maintaining conversation state."""

    __tablename__ = "telegram_bot_sessions"

    id = Column(Integer, primary_key=True, index=True)
    telegram_user_id = Column(Integer, ForeignKey("telegram_users.id"), nullable=False, index=True)
    session_id = Column(String(255), nullable=False, index=True)

    # Session state
    state = Column(String(50), nullable=False, default="idle")  # idle, linking, login, etc.
    context = Column(Text, nullable=True)  # JSON context data

    # Session lifecycle
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    expires_at = Column(DateTime, nullable=False, index=True)

    # Relationships
    telegram_user = relationship("TelegramUser")

    # Indexes
    __table_args__ = (
        Index("idx_bot_session_user", "telegram_user_id"),
        Index("idx_bot_session_state", "state"),
        Index("idx_bot_session_expires", "expires_at"),
        UniqueConstraint("telegram_user_id", "session_id", name="uq_telegram_user_session"),
    )

    def is_expired(self) -> bool:
        """Check if session is expired."""
        return datetime.utcnow() > self.expires_at

    def extend_session(self, hours: int = 24):
        """Extend session expiry."""
        self.expires_at = datetime.utcnow() + timedelta(hours=hours)
        self.updated_at = func.now()

    def update_state(self, new_state: str, context: dict = None):
        """Update session state and context."""
        self.state = new_state
        if context:
            import json

            self.context = json.dumps(context)
        self.updated_at = func.now()


class TelegramDeepLink(Base):
    """Deep link tracking for Telegram bot to web transitions."""

    __tablename__ = "telegram_deep_links"

    id = Column(Integer, primary_key=True, index=True)
    link_id = Column(String(255), nullable=False, unique=True, index=True)
    telegram_user_id = Column(Integer, ForeignKey("telegram_users.id"), nullable=False, index=True)

    # Link metadata
    action = Column(String(50), nullable=False)  # login, link_account, verify
    target_url = Column(Text, nullable=False)  # Where to redirect after action
    parameters = Column(Text, nullable=True)  # JSON parameters

    # Security
    nonce = Column(String(64), nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)

    # Link lifecycle
    expires_at = Column(DateTime, nullable=False, index=True)
    is_used = Column(Boolean, default=False, nullable=False)
    used_at = Column(DateTime, nullable=True)

    # Metadata
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # Relationships
    telegram_user = relationship("TelegramUser")

    # Indexes
    __table_args__ = (
        Index("idx_deep_link_expires", "expires_at"),
        Index("idx_deep_link_used", "is_used"),
        Index("idx_deep_link_action", "action"),
    )

    def is_expired(self) -> bool:
        """Check if deep link is expired."""
        return datetime.utcnow() > self.expires_at

    def can_use(self) -> bool:
        """Check if deep link can be used."""
        return not self.is_used and not self.is_expired()

    def mark_used(self):
        """Mark deep link as used."""
        self.is_used = True
        self.used_at = func.now()
        self.updated_at = func.now()

    @staticmethod
    def generate_link_id() -> str:
        """Generate a secure link ID."""
        return secrets.token_urlsafe(24)
