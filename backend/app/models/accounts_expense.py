"""Accounts Expense and Reimbursement ledger model."""
import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.company import Company
    from app.models.sales_order import SalesOrder
    from app.models.user import User


class AccountsExpense(Base):
    """Direct costs, statutory fees, vendor outlays, and employee reimbursements."""

    __tablename__ = "accounts_expense"
    __table_args__ = (
        {"comment": "Direct costs and employee reimbursements ledger for Accounts module"},
    )

    expense_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="Unique identifier for the expense record (UUIDv4)",
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "company_master.company_id",
            ondelete="RESTRICT",
            name="fk_accounts_expense_company_id",
        ),
        nullable=False,
        index=True,
        comment="Foreign key referencing company_master.company_id",
    )

    sales_order_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "sales_order.order_id",
            ondelete="SET NULL",
            name="fk_accounts_expense_sales_order_id",
        ),
        nullable=True,
        index=True,
        comment="Optional foreign key referencing sales_order.order_id for order-linked direct costs",
    )

    expense_number: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
        comment="Human-readable expense voucher number (e.g. EXP-2026-0001)",
    )

    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="Category: GOVT_FEES, VENDOR_COST, INCIDENTAL_COST, EMPLOYEE_REIMBURSEMENT, OTHER_DIRECT_COST",
    )

    amount: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        comment="Expense amount in INR (strictly positive)",
    )

    expense_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
        comment="Date on which expense was incurred or paid",
    )

    payee_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Name of vendor, statutory authority, or employee payee",
    )

    paid_by_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        server_default=text("'COMPANY'"),
        comment="Paid by: COMPANY (direct disbursement) or EMPLOYEE (out-of-pocket claim)",
    )

    paid_by_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "user_master.user_id",
            ondelete="RESTRICT",
            name="fk_accounts_expense_paid_by_user",
        ),
        nullable=True,
        index=True,
        comment="User who paid out of pocket if paid_by_type is EMPLOYEE",
    )

    payment_mode: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        server_default=text("'BANK_TRANSFER'"),
        comment="Payment mode: CASH, UPI, BANK_TRANSFER, CHALLAN, CHEQUE, CREDIT_CARD, OTHER",
    )

    transaction_reference: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Challan # / UTR / Reference identifier",
    )

    bill_attachment_path: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Storage path of uploaded bill, receipt, or challan copy",
    )

    bill_attachment_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Original filename of supporting document",
    )

    remark: Mapped[Optional[str]] = mapped_column(
        String(1000),
        nullable=True,
        comment="Details and purpose of the expenditure",
    )

    approval_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        server_default=text("'PENDING_APPROVAL'"),
        index=True,
        comment="Approval status: PENDING_APPROVAL, APPROVED, REJECTED",
    )

    approved_by_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "user_master.user_id",
            ondelete="RESTRICT",
            name="fk_accounts_expense_approved_by",
        ),
        nullable=True,
        comment="Accounts manager or Director who approved the expense",
    )

    approved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp when expense was approved",
    )

    rejection_reason: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Reason if expense claim was rejected",
    )

    settlement_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        server_default=text("'NOT_APPLICABLE'"),
        index=True,
        comment="Reimbursement settlement status: NOT_APPLICABLE, UNSETTLED, SETTLED",
    )

    settled_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp when employee reimbursement was disbursed/settled",
    )

    settled_by_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "user_master.user_id",
            ondelete="RESTRICT",
            name="fk_accounts_expense_settled_by",
        ),
        nullable=True,
        comment="Accounts user who disbursed the reimbursement settlement",
    )

    settlement_reference: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Payment reference for the reimbursement disbursement",
    )

    created_by_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "user_master.user_id",
            ondelete="RESTRICT",
            name="fk_accounts_expense_created_by",
        ),
        nullable=False,
        index=True,
        comment="User who logged the expense entry",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Record creation timestamp (UTC)",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="Record update timestamp (UTC)",
    )

    # Relationships
    company: Mapped["Company"] = relationship("Company")
    sales_order: Mapped[Optional["SalesOrder"]] = relationship("SalesOrder", back_populates="accounts_expenses")
    paid_by_user: Mapped[Optional["User"]] = relationship("User", foreign_keys=[paid_by_user_id])
    approved_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[approved_by_user_id])
    settled_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[settled_by_user_id])
    created_by: Mapped["User"] = relationship("User", foreign_keys=[created_by_user_id])
