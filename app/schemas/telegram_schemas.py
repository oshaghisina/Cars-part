"""
Pydantic schemas for Telegram SSO operations.
"""

from typing import Dict, Optional
from pydantic import BaseModel, Field, validator


class TelegramUserInfo(BaseModel):
    """Telegram user information schema."""
    
    telegram_id: int = Field(..., description="Telegram user ID")
    username: Optional[str] = Field(None, description="Telegram username")
    first_name: Optional[str] = Field(None, description="First name")
    last_name: Optional[str] = Field(None, description="Last name")
    language_code: Optional[str] = Field(None, description="Language code")
    is_bot: bool = Field(default=False, description="Is bot account")
    is_premium: bool = Field(default=False, description="Is premium account")


class TelegramLinkRequest(BaseModel):
    """Request schema for Telegram account linking."""
    
    telegram_id: int = Field(..., description="Telegram user ID")
    user_id: Optional[int] = Field(None, description="Platform user ID (for existing users)")
    action: str = Field(default="link_account", description="Link action type")
    
    @validator('action')
    def validate_action(cls, v):
        """Validate action type."""
        allowed_actions = ['link_account', 'login', 'verify']
        if v not in allowed_actions:
            raise ValueError(f'Action must be one of: {", ".join(allowed_actions)}')
        return v


class TelegramLinkResponse(BaseModel):
    """Response schema for Telegram account linking."""
    
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Response message")
    link_token: Optional[str] = Field(None, description="Link token for web authentication")
    telegram_url: Optional[str] = Field(None, description="Telegram bot URL")
    expires_in: Optional[int] = Field(None, description="Token expiry time in seconds")
    code: Optional[str] = Field(None, description="Error code if applicable")


class TelegramVerifyRequest(BaseModel):
    """Request schema for Telegram token verification."""
    
    token: str = Field(..., description="Link token to verify")
    action: str = Field(default="link_account", description="Expected action type")
    
    @validator('action')
    def validate_action(cls, v):
        """Validate action type."""
        allowed_actions = ['link_account', 'login', 'verify']
        if v not in allowed_actions:
            raise ValueError(f'Action must be one of: {", ".join(allowed_actions)}')
        return v


class TelegramVerifyResponse(BaseModel):
    """Response schema for Telegram token verification."""
    
    success: bool = Field(..., description="Whether verification was successful")
    message: str = Field(..., description="Response message")
    telegram_user: Optional[Dict] = Field(None, description="Telegram user information")
    platform_user: Optional[Dict] = Field(None, description="Platform user information")
    access_token: Optional[str] = Field(None, description="JWT access token if login successful")
    code: Optional[str] = Field(None, description="Error code if applicable")


class TelegramLoginRequest(BaseModel):
    """Request schema for Telegram-based login."""
    
    telegram_id: int = Field(..., description="Telegram user ID")
    user_info: Optional[TelegramUserInfo] = Field(None, description="Telegram user information")


class TelegramLoginResponse(BaseModel):
    """Response schema for Telegram-based login."""
    
    success: bool = Field(..., description="Whether login was successful")
    message: str = Field(..., description="Response message")
    access_token: Optional[str] = Field(None, description="JWT access token")
    expires_in: Optional[int] = Field(None, description="Token expiry time in seconds")
    user: Optional[Dict] = Field(None, description="User information")
    telegram_user: Optional[Dict] = Field(None, description="Telegram user information")
    code: Optional[str] = Field(None, description="Error code if applicable")


class TelegramDeepLinkRequest(BaseModel):
    """Request schema for creating Telegram deep links."""
    
    telegram_id: int = Field(..., description="Telegram user ID")
    action: str = Field(..., description="Deep link action")
    target_url: str = Field(..., description="Target URL for redirection")
    parameters: Optional[Dict] = Field(None, description="Additional parameters")
    
    @validator('action')
    def validate_action(cls, v):
        """Validate action type."""
        allowed_actions = ['login', 'link_account', 'verify', 'dashboard']
        if v not in allowed_actions:
            raise ValueError(f'Action must be one of: {", ".join(allowed_actions)}')
        return v


class TelegramDeepLinkResponse(BaseModel):
    """Response schema for Telegram deep links."""
    
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Response message")
    link_id: Optional[str] = Field(None, description="Deep link ID")
    telegram_url: Optional[str] = Field(None, description="Telegram bot URL with deep link")
    expires_in: Optional[int] = Field(None, description="Link expiry time in seconds")
    code: Optional[str] = Field(None, description="Error code if applicable")


class TelegramDeepLinkVerifyRequest(BaseModel):
    """Request schema for verifying Telegram deep links."""
    
    link_id: str = Field(..., description="Deep link ID to verify")


class TelegramDeepLinkVerifyResponse(BaseModel):
    """Response schema for Telegram deep link verification."""
    
    success: bool = Field(..., description="Whether verification was successful")
    message: str = Field(..., description="Response message")
    telegram_user: Optional[Dict] = Field(None, description="Telegram user information")
    action: Optional[str] = Field(None, description="Deep link action")
    target_url: Optional[str] = Field(None, description="Target URL")
    parameters: Optional[Dict] = Field(None, description="Link parameters")
    code: Optional[str] = Field(None, description="Error code if applicable")


class TelegramUnlinkRequest(BaseModel):
    """Request schema for unlinking Telegram account."""
    
    telegram_id: int = Field(..., description="Telegram user ID")


class TelegramUnlinkResponse(BaseModel):
    """Response schema for unlinking Telegram account."""
    
    success: bool = Field(..., description="Whether unlinking was successful")
    message: str = Field(..., description="Response message")
    code: Optional[str] = Field(None, description="Error code if applicable")


class TelegramBotSessionRequest(BaseModel):
    """Request schema for bot session management."""
    
    telegram_id: int = Field(..., description="Telegram user ID")
    state: str = Field(default="idle", description="Session state")
    context: Optional[Dict] = Field(None, description="Session context data")


class TelegramBotSessionResponse(BaseModel):
    """Response schema for bot session management."""
    
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Response message")
    session_id: Optional[str] = Field(None, description="Session ID")
    state: Optional[str] = Field(None, description="Current session state")
    context: Optional[Dict] = Field(None, description="Session context")
    expires_in: Optional[int] = Field(None, description="Session expiry time in seconds")
    code: Optional[str] = Field(None, description="Error code if applicable")


class TelegramStatsResponse(BaseModel):
    """Response schema for Telegram integration statistics."""
    
    total_telegram_users: int = Field(..., description="Total Telegram users")
    linked_users: int = Field(..., description="Linked users count")
    unlinked_users: int = Field(..., description="Unlinked users count")
    active_sessions: int = Field(..., description="Active bot sessions count")
    link_rate: float = Field(..., description="Account linking rate percentage")


class TelegramWebhookRequest(BaseModel):
    """Request schema for Telegram webhook updates."""
    
    update_id: int = Field(..., description="Update ID")
    message: Optional[Dict] = Field(None, description="Message data")
    callback_query: Optional[Dict] = Field(None, description="Callback query data")
    inline_query: Optional[Dict] = Field(None, description="Inline query data")


class TelegramWebhookResponse(BaseModel):
    """Response schema for Telegram webhook processing."""
    
    success: bool = Field(..., description="Whether webhook was processed successfully")
    message: str = Field(..., description="Response message")
    processed: bool = Field(default=False, description="Whether update was processed")
    code: Optional[str] = Field(None, description="Error code if applicable")
