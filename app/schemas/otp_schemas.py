"""
Pydantic schemas for OTP (One-Time Password) operations.
"""

from typing import Optional
from pydantic import BaseModel, Field, validator


class OTPRequest(BaseModel):
    """Request schema for OTP code generation."""
    
    phone_number: str = Field(..., description="Phone number in E.164 format")
    code_type: str = Field(default="login", description="Type of OTP code")
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        """Validate phone number format."""
        if not v.startswith('+'):
            raise ValueError('Phone number must start with +')
        if len(v) < 10 or len(v) > 16:
            raise ValueError('Phone number must be between 10 and 16 characters')
        return v
    
    @validator('code_type')
    def validate_code_type(cls, v):
        """Validate code type."""
        allowed_types = ['login', 'verify', 'reset']
        if v not in allowed_types:
            raise ValueError(f'Code type must be one of: {", ".join(allowed_types)}')
        return v


class OTPVerify(BaseModel):
    """Request schema for OTP code verification."""
    
    phone_number: str = Field(..., description="Phone number in E.164 format")
    code: str = Field(..., description="OTP code", min_length=4, max_length=8)
    code_type: str = Field(default="login", description="Type of OTP code")
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        """Validate phone number format."""
        if not v.startswith('+'):
            raise ValueError('Phone number must start with +')
        if len(v) < 10 or len(v) > 16:
            raise ValueError('Phone number must be between 10 and 16 characters')
        return v
    
    @validator('code')
    def validate_code(cls, v):
        """Validate OTP code format."""
        if not v.isdigit():
            raise ValueError('OTP code must contain only digits')
        return v
    
    @validator('code_type')
    def validate_code_type(cls, v):
        """Validate code type."""
        allowed_types = ['login', 'verify', 'reset']
        if v not in allowed_types:
            raise ValueError(f'Code type must be one of: {", ".join(allowed_types)}')
        return v


class OTPResponse(BaseModel):
    """Response schema for OTP operations."""
    
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Response message")
    code: Optional[str] = Field(None, description="Error code if applicable")
    expires_in: Optional[int] = Field(None, description="OTP expiry time in seconds")
    resend: Optional[bool] = Field(None, description="Whether this was a resend")


class OTPVerifyResponse(BaseModel):
    """Response schema for OTP verification."""
    
    success: bool = Field(..., description="Whether verification was successful")
    message: str = Field(..., description="Response message")
    code: Optional[str] = Field(None, description="Error code if applicable")
    user_id: Optional[int] = Field(None, description="User ID if verification successful")
    access_token: Optional[str] = Field(None, description="Access token if login successful")


class PhoneLoginRequest(BaseModel):
    """Request schema for phone-based login."""
    
    phone_number: str = Field(..., description="Phone number in E.164 format")
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        """Validate phone number format."""
        if not v.startswith('+'):
            raise ValueError('Phone number must start with +')
        if len(v) < 10 or len(v) > 16:
            raise ValueError('Phone number must be between 10 and 16 characters')
        return v


class PhoneLoginVerifyRequest(BaseModel):
    """Request schema for phone login verification."""
    
    phone_number: str = Field(..., description="Phone number in E.164 format")
    otp_code: str = Field(..., description="OTP code", min_length=4, max_length=8)
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        """Validate phone number format."""
        if not v.startswith('+'):
            raise ValueError('Phone number must start with +')
        if len(v) < 10 or len(v) > 16:
            raise ValueError('Phone number must be between 10 and 16 characters')
        return v
    
    @validator('otp_code')
    def validate_otp_code(cls, v):
        """Validate OTP code format."""
        if not v.isdigit():
            raise ValueError('OTP code must contain only digits')
        return v


class PhoneLoginResponse(BaseModel):
    """Response schema for phone login."""
    
    success: bool = Field(..., description="Whether login was successful")
    message: str = Field(..., description="Response message")
    access_token: Optional[str] = Field(None, description="JWT access token")
    expires_in: Optional[int] = Field(None, description="Token expiry time in seconds")
    user: Optional[dict] = Field(None, description="User information")
    code: Optional[str] = Field(None, description="Error code if applicable")


class OTPStatsResponse(BaseModel):
    """Response schema for OTP statistics."""
    
    active_otps: int = Field(..., description="Number of active OTP codes")
    total_24h: int = Field(..., description="Total OTP requests in last 24 hours")
    rate_limit_status: str = Field(..., description="Current rate limit status")


class RateLimitInfo(BaseModel):
    """Information about rate limits."""
    
    action: str = Field(..., description="Rate limited action")
    count: int = Field(..., description="Current count")
    limit: int = Field(..., description="Rate limit threshold")
    window_minutes: int = Field(..., description="Rate limit window in minutes")
    reset_at: Optional[str] = Field(None, description="When the rate limit resets")
