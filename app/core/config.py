"""Application configuration management."""

from typing import List, Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_env: str = "development"
    debug: bool = True

    # Database
    database_url: str = "sqlite:///./data/app.db"

    # Telegram Bot
    telegram_bot_token: str = "CHANGEME"
    telegram_bot_username: str = "CHANGEME"
    telegram_webhook_url: Optional[str] = None
    admin_telegram_ids: str = "176007160"

    # Telegram SSO
    telegram_sso_enabled: bool = True
    telegram_link_token_expiry_hours: int = 1
    telegram_deep_link_expiry_hours: int = 1
    telegram_session_expiry_hours: int = 24

    # AI Search (Legacy)
    ai_enabled: bool = True
    ai_model_path: Optional[str] = None
    ai_api_key: Optional[str] = None

    # AI Gateway Configuration
    ai_gateway_enabled: bool = True
    ai_gateway_experimental: bool = False
    ai_gateway_primary_provider: str = "openai"
    ai_gateway_fallback_providers: str = "stub"
    ai_gateway_timeout: int = 30
    ai_gateway_max_retries: int = 3
    ai_gateway_circuit_breaker_threshold: int = 5
    ai_gateway_circuit_breaker_timeout: int = 60

    # AI Gateway Advanced Configuration
    ai_fallback_enabled: bool = True
    ai_fallback_order: str = "openai,stub"
    ai_log_prompts_masked: bool = True
    ai_rate_limit_per_user: int = 20
    ai_budget_daily: int = 20

    # OpenAI Configuration
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-3.5-turbo"
    openai_embedding_model: str = "text-embedding-3-small"
    openai_max_tokens: int = 1000
    openai_temperature: float = 0.3
    openai_timeout: int = 30
    openai_max_retries: int = 3
    openai_requests_per_minute: int = 60
    openai_tokens_per_minute: int = 40000

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    frontend_origin: str = "http://localhost:5173,http://127.0.0.1:5173"

    # Security
    secret_key: str = "CHANGEME_GENERATE_A_SECURE_SECRET_KEY"
    jwt_secret_key: str = "your-secret-key-change-this-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    
    # Cache Configuration
    redis_url: str = "redis://localhost:6379/0"
    cache_enabled: bool = True
    cache_ttl: int = 300  # 5 minutes default
    cache_part_detail_ttl: int = 1  # 1 second for updated parts
    cache_part_list_ttl: int = 300  # 5 minutes for part lists
    
    # Real-time Configuration
    websocket_enabled: bool = True
    websocket_heartbeat_seconds: int = 30
    websocket_max_connections: int = 1000
    
    # Performance SLA
    part_detail_freshness_seconds: int = 1
    max_response_time_ms: int = 500
    
    # Concurrency Control
    optimistic_locking_enabled: bool = True
    max_retry_attempts: int = 3
    lock_timeout_seconds: int = 30
    
    # CDN Configuration
    cdn_enabled: bool = False
    cdn_provider: str = "cloudflare"  # cloudflare, cloudfront, none
    cdn_zone_id: Optional[str] = None
    cdn_api_token: Optional[str] = None

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

    # SMS Service Configuration (Melipayamak)
    sms_enabled: bool = True
    melipayamak_username: str = "CHANGEME"
    melipayamak_password: str = "CHANGEME"
    sms_sender_number: str = "5000..."
    sms_default_language: str = "fa"  # fa for Persian, en for English
    sms_rate_limit_per_hour: int = 100
    sms_max_retries: int = 3
    sms_retry_delay: int = 60  # seconds
    # Allow simulating SMS sends even in production (temporary fallback)
    sms_fallback_in_production: bool = False

    # Web Application URLs
    web_app_url: str = "http://localhost:5174"
    admin_panel_url: str = "http://localhost:5173"

    @property
    def admin_telegram_ids_list(self) -> List[int]:
        """Parse admin telegram IDs from comma-separated string."""
        return [int(id.strip()) for id in self.admin_telegram_ids.split(",") if id.strip()]

    @property
    def ai_gateway_fallback_providers_list(self) -> List[str]:
        """Parse AI Gateway fallback providers from comma-separated string."""
        return [
            provider.strip()
            for provider in self.ai_gateway_fallback_providers.split(",")
            if provider.strip()
        ]

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
