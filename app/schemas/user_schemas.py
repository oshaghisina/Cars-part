"""Pydantic schemas for user management."""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr, validator


class UserBase(BaseModel):
    """Base user schema."""
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    phone: Optional[str] = None
    role: str = "user"
    timezone: str = "UTC"
    language: str = "en"
    preferences: Optional[Dict[str, Any]] = None


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters long')
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError(
                'Username can only contain letters, numbers, underscores, and hyphens')
        return v


class UserUpdate(BaseModel):
    """Schema for updating user information."""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    timezone: Optional[str] = None
    language: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None

    @validator('username')
    def validate_username(cls, v):
        if v is not None:
            if len(v) < 3:
                raise ValueError('Username must be at least 3 characters long')
            if not v.replace('_', '').replace('-', '').isalnum():
                raise ValueError(
                    'Username can only contain letters, numbers, underscores, and hyphens')
        return v


class UserLogin(BaseModel):
    """Schema for user login."""
    username_or_email: str
    password: str


class PasswordChange(BaseModel):
    """Schema for password change."""
    current_password: str
    new_password: str

    @validator('new_password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class UserResponse(UserBase):
    """Schema for user response."""
    id: int
    is_active: bool
    is_verified: bool
    last_login: Optional[datetime] = None
    login_attempts: int
    locked_until: Optional[datetime] = None
    password_changed_at: datetime
    created_at: datetime
    updated_at: datetime
    avatar_url: Optional[str] = None

    class Config:
        from_attributes = True


class UserSummary(BaseModel):
    """Summary user information."""
    id: int
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    role: str
    is_active: bool
    last_login: Optional[datetime] = None
    created_at: datetime

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    class Config:
        from_attributes = True


class UserSessionResponse(BaseModel):
    Schema for user session response.
    id: int
    user_id: int
    session_token: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    is_active: bool
    expires_at: datetime
    last_activity: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# Note: Role and permission management has been simplified to use
# string-based roles


class UserActivityLogResponse(BaseModel):
    ""Schema for user activity log response."""
    id: int
    user_id: int
    action: str
    module: str
    resource_type: Optional[str] = None
    resource_id: Optional[int] = None
    description: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class UserStatistics(BaseModel):
    """Schema for user statistics."""
    total_users: int
    active_users: int
    verified_users: int
    recent_logins: int
    role_distribution: Dict[str, int]


class LoginResponse(BaseModel):
    """Schema for login response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class TokenResponse(BaseModel):
    """Schema for token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserListResponse(BaseModel):
    """Schema for user list response."""
    users: List[UserSummary]
    total: int
    page: int
    limit: int
    total_pages: int


class UserActivityListResponse(BaseModel):
    """Schema for user activity list response."""
    activities: List[UserActivityLogResponse]
    total: int
    page: int
    limit: int
    total_pages: int


# JWT Token schemas
class Token(BaseModel):
    """JWT token schema."""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """JWT token data schema."""
    username: Optional[str] = None
    user_id: Optional[int] = None
    role: Optional[str] = None


# System initialization schemas
class SystemInit(BaseModel):
    """Schema for system initialization."""
    admin_username: str
    admin_email: EmailStr
    admin_password: str
    admin_first_name: str
    admin_last_name: str

    @validator('admin_password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class BulkUserCreate(BaseModel):
    """Schema for bulk user creation."""
    users: List[UserCreate]

    @validator('users')
    def validate_users_list(cls, v):
        if len(v) == 0:
            raise ValueError('Users list cannot be empty')
        if len(v) > 100:
            raise ValueError('Cannot create more than 100 users at once')
        return v


class BulkRoleAssignment(BaseModel):
    """Schema for bulk role assignment."""
    user_ids: List[int]
    role: str

    @validator('user_ids')
    def validate_user_ids(cls, v):
        if len(v) == 0:
            raise ValueError('User IDs list cannot be empty')
        if len(v) > 100:
            raise ValueError(
                'Cannot assign roles to more than 100 users at once')
        return v
