from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from datetime import date, datetime


class SearchFilters(BaseModel):
    """Search filters for advanced search"""

    date_from: Optional[date] = None
    date_to: Optional[date] = None
    status: Optional[str] = None
    category: Optional[int] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    quantity_min: Optional[int] = None
    quantity_max: Optional[int] = None


class SearchRequest(BaseModel):
    """Basic search request"""

    query: str = Field(..., min_length=1, max_length=255)
    modules: List[str] = Field(
        default_factory=lambda: ["parts", "vehicles", "orders", "leads", "users"]
    )
    page: int = Field(default=0, ge=0)
    per_page: int = Field(default=25, ge=1, le=100)


class AdvancedSearchRequest(BaseModel):
    """Advanced search request with filters"""

    query: Optional[str] = None
    modules: List[str] = Field(
        default_factory=lambda: ["parts", "vehicles", "orders", "leads", "users"]
    )
    filters: Optional[SearchFilters] = None
    sort_by: Optional[Literal["relevance", "title", "created_at"]] = "relevance"
    sort_order: Optional[Literal["asc", "desc"]] = "desc"
    page: int = Field(default=0, ge=0)
    per_page: int = Field(default=25, ge=1, le=100)


class GlobalSearchRequest(BaseModel):
    """Global search request"""

    query: str = Field(..., min_length=1, max_length=255)
    limit: int = Field(default=50, ge=1, le=100)


class SearchResult(BaseModel):
    """Individual search result"""

    id: str
    module: str
    title: str
    description: str
    type: str
    url: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    relevance_score: float = Field(default=1.0, ge=0.0, le=1.0)


class SearchResponse(BaseModel):
    """Basic search response"""

    results: List[SearchResult]
    total_count: int
    page: int
    per_page: int
    total_pages: int


class AdvancedSearchResponse(BaseModel):
    """Advanced search response"""

    results: List[SearchResult]
    total_count: int
    page: int
    per_page: int
    total_pages: int
    applied_filters: Optional[SearchFilters] = None
    sort_by: Optional[str] = None
    sort_order: Optional[str] = None


class GlobalSearchResponse(BaseModel):
    """Global search response"""

    results: List[SearchResult]
    total_count: int
    query: str


class SearchSuggestion(BaseModel):
    """Search suggestion for autocomplete"""

    text: str
    type: str
    id: int
    description: Optional[str] = None


class SearchSuggestionsResponse(BaseModel):
    """Search suggestions response"""

    suggestions: List[SearchSuggestion]
