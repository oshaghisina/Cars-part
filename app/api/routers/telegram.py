"""
Telegram SSO API endpoints for bot integration and account linking.
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.db.models import User
from app.models.telegram_models import TelegramUser
from app.schemas.telegram_schemas import (
    TelegramBotSessionRequest,
    TelegramBotSessionResponse,
    TelegramDeepLinkRequest,
    TelegramDeepLinkResponse,
    TelegramDeepLinkVerifyRequest,
    TelegramDeepLinkVerifyResponse,
    TelegramLinkRequest,
    TelegramLinkResponse,
    TelegramLoginRequest,
    TelegramLoginResponse,
    TelegramStatsResponse,
    TelegramUnlinkRequest,
    TelegramUnlinkResponse,
    TelegramUserInfo,
    TelegramVerifyRequest,
    TelegramVerifyResponse,
    TelegramWebhookRequest,
    TelegramWebhookResponse,
)
from app.services.telegram_service import TelegramService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/link/request", response_model=TelegramLinkResponse)
async def request_telegram_link(
    request: TelegramLinkRequest,
    http_request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Request Telegram account linking.
    
    This endpoint creates a secure link token for linking a Telegram account
    to a platform user account.
    """
    try:
        telegram_service = TelegramService(db)
        
        # Get client IP and user agent
        client_ip = http_request.client.host if http_request.client else "unknown"
        user_agent = http_request.headers.get("user-agent", "unknown")
        
        # Get or create Telegram user
        telegram_user_info = await telegram_service.get_telegram_user_info(request.telegram_id)
        telegram_user = telegram_service.get_or_create_telegram_user(
            request.telegram_id, 
            telegram_user_info
        )
        
        # Check if already linked
        if telegram_user.is_linked:
            if current_user and telegram_user.user_id == current_user.id:
                return TelegramLinkResponse(
                    success=True,
                    message="Telegram account is already linked to your account",
                    telegram_url=f"https://t.me/{telegram_service.bot_username}"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Telegram account is already linked to another user"
                )
        
        # Create link token
        link_token = telegram_service.create_link_token(
            telegram_user=telegram_user,
            action=request.action,
            user_id=current_user.id if current_user else None,
            ip_address=client_ip,
            user_agent=user_agent
        )
        
        # Generate Telegram URL
        telegram_url = telegram_service.generate_telegram_link_url(telegram_user)
        
        logger.info(f"Created Telegram link token for user {request.telegram_id}")
        
        return TelegramLinkResponse(
            success=True,
            message="Telegram link token created successfully",
            link_token=link_token.token,
            telegram_url=telegram_url,
            expires_in=telegram_service.link_token_expiry_hours * 3600
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating Telegram link request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/link/verify", response_model=TelegramVerifyResponse)
async def verify_telegram_link(
    request: TelegramVerifyRequest,
    http_request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Verify Telegram link token and complete account linking.
    
    This endpoint verifies the link token and links the Telegram account
    to the platform user account.
    """
    try:
        telegram_service = TelegramService(db)
        
        # Verify link token
        link_token = telegram_service.verify_link_token(request.token, request.action)
        if not link_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired link token"
            )
        
        # Get Telegram user
        telegram_user = link_token.telegram_user
        
        # Check if already linked
        if telegram_user.is_linked:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Telegram account is already linked"
            )
        
        # Determine target user
        target_user_id = link_token.user_id or (current_user.id if current_user else None)
        if not target_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No target user specified for linking"
            )
        
        # Link accounts
        success = telegram_service.link_telegram_account(telegram_user, target_user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to link Telegram account"
            )
        
        # Mark token as used
        link_token.mark_used()
        db.commit()
        
        # Get platform user info
        platform_user = db.query(User).filter(User.id == target_user_id).first()
        
        # Prepare response data
        telegram_user_data = {
            "telegram_id": telegram_user.telegram_id,
            "username": telegram_user.username,
            "first_name": telegram_user.first_name,
            "last_name": telegram_user.last_name,
            "is_linked": telegram_user.is_linked,
            "linked_at": telegram_user.linked_at.isoformat() if telegram_user.linked_at else None
        }
        
        platform_user_data = {
            "id": platform_user.id,
            "username": platform_user.username,
            "email": platform_user.email,
            "role": platform_user.role
        } if platform_user else None
        
        logger.info(f"Successfully linked Telegram account {telegram_user.telegram_id} to user {target_user_id}")
        
        return TelegramVerifyResponse(
            success=True,
            message="Telegram account linked successfully",
            telegram_user=telegram_user_data,
            platform_user=platform_user_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying Telegram link: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/login", response_model=TelegramLoginResponse)
async def telegram_login(
    request: TelegramLoginRequest,
    http_request: Request,
    db: Session = Depends(get_db)
):
    """
    Authenticate user via Telegram.
    
    This endpoint authenticates a user using their Telegram account
    and returns a JWT token if successful.
    """
    try:
        telegram_service = TelegramService(db)
        
        # Get or create Telegram user
        telegram_user_info = await telegram_service.get_telegram_user_info(request.telegram_id)
        telegram_user = telegram_service.get_or_create_telegram_user(
            request.telegram_id,
            telegram_user_info or request.user_info.dict() if request.user_info else None
        )
        
        # Check if Telegram account is linked
        if not telegram_user.is_linked or not telegram_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Telegram account is not linked to any platform account"
            )
        
        # Get platform user
        platform_user = db.query(User).filter(User.id == telegram_user.user_id).first()
        if not platform_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Linked platform user not found"
            )
        
        # Check if user is active
        if not platform_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated"
            )
        
        # Check if account is locked
        if platform_user.is_locked():
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail="Account is temporarily locked"
            )
        
        # Create JWT token
        access_token = telegram_service.create_telegram_jwt_token(telegram_user)
        
        # Update last login
        from datetime import datetime
        platform_user.last_login = datetime.utcnow()
        platform_user.reset_login_attempts()
        db.commit()
        
        # Prepare response data
        user_data = {
            "id": platform_user.id,
            "username": platform_user.username,
            "email": platform_user.email,
            "first_name": platform_user.first_name,
            "last_name": platform_user.last_name,
            "role": platform_user.role,
            "is_active": platform_user.is_active,
            "is_verified": platform_user.is_verified,
            "last_login": platform_user.last_login.isoformat() if platform_user.last_login else None
        }
        
        telegram_user_data = {
            "telegram_id": telegram_user.telegram_id,
            "username": telegram_user.username,
            "first_name": telegram_user.first_name,
            "last_name": telegram_user.last_name,
            "is_linked": telegram_user.is_linked
        }
        
        logger.info(f"Telegram login successful for user {platform_user.username} ({platform_user.id})")
        
        return TelegramLoginResponse(
            success=True,
            message="Login successful",
            access_token=access_token,
            expires_in=30 * 60,  # 30 minutes
            user=user_data,
            telegram_user=telegram_user_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in Telegram login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/unlink", response_model=TelegramUnlinkResponse)
async def unlink_telegram_account(
    request: TelegramUnlinkRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Unlink Telegram account from platform user.
    
    This endpoint unlinks the Telegram account from the current user's account.
    """
    try:
        telegram_service = TelegramService(db)
        
        # Find Telegram user
        telegram_user = db.query(TelegramUser).filter(
            TelegramUser.telegram_id == request.telegram_id
        ).first()
        
        if not telegram_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Telegram account not found"
            )
        
        # Check if linked to current user
        if not telegram_user.is_linked or telegram_user.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Telegram account is not linked to your account"
            )
        
        # Unlink account
        success = telegram_service.unlink_telegram_account(telegram_user)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to unlink Telegram account"
            )
        
        logger.info(f"Successfully unlinked Telegram account {request.telegram_id} from user {current_user.id}")
        
        return TelegramUnlinkResponse(
            success=True,
            message="Telegram account unlinked successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error unlinking Telegram account: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/deep-link/create", response_model=TelegramDeepLinkResponse)
async def create_telegram_deep_link(
    request: TelegramDeepLinkRequest,
    http_request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Create a Telegram deep link for web to bot transitions.
    
    This endpoint creates a secure deep link that can be used to redirect
    users from the web interface to the Telegram bot.
    """
    try:
        telegram_service = TelegramService(db)
        
        # Get client IP and user agent
        client_ip = http_request.client.host if http_request.client else "unknown"
        user_agent = http_request.headers.get("user-agent", "unknown")
        
        # Get or create Telegram user
        telegram_user_info = await telegram_service.get_telegram_user_info(request.telegram_id)
        telegram_user = telegram_service.get_or_create_telegram_user(
            request.telegram_id,
            telegram_user_info
        )
        
        # Create deep link
        deep_link = telegram_service.create_deep_link(
            telegram_user=telegram_user,
            action=request.action,
            target_url=request.target_url,
            parameters=request.parameters,
            ip_address=client_ip,
            user_agent=user_agent
        )
        
        # Generate Telegram URL
        telegram_url = f"https://t.me/{telegram_service.bot_username}?start={deep_link.link_id}"
        
        logger.info(f"Created Telegram deep link for user {request.telegram_id}")
        
        return TelegramDeepLinkResponse(
            success=True,
            message="Telegram deep link created successfully",
            link_id=deep_link.link_id,
            telegram_url=telegram_url,
            expires_in=telegram_service.deep_link_expiry_hours * 3600
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating Telegram deep link: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/deep-link/verify", response_model=TelegramDeepLinkVerifyResponse)
async def verify_telegram_deep_link(
    request: TelegramDeepLinkVerifyRequest,
    db: Session = Depends(get_db)
):
    """
    Verify Telegram deep link and get link information.
    
    This endpoint verifies a deep link and returns the associated
    information for processing the link action.
    """
    try:
        telegram_service = TelegramService(db)
        
        # Verify deep link
        deep_link = telegram_service.verify_deep_link(request.link_id)
        if not deep_link:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired deep link"
            )
        
        # Mark link as used
        deep_link.mark_used()
        db.commit()
        
        # Prepare response data
        telegram_user_data = {
            "telegram_id": deep_link.telegram_user.telegram_id,
            "username": deep_link.telegram_user.username,
            "first_name": deep_link.telegram_user.first_name,
            "last_name": deep_link.telegram_user.last_name,
            "is_linked": deep_link.telegram_user.is_linked
        }
        
        parameters = {}
        if deep_link.parameters:
            import json
            parameters = json.loads(deep_link.parameters)
        
        logger.info(f"Verified Telegram deep link {request.link_id}")
        
        return TelegramDeepLinkVerifyResponse(
            success=True,
            message="Deep link verified successfully",
            telegram_user=telegram_user_data,
            action=deep_link.action,
            target_url=deep_link.target_url,
            parameters=parameters
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying Telegram deep link: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/stats", response_model=TelegramStatsResponse)
async def get_telegram_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get Telegram integration statistics.
    
    This endpoint requires admin privileges and returns statistics
    about Telegram user integration.
    """
    try:
        # Check admin privileges
        if not current_user.has_role("admin"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin privileges required"
            )
        
        telegram_service = TelegramService(db)
        stats = telegram_service.get_telegram_stats()
        
        return TelegramStatsResponse(**stats)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting Telegram stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/webhook", response_model=TelegramWebhookResponse)
async def telegram_webhook(
    request: TelegramWebhookRequest,
    db: Session = Depends(get_db)
):
    """
    Handle Telegram bot webhook updates.
    
    This endpoint processes incoming webhook updates from Telegram
    and handles bot interactions.
    """
    try:
        telegram_service = TelegramService(db)
        
        # Process webhook update
        processed = False
        message = "Webhook received"
        
        # Handle message updates
        if request.message:
            chat_id = request.message.get("chat", {}).get("id")
            text = request.message.get("text", "")
            
            if chat_id and text:
                # Get or create Telegram user
                telegram_user_info = await telegram_service.get_telegram_user_info(chat_id)
                telegram_user = telegram_service.get_or_create_telegram_user(
                    chat_id,
                    telegram_user_info
                )
                
                # Handle bot commands
                if text.startswith("/start"):
                    # Handle start command with deep link
                    if " " in text:
                        link_id = text.split(" ", 1)[1]
                        deep_link = telegram_service.verify_deep_link(link_id)
                        if deep_link:
                            # Process deep link action
                            if deep_link.action == "login":
                                await telegram_service.send_telegram_message(
                                    chat_id,
                                    "🔐 Login successful! You can now access your account."
                                )
                            elif deep_link.action == "link_account":
                                await telegram_service.send_telegram_message(
                                    chat_id,
                                    "🔗 Account linking initiated! Please complete the process on the web interface."
                                )
                            deep_link.mark_used()
                            db.commit()
                            processed = True
                    else:
                        # Regular start command
                        await telegram_service.send_telegram_message(
                            chat_id,
                            "👋 Welcome! Use /help to see available commands."
                        )
                        processed = True
                
                elif text == "/help":
                    help_text = """
🤖 **China Car Parts Bot Commands:**

/start - Start the bot
/help - Show this help message
/link - Link your Telegram account
/status - Check account status
/unlink - Unlink your account

For support, visit our website or contact customer service.
                    """
                    await telegram_service.send_telegram_message(chat_id, help_text)
                    processed = True
                
                elif text == "/status":
                    if telegram_user.is_linked:
                        status_text = f"""
✅ **Account Status:**
Linked: Yes
User ID: {telegram_user.user_id}
Linked at: {telegram_user.linked_at.strftime('%Y-%m-%d %H:%M') if telegram_user.linked_at else 'Unknown'}
                        """
                    else:
                        status_text = """
❌ **Account Status:**
Linked: No

Use /link to link your Telegram account to your platform account.
                        """
                    await telegram_service.send_telegram_message(chat_id, status_text)
                    processed = True
        
        # Handle callback queries
        elif request.callback_query:
            # Process callback query
            processed = True
        
        logger.info(f"Processed Telegram webhook update: {request.update_id}")
        
        return TelegramWebhookResponse(
            success=True,
            message=message,
            processed=processed
        )
        
    except Exception as e:
        logger.error(f"Error processing Telegram webhook: {e}")
        return TelegramWebhookResponse(
            success=False,
            message="Error processing webhook",
            processed=False,
            code="WEBHOOK_ERROR"
        )
