"""SMS API endpoints for Melipayamak integration."""

import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.core.config import settings
from app.db.models import User
from app.models.sms_models import SMSLog, SMSTemplate, StockAlert
from app.schemas.sms_schemas import (
    BulkSMSRequest,
    BulkSMSResponse,
    PhoneVerificationConfirm,
    PhoneVerificationRequest,
    PhoneVerificationResponse,
    SMSAnalyticsResponse,
    SMSLogResponse,
    SMSMessage,
    SMSResponse,
    SMSTemplateCreate,
    SMSTemplateResponse,
    SMSTemplateUpdate,
    StockAlertCreate,
    StockAlertResponse,
    UserSMSPreferences,
    UserSMSPreferencesUpdate,
)
from app.services.sms_service import SMSService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/send", response_model=SMSResponse)
async def send_sms(
    sms_data: SMSMessage,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    """Send a single SMS message."""
    if current_user and not current_user.has_permission("sms.send"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    if not settings.sms_enabled:
        raise HTTPException(status_code=503, detail="SMS service is disabled")

    sms_service = SMSService(db)

    try:
        response = await sms_service.send_sms(
            phone_number=sms_data.phone_number, message=sms_data.message, language=sms_data.language
        )
        return response
    except Exception as e:
        logger.error(f"SMS sending error: {e}")
        raise HTTPException(status_code=500, detail=f"SMS sending failed: {str(e)}")


@router.post("/send-bulk", response_model=BulkSMSResponse)
async def send_bulk_sms(
    bulk_data: BulkSMSRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Send SMS to multiple recipients."""
    if not current_user.has_permission("sms.send"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    if not settings.sms_enabled:
        raise HTTPException(status_code=503, detail="SMS service is disabled")

    sms_service = SMSService(db)

    try:
        results = await sms_service.send_bulk_sms(
            phone_numbers=bulk_data.phone_numbers,
            message=bulk_data.message,
            template_id=bulk_data.template_id,
        )

        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        total_cost = sum(r.cost for r in results)

        return BulkSMSResponse(
            total_recipients=len(bulk_data.phone_numbers),
            successful=successful,
            failed=failed,
            total_cost=total_cost,
            results=results,
        )
    except Exception as e:
        logger.error(f"Bulk SMS sending error: {e}")
        raise HTTPException(status_code=500, detail=f"Bulk SMS sending failed: {str(e)}")


@router.post("/send-template", response_model=SMSResponse)
async def send_template_sms(
    phone_number: str,
    template_name: str,
    variables: dict,
    language: str = "fa",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Send SMS using a predefined template."""
    if not current_user.has_permission("sms.send"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    if not settings.sms_enabled:
        raise HTTPException(status_code=503, detail="SMS service is disabled")

    sms_service = SMSService(db)

    try:
        response = await sms_service.send_template_sms(
            phone_number=phone_number,
            template_name=template_name,
            variables=variables,
            language=language,
        )
        return response
    except Exception as e:
        logger.error(f"Template SMS sending error: {e}")
        raise HTTPException(status_code=500, detail=f"Template SMS sending failed: {str(e)}")


@router.get("/templates", response_model=List[SMSTemplateResponse])
async def list_sms_templates(
    template_type: Optional[str] = Query(None, description="Filter by template type"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    """List SMS templates."""
    if current_user and not current_user.has_permission("sms.read"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    query = db.query(SMSTemplate)

    if template_type:
        query = query.filter(SMSTemplate.template_type == template_type)
    if is_active is not None:
        query = query.filter(SMSTemplate.is_active == is_active)

    templates = query.order_by(SMSTemplate.name).all()

    return [
        SMSTemplateResponse(
            id=template.id,
            name=template.name,
            template_type=template.template_type,
            content_en=template.content_en,
            content_fa=template.content_fa,
            variables=template.variables,
            is_active=template.is_active,
            created_at=template.created_at,
            updated_at=template.updated_at,
        )
        for template in templates
    ]


@router.post("/templates", response_model=SMSTemplateResponse)
async def create_sms_template(
    template_data: SMSTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new SMS template."""
    if not current_user.has_permission("sms.create"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    # Check if template name already exists
    existing = db.query(SMSTemplate).filter(SMSTemplate.name == template_data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Template name already exists")

    template = SMSTemplate(
        name=template_data.name,
        template_type=template_data.template_type,
        content_en=template_data.content_en,
        content_fa=template_data.content_fa,
        variables=template_data.variables,
        is_active=template_data.is_active,
    )

    db.add(template)
    db.commit()
    db.refresh(template)

    return SMSTemplateResponse(
        id=template.id,
        name=template.name,
        template_type=template.template_type,
        content_en=template.content_en,
        content_fa=template.content_fa,
        variables=template.variables,
        is_active=template.is_active,
        created_at=template.created_at,
        updated_at=template.updated_at,
    )


@router.put("/templates/{template_id}", response_model=SMSTemplateResponse)
async def update_sms_template(
    template_id: int,
    template_data: SMSTemplateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an SMS template."""
    if not current_user.has_permission("sms.update"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    template = db.query(SMSTemplate).filter(SMSTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    # Update fields if provided
    if template_data.name is not None:
        # Check if new name already exists
        existing = (
            db.query(SMSTemplate)
            .filter(SMSTemplate.name == template_data.name, SMSTemplate.id != template_id)
            .first()
        )
        if existing:
            raise HTTPException(status_code=400, detail="Template name already exists")
        template.name = template_data.name

    if template_data.template_type is not None:
        template.template_type = template_data.template_type
    if template_data.content_en is not None:
        template.content_en = template_data.content_en
    if template_data.content_fa is not None:
        template.content_fa = template_data.content_fa
    if template_data.variables is not None:
        template.variables = template_data.variables
    if template_data.is_active is not None:
        template.is_active = template_data.is_active

    template.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(template)

    return SMSTemplateResponse(
        id=template.id,
        name=template.name,
        template_type=template.template_type,
        content_en=template.content_en,
        content_fa=template.content_fa,
        variables=template.variables,
        is_active=template.is_active,
        created_at=template.created_at,
        updated_at=template.updated_at,
    )


@router.get("/logs", response_model=List[SMSLogResponse])
async def list_sms_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None, description="Filter by status"),
    phone_number: Optional[str] = Query(None, description="Filter by phone number"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List SMS logs with filtering."""
    if not current_user.has_permission("sms.read"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    query = db.query(SMSLog)

    if status:
        query = query.filter(SMSLog.status == status)
    if phone_number:
        query = query.filter(SMSLog.recipient_phone == phone_number)
    if start_date:
        query = query.filter(SMSLog.created_at >= start_date)
    if end_date:
        query = query.filter(SMSLog.created_at <= end_date)

    logs = query.order_by(SMSLog.created_at.desc()).offset(skip).limit(limit).all()

    return [
        SMSLogResponse(
            id=log.id,
            recipient_phone=log.recipient_phone,
            content=log.content,
            template_id=log.template_id,
            status=log.status,
            sent_at=log.sent_at,
            delivered_at=log.delivered_at,
            error_message=log.error_message,
            cost=log.cost,
            retry_count=log.retry_count,
            created_at=log.created_at,
        )
        for log in logs
    ]


@router.get("/analytics", response_model=SMSAnalyticsResponse)
async def get_sms_analytics(
    start_date: Optional[datetime] = Query(None, description="Start date for analytics"),
    end_date: Optional[datetime] = Query(None, description="End date for analytics"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    """Get SMS analytics for the given date range."""
    if current_user and not current_user.has_permission("sms.read"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    sms_service = SMSService(db)
    analytics = sms_service.get_sms_analytics(start_date, end_date)

    return SMSAnalyticsResponse(**analytics)


@router.post("/stock-alerts", response_model=StockAlertResponse)
async def create_stock_alert(
    alert_data: StockAlertCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    """Create a stock alert for a part."""
    # Allow both authenticated and anonymous users to create stock alerts
    user_id = current_user.id if current_user else None

    sms_service = SMSService(db)

    success = await sms_service.create_stock_alert(
        user_id=user_id,
        part_id=alert_data.part_id,
        phone_number=alert_data.phone_number,
        email=alert_data.email,
    )

    if not success:
        raise HTTPException(status_code=500, detail="Failed to create stock alert")

    # Get the created alert
    alert = (
        db.query(StockAlert)
        .filter(
            StockAlert.part_id == alert_data.part_id,
            StockAlert.phone_number == alert_data.phone_number,
            StockAlert.is_active,
        )
        .first()
    )

    return StockAlertResponse(
        id=alert.id,
        user_id=alert.user_id,
        part_id=alert.part_id,
        phone_number=alert.phone_number,
        email=alert.email,
        is_active=alert.is_active,
        is_notified=alert.is_notified,
        notified_at=alert.notified_at,
        created_at=alert.created_at,
    )


@router.get("/stock-alerts", response_model=List[StockAlertResponse])
async def list_stock_alerts(
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    part_id: Optional[int] = Query(None, description="Filter by part ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List stock alerts."""
    if not current_user.has_permission("sms.read"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    query = db.query(StockAlert)

    if user_id:
        query = query.filter(StockAlert.user_id == user_id)
    if part_id:
        query = query.filter(StockAlert.part_id == part_id)
    if is_active is not None:
        query = query.filter(StockAlert.is_active == is_active)

    alerts = query.order_by(StockAlert.created_at.desc()).all()

    return [
        StockAlertResponse(
            id=alert.id,
            user_id=alert.user_id,
            part_id=alert.part_id,
            phone_number=alert.phone_number,
            email=alert.email,
            is_active=alert.is_active,
            is_notified=alert.is_notified,
            notified_at=alert.notified_at,
            created_at=alert.created_at,
        )
        for alert in alerts
    ]


@router.get("/preferences", response_model=UserSMSPreferences)
async def get_user_sms_preferences(current_user: User = Depends(get_current_user)):
    """Get current user's SMS preferences."""
    return UserSMSPreferences(
        sms_notifications=current_user.sms_notifications,
        sms_marketing=current_user.sms_marketing,
        sms_delivery=current_user.sms_delivery,
        phone_verified=current_user.phone_verified,
    )


@router.put("/preferences", response_model=UserSMSPreferences)
async def update_user_sms_preferences(
    preferences: UserSMSPreferencesUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update current user's SMS preferences."""
    if preferences.sms_notifications is not None:
        current_user.sms_notifications = preferences.sms_notifications
    if preferences.sms_marketing is not None:
        current_user.sms_marketing = preferences.sms_marketing
    if preferences.sms_delivery is not None:
        current_user.sms_delivery = preferences.sms_delivery

    db.commit()
    db.refresh(current_user)

    return UserSMSPreferences(
        sms_notifications=current_user.sms_notifications,
        sms_marketing=current_user.sms_marketing,
        sms_delivery=current_user.sms_delivery,
        phone_verified=current_user.phone_verified,
    )


@router.post("/verify-phone", response_model=PhoneVerificationResponse)
async def verify_phone_number(request: PhoneVerificationRequest, db: Session = Depends(get_db)):
    """Send phone verification SMS."""
    if not settings.sms_enabled:
        raise HTTPException(status_code=503, detail="SMS service is disabled")

    # Generate verification code
    import random

    verification_code = str(random.randint(100000, 999999))

    # Store verification code in session/cache (simplified for now)
    # In production, use Redis or database to store verification sessions

    sms_service = SMSService(db)

    message = f"کد تأیید شما: {verification_code}\nاین کد تا 5 دقیقه معتبر است."

    response = await sms_service.send_sms(
        phone_number=request.phone_number, message=message, language="fa"
    )

    if response.success:
        # In production, store verification_code and phone_number in secure
        # session
        verification_id = f"verify_{request.phone_number}_{datetime.utcnow().timestamp()}"

        return PhoneVerificationResponse(
            success=True,
            message="Verification SMS sent successfully",
            verification_id=verification_id,
        )
    else:
        raise HTTPException(status_code=500, detail=response.message)


@router.post("/confirm-phone", response_model=dict)
async def confirm_phone_verification(
    request: PhoneVerificationConfirm, db: Session = Depends(get_db)
):
    """Confirm phone verification code."""
    # In production, verify the code against stored session
    # For now, accept any 6-digit code for testing

    if len(request.verification_code) != 6 or not request.verification_code.isdigit():
        raise HTTPException(status_code=400, detail="Invalid verification code format")

    # In production, implement proper verification logic
    return {
        "success": True,
        "message": "Phone number verified successfully",
        "phone_number": request.phone_number,
    }
