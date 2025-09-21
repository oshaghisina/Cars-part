from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from typing import Optional
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta

from app.db.database import get_db
from app.db.models import (
    Part,
    VehicleBrand,
    VehicleModel,
    VehicleTrim,
    PartCategory,
    Order,
    OrderItem,
    Lead,
    User,
    Price,
    WizardSession,
)
from app.schemas.analytics_schemas import (
    DashboardMetrics,
    SalesAnalytics,
    InventoryAnalytics,
    CustomerAnalytics,
    PerformanceMetrics,
    ReportRequest,
    ReportResponse,
    ChartData,
    TimeSeriesData,
)

router = APIRouter()


@router.get("/dashboard/metrics", response_model=DashboardMetrics)
async def get_dashboard_metrics(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    """
    Get comprehensive dashboard metrics
    """
    try:
        # Set default date range if not provided
        if not date_to:
            date_to = date.today()
        if not date_from:
            date_from = date_to - timedelta(days=30)

        # Calculate date filters
        date_filter = and_(
            func.date(Part.created_at) >= date_from,
            func.date(Part.created_at) <= date_to,
        )

        # Total Parts
        total_parts = db.query(Part).count()
        active_parts = db.query(Part).filter(Part.status == "active").count()

        # Total Vehicles
        total_brands = db.query(VehicleBrand).count()
        total_models = db.query(VehicleModel).count()
        total_trims = db.query(VehicleTrim).count()

        # Categories
        total_categories = db.query(PartCategory).count()

        # Orders
        total_orders = db.query(Order).filter(date_filter).count()
        pending_orders = (
            db.query(Order).filter(and_(Order.status == "pending", date_filter)).count()
        )
        completed_orders = (
            db.query(Order)
            .filter(and_(Order.status == "completed", date_filter))
            .count()
        )

        # Revenue (calculate from order items and prices)
        total_revenue = (
            db.query(func.sum(OrderItem.qty * Price.price))
            .join(Part, OrderItem.matched_part_id == Part.id)
            .join(Price, Part.id == Price.part_id)
            .join(Order, OrderItem.order_id == Order.id)
            .filter(and_(Order.status == "completed", date_filter))
            .scalar()
            or 0
        )

        # Leads
        total_leads = db.query(Lead).filter(date_filter).count()
        new_leads = (
            db.query(Lead)
            .filter(and_(func.date(Lead.created_at) >= date_from, date_filter))
            .count()
        )

        # Users
        total_users = db.query(User).count()
        active_users = db.query(User).filter(User.is_active).count()

        return DashboardMetrics(
            total_parts=total_parts,
            active_parts=active_parts,
            total_vehicles=total_brands + total_models + total_trims,
            total_categories=total_categories,
            total_orders=total_orders,
            pending_orders=pending_orders,
            completed_orders=completed_orders,
            total_revenue=float(total_revenue),
            total_leads=total_leads,
            new_leads=new_leads,
            total_users=total_users,
            active_users=active_users,
            date_range={"from": date_from.isoformat(), "to": date_to.isoformat()},
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching dashboard metrics: {str(e)}"
        )


@router.get("/sales/analytics", response_model=SalesAnalytics)
async def get_sales_analytics(
    period: str = Query("30d", regex="^(7d|30d|90d|1y)$"), db: Session = Depends(get_db)
):
    """
    Get sales analytics for the specified period
    """
    try:
        # Calculate date range based on period
        end_date = date.today()
        if period == "7d":
            start_date = end_date - timedelta(days=7)
        elif period == "30d":
            start_date = end_date - timedelta(days=30)
        elif period == "90d":
            start_date = end_date - timedelta(days=90)
        elif period == "1y":
            start_date = end_date - relativedelta(years=1)

        # Revenue trends (calculate from order items and prices)
        revenue_trends = (
            db.query(
                func.date(Order.created_at).label("date"),
                func.sum(OrderItem.qty * Price.price).label("revenue"),
                func.count(Order.id).label("orders"),
            )
            .join(OrderItem, Order.id == OrderItem.order_id)
            .join(Part, OrderItem.matched_part_id == Part.id)
            .join(Price, Part.id == Price.part_id)
            .filter(
                and_(
                    func.date(Order.created_at) >= start_date,
                    func.date(Order.created_at) <= end_date,
                    Order.status == "completed",
                )
            )
            .group_by(func.date(Order.created_at))
            .order_by("date")
            .all()
        )

        # Order status distribution
        status_distribution = (
            db.query(Order.status, func.count(Order.id).label("count"))
            .filter(
                and_(
                    func.date(Order.created_at) >= start_date,
                    func.date(Order.created_at) <= end_date,
                )
            )
            .group_by(Order.status)
            .all()
        )

        # Top customers by revenue (using lead name as customer)
        top_customers = (
            db.query(
                Lead.first_name.label("customer_name"),
                func.sum(OrderItem.qty * Price.price).label("total_revenue"),
                func.count(Order.id).label("order_count"),
            )
            .join(OrderItem, Order.id == OrderItem.order_id)
            .join(Part, OrderItem.matched_part_id == Part.id)
            .join(Price, Part.id == Price.part_id)
            .join(Lead, Order.lead_id == Lead.id)
            .filter(
                and_(
                    func.date(Order.created_at) >= start_date,
                    func.date(Order.created_at) <= end_date,
                    Order.status == "completed",
                )
            )
            .group_by(Lead.first_name)
            .order_by(desc("total_revenue"))
            .limit(10)
            .all()
        )

        # Monthly comparison (calculate from order items and prices)
        current_month_revenue = (
            db.query(func.sum(OrderItem.qty * Price.price))
            .join(Part, OrderItem.matched_part_id == Part.id)
            .join(Price, Part.id == Price.part_id)
            .join(Order, OrderItem.order_id == Order.id)
            .filter(
                and_(
                    func.extract("year", Order.created_at) == end_date.year,
                    func.extract("month", Order.created_at) == end_date.month,
                    Order.status == "completed",
                )
            )
            .scalar()
            or 0
        )

        previous_month_revenue = (
            db.query(func.sum(OrderItem.qty * Price.price))
            .join(Part, OrderItem.matched_part_id == Part.id)
            .join(Price, Part.id == Price.part_id)
            .join(Order, OrderItem.order_id == Order.id)
            .filter(
                and_(
                    func.extract("year", Order.created_at)
                    == (end_date - relativedelta(months=1)).year,
                    func.extract("month", Order.created_at)
                    == (end_date - relativedelta(months=1)).month,
                    Order.status == "completed",
                )
            )
            .scalar()
            or 0
        )

        revenue_growth = 0
        if previous_month_revenue > 0:
            revenue_growth = (
                (current_month_revenue - previous_month_revenue)
                / previous_month_revenue
            ) * 100

        return SalesAnalytics(
            period=period,
            total_revenue=float(current_month_revenue),
            revenue_growth=revenue_growth,
            total_orders=sum([trend.orders for trend in revenue_trends]),
            revenue_trends=[
                {
                    "date": trend.date.isoformat(),
                    "revenue": float(trend.revenue),
                    "orders": trend.orders,
                }
                for trend in revenue_trends
            ],
            status_distribution={
                status.status: status.count for status in status_distribution
            },
            top_customers=[
                {
                    "customer_name": customer.customer_name,
                    "total_revenue": float(customer.total_revenue),
                    "order_count": customer.order_count,
                }
                for customer in top_customers
            ],
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching sales analytics: {str(e)}"
        )


@router.get("/inventory/analytics", response_model=InventoryAnalytics)
async def get_inventory_analytics(db: Session = Depends(get_db)):
    """
    Get inventory analytics
    """
    try:
        # Parts by category
        parts_by_category = (
            db.query(
                PartCategory.name.label("category"),
                func.count(Part.id).label("count"),
                func.avg(Price.price).label("avg_price"),
            )
            .join(Part, Part.category_id == PartCategory.id)
            .join(Price, Part.id == Price.part_id)
            .group_by(PartCategory.name)
            .all()
        )

        # Parts by brand
        parts_by_brand = (
            db.query(
                Part.brand_oem.label("brand"),
                func.count(Part.id).label("count"),
                func.avg(Price.price).label("avg_price"),
            )
            .join(Price, Part.id == Price.part_id)
            .group_by(Part.brand_oem)
            .order_by(desc("count"))
            .limit(10)
            .all()
        )

        # Price distribution
        price_ranges = [
            ("0-100", db.query(Price).filter(Price.price.between(0, 100)).count()),
            ("100-500", db.query(Price).filter(Price.price.between(100, 500)).count()),
            (
                "500-1000",
                db.query(Price).filter(Price.price.between(500, 1000)).count(),
            ),
            (
                "1000-5000",
                db.query(Price).filter(Price.price.between(1000, 5000)).count(),
            ),
            ("5000+", db.query(Price).filter(Price.price > 5000).count()),
        ]

        # Status distribution
        status_distribution = (
            db.query(Part.status, func.count(Part.id).label("count"))
            .group_by(Part.status)
            .all()
        )

        # Low stock items (using Price available_qty)
        low_stock_items = (
            db.query(Part)
            .join(Price, Part.id == Price.part_id)
            .filter(or_(Price.available_qty < 10, Price.available_qty.is_(None)))
            .limit(20)
            .all()
        )

        return InventoryAnalytics(
            total_parts=db.query(Part).count(),
            parts_by_category=[
                {
                    "category": cat.category,
                    "count": cat.count,
                    "avg_price": float(cat.avg_price) if cat.avg_price else 0,
                }
                for cat in parts_by_category
            ],
            parts_by_brand=[
                {
                    "brand": brand.brand,
                    "count": brand.count,
                    "avg_price": float(brand.avg_price) if brand.avg_price else 0,
                }
                for brand in parts_by_brand
            ],
            price_distribution={
                range_name: count for range_name, count in price_ranges
            },
            status_distribution={
                status.status: status.count for status in status_distribution
            },
            low_stock_items=[
                {
                    "id": item.id,
                    "part_name": item.part_name,
                    "brand_oem": item.brand_oem,
                    "oem_code": item.oem_code,
                    "stock_quantity": 0,  # Will be populated from Price table in frontend
                }
                for item in low_stock_items
            ],
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching inventory analytics: {str(e)}"
        )


@router.get("/customers/analytics", response_model=CustomerAnalytics)
async def get_customer_analytics(
    period: str = Query("30d", regex="^(7d|30d|90d|1y)$"), db: Session = Depends(get_db)
):
    """
    Get customer analytics
    """
    try:
        # Calculate date range
        end_date = date.today()
        if period == "7d":
            start_date = end_date - timedelta(days=7)
        elif period == "30d":
            start_date = end_date - timedelta(days=30)
        elif period == "90d":
            start_date = end_date - timedelta(days=90)
        elif period == "1y":
            start_date = end_date - relativedelta(years=1)

        # Lead conversion rate
        total_leads = (
            db.query(Lead)
            .filter(
                and_(
                    func.date(Lead.created_at) >= start_date,
                    func.date(Lead.created_at) <= end_date,
                )
            )
            .count()
        )

        converted_leads = (
            db.query(Lead)
            .filter(
                and_(
                    func.date(Lead.created_at) >= start_date,
                    func.date(Lead.created_at) <= end_date,
                    Lead.status == "converted",
                )
            )
            .count()
        )

        conversion_rate = (
            (converted_leads / total_leads * 100) if total_leads > 0 else 0
        )

        # Customer acquisition trends
        acquisition_trends = (
            db.query(
                func.date(Lead.created_at).label("date"),
                func.count(Lead.id).label("new_leads"),
            )
            .filter(
                and_(
                    func.date(Lead.created_at) >= start_date,
                    func.date(Lead.created_at) <= end_date,
                )
            )
            .group_by(func.date(Lead.created_at))
            .order_by("date")
            .all()
        )

        # Geographic distribution
        geographic_distribution = (
            db.query(Lead.city, func.count(Lead.id).label("count"))
            .filter(
                and_(
                    func.date(Lead.created_at) >= start_date,
                    func.date(Lead.created_at) <= end_date,
                )
            )
            .group_by(Lead.city)
            .order_by(desc("count"))
            .limit(10)
            .all()
        )

        # Lead sources (assuming we have a source field)
        lead_sources = (
            db.query(
                func.coalesce(Lead.source, "Unknown").label("source"),
                func.count(Lead.id).label("count"),
            )
            .filter(
                and_(
                    func.date(Lead.created_at) >= start_date,
                    func.date(Lead.created_at) <= end_date,
                )
            )
            .group_by(Lead.source)
            .all()
        )

        return CustomerAnalytics(
            period=period,
            total_leads=total_leads,
            converted_leads=converted_leads,
            conversion_rate=conversion_rate,
            acquisition_trends=[
                {"date": trend.date.isoformat(), "new_leads": trend.new_leads}
                for trend in acquisition_trends
            ],
            geographic_distribution={
                geo.city: geo.count for geo in geographic_distribution
            },
            lead_sources={source.source: source.count for source in lead_sources},
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching customer analytics: {str(e)}"
        )


@router.get("/performance/metrics", response_model=PerformanceMetrics)
async def get_performance_metrics(db: Session = Depends(get_db)):
    """
    Get system performance metrics
    """
    try:
        # API response times (mock data for now)
        api_metrics = {
            "avg_response_time": 120,  # milliseconds
            "uptime": 99.9,  # percentage
            "requests_per_minute": 45,
            "error_rate": 0.1,  # percentage
        }

        # Database metrics
        db_metrics = {
            "connection_pool_size": 10,
            "active_connections": 3,
            "query_avg_time": 25,  # milliseconds
            "cache_hit_rate": 85.5,  # percentage
        }

        # Bot metrics
        bot_metrics = {
            "total_users": db.query(
                func.count(func.distinct(Lead.telegram_user_id))
            ).scalar()
            or 0,
            "active_sessions": db.query(WizardSession)
            .filter(func.date(WizardSession.created_at) == date.today())
            .count(),
            "messages_processed": db.query(func.count(WizardSession.id)).scalar() or 0,
            "avg_session_duration": 180,  # seconds
        }

        return PerformanceMetrics(
            api=api_metrics,
            database=db_metrics,
            bot=bot_metrics,
            last_updated=datetime.now().isoformat(),
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching performance metrics: {str(e)}"
        )


@router.post("/reports/generate", response_model=ReportResponse)
async def generate_report(report_request: ReportRequest, db: Session = Depends(get_db)):
    """
    Generate comprehensive reports
    """
    try:
        # Set default date range if not provided
        if not report_request.date_to:
            report_request.date_to = date.today()
        if not report_request.date_from:
            report_request.date_from = report_request.date_to - timedelta(days=30)

        report_data = {}

        if "sales" in report_request.sections:
            # Sales report data
            sales_data = await get_sales_analytics(
                period="custom",
                date_from=report_request.date_from,
                date_to=report_request.date_to,
                db=db,
            )
            report_data["sales"] = sales_data

        if "inventory" in report_request.sections:
            # Inventory report data
            inventory_data = await get_inventory_analytics(db=db)
            report_data["inventory"] = inventory_data

        if "customers" in report_request.sections:
            # Customer report data
            customer_data = await get_customer_analytics(
                period="custom",
                date_from=report_request.date_from,
                date_to=report_request.date_to,
                db=db,
            )
            report_data["customers"] = customer_data

        # Generate report summary
        summary = {
            "generated_at": datetime.now().isoformat(),
            "date_range": {
                "from": report_request.date_from.isoformat(),
                "to": report_request.date_to.isoformat(),
            },
            "sections": report_request.sections,
            "format": report_request.format,
        }

        return ReportResponse(
            success=True,
            report_id=f"report_{int(datetime.now().timestamp())}",
            summary=summary,
            data=report_data,
            download_url=f"/api/v1/analytics/reports/download/{summary['report_id']}",
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error generating report: {str(e)}"
        )


@router.get("/charts/parts-by-category", response_model=ChartData)
async def get_parts_by_category_chart(db: Session = Depends(get_db)):
    """Get parts distribution by category chart data"""
    try:
        categories = (
            db.query(PartCategory.name, func.count(Part.id).label("count"))
            .join(Part, Part.category_id == PartCategory.id)
            .group_by(PartCategory.name)
            .all()
        )

        return ChartData(
            type="doughnut",
            labels=[cat.name for cat in categories],
            datasets=[
                {
                    "label": "Parts Count",
                    "data": [cat.count for cat in categories],
                    "backgroundColor": [
                        "#FF6384",
                        "#36A2EB",
                        "#FFCE56",
                        "#4BC0C0",
                        "#9966FF",
                        "#FF9F40",
                        "#FF6384",
                        "#C9CBCF",
                    ],
                }
            ],
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching chart data: {str(e)}"
        )


@router.get("/charts/sales-trend", response_model=TimeSeriesData)
async def get_sales_trend_chart(
    period: str = Query("30d", regex="^(7d|30d|90d|1y)$"), db: Session = Depends(get_db)
):
    """Get sales trend chart data"""
    try:
        # Calculate date range
        end_date = date.today()
        if period == "7d":
            start_date = end_date - timedelta(days=7)
        elif period == "30d":
            start_date = end_date - timedelta(days=30)
        elif period == "90d":
            start_date = end_date - timedelta(days=90)
        elif period == "1y":
            start_date = end_date - relativedelta(years=1)

        sales_data = (
            db.query(
                func.date(Order.created_at).label("date"),
                func.sum(OrderItem.qty * Price.price).label("revenue"),
            )
            .join(OrderItem, Order.id == OrderItem.order_id)
            .join(Part, OrderItem.matched_part_id == Part.id)
            .join(Price, Part.id == Price.part_id)
            .filter(
                and_(
                    func.date(Order.created_at) >= start_date,
                    func.date(Order.created_at) <= end_date,
                    Order.status == "completed",
                )
            )
            .group_by(func.date(Order.created_at))
            .order_by("date")
            .all()
        )

        return TimeSeriesData(
            type="line",
            labels=[sale.date.isoformat() for sale in sales_data],
            datasets=[
                {
                    "label": "Revenue",
                    "data": [float(sale.revenue) for sale in sales_data],
                    "borderColor": "#36A2EB",
                    "backgroundColor": "rgba(54, 162, 235, 0.1)",
                    "fill": True,
                }
            ],
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching sales trend: {str(e)}"
        )
