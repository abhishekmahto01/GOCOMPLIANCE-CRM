"""Sales service layer handling orders, sequential IDs, calculation, operations handoff, and dashboard analytics."""
import csv
import io
import uuid
from calendar import monthrange
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import desc, func, or_, select
from sqlalchemy.orm import Session

from app.models.client import ClientMaster
from app.models.company import Company
from app.models.department import Department
from app.models.designation import Designation
from app.models.operation_application import (
    ApplicationActivityLog,
    ApplicationAssignmentHistory,
    ApplicationDocument,
    OperationApplication,
)
from app.models.sales_order import SalesOrder
from app.models.service import ServiceMaster, ServiceRequiredDocument
from app.models.user import User
from app.schemas.sales_dashboard import (
    FilterOptionItem,
    KpiMetric,
    LeadSourceItem,
    LeadSourcesBreakdown,
    PaymentStatusBreakdown,
    PaymentStatusItem,
    RecentOrderItem,
    SalesDashboardResponse,
    SalesFilterOptions,
    SalesKpiSummary,
    SalesTrendPoint,
    ServiceSalesItem,
    TeamPerformanceRow,
)
from app.schemas.sales_order import SalesOrderConfirmResponse, SalesOrderCreate
from app.services import permissions


class SalesOrderNotFoundError(Exception):
    """Raised when requested sales order is not found."""
    pass


class SalesOrderPermissionError(Exception):
    """Raised when user is not authorized to access or modify sales order."""
    pass


def format_inr(value: Decimal) -> str:
    """Format Decimal amount to Indian Rupee representation (e.g. ₹4,80,000)."""
    val_int = int(round(value))
    if val_int == 0:
        return "₹0"
    
    is_neg = val_int < 0
    s = str(abs(val_int))
    
    if len(s) <= 3:
        formatted = s
    else:
        last3 = s[-3:]
        rest = s[:-3]
        groups = []
        while len(rest) > 2:
            groups.insert(0, rest[-2:])
            rest = rest[:-2]
        if rest:
            groups.insert(0, rest)
        formatted = ",".join(groups) + "," + last3

    return f"-₹{formatted}" if is_neg else f"₹{formatted}"


def calculate_pct_change(current: Decimal, previous: Decimal) -> Tuple[float, bool]:
    """Calculate percentage change and whether trend direction is positive."""
    curr_f = float(current)
    prev_f = float(previous)
    
    if prev_f == 0.0:
        if curr_f == 0.0:
            return 0.0, True
        return 100.0, True
        
    pct = ((curr_f - prev_f) / prev_f) * 100.0
    return round(pct, 1), pct >= 0.0


def resolve_date_ranges(
    preset: Optional[str] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
) -> Tuple[date, date, date, date, str]:
    """Resolve current period (start_date, end_date) and previous equivalent period (prev_start, prev_end)."""
    today = date.today()
    preset_norm = (preset or "this_month").strip().lower().replace("-", "_")

    if preset_norm == "today":
        start_date = today
        end_date = today
        prev_start = today - timedelta(days=1)
        prev_end = today - timedelta(days=1)
        comparison_label = "vs yesterday"

    elif preset_norm == "this_week":
        # Monday to Sunday of this week
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)
        prev_start = start_date - timedelta(days=7)
        prev_end = end_date - timedelta(days=7)
        comparison_label = "vs last week"

    elif preset_norm == "this_month":
        start_date = date(today.year, today.month, 1)
        _, last_day = monthrange(today.year, today.month)
        end_date = date(today.year, today.month, last_day)
        
        # Previous month
        if today.month == 1:
            prev_year = today.year - 1
            prev_month = 12
        else:
            prev_year = today.year
            prev_month = today.month - 1
        _, prev_last_day = monthrange(prev_year, prev_month)
        prev_start = date(prev_year, prev_month, 1)
        prev_end = date(prev_year, prev_month, prev_last_day)
        comparison_label = "vs last month"

    elif preset_norm == "this_quarter":
        quarter = (today.month - 1) // 3 + 1
        q_start_month = (quarter - 1) * 3 + 1
        q_end_month = q_start_month + 2
        _, q_last_day = monthrange(today.year, q_end_month)
        start_date = date(today.year, q_start_month, 1)
        end_date = date(today.year, q_end_month, q_last_day)
        
        # Previous quarter
        if quarter == 1:
            pq_year = today.year - 1
            pq_start_month = 10
            pq_end_month = 12
        else:
            pq_year = today.year
            pq_start_month = (quarter - 2) * 3 + 1
            pq_end_month = pq_start_month + 2
        _, pq_last_day = monthrange(pq_year, pq_end_month)
        prev_start = date(pq_year, pq_start_month, 1)
        prev_end = date(pq_year, pq_end_month, pq_last_day)
        comparison_label = "vs last quarter"

    elif preset_norm == "this_year":
        start_date = date(today.year, 1, 1)
        end_date = date(today.year, 12, 31)
        prev_start = date(today.year - 1, 1, 1)
        prev_end = date(today.year - 1, 12, 31)
        comparison_label = "vs last year"

    elif preset_norm == "custom" and from_date and to_date:
        start_date = from_date
        end_date = to_date
        duration = (end_date - start_date).days + 1
        prev_end = start_date - timedelta(days=1)
        prev_start = prev_end - timedelta(days=duration - 1)
        comparison_label = "vs previous period"

    else:
        # Fallback to this_month
        start_date = from_date or date(today.year, today.month, 1)
        _, last_day = monthrange(today.year, today.month)
        end_date = to_date or date(today.year, today.month, last_day)
        duration = (end_date - start_date).days + 1
        prev_end = start_date - timedelta(days=1)
        prev_start = prev_end - timedelta(days=max(1, duration) - 1)
        comparison_label = "vs previous period"

    return start_date, end_date, prev_start, prev_end, comparison_label


def generate_sales_order_number(session: Session, order_date: Optional[date] = None) -> str:
    """Generate a unique sequential Sales Order ID (e.g. SO-2025-0001) for the given year."""
    target_year = (order_date or date.today()).year
    prefix = f"SO-{target_year}-"

    stmt = (
        select(SalesOrder.order_number)
        .where(SalesOrder.order_number.like(f"{prefix}%"))
        .order_by(SalesOrder.order_number.desc())
        .limit(1)
    )
    latest = session.execute(stmt).scalar_one_or_none()

    if latest:
        try:
            seq_part = latest[len(prefix):]
            next_num = int(seq_part) + 1
        except ValueError:
            next_num = session.query(SalesOrder).filter(SalesOrder.order_number.like(f"{prefix}%")).count() + 1
    else:
        next_num = 1

    return f"{prefix}{next_num:04d}"


def generate_application_number(session: Session, app_date: Optional[date] = None) -> str:
    """Generate a unique sequential Application ID (e.g. AP-2025-0001) for the given year."""
    target_year = (app_date or date.today()).year
    prefix = f"AP-{target_year}-"

    stmt = (
        select(OperationApplication.application_number)
        .where(OperationApplication.application_number.like(f"{prefix}%"))
        .order_by(OperationApplication.application_number.desc())
        .limit(1)
    )
    latest = session.execute(stmt).scalar_one_or_none()

    if latest:
        try:
            seq_part = latest[len(prefix):]
            next_num = int(seq_part) + 1
        except ValueError:
            next_num = session.query(OperationApplication).filter(OperationApplication.application_number.like(f"{prefix}%")).count() + 1
    else:
        next_num = 1

    return f"{prefix}{next_num:04d}"


def create_sales_order(
    session: Session,
    data: SalesOrderCreate,
    current_user: User,
) -> SalesOrder:
    """Create a new sales order with computed balance and optional auto-confirmation."""
    company = session.get(Company, data.company_id)
    if not company or company.status != "ACTIVE":
        raise ValueError(f"Active company with ID '{data.company_id}' not found.")

    client = session.get(ClientMaster, data.client_id)
    if not client or client.status != "ACTIVE":
        raise ValueError(f"Active client with ID '{data.client_id}' not found.")
    if client.company_id != data.company_id:
        raise ValueError("Client does not belong to specified company.")

    service = session.get(ServiceMaster, data.service_id)
    if not service or service.status != "ACTIVE":
        raise ValueError(f"Active service with ID '{data.service_id}' not found.")

    salesperson = session.get(User, data.salesperson_user_id)
    if not salesperson or salesperson.account_status != "ACTIVE":
        raise ValueError(f"Active salesperson with ID '{data.salesperson_user_id}' not found.")

    order_num = generate_sales_order_number(session, data.order_date)
    val = Decimal(str(data.order_value))
    rcvd = Decimal(str(data.amount_received))
    bal = max(Decimal("0.00"), val - rcvd)

    order = SalesOrder(
        order_number=order_num,
        company_id=data.company_id,
        client_id=data.client_id,
        service_id=data.service_id,
        salesperson_user_id=data.salesperson_user_id,
        lead_source=data.lead_source,
        order_date=data.order_date,
        order_value=val,
        amount_received=rcvd,
        balance_amount=bal,
        payment_status=data.payment_status,
        confirmation_status="DRAFT",
        notes=data.notes,
    )
    session.add(order)
    session.flush()

    if data.auto_confirm:
        confirm_sales_order(session, order.order_id, current_user)

    return order


def confirm_sales_order(
    session: Session,
    order_id: uuid.UUID,
    current_user: User,
) -> SalesOrderConfirmResponse:
    """Confirm a sales order and execute idempotent transactional handoff to Operations."""
    order = session.get(SalesOrder, order_id)
    if not order:
        raise SalesOrderNotFoundError(f"Sales order with ID '{order_id}' not found.")

    existing_app = session.execute(
        select(OperationApplication).where(OperationApplication.sales_order_id == order_id)
    ).scalar_one_or_none()

    if existing_app and order.confirmation_status == "CONFIRMED":
        doc_count = session.query(ApplicationDocument).filter(
            ApplicationDocument.application_id == existing_app.application_id
        ).count()
        return SalesOrderConfirmResponse(
            order_id=order.order_id,
            order_number=order.order_number,
            confirmation_status=order.confirmation_status,
            confirmed_at=order.confirmed_at or datetime.now(timezone.utc),
            application_id=existing_app.application_id,
            application_number=existing_app.application_number,
            application_status=existing_app.application_status,
            assigned_to_user_id=existing_app.assigned_to_user_id,
            documents_count=doc_count,
        )

    now_utc = datetime.now(timezone.utc)
    order.confirmation_status = "CONFIRMED"
    order.confirmed_at = now_utc

    app_num = generate_application_number(session, order.order_date)

    new_app = OperationApplication(
        application_number=app_num,
        sales_order_id=order.order_id,
        company_id=order.company_id,
        client_id=order.client_id,
        service_id=order.service_id,
        assigned_to_user_id=None,
        assigned_by_user_id=None,
        assigned_at=None,
        priority="MEDIUM",
        application_status="UNASSIGNED",
        target_due_date=None,
        assignment_notes=order.notes,
    )
    session.add(new_app)
    session.flush()

    required_docs = session.execute(
        select(ServiceRequiredDocument)
        .where(ServiceRequiredDocument.service_id == order.service_id)
        .order_by(ServiceRequiredDocument.display_order.asc())
    ).scalars().all()

    doc_count = 0
    for r_doc in required_docs:
        app_doc = ApplicationDocument(
            application_id=new_app.application_id,
            document_code=r_doc.document_code,
            document_name=r_doc.document_name,
            is_mandatory=r_doc.is_mandatory,
            status="PENDING",
        )
        session.add(app_doc)
        doc_count += 1

    activity = ApplicationActivityLog(
        application_id=new_app.application_id,
        actor_user_id=current_user.user_id,
        action_type="STATUS_CHANGE",
        old_value="NONE",
        new_value="UNASSIGNED",
        comment=f"Order '{order.order_number}' confirmed and handed over from Sales.",
    )
    session.add(activity)
    session.flush()

    return SalesOrderConfirmResponse(
        order_id=order.order_id,
        order_number=order.order_number,
        confirmation_status=order.confirmation_status,
        confirmed_at=order.confirmed_at,
        application_id=new_app.application_id,
        application_number=new_app.application_number,
        application_status=new_app.application_status,
        assigned_to_user_id=None,
        documents_count=doc_count,
    )


def _apply_sales_filters(
    query: Any,
    scope_ctx: permissions.DataScopeContext,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    employee_id: Optional[uuid.UUID] = None,
    service_id: Optional[uuid.UUID] = None,
    lead_source: Optional[str] = None,
    payment_status: Optional[str] = None,
) -> Any:
    """Apply RBAC data scoping and query filters to SalesOrder select query."""
    # 1. Base Scope
    if scope_ctx.scope == "SELF":
        query = query.where(SalesOrder.salesperson_user_id == scope_ctx.user_id)
    elif scope_ctx.scope == "TEAM":
        if employee_id:
            if employee_id in scope_ctx.team_user_ids:
                query = query.where(SalesOrder.salesperson_user_id == employee_id)
            else:
                # Disallowed employee outside team
                query = query.where(SalesOrder.salesperson_user_id == uuid.uuid4())
        else:
            query = query.where(SalesOrder.salesperson_user_id.in_(scope_ctx.team_user_ids))
    elif scope_ctx.scope == "DEPARTMENT":
        query = query.where(SalesOrder.company_id == scope_ctx.company_id)
        if employee_id:
            query = query.where(SalesOrder.salesperson_user_id == employee_id)
    elif scope_ctx.scope == "COMPANY":
        query = query.where(SalesOrder.company_id == scope_ctx.company_id)
        if employee_id:
            query = query.where(SalesOrder.salesperson_user_id == employee_id)
    elif scope_ctx.scope == "ALL":
        if employee_id:
            query = query.where(SalesOrder.salesperson_user_id == employee_id)

    # 2. Date Range
    if start_date:
        query = query.where(SalesOrder.order_date >= start_date)
    if end_date:
        query = query.where(SalesOrder.order_date <= end_date)

    # 3. Attributes
    if service_id:
        query = query.where(SalesOrder.service_id == service_id)
    if lead_source and lead_source != "ALL":
        query = query.where(SalesOrder.lead_source == lead_source.upper())
    if payment_status and payment_status != "ALL":
        query = query.where(SalesOrder.payment_status == payment_status.upper())

    return query


def get_sales_dashboard_data(
    session: Session,
    current_user: User,
    preset: Optional[str] = "this_month",
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    employee_id: Optional[uuid.UUID] = None,
    service_id: Optional[uuid.UUID] = None,
    lead_source: Optional[str] = None,
    payment_status: Optional[str] = None,
) -> SalesDashboardResponse:
    """Compute and return live Sales Dashboard KPIs, charts, team table, and recent orders."""
    scope_ctx = permissions.resolve_data_scope_context(session, current_user, "SALES_DASHBOARD")

    # If user is SELF scope, enforce their own employee ID
    if scope_ctx.scope == "SELF":
        employee_id = current_user.user_id

    preset_norm = (preset or "this_month").strip().lower().replace("-", "_")
    start_date, end_date, prev_start, prev_end, comp_label = resolve_date_ranges(
        preset=preset_norm,
        from_date=from_date,
        to_date=to_date,
    )

    # -------------------------------------------------------------------------
    # 1. KPIs for Current Period
    # -------------------------------------------------------------------------
    base_curr = _apply_sales_filters(
        select(SalesOrder),
        scope_ctx=scope_ctx,
        start_date=start_date,
        end_date=end_date,
        employee_id=employee_id,
        service_id=service_id,
        lead_source=lead_source,
        payment_status=payment_status,
    )
    curr_orders = session.execute(base_curr).scalars().all()

    total_sales_curr = sum((o.order_value for o in curr_orders), Decimal("0.00"))
    confirmed_orders_curr = sum(1 for o in curr_orders if o.confirmation_status == "CONFIRMED")
    amount_received_curr = sum((o.amount_received for o in curr_orders), Decimal("0.00"))
    outstanding_curr = sum((o.balance_amount for o in curr_orders), Decimal("0.00"))
    total_orders_curr = len(curr_orders)
    avg_order_val_curr = (
        total_sales_curr / Decimal(str(total_orders_curr))
        if total_orders_curr > 0
        else Decimal("0.00")
    )
    total_clients_curr = len(set(o.client_id for o in curr_orders))

    # -------------------------------------------------------------------------
    # 2. KPIs for Previous Period (for Comparison %)
    # -------------------------------------------------------------------------
    base_prev = _apply_sales_filters(
        select(SalesOrder),
        scope_ctx=scope_ctx,
        start_date=prev_start,
        end_date=prev_end,
        employee_id=employee_id,
        service_id=service_id,
        lead_source=lead_source,
        payment_status=payment_status,
    )
    prev_orders = session.execute(base_prev).scalars().all()

    total_sales_prev = sum((o.order_value for o in prev_orders), Decimal("0.00"))
    confirmed_orders_prev = sum(1 for o in prev_orders if o.confirmation_status == "CONFIRMED")
    amount_received_prev = sum((o.amount_received for o in prev_orders), Decimal("0.00"))
    outstanding_prev = sum((o.balance_amount for o in prev_orders), Decimal("0.00"))
    total_orders_prev = len(prev_orders)
    avg_order_val_prev = (
        total_sales_prev / Decimal(str(total_orders_prev))
        if total_orders_prev > 0
        else Decimal("0.00")
    )
    total_clients_prev = len(set(o.client_id for o in prev_orders))

    # Calculate Percentage Changes
    sales_pct, sales_pos = calculate_pct_change(total_sales_curr, total_sales_prev)
    orders_pct, orders_pos = calculate_pct_change(Decimal(confirmed_orders_curr), Decimal(confirmed_orders_prev))
    rcvd_pct, rcvd_pos = calculate_pct_change(amount_received_curr, amount_received_prev)
    out_pct, out_pos = calculate_pct_change(outstanding_curr, outstanding_prev)
    avg_pct, avg_pos = calculate_pct_change(avg_order_val_curr, avg_order_val_prev)
    clients_pct, clients_pos = calculate_pct_change(Decimal(total_clients_curr), Decimal(total_clients_prev))

    kpis = SalesKpiSummary(
        total_sales=KpiMetric(
            value=total_sales_curr,
            formatted_value=format_inr(total_sales_curr),
            previous_value=total_sales_prev,
            percentage_change=sales_pct,
            is_positive=sales_pos,
            comparison_label=comp_label,
        ),
        confirmed_orders=KpiMetric(
            value=Decimal(confirmed_orders_curr),
            formatted_value=str(confirmed_orders_curr),
            previous_value=Decimal(confirmed_orders_prev),
            percentage_change=orders_pct,
            is_positive=orders_pos,
            comparison_label=comp_label,
        ),
        amount_received=KpiMetric(
            value=amount_received_curr,
            formatted_value=format_inr(amount_received_curr),
            previous_value=amount_received_prev,
            percentage_change=rcvd_pct,
            is_positive=rcvd_pos,
            comparison_label=comp_label,
        ),
        outstanding=KpiMetric(
            value=outstanding_curr,
            formatted_value=format_inr(outstanding_curr),
            previous_value=outstanding_prev,
            percentage_change=out_pct,
            is_positive=not out_pos if out_pct > 0 else True,  # Outstanding increase is typically highlighted red
            comparison_label=comp_label,
        ),
        avg_order_value=KpiMetric(
            value=avg_order_val_curr,
            formatted_value=format_inr(avg_order_val_curr),
            previous_value=avg_order_val_prev,
            percentage_change=avg_pct,
            is_positive=avg_pos,
            comparison_label=comp_label,
        ),
        total_clients=KpiMetric(
            value=Decimal(total_clients_curr),
            formatted_value=str(total_clients_curr),
            previous_value=Decimal(total_clients_prev),
            percentage_change=clients_pct,
            is_positive=clients_pos,
            comparison_label=comp_label,
        ),
    )

    # -------------------------------------------------------------------------
    # 3. Sales Trend (Timeline points)
    # -------------------------------------------------------------------------
    days_span = (end_date - start_date).days + 1
    trend_points: List[SalesTrendPoint] = []

    if days_span <= 31:
        # Group by intervals or days
        curr_d = start_date
        while curr_d <= end_date:
            d_str = curr_d.strftime("%Y-%m-%d")
            lbl = curr_d.strftime("%b %d") if days_span > 1 else curr_d.strftime("%I %p")
            # Filter orders on this day
            d_orders = [o for o in curr_orders if o.order_date == curr_d]
            d_val = sum((o.order_value for o in d_orders), Decimal("0.00"))
            trend_points.append(
                SalesTrendPoint(
                    date=d_str,
                    label=lbl,
                    sales_value=d_val,
                    order_count=len(d_orders),
                )
            )
            curr_d += timedelta(days=1)
    else:
        # Group weekly / monthly
        curr_d = start_date
        while curr_d <= end_date:
            step_end = min(curr_d + timedelta(days=6), end_date)
            lbl = f"{curr_d.strftime('%b %d')}"
            d_orders = [o for o in curr_orders if curr_d <= o.order_date <= step_end]
            d_val = sum((o.order_value for o in d_orders), Decimal("0.00"))
            trend_points.append(
                SalesTrendPoint(
                    date=curr_d.strftime("%Y-%m-%d"),
                    label=lbl,
                    sales_value=d_val,
                    order_count=len(d_orders),
                )
            )
            curr_d = step_end + timedelta(days=1)

    # -------------------------------------------------------------------------
    # 4. Payment Status Donut
    # -------------------------------------------------------------------------
    status_order = [
        ("FULLY_PAID", "Fully Paid"),
        ("PARTIALLY_PAID", "Partially Paid"),
        ("PENDING", "Pending"),
        ("OVERDUE", "Overdue"),
    ]
    payment_items: List[PaymentStatusItem] = []
    for st_code, st_lbl in status_order:
        st_orders = [o for o in curr_orders if o.payment_status == st_code]
        cnt = len(st_orders)
        amt = sum((o.order_value for o in st_orders), Decimal("0.00"))
        pct = round((cnt / total_orders_curr * 100.0), 1) if total_orders_curr > 0 else 0.0
        payment_items.append(
            PaymentStatusItem(
                status=st_code,
                label=st_lbl,
                count=cnt,
                percentage=pct,
                amount=amt,
            )
        )
    payment_breakdown = PaymentStatusBreakdown(
        total_orders=total_orders_curr,
        items=payment_items,
    )

    # -------------------------------------------------------------------------
    # 5. Service/Licence-wise Sales
    # -------------------------------------------------------------------------
    services_map: Dict[uuid.UUID, Dict[str, Any]] = {}
    for o in curr_orders:
        if o.service_id not in services_map:
            s_name = o.service.service_name if o.service else "Other Service"
            s_code = o.service.service_code if o.service else "UNKNOWN"
            services_map[o.service_id] = {
                "service_id": o.service_id,
                "service_code": s_code,
                "service_name": s_name,
                "total_sales": Decimal("0.00"),
                "order_count": 0,
            }
        services_map[o.service_id]["total_sales"] += o.order_value
        services_map[o.service_id]["order_count"] += 1

    service_sales_list = [
        ServiceSalesItem(
            service_id=v["service_id"],
            service_code=v["service_code"],
            service_name=v["service_name"],
            total_sales=v["total_sales"],
            order_count=v["order_count"],
        )
        for v in sorted(services_map.values(), key=lambda x: x["total_sales"], reverse=True)
    ]

    # -------------------------------------------------------------------------
    # 6. Lead Sources Donut
    # -------------------------------------------------------------------------
    source_order = [
        ("WEBSITE", "Website"),
        ("REFERRAL", "Referral"),
        ("DIRECT", "Direct"),
        ("OTHERS", "Others"),
    ]
    lead_items: List[LeadSourceItem] = []
    for src_code, src_lbl in source_order:
        s_orders = [o for o in curr_orders if (o.lead_source or "").upper() == src_code]
        cnt = len(s_orders)
        pct = round((cnt / total_orders_curr * 100.0), 1) if total_orders_curr > 0 else 0.0
        lead_items.append(
            LeadSourceItem(
                source=src_code,
                label=src_lbl,
                count=cnt,
                percentage=pct,
            )
        )
    lead_breakdown = LeadSourcesBreakdown(
        total_leads=total_orders_curr,
        items=lead_items,
    )

    # -------------------------------------------------------------------------
    # 7. Sales Team Performance Table
    # -------------------------------------------------------------------------
    rep_map: Dict[uuid.UUID, Dict[str, Any]] = {}
    for o in curr_orders:
        if o.salesperson_user_id not in rep_map:
            u_name = f"{o.salesperson.first_name} {o.salesperson.last_name}" if o.salesperson else "Unknown"
            u_code = o.salesperson.employee_code if o.salesperson else "EMP"
            rep_map[o.salesperson_user_id] = {
                "salesperson_id": o.salesperson_user_id,
                "salesperson_name": u_name,
                "employee_code": u_code,
                "orders_count": 0,
                "total_sales": Decimal("0.00"),
                "amount_received": Decimal("0.00"),
                "outstanding": Decimal("0.00"),
            }
        rep_map[o.salesperson_user_id]["orders_count"] += 1
        rep_map[o.salesperson_user_id]["total_sales"] += o.order_value
        rep_map[o.salesperson_user_id]["amount_received"] += o.amount_received
        rep_map[o.salesperson_user_id]["outstanding"] += o.balance_amount

    team_perf_rows = [
        TeamPerformanceRow(
            salesperson_id=v["salesperson_id"],
            salesperson_name=v["salesperson_name"],
            employee_code=v["employee_code"],
            orders_count=v["orders_count"],
            total_sales=v["total_sales"],
            amount_received=v["amount_received"],
            outstanding=v["outstanding"],
        )
        for v in sorted(rep_map.values(), key=lambda x: x["total_sales"], reverse=True)
    ]

    # -------------------------------------------------------------------------
    # 8. Recent Sales Orders (Latest 10)
    # -------------------------------------------------------------------------
    sorted_recent = sorted(curr_orders, key=lambda x: (x.order_date, x.created_at), reverse=True)[:10]
    recent_items: List[RecentOrderItem] = []
    for o in sorted_recent:
        c_name = o.client.client_name if o.client else "Client"
        s_name = o.service.service_name if o.service else "Service"
        sp_name = f"{o.salesperson.first_name} {o.salesperson.last_name}" if o.salesperson else "Rep"
        
        # Operation Status
        op_status = "PENDING"
        if o.application:
            app_st = o.application.application_status
            if app_st in ("APPROVED", "COMPLETED"):
                op_status = "COMPLETED"
            elif app_st in ("ASSIGNED", "IN_PROGRESS", "SUBMITTED", "READY_FOR_SUBMISSION"):
                op_status = "IN_PROGRESS"
            else:
                op_status = "PENDING"

        recent_items.append(
            RecentOrderItem(
                order_id=o.order_id,
                order_number=o.order_number,
                order_date=o.order_date,
                formatted_date=o.order_date.strftime("%d %b %Y"),
                client_name=c_name,
                service_name=s_name,
                salesperson_name=sp_name,
                order_value=o.order_value,
                amount_received=o.amount_received,
                balance_amount=o.balance_amount,
                payment_status=o.payment_status,
                operation_status=op_status,
                confirmation_status=o.confirmation_status,
            )
        )

    # -------------------------------------------------------------------------
    # 9. Dynamic Filter Options
    # -------------------------------------------------------------------------
    # Filterable employees
    emp_options: List[FilterOptionItem] = []
    can_filter_emp = scope_ctx.scope != "SELF"
    default_emp_id = str(current_user.user_id) if scope_ctx.scope == "SELF" else None

    if scope_ctx.scope == "SELF":
        emp_options.append(
            FilterOptionItem(
                id=str(current_user.user_id),
                label=f"{current_user.first_name} {current_user.last_name}",
            )
        )
    elif scope_ctx.scope == "TEAM":
        team_users = session.execute(
            select(User)
            .outerjoin(Department, User.department_id == Department.department_id)
            .outerjoin(Designation, User.designation_id == Designation.designation_id)
            .where(
                User.user_id.in_(scope_ctx.team_user_ids),
                User.account_status == "ACTIVE",
                or_(
                    Department.department_name.ilike("%sales%"),
                    Department.department_code.ilike("%sales%"),
                    Designation.designation_name.ilike("%sales%"),
                    Designation.designation_code.ilike("%sales%"),
                    User.user_id.in_(select(SalesOrder.salesperson_user_id)),
                ),
            )
            .order_by(User.first_name.asc())
        ).scalars().all()
        # Fallback if no specific sales dept tagged yet in team
        if not team_users:
            team_users = session.execute(
                select(User).where(User.user_id.in_(scope_ctx.team_user_ids)).order_by(User.first_name.asc())
            ).scalars().all()

        for u in team_users:
            emp_options.append(
                FilterOptionItem(
                    id=str(u.user_id),
                    label=f"{u.first_name} {u.last_name} ({u.employee_code})",
                )
            )
    else:  # COMPANY, ALL
        comp_users_query = (
            select(User)
            .outerjoin(Department, User.department_id == Department.department_id)
            .outerjoin(Designation, User.designation_id == Designation.designation_id)
            .where(
                User.account_status == "ACTIVE",
                User.company_id == current_user.company_id if scope_ctx.scope == "COMPANY" else True,
                or_(
                    Department.department_name.ilike("%sales%"),
                    Department.department_code.ilike("%sales%"),
                    Designation.designation_name.ilike("%sales%"),
                    Designation.designation_code.ilike("%sales%"),
                    User.user_id.in_(select(SalesOrder.salesperson_user_id)),
                ),
            )
            .order_by(User.first_name.asc())
        )
        comp_users = session.execute(comp_users_query).scalars().all()
        # Fallback if no specific sales tag found
        if not comp_users:
            comp_users = session.execute(
                select(User)
                .where(
                    User.account_status == "ACTIVE",
                    User.company_id == current_user.company_id if scope_ctx.scope == "COMPANY" else True,
                )
                .order_by(User.first_name.asc())
            ).scalars().all()

        for u in comp_users:
            emp_options.append(
                FilterOptionItem(
                    id=str(u.user_id),
                    label=f"{u.first_name} {u.last_name} ({u.employee_code})",
                )
            )

    # Active services
    active_services = session.execute(
        select(ServiceMaster).where(ServiceMaster.status == "ACTIVE").order_by(ServiceMaster.service_name.asc())
    ).scalars().all()
    service_options = [
        FilterOptionItem(id=str(s.service_id), label=s.service_name)
        for s in active_services
    ]

    lead_source_options = [
        FilterOptionItem(id="WEBSITE", label="Website"),
        FilterOptionItem(id="REFERRAL", label="Referral"),
        FilterOptionItem(id="DIRECT", label="Direct"),
        FilterOptionItem(id="OTHERS", label="Others"),
    ]

    payment_status_options = [
        FilterOptionItem(id="FULLY_PAID", label="Fully Paid"),
        FilterOptionItem(id="PARTIALLY_PAID", label="Partially Paid"),
        FilterOptionItem(id="PENDING", label="Pending"),
        FilterOptionItem(id="OVERDUE", label="Overdue"),
    ]

    filter_options = SalesFilterOptions(
        employees=emp_options,
        services=service_options,
        lead_sources=lead_source_options,
        payment_statuses=payment_status_options,
        can_filter_employees=can_filter_emp,
        default_employee_id=default_emp_id,
    )

    return SalesDashboardResponse(
        date_range={
            "preset": preset_norm,
            "from_date": start_date.strftime("%Y-%m-%d"),
            "to_date": end_date.strftime("%Y-%m-%d"),
            "formatted_from": start_date.strftime("%d/%m/%Y"),
            "formatted_to": end_date.strftime("%d/%m/%Y"),
            "comparison_label": comp_label,
        },
        kpis=kpis,
        sales_trend=trend_points,
        payment_status=payment_breakdown,
        service_sales=service_sales_list,
        lead_sources=lead_breakdown,
        team_performance=team_perf_rows,
        recent_orders=recent_items,
        filter_options=filter_options,
    )


def export_sales_orders_csv(
    session: Session,
    current_user: User,
    preset: Optional[str] = "this_month",
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    employee_id: Optional[uuid.UUID] = None,
    service_id: Optional[uuid.UUID] = None,
    lead_source: Optional[str] = None,
    payment_status: Optional[str] = None,
) -> Tuple[str, str]:
    """Generate CSV string of filtered sales orders within permitted data scope.

    Returns:
        Tuple of (csv_content_string, filename).
    """
    scope_ctx = permissions.resolve_data_scope_context(session, current_user, "SALES_DASHBOARD")
    if scope_ctx.scope == "SELF":
        employee_id = current_user.user_id

    start_date, end_date, _, _, _ = resolve_date_ranges(
        preset=preset,
        from_date=from_date,
        to_date=to_date,
    )

    query = _apply_sales_filters(
        select(SalesOrder),
        scope_ctx=scope_ctx,
        start_date=start_date,
        end_date=end_date,
        employee_id=employee_id,
        service_id=service_id,
        lead_source=lead_source,
        payment_status=payment_status,
    ).order_by(SalesOrder.order_date.desc(), SalesOrder.created_at.desc())

    orders = session.execute(query).scalars().all()

    output = io.StringIO()
    writer = csv.writer(output)

    # Write Header
    writer.writerow([
        "Order ID",
        "Date",
        "Client",
        "Service",
        "Salesperson",
        "Lead Source",
        "Order Value (INR)",
        "Received (INR)",
        "Balance (INR)",
        "Payment Status",
        "Operation Status",
        "Confirmation Status",
    ])

    for o in orders:
        c_name = o.client.client_name if o.client else ""
        s_name = o.service.service_name if o.service else ""
        sp_name = f"{o.salesperson.first_name} {o.salesperson.last_name}" if o.salesperson else ""
        op_status = o.application.application_status if o.application else "PENDING"

        writer.writerow([
            o.order_number,
            o.order_date.strftime("%d/%m/%Y"),
            c_name,
            s_name,
            sp_name,
            o.lead_source,
            f"{o.order_value:.2f}",
            f"{o.amount_received:.2f}",
            f"{o.balance_amount:.2f}",
            o.payment_status,
            op_status,
            o.confirmation_status,
        ])

    csv_content = output.getvalue()
    filename = f"sales_report_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv"
    return csv_content, filename
