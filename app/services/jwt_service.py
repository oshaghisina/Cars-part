"""
Unified JWT service for authentication.
Consolidates JWT operations using a single library (PyJWT).
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import jwt
from fastapi import HTTPException, status

from app.core.config import settings

logger = logging.getLogger(__name__)


class JWTService:
    """Unified JWT service using PyJWT library."""

    def __init__(self):
        self.secret_key = settings.jwt_secret_key
        self.algorithm = settings.jwt_algorithm
        self.access_token_expire_minutes = settings.jwt_access_token_expire_minutes

    def create_access_token(
        self, 
        data: Dict[str, Any], 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create JWT access token with standardized claims.
        
        Args:
            data: Token payload data
            expires_delta: Custom expiration time
            
        Returns:
            Encoded JWT token string
        """
        to_encode = data.copy()
        
        # Set expiration time
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        # Standardized claims structure
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "iss": "china-car-parts-api",  # Issuer
            "aud": "china-car-parts-client"  # Audience
        })
        
        # Ensure sub claim is string (PyJWT requirement)
        if "sub" in to_encode and isinstance(to_encode["sub"], int):
            to_encode["sub"] = str(to_encode["sub"])
        
        try:
            encoded_jwt = jwt.encode(
                to_encode, 
                self.secret_key, 
                algorithm=self.algorithm
            )
            logger.debug(f"JWT token created for user: {data.get('sub', 'unknown')}")
            return encoded_jwt
        except Exception as e:
            logger.error(f"Failed to create JWT token: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Token creation failed"
            )

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify JWT token and return payload.
        
        Args:
            token: JWT token string
            
        Returns:
            Token payload if valid, None if invalid
        """
        try:
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm],
                audience="china-car-parts-client",
                issuer="china-car-parts-api"
            )
            
            # Validate required claims
            if not payload.get("sub"):
                logger.warning("JWT token missing 'sub' claim")
                return None
                
            logger.debug(f"JWT token verified for user: {payload.get('sub')}")
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {e}")
            return None
        except Exception as e:
            logger.error(f"JWT verification error: {e}")
            return None

    def get_user_id_from_token(self, token: str) -> Optional[int]:
        """
        Extract user ID from JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            User ID if valid, None if invalid
        """
        payload = self.verify_token(token)
        if not payload:
            return None
            
        # Support both canonical (sub=user_id) and legacy (sub=username) formats
        sub_claim = payload.get("sub")
        user_id_claim = payload.get("user_id")
        
        # If sub is an integer, it's the new canonical format
        if sub_claim is not None:
            try:
                return int(sub_claim)
            except (ValueError, TypeError):
                # If sub is not an integer, it might be legacy username format
                # In this case, we need to look up the user by username
                if user_id_claim is not None:
                    try:
                        return int(user_id_claim)
                    except (ValueError, TypeError):
                        pass
                # If no user_id claim, we can't resolve this token
                logger.warning(f"Legacy token with username sub claim: {sub_claim}")
                return None
        
        # Fallback to user_id claim
        if user_id_claim is not None:
            try:
                return int(user_id_claim)
            except (ValueError, TypeError):
                logger.warning(f"Invalid user_id in token: {user_id_claim}")
                return None
        
        return None

    def get_username_from_token(self, token: str) -> Optional[str]:
        """
        Extract username from JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            Username if valid, None if invalid
        """
        payload = self.verify_token(token)
        if not payload:
            return None
            
        # Support both 'username' and 'sub' claims for backward compatibility
        return payload.get("username") or payload.get("sub")

    def get_user_id_from_legacy_token(self, token: str, db_session) -> Optional[int]:
        """
        Handle legacy tokens where sub=username.
        Look up user by username to get user_id.
        
        Args:
            token: JWT token string
            db_session: Database session for user lookup
            
        Returns:
            User ID if found, None if not found
        """
        payload = self.verify_token(token)
        if not payload:
            return None
            
        sub_claim = payload.get("sub")
        if not sub_claim:
            return None
            
        # If sub is not an integer, treat it as username
        try:
            int(sub_claim)
            # If it's an integer, it's already canonical format
            return int(sub_claim)
        except (ValueError, TypeError):
            # It's a username, look it up
            try:
                from app.db.models import User
                user = db_session.query(User).filter(User.username == sub_claim).first()
                return user.id if user else None
            except Exception as e:
                logger.warning(f"Error looking up user by username {sub_claim}: {e}")
                return None

    def get_role_from_token(self, token: str) -> Optional[str]:
        """
        Extract role from JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            Role if valid, None if invalid
        """
        payload = self.verify_token(token)
        if not payload:
            return None
            
        return payload.get("role", "user")

    def is_token_expired(self, token: str) -> bool:
        """
        Check if token is expired without full verification.
        
        Args:
            token: JWT token string
            
        Returns:
            True if expired, False if not expired
        """
        try:
            # Decode without verification to check expiration
            payload = jwt.decode(
                token, 
                options={"verify_signature": False, "verify_exp": True}
            )
            return False  # If we get here, token is not expired
        except jwt.ExpiredSignatureError:
            return True
        except Exception:
            return True  # Treat any other error as expired

    def get_token_expiration(self, token: str) -> Optional[datetime]:
        """
        Get token expiration time.
        
        Args:
            token: JWT token string
            
        Returns:
            Expiration datetime if valid, None if invalid
        """
        try:
            payload = jwt.decode(
                token, 
                options={"verify_signature": False, "verify_exp": False}
            )
            exp_timestamp = payload.get("exp")
            if exp_timestamp:
                # Convert timestamp to UTC datetime (JWT timestamps are always UTC)
                return datetime.utcfromtimestamp(exp_timestamp)
        except Exception as e:
            logger.warning(f"Failed to get token expiration: {e}")
        return None


# Global JWT service instance
jwt_service = JWTService()


# Backward compatibility functions
def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Backward compatibility function for token creation."""
    return jwt_service.create_access_token(data, expires_delta)


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Backward compatibility function for token verification."""
    return jwt_service.verify_token(token)
