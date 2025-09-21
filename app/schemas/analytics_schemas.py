from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal, Union
from datetime import date, datetime


class DashboardMetrics(BaseModel):
    """Dashboard metrics summary"""

    total_parts: int = Field(ge=0)
    active_parts: int = Field(ge=0)
    total_vehicles: int = Field(ge=0)
    total_categories: int = Field(ge=0)
    total_orders: int = Field(ge=0)
    pending_orders: int = Field(ge=0)
    completed_orders: int = Field(ge=0)
    total_revenue: float = Field(ge=0)
    total_leads: int = Field(ge=0)
    new_leads: int = Field(ge=0)
    total_users: int = Field(ge=0)
    active_users: int = Field(ge=0)
    date_range: Dict[str, str]


class SalesTrend(BaseModel):
    """Sales trend data point"""

    date: str
    revenue: float
    orders: int


class StatusDistribution(BaseModel):
    """Status distribution data"""

    status: str
    count: int


class TopCustomer(BaseModel):
    """Top customer data"""

    customer_name: str
    total_revenue: float
    order_count: int


class SalesAnalytics(BaseModel):
    """Sales analytics data"""

    period: str
    total_revenue: float
    revenue_growth: float
    total_orders: int
    revenue_trends: List[SalesTrend]
    status_distribution: Dict[str, int]
    top_customers: List[TopCustomer]


class CategoryAnalytics(BaseModel):
    """Category analytics data"""

    category: str
    count: int
    avg_price: float


class BrandAnalytics(BaseModel):
    """Brand analytics data"""

    brand: str
    count: int
    avg_price: float


class LowStockItem(BaseModel):
    """Low stock item data"""

    id: int
    part_name: str
    brand_oem: str
    oem_code: str
    stock_quantity: int


class InventoryAnalytics(BaseModel):
    """Inventory analytics data"""

    total_parts: int
    parts_by_category: List[CategoryAnalytics]
    parts_by_brand: List[BrandAnalytics]
    price_distribution: Dict[str, int]
    status_distribution: Dict[str, int]
    low_stock_items: List[LowStockItem]


class AcquisitionTrend(BaseModel):
    """Customer acquisition trend data"""

    date: str
    new_leads: int


class CustomerAnalytics(BaseModel):
    """Customer analytics data"""

    period: str
    total_leads: int
    converted_leads: int
    conversion_rate: float
    acquisition_trends: List[AcquisitionTrend]
    geographic_distribution: Dict[str, int]
    lead_sources: Dict[str, int]


class APIMetrics(BaseModel):
    """API performance metrics"""

    avg_response_time: float  # milliseconds
    uptime: float  # percentage
    requests_per_minute: int
    error_rate: float  # percentage


class DatabaseMetrics(BaseModel):
    """Database performance metrics"""

    connection_pool_size: int
    active_connections: int
    query_avg_time: float  # milliseconds
    cache_hit_rate: float  # percentage


class BotMetrics(BaseModel):
    """Bot performance metrics"""

    total_users: int
    active_sessions: int
    messages_processed: int
    avg_session_duration: float  # seconds


class PerformanceMetrics(BaseModel):
    """System performance metrics"""

    api: APIMetrics
    database: DatabaseMetrics
    bot: BotMetrics
    last_updated: str


class ReportRequest(BaseModel):
    """Report generation request"""

    sections: List[Literal["sales", "inventory", "customers", "performance"]] = Field(
        ...
    )
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    format: Literal["json", "pdf", excel] = Field(default=json)
    include_charts: bool = Field(default=True)


class ReportResponse(BaseModel):
    Report generation response""

    success: bool
    report_id: str
    summary: Dict[str, Any]
    data: Dict[str, Any]
    download_url: str


class ChartDataset(BaseModel):
    """Chart dataset configuration"""

    label: str
    data: List[Any]
    backgroundColor: Optional[Union[str, List[str]]] = None
    borderColor: Optional[Union[str, List[str]]] = None
    fill: Optional[bool] = None


class ChartData(BaseModel):
    """Chart data structure"""

    type: Literal["bar", "line", "doughnut", "pie", "radar"]
    labels: List[str]
    datasets: List[ChartDataset]


class TimeSeriesData(BaseModel):
    """Time series chart data"""

    type: Literal["line", "bar"]
    labels: List[str]
    datasets: List[ChartDataset]


class AnalyticsFilter(BaseModel):
    """Analytics filter options"""

    date_from: Optional[date] = None
    date_to: Optional[date] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    status: Optional[str] = None
    period: Literal["7d", "30d", "90d", "1y", "custom"] = "30d"


class ExportRequest(BaseModel):
    """Analytics data export request"""

    data_type: Literal[
        "dashboard", "sales", "inventory", "customers", "performance"
    ] = Field(...)
    format: Literal["csv", "xlsx", "json"] = Field(default="xlsx")
    filters: Optional[AnalyticsFilter] = None
    include_charts: bool = Field(default=False)


class ExportResponse(BaseModel):
    """Analytics data export response"""

    success: bool
    filename: str
    content_type: str
    download_url: str
    record_count: int


class AlertThreshold(BaseModel):
    """Alert threshold configuration"""

    metric: str
    operator: Literal["gt", "lt", "eq", "gte", "lte"]
    value: float
    message: str


class Alert(BaseModel):
    """System alert"""

    id: str
    type: Literal["info", "warning", "error", "success"]
    title: str
    message: str
    timestamp: datetime
    acknowledged: bool = False


class SystemHealth(BaseModel):
    """System health status"""

    status: Literal["healthy", "warning", "critical"]
    api_status: str
    database_status: str
    bot_status: str
    last_check: datetime
    alerts: List[Alert] = Field(default_factory=list)
