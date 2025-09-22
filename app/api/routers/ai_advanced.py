"""
AI Advanced API Router - Epic E3 Features

This router provides API endpoints for advanced AI features including:
- Hybrid Search
- Smart Recommendations
- Natural Language Query Processing
- Language Analysis
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.auth import get_current_user
from app.db.models import User
from app.services.ai_orchestrator import AIOrchestrator
from app.services.ai_orchestrator_e3 import AIOrchestratorE3Extensions
from app.schemas.search_schemas import SearchRequest, SearchResponse, SearchResult

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["AI Advanced"])

# Initialize AI components
ai_orchestrator = AIOrchestrator()
ai_orchestrator.initialize()
e3_extensions = AIOrchestratorE3Extensions(ai_orchestrator)


@router.post("/hybrid-search", response_model=Dict[str, Any])
async def hybrid_search(
    query: str,
    search_type: str = Query("hybrid", description="Search type: hybrid, semantic, keyword, filter"),
    limit: int = Query(20, description="Maximum number of results"),
    filters: Optional[Dict[str, Any]] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Perform hybrid search combining multiple search methods.
    """
    try:
        # Get parts from database (simplified - in production, you'd want proper filtering)
        from app.db.models import Part
        parts_query = db.query(Part).limit(1000)  # Limit for performance
        parts_data = []
        
        for part in parts_query:
            parts_data.append({
                "id": part.id,
                "part_name": part.part_name,
                "brand_oem": part.brand_oem,
                "vehicle_make": part.vehicle_make,
                "vehicle_model": part.vehicle_model,
                "category": part.category,
                "price": float(part.price) if part.price else None,
                "availability": part.availability,
                "description": part.description
            })
        
        # Perform hybrid search
        results = await e3_extensions.hybrid_search(
            query=query,
            parts=parts_data,
            filters=filters,
            search_type=search_type,
            limit=limit,
            user_id=str(current_user.id)
        )
        
        return {
            "success": True,
            "query": query,
            "search_type": search_type,
            "results": results,
            "total_results": len(results),
            "filters_applied": filters or {}
        }
        
    except Exception as e:
        logger.error(f"Error in hybrid search: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.post("/recommendations/{part_id}", response_model=Dict[str, Any])
async def get_smart_recommendations(
    part_id: int,
    recommendation_types: Optional[List[str]] = Query(None, description="Types of recommendations"),
    limit: int = Query(5, description="Maximum number of recommendations"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get AI-powered smart recommendations for a specific part.
    """
    try:
        # Get part data from database
        from app.db.models import Part
        part = db.query(Part).filter(Part.id == part_id).first()
        
        if not part:
            raise HTTPException(status_code=404, detail="Part not found")
        
        part_data = {
            "id": part.id,
            "part_name": part.part_name,
            "brand_oem": part.brand_oem,
            "vehicle_make": part.vehicle_make,
            "vehicle_model": part.vehicle_model,
            "category": part.category,
            "price": float(part.price) if part.price else None,
            "availability": part.availability,
            "description": part.description
        }
        
        # Get user profile (simplified - in production, you'd build this from user data)
        user_profile = {
            "purchase_history": [],  # Would be populated from actual purchase data
            "search_history": [],    # Would be populated from actual search data
            "preferences": {},
            "vehicle_info": None
        }
        
        # Get recommendations
        recommendations = await e3_extensions.get_smart_recommendations(
            part_id=part_id,
            part_data=part_data,
            user_profile=user_profile,
            recommendation_types=recommendation_types,
            limit=limit,
            user_id=str(current_user.id)
        )
        
        return {
            "success": True,
            "part_id": part_id,
            "part_name": part.part_name,
            "recommendations": recommendations,
            "total_recommendations": len(recommendations),
            "recommendation_types": recommendation_types or ["all"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")


@router.post("/query-analysis", response_model=Dict[str, Any])
async def analyze_natural_language_query(
    query: str,
    current_user: User = Depends(get_current_user)
):
    """
    Analyze natural language query with advanced understanding.
    """
    try:
        # Process the query
        analysis = await e3_extensions.process_natural_language_query(
            query=query,
            user_id=str(current_user.id)
        )
        
        return analysis
        
    except Exception as e:
        logger.error(f"Error analyzing query: {e}")
        raise HTTPException(status_code=500, detail=f"Query analysis failed: {str(e)}")


@router.post("/language-analysis", response_model=Dict[str, Any])
async def analyze_language(
    text: str,
    current_user: User = Depends(get_current_user)
):
    """
    Analyze text for language detection and entity extraction.
    """
    try:
        # Analyze the text
        analysis = e3_extensions.get_language_analysis(text)
        
        return analysis
        
    except Exception as e:
        logger.error(f"Error analyzing language: {e}")
        raise HTTPException(status_code=500, detail=f"Language analysis failed: {str(e)}")


@router.get("/search-suggestions", response_model=Dict[str, Any])
async def get_search_suggestions(
    query: str = Query(..., description="Search query for suggestions"),
    limit: int = Query(5, description="Maximum number of suggestions"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get search suggestions based on query and available parts.
    """
    try:
        # Get parts from database for suggestions
        from app.db.models import Part
        parts_query = db.query(Part).limit(500)  # Limit for performance
        parts_data = []
        
        for part in parts_query:
            parts_data.append({
                "id": part.id,
                "part_name": part.part_name,
                "brand_oem": part.brand_oem,
                "vehicle_make": part.vehicle_make,
                "vehicle_model": part.vehicle_model,
                "category": part.category
            })
        
        # Get suggestions using hybrid search engine
        suggestions = e3_extensions.hybrid_search_engine.get_search_suggestions(
            query=query,
            parts=parts_data,
            limit=limit
        )
        
        return {
            "success": True,
            "query": query,
            "suggestions": suggestions,
            "total_suggestions": len(suggestions)
        }
        
    except Exception as e:
        logger.error(f"Error getting search suggestions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get suggestions: {str(e)}")


@router.get("/ai-status", response_model=Dict[str, Any])
async def get_ai_status(
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive AI Gateway status including Epic E3 components.
    """
    try:
        # Get AI status from orchestrator
        status = ai_orchestrator.get_ai_status()
        
        # Add Epic E3 specific status
        status["epic_e3"] = {
            "language_processor": "active",
            "hybrid_search": "active",
            "recommendations_engine": "active",
            "query_processor": "active"
        }
        
        return status
        
    except Exception as e:
        logger.error(f"Error getting AI status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get AI status: {str(e)}")


@router.post("/intelligent-search", response_model=Dict[str, Any])
async def intelligent_search(
    query: str,
    limit: int = Query(20, description="Maximum number of results"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Perform intelligent search with query understanding and hybrid search.
    """
    try:
        # First, analyze the query
        query_analysis = await e3_extensions.process_natural_language_query(
            query=query,
            user_id=str(current_user.id)
        )
        
        if not query_analysis.get("success", False):
            raise HTTPException(status_code=400, detail="Query analysis failed")
        
        # Get parts from database
        from app.db.models import Part
        parts_query = db.query(Part).limit(1000)
        parts_data = []
        
        for part in parts_query:
            parts_data.append({
                "id": part.id,
                "part_name": part.part_name,
                "brand_oem": part.brand_oem,
                "vehicle_make": part.vehicle_make,
                "vehicle_model": part.vehicle_model,
                "category": part.category,
                "price": float(part.price) if part.price else None,
                "availability": part.availability,
                "description": part.description
            })
        
        # Perform hybrid search using analyzed query
        search_results = await e3_extensions.hybrid_search(
            query=query,
            parts=parts_data,
            filters=query_analysis.get("filters", {}),
            search_type="hybrid",
            limit=limit,
            user_id=str(current_user.id)
        )
        
        return {
            "success": True,
            "query": query,
            "query_analysis": query_analysis,
            "search_results": search_results,
            "total_results": len(search_results),
            "search_type": "intelligent"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in intelligent search: {e}")
        raise HTTPException(status_code=500, detail=f"Intelligent search failed: {str(e)}")
