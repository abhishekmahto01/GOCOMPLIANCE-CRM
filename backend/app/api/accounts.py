"""FastAPI router for Accounts & Financial Management module.
Includes Payment Register, Outstanding & Follow-ups, Invoices, Expenses, Dashboard, Reports, and Secure File Access.
"""
import io
import os
import uuid
from datetime import date
from typing import List, Optional

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Query,
    Response,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import require_fully_activated_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.accounts import (
    AccountsDashboardResponse,
    AccountsEntriesResponse,
    AccountsEntryRead,
    AccountsEntryUpdate,
    AccountsExpenseApproval,
    AccountsExpenseCreate,
    AccountsExpenseListResponse,
    AccountsExpenseRead,
    AccountsFilterOptions,
    AccountsFollowUpCreate,
    AccountsFollowUpRead,
    AccountsInvoiceCreate,
    AccountsInvoiceListResponse,
    AccountsInvoiceRead,
    AccountsReimbursementSettle,
    OutstandingResponse,
    PaymentRegisterResponse,
    PaymentTransactionCreate,
    PaymentTransactionListResponse,
    PaymentTransactionRead,
    PaymentTransactionReverse,
    PaymentTransactionVerify,
)
from app.services import accounts_service, permissions

router = APIRouter(prefix="/accounts", tags=["Accounts & Financial Management"])


def check_access(session: Session, user: User, module_codes: List[str], action: str = "view") -> bool:
    """Evaluate permission across a list of module codes (e.g. child module fallback to parent module)."""
    if permissions.is_super_admin_user(session, user):
        return True
    for mod in module_codes:
        if permissions.has_permission(session, user, mod, action):
            return True
    return False


# ============================================================================
# FILTER OPTIONS & METADATA
# ============================================================================

@router.get(
    "/filter-options",
    response_model=AccountsFilterOptions,
    status_code=status.HTTP_200_OK,
    summary="Get Accounts Filter Dropdown Options",
    description="Retrieve companies, employees, and services available for filtering accounts data.",
)
def get_accounts_filter_options(
    current_user: User = Depends(require_fully_activated_user),
    session: Session = Depends(get_db),
) -> AccountsFilterOptions:
    try:
        return accounts_service.get_accounts_filter_options(session=session, user=current_user)
    except permissions.PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


# ============================================================================
# DASHBOARD
# ============================================================================

@router.get(
    "/dashboard",
    response_model=AccountsDashboardResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Accounts Financial Dashboard Analytics",
    description="Retrieve order value, advance amount, pending amount, direct costs, and payment status breakdown.",
)
def get_accounts_dashboard(
    company_id: Optional[str] = Query(None, description="Filter by company ID"),
    employee_id: Optional[str] = Query(None, description="Filter by salesperson ID"),
    from_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    to_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    current_user: User = Depends(require_fully_activated_user),
    session: Session = Depends(get_db),
) -> AccountsDashboardResponse:
    if not check_access(session, current_user, ["ACCOUNTS_DASHBOARD", "ACCOUNTS"], "view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to Accounts Dashboard")

    try:
        return accounts_service.get_accounts_dashboard_data(
            session=session,
            user=current_user,
            company_id=company_id,
            salesperson_id=employee_id,
            date_from=from_date,
            date_to=to_date,
        )
    except permissions.PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


# ============================================================================
# ACCOUNTS ENTRIES (CANONICAL 21 COLUMNS)
# ============================================================================

@router.get(
    "/entries/export",
    status_code=status.HTTP_200_OK,
    summary="Export Accounts Entries to Safe CSV",
    description="Export filtered Accounts Entries with all 21 canonical columns.",
)
def export_accounts_entries(
    search: Optional[str] = Query(None, description="Search term"),
    company_id: Optional[str] = Query(None, description="Company filter"),
    payment_status: Optional[str] = Query(None, description="Payment status filter"),
    from_date: Optional[date] = Query(None, description="Start date"),
    to_date: Optional[date] = Query(None, description="End date"),
    current_user: User = Depends(require_fully_activated_user),
    session: Session = Depends(get_db),
):
    if not (
        check_access(session, current_user, ["ACCOUNTS_ENTRIES", "ACCOUNTS"], "export")
        or check_access(session, current_user, ["ACCOUNTS_ENTRIES", "ACCOUNTS"], "view")
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to export Accounts Entries")

    try:
        csv_data = accounts_service.export_accounts_entries_csv(
            session=session,
            user=current_user,
            search=search,
            payment_status=payment_status,
            date_from=from_date,
            date_to=to_date,
            company_id=company_id,
        )
        filename = f"Accounts_Entries_{date.today().strftime('%Y%m%d')}.csv"
        return Response(
            content=csv_data,
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except permissions.PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get(
    "/entries",
    response_model=AccountsEntriesResponse,
    status_code=status.HTTP_200_OK,
    summary="List Accounts Entries",
    description="Retrieve all shared sales orders across company scope with the 21 canonical columns.",
)
def list_accounts_entries(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=200, description="Items per page"),
    search: Optional[str] = Query(None, description="Search client, work, order no, location, salesperson, or remarks"),
    company_id: Optional[str] = Query(None, description="Company filter"),
    payment_status: Optional[str] = Query(None, description="Payment status filter"),
    from_date: Optional[date] = Query(None, description="Order start date (YYYY-MM-DD)"),
    to_date: Optional[date] = Query(None, description="Order end date (YYYY-MM-DD)"),
    current_user: User = Depends(require_fully_activated_user),
    session: Session = Depends(get_db),
) -> AccountsEntriesResponse:
    if not check_access(session, current_user, ["ACCOUNTS_ENTRIES", "ACCOUNTS"], "view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to Accounts Entries")

    try:
        return accounts_service.get_accounts_entries(
            session=session,
            user=current_user,
            page=page,
            limit=limit,
            search=search,
            payment_status=payment_status,
            date_from=from_date,
            date_to=to_date,
            company_id=company_id,
        )
    except permissions.PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.patch(
    "/entries/{order_id}",
    response_model=AccountsEntryRead,
    status_code=status.HTTP_200_OK,
    summary="Update Accounts Entry (Allowed 4 Fields)",
    description="Accounts users may only edit Proforma Inv. No., Tax Inv. No., Reimbursement Note, and Remarks.",
)
@router.put(
    "/entries/{order_id}",
    response_model=AccountsEntryRead,
    status_code=status.HTTP_200_OK,
    summary="Update Accounts Entry (Allowed 4 Fields)",
    description="Accounts users may only edit Proforma Inv. No., Tax Inv. No., Reimbursement Note, and Remarks.",
)
def update_accounts_entry(
    order_id: uuid.UUID,
    data: AccountsEntryUpdate,
    current_user: User = Depends(require_fully_activated_user),
    session: Session = Depends(get_db),
) -> AccountsEntryRead:
    if not (
        check_access(session, current_user, ["ACCOUNTS_ENTRIES", "ACCOUNTS"], "edit")
        or check_access(session, current_user, ["ACCOUNTS_ENTRIES", "ACCOUNTS"], "update")
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to edit Accounts Entries")

    try:
        return accounts_service.update_accounts_entry(
            session=session,
            user=current_user,
            order_id=order_id,
            data=data,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except permissions.PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


# ============================================================================
# PAYMENT REGISTER & RECORDING
# ============================================================================

@router.get(
    "/payments",
    response_model=PaymentRegisterResponse,
    status_code=status.HTTP_200_OK,
    summary="List Payment Register Ledger",
    description="Paginated and searchable accounts ledger with calculated balances and remarks.",
)
def list_payment_register(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search client, order no, company, license, or remark"),
    company_id: Optional[str] = Query(None, description="Company filter"),
    client_id: Optional[str] = Query(None, description="Client filter"),
    salesperson_id: Optional[str] = Query(None, description="Salesperson filter"),
    payment_status: Optional[str] = Query(None, description="Payment status filter"),
    overdue_only: bool = Query(False, description="Filter overdue orders only"),
    from_date: Optional[date] = Query(None, description="Order start date"),
    to_date: Optional[date] = Query(None, description="Order end date"),
    current_user: User = Depends(require_fully_activated_user),
    session: Session = Depends(get_db),
) -> PaymentRegisterResponse:
    if not check_access(session, current_user, ["ACCOUNTS_PAYMENT_REGISTER", "ACCOUNTS", "SALES"], "view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to Payment Register")

    try:
        return accounts_service.get_payment_register(
            session=session,
            user=current_user,
            page=page,
            limit=limit,
            search=search,
            company_id=company_id,
            client_id=client_id,
            salesperson_id=salesperson_id,
            payment_status=payment_status,
            is_overdue=overdue_only,
            date_from=from_date,
            date_to=to_date,
        )
    except permissions.PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post(
    "/payments",
    response_model=PaymentTransactionRead,
    status_code=status.HTTP_201_CREATED,
    summary="Record a Collection / Payment",
    description="Submit an installment or full collection against a confirmed Sales Order.",
)
def record_payment(
    data: PaymentTransactionCreate,
    current_user: User = Depends(require_fully_activated_user),
    session: Session = Depends(get_db),
) -> PaymentTransactionRead:
    if not check_access(session, current_user, ["ACCOUNTS_PAYMENT_REGISTER", "ACCOUNTS", "SALES"], "create"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to record collections")

    try:
        return accounts_service.record_payment_transaction(session=session, user=current_user, data=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except permissions.PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post(
    "/payments/{payment_id}/verify",
    response_model=PaymentTransactionRead,
    status_code=status.HTTP_200_OK,
    summary="Verify Payment Collection",
    description="Accounts/Director authorizes and verifies a submitted collection, updating order balance.",
)
def verify_payment(
    payment_id: uuid.UUID,
    data: PaymentTransactionVerify,
    current_user: User = Depends(require_fully_activated_user),
    session: Session = Depends(get_db),
) -> PaymentTransactionRead:
    if not (
        check_access(session, current_user, ["ACCOUNTS_PAYMENT_REGISTER", "ACCOUNTS"], "approve")
        or check_access(session, current_user, ["ACCOUNTS_PAYMENT_REGISTER", "ACCOUNTS"], "edit")
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to verify payments")

    try:
        return accounts_service.verify_payment_transaction(session=session, user=current_user, payment_id=payment_id, data=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except permissions.PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post(
    "/payments/{payment_id}/reverse",
    response_model=PaymentTransactionRead,
    status_code=status.HTTP_200_OK,
    summary="Reverse a Payment",
    description="Authorized reversal with mandatory reason, restoring balance and recording audit history.",
)
def reverse_payment(
    payment_id: uuid.UUID,
    data: PaymentTransactionReverse,
    current_user: User = Depends(require_fully_activated_user),
    session: Session = Depends(get_db),
) -> PaymentTransactionRead:
    if not check_access(session, current_user, ["ACCOUNTS_PAYMENT_REGISTER", "ACCOUNTS"], "delete"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to reverse payments")

    try:
        return accounts_service.reverse_payment_transaction(session=session, user=current_user, payment_id=payment_id, data=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except permissions.PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get(
    "/orders/{order_id}/payments",
    response_model=PaymentTransactionListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Order Payment History",
    description="Retrieve all installments, unverified collections, and reversals for a sales order.",
)
def get_order_payment_history(
    order_id: uuid.UUID,
    current_user: User = Depends(require_fully_activated_user),
    session: Session = Depends(get_db),
) -> PaymentTransactionListResponse:
    if not check_access(session, current_user, ["ACCOUNTS_PAYMENT_REGISTER", "ACCOUNTS", "SALES"], "view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to order payment history")

    try:
        return accounts_service.get_order_payment_history(session=session, user=current_user, sales_order_id=order_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except permissions.PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


# ============================================================================
# OUTSTANDING & FOLLOW-UPS
# ============================================================================

@router.get(
    "/outstanding",
    response_model=OutstandingResponse,
    status_code=status.HTTP_200_OK,
    summary="List Outstanding Debtors with Ageing",
    description="Retrieve pending collections with ageing buckets (1-30, 31-60, 61-90, 90+, No Due Date) and latest follow-ups.",
)
def list_outstanding_accounts(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search client, order no, or license"),
    company_id: Optional[str] = Query(None, description="Company filter"),
    client_id: Optional[str] = Query(None, description="Client filter"),
    salesperson_id: Optional[str] = Query(None, description="Salesperson filter"),
    ageing_bucket: Optional[str] = Query(None, description="Ageing bucket filter"),
    operations_completed_only: bool = Query(False, description="Filter for completed Operations work"),
    from_date: Optional[date] = Query(None, description="Start date"),
    to_date: Optional[date] = Query(None, description="End date"),
    current_user: User = Depends(require_fully_activated_user),
    session: Session = Depends(get_db),
) -> OutstandingResponse:
    if not check_access(session, current_user, ["ACCOUNTS_OUTSTANDING", "ACCOUNTS", "SALES"], "view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to Outstanding & Follow-ups")

    try:
        return accounts_service.get_outstanding_receivables(
            session=session,
            user=current_user,
            page=page,
            limit=limit,
            search=search,
            company_id=company_id,
            client_id=client_id,
            salesperson_id=salesperson_id,
            ageing_bucket=ageing_bucket,
            completed_only=operations_completed_only,
            date_from=from_date,
            date_to=to_date,
        )
    except permissions.PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post(
    "/orders/{order_id}/follow-up",
    response_model=AccountsFollowUpRead,
    status_code=status.HTTP_201_CREATED,
    summary="Record a Debtor Follow-up",
    description="Log follow-up communication, next promised date, and remark for an order.",
)
def record_order_follow_up(
    order_id: uuid.UUID,
    data: AccountsFollowUpCreate,
    current_user: User = Depends(require_fully_activated_user),
    session: Session = Depends(get_db),
) -> AccountsFollowUpRead:
    if not check_access(session, current_user, ["ACCOUNTS_OUTSTANDING", "ACCOUNTS", "SALES"], "create"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to record follow-up")

    try:
        return accounts_service.record_accounts_follow_up(session=session, user=current_user, sales_order_id=order_id, data=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except permissions.PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get(
    "/orders/{order_id}/follow-ups",
    response_model=List[AccountsFollowUpRead],
    status_code=status.HTTP_200_OK,
    summary="Get Order Follow-up History",
    description="Retrieve all debtor follow-ups for a specific sales order.",
)
def get_order_follow_ups(
    order_id: uuid.UUID,
    current_user: User = Depends(require_fully_activated_user),
    session: Session = Depends(get_db),
) -> List[AccountsFollowUpRead]:
    if not check_access(session, current_user, ["ACCOUNTS_OUTSTANDING", "ACCOUNTS", "SALES"], "view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to order follow-up history")

    try:
        return accounts_service.get_order_follow_up_history(session=session, sales_order_id=order_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except permissions.PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


# ============================================================================
# INVOICES & RECEIPTS
# ============================================================================

@router.get(
    "/invoices",
    response_model=AccountsInvoiceListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Invoices",
    description="Paginated list of Proforma and Tax Invoices linked to orders.",
)
def list_invoices(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search invoice no, client, order"),
    company_id: Optional[str] = Query(None, description="Company filter"),
    invoice_type: Optional[str] = Query(None, description="Invoice type: PROFORMA, TAX_INVOICE"),
    missing_only: bool = Query(False, description="Filter orders missing tax invoice or receipt"),
    from_date: Optional[date] = Query(None, description="Invoice start date"),
    to_date: Optional[date] = Query(None, description="Invoice end date"),
    current_user: User = Depends(require_fully_activated_user),
    session: Session = Depends(get_db),
) -> AccountsInvoiceListResponse:
    if not check_access(session, current_user, ["ACCOUNTS_INVOICES", "ACCOUNTS", "SALES"], "view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to Invoices")

    try:
        return accounts_service.get_invoices(
            session=session,
            user=current_user,
            page=page,
            limit=limit,
            search=search,
            company_id=company_id,
            invoice_type=invoice_type,
            missing_only=missing_only,
            date_from=from_date,
            date_to=to_date,
        )
    except permissions.PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post(
    "/invoices",
    response_model=AccountsInvoiceRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create or Upload Invoice Record",
    description="Save invoice metadata, validate uniqueness in company/financial year, and update linked sales order numbers.",
)
def create_invoice(
    data: AccountsInvoiceCreate,
    current_user: User = Depends(require_fully_activated_user),
    session: Session = Depends(get_db),
) -> AccountsInvoiceRead:
    if not check_access(session, current_user, ["ACCOUNTS_INVOICES", "ACCOUNTS"], "create"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to create invoice")

    try:
        return accounts_service.create_invoice(session=session, user=current_user, data=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except permissions.PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


# ============================================================================
# EXPENSES & REIMBURSEMENTS
# ============================================================================

@router.get(
    "/expenses",
    response_model=AccountsExpenseListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Direct Expenses and Reimbursements",
    description="Paginated expenses by category, approval, and settlement status.",
)
def list_expenses(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search payee, order no, client, or remark"),
    company_id: Optional[str] = Query(None, description="Company filter"),
    category: Optional[str] = Query(None, description="Category filter"),
    approval_status: Optional[str] = Query(None, description="Approval status: PENDING, APPROVED, REJECTED"),
    settlement_status: Optional[str] = Query(None, description="Settlement status: UNSETTLED, SETTLED"),
    from_date: Optional[date] = Query(None, description="Expense start date"),
    to_date: Optional[date] = Query(None, description="Expense end date"),
    current_user: User = Depends(require_fully_activated_user),
    session: Session = Depends(get_db),
) -> AccountsExpenseListResponse:
    if not check_access(session, current_user, ["ACCOUNTS_EXPENSES", "ACCOUNTS", "OPERATIONS", "SALES"], "view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to Expenses & Reimbursements")

    try:
        return accounts_service.get_expenses(
            session=session,
            user=current_user,
            page=page,
            limit=limit,
            search=search,
            company_id=company_id,
            category=category,
            approval_status=approval_status,
            settlement_status=settlement_status,
            date_from=from_date,
            date_to=to_date,
        )
    except permissions.PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post(
    "/expenses",
    response_model=AccountsExpenseRead,
    status_code=status.HTTP_201_CREATED,
    summary="Record an Order Expense or Reimbursement Claim",
    description="Submit direct cost or employee out-of-pocket claim against an order.",
)
def record_expense(
    data: AccountsExpenseCreate,
    current_user: User = Depends(require_fully_activated_user),
    session: Session = Depends(get_db),
) -> AccountsExpenseRead:
    if not check_access(session, current_user, ["ACCOUNTS_EXPENSES", "ACCOUNTS", "OPERATIONS", "SALES"], "create"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to submit expense")

    try:
        return accounts_service.record_expense(session=session, user=current_user, data=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except permissions.PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post(
    "/expenses/{expense_id}/approve",
    response_model=AccountsExpenseRead,
    status_code=status.HTTP_200_OK,
    summary="Approve or Reject an Expense",
    description="Authorized approval of direct expense or reimbursement claim.",
)
def approve_expense(
    expense_id: uuid.UUID,
    data: AccountsExpenseApproval,
    current_user: User = Depends(require_fully_activated_user),
    session: Session = Depends(get_db),
) -> AccountsExpenseRead:
    if not (
        check_access(session, current_user, ["ACCOUNTS_EXPENSES", "ACCOUNTS"], "approve")
        or check_access(session, current_user, ["ACCOUNTS_EXPENSES", "ACCOUNTS"], "edit")
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to approve expense")

    try:
        return accounts_service.approve_expense(session=session, user=current_user, expense_id=expense_id, data=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except permissions.PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post(
    "/expenses/{expense_id}/settle",
    response_model=AccountsExpenseRead,
    status_code=status.HTTP_200_OK,
    summary="Settle Employee Reimbursement",
    description="Mark approved reimbursement claim as settled with disbursement payment reference.",
)
def settle_expense_reimbursement(
    expense_id: uuid.UUID,
    data: AccountsReimbursementSettle,
    current_user: User = Depends(require_fully_activated_user),
    session: Session = Depends(get_db),
) -> AccountsExpenseRead:
    if not (
        check_access(session, current_user, ["ACCOUNTS_EXPENSES", "ACCOUNTS"], "approve")
        or check_access(session, current_user, ["ACCOUNTS_EXPENSES", "ACCOUNTS"], "edit")
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to settle reimbursement")

    try:
        return accounts_service.settle_reimbursement(session=session, user=current_user, expense_id=expense_id, data=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except permissions.PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


# ============================================================================
# REPORTS & EXPORTS
# ============================================================================

@router.get(
    "/reports/export",
    status_code=status.HTTP_200_OK,
    summary="Export Filtered Accounts Data to Safe CSV",
    description="Export Payments, Outstanding, Expenses, or Client Statements with formula injection protection.",
)
def export_accounts_report(
    report_type: str = Query("payments", description="Report type: payments, outstanding, expenses, client_statement"),
    company_id: Optional[str] = Query(None, description="Company filter"),
    employee_id: Optional[str] = Query(None, description="Salesperson filter"),
    client_name: Optional[str] = Query(None, description="Client name filter for client statement"),
    payment_status: Optional[str] = Query(None, description="Payment status filter"),
    category: Optional[str] = Query(None, description="Expense category filter"),
    from_date: Optional[date] = Query(None, description="Start date"),
    to_date: Optional[date] = Query(None, description="End date"),
    current_user: User = Depends(require_fully_activated_user),
    session: Session = Depends(get_db),
):
    if not (
        check_access(session, current_user, ["ACCOUNTS_REPORTS", "ACCOUNTS"], "export")
        or check_access(session, current_user, ["ACCOUNTS_REPORTS", "ACCOUNTS"], "view")
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to export reports")

    try:
        if report_type == "outstanding":
            csv_data = accounts_service.export_outstanding_ageing_csv(
                session=session,
                user=current_user,
                company_id=company_id,
            )
            filename = f"Outstanding_Ageing_{date.today().strftime('%Y%m%d')}.csv"
        else:
            csv_data = accounts_service.export_payment_register_csv(
                session=session,
                user=current_user,
                company_id=company_id,
                salesperson_id=employee_id,
                payment_status=payment_status,
                date_from=from_date,
                date_to=to_date,
            )
            filename = f"Payment_Register_{date.today().strftime('%Y%m%d')}.csv"

        return Response(
            content=csv_data,
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except permissions.PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


# ============================================================================
# FILE UPLOADS & SECURE ATTACHMENT ACCESS
# ============================================================================

@router.post(
    "/upload-attachment",
    status_code=status.HTTP_200_OK,
    summary="Upload Proof / Bill / Invoice Attachment",
    description="Upload a supporting document (PDF, PNG, JPG) securely to the server.",
)
def upload_accounts_attachment(
    file: UploadFile = File(...),
    subfolder: str = Query("payments", description="Subfolder: payments, invoices, expenses"),
    current_user: User = Depends(require_fully_activated_user),
):
    # Validate extension
    filename = file.filename or "document.pdf"
    ext = os.path.splitext(filename)[1].lower()
    allowed = {".pdf", ".png", ".jpg", ".jpeg", ".webp"}
    if ext not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type '{ext}'. Allowed types: {', '.join(allowed)}",
        )

    # Read content and validate size (max 10MB)
    content = file.file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File size exceeds maximum allowed 10MB")

    subfolder_clean = subfolder.strip().lower()
    if subfolder_clean not in {"payments", "invoices", "expenses"}:
        subfolder_clean = "payments"

    rel_path = accounts_service.save_attachment_file(
        file_bytes=content,
        original_filename=filename,
        subfolder=subfolder_clean,
    )
    return {"file_path": rel_path, "filename": filename, "size": len(content)}


@router.get(
    "/attachments/{subfolder}/{filename}",
    status_code=status.HTTP_200_OK,
    summary="Download Attachment",
    description="Secure authorized access to payment proofs, bills, and invoice PDFs.",
)
def get_accounts_attachment(
    subfolder: str,
    filename: str,
    current_user: User = Depends(require_fully_activated_user),
    session: Session = Depends(get_db),
):
    if not check_access(
        session,
        current_user,
        ["ACCOUNTS", "ACCOUNTS_PAYMENT_REGISTER", "ACCOUNTS_INVOICES", "ACCOUNTS_EXPENSES", "SALES", "OPERATIONS"],
        "view",
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to attachment")

    rel_path = f"uploads/accounts/{subfolder}/{filename}"
    abs_path = accounts_service.get_attachment_absolute_path(rel_path)
    if not os.path.isfile(abs_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attachment not found")

    media_type = "application/pdf" if filename.lower().endswith(".pdf") else "application/octet-stream"
    return FileResponse(path=abs_path, media_type=media_type, filename=filename)
