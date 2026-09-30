"""Accounts Invoice tracking model for Proforma and Tax Invoices."""
import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    UniqueConstraint,
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


class AccountsInvoice(Base):
    """Invoice document and metadata records linked to Sales Orders."""

    __tablename__ = "accounts_invoice"
    __table_args__ = (
        UniqueConstraint(
            "company_id",
            "invoice_type",
            "invoice_number",
            name="uq_accounts_invoice_company_type_number",
        ),
        {"comment": "Invoice metadata and document attachments for Accounts module"},
    )

    invoice_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="Unique identifier for the invoice record (UUIDv4)",
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "company_master.company_id",
            ondelete="RESTRICT",
            name="fk_accounts_invoice_company_id",
        ),
        nullable=False,
        index=True,
        comment="Foreign key referencing company_master.company_id",
    )

    sales_order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "sales_order.order_id",
            ondelete="RESTRICT",
            name="fk_accounts_invoice_sales_order_id",
        ),
        nullable=False,
        index=True,
        comment="Foreign key referencing sales_order.order_id",
    )

    invoice_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
        comment="Invoice type: PROFORMA or TAX_INVOICE",
    )

    invoice_number: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="Official invoice reference code",
    )

    invoice_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
        comment="Date of invoice issuance",
    )

    due_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
        comment="Payment due date indicated on the invoice",
    )

    amount: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        comment="Total invoice amount in INR",
    )

    taxable_amount: Mapped[Optional[float]] = mapped_column(
        Numeric(12, 2),
        nullable=True,
        comment="Taxable base value before GST in INR",
    )

    cgst_amount: Mapped[Optional[float]] = mapped_column(
        Numeric(12, 2),
        nullable=True,
        comment="Central GST component in INR",
    )

    sgst_amount: Mapped[Optional[float]] = mapped_column(
        Numeric(12, 2),
        nullable=True,
        comment="State GST component in INR",
    )

    igst_amount: Mapped[Optional[float]] = mapped_column(
        Numeric(12, 2),
        nullable=True,
        comment="Integrated GST component in INR",
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        server_default=text("'ISSUED'"),
        comment="Invoice status: ISSUED, CANCELLED, DRAFT",
    )

    file_path: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Storage path of uploaded invoice PDF",
    )

    file_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Original filename of invoice PDF",
    )

    notes: Mapped[Optional[str]] = mapped_column(
        String(1000),
        nullable=True,
        comment="Invoice notes or delivery instructions",
    )

    created_by_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "user_master.user_id",
            ondelete="RESTRICT",
            name="fk_accounts_invoice_created_by",
        ),
        nullable=False,
        index=True,
        comment="User who recorded the invoice",
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
    sales_order: Mapped["SalesOrder"] = relationship("SalesOrder", back_populates="accounts_invoices")
    created_by: Mapped["User"] = relationship("User", foreign_keys=[created_by_user_id])
