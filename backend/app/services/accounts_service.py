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
from app.models.operation_application import ApplicationActivityLog, OperationApplication
from app.models.payment_transaction import PaymentTransaction
from app.models.sales_order import SalesOrder
from app.models.service import ServiceMaster
from app.models.task_conversation import TaskConversationMessage
from app.models.user import User
from app.schemas.accounts import (
    AccountsDashboardResponse,
    AccountsEntriesResponse,
    AccountsEntriesSummary,
    AccountsEntryRead,
    AccountsEntryUpdate,
    AccountsExpenseApproval,
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
    AccountsReimbursementSettle,
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
    PaymentStatusBreakdownItem,
    PaymentTransactionCreate,
    PaymentTransactionListResponse,
    PaymentTransactionRead,
    PaymentTransactionReverse,
    PaymentTransactionVerify,
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
    """Apply RBAC data scope filters to SalesOrder or Accounts queries.
    Accounts users see all sales entries within their authorized company scope.
    """
    if context.scope == "ALL":
        return stmt
    return stmt.where(SalesOrder.company_id == (context.company_id or user.company_id))



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
    """Compute live Accounts Dashboard KPIs and payment status breakdown based on authorized Sales records."""
    try:
        scope_ctx = permissions.resolve_data_scope_context(session, user, "ACCOUNTS_DASHBOARD")
    except permissions.PermissionDeniedError:
        scope_ctx = permissions.resolve_data_scope_context(session, user, "ACCOUNTS")

    dt_from = date_from or start_date
    dt_to = date_to or end_date

    order_stmt = (
        select(SalesOrder)
        .where(
            SalesOrder.confirmation_status != "CANCELLED",
            SalesOrder.gst_invoice_required.is_(True),
        )
        .options(
            joinedload(SalesOrder.client),
            joinedload(SalesOrder.company),
            joinedload(SalesOrder.salesperson),
            joinedload(SalesOrder.service),
            joinedload(SalesOrder.application).joinedload(OperationApplication.assigned_to),
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

    if dt_from:
        order_stmt = order_stmt.where(SalesOrder.order_date >= dt_from)
    if dt_to:
        order_stmt = order_stmt.where(SalesOrder.order_date <= dt_to)

    order_stmt = order_stmt.order_by(SalesOrder.order_date.desc(), SalesOrder.created_at.desc())

    orders = session.execute(order_stmt).unique().scalars().all()

    total_entries = len(orders)
    tot_amt = sum(float(o.order_value or 0) for o in orders)
    adv_amt = sum(float(o.amount_received or 0) for o in orders)
    pend_amt = sum(float(o.balance_amount or 0) for o in orders)
    g_fees = sum(float(o.govt_fees or 0) for o in orders)
    inc_cost = sum(float(o.incidental_cost or 0) for o in orders)
    est_profit = sum(
        float(
            o.profit_amount
            if (o.profit_amount is not None and float(o.profit_amount) != 0)
            else ((o.order_value or 0) - (o.govt_fees or 0) - (o.incidental_cost or 0))
        )
        for o in orders
    )

    kpis = AccountsKpiSummary(
        total_entries=total_entries,
        total_amount=tot_amt,
        formatted_total_amount=format_inr(tot_amt),
        advance_amount=adv_amt,
        formatted_advance_amount=format_inr(adv_amt),
        pending_amount=pend_amt,
        formatted_pending_amount=format_inr(pend_amt),
        govt_fees=g_fees,
        formatted_govt_fees=format_inr(g_fees),
        incidental_cost=inc_cost,
        formatted_incidental_cost=format_inr(inc_cost),
        estimated_profit=est_profit,
        formatted_estimated_profit=format_inr(est_profit),
        # Legacy compatibility aliases
        confirmed_order_value=tot_amt,
        formatted_confirmed_order_value=format_inr(tot_amt),
        confirmed_order_count=total_entries,
        verified_collections=adv_amt,
        formatted_verified_collections=format_inr(adv_amt),
        current_outstanding=pend_amt,
        formatted_current_outstanding=format_inr(pend_amt),
    )

    # Payment status breakdown
    status_order = [
        ("FULLY_PAID", "Fully Paid"),
        ("PARTIALLY_PAID", "Partially Paid"),
        ("PENDING", "Pending"),
        ("OVERDUE", "Overdue"),
    ]
    payment_breakdown: List[PaymentStatusBreakdownItem] = []
    for st_code, st_lbl in status_order:
        st_orders = [o for o in orders if o.payment_status == st_code]
        cnt = len(st_orders)
        amt = sum(float(o.order_value or 0) for o in st_orders)
        pct = round((cnt / total_entries * 100.0), 1) if total_entries > 0 else 0.0
        payment_breakdown.append(
            PaymentStatusBreakdownItem(
                status=st_code,
                label=st_lbl,
                count=cnt,
                amount=amt,
                formatted_amount=format_inr(amt),
                percentage=pct,
            )
        )

    # Recent entries (canonical 21-column schema)
    recent_entries = [_to_accounts_entry_read(o, idx + 1) for idx, o in enumerate(orders[:8])]

    filter_opts = get_accounts_filter_options(session, user)

    date_range_dict = {
        "start_date": dt_from.strftime("%Y-%m-%d") if dt_from else "",
        "end_date": dt_to.strftime("%Y-%m-%d") if dt_to else "",
        "formatted": f"{dt_from.strftime('%d %b %Y')} – {dt_to.strftime('%d %b %Y')}" if (dt_from and dt_to) else "All Time",
    }

    return AccountsDashboardResponse(
        date_range=date_range_dict,
        kpis=kpis,
        payment_status_breakdown=payment_breakdown,
        recent_entries=recent_entries,
        filter_options=filter_opts,
    )


# -----------------------------------------------------------------------------
# 7.1 Accounts Entries (Shared Sales Records with Canonical 21 Columns)
# -----------------------------------------------------------------------------
def _to_accounts_entry_read(order: SalesOrder, s_no: int = 1) -> AccountsEntryRead:
    """Map SalesOrder to canonical 21-column AccountsEntryRead."""
    c_name = order.client.client_name if order.client else "—"
    c_phone = order.client.contact_phone if order.client else None
    s_name = order.service.service_name if order.service else "—"
    s_code = order.service.service_code if order.service else None
    sp_name = f"{order.salesperson.first_name} {order.salesperson.last_name}".strip() if order.salesperson else "—"
    sp_code = order.salesperson.employee_code if order.salesperson else None

    app = order.application
    app_id = app.application_id if app else None
    assigned_to_id = app.assigned_to_user_id if app else None
    assigned_to_name = (
        f"{app.assigned_to.first_name} {app.assigned_to.last_name}".strip()
        if (app and app.assigned_to)
        else "Unassigned"
    )
    assigned_to_code = app.assigned_to.employee_code if (app and app.assigned_to) else None
    op_status = app.application_status if app else None
    work_status = app.application_status if app else order.confirmation_status

    t_val = float(order.order_value or 0)
    r_val = float(order.amount_received or 0)
    b_val = float(order.balance_amount or 0)
    g_val = float(order.govt_fees or 0)
    i_val = float(order.incidental_cost or 0)
    p_val = float(
        order.profit_amount
        if (order.profit_amount is not None and float(order.profit_amount) != 0)
        else (t_val - g_val - i_val)
    )

    return AccountsEntryRead(
        s_no=s_no,
        order_id=order.order_id,
        order_number=order.order_number,
        company_id=order.company_id,
        client_id=order.client_id,
        service_id=order.service_id,
        salesperson_user_id=order.salesperson_user_id,
        assigned_to_user_id=assigned_to_id,
        application_id=app_id,
        order_date=order.order_date,
        formatted_date=order.order_date.strftime("%d %b %Y"),
        client_name=c_name,
        location=order.location,
        contact_no=c_phone,
        lead_source=order.lead_source,
        service_name=s_name,
        service_code=s_code,
        salesperson_name=sp_name,
        salesperson_code=sp_code,
        assigned_to_name=assigned_to_name,
        assigned_to_code=assigned_to_code,
        work_status=work_status,
        operation_status=op_status,
        order_value=t_val,
        formatted_order_value=format_inr(t_val),
        amount_received=r_val,
        formatted_amount_received=format_inr(r_val),
        balance_amount=b_val,
        formatted_balance_amount=format_inr(b_val),
        payment_status=order.payment_status,
        proforma_invoice_no=order.proforma_invoice_no,
        tax_invoice_no=order.tax_invoice_no,
        reimbursement_note=order.reimbursement_note,
        govt_fees=g_val,
        formatted_govt_fees=format_inr(g_val),
        incidental_cost=i_val,
        formatted_incidental_cost=format_inr(i_val),
        profit_amount=p_val,
        formatted_profit_amount=format_inr(p_val),
        remarks=order.notes,
        notes=order.notes,
        gst_invoice_required=getattr(order, "gst_invoice_required", True),
        company_name=order.company.company_name if order.company else None,
        company_code=order.company.company_code if order.company else None,
        confirmation_status=order.confirmation_status,
        created_at=order.created_at,
        updated_at=order.updated_at,
    )


def get_accounts_entries(
    session: Session,
    user: User,
    page: int = 1,
    limit: int = 50,
    search: Optional[str] = None,
    payment_status: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    company_id: Optional[str] = None,
) -> AccountsEntriesResponse:
    """Retrieve filtered, paginated Accounts entries showing shared Sales orders across company scope."""
    try:
        scope_ctx = permissions.resolve_data_scope_context(session, user, "ACCOUNTS_ENTRIES")
    except permissions.PermissionDeniedError:
        scope_ctx = permissions.resolve_data_scope_context(session, user, "ACCOUNTS")

    query = (
        select(SalesOrder)
        .join(ClientMaster, SalesOrder.client_id == ClientMaster.client_id)
        .join(ServiceMaster, SalesOrder.service_id == ServiceMaster.service_id)
        .join(User, SalesOrder.salesperson_user_id == User.user_id)
        .outerjoin(OperationApplication, SalesOrder.order_id == OperationApplication.sales_order_id)
        .options(
            joinedload(SalesOrder.client),
            joinedload(SalesOrder.company),
            joinedload(SalesOrder.service),
            joinedload(SalesOrder.salesperson),
            joinedload(SalesOrder.application).joinedload(OperationApplication.assigned_to),
        )
        .where(
            SalesOrder.confirmation_status != "CANCELLED",
            SalesOrder.gst_invoice_required.is_(True),
        )
    )

    query = _apply_accounts_scope(query, user, scope_ctx)

    if company_id and company_id != "ALL":
        try:
            query = query.where(SalesOrder.company_id == uuid.UUID(company_id))
        except ValueError:
            pass

    if date_from:
        query = query.where(SalesOrder.order_date >= date_from)
    if date_to:
        query = query.where(SalesOrder.order_date <= date_to)

    if payment_status and payment_status != "ALL":
        query = query.where(SalesOrder.payment_status == payment_status.upper())

    if search and search.strip():
        term = f"%{search.strip()}%"
        query = query.where(
            or_(
                ClientMaster.client_name.ilike(term),
                ClientMaster.contact_phone.ilike(term),
                SalesOrder.location.ilike(term),
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

    query = query.order_by(SalesOrder.order_date.desc(), SalesOrder.created_at.desc())

    all_matched = session.execute(query).unique().scalars().all()

    total_count = len(all_matched)
    total_val = sum(float(o.order_value or 0) for o in all_matched)
    total_adv = sum(float(o.amount_received or 0) for o in all_matched)
    total_pend = sum(float(o.balance_amount or 0) for o in all_matched)
    total_g_fees = sum(float(o.govt_fees or 0) for o in all_matched)
    total_inc = sum(float(o.incidental_cost or 0) for o in all_matched)
    total_prof = sum(
        float(
            o.profit_amount
            if (o.profit_amount is not None and float(o.profit_amount) != 0)
            else ((o.order_value or 0) - (o.govt_fees or 0) - (o.incidental_cost or 0))
        )
        for o in all_matched
    )

    summary = AccountsEntriesSummary(
        total_orders=total_count,
        total_amount=total_val,
        formatted_total_amount=format_inr(total_val),
        total_advance=total_adv,
        formatted_total_advance=format_inr(total_adv),
        total_pending=total_pend,
        formatted_total_pending=format_inr(total_pend),
        total_govt_fees=total_g_fees,
        formatted_total_govt_fees=format_inr(total_g_fees),
        total_incidental_cost=total_inc,
        formatted_total_incidental_cost=format_inr(total_inc),
        total_profits=total_prof,
        formatted_total_profits=format_inr(total_prof),
    )

    safe_page = max(1, page)
    safe_limit = max(1, min(200, limit))
    offset_val = (safe_page - 1) * safe_limit
    paged_orders = all_matched[offset_val : offset_val + safe_limit]
    total_pages = max(1, (total_count + safe_limit - 1) // safe_limit)

    items = [
        _to_accounts_entry_read(o, s_no=offset_val + idx + 1)
        for idx, o in enumerate(paged_orders)
    ]

    return AccountsEntriesResponse(
        items=items,
        total_count=total_count,
        page=safe_page,
        limit=safe_limit,
        total_pages=total_pages,
        summary=summary,
    )


def update_accounts_entry(
    session: Session,
    user: User,
    order_id: uuid.UUID,
    data: AccountsEntryUpdate,
    ip_address: Optional[str] = None,
) -> AccountsEntryRead:
    """Update only allowed accounts fields (Proforma Inv, Tax Inv, Reimbursement Note, Remarks) on SalesOrder."""
    has_perm = (
        permissions.is_super_admin_user(session, user)
        or permissions.has_permission(session, user, "ACCOUNTS_ENTRIES", "edit")
        or permissions.has_permission(session, user, "ACCOUNTS_ENTRIES", "update")
        or permissions.has_permission(session, user, "ACCOUNTS", "edit")
        or permissions.has_permission(session, user, "ACCOUNTS", "update")
    )
    if not has_perm:
        raise permissions.PermissionDeniedError("You do not have permission to edit Accounts entry fields.")

    try:
        scope_ctx = permissions.resolve_data_scope_context(session, user, "ACCOUNTS_ENTRIES")
    except permissions.PermissionDeniedError:
        scope_ctx = permissions.resolve_data_scope_context(session, user, "ACCOUNTS")

    order = (
        session.query(SalesOrder)
        .options(
            joinedload(SalesOrder.client),
            joinedload(SalesOrder.company),
            joinedload(SalesOrder.service),
            joinedload(SalesOrder.salesperson),
            joinedload(SalesOrder.application).joinedload(OperationApplication.assigned_to),
        )
        .filter(SalesOrder.order_id == order_id)
        .first()
    )

    if not order or order.confirmation_status == "CANCELLED" or not getattr(order, "gst_invoice_required", False):
        raise ValueError(f"Sales order with ID '{order_id}' not found.")

    if not scope_ctx.is_user_permitted(order.salesperson_user_id, order.company_id):
        raise permissions.PermissionDeniedError("You are not authorized to update records for this company.")

    old_values = {
        "proforma_invoice_no": order.proforma_invoice_no,
        "tax_invoice_no": order.tax_invoice_no,
        "reimbursement_note": order.reimbursement_note,
        "notes": order.notes,
    }

    changed = False
    new_values: Dict[str, Any] = {}

    if data.proforma_invoice_no is not None:
        val = data.proforma_invoice_no.strip() if data.proforma_invoice_no else None
        if val != order.proforma_invoice_no:
            order.proforma_invoice_no = val
            changed = True
        new_values["proforma_invoice_no"] = val

    if data.tax_invoice_no is not None:
        val = data.tax_invoice_no.strip() if data.tax_invoice_no else None
        if val != order.tax_invoice_no:
            order.tax_invoice_no = val
            changed = True
        new_values["tax_invoice_no"] = val

    if data.reimbursement_note is not None:
        val = data.reimbursement_note.strip() if data.reimbursement_note else None
        if val != order.reimbursement_note:
            order.reimbursement_note = val
            changed = True
        new_values["reimbursement_note"] = val

    remarks_input = data.remarks if data.remarks is not None else data.notes
    if remarks_input is not None:
        val = remarks_input.strip() if remarks_input else None
        if val and val != order.notes:
            order.notes = val
            changed = True
            # Also record in shared TaskConversationMessage
            author_name = f"{user.first_name} {user.last_name}".strip() or "Accounts"
            author_code = user.employee_code
            dept_name = user.department.department_name if user.department else "Accounts"
            role_name = user.designation.designation_name if user.designation else None

            conv_msg = TaskConversationMessage(
                sales_order_id=order.order_id,
                author_user_id=user.user_id,
                message_type="COMMENT",
                message_text=val,
                author_name=author_name,
                author_employee_code=author_code,
                author_department_name=dept_name,
                author_role_name=role_name,
                created_at=datetime.now(timezone.utc),
            )
            session.add(conv_msg)
        elif val != order.notes:
            order.notes = val
            changed = True
        new_values["notes"] = val

    if changed:
        order.updated_at = datetime.now(timezone.utc)
        session.flush()

        _log_accounts_audit(
            session=session,
            company_id=order.company_id,
            entity_type="SALES_ORDER",
            entity_id=order.order_id,
            action="ACCOUNTS_UPDATE",
            actor_user_id=user.user_id,
            old_values=old_values,
            new_values=new_values,
            reason="Updated Accounts financial fields",
            ip_address=ip_address,
        )

        if order.application:
            comment_str = f"Accounts fields updated by {user.first_name} {user.last_name}"
            activity = ApplicationActivityLog(
                application_id=order.application.application_id,
                actor_user_id=user.user_id,
                action_type="ACCOUNTS_UPDATE",
                old_value=json.dumps(old_values, default=str)[:255],
                new_value=json.dumps(new_values, default=str)[:255],
                comment=comment_str,
                created_at=datetime.now(timezone.utc),
            )
            session.add(activity)

        session.commit()

    return _to_accounts_entry_read(order)


def get_accounts_entry_by_id(
    session: Session,
    user: User,
    order_id: uuid.UUID,
) -> AccountsEntryRead:
    """Retrieve single Accounts Entry ensuring company scope authorization and gst_invoice_required routing flag."""
    try:
        scope_ctx = permissions.resolve_data_scope_context(session, user, "ACCOUNTS_ENTRIES")
    except permissions.PermissionDeniedError:
        scope_ctx = permissions.resolve_data_scope_context(session, user, "ACCOUNTS")

    order = (
        session.query(SalesOrder)
        .options(
            joinedload(SalesOrder.client),
            joinedload(SalesOrder.company),
            joinedload(SalesOrder.service),
            joinedload(SalesOrder.salesperson),
            joinedload(SalesOrder.application).joinedload(OperationApplication.assigned_to),
        )
        .filter(SalesOrder.order_id == order_id)
        .first()
    )

    if not order or order.confirmation_status == "CANCELLED" or not getattr(order, "gst_invoice_required", False):
        raise ValueError(f"Sales order with ID '{order_id}' not found.")

    if not scope_ctx.is_user_permitted(order.salesperson_user_id, order.company_id):
        raise permissions.PermissionDeniedError("You are not authorized to view records for this company.")

    return _to_accounts_entry_read(order)


def export_accounts_entries_csv(
    session: Session,
    user: User,
    search: Optional[str] = None,
    payment_status: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    company_id: Optional[str] = None,
) -> str:
    """Generate safe, sanitized CSV export covering all 21 canonical columns."""
    res = get_accounts_entries(
        session=session,
        user=user,
        page=1,
        limit=10000,
        search=search,
        payment_status=payment_status,
        date_from=date_from,
        date_to=date_to,
        company_id=company_id,
    )

    output = io.StringIO()
    writer = csv.writer(output, dialect="excel")

    writer.writerow([
        "S.No",
        "Date",
        "Client Name",
        "Location",
        "Contact No",
        "Source",
        "Work",
        "Converted By",
        "Assigned To",
        "Work Status",
        "Total Amount (INR)",
        "Advance Amount (INR)",
        "Pending Amount (INR)",
        "Payment Status",
        "Proforma Inv. No.",
        "Tax Inv. No.",
        "Reimbursement Note",
        "Govt Fees (INR)",
        "Incidental Cost (INR)",
        "Profits (INR)",
        "Remarks",
    ])

    for item in res.items:
        writer.writerow([
            item.s_no,
            sanitize_csv_field(item.formatted_date),
            sanitize_csv_field(item.client_name),
            sanitize_csv_field(item.location or ""),
            sanitize_csv_field(item.contact_no or ""),
            sanitize_csv_field(item.lead_source),
            sanitize_csv_field(item.service_name),
            sanitize_csv_field(item.salesperson_name),
            sanitize_csv_field(item.assigned_to_name or "Unassigned"),
            sanitize_csv_field(item.work_status),
            item.order_value,
            item.amount_received,
            item.balance_amount,
            sanitize_csv_field(item.payment_status),
            sanitize_csv_field(item.proforma_invoice_no or ""),
            sanitize_csv_field(item.tax_invoice_no or ""),
            sanitize_csv_field(item.reimbursement_note or ""),
            item.govt_fees,
            item.incidental_cost,
            item.profit_amount,
            sanitize_csv_field(item.remarks or item.notes or ""),
        ])

    return output.getvalue()


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
