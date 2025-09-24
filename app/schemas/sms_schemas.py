"""SMS-related Pydantic schemas."""

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class SMSMessage(BaseModel):
    """SMS message schema."""
    
    phone_number: str = Field(..., description="Recipient phone number")
    message: str = Field(..., description="SMS message content")
    language: str = Field(default="fa", description="Message language (fa/en)")
    
    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, v):
        """Validate Iranian phone number format."""
        # Remove any non-digit characters
        cleaned = ''.join(filter(str.isdigit, v))
        
        # Iranian mobile numbers: 09xxxxxxxxx (11 digits)
        if len(cleaned) == 11 and cleaned.startswith('09'):
            return v
        
        # International format: +989xxxxxxxxx
        if len(cleaned) == 12 and cleaned.startswith('989'):
            return v
            
        raise ValueError('Invalid Iranian phone number format')


class SMSResponse(BaseModel):
    """SMS response schema."""
    
    success: bool = Field(..., description="Whether SMS was sent successfully")
    message: str = Field(..., description="Response message")
    message_id: Optional[int] = Field(None, description="SMS log ID")
    cost: float = Field(default=0.0, description="SMS cost")


class SMSTemplateData(BaseModel):
    """SMS template data schema."""
    
    name: str = Field(..., description="Template name")
    template_type: str = Field(..., description="Template type")
    content_en: Optional[str] = Field(None, description="English content")
    content_fa: Optional[str] = Field(None, description="Persian content")
    variables: Optional[Dict[str, str]] = Field(None, description="Template variables")
    is_active: bool = Field(default=True, description="Whether template is active")


class SMSTemplateResponse(BaseModel):
    """SMS template response schema."""
    
    id: int
    name: str
    template_type: str
    content_en: Optional[str]
    content_fa: Optional[str]
    variables: Optional[Dict[str, str]]
    is_active: bool
    created_at: datetime
    updated_at: datetime


class SMSTemplateCreate(BaseModel):
    """SMS template creation schema."""
    
    name: str = Field(..., description="Template name")
    template_type: str = Field(..., description="Template type")
    content_en: Optional[str] = Field(None, description="English content")
    content_fa: Optional[str] = Field(None, description="Persian content")
    variables: Optional[Dict[str, str]] = Field(None, description="Template variables")
    is_active: bool = Field(default=True, description="Whether template is active")


class SMSTemplateUpdate(BaseModel):
    """SMS template update schema."""
    
    name: Optional[str] = Field(None, description="Template name")
    template_type: Optional[str] = Field(None, description="Template type")
    content_en: Optional[str] = Field(None, description="English content")
    content_fa: Optional[str] = Field(None, description="Persian content")
    variables: Optional[Dict[str, str]] = Field(None, description="Template variables")
    is_active: Optional[bool] = Field(None, description="Whether template is active")


class SMSLogResponse(BaseModel):
    """SMS log response schema."""
    
    id: int
    recipient_phone: str
    content: str
    template_id: Optional[int]
    status: str
    sent_at: Optional[datetime]
    delivered_at: Optional[datetime]
    error_message: Optional[str]
    cost: Optional[float]
    retry_count: int
    created_at: datetime


class StockAlertCreate(BaseModel):
    """Stock alert creation schema."""
    
    part_id: int = Field(..., description="Part ID to monitor")
    phone_number: str = Field(..., description="Phone number for notifications")
    email: Optional[str] = Field(None, description="Email for notifications")
    
    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, v):
        """Validate Iranian phone number format."""
        # Remove any non-digit characters
        cleaned = ''.join(filter(str.isdigit, v))
        
        # Iranian mobile numbers: 09xxxxxxxxx (11 digits)
        if len(cleaned) == 11 and cleaned.startswith('09'):
            return v
        
        # International format: +989xxxxxxxxx
        if len(cleaned) == 12 and cleaned.startswith('989'):
            return v
            
        raise ValueError('Invalid Iranian phone number format')


class StockAlertResponse(BaseModel):
    """Stock alert response schema."""
    
    id: int
    user_id: Optional[int]
    part_id: int
    phone_number: str
    email: Optional[str]
    is_active: bool
    is_notified: bool
    notified_at: Optional[datetime]
    created_at: datetime


class SMSCampaignCreate(BaseModel):
    """SMS campaign creation schema."""
    
    name: str = Field(..., description="Campaign name")
    description: Optional[str] = Field(None, description="Campaign description")
    template_id: int = Field(..., description="Template ID to use")
    target_audience: str = Field(..., description="Target audience")
    scheduled_at: Optional[datetime] = Field(None, description="Scheduled send time")


class SMSCampaignResponse(BaseModel):
    """SMS campaign response schema."""
    
    id: int
    name: str
    description: Optional[str]
    template_id: int
    target_audience: str
    status: str
    scheduled_at: Optional[datetime]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    total_recipients: int
    sent_count: int
    delivered_count: int
    failed_count: int
    total_cost: Optional[float]
    created_at: datetime
    updated_at: datetime


class SMSAnalyticsResponse(BaseModel):
    """SMS analytics response schema."""
    
    total_sent: int = Field(..., description="Total SMS sent")
    successful: int = Field(..., description="Successfully sent SMS")
    failed: int = Field(..., description="Failed SMS")
    success_rate: float = Field(..., description="Success rate percentage")
    total_cost: float = Field(..., description="Total cost")
    average_cost: float = Field(..., description="Average cost per SMS")


class UserSMSPreferences(BaseModel):
    """User SMS preferences schema."""
    
    sms_notifications: bool = Field(default=True, description="General SMS notifications")
    sms_marketing: bool = Field(default=False, description="Marketing SMS")
    sms_delivery: bool = Field(default=True, description="Delivery notifications")
    phone_verified: bool = Field(default=False, description="Phone verification status")


class UserSMSPreferencesUpdate(BaseModel):
    """User SMS preferences update schema."""
    
    sms_notifications: Optional[bool] = Field(None, description="General SMS notifications")
    sms_marketing: Optional[bool] = Field(None, description="Marketing SMS")
    sms_delivery: Optional[bool] = Field(None, description="Delivery notifications")


class BulkSMSRequest(BaseModel):
    """Bulk SMS request schema."""
    
    phone_numbers: List[str] = Field(..., description="List of phone numbers")
    message: str = Field(..., description="SMS message content")
    template_id: Optional[int] = Field(None, description="Template ID for tracking")
    
    @field_validator('phone_numbers')
    @classmethod
    def validate_phone_numbers(cls, v):
        """Validate phone numbers list."""
        if not v:
            raise ValueError('Phone numbers list cannot be empty')
        
        if len(v) > 1000:  # Limit bulk SMS size
            raise ValueError('Cannot send to more than 1000 recipients at once')
        
        # Validate each phone number
        for phone in v:
            cleaned = ''.join(filter(str.isdigit, phone))
            if not ((len(cleaned) == 11 and cleaned.startswith('09')) or 
                   (len(cleaned) == 12 and cleaned.startswith('989'))):
                raise ValueError(f'Invalid phone number format: {phone}')
        
        return v


class BulkSMSResponse(BaseModel):
    """Bulk SMS response schema."""
    
    total_recipients: int = Field(..., description="Total recipients")
    successful: int = Field(..., description="Successfully sent")
    failed: int = Field(..., description="Failed to send")
    total_cost: float = Field(..., description="Total cost")
    results: List[SMSResponse] = Field(..., description="Individual SMS results")


class PhoneVerificationRequest(BaseModel):
    """Phone verification request schema."""
    
    phone_number: str = Field(..., description="Phone number to verify")
    
    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, v):
        """Validate Iranian phone number format."""
        cleaned = ''.join(filter(str.isdigit, v))
        
        if len(cleaned) == 11 and cleaned.startswith('09'):
            return v
        
        if len(cleaned) == 12 and cleaned.startswith('989'):
            return v
            
        raise ValueError('Invalid Iranian phone number format')


class PhoneVerificationResponse(BaseModel):
    """Phone verification response schema."""
    
    success: bool = Field(..., description="Whether verification SMS was sent")
    message: str = Field(..., description="Response message")
    verification_id: Optional[str] = Field(None, description="Verification session ID")


class PhoneVerificationConfirm(BaseModel):
    """Phone verification confirmation schema."""
    
    phone_number: str = Field(..., description="Phone number")
    verification_code: str = Field(..., description="Verification code")
    verification_id: str = Field(..., description="Verification session ID")
    
    @field_validator('verification_code')
    @classmethod
    def validate_verification_code(cls, v):
        """Validate verification code format."""
        if not v.isdigit() or len(v) != 6:
            raise ValueError('Verification code must be 6 digits')
        return v
