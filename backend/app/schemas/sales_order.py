"""Pydantic schemas for Sales Orders, Entry Form, and Sales Register."""
import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class SalesOrderBase(BaseModel):
    """Base schema for Sales Order."""

    company_id: Optional[uuid.UUID] = None
    client_id: Optional[uuid.UUID] = None
    client_name: Optional[str] = Field(None, max_length=200, description="Client name for direct entry or matching")
    contact_no: Optional[str] = Field(None, max_length=20, description="Client contact / phone number")
    service_id: uuid.UUID = Field(..., description="Service / Work identifier")
    salesperson_user_id: Optional[uuid.UUID] = Field(None, description="Salesperson who converted the order")
    lead_source: str = Field(default="DIRECT", description="WEBSITE, REFERRAL, DIRECT, JUSTDIAL, INDIAMART, OTHERS")
    order_date: date = Field(..., description="Date when order was recorded")
    order_value: Decimal = Field(..., ge=0, description="Total order amount (Total Amount) in INR")
    amount_received: Decimal = Field(default=Decimal("0.00"), ge=0, description="Advance collected in INR")
    govt_fees: Decimal = Field(default=Decimal("0.00"), ge=0, description="Government fees in INR")
    incidental_cost: Decimal = Field(default=Decimal("0.00"), ge=0, description="Incidental / expense costs in INR")
    payment_status: Optional[str] = Field(None, description="FULLY_PAID, PARTIALLY_PAID, PENDING, OVERDUE")
    proforma_invoice_no: Optional[str] = Field(None, max_length=100, description="Proforma Invoice Number")
    tax_invoice_no: Optional[str] = Field(None, max_length=100, description="Tax Invoice Number")
    reimbursement_note: Optional[str] = Field(None, max_length=500, description="Reimbursement Note")
    notes: Optional[str] = Field(None, max_length=1000, description="Order remarks or notes")

    @field_validator("lead_source", mode="before")
    @classmethod
    def normalize_lead_source(cls, v: Optional[str]) -> str:
        if isinstance(v, str):
            v = v.strip().upper()
        return v or "DIRECT"

    @field_validator("payment_status", mode="before")
    @classmethod
    def normalize_payment_status(cls, v: Optional[str]) -> Optional[str]:
        if isinstance(v, str) and v.strip():
            v = v.strip().upper()
            if v not in ("FULLY_PAID", "PARTIALLY_PAID", "PENDING", "OVERDUE"):
                raise ValueError(f"Invalid payment status '{v}'")
            return v
        return None


class SalesOrderCreate(SalesOrderBase):
    """Schema for creating a sales order."""

    auto_confirm: bool = Field(default=False, description="Automatically confirm order and hand over to operations")
    assignee_user_id: Optional[uuid.UUID] = Field(default=None, description="Optional Operations employee ID to assign the work to immediately")

    @model_validator(mode="after")
    def validate_amounts_and_client(self) -> "SalesOrderCreate":
        if self.amount_received > self.order_value:
            raise ValueError("Advance Amount cannot be greater than Total Amount.")
        if not self.client_id and not (self.client_name and self.client_name.strip()):
            raise ValueError("Either Client Name or an existing Client ID must be provided.")
        return self


class SalesOrderUpdate(BaseModel):
    """Schema for updating a sales order."""

    client_name: Optional[str] = Field(None, max_length=200, description="Client Name")
    contact_no: Optional[str] = Field(None, max_length=20, description="Client Contact Number")
    order_value: Optional[Decimal] = Field(None, ge=0, description="Total order amount (Total Amount) in INR")
    amount_received: Optional[Decimal] = Field(None, ge=0, description="Advance / Received amount in INR")
    govt_fees: Optional[Decimal] = Field(None, ge=0, description="Government fees in INR")
    incidental_cost: Optional[Decimal] = Field(None, ge=0, description="Incidental / expense costs in INR")
    payment_status: Optional[str] = Field(None, description="FULLY_PAID, PARTIALLY_PAID, PENDING, OVERDUE")
    lead_source: Optional[str] = Field(None, description="WEBSITE, REFERRAL, DIRECT, JUSTDIAL, INDIAMART, OTHERS")
    order_date: Optional[date] = Field(None, description="Date when order was recorded")
    proforma_invoice_no: Optional[str] = Field(None, max_length=100, description="Proforma Invoice Number")
    tax_invoice_no: Optional[str] = Field(None, max_length=100, description="Tax Invoice Number")
    reimbursement_note: Optional[str] = Field(None, max_length=500, description="Reimbursement Note")
    notes: Optional[str] = Field(None, max_length=1000, description="Order remarks or notes")

    @field_validator("lead_source", mode="before")
    @classmethod
    def normalize_lead_source(cls, v: Optional[str]) -> Optional[str]:
        if isinstance(v, str) and v.strip():
            return v.strip().upper()
        return v

    @field_validator("payment_status", mode="before")
    @classmethod
    def normalize_payment_status(cls, v: Optional[str]) -> Optional[str]:
        if isinstance(v, str) and v.strip():
            v = v.strip().upper()
            if v not in ("FULLY_PAID", "PARTIALLY_PAID", "PENDING", "OVERDUE"):
                raise ValueError(f"Invalid payment status '{v}'")
            return v
        return None

    @model_validator(mode="after")
    def validate_amounts(self) -> "SalesOrderUpdate":
        if (
            self.amount_received is not None
            and self.order_value is not None
            and self.amount_received > self.order_value
        ):
            raise ValueError("Advance Amount cannot be greater than Total Amount.")
        return self


class SalesOrderRead(BaseModel):
    """Lightweight read schema for Sales Order."""

    order_id: uuid.UUID
    order_number: str
    company_id: uuid.UUID
    client_id: uuid.UUID
    service_id: uuid.UUID
    salesperson_user_id: uuid.UUID
    lead_source: str
    order_date: date
    order_value: Decimal
    amount_received: Decimal
    balance_amount: Decimal
    govt_fees: Decimal = Decimal("0.00")
    incidental_cost: Decimal = Decimal("0.00")
    profit_amount: Decimal = Decimal("0.00")
    payment_status: str
    confirmation_status: str
    confirmed_at: Optional[datetime] = None
    proforma_invoice_no: Optional[str] = None
    tax_invoice_no: Optional[str] = None
    reimbursement_note: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SalesOrderDetailRead(SalesOrderRead):
    """Enriched Sales Order read schema exposing all 20 columns in the director-specified sequence."""

    # 1. S.No
    s_no: Optional[int] = None
    # 2. Date
    formatted_date: Optional[str] = None
    # 3. Client Name
    client_name: Optional[str] = None
    # 4. Contact No
    contact_no: Optional[str] = None
    # 5. Source (inherited as lead_source)
    # 6. Work
    service_name: Optional[str] = None
    service_code: Optional[str] = None
    # 7. Converted By
    salesperson_name: Optional[str] = None
    salesperson_code: Optional[str] = None
    # 8. Assigned To
    assigned_to_user_id: Optional[uuid.UUID] = None
    assigned_to_name: Optional[str] = None
    assigned_to_code: Optional[str] = None
    # 9. Work Status
    work_status: Optional[str] = None
    # 10. Total Amount (inherited as order_value)
    # 11. Advance Amount (inherited as amount_received)
    # 12. Pending Amount (inherited as balance_amount)
    # 13. Payment Status (inherited as payment_status)
    # 14. Proforma Invoice No. (inherited as proforma_invoice_no)
    # 15. Tax Invoice No. (inherited as tax_invoice_no)
    # 16. Reimbursement Note (inherited as reimbursement_note)
    # 17. Govt Fees (inherited as govt_fees)
    # 18. Incidental Cost (inherited as incidental_cost)
    # 19. Profits (inherited as profit_amount)
    # 20. Remarks (inherited as notes)
    remarks: Optional[str] = None

    # Operations link
    application_id: Optional[uuid.UUID] = None
    application_number: Optional[str] = None
    operation_status: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class SalesRegisterSummary(BaseModel):
    """Summary metrics across filtered sales orders."""

    total_orders: int = 0
    total_sales: Decimal = Decimal("0.00")
    total_advance: Decimal = Decimal("0.00")
    total_pending: Decimal = Decimal("0.00")
    total_govt_fees: Decimal = Decimal("0.00")
    total_incidental_cost: Decimal = Decimal("0.00")
    total_profits: Decimal = Decimal("0.00")
    formatted_total_sales: str = "₹0"
    formatted_total_advance: str = "₹0"
    formatted_total_pending: str = "₹0"
    formatted_total_govt_fees: str = "₹0"
    formatted_total_incidental_cost: str = "₹0"
    formatted_total_profits: str = "₹0"


class SalesRegisterResponse(BaseModel):
    """Paginated response for the Sales Register table."""

    items: List[SalesOrderDetailRead]
    total_count: int
    page: int
    limit: int
    total_pages: int
    summary: SalesRegisterSummary


class SalesServiceOption(BaseModel):
    """Active service option for sales form selector."""

    service_id: uuid.UUID
    service_code: str
    service_name: str
    category: str
    base_price: Decimal
    govt_fee: Decimal


class SalesEmployeeOption(BaseModel):
    """Active salesperson / employee option for sales form selector."""

    user_id: uuid.UUID
    employee_code: str
    full_name: str
    department_name: Optional[str] = None
    designation_name: Optional[str] = None


class SalesClientOption(BaseModel):
    """Client lookup option for sales form matching."""

    client_id: uuid.UUID
    client_name: str
    contact_phone: str
    contact_email: Optional[str] = None
    contact_person: Optional[str] = None
    entity_type: Optional[str] = None


class SalesFormOptionsResponse(BaseModel):
    """Dropdown options for the Sales Entry form and assignment modals, scoped to user RBAC."""

    services: List[SalesServiceOption]
    salespersons: List[SalesEmployeeOption]
    clients: List[SalesClientOption]
    lead_sources: List[str]
    operations_assignees: List[SalesEmployeeOption] = Field(
        default_factory=list,
        description="Eligible Operations team members for task assignment",
    )
    default_salesperson_id: Optional[uuid.UUID] = None
    can_select_salesperson: bool = True
    company_id: uuid.UUID
    company_name: str


class SalesOrderAssignRequest(BaseModel):
    """Schema for assigning or reassigning an Operations task to an eligible Operations team member."""

    assignee_user_id: uuid.UUID = Field(..., description="Eligible Operations employee ID to assign the work to")
    priority: Optional[str] = Field("MEDIUM", description="Task priority (LOW, MEDIUM, HIGH, URGENT)")
    target_due_date: Optional[date] = Field(None, description="Optional target completion date")
    notes: Optional[str] = Field(None, max_length=1000, description="Assignment / handover notes from Ops Manager")

    @model_validator(mode="before")
    @classmethod
    def populate_aliases(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "assigned_to_user_id" in data and "assignee_user_id" not in data:
                data["assignee_user_id"] = data["assigned_to_user_id"]
            if "target_completion_date" in data and "target_due_date" not in data:
                data["target_due_date"] = data["target_completion_date"]
            if "handover_notes" in data and "notes" not in data:
                data["notes"] = data["handover_notes"]
        return data


class SalesOrderConfirmResponse(BaseModel):
    """Response returned when an order is confirmed and handed over to operations."""

    order_id: uuid.UUID
    order_number: str
    confirmation_status: str
    confirmed_at: datetime
    application_id: uuid.UUID
    application_number: str
    application_status: str
    assigned_to_user_id: Optional[uuid.UUID] = None
    documents_count: int

    model_config = ConfigDict(from_attributes=True)
