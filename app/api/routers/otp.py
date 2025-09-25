"""
OTP (One-Time Password) API endpoints for phone authentication.
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.db.models import User
from app.schemas.otp_schemas import (
    OTPRequest,
    OTPResponse,
    OTPStatsResponse,
    OTPVerify,
    OTPVerifyResponse,
    PhoneLoginRequest,
    PhoneLoginResponse,
    PhoneLoginVerifyRequest,
)
from app.services.jwt_service import jwt_service
from app.services.otp_service import OTPService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/request", response_model=OTPResponse)
async def request_otp(
    request: OTPRequest,
    http_request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    """
    Request OTP code for phone authentication.

    This endpoint generates and sends an OTP code to the specified phone number.
    Rate limiting is applied to prevent abuse.
    """
    try:
        otp_service = OTPService(db)

        # Get client IP for additional rate limiting
        client_ip = http_request.client.host if http_request.client else "unknown"

        # Check IP-based rate limiting
        is_allowed, message = otp_service.check_rate_limit(client_ip, "ip", "otp_request")
        if not is_allowed:
            logger.warning(f"IP rate limited: {client_ip}")
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=message)

        # Request OTP
        result = await otp_service.request_otp(
            phone_number=request.phone_number,
            code_type=request.code_type,
            user_id=current_user.id if current_user else None,
        )

        if result["success"]:
            return OTPResponse(
                success=True,
                message=result["message"],
                expires_in=result.get("expires_in"),
                resend=result.get("resend", False),
            )
        else:
            # Handle specific error codes
            if result.get("code") == "RATE_LIMITED":
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=result["message"]
                )
            elif result.get("code") == "SMS_FAILED":
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=result["message"]
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=result["message"]
                )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error requesting OTP: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error"
        )


@router.post("/verify", response_model=OTPVerifyResponse)
async def verify_otp(request: OTPVerify, http_request: Request, db: Session = Depends(get_db)):
    """
    Verify OTP code for phone authentication.

    This endpoint verifies the OTP code and returns success/failure status.
    """
    try:
        otp_service = OTPService(db)

        # Get client IP for additional rate limiting
        client_ip = http_request.client.host if http_request.client else "unknown"

        # Check IP-based rate limiting
        is_allowed, message = otp_service.check_rate_limit(client_ip, "ip", "otp_verify")
        if not is_allowed:
            logger.warning(f"IP rate limited for verification: {client_ip}")
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=message)

        # Verify OTP
        result = await otp_service.verify_otp(
            phone_number=request.phone_number, code=request.code, code_type=request.code_type
        )

        if result["success"]:
            return OTPVerifyResponse(
                success=True, message=result["message"], user_id=result.get("user_id")
            )
        else:
            # Handle specific error codes
            if result.get("code") == "RATE_LIMITED":
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=result["message"]
                )
            elif result.get("code") == "NO_OTP":
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result["message"])
            elif result.get("code") == "OTP_EXHAUSTED":
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=result["message"]
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=result["message"]
                )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying OTP: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error"
        )


@router.post("/phone/login/request", response_model=OTPResponse)
async def request_phone_login(
    request: PhoneLoginRequest, http_request: Request, db: Session = Depends(get_db)
):
    """
    Request OTP for phone-based login.

    This endpoint initiates the phone login process by sending an OTP code.
    """
    try:
        otp_service = OTPService(db)

        # Get client IP for rate limiting
        client_ip = http_request.client.host if http_request.client else "unknown"

        # Check IP-based rate limiting
        is_allowed, message = otp_service.check_rate_limit(client_ip, "ip", "otp_request")
        if not is_allowed:
            logger.warning(f"IP rate limited for phone login: {client_ip}")
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=message)

        # Request OTP for login
        result = await otp_service.request_otp(phone_number=request.phone_number, code_type="login")

        if result["success"]:
            return OTPResponse(
                success=True,
                message=result["message"],
                expires_in=result.get("expires_in"),
                resend=result.get("resend", False),
            )
        else:
            # Handle specific error codes
            if result.get("code") == "RATE_LIMITED":
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=result["message"]
                )
            elif result.get("code") == "SMS_FAILED":
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=result["message"]
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=result["message"]
                )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error requesting phone login OTP: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error"
        )


@router.post("/phone/login/verify", response_model=PhoneLoginResponse)
async def verify_phone_login(
    request: PhoneLoginVerifyRequest, http_request: Request, db: Session = Depends(get_db)
):
    """
    Verify OTP and complete phone-based login.

    This endpoint verifies the OTP code and returns a JWT token if successful.
    """
    try:
        otp_service = OTPService(db)

        # Get client IP for rate limiting
        client_ip = http_request.client.host if http_request.client else "unknown"

        # Check IP-based rate limiting
        is_allowed, message = otp_service.check_rate_limit(client_ip, "ip", "login_attempt")
        if not is_allowed:
            logger.warning(f"IP rate limited for phone login verification: {client_ip}")
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=message)

        # Verify OTP
        result = await otp_service.verify_otp(
            phone_number=request.phone_number, code=request.otp_code, code_type="login"
        )

        if not result["success"]:
            # Handle specific error codes
            if result.get("code") == "RATE_LIMITED":
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=result["message"]
                )
            elif result.get("code") == "NO_OTP":
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result["message"])
            elif result.get("code") == "OTP_EXHAUSTED":
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=result["message"]
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=result["message"]
                )

        # OTP verified successfully
        user_id = result.get("user_id")

        if user_id:
            # Existing user - get user details
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

            # Check if user is active
            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Account is deactivated"
                )

            # Check if account is locked
            if user.is_locked():
                raise HTTPException(
                    status_code=status.HTTP_423_LOCKED, detail="Account is temporarily locked"
                )

            # Update last login
            from datetime import datetime

            user.last_login = datetime.utcnow()
            user.reset_login_attempts()
            db.commit()

            # Create JWT token
            access_token = jwt_service.create_access_token(
                {
                    "sub": str(user.id),
                    "user_id": user.id,
                    "username": user.username,
                    "role": user.role,
                }
            )

            # Return user data (without sensitive information)
            user_data = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "phone": user.phone,
                "role": user.role,
                "is_active": user.is_active,
                "is_verified": user.is_verified,
                "last_login": user.last_login.isoformat() if user.last_login else None,
                "created_at": user.created_at.isoformat(),
                "updated_at": user.updated_at.isoformat(),
            }

            logger.info(f"Phone login successful for user {user.username} ({user.id})")

            return PhoneLoginResponse(
                success=True,
                message="Login successful",
                access_token=access_token,
                expires_in=30 * 60,  # 30 minutes
                user=user_data,
            )
        else:
            # New user - create account
            # For now, we'll require users to have an existing account
            # In the future, this could create a new user account
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No account found for this phone number. Please contact support.",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying phone login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error"
        )


@router.get("/stats/{phone_number}", response_model=OTPStatsResponse)
async def get_otp_stats(
    phone_number: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """
    Get OTP statistics for a phone number.

    This endpoint requires authentication and returns statistics about OTP usage.
    """
    try:
        # Only allow users to check their own phone or admins to check any phone
        if current_user.phone != phone_number and not current_user.has_role("admin"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

        otp_service = OTPService(db)
        stats = otp_service.get_otp_stats(phone_number)

        return OTPStatsResponse(**stats)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting OTP stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error"
        )
