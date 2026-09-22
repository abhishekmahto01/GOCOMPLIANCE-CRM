"""Pydantic schemas for Sales Dashboard analytics, KPIs, charts, and filter options."""
import uuid
from datetime import date
from decimal import Decimal
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class KpiMetric(BaseModel):
    """KPI metric item with value and comparison percentage."""

    value: float
    formatted_value: str
    previous_value: float = 0.0
    percentage_change: float = 0.0
    is_positive: bool = True
    comparison_label: str = "vs last month"


class SalesKpiSummary(BaseModel):
    """Complete collection of KPI cards for Sales Dashboard."""

    total_sales: KpiMetric
    confirmed_orders: KpiMetric
    amount_received: KpiMetric
    outstanding: KpiMetric
    avg_order_value: KpiMetric
    total_clients: KpiMetric


class SalesTrendPoint(BaseModel):
    """Single data point for sales trend line/area chart."""

    date: str
    label: str
    sales_value: float
    order_count: int


class PaymentStatusItem(BaseModel):
    """Payment status segment in donut chart."""

    status: str
    label: str
    count: int
    percentage: float
    amount: float


class PaymentStatusBreakdown(BaseModel):
    """Payment status donut dataset."""

    total_orders: int
    items: List[PaymentStatusItem]


class ServiceSalesItem(BaseModel):
    """Service/licence sales horizontal bar item."""

    service_id: uuid.UUID
    service_code: str
    service_name: str
    total_sales: float
    order_count: int


class LeadSourceItem(BaseModel):
    """Lead source segment in donut chart."""

    source: str
    label: str
    count: int
    percentage: float


class LeadSourcesBreakdown(BaseModel):
    """Lead source donut dataset."""

    total_leads: int
    items: List[LeadSourceItem]


class TeamPerformanceRow(BaseModel):
    """Sales team member row in performance table."""

    salesperson_id: uuid.UUID
    salesperson_name: str
    employee_code: str
    orders_count: int
    total_sales: float
    amount_received: float
    outstanding: float


class RecentOrderItem(BaseModel):
    """Recent sales order item for table."""

    order_id: uuid.UUID
    order_number: str
    order_date: date
    formatted_date: str
    client_name: str
    service_name: str
    salesperson_name: str
    order_value: float
    amount_received: float
    balance_amount: float
    payment_status: str
    operation_status: str
    confirmation_status: str


class FilterOptionItem(BaseModel):
    """Key-value filter option item for dropdowns."""

    id: str
    label: str


class SalesFilterOptions(BaseModel):
    """Available filter options dynamically permitted for the logged-in user."""

    employees: List[FilterOptionItem]
    services: List[FilterOptionItem]
    lead_sources: List[FilterOptionItem]
    payment_statuses: List[FilterOptionItem]
    can_filter_employees: bool = True
    default_employee_id: Optional[str] = None


class SalesDashboardResponse(BaseModel):
    """Unified dashboard response payload."""

    date_range: Dict[str, str]
    kpis: SalesKpiSummary
    sales_trend: List[SalesTrendPoint]
    payment_status: PaymentStatusBreakdown
    service_sales: List[ServiceSalesItem]
    lead_sources: LeadSourcesBreakdown
    team_performance: List[TeamPerformanceRow]
    recent_orders: List[RecentOrderItem]
    filter_options: SalesFilterOptions

    model_config = ConfigDict(from_attributes=True)
