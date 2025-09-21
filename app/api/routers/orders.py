"""Orders API endpoints."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Order
from app.services.order_service import OrderService

router = APIRouter()


class OrderItemResponse(BaseModel):
    """Response model for order item."""

    line_no: int
    query_text: str
    matched_part_id: Optional[int]
    qty: int
    unit: str
    notes: Optional[str]


class OrderResponse(BaseModel):
    """Response model for order data."""

    id: int
    lead_id: int
    status: str
    notes: Optional[str]
    created_at: str
    updated_at: str
    items: List[OrderItemResponse]


class OrderCreateRequest(BaseModel):
    """Request model for creating an order."""

    lead_id: int
    items: List[dict]  # List of order item dictionaries


class OrderUpdateRequest(BaseModel):
    """Request model for updating an order."""

    status: Optional[str] = None
    notes: Optional[str] = None


@router.get("/", response_model=List[OrderResponse])
async def list_orders(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
):
    """List all orders with pagination and status filtering."""
    query = db.query(Order)

    if status:
        query = query.filter(Order.status == status)

    orders = query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()

    order_service = OrderService(db)
    result = []

    for order in orders:
        summary = order_service.get_order_summary(order)
        result.append(
            OrderResponse(
                id=order.id,
                lead_id=order.lead_id,
                status=order.status,
                notes=order.notes,
                created_at=order.created_at.isoformat(),
                updated_at=order.updated_at.isoformat(),
                items=[
                    OrderItemResponse(
                        line_no=item["line_no"],
                        query_text=item["query_text"],
                        matched_part_id=item["matched_part_id"],
                        qty=item["qty"],
                        unit=item["unit"],
                        notes=item["notes"],
                    )
                    for item in summary["items"]
                ],
            )
        )

    return result


@router.post("/", response_model=OrderResponse)
async def create_order(request: OrderCreateRequest, db: Session = Depends(get_db)):
    """Create a new order."""
    order_service = OrderService(db)

    result = order_service.create_order(
        lead_id=request.lead_id, order_items=request.items
    )

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])

    order = result["order"]
    summary = order_service.get_order_summary(order)

    return OrderResponse(
        id=order.id,
        lead_id=order.lead_id,
        status=order.status,
        notes=order.notes,
        created_at=order.created_at.isoformat(),
        updated_at=order.updated_at.isoformat(),
        items=[
            OrderItemResponse(
                line_no=item["line_no"],
                query_text=item["query_text"],
                matched_part_id=item["matched_part_id"],
                qty=item["qty"],
                unit=item["unit"],
                notes=item["notes"],
            )
            for item in summary["items"]
        ],
    )


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int, db: Session = Depends(get_db)):
    """Get order by ID."""
    order_service = OrderService(db)
    order = order_service.get_order_by_id(order_id)

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    summary = order_service.get_order_summary(order)

    return OrderResponse(
        id=order.id,
        lead_id=order.lead_id,
        status=order.status,
        notes=order.notes,
        created_at=order.created_at.isoformat(),
        updated_at=order.updated_at.isoformat(),
        items=[
            OrderItemResponse(
                line_no=item["line_no"],
                query_text=item["query_text"],
                matched_part_id=item["matched_part_id"],
                qty=item["qty"],
                unit=item["unit"],
                notes=item["notes"],
            )
            for item in summary["items"]
        ],
    )


@router.put("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: int, request: OrderUpdateRequest, db: Session = Depends(get_db)
):
    """Update order by ID."""
    order_service = OrderService(db)

    result = order_service.update_order_status(
        order_id=order_id, status=request.status, notes=request.notes
    )

    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["message"])

    order = result["order"]
    summary = order_service.get_order_summary(order)

    return OrderResponse(
        id=order.id,
        lead_id=order.lead_id,
        status=order.status,
        notes=order.notes,
        created_at=order.created_at.isoformat(),
        updated_at=order.updated_at.isoformat(),
        items=[
            OrderItemResponse(
                line_no=item["line_no"],
                query_text=item["query_text"],
                matched_part_id=item["matched_part_id"],
                qty=item["qty"],
                unit=item["unit"],
                notes=item["notes"],
            )
            for item in summary["items"]
        ],
    )
