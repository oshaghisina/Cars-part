"""Settings management service."""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.models import Setting
import logging

logger = logging.getLogger(__name__)


class SettingsService:
    """Service for managing system settings."""

    def __init__(self, db: Session):
        self.db = db

    def get_setting(self, key: str) -> Optional[str]:
        """Get a single setting value."""
        setting = self.db.query(Setting).filter(Setting.key == key).first()
        return setting.value if setting else None  # type: ignore[return-value]

    def get_settings(self, keys: Optional[list] = None) -> Dict[str, str]:
        """Get multiple settings."""
        query = self.db.query(Setting)

        if keys:
            query = query.filter(Setting.key.in_(keys))

        settings = query.all()
        # type: ignore[misc]
        return {setting.key: setting.value for setting in settings}

    def set_setting(self, key: str, value: str, updated_by: Optional[int] = None) -> Setting:
        """Set a setting value."""
        setting = self.db.query(Setting).filter(Setting.key == key).first()

        if setting:
            setting.value = value  # type: ignore[assignment]
            setting.updated_at = func.now()  # type: ignore[assignment]
            setting.updated_by = updated_by  # type: ignore[assignment]
        else:
            setting = Setting(key=key, value=value, updated_by=updated_by)
            self.db.add(setting)

        self.db.commit()
        self.db.refresh(setting)

        logger.info(f"Setting updated: {key} = {value}")
        return setting

    def set_settings(
        self, settings: Dict[str, str], updated_by: Optional[int] = None
    ) -> Dict[str, str]:
        """Set multiple settings."""
        results = {}

        for key, value in settings.items():
            results[key] = self.set_setting(key, value, updated_by).value

        return results

    def get_system_settings(self) -> Dict[str, Any]:
        """Get common system settings with proper types."""
        raw_settings = self.get_settings(
            [
                "AI_ENABLED",
                "BULK_LIMIT_DEFAULT",
                "MAX_UPLOAD_SIZE",
                "SESSION_TIMEOUT",
                "MAINTENANCE_MODE",
                "BACKUP_ENABLED",
                "BACKUP_INTERVAL_HOURS",
            ]
        )

        # Convert to appropriate types
        system_settings = {}

        # Boolean settings
        bool_keys = ["AI_ENABLED", "MAINTENANCE_MODE", "BACKUP_ENABLED"]
        for key in bool_keys:
            if key in raw_settings:
                system_settings[key] = raw_settings[key].lower() in ("true", "1", "yes", "on")

        # Integer settings
        int_keys = [
            "BULK_LIMIT_DEFAULT",
            "MAX_UPLOAD_SIZE",
            "SESSION_TIMEOUT",
            "BACKUP_INTERVAL_HOURS",
        ]
        for key in int_keys:
            if key in raw_settings:
                try:
                    system_settings[key] = int(raw_settings[key])
                except (ValueError, TypeError):
                    system_settings[key] = 0

        return system_settings

    def initialize_default_settings(self):
        """Initialize default system settings if they don't exist."""
        default_settings = {
            "AI_ENABLED": "true",
            "BULK_LIMIT_DEFAULT": "10",
            "MAX_UPLOAD_SIZE": "10485760",  # 10MB
            "SESSION_TIMEOUT": "86400",  # 24 hours
            "MAINTENANCE_MODE": "false",
            "BACKUP_ENABLED": "true",
            "BACKUP_INTERVAL_HOURS": "24",
        }

        for key, value in default_settings.items():
            if not self.get_setting(key):
                self.set_setting(key, value)

        logger.info("Default settings initialized")
