"""
OTP (One-Time Password) models for phone authentication.
"""

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
)
from sqlalchemy.sql import func

from app.db.database import Base


class OTPCode(Base):
    """OTP codes table for phone authentication."""

    __tablename__ = "otp_codes"

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(20), nullable=False, index=True)
    code_hash = Column(String(255), nullable=False)  # Hashed OTP code
    code_type = Column(String(20), nullable=False, default="login")  # login, verify, reset
    expires_at = Column(DateTime, nullable=False, index=True)
    attempts = Column(Integer, default=0, nullable=False)
    max_attempts = Column(Integer, default=5, nullable=False)
    is_used = Column(Boolean, default=False, nullable=False)
    used_at = Column(DateTime, nullable=True)

    # Optional user association (for existing users)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    # Metadata
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # SMS delivery tracking
    sms_sent = Column(Boolean, default=False, nullable=False)
    sms_sent_at = Column(DateTime, nullable=True)
    sms_provider = Column(String(50), nullable=True)
    sms_provider_id = Column(String(100), nullable=True)
    sms_error = Column(Text, nullable=True)

    # Relationships
    # user = relationship("User", back_populates="otp_codes")

    # Indexes for performance
    __table_args__ = (
        Index("idx_otp_phone_expires", "phone_number", "expires_at"),
        Index("idx_otp_user_type", "user_id", "code_type"),
    )

    def is_expired(self) -> bool:
        """Check if OTP code is expired."""
        return datetime.utcnow() > self.expires_at

    def is_exhausted(self) -> bool:
        """Check if OTP code has exceeded max attempts."""
        return self.attempts >= self.max_attempts

    def can_use(self) -> bool:
        """Check if OTP code can be used."""
        return not self.is_used and not self.is_expired() and not self.is_exhausted()

    def increment_attempts(self):
        """Increment attempt counter."""
        self.attempts += 1
        self.updated_at = func.now()

    def mark_used(self):
        """Mark OTP as used."""
        self.is_used = True
        self.used_at = func.now()
        self.updated_at = func.now()


class PhoneVerification(Base):
    """Phone verification tracking for users."""

    __tablename__ = "phone_verifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    phone_number = Column(String(20), nullable=False, index=True)
    verification_status = Column(
        String(20), nullable=False, default="pending"
    )  # pending, verified, failed
    verified_at = Column(DateTime, nullable=True)
    verification_method = Column(String(20), nullable=False, default="sms")  # sms, call

    # Metadata
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # Relationships
    # user = relationship("User", back_populates="phone_verifications")

    def is_verified(self) -> bool:
        """Check if phone is verified."""
        return self.verification_status == "verified"

    def mark_verified(self):
        """Mark phone as verified."""
        self.verification_status = "verified"
        self.verified_at = func.now()
        self.updated_at = func.now()


class RateLimit(Base):
    """Rate limiting tracking for OTP requests."""

    __tablename__ = "rate_limits"

    id = Column(Integer, primary_key=True, index=True)
    identifier = Column(String(100), nullable=False, index=True)  # phone, IP, user_id
    identifier_type = Column(String(20), nullable=False, index=True)  # phone, ip, user
    action = Column(
        String(50), nullable=False, index=True
    )  # otp_request, otp_verify, login_attempt
    count = Column(Integer, default=1, nullable=False)
    window_start = Column(DateTime, nullable=False, default=func.now(), index=True)
    window_duration = Column(Integer, nullable=False, default=900)  # 15 minutes in seconds

    # Metadata
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # Indexes for performance
    __table_args__ = (
        Index("idx_rate_limit_lookup", "identifier", "identifier_type", "action", "window_start"),
    )

    def is_expired(self) -> bool:
        """Check if rate limit window is expired."""
        return datetime.utcnow() > (self.window_start + timedelta(seconds=self.window_duration))

    def increment_count(self):
        """Increment the count."""
        self.count += 1
        self.updated_at = func.now()

    def reset_window(self):
        """Reset the rate limit window."""
        self.count = 1
        self.window_start = func.now()
        self.updated_at = func.now()
