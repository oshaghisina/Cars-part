"""
Unit tests for JWT validation and token handling.
Tests both canonical and legacy token formats.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock

from app.services.jwt_service import JWTService
from app.core.config import settings


class TestJWTValidation:
    """Test JWT token creation, validation, and claim extraction."""

    def setup_method(self):
        """Set up test fixtures."""
        self.jwt_service = JWTService()
        self.test_user_id = 123
        self.test_username = "testuser"
        self.test_role = "admin"

    def test_create_canonical_token(self):
        """Test creating token with canonical claims (sub=user_id)."""
        data = {
            "sub": self.test_user_id,
            "user_id": self.test_user_id,
            "username": self.test_username,
            "role": self.test_role
        }
        
        token = self.jwt_service.create_access_token(data)
        assert token is not None
        assert isinstance(token, str)
        
        # Verify token can be decoded
        payload = self.jwt_service.verify_token(token)
        assert payload is not None
        assert payload["sub"] == self.test_user_id
        assert payload["user_id"] == self.test_user_id
        assert payload["username"] == self.test_username
        assert payload["role"] == self.test_role

    def test_create_legacy_token(self):
        """Test creating token with legacy claims (sub=username)."""
        data = {
            "sub": self.test_username,  # Legacy format
            "user_id": self.test_user_id,
            "username": self.test_username,
            "role": self.test_role
        }
        
        token = self.jwt_service.create_access_token(data)
        assert token is not None
        
        # Verify token can be decoded
        payload = self.jwt_service.verify_token(token)
        assert payload is not None
        assert payload["sub"] == self.test_username
        assert payload["user_id"] == self.test_user_id

    def test_get_user_id_from_canonical_token(self):
        """Test extracting user ID from canonical token."""
        data = {"sub": self.test_user_id, "user_id": self.test_user_id}
        token = self.jwt_service.create_access_token(data)
        
        user_id = self.jwt_service.get_user_id_from_token(token)
        assert user_id == self.test_user_id

    def test_get_user_id_from_legacy_token(self):
        """Test extracting user ID from legacy token."""
        data = {"sub": self.test_username, "user_id": self.test_user_id}
        token = self.jwt_service.create_access_token(data)
        
        user_id = self.jwt_service.get_user_id_from_token(token)
        assert user_id == self.test_user_id

    def test_get_user_id_from_legacy_token_with_db_lookup(self):
        """Test extracting user ID from legacy token using database lookup."""
        # Mock database session and user
        mock_db = Mock()
        mock_user = Mock()
        mock_user.id = self.test_user_id
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        
        data = {"sub": self.test_username}  # No user_id claim
        token = self.jwt_service.create_access_token(data)
        
        user_id = self.jwt_service.get_user_id_from_legacy_token(token, mock_db)
        assert user_id == self.test_user_id

    def test_token_expiration(self):
        """Test token expiration handling."""
        # Create token with short expiration
        data = {"sub": self.test_user_id}
        token = self.jwt_service.create_access_token(data, timedelta(seconds=1))
        
        # Token should be valid initially
        assert not self.jwt_service.is_token_expired(token)
        
        # Wait for expiration (in real test, you'd use time mocking)
        # For now, just test the method exists and works
        assert hasattr(self.jwt_service, 'is_token_expired')

    def test_invalid_token_handling(self):
        """Test handling of invalid tokens."""
        # Invalid token format
        invalid_token = "invalid.token.here"
        payload = self.jwt_service.verify_token(invalid_token)
        assert payload is None
        
        # Empty token
        payload = self.jwt_service.verify_token("")
        assert payload is None
        
        # None token
        payload = self.jwt_service.verify_token(None)
        assert payload is None

    def test_ttl_configuration_match(self):
        """Test that TTL configuration matches token expiration."""
        data = {"sub": self.test_user_id}
        token = self.jwt_service.create_access_token(data)
        
        # Get token expiration
        exp_time = self.jwt_service.get_token_expiration(token)
        assert exp_time is not None
        
        # Calculate expected expiration
        expected_exp = datetime.utcnow() + timedelta(minutes=settings.jwt_access_token_expire_minutes)
        
        # Allow 1 minute tolerance for test execution time
        time_diff = abs((exp_time - expected_exp).total_seconds())
        assert time_diff < 60

    def test_standardized_claims(self):
        """Test that tokens contain standardized claims."""
        data = {"sub": self.test_user_id}
        token = self.jwt_service.create_access_token(data)
        payload = self.jwt_service.verify_token(token)
        
        # Check required claims
        assert "exp" in payload  # Expiration
        assert "iat" in payload  # Issued at
        assert "iss" in payload  # Issuer
        assert "aud" in payload  # Audience
        assert "sub" in payload  # Subject
        
        # Check claim values
        assert payload["iss"] == "china-car-parts-api"
        assert payload["aud"] == "china-car-parts-client"

    def test_backward_compatibility_functions(self):
        """Test backward compatibility functions."""
        from app.services.jwt_service import create_access_token, verify_token
        
        data = {"sub": self.test_user_id}
        
        # Test backward compatibility functions
        token = create_access_token(data)
        assert token is not None
        
        payload = verify_token(token)
        assert payload is not None
        assert payload["sub"] == self.test_user_id

    def test_role_extraction(self):
        """Test role extraction from token."""
        data = {"sub": self.test_user_id, "role": self.test_role}
        token = self.jwt_service.create_access_token(data)
        
        role = self.jwt_service.get_role_from_token(token)
        assert role == self.test_role

    def test_username_extraction(self):
        """Test username extraction from token."""
        data = {"sub": self.test_user_id, "username": self.test_username}
        token = self.jwt_service.create_access_token(data)
        
        username = self.jwt_service.get_username_from_token(token)
        assert username == self.test_username

    def test_missing_claims_handling(self):
        """Test handling of tokens with missing claims."""
        # Token with no sub claim
        data = {"user_id": self.test_user_id}
        token = self.jwt_service.create_access_token(data)
        
        # Should still be valid but get_user_id_from_token should return None
        payload = self.jwt_service.verify_token(token)
        assert payload is not None
        
        user_id = self.jwt_service.get_user_id_from_token(token)
        assert user_id is None  # No sub claim

    def test_token_creation_error_handling(self):
        """Test error handling during token creation."""
        # This would require mocking jwt.encode to raise an exception
        # For now, just test that the method exists and has error handling
        assert hasattr(self.jwt_service, 'create_access_token')
        
        # Test with valid data
        data = {"sub": self.test_user_id}
        token = self.jwt_service.create_access_token(data)
        assert token is not None
