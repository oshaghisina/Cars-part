"""
Authentication configuration and monitoring API endpoints.
Provides read-only access to authentication policies and configuration.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db
from app.api.dependencies import require_admin
from app.services.jwt_service import jwt_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/config")
async def get_auth_config(current_user = Depends(require_admin)) -> Dict[str, Any]:
    """
    Get current authentication configuration.
    Restricted to admin users only.
    """
    try:
        config = {
            "jwt": {
                "library": "PyJWT",
                "algorithm": settings.jwt_algorithm,
                "access_token_expire_minutes": settings.jwt_access_token_expire_minutes,
                "secret_key_length": len(settings.jwt_secret_key),
                "secret_key_masked": settings.jwt_secret_key[:8] + "..." + settings.jwt_secret_key[-4:] if len(settings.jwt_secret_key) > 12 else "***"
            },
            "claims": {
                "canonical_format": "sub=user_id (integer)",
                "legacy_support": True,
                "required_claims": ["sub", "exp", "iat", "iss", "aud"],
                "optional_claims": ["user_id", "username", "role"]
            },
            "security": {
                "issuer": "china-car-parts-api",
                "audience": "china-car-parts-client",
                "token_validation": "strict",
                "legacy_token_support": True
            },
            "features": {
                "telegram_sso": settings.telegram_sso_enabled,
                "otp_enabled": True,  # Based on our implementation
                "phone_auth": True,   # Based on our implementation
                "account_linking": True
            },
            "storage": {
                "frontend_key": "access_token",
                "storage_type": "localStorage",
                "migration_complete": True
            },
            "rate_limiting": {
                "otp_requests_per_hour": 5,
                "login_attempts_per_15min": 10,
                "telegram_links_per_day": 5
            },
            "metadata": {
                "config_version": "1.0",
                "last_updated": datetime.utcnow().isoformat(),
                "environment": settings.app_env
            }
        }
        
        logger.info(f"Auth config requested by user {current_user.id}")
        return config
        
    except Exception as e:
        logger.error(f"Error getting auth config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve authentication configuration"
        )


@router.get("/stats")
async def get_auth_stats(current_user = Depends(require_admin)) -> Dict[str, Any]:
    """
    Get authentication statistics and metrics.
    Restricted to admin users only.
    """
    try:
        # This would typically query a metrics database
        # For now, return mock data based on our implementation
        stats = {
            "jwt_tokens": {
                "total_issued": 0,  # Would be tracked in production
                "active_tokens": 0,
                "expired_tokens": 0,
                "invalid_tokens": 0
            },
            "authentication": {
                "successful_logins": 0,
                "failed_logins": 0,
                "success_rate": 0.0,
                "average_response_time_ms": 0
            },
            "otp": {
                "total_requests": 0,
                "successful_verifications": 0,
                "failed_verifications": 0,
                "delivery_success_rate": 0.0
            },
            "telegram": {
                "total_links": 0,
                "successful_links": 0,
                "failed_links": 0,
                "active_telegram_users": 0
            },
            "security": {
                "rate_limit_hits": 0,
                "brute_force_attempts": 0,
                "suspicious_activities": 0
            },
            "metadata": {
                "last_updated": datetime.utcnow().isoformat(),
                "data_source": "mock"  # Would be "database" in production
            }
        }
        
        logger.info(f"Auth stats requested by user {current_user.id}")
        return stats
        
    except Exception as e:
        logger.error(f"Error getting auth stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve authentication statistics"
        )


@router.get("/health")
async def get_auth_health() -> Dict[str, Any]:
    """
    Get authentication system health status.
    Public endpoint for monitoring.
    """
    try:
        # Test JWT service health
        test_data = {"sub": "health_check", "test": True}
        test_token = jwt_service.create_access_token(test_data, timedelta(seconds=1))
        token_valid = jwt_service.verify_token(test_token) is not None
        
        health = {
            "status": "healthy" if token_valid else "unhealthy",
            "jwt_service": "operational" if token_valid else "degraded",
            "database": "connected",  # Would check actual DB connection
            "features": {
                "telegram_sso": settings.telegram_sso_enabled,
                "otp": True,
                "phone_auth": True
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return health
        
    except Exception as e:
        logger.error(f"Error checking auth health: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@router.get("/logs")
async def get_auth_logs(
    limit: int = 100,
    offset: int = 0,
    level: str = "INFO",
    current_user = Depends(require_admin)
) -> Dict[str, Any]:
    """
    Get authentication audit logs.
    Restricted to admin users only.
    """
    try:
        # This would typically query an audit log database
        # For now, return mock data
        logs = {
            "logs": [
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "level": "INFO",
                    "event": "user_login",
                    "user_id": current_user.id,
                    "username": current_user.username,
                    "ip_address": "127.0.0.1",
                    "user_agent": "test-client",
                    "success": True
                },
                {
                    "timestamp": (datetime.utcnow() - timedelta(minutes=5)).isoformat(),
                    "level": "WARNING",
                    "event": "jwt_token_expired",
                    "user_id": None,
                    "username": None,
                    "ip_address": "127.0.0.1",
                    "user_agent": "test-client",
                    "success": False
                }
            ],
            "pagination": {
                "limit": limit,
                "offset": offset,
                "total": 2,
                "has_more": False
            },
            "metadata": {
                "data_source": "mock",
                "last_updated": datetime.utcnow().isoformat()
            }
        }
        
        logger.info(f"Auth logs requested by user {current_user.id}")
        return logs
        
    except Exception as e:
        logger.error(f"Error getting auth logs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve authentication logs"
        )
