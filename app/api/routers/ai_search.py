"""AI-enhanced search API endpoints."""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from app.db.database import get_db
from app.services.ai_service import AIService
from app.core.config import settings

router = APIRouter()


class IntelligentSearchResponse(BaseModel):
    """Response model for intelligent search."""

    success: bool
    parts: List[Dict[str, Any]]
    query_analysis: Optional[Dict[str, Any]]
    suggestions: List[str]
    search_type: str
    error: Optional[str] = None


class BulkIntelligentSearchRequest(BaseModel):
    """Request model for bulk intelligent search."""

    queries: List[str]
    limit_per_query: int = 5


class BulkIntelligentSearchResponse(BaseModel):
    """Response model for bulk intelligent search."""

    results: List[Dict[str, Any]]


class PartRecommendationResponse(BaseModel):
    """Response model for part recommendations."""

    recommendations: List[Dict[str, Any]]


@router.get("/intelligent", response_model=IntelligentSearchResponse)
async def intelligent_search(
    q: str = Query(..., description="Search query"),
    limit: int = Query(10, description="Maximum number of results"),
    db: Session = Depends(get_db),
):
    """Perform intelligent search with AI-powered query understanding."""
    if not q.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    if not settings.ai_enabled:
        raise HTTPException(
            status_code=503,
            detail="AI search is disabled. Please enable AI_ENABLED in configuration.",
        )

    try:
        ai_service = AIService(db)
        if not ai_service.is_available():
            raise HTTPException(
                status_code=503,
                detail="AI service is not available. Please check OpenAI API key configuration.",
            )

        result = ai_service.intelligent_search(q, limit)
        return IntelligentSearchResponse(**result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI search failed: {str(e)}")


@router.post("/intelligent/bulk", response_model=BulkIntelligentSearchResponse)
async def bulk_intelligent_search(
    request: BulkIntelligentSearchRequest, db: Session = Depends(get_db)
):
    """Perform bulk intelligent search for multiple queries."""
    if not request.queries:
        raise HTTPException(status_code=400, detail="Queries list cannot be empty")

    if len(request.queries) > 20:  # Bulk limit
        raise HTTPException(status_code=400, detail="Too many queries (max 20)")

    if not settings.ai_enabled:
        raise HTTPException(
            status_code=503,
            detail="AI search is disabled. Please enable AI_ENABLED in configuration.",
        )

    try:
        ai_service = AIService(db)
        if not ai_service.is_available():
            raise HTTPException(
                status_code=503,
                detail="AI service is not available. Please check OpenAI API key configuration.",
            )

        results = ai_service.bulk_intelligent_search(request.queries, request.limit_per_query)
        return BulkIntelligentSearchResponse(results=results)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bulk AI search failed: {str(e)}")


@router.get("/recommendations/{part_id}", response_model=PartRecommendationResponse)
async def get_part_recommendations(
    part_id: int,
    limit: int = Query(5, description="Maximum number of recommendations"),
    db: Session = Depends(get_db),
):
    """Get AI-powered part recommendations based on a specific part."""
    if not settings.ai_enabled:
        raise HTTPException(
            status_code=503,
            detail="AI search is disabled. Please enable AI_ENABLED in configuration.",
        )

    try:
        ai_service = AIService(db)
        if not ai_service.is_available():
            raise HTTPException(
                status_code=503,
                detail="AI service is not available. Please check OpenAI API key configuration.",
            )

        recommendations = ai_service.get_part_recommendations(part_id, limit)
        return PartRecommendationResponse(recommendations=recommendations)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")


@router.get("/semantic", response_model=List[Dict[str, Any]])
async def semantic_search(
    q: str = Query(..., description="Search query"),
    limit: int = Query(10, description="Maximum number of results"),
    db: Session = Depends(get_db),
):
    """Perform semantic search using OpenAI embeddings."""
    if not q.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    if not settings.ai_enabled:
        raise HTTPException(
            status_code=503,
            detail="AI search is disabled. Please enable AI_ENABLED in configuration.",
        )

    try:
        ai_service = AIService(db)
        if not ai_service.is_available():
            raise HTTPException(
                status_code=503,
                detail="AI service is not available. Please check OpenAI API key configuration.",
            )

        results = ai_service.semantic_search(q, limit)
        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Semantic search failed: {str(e)}")


@router.get("/status")
async def ai_status():
    """Check AI service status and configuration."""
    return {
        "ai_enabled": settings.ai_enabled,
        "openai_configured": bool(settings.openai_api_key),
        "openai_model": settings.openai_model,
        "embedding_model": settings.openai_embedding_model,
        "max_tokens": settings.openai_max_tokens,
        "temperature": settings.openai_temperature,
    }
