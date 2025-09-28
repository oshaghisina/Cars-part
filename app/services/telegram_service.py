"""
Telegram SSO service for bot integration and account linking.
"""

import hashlib
import json
import logging
import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional

import httpx
from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.telegram_models import (
    TelegramBotSession,
    TelegramDeepLink,
    TelegramLinkToken,
    TelegramUser,
)
from app.services.jwt_service import jwt_service

logger = logging.getLogger(__name__)


class TelegramService:
    """Service for managing Telegram SSO and bot interactions."""

    def __init__(self, db: Session):
        self.db = db
        self.bot_token = getattr(settings, "telegram_bot_token", None)
        self.bot_username = getattr(settings, "telegram_bot_username", None)
        self.web_app_url = getattr(settings, "web_app_url", "http://localhost:5174")
        self.admin_panel_url = getattr(settings, "admin_panel_url", "http://localhost:5173")

        # Token expiry times
        self.link_token_expiry_hours = 1
        self.deep_link_expiry_hours = 1
        self.session_expiry_hours = 24

    def hash_token(self, token: str) -> str:
        """Hash token for secure storage."""
        salt = secrets.token_hex(16)
        hash_value = hashlib.pbkdf2_hmac(
            "sha256", token.encode("utf-8"), salt.encode("utf-8"), 100000
        ).hex()
        return f"{salt}:{hash_value}"

    def verify_token(self, token: str, hashed_token: str) -> bool:
        """Verify token against hash."""
        try:
            salt, stored_hash = hashed_token.split(":", 1)
            computed_hash = hashlib.pbkdf2_hmac(
                "sha256", token.encode("utf-8"), salt.encode("utf-8"), 100000
            ).hex()
            return computed_hash == stored_hash
        except (ValueError, AttributeError):
            return False

    async def get_telegram_user_info(self, telegram_id: int) -> Optional[Dict]:
        """Get Telegram user information from Telegram API."""
        if not self.bot_token or self.bot_token == "CHANGEME":
            logger.warning("Telegram bot token not configured")
            return None

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"https://api.telegram.org/bot{self.bot_token}/getChat",
                    params={"chat_id": telegram_id},
                )

                if response.status_code == 200:
                    data = response.json()
                    if data.get("ok"):
                        return data.get("result")
                    else:
                        logger.warning(f"Telegram API error: {data.get('description')}")
                        return None
                else:
                    logger.error(f"Telegram API request failed: {response.status_code}")
                    return None

        except Exception as e:
            logger.error(f"Error getting Telegram user info: {e}")
            return None

    def get_or_create_telegram_user(self, telegram_id: int, user_info: Dict = None) -> TelegramUser:
        """Get or create Telegram user record."""
        telegram_user = (
            self.db.query(TelegramUser).filter(TelegramUser.telegram_id == telegram_id).first()
        )

        if not telegram_user:
            # Create new Telegram user
            telegram_user = TelegramUser(
                telegram_id=telegram_id,
                username=user_info.get("username") if user_info else None,
                first_name=user_info.get("first_name") if user_info else None,
                last_name=user_info.get("last_name") if user_info else None,
                language_code=user_info.get("language_code") if user_info else None,
                is_bot=user_info.get("is_bot", False) if user_info else False,
                is_premium=user_info.get("is_premium", False) if user_info else False,
            )
            self.db.add(telegram_user)
            self.db.flush()
        else:
            # Update existing user info
            if user_info:
                telegram_user.username = user_info.get("username")
                telegram_user.first_name = user_info.get("first_name")
                telegram_user.last_name = user_info.get("last_name")
                telegram_user.language_code = user_info.get("language_code")
                telegram_user.is_bot = user_info.get("is_bot", False)
                telegram_user.is_premium = user_info.get("is_premium", False)
                telegram_user.updated_at = func.now()

        # Update activity
        telegram_user.update_activity()
        self.db.commit()

        return telegram_user

    def create_link_token(
        self,
        telegram_user: TelegramUser,
        action: str = "link_account",
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> TelegramLinkToken:
        """Create a secure link token for account linking."""
        # Generate token and nonce
        token = TelegramLinkToken.generate_token()
        nonce = TelegramLinkToken.generate_nonce()

        # Create token record
        link_token = TelegramLinkToken(
            token=token,
            token_hash=self.hash_token(token),
            telegram_user_id=telegram_user.id,
            user_id=user_id,
            expires_at=datetime.utcnow() + timedelta(hours=self.link_token_expiry_hours),
            nonce=nonce,
            ip_address=ip_address,
            user_agent=user_agent,
            action=action,
        )

        self.db.add(link_token)
        self.db.commit()

        return link_token

    def verify_link_token(
        self, token: str, action: str = "link_account"
    ) -> Optional[TelegramLinkToken]:
        """Verify and retrieve link token."""
        # Find token by hash
        for link_token in (
            self.db.query(TelegramLinkToken)
            .filter(
                and_(
                    TelegramLinkToken.action == action,
                    TelegramLinkToken.is_used.is_(False),
                    TelegramLinkToken.expires_at > func.now(),
                )
            )
            .all()
        ):
            if self.verify_token(token, link_token.token_hash):
                return link_token

        return None

    def create_deep_link(
        self,
        telegram_user: TelegramUser,
        action: str,
        target_url: str,
        parameters: Dict = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> TelegramDeepLink:
        """Create a deep link for Telegram to web transitions."""
        link_id = TelegramDeepLink.generate_link_id()
        nonce = TelegramDeepLink.generate_link_id()  # Using same method for nonce

        deep_link = TelegramDeepLink(
            link_id=link_id,
            telegram_user_id=telegram_user.id,
            action=action,
            target_url=target_url,
            parameters=json.dumps(parameters) if parameters else None,
            nonce=nonce,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=datetime.utcnow() + timedelta(hours=self.deep_link_expiry_hours),
        )

        self.db.add(deep_link)
        self.db.commit()

        return deep_link

    def verify_deep_link(self, link_id: str) -> Optional[TelegramDeepLink]:
        """Verify and retrieve deep link."""
        deep_link = (
            self.db.query(TelegramDeepLink)
            .filter(
                and_(
                    TelegramDeepLink.link_id == link_id,
                    TelegramDeepLink.is_used.is_(False),
                    TelegramDeepLink.expires_at > func.now(),
                )
            )
            .first()
        )

        return deep_link

    def link_telegram_account(self, telegram_user: TelegramUser, user_id: int) -> bool:
        """Link Telegram account to platform user account."""
        try:
            # Check if Telegram user is already linked
            if telegram_user.is_linked and telegram_user.user_id:
                logger.warning(
                    f"Telegram user {telegram_user.telegram_id} "
                    f"already linked to user {telegram_user.user_id}"
                )
                return False

            # Check if platform user already has Telegram account
            existing_telegram = (
                self.db.query(TelegramUser)
                .filter(and_(TelegramUser.user_id == user_id, TelegramUser.is_linked.is_(True)))
                .first()
            )

            if existing_telegram:
                logger.warning(f"User {user_id} already has linked Telegram account")
                return False

            # Link accounts
            telegram_user.user_id = user_id
            telegram_user.is_linked = True
            telegram_user.linked_at = func.now()
            telegram_user.update_activity()

            self.db.commit()

            logger.info(
                f"Successfully linked Telegram user {telegram_user.telegram_id} "
                f"to platform user {user_id}"
            )
            return True

        except Exception as e:
            logger.error(f"Error linking Telegram account: {e}")
            self.db.rollback()
            return False

    def unlink_telegram_account(self, telegram_user: TelegramUser) -> bool:
        """Unlink Telegram account from platform user."""
        try:
            telegram_user.user_id = None
            telegram_user.is_linked = False
            telegram_user.linked_at = None
            telegram_user.update_activity()

            self.db.commit()

            logger.info(f"Successfully unlinked Telegram user {telegram_user.telegram_id}")
            return True

        except Exception as e:
            logger.error(f"Error unlinking Telegram account: {e}")
            self.db.rollback()
            return False

    def create_bot_session(
        self, telegram_user: TelegramUser, state: str = "idle", context: Dict = None
    ) -> TelegramBotSession:
        """Create or update bot session."""
        # Find existing session
        session = (
            self.db.query(TelegramBotSession)
            .filter(
                and_(
                    TelegramBotSession.telegram_user_id == telegram_user.id,
                    TelegramBotSession.expires_at > func.now(),
                )
            )
            .first()
        )

        if session:
            # Update existing session
            session.state = state
            if context:
                session.context = json.dumps(context)
            session.extend_session(self.session_expiry_hours)
        else:
            # Create new session
            session = TelegramBotSession(
                telegram_user_id=telegram_user.id,
                session_id=secrets.token_urlsafe(16),
                state=state,
                context=json.dumps(context) if context else None,
                expires_at=datetime.utcnow() + timedelta(hours=self.session_expiry_hours),
            )
            self.db.add(session)

        self.db.commit()
        return session

    def get_bot_session(self, telegram_user: TelegramUser) -> Optional[TelegramBotSession]:
        """Get active bot session for Telegram user."""
        return (
            self.db.query(TelegramBotSession)
            .filter(
                and_(
                    TelegramBotSession.telegram_user_id == telegram_user.id,
                    TelegramBotSession.expires_at > func.now(),
                )
            )
            .first()
        )

    def generate_telegram_login_url(
        self, telegram_user: TelegramUser, action: str = "login"
    ) -> str:
        """Generate Telegram login URL for web authentication."""
        deep_link = self.create_deep_link(
            telegram_user=telegram_user,
            action=action,
            target_url=f"{self.web_app_url}/auth/telegram/callback",
            parameters={"action": action},
        )

        # Create Telegram login URL
        if self.bot_username and self.bot_username != "CHANGEME":
            login_url = f"https://t.me/{self.bot_username}?start={deep_link.link_id}"
        else:
            login_url = f"https://t.me/your_bot?start={deep_link.link_id}"
        return login_url

    def generate_telegram_link_url(self, telegram_user: TelegramUser) -> str:
        """Generate Telegram account linking URL."""
        deep_link = self.create_deep_link(
            telegram_user=telegram_user,
            action="link_account",
            target_url=f"{self.web_app_url}/auth/telegram/link",
            parameters={"action": "link_account"},
        )

        if self.bot_username and self.bot_username != "CHANGEME":
            link_url = f"https://t.me/{self.bot_username}?start={deep_link.link_id}"
        else:
            link_url = f"https://t.me/your_bot?start={deep_link.link_id}"
        return link_url

    async def send_telegram_message(
        self, telegram_id: int, message: str, parse_mode: str = "HTML"
    ) -> bool:
        """Send message to Telegram user."""
        if not self.bot_token or self.bot_token == "CHANGEME":
            logger.warning("Telegram bot token not configured")
            return False

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(
                    f"https://api.telegram.org/bot{self.bot_token}/sendMessage",
                    json={"chat_id": telegram_id, "text": message, "parse_mode": parse_mode},
                )

                if response.status_code == 200:
                    data = response.json()
                    return data.get("ok", False)
                else:
                    logger.error(f"Failed to send Telegram message: {response.status_code}")
                    return False

        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
            return False

    def create_telegram_jwt_token(self, telegram_user: TelegramUser) -> str:
        """Create JWT token for authenticated Telegram user."""
        if not telegram_user.is_linked or not telegram_user.user_id:
            raise ValueError("Telegram user must be linked to platform account")

        # Get platform user
        from app.db.models import User

        user = self.db.query(User).filter(User.id == telegram_user.user_id).first()
        if not user:
            raise ValueError("Linked platform user not found")

        # Create JWT token
        token_data = {
            "sub": str(user.id),
            "user_id": user.id,
            "username": user.username,
            "role": user.role,
            "telegram_id": telegram_user.telegram_id,
            "auth_method": "telegram",
        }

        return jwt_service.create_access_token(token_data)

    def cleanup_expired_tokens(self):
        """Clean up expired tokens and sessions."""
        try:
            # Clean up expired link tokens
            expired_tokens = (
                self.db.query(TelegramLinkToken)
                .filter(TelegramLinkToken.expires_at < func.now())
                .all()
            )

            for token in expired_tokens:
                self.db.delete(token)

            # Clean up expired deep links
            expired_links = (
                self.db.query(TelegramDeepLink)
                .filter(TelegramDeepLink.expires_at < func.now())
                .all()
            )

            for link in expired_links:
                self.db.delete(link)

            # Clean up expired sessions
            expired_sessions = (
                self.db.query(TelegramBotSession)
                .filter(TelegramBotSession.expires_at < func.now())
                .all()
            )

            for session in expired_sessions:
                self.db.delete(session)

            if expired_tokens or expired_links or expired_sessions:
                self.db.commit()
                logger.info(
                    f"Cleaned up {len(expired_tokens)} tokens, "
                    f"{len(expired_links)} links, {len(expired_sessions)} sessions"
                )

        except Exception as e:
            logger.error(f"Error cleaning up expired Telegram data: {e}")
            self.db.rollback()

    def get_telegram_stats(self) -> Dict:
        """Get Telegram integration statistics."""
        try:
            total_telegram_users = self.db.query(TelegramUser).count()
            linked_users = (
                self.db.query(TelegramUser).filter(TelegramUser.is_linked.is_(True)).count()
            )
            active_sessions = (
                self.db.query(TelegramBotSession)
                .filter(TelegramBotSession.expires_at > func.now())
                .count()
            )

            return {
                "total_telegram_users": total_telegram_users,
                "linked_users": linked_users,
                "unlinked_users": total_telegram_users - linked_users,
                "active_sessions": active_sessions,
                "link_rate": (
                    (linked_users / total_telegram_users * 100) if total_telegram_users > 0 else 0
                ),
            }

        except Exception as e:
            logger.error(f"Error getting Telegram stats: {e}")
            return {
                "total_telegram_users": 0,
                "linked_users": 0,
                "unlinked_users": 0,
                "active_sessions": 0,
                "link_rate": 0,
            }
