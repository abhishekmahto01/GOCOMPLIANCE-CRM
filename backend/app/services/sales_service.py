"""Sales service layer handling orders, sequential IDs, calculation, operations handoff, and dashboard analytics."""
import csv
import io
import uuid
from calendar import monthrange
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import case, desc, func, or_, select
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
from app.schemas.sales_order import (
    SalesClientOption,
    SalesEmployeeOption,
    SalesFormOptionsResponse,
    SalesOrderConfirmResponse,
    SalesOrderCreate,
    SalesOrderDetailRead,
    SalesOrderRead,
    SalesOrderUpdate,
    SalesRegisterResponse,
    SalesRegisterSummary,
    SalesServiceOption,
)
from app.services import operation_service, permissions


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
    """Create a new sales order with client matching/deduplication, RBAC scoping, and financial calculations."""
    company_id = data.company_id or current_user.company_id
    company = session.get(Company, company_id)
    if not company or company.status != "ACTIVE":
        raise ValueError(f"Active company with ID '{company_id}' not found.")

    # 1. Client Resolution and Deduplication
    client = None
    if data.client_id:
        client = session.get(ClientMaster, data.client_id)
        if not client or client.status != "ACTIVE":
            raise ValueError(f"Active client with ID '{data.client_id}' not found.")
        if client.company_id != company_id:
            raise ValueError("Client does not belong to specified company.")
    elif data.client_name and data.client_name.strip():
        c_name = data.client_name.strip()
        c_phone = (data.contact_no or "").strip()

        # Check existing client in company by name or contact phone
        query = session.query(ClientMaster).filter(
            ClientMaster.company_id == company_id,
            ClientMaster.status == "ACTIVE",
        )
        if c_phone:
            matched_client = query.filter(
                or_(
                    func.lower(ClientMaster.client_name) == func.lower(c_name),
                    ClientMaster.contact_phone == c_phone,
                )
            ).first()
        else:
            matched_client = query.filter(
                func.lower(ClientMaster.client_name) == func.lower(c_name)
            ).first()

        if matched_client:
            client = matched_client
            if c_phone and not matched_client.contact_phone:
                matched_client.contact_phone = c_phone
        else:
            client = ClientMaster(
                client_id=uuid.uuid4(),
                company_id=company_id,
                client_name=c_name,
                contact_person=c_name,
                contact_email=f"{c_phone}@client.crm" if c_phone else "",
                contact_phone=c_phone or "0000000000",
                entity_type="INDIVIDUAL",
                created_by_user_id=current_user.user_id,
                status="ACTIVE",
            )
            session.add(client)
            session.flush()

    if not client:
        raise ValueError("Valid client could not be identified or created.")

    # 2. Service Verification
    service = session.get(ServiceMaster, data.service_id)
    if not service or service.status != "ACTIVE":
        raise ValueError(f"Active service with ID '{data.service_id}' not found.")

    # 3. Salesperson Resolution and Data Scope Check
    try:
        scope_ctx = permissions.resolve_data_scope_context(session, current_user, "SALES_CONFIRMED_ORDER")
    except permissions.PermissionDeniedError:
        scope_ctx = None

    if scope_ctx:
        if scope_ctx.scope == "SELF":
            salesperson_id = current_user.user_id
        elif data.salesperson_user_id:
            salesperson_id = data.salesperson_user_id
            if scope_ctx.scope == "TEAM":
                if salesperson_id not in scope_ctx.team_user_ids:
                    raise ValueError("Selected salesperson is not within your permitted team.")
            elif scope_ctx.scope in ("COMPANY", "DEPARTMENT"):
                sp_user = session.get(User, salesperson_id)
                if not sp_user or sp_user.company_id != current_user.company_id:
                    raise ValueError("Selected salesperson does not belong to your company.")
        else:
            salesperson_id = current_user.user_id
    else:
        salesperson_id = data.salesperson_user_id or current_user.user_id

    salesperson = session.get(User, salesperson_id)
    if not salesperson or salesperson.account_status != "ACTIVE":
        raise ValueError(f"Active salesperson with ID '{salesperson_id}' not found.")

    # 4. Financial Calculations & Validations
    val = Decimal(str(data.order_value))
    rcvd = Decimal(str(data.amount_received or "0.00"))
    g_fee = Decimal(str(data.govt_fees or "0.00"))
    i_cost = Decimal(str(data.incidental_cost or "0.00"))

    if val < Decimal("0.00") or rcvd < Decimal("0.00") or g_fee < Decimal("0.00") or i_cost < Decimal("0.00"):
        raise ValueError("Amounts cannot be negative.")

    if rcvd > val:
        raise ValueError("Advance Amount cannot be greater than Total Amount.")

    bal = max(Decimal("0.00"), val - rcvd)
    profit = val - g_fee - i_cost

    # Payment Status
    if data.payment_status:
        pmt_status = data.payment_status.upper()
    else:
        if rcvd >= val and val > Decimal("0.00"):
            pmt_status = "FULLY_PAID"
        elif rcvd > Decimal("0.00"):
            pmt_status = "PARTIALLY_PAID"
        else:
            pmt_status = "PENDING"

    order_num = generate_sales_order_number(session, data.order_date)

    order = SalesOrder(
        order_number=order_num,
        company_id=company_id,
        client_id=client.client_id,
        service_id=data.service_id,
        salesperson_user_id=salesperson_id,
        lead_source=data.lead_source,
        order_date=data.order_date,
        order_value=val,
        amount_received=rcvd,
        balance_amount=bal,
        govt_fees=g_fee,
        incidental_cost=i_cost,
        profit_amount=profit,
        payment_status=pmt_status,
        confirmation_status="DRAFT",
        proforma_invoice_no=data.proforma_invoice_no.strip() if data.proforma_invoice_no else None,
        tax_invoice_no=data.tax_invoice_no.strip() if data.tax_invoice_no else None,
        reimbursement_note=data.reimbursement_note.strip() if data.reimbursement_note else None,
        notes=data.notes,
    )
    session.add(order)
    session.flush()

    if data.auto_confirm:
        confirm_sales_order(session, order.order_id, current_user, assignee_user_id=data.assignee_user_id)

    return order


def update_sales_order(
    session: Session,
    order_id: uuid.UUID,
    data: SalesOrderUpdate,
    current_user: User,
) -> SalesOrderDetailRead:
    """Update an existing sales order's financial and sales fields with RBAC check and audit logging."""
    order = session.get(SalesOrder, order_id)
    if not order:
        raise SalesOrderNotFoundError(f"Sales order with ID '{order_id}' not found.")

    # Check RBAC Permission & Data Scope
    try:
        scope_ctx = permissions.resolve_data_scope_context(session, current_user, "SALES_MY_ORDERS")
    except permissions.PermissionDeniedError:
        try:
            scope_ctx = permissions.resolve_data_scope_context(session, current_user, "SALES_ALL_ORDERS")
        except permissions.PermissionDeniedError:
            try:
                scope_ctx = permissions.resolve_data_scope_context(session, current_user, "SALES_CONFIRMED_ORDER")
            except permissions.PermissionDeniedError:
                raise SalesOrderPermissionError("You do not have permission to edit sales orders.")

    if not scope_ctx.is_user_permitted(order.salesperson_user_id, order.company_id):
        raise SalesOrderPermissionError("You are not authorized to edit this sales order.")

    # Track old values for audit trail
    old_values = {
        "order_value": Decimal(str(order.order_value)),
        "amount_received": Decimal(str(order.amount_received)),
        "balance_amount": Decimal(str(order.balance_amount)),
        "govt_fees": Decimal(str(order.govt_fees)),
        "incidental_cost": Decimal(str(order.incidental_cost)),
        "profit_amount": Decimal(str(order.profit_amount)),
        "payment_status": str(order.payment_status),
        "lead_source": str(order.lead_source),
        "order_date": order.order_date,
        "proforma_invoice_no": order.proforma_invoice_no,
        "tax_invoice_no": order.tax_invoice_no,
        "reimbursement_note": order.reimbursement_note,
        "notes": order.notes,
        "client_name": order.client.client_name if order.client else "",
        "contact_no": order.client.contact_phone if order.client else "",
    }

    # Financial Field updates & Decimal-safe validations
    new_val = Decimal(str(data.order_value)) if data.order_value is not None else old_values["order_value"]
    new_rcvd = Decimal(str(data.amount_received)) if data.amount_received is not None else old_values["amount_received"]
    new_g_fee = Decimal(str(data.govt_fees)) if data.govt_fees is not None else old_values["govt_fees"]
    new_i_cost = Decimal(str(data.incidental_cost)) if data.incidental_cost is not None else old_values["incidental_cost"]

    if new_val < Decimal("0.00") or new_rcvd < Decimal("0.00") or new_g_fee < Decimal("0.00") or new_i_cost < Decimal("0.00"):
        raise ValueError("Financial amounts cannot be negative.")

    if new_rcvd > new_val:
        raise ValueError("Advance Amount cannot be greater than Total Amount.")

    # Server Calculations
    new_bal = max(Decimal("0.00"), new_val - new_rcvd)
    new_profit = new_val - new_g_fee - new_i_cost

    # Payment status derivation
    if data.payment_status:
        new_pmt_status = data.payment_status.upper()
    else:
        if new_rcvd >= new_val and new_val > Decimal("0.00"):
            new_pmt_status = "FULLY_PAID"
        elif new_rcvd > Decimal("0.00"):
            new_pmt_status = "PARTIALLY_PAID"
        else:
            new_pmt_status = "PENDING"

    # Update SalesOrder attributes
    order.order_value = new_val
    order.amount_received = new_rcvd
    order.balance_amount = new_bal
    order.govt_fees = new_g_fee
    order.incidental_cost = new_i_cost
    order.profit_amount = new_profit
    order.payment_status = new_pmt_status

    if data.lead_source is not None:
        order.lead_source = data.lead_source
    if data.order_date is not None:
        order.order_date = data.order_date
    if data.proforma_invoice_no is not None:
        order.proforma_invoice_no = data.proforma_invoice_no.strip() if data.proforma_invoice_no.strip() else None
    if data.tax_invoice_no is not None:
        order.tax_invoice_no = data.tax_invoice_no.strip() if data.tax_invoice_no.strip() else None
    if data.reimbursement_note is not None:
        order.reimbursement_note = data.reimbursement_note.strip() if data.reimbursement_note.strip() else None
    if data.notes is not None:
        order.notes = data.notes.strip() if data.notes.strip() else None

    # Update client if client_name or contact_no provided
    if order.client:
        if data.client_name and data.client_name.strip():
            order.client.client_name = data.client_name.strip()
        if data.contact_no is not None and data.contact_no.strip():
            order.client.contact_phone = data.contact_no.strip()

    # Compare changes and create audit log
    changes = []
    if old_values["order_value"] != order.order_value:
        changes.append(f"Total Amount: {format_inr(old_values['order_value'])} -> {format_inr(order.order_value)}")
    if old_values["amount_received"] != order.amount_received:
        changes.append(f"Advance Amount: {format_inr(old_values['amount_received'])} -> {format_inr(order.amount_received)}")
    if old_values["balance_amount"] != order.balance_amount:
        changes.append(f"Pending Amount: {format_inr(old_values['balance_amount'])} -> {format_inr(order.balance_amount)}")
    if old_values["govt_fees"] != order.govt_fees:
        changes.append(f"Govt Fees: {format_inr(old_values['govt_fees'])} -> {format_inr(order.govt_fees)}")
    if old_values["incidental_cost"] != order.incidental_cost:
        changes.append(f"Incidental Cost: {format_inr(old_values['incidental_cost'])} -> {format_inr(order.incidental_cost)}")
    if old_values["profit_amount"] != order.profit_amount:
        changes.append(f"Profits: {format_inr(old_values['profit_amount'])} -> {format_inr(order.profit_amount)}")
    if old_values["payment_status"] != order.payment_status:
        changes.append(f"Payment Status: {old_values['payment_status']} -> {order.payment_status}")
    if old_values["proforma_invoice_no"] != order.proforma_invoice_no:
        changes.append(f"Proforma Invoice: {old_values['proforma_invoice_no'] or 'None'} -> {order.proforma_invoice_no or 'None'}")
    if old_values["tax_invoice_no"] != order.tax_invoice_no:
        changes.append(f"Tax Invoice: {old_values['tax_invoice_no'] or 'None'} -> {order.tax_invoice_no or 'None'}")
    if old_values["reimbursement_note"] != order.reimbursement_note:
        changes.append(f"Reimbursement Note: {old_values['reimbursement_note'] or 'None'} -> {order.reimbursement_note or 'None'}")
    if old_values["notes"] != order.notes:
        changes.append(f"Remarks: {old_values['notes'] or 'None'} -> {order.notes or 'None'}")
    if old_values["client_name"] != (order.client.client_name if order.client else ""):
        changes.append(f"Client Name: {old_values['client_name']} -> {order.client.client_name if order.client else ''}")
    if old_values["contact_no"] != (order.client.contact_phone if order.client else ""):
        changes.append(f"Contact No: {old_values['contact_no']} -> {order.client.contact_phone if order.client else ''}")
    if old_values["lead_source"] != order.lead_source:
        changes.append(f"Lead Source: {old_values['lead_source']} -> {order.lead_source}")

    if order.application:
        comment_str = f"Sales order '{order.order_number}' updated: " + (", ".join(changes) if changes else "No field changes detected.")
        if len(comment_str) > 1000:
            comment_str = comment_str[:997] + "..."
        old_val_summary = f"Val:{old_values['order_value']}|Recvd:{old_values['amount_received']}|Pmt:{old_values['payment_status']}"
        new_val_summary = f"Val:{order.order_value}|Recvd:{order.amount_received}|Pmt:{order.payment_status}"
        if len(old_val_summary) > 255:
            old_val_summary = old_val_summary[:255]
        if len(new_val_summary) > 255:
            new_val_summary = new_val_summary[:255]

        activity = ApplicationActivityLog(
            application_id=order.application.application_id,
            actor_user_id=current_user.user_id,
            action_type="SALES_UPDATE",
            old_value=old_val_summary,
            new_value=new_val_summary,
            comment=comment_str,
            created_at=datetime.now(timezone.utc),
        )
        session.add(activity)

    session.flush()

    c_name = order.client.client_name if order.client else "—"
    c_phone = order.client.contact_phone if order.client else "—"
    s_name = order.service.service_name if order.service else "—"
    s_code = order.service.service_code if order.service else ""
    sp_name = f"{order.salesperson.first_name} {order.salesperson.last_name}".strip() if order.salesperson else "—"
    sp_code = order.salesperson.employee_code if order.salesperson else ""

    app_id = order.application.application_id if order.application else None
    app_num = order.application.application_number if order.application else None
    op_st = order.application.application_status if order.application else order.confirmation_status

    assigned_to_id = order.application.assigned_to_user_id if order.application else None
    assigned_to_name = (
        f"{order.application.assigned_to.first_name} {order.application.assigned_to.last_name}".strip()
        if (order.application and order.application.assigned_to)
        else "Unassigned"
    )
    assigned_to_code = (
        order.application.assigned_to.employee_code
        if (order.application and order.application.assigned_to)
        else None
    )

    return SalesOrderDetailRead(
        s_no=1,
        order_id=order.order_id,
        order_number=order.order_number,
        company_id=order.company_id,
        client_id=order.client_id,
        service_id=order.service_id,
        salesperson_user_id=order.salesperson_user_id,
        lead_source=order.lead_source,
        order_date=order.order_date,
        formatted_date=order.order_date.strftime("%d %b %Y"),
        order_value=order.order_value,
        amount_received=order.amount_received,
        balance_amount=order.balance_amount,
        govt_fees=order.govt_fees,
        incidental_cost=order.incidental_cost,
        profit_amount=order.profit_amount,
        payment_status=order.payment_status,
        confirmation_status=order.confirmation_status,
        confirmed_at=order.confirmed_at,
        proforma_invoice_no=order.proforma_invoice_no,
        tax_invoice_no=order.tax_invoice_no,
        reimbursement_note=order.reimbursement_note,
        notes=order.notes,
        remarks=order.notes,
        created_at=order.created_at,
        updated_at=order.updated_at,
        client_name=c_name,
        contact_no=c_phone,
        service_name=s_name,
        service_code=s_code,
        salesperson_name=sp_name,
        salesperson_code=sp_code,
        assigned_to_user_id=assigned_to_id,
        assigned_to_name=assigned_to_name,
        assigned_to_code=assigned_to_code,
        work_status=op_st,
        application_id=app_id,
        application_number=app_num,
        operation_status=op_st,
    )


def confirm_sales_order(
    session: Session,
    order_id: uuid.UUID,
    current_user: User,
    assignee_user_id: Optional[uuid.UUID] = None,
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

    # Look up assigned target: either specified assignee_user_id or default Mansi Singhal / Operations lead
    assigned_target = None
    if assignee_user_id:
        target_user = session.get(User, assignee_user_id)
        if (
            target_user
            and target_user.account_status == "ACTIVE"
            and target_user.company_id == order.company_id
            and not operation_service.is_disallowed_ops_assignee(target_user)
        ):
            assigned_target = target_user

    if not assigned_target:
        assigned_target = session.execute(
            select(User)
            .outerjoin(Department, User.department_id == Department.department_id)
            .where(
                User.company_id == order.company_id,
                User.account_status == "ACTIVE",
                or_(
                    User.employee_code == "CG0003",
                    User.first_name.ilike("%mansi%"),
                    Department.department_code.in_(["OP", "OPS", "OPERATIONS"]),
                    Department.department_name.ilike("%operation%"),
                ),
            )
            .order_by(
                case(
                    (User.employee_code == "CG0003", 0),
                    (User.first_name.ilike("%mansi%"), 1),
                    else_=2,
                ),
                User.created_at.asc(),
            )
        ).scalars().first()

    default_assigned_to = assigned_target.user_id if assigned_target else None
    default_assigned_by = current_user.user_id if assigned_target else None
    default_assigned_at = now_utc if assigned_target else None
    default_app_status = "ASSIGNED" if assigned_target else "UNASSIGNED"

    app_num = generate_application_number(session, order.order_date)

    new_app = OperationApplication(
        application_number=app_num,
        sales_order_id=order.order_id,
        company_id=order.company_id,
        client_id=order.client_id,
        service_id=order.service_id,
        assigned_to_user_id=default_assigned_to,
        assigned_by_user_id=default_assigned_by,
        assigned_at=default_assigned_at,
        priority="MEDIUM",
        application_status=default_app_status,
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

    if assigned_target:
        history = ApplicationAssignmentHistory(
            application_id=new_app.application_id,
            assigned_by_user_id=current_user.user_id,
            previous_assignee_user_id=None,
            new_assignee_user_id=assigned_target.user_id,
            reason="Initial task assignment on sales entry confirmation",
            assigned_at=now_utc,
        )
        session.add(history)

    activity = ApplicationActivityLog(
        application_id=new_app.application_id,
        actor_user_id=current_user.user_id,
        action_type="ASSIGNMENT_CHANGE" if assigned_target else "STATUS_CHANGE",
        old_value="NONE",
        new_value=f"{assigned_target.first_name} {assigned_target.last_name} ({assigned_target.employee_code})" if assigned_target else "UNASSIGNED",
        comment=(
            f"Order '{order.order_number}' confirmed and assigned to {assigned_target.first_name} {assigned_target.last_name} ({assigned_target.employee_code})."
            if assigned_target
            else f"Order '{order.order_number}' confirmed and handed over from Sales."
        ),
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
        assigned_to_user_id=new_app.assigned_to_user_id,
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
        ("JUSTDIAL", "Justdial"),
        ("INDIAMART", "IndiaMART"),
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
        FilterOptionItem(id="JUSTDIAL", label="Justdial"),
        FilterOptionItem(id="INDIAMART", label="IndiaMART"),
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


def get_sales_register_data(
    session: Session,
    current_user: User,
    page: int = 1,
    limit: int = 50,
    search: Optional[str] = None,
    payment_status: Optional[str] = None,
    work_status: Optional[str] = None,
    employee_id: Optional[uuid.UUID] = None,
    service_id: Optional[uuid.UUID] = None,
    lead_source: Optional[str] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    sort_by: str = "order_date",
    sort_dir: str = "desc",
) -> SalesRegisterResponse:
    """Retrieve filtered and paginated Sales Register records covering all 20 columns."""
    try:
        scope_ctx = permissions.resolve_data_scope_context(session, current_user, "SALES_MY_ORDERS")
    except permissions.PermissionDeniedError:
        try:
            scope_ctx = permissions.resolve_data_scope_context(session, current_user, "SALES_ALL_ORDERS")
        except permissions.PermissionDeniedError:
            scope_ctx = permissions.resolve_data_scope_context(session, current_user, "SALES_DASHBOARD")

    if scope_ctx.scope == "SELF":
        employee_id = current_user.user_id

    query = (
        select(SalesOrder)
        .join(ClientMaster, SalesOrder.client_id == ClientMaster.client_id)
        .join(ServiceMaster, SalesOrder.service_id == ServiceMaster.service_id)
        .join(User, SalesOrder.salesperson_user_id == User.user_id)
        .outerjoin(OperationApplication, SalesOrder.order_id == OperationApplication.sales_order_id)
    )

    query = _apply_sales_filters(
        query,
        scope_ctx=scope_ctx,
        start_date=from_date,
        end_date=to_date,
        employee_id=employee_id,
        service_id=service_id,
        lead_source=lead_source,
        payment_status=payment_status,
    )

    if work_status and work_status != "ALL":
        ws_upper = work_status.upper()
        if ws_upper in ("DRAFT", "CONFIRMED", "CANCELLED"):
            query = query.where(
                or_(
                    SalesOrder.confirmation_status == ws_upper,
                    OperationApplication.application_status == ws_upper,
                )
            )
        else:
            query = query.where(OperationApplication.application_status == ws_upper)

    if search and search.strip():
        term = f"%{search.strip()}%"
        query = query.where(
            or_(
                ClientMaster.client_name.ilike(term),
                ClientMaster.contact_phone.ilike(term),
                SalesOrder.order_number.ilike(term),
                SalesOrder.proforma_invoice_no.ilike(term),
                SalesOrder.tax_invoice_no.ilike(term),
                SalesOrder.reimbursement_note.ilike(term),
                SalesOrder.notes.ilike(term),
                ServiceMaster.service_name.ilike(term),
                User.first_name.ilike(term),
                User.last_name.ilike(term),
                User.employee_code.ilike(term),
            )
        )

    all_matched = session.execute(query).scalars().all()
    total_count = len(all_matched)

    total_sales = sum((o.order_value for o in all_matched), Decimal("0.00"))
    total_advance = sum((o.amount_received for o in all_matched), Decimal("0.00"))
    total_pending = sum((o.balance_amount for o in all_matched), Decimal("0.00"))
    total_govt = sum((o.govt_fees for o in all_matched), Decimal("0.00"))
    total_incidental = sum((o.incidental_cost for o in all_matched), Decimal("0.00"))
    total_profit = sum((o.profit_amount for o in all_matched), Decimal("0.00"))

    summary = SalesRegisterSummary(
        total_orders=total_count,
        total_sales=total_sales,
        total_advance=total_advance,
        total_pending=total_pending,
        total_govt_fees=total_govt,
        total_incidental_cost=total_incidental,
        total_profits=total_profit,
        formatted_total_sales=format_inr(total_sales),
        formatted_total_advance=format_inr(total_advance),
        formatted_total_pending=format_inr(total_pending),
        formatted_total_govt_fees=format_inr(total_govt),
        formatted_total_incidental_cost=format_inr(total_incidental),
        formatted_total_profits=format_inr(total_profit),
    )

    if sort_dir.lower() == "asc":
        query = query.order_by(SalesOrder.order_date.asc(), SalesOrder.created_at.asc())
    else:
        query = query.order_by(SalesOrder.order_date.desc(), SalesOrder.created_at.desc())

    safe_page = max(1, page)
    safe_limit = max(1, min(100, limit))
    offset_val = (safe_page - 1) * safe_limit

    paged_orders = session.execute(query.offset(offset_val).limit(safe_limit)).scalars().all()

    items: List[SalesOrderDetailRead] = []
    for idx, o in enumerate(paged_orders):
        s_no = offset_val + idx + 1
        c_name = o.client.client_name if o.client else "—"
        c_phone = o.client.contact_phone if o.client else "—"
        s_name = o.service.service_name if o.service else "—"
        s_code = o.service.service_code if o.service else ""
        sp_name = f"{o.salesperson.first_name} {o.salesperson.last_name}".strip() if o.salesperson else "—"
        sp_code = o.salesperson.employee_code if o.salesperson else ""

        app_id = o.application.application_id if o.application else None
        app_num = o.application.application_number if o.application else None
        op_st = o.application.application_status if o.application else o.confirmation_status

        assigned_to_id = o.application.assigned_to_user_id if o.application else None
        assigned_to_name = (
            f"{o.application.assigned_to.first_name} {o.application.assigned_to.last_name}".strip()
            if (o.application and o.application.assigned_to)
            else "Unassigned"
        )
        assigned_to_code = (
            o.application.assigned_to.employee_code
            if (o.application and o.application.assigned_to)
            else None
        )

        items.append(
            SalesOrderDetailRead(
                s_no=s_no,
                order_id=o.order_id,
                order_number=o.order_number,
                company_id=o.company_id,
                client_id=o.client_id,
                service_id=o.service_id,
                salesperson_user_id=o.salesperson_user_id,
                lead_source=o.lead_source,
                order_date=o.order_date,
                formatted_date=o.order_date.strftime("%d %b %Y"),
                order_value=o.order_value,
                amount_received=o.amount_received,
                balance_amount=o.balance_amount,
                govt_fees=o.govt_fees,
                incidental_cost=o.incidental_cost,
                profit_amount=o.profit_amount,
                payment_status=o.payment_status,
                confirmation_status=o.confirmation_status,
                confirmed_at=o.confirmed_at,
                proforma_invoice_no=o.proforma_invoice_no,
                tax_invoice_no=o.tax_invoice_no,
                reimbursement_note=o.reimbursement_note,
                notes=o.notes,
                remarks=o.notes,
                created_at=o.created_at,
                updated_at=o.updated_at,
                client_name=c_name,
                contact_no=c_phone,
                service_name=s_name,
                service_code=s_code,
                salesperson_name=sp_name,
                salesperson_code=sp_code,
                assigned_to_user_id=assigned_to_id,
                assigned_to_name=assigned_to_name,
                assigned_to_code=assigned_to_code,
                work_status=op_st,
                application_id=app_id,
                application_number=app_num,
                operation_status=op_st,
            )
        )

    total_pages = (total_count + safe_limit - 1) // safe_limit if total_count > 0 else 1

    return SalesRegisterResponse(
        items=items,
        total_count=total_count,
        page=safe_page,
        limit=safe_limit,
        total_pages=total_pages,
        summary=summary,
    )


def get_sales_form_options(
    session: Session,
    current_user: User,
) -> SalesFormOptionsResponse:
    """Retrieve dropdown options for the Sales Entry form, respecting data scoping."""
    # 1. Services
    services = session.execute(
        select(ServiceMaster).where(ServiceMaster.status == "ACTIVE").order_by(ServiceMaster.service_name.asc())
    ).scalars().all()
    service_opts = [
        SalesServiceOption(
            service_id=s.service_id,
            service_code=s.service_code,
            service_name=s.service_name,
            category=s.category,
            base_price=s.base_price,
            govt_fee=s.govt_fee,
        )
        for s in services
    ]

    # 2. Salespersons scoped by RBAC
    try:
        scope_ctx = permissions.resolve_data_scope_context(session, current_user, "SALES_CONFIRMED_ORDER")
    except permissions.PermissionDeniedError:
        scope_ctx = permissions.DataScopeContext(
            scope="SELF",
            user_id=current_user.user_id,
            company_id=current_user.company_id,
            department_id=current_user.department_id or uuid.uuid4(),
            team_user_ids=[current_user.user_id],
        )

    if scope_ctx.scope == "SELF":
        sp_users = [current_user]
        can_select = False
    elif scope_ctx.scope == "TEAM":
        sp_users = session.execute(
            select(User)
            .outerjoin(Department, User.department_id == Department.department_id)
            .outerjoin(Designation, User.designation_id == Designation.designation_id)
            .where(
                User.user_id.in_(scope_ctx.team_user_ids),
                User.account_status == "ACTIVE",
            )
            .order_by(User.first_name.asc())
        ).scalars().all()
        can_select = True
    else:  # COMPANY, ALL
        sp_users = session.execute(
            select(User)
            .outerjoin(Department, User.department_id == Department.department_id)
            .outerjoin(Designation, User.designation_id == Designation.designation_id)
            .where(
                User.company_id == current_user.company_id if scope_ctx.scope == "COMPANY" else True,
                User.account_status == "ACTIVE",
            )
            .order_by(User.first_name.asc())
        ).scalars().all()
        can_select = True

    employee_opts = [
        SalesEmployeeOption(
            user_id=u.user_id,
            employee_code=u.employee_code,
            full_name=f"{u.first_name} {u.last_name}".strip(),
            department_name=u.department.department_name if u.department else None,
            designation_name=u.designation.designation_name if u.designation else None,
        )
        for u in sp_users
    ]

    # 3. Clients in company
    clients = session.execute(
        select(ClientMaster).where(
            ClientMaster.company_id == current_user.company_id,
            ClientMaster.status == "ACTIVE",
        ).order_by(ClientMaster.client_name.asc()).limit(300)
    ).scalars().all()

    client_opts = [
        SalesClientOption(
            client_id=c.client_id,
            client_name=c.client_name,
            contact_phone=c.contact_phone,
            contact_email=c.contact_email,
            contact_person=c.contact_person,
            entity_type=c.entity_type,
        )
        for c in clients
    ]

    # 4. Eligible Operations Assignees
    ops_assignees = get_eligible_operations_assignees(session, current_user.company_id)

    lead_sources = ["WEBSITE", "REFERRAL", "DIRECT", "JUSTDIAL", "INDIAMART", "OTHERS"]
    comp = session.get(Company, current_user.company_id)
    comp_name = comp.company_name if comp else "GoCompliance CRM"

    return SalesFormOptionsResponse(
        services=service_opts,
        salespersons=employee_opts,
        clients=client_opts,
        lead_sources=lead_sources,
        operations_assignees=ops_assignees,
        default_salesperson_id=current_user.user_id,
        can_select_salesperson=can_select,
        company_id=current_user.company_id,
        company_name=comp_name,
    )


def get_eligible_operations_assignees(
    session: Session,
    company_id: uuid.UUID,
) -> List[SalesEmployeeOption]:
    """Retrieve active employees in the Operations department/roles for task assignment (strictly excluding Sales, Admin, and Directors)."""
    from app.services.operation_service import is_disallowed_ops_assignee

    stmt = (
        select(User)
        .outerjoin(Department, User.department_id == Department.department_id)
        .outerjoin(Designation, User.designation_id == Designation.designation_id)
        .where(
            User.company_id == company_id,
            User.account_status == "ACTIVE",
            or_(
                Department.department_name.ilike("%operation%"),
                Department.department_code.ilike("%operation%"),
                Department.department_code.ilike("%ops%"),
                Designation.designation_name.ilike("%operation%"),
                Designation.designation_code.ilike("%ops%"),
            ),
        )
        .order_by(User.first_name.asc(), User.last_name.asc())
    )
    users = session.execute(stmt).scalars().all()
    eligible = [u for u in users if not is_disallowed_ops_assignee(u)]

    return [
        SalesEmployeeOption(
            user_id=u.user_id,
            employee_code=u.employee_code,
            full_name=f"{u.first_name} {u.last_name}".strip(),
            department_name=u.department.department_name if u.department else None,
            designation_name=u.designation.designation_name if u.designation else None,
        )
        for u in eligible
    ]


def assign_sales_order_operations(
    session: Session,
    order_id: uuid.UUID,
    assignee_user_id: uuid.UUID,
    assigned_by: User,
    priority: str = "MEDIUM",
    target_due_date: Optional[date] = None,
    notes: Optional[str] = None,
) -> SalesOrderDetailRead:
    """Assign or reassign an order's operations application to an eligible Operations team member."""
    order = session.get(SalesOrder, order_id)
    if not order:
        raise SalesOrderNotFoundError(f"Sales order with ID '{order_id}' not found.")

    # Authorization Check: order creator / salesperson, Operations manager / head / super admin / director
    is_authorized = False
    if getattr(assigned_by, "is_super_admin", False):
        is_authorized = True
    elif str(assigned_by.user_id) == str(order.salesperson_user_id):
        is_authorized = True
    else:
        for mod_code in ("OPERATIONS", "OPS_APPLICATIONS", "ADMIN", "SALES"):
            try:
                scope_ctx = permissions.resolve_data_scope_context(session, assigned_by, mod_code)
                if scope_ctx and scope_ctx.scope in ("COMPANY", "DEPARTMENT", "TEAM", "ALL"):
                    is_authorized = True
                    break
            except permissions.PermissionDeniedError:
                continue

    if not is_authorized and assigned_by.department:
        dept_name = (assigned_by.department.department_name or "").upper()
        if "OPERATION" in dept_name or "ADMIN" in dept_name or getattr(assigned_by, "is_reporting_manager", False):
            is_authorized = True

    if not is_authorized:
        if getattr(assigned_by, "is_reporting_manager", False):
            is_authorized = True
        else:
            raise SalesOrderPermissionError("Only authorized Operations managers/heads or the order salesperson can assign or reassign work.")

    # Ensure application exists (confirm if draft)
    if not order.application:
        confirm_sales_order(session, order_id, assigned_by)
        session.refresh(order)

    app = order.application
    if not app:
        raise ValueError("Could not initialize operations application for this order.")

    # Validate assignee is an active employee in the same company
    from app.services.operation_service import is_disallowed_ops_assignee

    assignee = session.get(User, assignee_user_id)
    if not assignee or assignee.account_status != "ACTIVE":
        raise ValueError(f"Target assignee '{assignee_user_id}' is not an active employee.")
    if assignee.company_id != order.company_id:
        raise ValueError("Assignee does not belong to the same company as the sales order.")
    if is_disallowed_ops_assignee(assignee):
        raise ValueError("Task cannot be assigned to Sales, Administration, or Director personnel.")

    # Call operation_service.assign_task
    operation_service.assign_task(
        session=session,
        application_id=app.application_id,
        assignee_user_id=assignee_user_id,
        assigned_by=assigned_by,
        priority=priority or "MEDIUM",
        target_due_date=target_due_date,
        notes=notes,
    )
    session.flush()
    session.refresh(order)
    session.refresh(app)

    c_name = order.client.client_name if order.client else "—"
    c_phone = order.client.contact_phone if order.client else "—"
    s_name = order.service.service_name if order.service else "—"
    s_code = order.service.service_code if order.service else ""
    sp_name = f"{order.salesperson.first_name} {order.salesperson.last_name}".strip() if order.salesperson else "—"
    sp_code = order.salesperson.employee_code if order.salesperson else ""

    assigned_to_name = (
        f"{app.assigned_to.first_name} {app.assigned_to.last_name}".strip()
        if app.assigned_to
        else "Unassigned"
    )
    assigned_to_code = app.assigned_to.employee_code if app.assigned_to else None

    return SalesOrderDetailRead(
        s_no=1,
        order_id=order.order_id,
        order_number=order.order_number,
        company_id=order.company_id,
        client_id=order.client_id,
        service_id=order.service_id,
        salesperson_user_id=order.salesperson_user_id,
        lead_source=order.lead_source,
        order_date=order.order_date,
        formatted_date=order.order_date.strftime("%d %b %Y"),
        order_value=order.order_value,
        amount_received=order.amount_received,
        balance_amount=order.balance_amount,
        govt_fees=order.govt_fees,
        incidental_cost=order.incidental_cost,
        profit_amount=order.profit_amount,
        payment_status=order.payment_status,
        confirmation_status=order.confirmation_status,
        confirmed_at=order.confirmed_at,
        proforma_invoice_no=order.proforma_invoice_no,
        tax_invoice_no=order.tax_invoice_no,
        reimbursement_note=order.reimbursement_note,
        notes=order.notes,
        remarks=order.notes,
        created_at=order.created_at,
        updated_at=order.updated_at,
        client_name=c_name,
        contact_no=c_phone,
        service_name=s_name,
        service_code=s_code,
        salesperson_name=sp_name,
        salesperson_code=sp_code,
        assigned_to_user_id=app.assigned_to_user_id,
        assigned_to_name=assigned_to_name,
        assigned_to_code=assigned_to_code,
        work_status=app.application_status,
        application_id=app.application_id,
        application_number=app.application_number,
        operation_status=app.application_status,
    )


def export_sales_register_csv(
    session: Session,
    current_user: User,
    search: Optional[str] = None,
    payment_status: Optional[str] = None,
    work_status: Optional[str] = None,
    employee_id: Optional[uuid.UUID] = None,
    service_id: Optional[uuid.UUID] = None,
    lead_source: Optional[str] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
) -> Tuple[str, str]:
    """Generate CSV of Sales Register matching all 20 columns in the director's order."""
    reg_response = get_sales_register_data(
        session=session,
        current_user=current_user,
        page=1,
        limit=100000,
        search=search,
        payment_status=payment_status,
        work_status=work_status,
        employee_id=employee_id,
        service_id=service_id,
        lead_source=lead_source,
        from_date=from_date,
        to_date=to_date,
    )

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "S.No",
        "Date",
        "Client Name",
        "Contact No",
        "Source",
        "Work",
        "Converted By",
        "Assigned To",
        "Work Status",
        "Total Amount",
        "Advance Amount",
        "Pending Amount",
        "Payment Status",
        "Proforma Invoice No.",
        "Tax Invoice No.",
        "Reimbursement Note",
        "Govt Fees",
        "Incidental Cost",
        "Profits",
        "Remarks",
    ])

    for row in reg_response.items:
        writer.writerow([
            row.s_no,
            row.formatted_date or row.order_date.strftime("%d/%m/%Y"),
            row.client_name or "",
            row.contact_no or "",
            row.lead_source or "",
            row.service_name or "",
            row.salesperson_name or "",
            row.assigned_to_name or "Unassigned",
            row.work_status or row.confirmation_status,
            f"{row.order_value:.2f}",
            f"{row.amount_received:.2f}",
            f"{row.balance_amount:.2f}",
            row.payment_status or "",
            row.proforma_invoice_no or "",
            row.tax_invoice_no or "",
            row.reimbursement_note or "",
            f"{row.govt_fees:.2f}",
            f"{row.incidental_cost:.2f}",
            f"{row.profit_amount:.2f}",
            row.notes or "",
        ])

    today_str = date.today().strftime("%Y%m%d")
    filename = f"sales_register_{today_str}.csv"
    return output.getvalue(), filename
