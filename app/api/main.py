"""FastAPI main application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routers import search, orders, leads, users, bulk_operations, analytics, admin
import app.api.routers.parts as parts_module
import app.api.routers.ai_search as ai_search_module
import app.api.routers.wizard as wizard_module
import app.api.routers.vehicles as vehicles_module
import app.api.routers.categories as categories_module

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
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)


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
app.include_router(parts_module.router, prefix="/api/v1/parts", tags=["parts"])
app.include_router(vehicles_module.router, prefix="/api/v1/vehicles", tags=["vehicles"])
app.include_router(categories_module.router, prefix="/api/v1/categories", tags=["categories"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])


@app.get("/api/v1/health")
async def api_health_check():
    """Versioned health check endpoint used by CI/CD and monitors."""
    return {
        "status": "healthy",
        "app_env": settings.app_env,
        "debug": settings.debug,
        "version": "1.0.0"
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Chinese Auto Parts Price Bot API",
        "version": "1.0.0",
        "docs": "/docs" if settings.debug else "Documentation disabled in production"
    }
