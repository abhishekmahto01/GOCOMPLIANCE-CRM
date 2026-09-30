"""Accounts & Financial Management Service layer for Gocompliances CRM."""
import csv
import io
import json
import os
import uuid
from datetime import date, datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.accounts_audit_log import AccountsAuditLog
from app.models.accounts_expense import AccountsExpense
from app.models.accounts_follow_up import AccountsFollowUp
from app.models.accounts_invoice import AccountsInvoice
from app.models.client import ClientMaster
from app.models.company import Company
from app.models.operation_application import OperationApplication
from app.models.payment_transaction import PaymentTransaction
from app.models.sales_order import SalesOrder
from app.models.user import User
from app.schemas.accounts import (
    AccountsDashboardResponse,
    AccountsExpenseCreate,
    AccountsExpenseListResponse,
    AccountsExpenseRead,
    AccountsFilterOptionItem,
    AccountsFilterOptions,
    AccountsFollowUpCreate,
    AccountsFollowUpRead,
    AccountsInvoiceCreate,
    AccountsInvoiceListResponse,
    AccountsInvoiceRead,
    AccountsInvoiceUpdate,
    AccountsKpiSummary,
    AgeingBreakdownItem,
    CategoryExpenseItem,
    CollectionsTrendPoint,
    CompanyFinancialItem,
    OutstandingAgeingSummary,
    OutstandingItemRead,
    OutstandingResponse,
    PaymentRegisterItemRead,
    PaymentRegisterResponse,
    PaymentRegisterSummary,
    PaymentTransactionCreate,
    PaymentTransactionListResponse,
    PaymentTransactionRead,
    PaymentTransactionReverse,
    PaymentTransactionVerify,
    AccountsExpenseApproval,
    AccountsReimbursementSettle,
    RecentTransactionItem,
    TopOutstandingItem,
)
from app.services import permissions

UPLOAD_DIR = os.path.join(os.getcwd(), "uploads", "accounts")
RECEIPTS_DIR = os.path.join(UPLOAD_DIR, "receipts")
INVOICES_DIR = os.path.join(UPLOAD_DIR, "invoices")
BILLS_DIR = os.path.join(UPLOAD_DIR, "bills")

for d in (RECEIPTS_DIR, INVOICES_DIR, BILLS_DIR):
    os.makedirs(d, exist_ok=True)


def format_inr(val: Optional[float]) -> str:
    """Format numeric amount into Indian Rupee style string."""
    if val is None:
        return "₹0.00"
    is_neg = val < 0
    abs_val = abs(val)
    int_part = int(abs_val)
    dec_part = f"{abs_val - int_part:.2f}"[2:]
    s = str(int_part)
    if len(s) <= 3:
        formatted = s
    else:
        last3 = s[-3:]
        rest = s[:-3]
        groups = []
        while len(rest) > 2:
            groups.append(rest[-2:])
            rest = rest[:-2]
        if rest:
            groups.append(rest)
        groups.reverse()
        formatted = ",".join(groups) + "," + last3
    res = f"₹{formatted}.{dec_part}"
    return f"-{res}" if is_neg else res


def sanitize_csv_field(val: Any) -> str:
    """Sanitize string for CSV export to prevent spreadsheet formula injection."""
    if val is None:
        return ""
    s = str(val).strip()
    if s.startswith(("=", "+", "-", "@")):
        return f"'{s}"
    return s


def _generate_payment_number(session: Session, company_id: uuid.UUID) -> str:
    """Generate sequential voucher number e.g. PAY-2026-0001."""
    year = date.today().year
    prefix = f"PAY-{year}-"
    stmt = (
        select(func.count(PaymentTransaction.payment_id))
        .where(PaymentTransaction.payment_number.like(f"{prefix}%"))
    )
    count = session.execute(stmt).scalar() or 0
    return f"{prefix}{count + 1:04d}"


def _generate_expense_number(session: Session, company_id: uuid.UUID) -> str:
    """Generate sequential expense number e.g. EXP-2026-0001."""
    year = date.today().year
    prefix = f"EXP-{year}-"
    stmt = (
        select(func.count(AccountsExpense.expense_id))
        .where(AccountsExpense.expense_number.like(f"{prefix}%"))
    )
    count = session.execute(stmt).scalar() or 0
    return f"{prefix}{count + 1:04d}"


def _log_accounts_audit(
    session: Session,
    company_id: uuid.UUID,
    entity_type: str,
    entity_id: uuid.UUID,
    action: str,
    actor_user_id: uuid.UUID,
    old_values: Optional[Dict[str, Any]] = None,
    new_values: Optional[Dict[str, Any]] = None,
    reason: Optional[str] = None,
    ip_address: Optional[str] = None,
) -> None:
    """Write immutable audit record."""
    audit = AccountsAuditLog(
        audit_id=uuid.uuid4(),
        company_id=company_id,
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        actor_user_id=actor_user_id,
        old_values=json.dumps(old_values, default=str) if old_values else None,
        new_values=json.dumps(new_values, default=str) if new_values else None,
        reason=reason,
        ip_address=ip_address,
        created_at=datetime.now(timezone.utc),
    )
    session.add(audit)


def _reconcile_legacy_advances(session: Session, orders: List[SalesOrder]) -> None:
    """Transparently ensure legacy advance amounts on existing Sales Orders have verified payment records.
    
    Prevents double-counting existing advances while maintaining complete transaction audit integrity.
    """
    for order in orders:
        if float(order.amount_received or 0) > 0:
            # Check if verified payment transactions already exist
            existing_verified = sum(
                float(p.amount)
                for p in order.payment_transactions
                if p.verification_status == "VERIFIED"
            )
            legacy_amount = float(order.amount_received)
            if existing_verified < legacy_amount:
                diff = legacy_amount - existing_verified
                # Create an opening/legacy collection record for the difference
                opening_payment = PaymentTransaction(
                    payment_id=uuid.uuid4(),
                    company_id=order.company_id,
                    sales_order_id=order.order_id,
                    payment_number=_generate_payment_number(session, order.company_id),
                    amount=diff,
                    payment_date=order.order_date,
                    payment_mode="LEGACY_OPENING",
                    transaction_reference="Opening Advance Balance",
                    receiving_account="Opening Accounts Ledger",
                    remark="Opening / Legacy advance collection recorded at Sales Entry",
                    submitted_by_user_id=order.salesperson_user_id,
                    submitted_at=order.created_at or datetime.now(timezone.utc),
                    verification_status="VERIFIED",
                    verified_by_user_id=order.salesperson_user_id,
                    verified_at=order.created_at or datetime.now(timezone.utc),
                    is_opening_balance=True,
                    created_at=order.created_at or datetime.now(timezone.utc),
                )
                session.add(opening_payment)
                order.payment_transactions.append(opening_payment)
    session.flush()


def _recalculate_order_financials(session: Session, order: SalesOrder) -> None:
    """Recalculate order's verified received amount, balance amount, and payment status."""
    verified_sum = sum(
        float(p.amount)
        for p in order.payment_transactions
        if p.verification_status == "VERIFIED"
    )
    total_val = float(order.order_value or 0)
    order.amount_received = verified_sum
    order.balance_amount = max(0.0, total_val - verified_sum)
    
    today = date.today()
    if verified_sum >= total_val:
        order.payment_status = "FULLY_PAID"
    elif verified_sum > 0:
        order.payment_status = "PARTIALLY_PAID"
    else:
        order.payment_status = "PENDING"

    session.add(order)
    session.flush()


def _apply_accounts_scope(
    stmt: Any,
    user: User,
    context: permissions.DataScopeContext,
) -> Any:
    """Apply RBAC data scope filters to SalesOrder or Accounts queries."""
    if context.scope == "ALL":
        return stmt
    if context.scope in ("COMPANY", "DEPARTMENT"):
        return stmt.where(SalesOrder.company_id == context.company_id)
    if context.scope == "TEAM":
        return stmt.where(
            or_(
                SalesOrder.salesperson_user_id.in_(context.team_user_ids),
                SalesOrder.company_id == context.company_id,
            )
        )
    if context.scope == "SELF":
        return stmt.where(
            or_(
                SalesOrder.salesperson_user_id == user.user_id,
                SalesOrder.company_id == context.company_id,
            )
        )
    return stmt.where(SalesOrder.company_id == context.company_id)


# -----------------------------------------------------------------------------
# 1. Filter Options Provider
# -----------------------------------------------------------------------------
def get_accounts_filter_options(session: Session, user: User) -> AccountsFilterOptions:
    """Provide permitted dynamic filter dropdown choices."""
    scope_ctx = permissions.resolve_data_scope_context(session, user, "ACCOUNTS_PAYMENT_REGISTER")
    
    # Companies
    comp_stmt = select(Company).where(Company.status == "ACTIVE").order_by(Company.company_name.asc())
    if scope_ctx.scope != "ALL":
        comp_stmt = comp_stmt.where(Company.company_id == scope_ctx.company_id)
    companies = session.execute(comp_stmt).scalars().all()
    company_options = [AccountsFilterOptionItem(id=str(c.company_id), label=c.company_name) for c in companies]
    
    # Clients
    cli_stmt = select(ClientMaster).where(ClientMaster.status == "ACTIVE").order_by(ClientMaster.client_name.asc())
    if scope_ctx.scope != "ALL":
        cli_stmt = cli_stmt.where(ClientMaster.company_id == scope_ctx.company_id)
    clients = session.execute(cli_stmt).scalars().all()
    client_options = [AccountsFilterOptionItem(id=str(c.client_id), label=c.client_name) for c in clients]
    
    # Salespersons
    sp_stmt = select(User).where(User.account_status == "ACTIVE").order_by(User.first_name.asc(), User.last_name.asc())
    if scope_ctx.scope != "ALL":
        sp_stmt = sp_stmt.where(User.company_id == scope_ctx.company_id)
    salespersons = session.execute(sp_stmt).scalars().all()
    salesperson_options = [
        AccountsFilterOptionItem(
            id=str(u.user_id),
            label=f"{u.first_name} {u.last_name} ({u.employee_code})".strip()
        )
        for u in salespersons
    ]
    
    payment_statuses = [
        AccountsFilterOptionItem(id="ALL", label="All Statuses"),
        AccountsFilterOptionItem(id="PENDING", label="Pending"),
        AccountsFilterOptionItem(id="PARTIALLY_PAID", label="Partially Paid"),
        AccountsFilterOptionItem(id="FULLY_PAID", label="Fully Paid"),
        AccountsFilterOptionItem(id="OVERDUE", label="Overdue"),
    ]
    
    payment_modes = [
        AccountsFilterOptionItem(id="BANK_TRANSFER", label="Bank Transfer (NEFT/RTGS/IMPS)"),
        AccountsFilterOptionItem(id="UPI", label="UPI / QR Code"),
        AccountsFilterOptionItem(id="CHEQUE", label="Cheque / DD"),
        AccountsFilterOptionItem(id="CASH", label="Cash"),
        AccountsFilterOptionItem(id="OTHER", label="Other"),
    ]
    
    expense_categories = [
        AccountsFilterOptionItem(id="GOVT_FEES", label="Government / Statutory Fees"),
        AccountsFilterOptionItem(id="VENDOR_COST", label="Vendor / Consultant Outlay"),
        AccountsFilterOptionItem(id="INCIDENTAL_COST", label="Incidental & Operational Cost"),
        AccountsFilterOptionItem(id="EMPLOYEE_REIMBURSEMENT", label="Employee Reimbursement Claim"),
        AccountsFilterOptionItem(id="OTHER_DIRECT_COST", label="Other Direct Cost"),
    ]
    
    receiving_accounts = [
        "HDFC Bank - Current A/c 502000123456",
        "ICICI Bank - Current A/c 001105001234",
        "Axis Bank - Operating A/c 918020012345",
        "UPI - gocompliance@hdfcbank",
        "Cash in Hand Ledger",
    ]
    
    return AccountsFilterOptions(
        companies=company_options,
        clients=client_options,
        salespersons=salesperson_options,
        payment_statuses=payment_statuses,
        payment_modes=payment_modes,
        expense_categories=expense_categories,
        receiving_accounts=receiving_accounts,
    )


# -----------------------------------------------------------------------------
# 2. Payment Register
# -----------------------------------------------------------------------------
def get_payment_register(
    session: Session,
    user: User,
    page: int = 1,
    limit: int = 20,
    search: Optional[str] = None,
    company_id: Optional[str] = None,
    client_id: Optional[str] = None,
    salesperson_id: Optional[str] = None,
    payment_status: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    is_overdue: Optional[bool] = None,
) -> PaymentRegisterResponse:
    """List and aggregate confirmed sales orders in the Payment Register."""
    scope_ctx = permissions.resolve_data_scope_context(session, user, "ACCOUNTS_PAYMENT_REGISTER")
    
    # Query all confirmed sales orders
    query = (
        select(SalesOrder)
        .where(SalesOrder.confirmation_status == "CONFIRMED")
        .options(
            joinedload(SalesOrder.company),
            joinedload(SalesOrder.client),
            joinedload(SalesOrder.service),
            joinedload(SalesOrder.salesperson),
            joinedload(SalesOrder.application),
            selectinload(SalesOrder.payment_transactions),
            selectinload(SalesOrder.accounts_follow_ups).joinedload(AccountsFollowUp.created_by),
        )
    )
    
    query = _apply_accounts_scope(query, user, scope_ctx)
    
    # Apply filters
    if company_id and company_id != "ALL":
        try:
            query = query.where(SalesOrder.company_id == uuid.UUID(company_id))
        except ValueError:
            pass
            
    if client_id and client_id != "ALL":
        try:
            query = query.where(SalesOrder.client_id == uuid.UUID(client_id))
        except ValueError:
            pass
            
    if salesperson_id and salesperson_id != "ALL":
        try:
            query = query.where(SalesOrder.salesperson_user_id == uuid.UUID(salesperson_id))
        except ValueError:
            pass
            
    if date_from:
        query = query.where(SalesOrder.order_date >= date_from)
    if date_to:
        query = query.where(SalesOrder.order_date <= date_to)
        
    if search:
        s = f"%{search.strip()}%"
        query = query.join(SalesOrder.client).join(SalesOrder.service).where(
            or_(
                SalesOrder.order_number.ilike(s),
                ClientMaster.client_name.ilike(s),
                ClientMaster.contact_phone.ilike(s),
                SalesOrder.location.ilike(s),
                SalesOrder.proforma_invoice_no.ilike(s),
                SalesOrder.tax_invoice_no.ilike(s),
            )
        )
        
    all_matched_orders = session.execute(query).unique().scalars().all()
    
    # Reconcile any legacy advance opening balances
    _reconcile_legacy_advances(session, all_matched_orders)
    
    today = date.today()
    processed_items: List[PaymentRegisterItemRead] = []
    
    total_payable_sum = 0.0
    total_verified_sum = 0.0
    total_unverified_sum = 0.0
    total_pending_sum = 0.0
    fully_paid_count = 0
    partially_paid_count = 0
    pending_count = 0
    overdue_count = 0
    
    for order in all_matched_orders:
        t_payable = float(order.order_value or 0)
        v_received = sum(
            float(p.amount) for p in order.payment_transactions if p.verification_status == "VERIFIED"
        )
        u_amount = sum(
            float(p.amount) for p in order.payment_transactions if p.verification_status == "PENDING_VERIFICATION"
        )
        p_amount = max(0.0, t_payable - v_received)
        
        # Determine status
        if v_received >= t_payable:
            st = "FULLY_PAID"
        elif v_received > 0:
            st = "PARTIALLY_PAID"
        else:
            st = "PENDING"
            
        # Due Date & Overdue calculation (default due date: order_date + 15 days if not set)
        order_due_date = order.order_date + timedelta(days=15)
        is_order_overdue = False
        days_od = 0
        if p_amount > 0 and today > order_due_date:
            is_order_overdue = True
            days_od = (today - order_due_date).days
            if st == "PENDING":
                st = "OVERDUE"
                
        # Status Filter Check
        if payment_status and payment_status != "ALL":
            if payment_status == "OVERDUE" and not is_order_overdue:
                continue
            elif payment_status != "OVERDUE" and st != payment_status:
                continue
                
        if is_overdue is True and not is_order_overdue:
            continue
            
        # Accumulate Summary metrics
        total_payable_sum += t_payable
        total_verified_sum += v_received
        total_unverified_sum += u_amount
        total_pending_sum += p_amount
        if st == "FULLY_PAID":
            fully_paid_count += 1
        elif st == "PARTIALLY_PAID":
            partially_paid_count += 1
        elif is_order_overdue:
            overdue_count += 1
        else:
            pending_count += 1
            
        # Latest Remark resolution
        latest_rem_text = None
        latest_rem_date = None
        latest_rem_author = None
        
        if order.accounts_follow_ups:
            sorted_fu = sorted(order.accounts_follow_ups, key=lambda f: f.created_at, reverse=True)
            top_fu = sorted_fu[0]
            latest_rem_text = top_fu.remark_text
            latest_rem_date = top_fu.follow_up_date.strftime("%d %b %Y")
            latest_rem_author = f"{top_fu.created_by.first_name} {top_fu.created_by.last_name}".strip() if top_fu.created_by else None
        elif order.payment_transactions:
            sorted_pt = sorted(order.payment_transactions, key=lambda p: p.created_at, reverse=True)
            for pt in sorted_pt:
                if pt.remark:
                    latest_rem_text = pt.remark
                    latest_rem_date = pt.payment_date.strftime("%d %b %Y")
                    latest_rem_author = f"{pt.submitted_by.first_name} {pt.submitted_by.last_name}".strip() if pt.submitted_by else None
                    break
                    
        op_status = None
        if order.application:
            op_status = order.application.application_status
            
        processed_items.append(
            PaymentRegisterItemRead(
                sales_order_id=order.order_id,
                order_number=order.order_number,
                order_date=order.order_date,
                formatted_order_date=order.order_date.strftime("%d %b %Y"),
                company_id=order.company_id,
                company_name=order.company.company_name if order.company else "GoCompliance",
                client_id=order.client_id,
                client_name=order.client.client_name if order.client else "—",
                client_phone=order.client.contact_phone if order.client else None,
                location=order.location,
                service_id=order.service_id,
                service_name=order.service.service_name if order.service else "—",
                service_code=order.service.service_code if order.service else None,
                salesperson_user_id=order.salesperson_user_id,
                salesperson_name=f"{order.salesperson.first_name} {order.salesperson.last_name}".strip() if order.salesperson else "—",
                salesperson_code=order.salesperson.employee_code if order.salesperson else None,
                total_payable=t_payable,
                formatted_total_payable=format_inr(t_payable),
                verified_received=v_received,
                formatted_verified_received=format_inr(v_received),
                unverified_amount=u_amount,
                formatted_unverified_amount=format_inr(u_amount),
                pending_amount=p_amount,
                formatted_pending_amount=format_inr(p_amount),
                payment_status=st,
                due_date=order_due_date,
                formatted_due_date=order_due_date.strftime("%d %b %Y"),
                is_overdue=is_order_overdue,
                days_overdue=days_od,
                proforma_invoice_no=order.proforma_invoice_no,
                tax_invoice_no=order.tax_invoice_no,
                govt_fees=float(order.govt_fees or 0),
                incidental_cost=float(order.incidental_cost or 0),
                profit_amount=float(order.profit_amount or 0),
                operation_status=op_status,
                latest_remark=latest_rem_text,
                latest_remark_date=latest_rem_date,
                latest_remark_author=latest_rem_author,
                payment_count=len(order.payment_transactions),
                unverified_payment_count=sum(1 for p in order.payment_transactions if p.verification_status == "PENDING_VERIFICATION"),
            )
        )
        
    # Sort by order date desc
    processed_items.sort(key=lambda x: x.order_date, reverse=True)
    
    total_count = len(processed_items)
    safe_page = max(1, page)
    safe_limit = max(1, min(100, limit))
    offset_val = (safe_page - 1) * safe_limit
    paged_items = processed_items[offset_val : offset_val + safe_limit]
    total_pages = max(1, (total_count + safe_limit - 1) // safe_limit)
    
    summary = PaymentRegisterSummary(
        total_orders=total_count,
        total_payable=total_payable_sum,
        total_verified_received=total_verified_sum,
        total_unverified_amount=total_unverified_sum,
        total_pending=total_pending_sum,
        fully_paid_count=fully_paid_count,
        partially_paid_count=partially_paid_count,
        pending_count=pending_count,
        overdue_count=overdue_count,
        formatted_total_payable=format_inr(total_payable_sum),
        formatted_total_verified_received=format_inr(total_verified_sum),
        formatted_total_unverified_amount=format_inr(total_unverified_sum),
        formatted_total_pending=format_inr(total_pending_sum),
    )
    
    return PaymentRegisterResponse(
        items=paged_items,
        summary=summary,
        total_count=total_count,
        page=safe_page,
        limit=safe_limit,
        total_pages=total_pages,
    )


# -----------------------------------------------------------------------------
# 3. Payment Transactions: Record, Verify, Reverse, History
# -----------------------------------------------------------------------------
def record_payment_transaction(
    session: Session,
    user: User,
    data: PaymentTransactionCreate,
    proof_file_path: Optional[str] = None,
    proof_file_name: Optional[str] = None,
    ip_address: Optional[str] = None,
) -> PaymentTransactionRead:
    """Record a payment collection against a confirmed Sales Order."""
    scope_ctx = permissions.resolve_data_scope_context(session, user, "ACCOUNTS_PAYMENT_REGISTER")
    
    order = session.get(SalesOrder, data.sales_order_id)
    if not order:
        raise ValueError(f"Sales order {data.sales_order_id} not found.")
        
    if order.confirmation_status != "CONFIRMED":
        raise ValueError("Payments can only be recorded on confirmed sales orders.")
        
    # Reconcile any legacy advance before processing new payment
    _reconcile_legacy_advances(session, [order])
        
    # Check data scope permissions
    if not scope_ctx.is_user_permitted(target_user_id=order.salesperson_user_id, target_company_id=order.company_id):
        raise permissions.PermissionDeniedError("You are not authorized to record payments for this company/order.")
        
    if data.amount <= 0:
        raise ValueError("Payment amount must be strictly positive.")
        
    # Calculate current verified and pending
    verified_sum = sum(
        float(p.amount) for p in order.payment_transactions if p.verification_status == "VERIFIED"
    )
    total_val = float(order.order_value or 0)
    
    if verified_sum + data.amount > total_val + 0.01:
        max_allowed = max(0.0, total_val - verified_sum)
        raise ValueError(
            f"Payment amount of {format_inr(data.amount)} exceeds the remaining balance of {format_inr(max_allowed)}."
        )
        
    # Idempotency / duplicate check (prevents double submits within 60 seconds with same ref/amount)
    cutoff = datetime.now(timezone.utc) - timedelta(seconds=60)
    existing_dup = session.execute(
        select(PaymentTransaction).where(
            PaymentTransaction.sales_order_id == data.sales_order_id,
            PaymentTransaction.amount == data.amount,
            PaymentTransaction.submitted_by_user_id == user.user_id,
            PaymentTransaction.created_at >= cutoff,
        )
    ).scalar_one_or_none()
    
    if existing_dup:
        return _to_payment_read(existing_dup)
        
    # Determine initial verification status:
    # Super Admin or Accounts users with 'approve' / 'edit' on Accounts get auto-verified if requested
    can_auto_verify = (
        permissions.is_super_admin_user(session, user)
        or permissions.has_permission(session, user, "ACCOUNTS_PAYMENT_REGISTER", "approve")
        or permissions.has_permission(session, user, "ACCOUNTS_PAYMENT_REGISTER", "edit")
        or permissions.has_permission(session, user, "ACCOUNTS", "approve")
        or permissions.has_permission(session, user, "ACCOUNTS", "edit")
    )
    
    v_status = "VERIFIED" if (data.auto_verify and can_auto_verify) else "PENDING_VERIFICATION"
    v_by = user.user_id if v_status == "VERIFIED" else None
    v_at = datetime.now(timezone.utc) if v_status == "VERIFIED" else None
    
    payment = PaymentTransaction(
        payment_id=uuid.uuid4(),
        company_id=order.company_id,
        sales_order_id=order.order_id,
        payment_number=_generate_payment_number(session, order.company_id),
        amount=data.amount,
        payment_date=data.payment_date,
        payment_mode=data.payment_mode,
        transaction_reference=data.transaction_reference.strip() if data.transaction_reference else None,
        receiving_account=data.receiving_account.strip() if data.receiving_account else None,
        proof_attachment_path=proof_file_path,
        proof_attachment_name=proof_file_name,
        remark=data.remark.strip() if data.remark else None,
        submitted_by_user_id=user.user_id,
        submitted_at=datetime.now(timezone.utc),
        verification_status=v_status,
        verified_by_user_id=v_by,
        verified_at=v_at,
        is_opening_balance=False,
    )
    session.add(payment)
    order.payment_transactions.append(payment)
    session.flush()
    
    # Recalculate order financials if verified
    if v_status == "VERIFIED":
        _recalculate_order_financials(session, order)
        
    _log_accounts_audit(
        session=session,
        company_id=order.company_id,
        entity_type="PAYMENT",
        entity_id=payment.payment_id,
        action="CREATE",
        actor_user_id=user.user_id,
        new_values={"payment_number": payment.payment_number, "amount": float(payment.amount), "status": v_status},
        ip_address=ip_address,
    )
    
    session.commit()
    return _to_payment_read(payment)


def verify_payment_transaction(
    session: Session,
    user: User,
    payment_id: uuid.UUID,
    action: Optional[str] = None,
    data: Optional[PaymentTransactionVerify] = None,
    rejection_reason: Optional[str] = None,
    ip_address: Optional[str] = None,
) -> PaymentTransactionRead:
    """Verify or reject a pending payment submission."""
    if data is not None:
        action = data.action
        rejection_reason = data.rejection_reason
    action = (action or "VERIFY").strip().upper()

    # Check permissions
    is_sa = permissions.is_super_admin_user(session, user)
    has_perm = (
        is_sa
        or permissions.has_permission(session, user, "ACCOUNTS_PAYMENT_REGISTER", "approve")
        or permissions.has_permission(session, user, "ACCOUNTS_PAYMENT_REGISTER", "edit")
        or permissions.has_permission(session, user, "ACCOUNTS", "approve")
        or permissions.has_permission(session, user, "ACCOUNTS", "edit")
    )
    if not has_perm:
        raise permissions.PermissionDeniedError("You do not have permission to verify payments.")
        
    payment = session.get(PaymentTransaction, payment_id)
    if not payment:
        raise ValueError(f"Payment transaction {payment_id} not found.")
        
    if payment.verification_status != "PENDING_VERIFICATION":
        raise ValueError(f"Payment is already in status '{payment.verification_status}' and cannot be verified.")
        
    old_st = payment.verification_status
    if action == "VERIFY":
        payment.verification_status = "VERIFIED"
        payment.verified_by_user_id = user.user_id
        payment.verified_at = datetime.now(timezone.utc)
        payment.reversal_reason = None
    elif action == "REJECT":
        payment.verification_status = "REJECTED"
        payment.reversal_reason = rejection_reason.strip() if rejection_reason else "Payment rejected by Accounts"
    else:
        raise ValueError(f"Invalid verification action '{action}'. Use VERIFY or REJECT.")
        
    session.add(payment)
    session.flush()
    
    # Recalculate order financials
    order = payment.sales_order
    if order:
        _recalculate_order_financials(session, order)
        
    _log_accounts_audit(
        session=session,
        company_id=payment.company_id,
        entity_type="PAYMENT",
        entity_id=payment.payment_id,
        action="VERIFY" if action == "VERIFY" else "REJECT",
        actor_user_id=user.user_id,
        old_values={"status": old_st},
        new_values={"status": payment.verification_status, "reason": payment.reversal_reason},
        ip_address=ip_address,
    )
    
    session.commit()
    return _to_payment_read(payment)


def reverse_payment_transaction(
    session: Session,
    user: User,
    payment_id: uuid.UUID,
    reversal_reason: Optional[str] = None,
    data: Optional[PaymentTransactionReverse] = None,
    ip_address: Optional[str] = None,
) -> PaymentTransactionRead:
    """Authorized reversal of a verified payment transaction."""
    if data is not None:
        reversal_reason = data.reversal_reason
    reversal_reason = (reversal_reason or "").strip()

    is_sa = permissions.is_super_admin_user(session, user)
    has_perm = (
        is_sa
        or permissions.has_permission(session, user, "ACCOUNTS_PAYMENT_REGISTER", "delete")
        or permissions.has_permission(session, user, "ACCOUNTS_PAYMENT_REGISTER", "approve")
        or permissions.has_permission(session, user, "ACCOUNTS", "delete")
    )
    if not has_perm:
        raise permissions.PermissionDeniedError("You do not have authorization to reverse verified payments.")
        
    if not reversal_reason or len(reversal_reason) < 3:
        raise ValueError("A clear, valid reversal reason is mandatory to reverse a verified payment.")
        
    payment = session.get(PaymentTransaction, payment_id)
    if not payment:
        raise ValueError(f"Payment transaction {payment_id} not found.")
        
    if payment.verification_status != "VERIFIED":
        raise ValueError(f"Only verified payments can be reversed. Current status: '{payment.verification_status}'.")
        
    old_vals = {
        "status": payment.verification_status,
        "amount": float(payment.amount),
        "payment_number": payment.payment_number,
    }
    
    payment.verification_status = "REVERSED"
    payment.reversed_by_user_id = user.user_id
    payment.reversed_at = datetime.now(timezone.utc)
    payment.reversal_reason = reversal_reason
    session.add(payment)
    session.flush()
    
    # Recalculate order financials
    order = payment.sales_order
    if order:
        _recalculate_order_financials(session, order)
        
    _log_accounts_audit(
        session=session,
        company_id=payment.company_id,
        entity_type="PAYMENT",
        entity_id=payment.payment_id,
        action="REVERSE",
        actor_user_id=user.user_id,
        old_values=old_vals,
        new_values={"status": payment.verification_status, "reversal_reason": payment.reversal_reason},
        reason=reversal_reason,
        ip_address=ip_address,
    )
    
    session.commit()
    return _to_payment_read(payment)


def get_order_payment_history(
    session: Session,
    user: User,
    sales_order_id: uuid.UUID,
) -> PaymentTransactionListResponse:
    """Retrieve all payment transactions and audit states for a sales order."""
    order = session.get(SalesOrder, sales_order_id)
    if not order:
        raise ValueError(f"Sales order {sales_order_id} not found.")
        
    # Reconcile any legacy opening advance
    _reconcile_legacy_advances(session, [order])
    
    stmt = (
        select(PaymentTransaction)
        .where(PaymentTransaction.sales_order_id == sales_order_id)
        .options(
            joinedload(PaymentTransaction.submitted_by),
            joinedload(PaymentTransaction.verified_by),
            joinedload(PaymentTransaction.reversed_by),
        )
        .order_by(PaymentTransaction.payment_date.desc(), PaymentTransaction.created_at.desc())
    )
    payments = session.execute(stmt).scalars().all()
    
    items = [_to_payment_read(p) for p in payments]
    verified_tot = sum(p.amount for p in items if p.verification_status == "VERIFIED")
    unverified_tot = sum(p.amount for p in items if p.verification_status == "PENDING_VERIFICATION")
    
    return PaymentTransactionListResponse(
        items=items,
        total_count=len(items),
        total_verified_amount=verified_tot,
        total_unverified_amount=unverified_tot,
    )


def _to_payment_read(p: PaymentTransaction) -> PaymentTransactionRead:
    """Convert ORM PaymentTransaction to Read DTO."""
    amt = float(p.amount)
    sub_name = f"{p.submitted_by.first_name} {p.submitted_by.last_name}".strip() if p.submitted_by else None
    ver_name = f"{p.verified_by.first_name} {p.verified_by.last_name}".strip() if p.verified_by else None
    rev_name = f"{p.reversed_by.first_name} {p.reversed_by.last_name}".strip() if p.reversed_by else None
    
    return PaymentTransactionRead(
        payment_id=p.payment_id,
        company_id=p.company_id,
        company_name=p.company.company_name if p.company else None,
        sales_order_id=p.sales_order_id,
        sales_order_number=p.sales_order.order_number if p.sales_order else None,
        client_id=p.sales_order.client_id if p.sales_order else None,
        client_name=p.sales_order.client.client_name if p.sales_order and p.sales_order.client else None,
        payment_number=p.payment_number,
        amount=amt,
        formatted_amount=format_inr(amt),
        payment_date=p.payment_date,
        formatted_payment_date=p.payment_date.strftime("%d %b %Y"),
        payment_mode=p.payment_mode,
        transaction_reference=p.transaction_reference,
        receiving_account=p.receiving_account,
        proof_attachment_path=p.proof_attachment_path,
        proof_attachment_name=p.proof_attachment_name,
        remark=p.remark,
        submitted_by_user_id=p.submitted_by_user_id,
        submitted_by_name=sub_name,
        submitted_at=p.submitted_at,
        formatted_submitted_at=p.submitted_at.strftime("%d %b %Y, %I:%M %p") if p.submitted_at else None,
        verification_status=p.verification_status,
        verified_by_user_id=p.verified_by_user_id,
        verified_by_name=ver_name,
        verified_at=p.verified_at,
        formatted_verified_at=p.verified_at.strftime("%d %b %Y, %I:%M %p") if p.verified_at else None,
        reversal_reason=p.reversal_reason,
        reversed_by_user_id=p.reversed_by_user_id,
        reversed_by_name=rev_name,
        reversed_at=p.reversed_at,
        is_opening_balance=p.is_opening_balance,
        created_at=p.created_at,
    )


# -----------------------------------------------------------------------------
# 4. Outstanding Receivables & Ageing Follow-ups
# -----------------------------------------------------------------------------
def get_outstanding_receivables(
    session: Session,
    user: User,
    page: int = 1,
    limit: int = 20,
    search: Optional[str] = None,
    company_id: Optional[str] = None,
    client_id: Optional[str] = None,
    salesperson_id: Optional[str] = None,
    ageing_bucket: Optional[str] = None,
    completed_operations_only: Optional[bool] = None,
    completed_only: Optional[bool] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    **kwargs,
) -> OutstandingResponse:
    """Retrieve outstanding debtors with ageing breakdown and operations fulfillment status."""
    if completed_only is not None and completed_operations_only is None:
        completed_operations_only = completed_only
    scope_ctx = permissions.resolve_data_scope_context(session, user, "ACCOUNTS_OUTSTANDING")
    
    query = (
        select(SalesOrder)
        .where(SalesOrder.confirmation_status == "CONFIRMED")
        .options(
            joinedload(SalesOrder.company),
            joinedload(SalesOrder.client),
            joinedload(SalesOrder.service),
            joinedload(SalesOrder.salesperson),
            joinedload(SalesOrder.application),
            selectinload(SalesOrder.payment_transactions),
            selectinload(SalesOrder.accounts_follow_ups).joinedload(AccountsFollowUp.created_by),
        )
    )
    query = _apply_accounts_scope(query, user, scope_ctx)
    
    if company_id and company_id != "ALL":
        try:
            query = query.where(SalesOrder.company_id == uuid.UUID(company_id))
        except ValueError:
            pass
            
    if salesperson_id and salesperson_id != "ALL":
        try:
            query = query.where(SalesOrder.salesperson_user_id == uuid.UUID(salesperson_id))
        except ValueError:
            pass
            
    if search:
        s = f"%{search.strip()}%"
        query = query.join(SalesOrder.client).join(SalesOrder.service).where(
            or_(
                SalesOrder.order_number.ilike(s),
                ClientMaster.client_name.ilike(s),
                SalesOrder.location.ilike(s),
            )
        )
        
    orders = session.execute(query).unique().scalars().all()
    _reconcile_legacy_advances(session, orders)
    
    today = date.today()
    outstanding_items: List[OutstandingItemRead] = []
    
    total_out_sum = 0.0
    total_od_sum = 0.0
    
    current_amt = 0.0
    current_cnt = 0
    days_1_30_amt = 0.0
    days_1_30_cnt = 0
    days_31_60_amt = 0.0
    days_31_60_cnt = 0
    days_61_90_amt = 0.0
    days_61_90_cnt = 0
    over_90_amt = 0.0
    over_90_cnt = 0
    no_due_amt = 0.0
    no_due_cnt = 0
    
    completed_ops_amt = 0.0
    completed_ops_cnt = 0
    
    for order in orders:
        t_payable = float(order.order_value or 0)
        v_received = sum(
            float(p.amount) for p in order.payment_transactions if p.verification_status == "VERIFIED"
        )
        pending = max(0.0, t_payable - v_received)
        
        # Only include orders that have a pending balance
        if pending <= 0:
            continue
            
        due_dt = order.order_date + timedelta(days=15)
        days_od = (today - due_dt).days if today > due_dt else 0
        
        # Determine ageing bucket
        if today <= due_dt:
            bucket = "CURRENT"
            current_amt += pending
            current_cnt += 1
        elif 1 <= days_od <= 30:
            bucket = "1_30_DAYS"
            days_1_30_amt += pending
            days_1_30_cnt += 1
        elif 31 <= days_od <= 60:
            bucket = "31_60_DAYS"
            days_31_60_amt += pending
            days_31_60_cnt += 1
        elif 61 <= days_od <= 90:
            bucket = "61_90_DAYS"
            days_61_90_amt += pending
            days_61_90_cnt += 1
        else:
            bucket = "OVER_90_DAYS"
            over_90_amt += pending
            over_90_cnt += 1
            
        total_out_sum += pending
        if days_od > 0:
            total_od_sum += pending
            
        op_st = order.application.application_status if order.application else None
        is_completed = op_st in ("COMPLETED", "APPROVED")
        if is_completed:
            completed_ops_amt += pending
            completed_ops_cnt += 1
            
        # Ageing filter check
        if ageing_bucket and ageing_bucket != "ALL" and bucket != ageing_bucket:
            continue
            
        if completed_operations_only is True and not is_completed:
            continue
            
        # Latest follow-up resolution
        latest_fu_read = None
        if order.accounts_follow_ups:
            sorted_fu = sorted(order.accounts_follow_ups, key=lambda f: f.created_at, reverse=True)
            latest_fu_read = _to_follow_up_read(sorted_fu[0])
            
        outstanding_items.append(
            OutstandingItemRead(
                sales_order_id=order.order_id,
                order_number=order.order_number,
                order_date=order.order_date,
                formatted_order_date=order.order_date.strftime("%d %b %Y"),
                company_id=order.company_id,
                company_name=order.company.company_name if order.company else "GoCompliance",
                client_id=order.client_id,
                client_name=order.client.client_name if order.client else "—",
                client_phone=order.client.contact_phone if order.client else None,
                client_email=order.client.contact_email if order.client else None,
                location=order.location,
                service_id=order.service_id,
                service_name=order.service.service_name if order.service else "—",
                salesperson_name=f"{order.salesperson.first_name} {order.salesperson.last_name}".strip() if order.salesperson else "—",
                salesperson_code=order.salesperson.employee_code if order.salesperson else None,
                total_payable=t_payable,
                formatted_total_payable=format_inr(t_payable),
                verified_received=v_received,
                formatted_verified_received=format_inr(v_received),
                pending_amount=pending,
                formatted_pending_amount=format_inr(pending),
                due_date=due_dt,
                formatted_due_date=due_dt.strftime("%d %b %Y"),
                days_overdue=days_od,
                ageing_bucket=bucket,
                operation_status=op_st,
                is_work_completed=is_completed,
                latest_follow_up=latest_fu_read,
                follow_up_count=len(order.accounts_follow_ups),
            )
        )
        
    # Sort highest overdue days first, then highest pending amount
    outstanding_items.sort(key=lambda x: (x.days_overdue, x.pending_amount), reverse=True)
    
    total_count = len(outstanding_items)
    safe_page = max(1, page)
    safe_limit = max(1, min(100, limit))
    offset_val = (safe_page - 1) * safe_limit
    paged_items = outstanding_items[offset_val : offset_val + safe_limit]
    total_pages = max(1, (total_count + safe_limit - 1) // safe_limit)
    
    summary = OutstandingAgeingSummary(
        total_outstanding_amount=total_out_sum,
        formatted_total_outstanding=format_inr(total_out_sum),
        total_overdue_amount=total_od_sum,
        formatted_total_overdue=format_inr(total_od_sum),
        total_debtors_count=total_count,
        current_amount=current_amt,
        current_count=current_cnt,
        days_1_30_amount=days_1_30_amt,
        days_1_30_count=days_1_30_cnt,
        days_31_60_amount=days_31_60_amt,
        days_31_60_count=days_31_60_cnt,
        days_61_90_amount=days_61_90_amt,
        days_61_90_count=days_61_90_cnt,
        over_90_days_amount=over_90_amt,
        over_90_days_count=over_90_cnt,
        no_due_date_amount=no_due_amt,
        no_due_date_count=no_due_cnt,
        completed_work_pending_amount=completed_ops_amt,
        completed_work_pending_count=completed_ops_cnt,
    )
    
    return OutstandingResponse(
        items=paged_items,
        summary=summary,
        total_count=total_count,
        page=safe_page,
        limit=safe_limit,
        total_pages=total_pages,
    )


def record_accounts_follow_up(
    session: Session,
    user: User,
    sales_order_id: uuid.UUID,
    data: AccountsFollowUpCreate,
) -> AccountsFollowUpRead:
    """Record a debt follow-up remark on an outstanding sales order."""
    order = session.get(SalesOrder, sales_order_id)
    if not order:
        raise ValueError(f"Sales order {sales_order_id} not found.")
        
    fu = AccountsFollowUp(
        follow_up_id=uuid.uuid4(),
        company_id=order.company_id,
        sales_order_id=order.order_id,
        follow_up_date=data.follow_up_date,
        next_follow_up_date=data.next_follow_up_date,
        contact_channel=data.contact_channel,
        contact_person=data.contact_person.strip() if data.contact_person else None,
        remark_text=data.remark_text.strip(),
        created_by_user_id=user.user_id,
    )
    session.add(fu)
    session.flush()
    
    _log_accounts_audit(
        session=session,
        company_id=order.company_id,
        entity_type="FOLLOW_UP",
        entity_id=fu.follow_up_id,
        action="CREATE",
        actor_user_id=user.user_id,
        new_values={"remark": fu.remark_text, "channel": fu.contact_channel},
    )
    
    session.commit()
    return _to_follow_up_read(fu)


def get_order_follow_up_history(
    session: Session,
    sales_order_id: uuid.UUID,
) -> List[AccountsFollowUpRead]:
    """Retrieve full follow-up history for a sales order."""
    stmt = (
        select(AccountsFollowUp)
        .where(AccountsFollowUp.sales_order_id == sales_order_id)
        .options(joinedload(AccountsFollowUp.created_by))
        .order_by(AccountsFollowUp.follow_up_date.desc(), AccountsFollowUp.created_at.desc())
    )
    records = session.execute(stmt).scalars().all()
    return [_to_follow_up_read(f) for f in records]


def _to_follow_up_read(f: AccountsFollowUp) -> AccountsFollowUpRead:
    """Convert ORM AccountsFollowUp to Read DTO."""
    created_name = f"{f.created_by.first_name} {f.created_by.last_name}".strip() if f.created_by else None
    return AccountsFollowUpRead(
        follow_up_id=f.follow_up_id,
        sales_order_id=f.sales_order_id,
        company_id=f.company_id,
        follow_up_date=f.follow_up_date,
        formatted_follow_up_date=f.follow_up_date.strftime("%d %b %Y"),
        next_follow_up_date=f.next_follow_up_date,
        formatted_next_follow_up_date=f.next_follow_up_date.strftime("%d %b %Y") if f.next_follow_up_date else None,
        contact_channel=f.contact_channel,
        contact_person=f.contact_person,
        remark_text=f.remark_text,
        created_by_user_id=f.created_by_user_id,
        created_by_name=created_name,
        created_at=f.created_at,
        formatted_created_at=f.created_at.strftime("%d %b %Y, %I:%M %p") if f.created_at else None,
    )


# -----------------------------------------------------------------------------
# 5. Invoices & Receipts Management
# -----------------------------------------------------------------------------
def get_invoices(
    session: Session,
    user: User,
    page: int = 1,
    limit: int = 20,
    search: Optional[str] = None,
    company_id: Optional[str] = None,
    invoice_type: Optional[str] = None,
    missing_only: bool = False,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    **kwargs,
) -> AccountsInvoiceListResponse:
    """List Proforma and Tax invoices with document attachments."""
    scope_ctx = permissions.resolve_data_scope_context(session, user, "ACCOUNTS_INVOICES")
    
    stmt = (
        select(AccountsInvoice)
        .options(
            joinedload(AccountsInvoice.company),
            joinedload(AccountsInvoice.sales_order).joinedload(SalesOrder.client),
            joinedload(AccountsInvoice.sales_order).joinedload(SalesOrder.service),
            joinedload(AccountsInvoice.created_by),
        )
        .order_by(AccountsInvoice.invoice_date.desc(), AccountsInvoice.created_at.desc())
    )
    
    if scope_ctx.scope != "ALL":
        stmt = stmt.where(AccountsInvoice.company_id == scope_ctx.company_id)
        
    if company_id and company_id != "ALL":
        try:
            stmt = stmt.where(AccountsInvoice.company_id == uuid.UUID(company_id))
        except ValueError:
            pass
            
    if invoice_type and invoice_type != "ALL":
        stmt = stmt.where(AccountsInvoice.invoice_type == invoice_type)
        
    if search:
        s = f"%{search.strip()}%"
        stmt = stmt.join(AccountsInvoice.sales_order).join(SalesOrder.client).where(
            or_(
                AccountsInvoice.invoice_number.ilike(s),
                SalesOrder.order_number.ilike(s),
                ClientMaster.client_name.ilike(s),
            )
        )
        
    invoices = session.execute(stmt).scalars().all()
    items = [_to_invoice_read(inv) for inv in invoices]
    
    proforma_cnt = sum(1 for i in items if i.invoice_type == "PROFORMA")
    tax_cnt = sum(1 for i in items if i.invoice_type == "TAX_INVOICE")
    tot_amt = sum(i.amount for i in items)
    
    # Count confirmed orders missing invoices
    orders_no_inv_stmt = (
        select(func.count(SalesOrder.order_id))
        .where(
            SalesOrder.confirmation_status == "CONFIRMED",
            SalesOrder.tax_invoice_no.is_(None),
            SalesOrder.proforma_invoice_no.is_(None),
        )
    )
    if scope_ctx.scope != "ALL":
        orders_no_inv_stmt = orders_no_inv_stmt.where(SalesOrder.company_id == scope_ctx.company_id)
    missing_cnt = session.execute(orders_no_inv_stmt).scalar() or 0
    
    return AccountsInvoiceListResponse(
        items=items,
        total_count=len(items),
        total_proforma_count=proforma_cnt,
        total_tax_invoice_count=tax_cnt,
        total_invoiced_amount=tot_amt,
        orders_without_invoice_count=missing_cnt,
    )


def create_invoice(
    session: Session,
    user: User,
    data: AccountsInvoiceCreate,
    file_path: Optional[str] = None,
    file_name: Optional[str] = None,
    ip_address: Optional[str] = None,
) -> AccountsInvoiceRead:
    """Create a Proforma or Tax Invoice entry and link to Sales Order."""
    order = session.get(SalesOrder, data.sales_order_id)
    if not order:
        raise ValueError(f"Sales order {data.sales_order_id} not found.")
        
    # Check invoice uniqueness per company and type
    existing = session.execute(
        select(AccountsInvoice).where(
            AccountsInvoice.company_id == order.company_id,
            AccountsInvoice.invoice_type == data.invoice_type,
            AccountsInvoice.invoice_number == data.invoice_number.strip(),
        )
    ).scalar_one_or_none()
    
    if existing:
        raise ValueError(
            f"An invoice with number '{data.invoice_number}' already exists for this company and type."
        )
        
    inv = AccountsInvoice(
        invoice_id=uuid.uuid4(),
        company_id=order.company_id,
        sales_order_id=order.order_id,
        invoice_type=data.invoice_type.upper(),
        invoice_number=data.invoice_number.strip(),
        invoice_date=data.invoice_date,
        due_date=data.due_date,
        amount=data.amount,
        taxable_amount=data.taxable_amount,
        cgst_amount=data.cgst_amount,
        sgst_amount=data.sgst_amount,
        igst_amount=data.igst_amount,
        status="ISSUED",
        file_path=file_path,
        file_name=file_name,
        notes=data.notes.strip() if data.notes else None,
        created_by_user_id=user.user_id,
    )
    session.add(inv)
    
    # Sync invoice number to sales order
    if inv.invoice_type == "PROFORMA":
        order.proforma_invoice_no = inv.invoice_number
    elif inv.invoice_type == "TAX_INVOICE":
        order.tax_invoice_no = inv.invoice_number
    session.add(order)
    session.flush()
    
    _log_accounts_audit(
        session=session,
        company_id=order.company_id,
        entity_type="INVOICE",
        entity_id=inv.invoice_id,
        action="CREATE",
        actor_user_id=user.user_id,
        new_values={"number": inv.invoice_number, "type": inv.invoice_type, "amount": float(inv.amount)},
        ip_address=ip_address,
    )
    
    session.commit()
    return _to_invoice_read(inv)


def _to_invoice_read(inv: AccountsInvoice) -> AccountsInvoiceRead:
    """Convert ORM AccountsInvoice to Read DTO."""
    amt = float(inv.amount)
    c_name = inv.created_by.first_name + " " + inv.created_by.last_name if inv.created_by else None
    return AccountsInvoiceRead(
        invoice_id=inv.invoice_id,
        company_id=inv.company_id,
        company_name=inv.company.company_name if inv.company else None,
        sales_order_id=inv.sales_order_id,
        sales_order_number=inv.sales_order.order_number if inv.sales_order else None,
        client_id=inv.sales_order.client_id if inv.sales_order else None,
        client_name=inv.sales_order.client.client_name if inv.sales_order and inv.sales_order.client else None,
        service_name=inv.sales_order.service.service_name if inv.sales_order and inv.sales_order.service else None,
        invoice_type=inv.invoice_type,
        invoice_number=inv.invoice_number,
        invoice_date=inv.invoice_date,
        formatted_invoice_date=inv.invoice_date.strftime("%d %b %Y"),
        due_date=inv.due_date,
        formatted_due_date=inv.due_date.strftime("%d %b %Y") if inv.due_date else None,
        amount=amt,
        formatted_amount=format_inr(amt),
        taxable_amount=float(inv.taxable_amount) if inv.taxable_amount else None,
        cgst_amount=float(inv.cgst_amount) if inv.cgst_amount else None,
        sgst_amount=float(inv.sgst_amount) if inv.sgst_amount else None,
        igst_amount=float(inv.igst_amount) if inv.igst_amount else None,
        status=inv.status,
        file_path=inv.file_path,
        file_name=inv.file_name,
        notes=inv.notes,
        created_by_user_id=inv.created_by_user_id,
        created_by_name=c_name.strip() if c_name else None,
        created_at=inv.created_at,
    )


# -----------------------------------------------------------------------------
# 6. Expenses & Reimbursements Management
# -----------------------------------------------------------------------------
def get_expenses(
    session: Session,
    user: User,
    page: int = 1,
    limit: int = 20,
    search: Optional[str] = None,
    company_id: Optional[str] = None,
    category: Optional[str] = None,
    approval_status: Optional[str] = None,
    settlement_status: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    **kwargs,
) -> AccountsExpenseListResponse:
    """List direct costs, statutory fee payments, and employee reimbursement claims."""
    scope_ctx = permissions.resolve_data_scope_context(session, user, "ACCOUNTS_EXPENSES")
    
    stmt = (
        select(AccountsExpense)
        .options(
            joinedload(AccountsExpense.company),
            joinedload(AccountsExpense.sales_order).joinedload(SalesOrder.client),
            joinedload(AccountsExpense.paid_by_user),
            joinedload(AccountsExpense.approved_by),
            joinedload(AccountsExpense.settled_by),
            joinedload(AccountsExpense.created_by),
        )
        .order_by(AccountsExpense.expense_date.desc(), AccountsExpense.created_at.desc())
    )
    
    if scope_ctx.scope != "ALL":
        stmt = stmt.where(AccountsExpense.company_id == scope_ctx.company_id)
        
    if category and category != "ALL":
        stmt = stmt.where(AccountsExpense.category == category)
        
    if approval_status and approval_status != "ALL":
        stmt = stmt.where(AccountsExpense.approval_status == approval_status)
        
    if settlement_status and settlement_status != "ALL":
        stmt = stmt.where(AccountsExpense.settlement_status == settlement_status)
        
    if search:
        s = f"%{search.strip()}%"
        stmt = stmt.where(
            or_(
                AccountsExpense.expense_number.ilike(s),
                AccountsExpense.payee_name.ilike(s),
                AccountsExpense.transaction_reference.ilike(s),
                AccountsExpense.remark.ilike(s),
            )
        )
        
    expenses = session.execute(stmt).scalars().all()
    items = [_to_expense_read(exp) for exp in expenses]
    
    tot_approved = sum(e.amount for e in items if e.approval_status == "APPROVED")
    tot_pending_app = sum(e.amount for e in items if e.approval_status == "PENDING_APPROVAL")
    tot_pending_reimb = sum(
        e.amount for e in items if e.paid_by_type == "EMPLOYEE" and e.settlement_status == "UNSETTLED"
    )
    tot_settled_reimb = sum(
        e.amount for e in items if e.paid_by_type == "EMPLOYEE" and e.settlement_status == "SETTLED"
    )
    
    return AccountsExpenseListResponse(
        items=items,
        total_count=len(items),
        total_approved_expenses=tot_approved,
        total_pending_approval=tot_pending_app,
        total_pending_reimbursements=tot_pending_reimb,
        total_settled_reimbursements=tot_settled_reimb,
    )


def record_expense(
    session: Session,
    user: User,
    data: AccountsExpenseCreate,
    bill_file_path: Optional[str] = None,
    bill_file_name: Optional[str] = None,
    ip_address: Optional[str] = None,
) -> AccountsExpenseRead:
    """Record a direct order expense or employee reimbursement claim."""
    if data.amount <= 0:
        raise ValueError("Expense amount must be strictly positive.")
        
    company_id = user.company_id
    if data.sales_order_id:
        order = session.get(SalesOrder, data.sales_order_id)
        if order:
            company_id = order.company_id
            
    is_sa = permissions.is_super_admin_user(session, user)
    can_auto_approve = (
        is_sa
        or permissions.has_permission(session, user, "ACCOUNTS_EXPENSES", "approve")
        or permissions.has_permission(session, user, "ACCOUNTS", "approve")
    )
    
    app_status = "APPROVED" if (data.paid_by_type == "COMPANY" and can_auto_approve) else "PENDING_APPROVAL"
    app_by = user.user_id if app_status == "APPROVED" else None
    app_at = datetime.now(timezone.utc) if app_status == "APPROVED" else None
    
    settle_status = "UNSETTLED" if data.paid_by_type == "EMPLOYEE" else "NOT_APPLICABLE"
    paid_user_id = data.paid_by_user_id if data.paid_by_type == "EMPLOYEE" else None
    if data.paid_by_type == "EMPLOYEE" and not paid_user_id:
        paid_user_id = user.user_id
        
    exp = AccountsExpense(
        expense_id=uuid.uuid4(),
        company_id=company_id,
        sales_order_id=data.sales_order_id,
        expense_number=_generate_expense_number(session, company_id),
        category=data.category,
        amount=data.amount,
        expense_date=data.expense_date,
        payee_name=data.payee_name.strip(),
        paid_by_type=data.paid_by_type,
        paid_by_user_id=paid_user_id,
        payment_mode=data.payment_mode,
        transaction_reference=data.transaction_reference.strip() if data.transaction_reference else None,
        bill_attachment_path=bill_file_path,
        bill_attachment_name=bill_file_name,
        remark=data.remark.strip() if data.remark else None,
        approval_status=app_status,
        approved_by_user_id=app_by,
        approved_at=app_at,
        settlement_status=settle_status,
        created_by_user_id=user.user_id,
    )
    session.add(exp)
    session.flush()
    
    _log_accounts_audit(
        session=session,
        company_id=company_id,
        entity_type="EXPENSE",
        entity_id=exp.expense_id,
        action="CREATE",
        actor_user_id=user.user_id,
        new_values={"number": exp.expense_number, "amount": float(exp.amount), "category": exp.category},
        ip_address=ip_address,
    )
    
    session.commit()
    return _to_expense_read(exp)


def approve_expense(
    session: Session,
    user: User,
    expense_id: uuid.UUID,
    action: Optional[str] = None,
    data: Optional[AccountsExpenseApproval] = None,
    rejection_reason: Optional[str] = None,
    ip_address: Optional[str] = None,
) -> AccountsExpenseRead:
    """Approve or reject a direct expense / reimbursement claim."""
    if data is not None:
        action = data.action
        rejection_reason = data.rejection_reason
    action = (action or "APPROVE").strip().upper()

    is_sa = permissions.is_super_admin_user(session, user)
    has_perm = (
        is_sa
        or permissions.has_permission(session, user, "ACCOUNTS_EXPENSES", "approve")
        or permissions.has_permission(session, user, "ACCOUNTS_EXPENSES", "edit")
        or permissions.has_permission(session, user, "ACCOUNTS", "approve")
    )
    if not has_perm:
        raise permissions.PermissionDeniedError("You do not have permission to approve expenses.")
        
    exp = session.get(AccountsExpense, expense_id)
    if not exp:
        raise ValueError(f"Expense {expense_id} not found.")
        
    old_st = exp.approval_status
    if action == "APPROVE":
        exp.approval_status = "APPROVED"
        exp.approved_by_user_id = user.user_id
        exp.approved_at = datetime.now(timezone.utc)
        exp.rejection_reason = None
    elif action == "REJECT":
        exp.approval_status = "REJECTED"
        exp.rejection_reason = rejection_reason.strip() if rejection_reason else "Rejected by Accounts"
    else:
        raise ValueError(f"Invalid action '{action}'. Use APPROVE or REJECT.")
        
    session.add(exp)
    session.flush()
    
    _log_accounts_audit(
        session=session,
        company_id=exp.company_id,
        entity_type="EXPENSE",
        entity_id=exp.expense_id,
        action=action,
        actor_user_id=user.user_id,
        old_values={"status": old_st},
        new_values={"status": exp.approval_status, "reason": exp.rejection_reason},
        ip_address=ip_address,
    )
    
    session.commit()
    return _to_expense_read(exp)


def settle_reimbursement(
    session: Session,
    user: User,
    expense_id: uuid.UUID,
    settlement_reference: Optional[str] = None,
    data: Optional[AccountsReimbursementSettle] = None,
    ip_address: Optional[str] = None,
) -> AccountsExpenseRead:
    """Disburse payment to employee to settle an approved reimbursement claim."""
    if data is not None:
        settlement_reference = data.settlement_reference

    is_sa = permissions.is_super_admin_user(session, user)
    has_perm = (
        is_sa
        or permissions.has_permission(session, user, "ACCOUNTS_EXPENSES", "approve")
        or permissions.has_permission(session, user, "ACCOUNTS_EXPENSES", "edit")
        or permissions.has_permission(session, user, "ACCOUNTS", "edit")
    )
    if not has_perm:
        raise permissions.PermissionDeniedError("You do not have permission to settle employee reimbursements.")
        
    exp = session.get(AccountsExpense, expense_id)
    if not exp:
        raise ValueError(f"Expense {expense_id} not found.")
        
    if exp.paid_by_type != "EMPLOYEE":
        raise ValueError("Only employee reimbursement claims require settlement.")
        
    if exp.approval_status != "APPROVED":
        raise ValueError("Reimbursements must be approved before settlement disbursement.")
        
    exp.settlement_status = "SETTLED"
    exp.settled_at = datetime.now(timezone.utc)
    exp.settled_by_user_id = user.user_id
    exp.settlement_reference = settlement_reference.strip() if settlement_reference else "Direct Settlement"
    session.add(exp)
    session.flush()
    
    _log_accounts_audit(
        session=session,
        company_id=exp.company_id,
        entity_type="EXPENSE",
        entity_id=exp.expense_id,
        action="SETTLE",
        actor_user_id=user.user_id,
        new_values={"settlement_status": "SETTLED", "reference": exp.settlement_reference},
        ip_address=ip_address,
    )
    
    session.commit()
    return _to_expense_read(exp)


def _to_expense_read(exp: AccountsExpense) -> AccountsExpenseRead:
    """Convert ORM AccountsExpense to Read DTO."""
    amt = float(exp.amount)
    c_name = f"{exp.created_by.first_name} {exp.created_by.last_name}".strip() if exp.created_by else None
    p_name = f"{exp.paid_by_user.first_name} {exp.paid_by_user.last_name}".strip() if exp.paid_by_user else None
    app_name = f"{exp.approved_by.first_name} {exp.approved_by.last_name}".strip() if exp.approved_by else None
    set_name = f"{exp.settled_by.first_name} {exp.settled_by.last_name}".strip() if exp.settled_by else None
    
    return AccountsExpenseRead(
        expense_id=exp.expense_id,
        company_id=exp.company_id,
        company_name=exp.company.company_name if exp.company else None,
        sales_order_id=exp.sales_order_id,
        sales_order_number=exp.sales_order.order_number if exp.sales_order else None,
        client_name=exp.sales_order.client.client_name if exp.sales_order and exp.sales_order.client else None,
        expense_number=exp.expense_number,
        category=exp.category,
        amount=amt,
        formatted_amount=format_inr(amt),
        expense_date=exp.expense_date,
        formatted_expense_date=exp.expense_date.strftime("%d %b %Y"),
        payee_name=exp.payee_name,
        paid_by_type=exp.paid_by_type,
        paid_by_user_id=exp.paid_by_user_id,
        paid_by_user_name=p_name,
        payment_mode=exp.payment_mode,
        transaction_reference=exp.transaction_reference,
        bill_attachment_path=exp.bill_attachment_path,
        bill_attachment_name=exp.bill_attachment_name,
        remark=exp.remark,
        approval_status=exp.approval_status,
        approved_by_user_id=exp.approved_by_user_id,
        approved_by_name=app_name,
        approved_at=exp.approved_at,
        rejection_reason=exp.rejection_reason,
        settlement_status=exp.settlement_status,
        settled_at=exp.settled_at,
        settled_by_user_id=exp.settled_by_user_id,
        settled_by_name=set_name,
        settlement_reference=exp.settlement_reference,
        created_by_user_id=exp.created_by_user_id,
        created_by_name=c_name,
        created_at=exp.created_at,
    )


# -----------------------------------------------------------------------------
# 7. Accounts Dashboard Analytics
# -----------------------------------------------------------------------------
def get_accounts_dashboard_data(
    session: Session,
    user: User,
    company_id: Optional[str] = None,
    salesperson_id: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    **kwargs,
) -> AccountsDashboardResponse:
    """Compute live financial metrics, collection trends, ageing analysis, and drill-down datasets."""
    scope_ctx = permissions.resolve_data_scope_context(session, user, "ACCOUNTS_DASHBOARD")
    
    today = date.today()
    dt_from = date_from or start_date or (today - timedelta(days=30))
    dt_to = date_to or end_date or today
    
    # 1. Confirmed Orders in date range
    order_stmt = (
        select(SalesOrder)
        .where(
            SalesOrder.confirmation_status == "CONFIRMED",
            SalesOrder.order_date >= dt_from,
            SalesOrder.order_date <= dt_to,
        )
        .options(
            joinedload(SalesOrder.client),
            joinedload(SalesOrder.company),
            joinedload(SalesOrder.salesperson),
            joinedload(SalesOrder.service),
            selectinload(SalesOrder.payment_transactions),
        )
    )
    order_stmt = _apply_accounts_scope(order_stmt, user, scope_ctx)
    if company_id and company_id != "ALL":
        try:
            order_stmt = order_stmt.where(SalesOrder.company_id == uuid.UUID(company_id))
        except ValueError:
            pass
    if salesperson_id and salesperson_id != "ALL":
        try:
            order_stmt = order_stmt.where(SalesOrder.salesperson_user_id == uuid.UUID(salesperson_id))
        except ValueError:
            pass
            
    range_orders = session.execute(order_stmt).unique().scalars().all()
    _reconcile_legacy_advances(session, range_orders)
    
    conf_order_val = sum(float(o.order_value or 0) for o in range_orders)
    conf_order_cnt = len(range_orders)
    
    # 2. Verified Collections in date range
    pay_stmt = (
        select(PaymentTransaction)
        .where(
            PaymentTransaction.payment_date >= dt_from,
            PaymentTransaction.payment_date <= dt_to,
        )
        .options(
            joinedload(PaymentTransaction.sales_order).joinedload(SalesOrder.client),
        )
    )
    if scope_ctx.scope != "ALL":
        pay_stmt = pay_stmt.where(PaymentTransaction.company_id == scope_ctx.company_id)
    if company_id and company_id != "ALL":
        try:
            pay_stmt = pay_stmt.where(PaymentTransaction.company_id == uuid.UUID(company_id))
        except ValueError:
            pass
            
    range_payments = session.execute(pay_stmt).scalars().all()
    verified_payments = [p for p in range_payments if p.verification_status == "VERIFIED"]
    unverified_payments = [p for p in range_payments if p.verification_status == "PENDING_VERIFICATION"]
    
    ver_col_amt = sum(float(p.amount) for p in verified_payments)
    unver_col_amt = sum(float(p.amount) for p in unverified_payments)
    
    # 3. As-of-Today Outstanding & Overdue across all confirmed orders
    all_order_stmt = (
        select(SalesOrder)
        .where(SalesOrder.confirmation_status == "CONFIRMED")
        .options(
            joinedload(SalesOrder.company),
            joinedload(SalesOrder.client),
            joinedload(SalesOrder.service),
            joinedload(SalesOrder.salesperson),
            joinedload(SalesOrder.application),
            selectinload(SalesOrder.payment_transactions),
        )
    )
    all_order_stmt = _apply_accounts_scope(all_order_stmt, user, scope_ctx)
    if company_id and company_id != "ALL":
        try:
            all_order_stmt = all_order_stmt.where(SalesOrder.company_id == uuid.UUID(company_id))
        except ValueError:
            pass
    if salesperson_id and salesperson_id != "ALL":
        try:
            all_order_stmt = all_order_stmt.where(SalesOrder.salesperson_user_id == uuid.UUID(salesperson_id))
        except ValueError:
            pass
            
    all_orders = session.execute(all_order_stmt).unique().scalars().all()
    _reconcile_legacy_advances(session, all_orders)
    
    curr_outstanding = 0.0
    curr_overdue = 0.0
    outstanding_cnt = 0
    overdue_cnt = 0
    
    ageing_dict: Dict[str, Dict[str, Any]] = {
        "CURRENT": {"label": "Current (Not Due)", "amount": 0.0, "count": 0, "color": "#10b981"},
        "1_30_DAYS": {"label": "1–30 Days Overdue", "amount": 0.0, "count": 0, "color": "#3b82f6"},
        "31_60_DAYS": {"label": "31–60 Days Overdue", "amount": 0.0, "count": 0, "color": "#f59e0b"},
        "61_90_DAYS": {"label": "61–90 Days Overdue", "amount": 0.0, "count": 0, "color": "#f97316"},
        "OVER_90_DAYS": {"label": "90+ Days Critical", "amount": 0.0, "count": 0, "color": "#ef4444"},
    }
    
    debtor_list: List[TopOutstandingItem] = []
    company_agg: Dict[uuid.UUID, Dict[str, Any]] = {}
    
    for order in all_orders:
        t_val = float(order.order_value or 0)
        v_rec = sum(float(p.amount) for p in order.payment_transactions if p.verification_status == "VERIFIED")
        pend = max(0.0, t_val - v_rec)
        
        c_id = order.company_id
        c_name = order.company.company_name if order.company else "GoCompliance"
        if c_id not in company_agg:
            company_agg[c_id] = {"name": c_name, "order_val": 0.0, "received": 0.0, "outstanding": 0.0}
        company_agg[c_id]["order_val"] += t_val
        company_agg[c_id]["received"] += v_rec
        company_agg[c_id]["outstanding"] += pend
        
        if pend > 0:
            curr_outstanding += pend
            outstanding_cnt += 1
            
            due_dt = order.order_date + timedelta(days=15)
            days_od = (today - due_dt).days if today > due_dt else 0
            
            if days_od > 0:
                curr_overdue += pend
                overdue_cnt += 1
                
            if today <= due_dt:
                ageing_dict["CURRENT"]["amount"] += pend
                ageing_dict["CURRENT"]["count"] += 1
            elif 1 <= days_od <= 30:
                ageing_dict["1_30_DAYS"]["amount"] += pend
                ageing_dict["1_30_DAYS"]["count"] += 1
            elif 31 <= days_od <= 60:
                ageing_dict["31_60_DAYS"]["amount"] += pend
                ageing_dict["31_60_DAYS"]["count"] += 1
            elif 61 <= days_od <= 90:
                ageing_dict["61_90_DAYS"]["amount"] += pend
                ageing_dict["61_90_DAYS"]["count"] += 1
            else:
                ageing_dict["OVER_90_DAYS"]["amount"] += pend
                ageing_dict["OVER_90_DAYS"]["count"] += 1
                
            sp_name = f"{order.salesperson.first_name} {order.salesperson.last_name}".strip() if order.salesperson else "—"
            op_st = order.application.application_status if order.application else None
            
            debtor_list.append(
                TopOutstandingItem(
                    sales_order_id=order.order_id,
                    order_number=order.order_number,
                    client_name=order.client.client_name if order.client else "—",
                    service_name=order.service.service_name if order.service else "—",
                    salesperson_name=sp_name,
                    total_payable=t_val,
                    verified_received=v_rec,
                    pending_amount=pend,
                    formatted_pending_amount=format_inr(pend),
                    days_overdue=days_od,
                    operation_status=op_st,
                )
            )
            
    debtor_list.sort(key=lambda d: d.pending_amount, reverse=True)
    top_outstanding = debtor_list[:5]
    
    # 4. Direct Costs in date range
    exp_stmt = (
        select(AccountsExpense)
        .where(
            AccountsExpense.approval_status == "APPROVED",
            AccountsExpense.expense_date >= dt_from,
            AccountsExpense.expense_date <= dt_to,
        )
    )
    if scope_ctx.scope != "ALL":
        exp_stmt = exp_stmt.where(AccountsExpense.company_id == scope_ctx.company_id)
    if company_id and company_id != "ALL":
        try:
            exp_stmt = exp_stmt.where(AccountsExpense.company_id == uuid.UUID(company_id))
        except ValueError:
            pass
            
    approved_expenses = session.execute(exp_stmt).scalars().all()
    direct_costs_amt = sum(float(e.amount) for e in approved_expenses)
    
    # Estimated Margin
    est_margin = max(0.0, conf_order_val - direct_costs_amt)
    margin_pct = (est_margin / conf_order_val * 100.0) if conf_order_val > 0 else 0.0
    
    kpis = AccountsKpiSummary(
        confirmed_order_value=conf_order_val,
        formatted_confirmed_order_value=format_inr(conf_order_val),
        confirmed_order_count=conf_order_cnt,
        verified_collections=ver_col_amt,
        formatted_verified_collections=format_inr(ver_col_amt),
        verified_collections_count=len(verified_payments),
        unverified_collections=unver_col_amt,
        formatted_unverified_collections=format_inr(unver_col_amt),
        unverified_collections_count=len(unverified_payments),
        current_outstanding=curr_outstanding,
        formatted_current_outstanding=format_inr(curr_outstanding),
        outstanding_orders_count=outstanding_cnt,
        current_overdue=curr_overdue,
        formatted_current_overdue=format_inr(curr_overdue),
        overdue_orders_count=overdue_cnt,
        recorded_direct_costs=direct_costs_amt,
        formatted_recorded_direct_costs=format_inr(direct_costs_amt),
        estimated_order_margin=est_margin,
        formatted_estimated_order_margin=format_inr(est_margin),
        margin_percentage=round(margin_pct, 1),
    )
    
    # 5. Collections Trend Points (grouped by day)
    trend_map: Dict[str, float] = {}
    trend_cnt_map: Dict[str, int] = {}
    curr_dt = dt_from
    while curr_dt <= dt_to:
        ds = curr_dt.strftime("%Y-%m-%d")
        trend_map[ds] = 0.0
        trend_cnt_map[ds] = 0
        curr_dt += timedelta(days=1)
        
    for p in verified_payments:
        ds = p.payment_date.strftime("%Y-%m-%d")
        if ds in trend_map:
            trend_map[ds] += float(p.amount)
            trend_cnt_map[ds] += 1
            
    trend_points: List[CollectionsTrendPoint] = [
        CollectionsTrendPoint(
            date=d_str,
            label=datetime.strptime(d_str, "%Y-%m-%d").strftime("%d %b"),
            verified_amount=amt,
            order_count=trend_cnt_map[d_str],
        )
        for d_str, amt in sorted(trend_map.items())
    ]
    
    # 6. Ageing Breakdown Items
    ageing_breakdown: List[AgeingBreakdownItem] = []
    tot_ageing_amt = sum(v["amount"] for v in ageing_dict.values())
    for b_key, b_info in ageing_dict.items():
        pct = (b_info["amount"] / tot_ageing_amt * 100.0) if tot_ageing_amt > 0 else 0.0
        ageing_breakdown.append(
            AgeingBreakdownItem(
                bucket=b_key,
                label=b_info["label"],
                amount=b_info["amount"],
                count=b_info["count"],
                percentage=round(pct, 1),
                color=b_info["color"],
            )
        )
        
    # 7. Company Breakdown Items
    company_breakdown: List[CompanyFinancialItem] = []
    for c_uuid, c_data in company_agg.items():
        c_rate = (c_data["received"] / c_data["order_val"] * 100.0) if c_data["order_val"] > 0 else 0.0
        company_breakdown.append(
            CompanyFinancialItem(
                company_id=c_uuid,
                company_name=c_data["name"],
                order_value=c_data["order_val"],
                verified_received=c_data["received"],
                outstanding=c_data["outstanding"],
                collection_rate=round(c_rate, 1),
            )
        )
        
    # 8. Category Expense Items
    cat_names = {
        "GOVT_FEES": "Statutory / Govt Fees",
        "VENDOR_COST": "Vendor / Outlay Cost",
        "INCIDENTAL_COST": "Incidental Cost",
        "EMPLOYEE_REIMBURSEMENT": "Employee Reimbursements",
        "OTHER_DIRECT_COST": "Other Direct Cost",
    }
    cat_agg: Dict[str, float] = {}
    cat_cnt: Dict[str, int] = {}
    for exp in approved_expenses:
        cat_agg[exp.category] = cat_agg.get(exp.category, 0.0) + float(exp.amount)
        cat_cnt[exp.category] = cat_cnt.get(exp.category, 0) + 1
        
    expense_breakdown: List[CategoryExpenseItem] = []
    for c_code, c_amt in cat_agg.items():
        pct = (c_amt / direct_costs_amt * 100.0) if direct_costs_amt > 0 else 0.0
        expense_breakdown.append(
            CategoryExpenseItem(
                category=c_code,
                label=cat_names.get(c_code, c_code),
                amount=c_amt,
                percentage=round(pct, 1),
                count=cat_cnt.get(c_code, 0),
            )
        )
        
    # 9. Recent Transactions
    sorted_recent = sorted(range_payments, key=lambda p: (p.payment_date, p.created_at), reverse=True)[:6]
    recent_transactions: List[RecentTransactionItem] = [
        RecentTransactionItem(
            payment_id=p.payment_id,
            payment_number=p.payment_number,
            sales_order_number=p.sales_order.order_number if p.sales_order else "—",
            client_name=p.sales_order.client.client_name if p.sales_order and p.sales_order.client else "—",
            amount=float(p.amount),
            formatted_amount=format_inr(float(p.amount)),
            payment_date=p.payment_date.strftime("%d %b %Y"),
            payment_mode=p.payment_mode,
            verification_status=p.verification_status,
        )
        for p in sorted_recent
    ]
    
    filter_opts = get_accounts_filter_options(session, user)
    
    return AccountsDashboardResponse(
        date_range={
            "start_date": dt_from.strftime("%Y-%m-%d"),
            "end_date": dt_to.strftime("%Y-%m-%d"),
            "formatted": f"{dt_from.strftime('%d %b %Y')} – {dt_to.strftime('%d %b %Y')}",
        },
        kpis=kpis,
        collections_trend=trend_points,
        ageing_breakdown=ageing_breakdown,
        company_breakdown=company_breakdown,
        expense_breakdown=expense_breakdown,
        recent_transactions=recent_transactions,
        top_outstanding=top_outstanding,
        filter_options=filter_opts,
    )


# -----------------------------------------------------------------------------
# 8. Filtered Financial CSV Reports
# -----------------------------------------------------------------------------
def export_payment_register_csv(
    session: Session,
    user: User,
    company_id: Optional[str] = None,
    client_id: Optional[str] = None,
    salesperson_id: Optional[str] = None,
    payment_status: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
) -> str:
    """Generate safe, sanitized CSV content for Payment Register export."""
    reg = get_payment_register(
        session=session,
        user=user,
        page=1,
        limit=5000,
        company_id=company_id,
        client_id=client_id,
        salesperson_id=salesperson_id,
        payment_status=payment_status,
        date_from=date_from,
        date_to=date_to,
    )
    
    output = io.StringIO()
    writer = csv.writer(output, dialect="excel")
    
    writer.writerow([
        "S.No",
        "Order Number",
        "Order Date",
        "Company",
        "Client Name",
        "Location",
        "Service",
        "Salesperson",
        "Total Amount (INR)",
        "Verified Received (INR)",
        "Unverified Collection (INR)",
        "Pending Balance (INR)",
        "Payment Status",
        "Due Date",
        "Days Overdue",
        "Proforma Inv No",
        "Tax Inv No",
        "Latest Remark",
    ])
    
    for idx, item in enumerate(reg.items, 1):
        writer.writerow([
            idx,
            sanitize_csv_field(item.order_number),
            sanitize_csv_field(item.formatted_order_date),
            sanitize_csv_field(item.company_name),
            sanitize_csv_field(item.client_name),
            sanitize_csv_field(item.location or ""),
            sanitize_csv_field(item.service_name),
            sanitize_csv_field(item.salesperson_name),
            item.total_payable,
            item.verified_received,
            item.unverified_amount,
            item.pending_amount,
            sanitize_csv_field(item.payment_status),
            sanitize_csv_field(item.formatted_due_date or ""),
            item.days_overdue,
            sanitize_csv_field(item.proforma_invoice_no or ""),
            sanitize_csv_field(item.tax_invoice_no or ""),
            sanitize_csv_field(item.latest_remark or ""),
        ])
        
    return output.getvalue()


def export_outstanding_ageing_csv(
    session: Session,
    user: User,
    company_id: Optional[str] = None,
    ageing_bucket: Optional[str] = None,
) -> str:
    """Generate safe CSV content for Debtors Outstanding & Ageing report."""
    res = get_outstanding_receivables(
        session=session,
        user=user,
        page=1,
        limit=5000,
        company_id=company_id,
        ageing_bucket=ageing_bucket,
    )
    
    output = io.StringIO()
    writer = csv.writer(output, dialect="excel")
    
    writer.writerow([
        "S.No",
        "Order Number",
        "Order Date",
        "Company",
        "Client Name",
        "Contact Phone",
        "Location",
        "Service",
        "Salesperson",
        "Total Amount (INR)",
        "Verified Received (INR)",
        "Pending Balance (INR)",
        "Due Date",
        "Days Overdue",
        "Ageing Bucket",
        "Operations Status",
        "Latest Follow-up Date",
        "Latest Follow-up Remark",
    ])
    
    for idx, item in enumerate(res.items, 1):
        fu_dt = item.latest_follow_up.formatted_follow_up_date if item.latest_follow_up else ""
        fu_rem = item.latest_follow_up.remark_text if item.latest_follow_up else ""
        writer.writerow([
            idx,
            sanitize_csv_field(item.order_number),
            sanitize_csv_field(item.formatted_order_date),
            sanitize_csv_field(item.company_name),
            sanitize_csv_field(item.client_name),
            sanitize_csv_field(item.client_phone or ""),
            sanitize_csv_field(item.location or ""),
            sanitize_csv_field(item.service_name),
            sanitize_csv_field(item.salesperson_name),
            item.total_payable,
            item.verified_received,
            item.pending_amount,
            sanitize_csv_field(item.formatted_due_date or ""),
            item.days_overdue,
            sanitize_csv_field(item.ageing_bucket),
            sanitize_csv_field(item.operation_status or "PENDING"),
            sanitize_csv_field(fu_dt),
            sanitize_csv_field(fu_rem),
        ])
        
    return output.getvalue()
