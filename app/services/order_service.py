"""Order service for managing orders and order items."""

from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.db.models import Order, OrderItem


class OrderService:
    """Service for managing orders."""

    def __init__(self, db: Session):
        self.db = db

    def create_order(self, lead_id: int, order_items: List[Dict]) -> Dict:
        """
        Create a new order with order items.

        Args:
            lead_id: ID of the lead/customer
            order_items: List of order item dictionaries

        Returns:
            Dictionary with order information and status
        """
        try:
            # Create the order
            new_order = Order(
                lead_id=lead_id, status="new", notes="Order created via Telegram bot"
            )

            self.db.add(new_order)
            self.db.flush()  # Get the order ID

            # Create order items
            for line_no, item in enumerate(order_items, 1):
                order_item = OrderItem(
                    order_id=new_order.id,
                    line_no=line_no,
                    query_text=item["query_text"],
                    matched_part_id=item.get("matched_part_id"),
                    qty=item.get("qty", 1),
                    unit=item.get("unit", "pcs"),
                    notes=item.get("notes", ""),
                )

                self.db.add(order_item)

            self.db.commit()
            self.db.refresh(new_order)

            return {
                "success": True,
                "order": new_order,
                "message": f"سفارش شما با موفقیت ثبت شد. شماره سفارش: #ORD-{new_order.id:05d}",
            }

        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "message": "خطایی در ثبت سفارش رخ داد. لطفاً دوباره تلاش کنید.",
                "error": str(e),
            }

    def get_order_by_id(self, order_id: int) -> Optional[Order]:
        """Get order by ID with order items."""
        return self.db.query(Order).filter(Order.id == order_id).first()

    def get_orders_by_lead(self, lead_id: int) -> List[Order]:
        """Get all orders for a lead."""
        return (
            self.db.query(Order)
            .filter(Order.lead_id == lead_id)
            .order_by(Order.created_at.desc())
            .all()
        )

    def update_order_status(
        self, order_id: int, status: str, notes: str = None
    ) -> Dict:
        """Update order status."""
        order = self.db.query(Order).filter(Order.id == order_id).first()

        if not order:
            return {"success": False, "message": "Order not found"}

        order.status = status
        if notes:
            order.notes = notes

        self.db.commit()

        return {"success": True, "message": "Order status updated", "order": order}

    def get_order_summary(self, order: Order) -> Dict:
        """Get formatted order summary."""
        order_items = (
            self.db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
        )

        total_items = len(order_items)
        matched_items = sum(1 for item in order_items if item.matched_part_id)

        return {
            "order_id": order.id,
            "status": order.status,
            "created_at": order.created_at,
            "total_items": total_items,
            "matched_items": matched_items,
            "items": [
                {
                    "line_no": item.line_no,
                    "query_text": item.query_text,
                    "matched_part_id": item.matched_part_id,
                    "qty": item.qty,
                    "unit": item.unit,
                    "notes": item.notes,
                }
                for item in order_items
            ],
        }
