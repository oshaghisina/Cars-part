from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func, text
from datetime import datetime, timedelta

from app.db.database import get_db
from app.db.models import Part, VehicleBrand, VehicleModel, VehicleTrim, PartCategory, Order, Lead, User
from app.schemas.search_schemas import (
    SearchRequest, SearchResponse, SearchResult,
    AdvancedSearchRequest, AdvancedSearchResponse,
    GlobalSearchRequest, GlobalSearchResponse
)

router = APIRouter()


@router.post("/advanced", response_model=AdvancedSearchResponse)
async def advanced_search(
    search_request: AdvancedSearchRequest,
    db: Session = Depends(get_db)
):
    """
    Perform advanced search across multiple modules with filters
    """
    try:
        results = []
        total_count = 0

        # Search in each selected module
        for module in search_request.modules:
            module_results, module_count = await search_module(
                module, search_request, db
            )
            results.extend(module_results)
            total_count += module_count

        # Apply global filters
        if search_request.filters:
            results = apply_global_filters(results, search_request.filters)

        # Sort results
        if search_request.sort_by:
            results = sort_results(
                results,
                search_request.sort_by,
                search_request.sort_order)

        # Paginate results
        start = search_request.page * search_request.per_page
        end = start + search_request.per_page
        paginated_results = results[start:end]

        return AdvancedSearchResponse(
            results=paginated_results,
            total_count=len(results),
            page=search_request.page,
            per_page=search_request.per_page,
            total_pages=(
                len(results) +
                search_request.per_page -
                1) //
            search_request.per_page)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


@router.post("/global", response_model=GlobalSearchResponse)
async def global_search(
    search_request: GlobalSearchRequest,
    db: Session = Depends(get_db)
):
    """
    Perform global search across all modules
    """
    try:
        query = search_request.query.lower()
        results = []

        # Search across all modules
        modules = ['vehicles', 'parts', 'orders', 'leads', 'users']

        for module in modules:
            module_results = await search_module_global(module, query, db)
            results.extend(module_results)

        # Sort by relevance and limit results
        results = sorted(
            results,
            key=lambda x: x.relevance_score,
            reverse=True)
        results = results[:search_request.limit]

        return GlobalSearchResponse(
            results=results,
            total_count=len(results),
            query=search_request.query
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Global search error: {str(e)}")


@router.get("/suggestions")
async def get_search_suggestions(
    q: str = Query(..., min_length=2),
    module: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get search suggestions for autocomplete
    """
    try:
        query = q.lower()
        suggestions = []

        # Get suggestions from different modules
        if not module or module == 'parts':
            parts = db.query(Part).filter(
                or_(
                    func.lower(Part.part_name).contains(query),
                    func.lower(Part.brand_oem).contains(query),
                    func.lower(Part.oem_code).contains(query)
                )
            ).limit(5).all()

            for part in parts:
                suggestions.append({
                    'text': part.part_name,
                    'type': 'part',
                    'id': part.id,
                    'description': f"{part.brand_oem} - {part.oem_code}"
                })

        if not module or module == 'vehicles':
            brands = db.query(VehicleBrand).filter(
                func.lower(VehicleBrand.name).contains(query)
            ).limit(3).all()

            for brand in brands:
                suggestions.append({
                    'text': brand.name,
                    'type': 'brand',
                    'id': brand.id,
                    'description': 'Vehicle Brand'
                })

        if not module or module == 'categories':
            categories = db.query(PartCategory).filter(
                func.lower(PartCategory.name).contains(query)
            ).limit(3).all()

            for category in categories:
                suggestions.append({
                    'text': category.name,
                    'type': 'category',
                    'id': category.id,
                    'description': 'Part Category'
                })

        return {'suggestions': suggestions}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Suggestions error: {str(e)}")


async def search_module(
        module: str,
        search_request: AdvancedSearchRequest,
        db: Session):
    """
    Search within a specific module
    """
    results = []
    count = 0

    if module == 'parts':
        query = db.query(Part)

        # Apply text search
        if search_request.query:
            text_filter = or_(
                func.lower(
                    Part.part_name).contains(
                    search_request.query.lower()),
                func.lower(
                    Part.brand_oem).contains(
                    search_request.query.lower()),
                func.lower(
                    Part.oem_code).contains(
                    search_request.query.lower()),
                func.lower(
                    Part.description).contains(
                    search_request.query.lower()))
            query = query.filter(text_filter)

        # Apply filters
        if search_request.filters:
            if search_request.filters.category:
                query = query.filter(
                    Part.category_id == search_request.filters.category)
            if search_request.filters.status:
                query = query.filter(
                    Part.status == search_request.filters.status)
            if search_request.filters.price_min:
                query = query.filter(
                    Part.price >= search_request.filters.price_min)
            if search_request.filters.price_max:
                query = query.filter(
                    Part.price <= search_request.filters.price_max)

        count = query.count()
        parts = query.all()

        for part in parts:
            results.append(SearchResult(
                id=str(part.id),
                module='parts',
                title=part.part_name,
                description=f"{part.brand_oem} - {part.oem_code}",
                type='Part',
                url=f"/parts/{part.id}",
                metadata={
                    'category': part.category.name if part.category else None,
                    'price': float(part.price) if part.price else None,
                    'status': part.status,
                    'created_at': part.created_at.isoformat() if part.created_at else None
                },
                relevance_score=1.0
            ))

    elif module == 'vehicles':
        query = db.query(VehicleBrand)

        if search_request.query:
            text_filter = func.lower(
                VehicleBrand.name).contains(
                search_request.query.lower())
            query = query.filter(text_filter)

        count = query.count()
        brands = query.all()

        for brand in brands:
            results.append(SearchResult(
                id=str(brand.id),
                module='vehicles',
                title=brand.name,
                description=f"Vehicle brand with {len(brand.models)} models",
                type='Vehicle Brand',
                url=f"/vehicles/brands/{brand.id}",
                metadata={
                    'model_count': len(brand.models),
                    'created_at': brand.created_at.isoformat() if brand.created_at else None
                },
                relevance_score=1.0
            ))

    elif module == 'orders':
        query = db.query(Order)

        if search_request.query:
            text_filter = or_(
                func.lower(
                    Order.customer_name).contains(
                    search_request.query.lower()),
                func.lower(
                    Order.customer_phone).contains(
                    search_request.query.lower()),
                func.lower(
                    Order.notes).contains(
                    search_request.query.lower()))
            query = query.filter(text_filter)

        if search_request.filters:
            if search_request.filters.status:
                query = query.filter(
                    Order.status == search_request.filters.status)
            if search_request.filters.date_from:
                query = query.filter(
                    Order.created_at >= search_request.filters.date_from)
            if search_request.filters.date_to:
                query = query.filter(
                    Order.created_at <= search_request.filters.date_to)

        count = query.count()
        orders = query.all()

        for order in orders:
            results.append(SearchResult(
                id=str(order.id),
                module='orders',
                title=f"Order #{order.id}",
                description=f"{order.customer_name} - {order.status}",
                type='Order',
                url=f"/orders/{order.id}",
                metadata={
                    'status': order.status,
                    'total': float(order.total) if order.total else None,
                    'created_at': order.created_at.isoformat() if order.created_at else None
                },
                relevance_score=1.0
            ))

    elif module == 'leads':
        query = db.query(Lead)

        if search_request.query:
            text_filter = or_(
                func.lower(
                    Lead.first_name).contains(
                    search_request.query.lower()),
                func.lower(
                    Lead.last_name).contains(
                    search_request.query.lower()),
                func.lower(
                    Lead.phone_e164).contains(
                    search_request.query.lower()),
                func.lower(
                    Lead.city).contains(
                    search_request.query.lower()))
            query = query.filter(text_filter)

        count = query.count()
        leads = query.all()

        for lead in leads:
            results.append(SearchResult(
                id=str(lead.id),
                module='leads',
                title=f"{lead.first_name} {lead.last_name}",
                description=f"{lead.city} - {lead.phone_e164}",
                type='Lead',
                url=f"/leads/{lead.id}",
                metadata={
                    'city': lead.city,
                    'phone': lead.phone_e164,
                    'created_at': lead.created_at.isoformat() if lead.created_at else None
                },
                relevance_score=1.0
            ))

    elif module == 'users':
        query = db.query(User)

        if search_request.query:
            text_filter = or_(
                func.lower(
                    User.username).contains(
                    search_request.query.lower()),
                func.lower(
                    User.email).contains(
                    search_request.query.lower()),
                func.lower(
                    User.first_name).contains(
                    search_request.query.lower()),
                func.lower(
                    User.last_name).contains(
                    search_request.query.lower()))
            query = query.filter(text_filter)

        count = query.count()
        users = query.all()

        for user in users:
            results.append(SearchResult(
                id=str(user.id),
                module='users',
                title=f"{user.first_name} {user.last_name}",
                description=f"{user.username} - {user.role}",
                type='User',
                url=f"/users/{user.id}",
                metadata={
                    'username': user.username,
                    'email': user.email,
                    'role': user.role,
                    'created_at': user.created_at.isoformat() if user.created_at else None
                },
                relevance_score=1.0
            ))

    return results, count


async def search_module_global(module: str, query: str, db: Session):
    """
    Global search within a specific module
    """
    results = []

    if module == 'parts':
        parts = db.query(Part).filter(
            or_(
                func.lower(Part.part_name).contains(query),
                func.lower(Part.brand_oem).contains(query),
                func.lower(Part.oem_code).contains(query)
            )
        ).limit(10).all()

        for part in parts:
            results.append(SearchResult(
                id=str(part.id),
                module='parts',
                title=part.part_name,
                description=f"{part.brand_oem} - {part.oem_code}",
                type='Part',
                url=f"/parts/{part.id}",
                metadata={'category': part.category.name if part.category else None},
                relevance_score=1.0
            ))

    # Similar implementations for other modules...

    return results


def apply_global_filters(results: List[SearchResult], filters):
    """
    Apply global filters to search results
    """
    filtered_results = []

    for result in results:
        include = True

        # Date range filter
        if filters.date_from or filters.date_to:
            if 'created_at' in result.metadata:
                created_at = datetime.fromisoformat(
                    result.metadata['created_at'].replace('Z', '+00:00'))
                if filters.date_from and created_at.date() < filters.date_from:
                    include = False
                if filters.date_to and created_at.date() > filters.date_to:
                    include = False

        # Price range filter
        if filters.price_min or filters.price_max:
            if 'price' in result.metadata and result.metadata['price']:
                price = result.metadata['price']
                if filters.price_min and price < filters.price_min:
                    include = False
                if filters.price_max and price > filters.price_max:
                    include = False

        if include:
            filtered_results.append(result)

    return filtered_results


def sort_results(results: List[SearchResult], sort_by: str, sort_order: str):
    """Sort search results"""
    reverse = sort_order == 'desc'

    if sort_by == 'relevance':
        return sorted(
            results,
            key=lambda x: x.relevance_score,
            reverse=reverse)
    elif sort_by == 'title':
        return sorted(results, key=lambda x: x.title.lower(), reverse=reverse)
    elif sort_by == 'created_at':
        return sorted(
            results,
            key=lambda x: x.metadata.get(
                'created_at',
                ''),
            reverse=reverse)

    return results
