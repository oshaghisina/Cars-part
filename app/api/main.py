"""FastAPI main application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import app.api.routers.ai_search as ai_search_module
import app.api.routers.categories as categories_module
# import app.api.routers.parts as parts_module  # Temporarily disabled
import app.api.routers.vehicles as vehicles_module
import app.api.routers.wizard as wizard_module
from app.api.routers import (
    admin,
    analytics,
    auth,
    bulk_operations,
    images,
    leads,
    orders,
    otp,
    pdp,
    search,
    sms,
    telegram,
    users,
    vehicles_enhanced,
)
from app.api.routers.parts_public import router as parts_public_router
from app.api.routers.parts_admin import router as parts_admin_router
from app.core.config import settings
from app.db.database import Base, engine
from app.db.models import (  # noqa: F401; Ensure User model is loaded for foreign key relationships
    User,
)
from app.models.stock_models import (  # noqa: F401; Ensure stock models are loaded
    StockLevel,
    PartPrice,
)

# Conditionally import AI modules only if AI Gateway is enabled
if getattr(settings, "ai_gateway_enabled", False):
    from app.api.routers import ai_admin, ai_advanced, ai_chat

# Create FastAPI application
app = FastAPI(
    title="Chinese Auto Parts Price Bot API",
    description="API for Chinese car parts price lookup and order management",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# Add CORS middleware
cors_origins = [
    "http://localhost:5173",  # Admin panel
    "http://127.0.0.1:5173",
    "http://localhost:5174",  # Web portal
    "http://127.0.0.1:5174",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    # Production origins
    "http://5.223.41.154",  # Production HTTP
    "https://5.223.41.154",  # Production HTTPS
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def ensure_critical_tables():
    """Ensure critical tables (OTP, core app tables) and User columns exist on startup."""
    try:
        import logging

        from sqlalchemy import inspect, text

        logger = logging.getLogger(__name__)

        # Check if critical tables exist
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()

        critical_tables = [
            "otp_codes",
            "rate_limits",
            "phone_verifications",
            "parts",
            "part_categories",
            "prices",
            "synonyms",
            "order_items",
            "part_specifications",
            "part_images",
            "leads",
            "orders",
            "stock_levels",
            "prices_new",
        ]
        missing_tables = [table for table in critical_tables if table not in existing_tables]

        if missing_tables:
            logger.warning(f"Missing critical tables: {missing_tables}. Creating them...")

            # Import models to ensure they're registered with SQLAlchemy Base
            # Import core application models
            from app.db.models import (  # noqa: F401
                Lead,
                Order,
                OrderItem,
                Part,
                PartCategory,
                PartImage,
                PartSpecification,
                Price,
                Synonym,
            )
            from app.models.otp_models import (  # noqa: F401
                OTPCode,
                PhoneVerification,
                RateLimit,
            )
            from app.models.sms_models import (  # noqa: F401
                SMSLog,
                SMSTemplate,
                StockAlert,
            )
            from app.models.telegram_models import (  # noqa: F401
                TelegramBotSession,
                TelegramDeepLink,
                TelegramLinkToken,
                TelegramUser,
            )

            # Create missing tables
            Base.metadata.create_all(bind=engine)
            logger.info(f"Critical tables created successfully: {missing_tables}")
        else:
            logger.info("All critical tables exist")

        # Check if users table has required SMS columns
        if "users" in existing_tables:
            logger.info("Checking users table for required SMS columns...")

            # Get existing columns in users table
            user_columns = inspector.get_columns("users")
            existing_column_names = [col["name"] for col in user_columns]

            # Required SMS columns that should exist
            required_sms_columns = [
                "sms_notifications",
                "sms_marketing",
                "sms_delivery",
                "phone_verified",
            ]

            missing_columns = [
                col for col in required_sms_columns if col not in existing_column_names
            ]

            if missing_columns:
                logger.warning(
                    f"Missing SMS columns in users table: {missing_columns}. Adding them..."
                )

                # Add missing columns with proper defaults
                with engine.connect() as connection:
                    for column in missing_columns:
                        if column in ["sms_notifications", "sms_delivery", "phone_verified"]:
                            # These default to True/False based on column purpose
                            if column in ["sms_notifications", "sms_delivery"]:
                                default_value = "TRUE"
                            else:
                                default_value = "FALSE"
                            sql = (
                                f"ALTER TABLE users ADD COLUMN {column} "
                                f"BOOLEAN NOT NULL DEFAULT {default_value}"
                            )
                        elif column == "sms_marketing":
                            # Marketing defaults to False
                            sql = (
                                f"ALTER TABLE users ADD COLUMN {column} "
                                f"BOOLEAN NOT NULL DEFAULT FALSE"
                            )

                        try:
                            connection.execute(text(sql))
                            logger.info(f"Added column {column} to users table")
                        except Exception as col_error:
                            logger.error(f"Failed to add column {column}: {col_error}")

                    # Commit the changes
                    connection.commit()

                logger.info("SMS columns added successfully to users table")
            else:
                logger.info("All required SMS columns exist in users table")

    except Exception as e:
        logger.error(f"Failed to ensure critical tables and columns: {e}")


@app.get("/health")
async def health_check():
    """Basic health check endpoint (minimal payload)."""
    return {"status": "healthy"}


app.include_router(search.router, prefix="/api/v1/search", tags=["search"])
app.include_router(bulk_operations.router, prefix="/api/v1/bulk", tags=["bulk-operations"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])
app.include_router(ai_search_module.router, prefix="/api/v1/ai-search", tags=["ai-search"])
app.include_router(wizard_module.router, prefix="/api/v1/wizard", tags=["wizard"])
app.include_router(orders.router, prefix="/api/v1/orders", tags=["orders"])
app.include_router(leads.router, prefix="/api/v1/leads", tags=["leads"])
# app.include_router(parts_module.router, prefix="/api/v1/parts", tags=["parts"])
# Temporarily disabled
app.include_router(parts_public_router, prefix="/api/v1/parts", tags=["parts-public"])
app.include_router(parts_admin_router, prefix="/api/v1/admin/parts", tags=["parts-admin"])
app.include_router(vehicles_module.router, prefix="/api/v1/vehicles", tags=["vehicles"])
app.include_router(categories_module.router, prefix="/api/v1/categories", tags=["categories"])
app.include_router(vehicles_enhanced.router, prefix="/api/v1", tags=["vehicles-enhanced"])
app.include_router(pdp.router, prefix="/api/v1", tags=["pdp"])
app.include_router(images.router, prefix="/api/v1", tags=["images"])
app.include_router(sms.router, prefix="/api/v1/sms", tags=["sms"])
app.include_router(otp.router, prefix="/api/v1/otp", tags=["otp"])
app.include_router(telegram.router, prefix="/api/v1/telegram", tags=["telegram"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])

# Include AI routers only if AI Gateway is enabled
if getattr(settings, "ai_gateway_enabled", False):
    # Include AI advanced router for Epic E3 features
    app.include_router(ai_advanced.router, prefix="/api/v1", tags=["ai-advanced"])

    # Include AI chat router
    app.include_router(ai_chat.router, prefix="/api/v1", tags=["ai-chat"])

    # Include AI admin router only if experimental mode is enabled
    if getattr(settings, "ai_gateway_experimental", False):
        app.include_router(ai_admin.router, prefix="/api/v1", tags=["ai-admin"])


@app.get("/api/v1/health")
async def api_health_check():
    """Versioned health check endpoint used by CI/CD and monitors."""
    return {
        "status": "healthy",
        "app_env": settings.app_env,
        "debug": settings.debug,
        "version": "1.0.0",
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Chinese Auto Parts Price Bot API",
        "version": "1.0.0",
        "docs": "/docs" if settings.debug else "Documentation disabled in production",
    }
