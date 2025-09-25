"""
OTP (One-Time Password) service for phone authentication.
"""

import hashlib
import logging
import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.otp_models import OTPCode, RateLimit
from app.services.sms_service import SMSService

logger = logging.getLogger(__name__)


class OTPService:
    """Service for managing OTP codes and phone authentication."""

    def __init__(self, db: Session):
        self.db = db
        self.code_length = 6
        self.code_expiry_minutes = 5
        self.max_attempts = 5

        # Rate limiting configuration
        self.rate_limits = {
            "otp_request": {"count": 5, "window_minutes": 30},  # 5 requests per 30 minutes
            "otp_verify": {"count": 10, "window_minutes": 15},  # 10 verifications per 15 minutes
            "login_attempt": {
                "count": 10,
                "window_minutes": 15,
            },  # 10 login attempts per 15 minutes
        }

    def generate_otp_code(self) -> str:
        """Generate a random OTP code."""
        return str(secrets.randbelow(10**self.code_length)).zfill(self.code_length)

    def hash_otp_code(self, code: str) -> str:
        """Hash OTP code for secure storage."""
        salt = secrets.token_hex(16)
        hash_value = hashlib.pbkdf2_hmac(
            "sha256", code.encode("utf-8"), salt.encode("utf-8"), 100000
        ).hex()
        return f"{salt}:{hash_value}"

    def verify_otp_code(self, code: str, hashed_code: str) -> bool:
        """Verify OTP code against hash."""
        try:
            salt, stored_hash = hashed_code.split(":", 1)
            computed_hash = hashlib.pbkdf2_hmac(
                "sha256", code.encode("utf-8"), salt.encode("utf-8"), 100000
            ).hex()
            return computed_hash == stored_hash
        except (ValueError, AttributeError):
            return False

    def check_rate_limit(
        self, identifier: str, identifier_type: str, action: str
    ) -> Tuple[bool, str]:
        """
        Check if action is rate limited.

        Returns:
            Tuple of (is_allowed, message)
        """
        if action not in self.rate_limits:
            return True, "Rate limit not configured"

        limit_config = self.rate_limits[action]
        window_duration = limit_config["window_minutes"] * 60

        # Get current rate limit record (SQLite compatible)
        cutoff_time = datetime.utcnow() - timedelta(seconds=window_duration)
        rate_limit = (
            self.db.query(RateLimit)
            .filter(
                and_(
                    RateLimit.identifier == identifier,
                    RateLimit.identifier_type == identifier_type,
                    RateLimit.action == action,
                    RateLimit.window_start >= cutoff_time,
                )
            )
            .first()
        )

        if not rate_limit:
            # No rate limit record, create one
            rate_limit = RateLimit(
                identifier=identifier,
                identifier_type=identifier_type,
                action=action,
                count=1,
                window_start=datetime.utcnow(),
                window_duration=window_duration,
            )
            self.db.add(rate_limit)
            self.db.commit()
            return True, "Rate limit check passed"

        if rate_limit.is_expired():
            # Window expired, reset
            rate_limit.reset_window()
            self.db.commit()
            return True, "Rate limit window reset"

        if rate_limit.count >= limit_config["count"]:
            return (
                False,
                f"Rate limit exceeded. Max {limit_config['count']} {action} "
                f"per {limit_config['window_minutes']} minutes",
            )

        # Increment count
        rate_limit.increment_count()
        self.db.commit()
        return True, "Rate limit check passed"

    async def request_otp(
        self, phone_number: str, code_type: str = "login", user_id: Optional[int] = None
    ) -> Dict:
        """
        Request OTP code for phone number.

        Args:
            phone_number: Phone number in E.164 format
            code_type: Type of OTP (login, verify, reset)
            user_id: Optional user ID for existing users

        Returns:
            Dictionary with result status and message
        """
        try:
            # Check rate limits
            is_allowed, message = self.check_rate_limit(phone_number, "phone", "otp_request")
            if not is_allowed:
                logger.warning(f"OTP request rate limited for {phone_number}: {message}")
                return {"success": False, "message": message, "code": "RATE_LIMITED"}

            # Clean up expired OTPs for this phone
            self._cleanup_expired_otps(phone_number)

            # Check if there's an active OTP that can be reused
            active_otp = (
                self.db.query(OTPCode)
                .filter(
                    and_(
                        OTPCode.phone_number == phone_number,
                        OTPCode.code_type == code_type,
                        OTPCode.is_used.is_(False),
                        OTPCode.expires_at > func.now(),
                        OTPCode.attempts < OTPCode.max_attempts,
                    )
                )
                .first()
            )

            if active_otp:
                # Resend existing OTP
                otp_code = self.generate_otp_code()
                active_otp.code_hash = self.hash_otp_code(otp_code)
                active_otp.updated_at = func.now()

                # Send SMS
                sms_result = await self._send_otp_sms(phone_number, otp_code, code_type)
                if sms_result["success"]:
                    self.db.commit()
                    logger.info(f"OTP resent for {phone_number}")
                    return {"success": True, "message": "OTP code sent", "resend": True}
                else:
                    return {
                        "success": False,
                        "message": f"SMS sending failed: {sms_result['message']}",
                        "code": "SMS_FAILED",
                    }

            # Generate new OTP
            otp_code = self.generate_otp_code()
            hashed_code = self.hash_otp_code(otp_code)

            # Create OTP record (SQLite compatible)
            expires_at = datetime.utcnow() + timedelta(minutes=self.code_expiry_minutes)
            otp_record = OTPCode(
                phone_number=phone_number,
                code_hash=hashed_code,
                code_type=code_type,
                expires_at=expires_at,
                user_id=user_id,
            )

            self.db.add(otp_record)
            self.db.flush()  # Get the ID

            # Send SMS
            sms_result = await self._send_otp_sms(phone_number, otp_code, code_type)

            if sms_result["success"]:
                otp_record.sms_sent = True
                otp_record.sms_sent_at = func.now()
                otp_record.sms_provider = sms_result.get("provider")
                otp_record.sms_provider_id = sms_result.get("provider_id")
                self.db.commit()

                logger.info(f"OTP sent successfully to {phone_number}")
                return {
                    "success": True,
                    "message": "OTP code sent",
                    "expires_in": self.code_expiry_minutes * 60,
                }
            else:
                # In development mode, if SMS fails, log the code and mark as sent
                if settings.app_env == "development":
                    logger.warning(
                        f"SMS failed for {phone_number}, but in development mode - "
                        f"logging OTP: {otp_code}"
                    )
                    otp_record.sms_sent = True
                    otp_record.sms_sent_at = func.now()
                    otp_record.sms_provider = "development"
                    otp_record.sms_error = f"Development mode: {sms_result.get('message')}"
                    self.db.commit()

                    return {
                        "success": True,
                        "message": f"OTP code generated (dev mode): {otp_code}",
                        "expires_in": self.code_expiry_minutes * 60,
                    }
                else:
                    otp_record.sms_error = sms_result.get("message")
                    self.db.commit()

                    logger.error(f"Failed to send OTP to {phone_number}: {sms_result['message']}")
                    return {
                        "success": False,
                        "message": f"SMS sending failed: {sms_result['message']}",
                        "code": "SMS_FAILED",
                    }

        except Exception as e:
            logger.error(f"Error requesting OTP for {phone_number}: {e}", exc_info=True)
            try:
                self.db.rollback()
            except Exception as rollback_error:
                logger.error(f"Error during rollback: {rollback_error}")
            return {
                "success": False,
                "message": f"Failed to send OTP: {str(e)}",
                "code": "INTERNAL_ERROR",
            }

    async def verify_otp(self, phone_number: str, code: str, code_type: str = "login") -> Dict:
        """
        Verify OTP code for phone number.

        Args:
            phone_number: Phone number in E.164 format
            code: OTP code to verify
            code_type: Type of OTP (login, verify, reset)

        Returns:
            Dictionary with verification result
        """
        try:
            # Check rate limits
            is_allowed, message = self.check_rate_limit(phone_number, "phone", "otp_verify")
            if not is_allowed:
                logger.warning(f"OTP verification rate limited for {phone_number}: {message}")
                return {"success": False, "message": message, "code": "RATE_LIMITED"}

            # Find active OTP record
            otp_record = (
                self.db.query(OTPCode)
                .filter(
                    and_(
                        OTPCode.phone_number == phone_number,
                        OTPCode.code_type == code_type,
                        OTPCode.is_used.is_(False),
                        OTPCode.expires_at > func.now(),
                    )
                )
                .order_by(OTPCode.created_at.desc())
                .first()
            )

            if not otp_record:
                logger.warning(f"No active OTP found for {phone_number}")
                return {"success": False, "message": "No active OTP code found", "code": "NO_OTP"}

            if otp_record.is_exhausted():
                logger.warning(f"OTP exhausted for {phone_number}")
                return {
                    "success": False,
                    "message": "OTP code has exceeded maximum attempts",
                    "code": "OTP_EXHAUSTED",
                }

            # Increment attempts
            otp_record.increment_attempts()

            # Verify code
            if self.verify_otp_code(code, otp_record.code_hash):
                # Success
                otp_record.mark_used()
                self.db.commit()

                logger.info(f"OTP verified successfully for {phone_number}")
                return {
                    "success": True,
                    "message": "OTP verified successfully",
                    "user_id": otp_record.user_id,
                }
            else:
                # Failed verification
                self.db.commit()

                if otp_record.is_exhausted():
                    logger.warning(f"OTP verification failed and exhausted for {phone_number}")
                    return {
                        "success": False,
                        "message": "OTP code has exceeded maximum attempts",
                        "code": "OTP_EXHAUSTED",
                    }
                else:
                    remaining_attempts = otp_record.max_attempts - otp_record.attempts
                    logger.warning(
                        f"OTP verification failed for {phone_number}, "
                        f"{remaining_attempts} attempts remaining"
                    )
                    return {
                        "success": False,
                        "message": f"Invalid OTP code. {remaining_attempts} attempts remaining",
                        "code": "INVALID_OTP",
                    }

        except Exception as e:
            logger.error(f"Error verifying OTP for {phone_number}: {e}")
            self.db.rollback()
            return {"success": False, "message": "Internal server error", "code": "INTERNAL_ERROR"}

    async def _send_otp_sms(self, phone_number: str, code: str, code_type: str) -> Dict:
        """Send OTP code via SMS."""
        try:
            # Create SMS message based on code type
            if code_type == "login":
                message = (
                    f"Your login code is: {code}. Valid for 5 minutes. Do not share this code."
                )
            elif code_type == "verify":
                message = (
                    f"Your verification code is: {code}. "
                    f"Valid for 5 minutes. Do not share this code."
                )
            elif code_type == "reset":
                message = (
                    f"Your password reset code is: {code}. "
                    f"Valid for 5 minutes. Do not share this code."
                )
            else:
                message = f"Your code is: {code}. " f"Valid for 5 minutes. Do not share this code."

            # Create SMS service instance
            sms_service = SMSService(self.db)

            # Send SMS
            result = await sms_service.send_sms(phone_number, message)

            if result.success:
                return {
                    "success": True,
                    "provider": "melipayamak",
                    "provider_id": result.message_id,
                }
            else:
                return {"success": False, "message": result.message or "SMS sending failed"}

        except Exception as e:
            logger.error(f"Error sending OTP SMS to {phone_number}: {e}")
            return {"success": False, "message": str(e)}

    def _cleanup_expired_otps(self, phone_number: str):
        """Clean up expired OTP records for a phone number."""
        try:
            expired_otps = (
                self.db.query(OTPCode)
                .filter(and_(OTPCode.phone_number == phone_number, OTPCode.expires_at < func.now()))
                .all()
            )

            for otp in expired_otps:
                self.db.delete(otp)

            if expired_otps:
                self.db.commit()
                logger.info(f"Cleaned up {len(expired_otps)} expired OTPs for {phone_number}")

        except Exception as e:
            logger.error(f"Error cleaning up expired OTPs for {phone_number}: {e}")
            # Don't let cleanup errors break the main flow
            try:
                self.db.rollback()
            except Exception:
                pass

    def get_otp_stats(self, phone_number: str) -> Dict:
        """Get OTP statistics for a phone number."""
        try:
            # Count active OTPs
            active_count = (
                self.db.query(OTPCode)
                .filter(
                    and_(
                        OTPCode.phone_number == phone_number,
                        OTPCode.is_used.is_(False),
                        OTPCode.expires_at > func.now(),
                    )
                )
                .count()
            )

            # Count total OTPs in last 24 hours (SQLite compatible)
            cutoff_24h = datetime.utcnow() - timedelta(hours=24)
            total_24h = (
                self.db.query(OTPCode)
                .filter(
                    and_(OTPCode.phone_number == phone_number, OTPCode.created_at >= cutoff_24h)
                )
                .count()
            )

            return {
                "active_otps": active_count,
                "total_24h": total_24h,
                "rate_limit_status": "normal",  # Could be enhanced with actual rate limit status
            }

        except Exception as e:
            logger.error(f"Error getting OTP stats for {phone_number}: {e}")
            return {"active_otps": 0, "total_24h": 0, "rate_limit_status": "error"}
