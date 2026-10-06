"""Pydantic schemas for the Accounts & Financial Management module."""
import uuid
from datetime import date, datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


# -----------------------------------------------------------------------------
# Common Key-Value and Option Items
# -----------------------------------------------------------------------------
class AccountsFilterOptionItem(BaseModel):
    """Dropdown filter option."""
    id: str
    label: str


class AccountsFilterOptions(BaseModel):
    """Dynamic filter dropdown choices available for the logged-in user."""
    companies: List[AccountsFilterOptionItem]
    clients: List[AccountsFilterOptionItem]
    salespersons: List[AccountsFilterOptionItem]
    payment_statuses: List[AccountsFilterOptionItem]
    payment_modes: List[AccountsFilterOptionItem]
    expense_categories: List[AccountsFilterOptionItem]
    receiving_accounts: List[str]


# -----------------------------------------------------------------------------
# Payment Transactions & Payment Register
# -----------------------------------------------------------------------------
class PaymentTransactionCreate(BaseModel):
    """Payload to record a new payment collection against a sales order."""
    sales_order_id: uuid.UUID
    amount: float = Field(..., gt=0, description="Payment amount in INR (strictly positive)")
    payment_date: date = Field(..., description="Actual payment received date")
    payment_mode: str = Field(default="BANK_TRANSFER", description="Payment mode (CASH, UPI, BANK_TRANSFER, CHEQUE, OTHER)")
    transaction_reference: Optional[str] = Field(None, max_length=100, description="Bank UTR / Cheque # / UPI ref")
    receiving_account: Optional[str] = Field(None, max_length=100, description="Designated receiving bank or cash ledger")
    remark: Optional[str] = Field(None, max_length=1000)
    auto_verify: bool = Field(default=False, description="Automatically mark verified if permitted")


class PaymentTransactionVerify(BaseModel):
    """Payload to verify or reject a pending payment submission."""
    action: str = Field(..., description="Action: VERIFY or REJECT")
    rejection_reason: Optional[str] = Field(None, max_length=500)


class PaymentTransactionReverse(BaseModel):
    """Payload to reverse a verified payment with audit explanation."""
    reversal_reason: str = Field(..., min_length=3, max_length=500, description="Mandatory reversal explanation")


class PaymentTransactionRead(BaseModel):
    """Read representation of a single payment collection transaction."""
    payment_id: uuid.UUID
    company_id: uuid.UUID
    company_name: Optional[str] = None
    sales_order_id: uuid.UUID
    sales_order_number: Optional[str] = None
    client_id: Optional[uuid.UUID] = None
    client_name: Optional[str] = None
    payment_number: str
    amount: float
    formatted_amount: str
    payment_date: date
    formatted_payment_date: str
    payment_mode: str
    transaction_reference: Optional[str] = None
    receiving_account: Optional[str] = None
    proof_attachment_path: Optional[str] = None
    proof_attachment_name: Optional[str] = None
    remark: Optional[str] = None
    submitted_by_user_id: uuid.UUID
    submitted_by_name: Optional[str] = None
    submitted_at: datetime
    formatted_submitted_at: Optional[str] = None
    verification_status: str
    verified_by_user_id: Optional[uuid.UUID] = None
    verified_by_name: Optional[str] = None
    verified_at: Optional[datetime] = None
    formatted_verified_at: Optional[str] = None
    reversal_reason: Optional[str] = None
    reversed_by_user_id: Optional[uuid.UUID] = None
    reversed_by_name: Optional[str] = None
    reversed_at: Optional[datetime] = None
    is_opening_balance: bool = False
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaymentTransactionListResponse(BaseModel):
    """List response for payment transaction history."""
    items: List[PaymentTransactionRead]
    total_count: int
    total_verified_amount: float
    total_unverified_amount: float


class PaymentRegisterItemRead(BaseModel):
    """Order-level aggregated financial status row in the Payment Register."""
    sales_order_id: uuid.UUID
    order_number: str
    order_date: date
    formatted_order_date: str
    company_id: uuid.UUID
    company_name: str
    client_id: uuid.UUID
    client_name: str
    client_phone: Optional[str] = None
    location: Optional[str] = None
    service_id: uuid.UUID
    service_name: str
    service_code: Optional[str] = None
    salesperson_user_id: uuid.UUID
    salesperson_name: str
    salesperson_code: Optional[str] = None
    
    # Financial Aggregates
    total_payable: float
    formatted_total_payable: str
    verified_received: float
    formatted_verified_received: str
    unverified_amount: float
    formatted_unverified_amount: str
    pending_amount: float
    formatted_pending_amount: str
    
    # Status & Due Date
    payment_status: str
    due_date: Optional[date] = None
    formatted_due_date: Optional[str] = None
    is_overdue: bool = False
    days_overdue: int = 0
    
    # Invoice references
    proforma_invoice_no: Optional[str] = None
    tax_invoice_no: Optional[str] = None
    
    # Direct Costs & Profit (as per Sales ledger)
    govt_fees: float = 0.0
    incidental_cost: float = 0.0
    profit_amount: float = 0.0
    
    # Operations link
    operation_status: Optional[str] = None
    
    # Remarks
    latest_remark: Optional[str] = None
    latest_remark_date: Optional[str] = None
    latest_remark_author: Optional[str] = None
    
    # Payment transaction count
    payment_count: int = 0
    unverified_payment_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class PaymentRegisterSummary(BaseModel):
    """Aggregated financial summary across filtered payment register orders."""
    total_orders: int
    total_payable: float
    total_verified_received: float
    total_unverified_amount: float
    total_pending: float
    fully_paid_count: int
    partially_paid_count: int
    pending_count: int
    overdue_count: int
    formatted_total_payable: str
    formatted_total_verified_received: str
    formatted_total_unverified_amount: str
    formatted_total_pending: str


class PaymentRegisterResponse(BaseModel):
    """Paginated Payment Register response."""
    items: List[PaymentRegisterItemRead]
    summary: PaymentRegisterSummary
    total_count: int
    page: int
    limit: int
    total_pages: int


# -----------------------------------------------------------------------------
# Outstanding & Follow-ups
# -----------------------------------------------------------------------------
class AccountsFollowUpCreate(BaseModel):
    """Payload to log a debt follow-up remark on an outstanding order."""
    follow_up_date: date = Field(default_factory=date.today)
    next_follow_up_date: Optional[date] = None
    contact_channel: str = Field(default="PHONE")
    contact_person: Optional[str] = Field(None, max_length=150)
    remark_text: str = Field(..., min_length=2, max_length=1000)


class AccountsFollowUpRead(BaseModel):
    """Read representation of an accounts follow-up record."""
    follow_up_id: uuid.UUID
    sales_order_id: uuid.UUID
    company_id: uuid.UUID
    follow_up_date: date
    formatted_follow_up_date: str
    next_follow_up_date: Optional[date] = None
    formatted_next_follow_up_date: Optional[str] = None
    contact_channel: str
    contact_person: Optional[str] = None
    remark_text: str
    created_by_user_id: uuid.UUID
    created_by_name: Optional[str] = None
    created_at: datetime
    formatted_created_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class OutstandingItemRead(BaseModel):
    """Outstanding debtor record with ageing and operations fulfillment status."""
    sales_order_id: uuid.UUID
    order_number: str
    order_date: date
    formatted_order_date: str
    company_id: uuid.UUID
    company_name: str
    client_id: uuid.UUID
    client_name: str
    client_phone: Optional[str] = None
    client_email: Optional[str] = None
    location: Optional[str] = None
    service_id: uuid.UUID
    service_name: str
    salesperson_name: str
    salesperson_code: Optional[str] = None
    
    total_payable: float
    formatted_total_payable: str
    verified_received: float
    formatted_verified_received: str
    pending_amount: float
    formatted_pending_amount: str
    
    due_date: Optional[date] = None
    formatted_due_date: Optional[str] = None
    days_overdue: int = 0
    ageing_bucket: str  # CURRENT, 1_30_DAYS, 31_60_DAYS, 61_90_DAYS, OVER_90_DAYS, NO_DUE_DATE
    
    operation_status: Optional[str] = None
    is_work_completed: bool = False
    
    latest_follow_up: Optional[AccountsFollowUpRead] = None
    follow_up_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class OutstandingAgeingSummary(BaseModel):
    """Ageing breakdown metrics for outstanding receivables."""
    total_outstanding_amount: float
    formatted_total_outstanding: str
    total_overdue_amount: float
    formatted_total_overdue: str
    total_debtors_count: int
    
    # Ageing buckets
    current_amount: float = 0.0
    current_count: int = 0
    days_1_30_amount: float = 0.0
    days_1_30_count: int = 0
    days_31_60_amount: float = 0.0
    days_31_60_count: int = 0
    days_61_90_amount: float = 0.0
    days_61_90_count: int = 0
    over_90_days_amount: float = 0.0
    over_90_days_count: int = 0
    no_due_date_amount: float = 0.0
    no_due_date_count: int = 0
    
    # Operations completed with pending payment
    completed_work_pending_amount: float = 0.0
    completed_work_pending_count: int = 0


class OutstandingResponse(BaseModel):
    """Outstanding accounts list response."""
    items: List[OutstandingItemRead]
    summary: OutstandingAgeingSummary
    total_count: int
    page: int
    limit: int
    total_pages: int


# -----------------------------------------------------------------------------
# Invoices & Receipts
# -----------------------------------------------------------------------------
class AccountsInvoiceCreate(BaseModel):
    """Payload to create or link an invoice to a Sales Order."""
    sales_order_id: uuid.UUID
    invoice_type: str = Field(..., description="PROFORMA or TAX_INVOICE")
    invoice_number: str = Field(..., min_length=1, max_length=100)
    invoice_date: date = Field(default_factory=date.today)
    due_date: Optional[date] = None
    amount: float = Field(..., gt=0)
    taxable_amount: Optional[float] = None
    cgst_amount: Optional[float] = None
    sgst_amount: Optional[float] = None
    igst_amount: Optional[float] = None
    notes: Optional[str] = Field(None, max_length=1000)


class AccountsInvoiceUpdate(BaseModel):
    """Payload to update invoice metadata."""
    invoice_number: Optional[str] = None
    invoice_date: Optional[date] = None
    due_date: Optional[date] = None
    amount: Optional[float] = Field(None, gt=0)
    taxable_amount: Optional[float] = None
    cgst_amount: Optional[float] = None
    sgst_amount: Optional[float] = None
    igst_amount: Optional[float] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class AccountsInvoiceRead(BaseModel):
    """Read schema for Accounts Invoices."""
    invoice_id: uuid.UUID
    company_id: uuid.UUID
    company_name: Optional[str] = None
    sales_order_id: uuid.UUID
    sales_order_number: Optional[str] = None
    client_id: Optional[uuid.UUID] = None
    client_name: Optional[str] = None
    service_name: Optional[str] = None
    invoice_type: str
    invoice_number: str
    invoice_date: date
    formatted_invoice_date: str
    due_date: Optional[date] = None
    formatted_due_date: Optional[str] = None
    amount: float
    formatted_amount: str
    taxable_amount: Optional[float] = None
    cgst_amount: Optional[float] = None
    sgst_amount: Optional[float] = None
    igst_amount: Optional[float] = None
    status: str
    file_path: Optional[str] = None
    file_name: Optional[str] = None
    notes: Optional[str] = None
    created_by_user_id: uuid.UUID
    created_by_name: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AccountsInvoiceListResponse(BaseModel):
    """List response for invoices."""
    items: List[AccountsInvoiceRead]
    total_count: int
    total_proforma_count: int
    total_tax_invoice_count: int
    total_invoiced_amount: float
    orders_without_invoice_count: int = 0


# -----------------------------------------------------------------------------
# Expenses & Reimbursements
# -----------------------------------------------------------------------------
class AccountsExpenseCreate(BaseModel):
    """Payload to log a direct expense or employee reimbursement claim."""
    sales_order_id: Optional[uuid.UUID] = None
    category: str = Field(..., description="GOVT_FEES, VENDOR_COST, INCIDENTAL_COST, EMPLOYEE_REIMBURSEMENT, OTHER_DIRECT_COST")
    amount: float = Field(..., gt=0, description="Expense amount in INR")
    expense_date: date = Field(default_factory=date.today)
    payee_name: str = Field(..., min_length=2, max_length=200)
    paid_by_type: str = Field(default="COMPANY", description="COMPANY or EMPLOYEE")
    paid_by_user_id: Optional[uuid.UUID] = None
    payment_mode: str = Field(default="BANK_TRANSFER")
    transaction_reference: Optional[str] = Field(None, max_length=100)
    remark: Optional[str] = Field(None, max_length=1000)


class AccountsExpenseApproval(BaseModel):
    """Payload to approve or reject an expense entry."""
    action: str = Field(..., description="APPROVE or REJECT")
    rejection_reason: Optional[str] = Field(None, max_length=500)


class AccountsReimbursementSettle(BaseModel):
    """Payload to record employee reimbursement disbursement settlement."""
    settlement_reference: Optional[str] = Field(None, max_length=100, description="Payment UTR / voucher #")


class AccountsExpenseRead(BaseModel):
    """Read schema for direct expenses and reimbursements."""
    expense_id: uuid.UUID
    company_id: uuid.UUID
    company_name: Optional[str] = None
    sales_order_id: Optional[uuid.UUID] = None
    sales_order_number: Optional[str] = None
    client_name: Optional[str] = None
    expense_number: str
    category: str
    amount: float
    formatted_amount: str
    expense_date: date
    formatted_expense_date: str
    payee_name: str
    paid_by_type: str
    paid_by_user_id: Optional[uuid.UUID] = None
    paid_by_user_name: Optional[str] = None
    payment_mode: str
    transaction_reference: Optional[str] = None
    bill_attachment_path: Optional[str] = None
    bill_attachment_name: Optional[str] = None
    remark: Optional[str] = None
    approval_status: str
    approved_by_user_id: Optional[uuid.UUID] = None
    approved_by_name: Optional[str] = None
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    settlement_status: str
    settled_at: Optional[datetime] = None
    settled_by_user_id: Optional[uuid.UUID] = None
    settled_by_name: Optional[str] = None
    settlement_reference: Optional[str] = None
    created_by_user_id: uuid.UUID
    created_by_name: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AccountsExpenseListResponse(BaseModel):
    """List response for expenses and direct costs."""
    items: List[AccountsExpenseRead]
    total_count: int
    total_approved_expenses: float
    total_pending_approval: float
    total_pending_reimbursements: float
    total_settled_reimbursements: float


# -----------------------------------------------------------------------------
# Accounts Dashboard Metrics & Aggregates
# -----------------------------------------------------------------------------
class PaymentStatusBreakdownItem(BaseModel):
    """Breakdown item for payment status."""
    status: str
    label: str
    count: int
    amount: float
    formatted_amount: str
    percentage: float


class AccountsKpiSummary(BaseModel):
    """Top KPI card metrics for Accounts Dashboard."""
    total_entries: int = 0
    total_amount: float = 0.0
    formatted_total_amount: str = "₹0"
    advance_amount: float = 0.0
    formatted_advance_amount: str = "₹0"
    pending_amount: float = 0.0
    formatted_pending_amount: str = "₹0"
    govt_fees: float = 0.0
    formatted_govt_fees: str = "₹0"
    incidental_cost: float = 0.0
    formatted_incidental_cost: str = "₹0"
    estimated_profit: float = 0.0
    formatted_estimated_profit: str = "₹0"

    # Compatibility fields for any legacy consumer
    confirmed_order_value: float = 0.0
    formatted_confirmed_order_value: str = "₹0"
    confirmed_order_count: int = 0
    verified_collections: float = 0.0
    formatted_verified_collections: str = "₹0"
    verified_collections_count: int = 0
    unverified_collections: float = 0.0
    formatted_unverified_collections: str = "₹0"
    unverified_collections_count: int = 0
    current_outstanding: float = 0.0
    formatted_current_outstanding: str = "₹0"
    outstanding_orders_count: int = 0
    current_overdue: float = 0.0
    formatted_current_overdue: str = "₹0"
    overdue_orders_count: int = 0
    recorded_direct_costs: float = 0.0
    formatted_recorded_direct_costs: str = "₹0"
    estimated_order_margin: float = 0.0
    formatted_estimated_order_margin: str = "₹0"
    margin_percentage: float = 0.0


class CollectionsTrendPoint(BaseModel):
    """Daily or periodic verified collections point."""
    date: str
    label: str
    verified_amount: float
    order_count: int


class AgeingBreakdownItem(BaseModel):
    """Outstanding ageing bucket item for chart and breakdown."""
    bucket: str
    label: str
    amount: float
    count: int
    percentage: float
    color: str


class CompanyFinancialItem(BaseModel):
    """Company-wise financial breakdown."""
    company_id: uuid.UUID
    company_name: str
    order_value: float
    verified_received: float
    outstanding: float
    collection_rate: float


class CategoryExpenseItem(BaseModel):
    """Expense breakdown by category."""
    category: str
    label: str
    amount: float
    percentage: float
    count: int


class RecentTransactionItem(BaseModel):
    """Recent payment collection item for dashboard widget."""
    payment_id: uuid.UUID
    payment_number: str
    sales_order_number: str
    client_name: str
    amount: float
    formatted_amount: str
    payment_date: str
    payment_mode: str
    verification_status: str


class TopOutstandingItem(BaseModel):
    """Top outstanding client debtor item for dashboard widget."""
    sales_order_id: uuid.UUID
    order_number: str
    client_name: str
    service_name: str
    salesperson_name: str
    total_payable: float
    verified_received: float
    pending_amount: float
    formatted_pending_amount: str
    days_overdue: int
    operation_status: Optional[str] = None


# -----------------------------------------------------------------------------
# Accounts Entries (21 Columns)
# -----------------------------------------------------------------------------
class AccountsEntryRead(BaseModel):
    """Accounts Entry representing a shared Sales Order with the exact 21 canonical columns."""
    # 1. S.No
    s_no: int = 1

    # Identifiers
    order_id: uuid.UUID
    order_number: str
    company_id: uuid.UUID
    client_id: uuid.UUID
    service_id: uuid.UUID
    salesperson_user_id: uuid.UUID
    assigned_to_user_id: Optional[uuid.UUID] = None
    application_id: Optional[uuid.UUID] = None

    # 2. Date
    order_date: date
    formatted_date: str

    # 3. Client Name
    client_name: str

    # 4. Location
    location: Optional[str] = None

    # 5. Contact No
    contact_no: Optional[str] = None

    # 6. Source
    lead_source: str

    # 7. Work
    service_name: str
    service_code: Optional[str] = None

    # 8. Converted By
    salesperson_name: str
    salesperson_code: Optional[str] = None

    # 9. Assigned To
    assigned_to_name: Optional[str] = None
    assigned_to_code: Optional[str] = None

    # 10. Work Status
    work_status: str
    operation_status: Optional[str] = None

    # 11. Total Amount
    order_value: float
    formatted_order_value: str

    # 12. Advance Amount
    amount_received: float
    formatted_amount_received: str

    # 13. Pending Amount
    balance_amount: float
    formatted_balance_amount: str

    # 14. Payment Status
    payment_status: str

    # 15. Proforma Inv. No. (Editable by Accounts)
    proforma_invoice_no: Optional[str] = None

    # 16. Tax Inv. No. (Editable by Accounts)
    tax_invoice_no: Optional[str] = None

    # 17. Reimbursement Note (Editable by Accounts)
    reimbursement_note: Optional[str] = None

    # 18. Govt Fees
    govt_fees: float = 0.0
    formatted_govt_fees: str = "₹0"

    # 19. Incidental Cost
    incidental_cost: float = 0.0
    formatted_incidental_cost: str = "₹0"

    # 20. Profits
    profit_amount: float = 0.0
    formatted_profit_amount: str = "₹0"

    # 21. Remarks (Editable by Accounts)
    remarks: Optional[str] = None
    notes: Optional[str] = None

    # Timestamps & status
    gst_invoice_required: bool = True
    confirmation_status: str = "CONFIRMED"
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AccountsEntriesSummary(BaseModel):
    """Aggregated financial summary across filtered Accounts Entries."""
    total_orders: int = 0
    total_amount: float = 0.0
    formatted_total_amount: str = "₹0"
    total_advance: float = 0.0
    formatted_total_advance: str = "₹0"
    total_pending: float = 0.0
    formatted_total_pending: str = "₹0"
    total_govt_fees: float = 0.0
    formatted_total_govt_fees: str = "₹0"
    total_incidental_cost: float = 0.0
    formatted_total_incidental_cost: str = "₹0"
    total_profits: float = 0.0
    formatted_total_profits: str = "₹0"


class AccountsEntriesResponse(BaseModel):
    """Paginated list response for Accounts Entries."""
    items: List[AccountsEntryRead]
    total_count: int
    page: int
    limit: int
    total_pages: int
    summary: AccountsEntriesSummary


class AccountsEntryUpdate(BaseModel):
    """Strict allowlist payload for Accounts users.
    Accounts users may ONLY edit columns 15, 16, 17, and 21 (Remarks).
    Any other fields will be rejected.
    """
    proforma_invoice_no: Optional[str] = Field(None, max_length=100, description="Column 15: Proforma Inv. No.")
    tax_invoice_no: Optional[str] = Field(None, max_length=100, description="Column 16: Tax Inv. No.")
    reimbursement_note: Optional[str] = Field(None, max_length=500, description="Column 17: Reimbursement Note")
    remarks: Optional[str] = Field(None, max_length=1000, description="Column 21: Remarks")
    notes: Optional[str] = Field(None, max_length=1000, description="Alias for Column 21: Remarks")

    model_config = ConfigDict(extra="forbid")


class AccountsDashboardResponse(BaseModel):
    """Payload for the Accounts Dashboard based on authorized Sales records."""
    date_range: Dict[str, str]
    kpis: AccountsKpiSummary
    payment_status_breakdown: List[PaymentStatusBreakdownItem] = Field(default_factory=list)
    recent_entries: List[AccountsEntryRead] = Field(default_factory=list)
    collections_trend: List[CollectionsTrendPoint] = Field(default_factory=list)
    ageing_breakdown: List[AgeingBreakdownItem] = Field(default_factory=list)
    company_breakdown: List[CompanyFinancialItem] = Field(default_factory=list)
    expense_breakdown: List[CategoryExpenseItem] = Field(default_factory=list)
    recent_transactions: List[RecentTransactionItem] = Field(default_factory=list)
    top_outstanding: List[TopOutstandingItem] = Field(default_factory=list)
    filter_options: Optional[AccountsFilterOptions] = None

    model_config = ConfigDict(from_attributes=True)

