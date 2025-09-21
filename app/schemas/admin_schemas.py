"""Admin API schemas."""

from typing import Dict, Optional, List
from pydantic import BaseModel
from datetime import datetime


class SettingResponse(BaseModel):
    """Setting response schema."""

    key: str
    value: str
    updated_at: datetime
    updated_by: Optional[int] = None


class SettingUpdate(BaseModel):
    """Setting update schema."""

    value: str


class SettingsResponse(BaseModel):
    """Multiple settings response schema."""

    settings: Dict[str, str]
    total: int


class AdminUserResponse(BaseModel):
    """Admin user response schema."""

    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    role: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None


class AdminUserListResponse(BaseModel):
    """Admin users list response schema."""

    users: List[AdminUserResponse]
    total: int
    page: int
    limit: int
    total_pages: int


class AdminUserCreate(BaseModel):
    """Admin user creation schema."""

    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str = "admin"


class SystemStatusResponse(BaseModel):
    """System status response schema."""

    status: str
    version: str
    environment: str
    database_status: str
    total_users: int
    total_parts: int
    total_orders: int
    last_backup: Optional[datetime] = None
