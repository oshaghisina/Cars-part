"""Application configuration management."""

from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_env: str = "development"
    debug: bool = True

    # Database
    database_url: str = "sqlite:///./data/app.db"

    # Telegram Bot
    telegram_bot_token: str = "CHANGEME"
    telegram_webhook_url: Optional[str] = None
    admin_telegram_ids: str = "176007160"

    # AI Search
    ai_enabled: bool = True
    ai_model_path: Optional[str] = None
    ai_api_key: Optional[str] = None

    # OpenAI Configuration
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-3.5-turbo"
    openai_embedding_model: str = "text-embedding-3-small"
    openai_max_tokens: int = 1000
    openai_temperature: float = 0.3

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    frontend_origin: str = "http://localhost:5173,http://127.0.0.1:5173"

    # Security
    secret_key: str = "CHANGEME_GENERATE_A_SECURE_SECRET_KEY"
    jwt_secret_key: str = "your-secret-key-change-this-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30

    # Rate Limiting
    rate_limit_per_minute: int = 60
    rate_limit_burst: int = 10

    # Logging
    log_level: str = "INFO"
    log_file: Optional[str] = None

    # Admin Panel
    admin_panel_enabled: bool = True
    admin_panel_port: int = 3000

    # Features
    bulk_limit_default: int = 10
    maintenance_mode: bool = False

    # Email settings (for notifications)
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_from_email: Optional[str] = None

    # Redis settings (for caching)
    redis_url: str = "redis://localhost:6379/0"

    @property
    def admin_telegram_ids_list(self) -> List[int]:
        """Parse admin telegram IDs from comma-separated string."""
        return [int(id.strip()) for id in self.admin_telegram_ids.split(",") if id.strip()]

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
