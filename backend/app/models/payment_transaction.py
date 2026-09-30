"""Payment Transaction model definition for Accounts module."""
import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    Boolean,
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


class PaymentTransaction(Base):
    """Payment transaction ledger record representing collections against Sales Orders."""

    __tablename__ = "payment_transaction"
    __table_args__ = (
        {"comment": "Payment receipts and collections ledger for Accounts module"},
    )

    payment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="Unique identifier for the payment transaction (UUIDv4)",
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "company_master.company_id",
            ondelete="RESTRICT",
            name="fk_payment_transaction_company_id",
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
            name="fk_payment_transaction_sales_order_id",
        ),
        nullable=False,
        index=True,
        comment="Foreign key referencing sales_order.order_id",
    )

    payment_number: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
        comment="Human-readable payment receipt voucher number (e.g. PAY-2026-0001)",
    )

    amount: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        comment="Transaction amount in INR (strictly positive)",
    )

    payment_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
        comment="Actual date on which payment was received",
    )

    payment_mode: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        server_default=text("'BANK_TRANSFER'"),
        comment="Payment mode: CASH, UPI, BANK_TRANSFER, CHEQUE, OTHER, LEGACY_OPENING",
    )

    transaction_reference: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        comment="Bank UTR / Cheque No / UPI reference identifier",
    )

    receiving_account: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Designated company bank account or cash ledger that received the funds",
    )

    proof_attachment_path: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Relative path to stored payment proof / bank receipt document",
    )

    proof_attachment_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Original filename of uploaded proof document",
    )

    remark: Mapped[Optional[str]] = mapped_column(
        String(1000),
        nullable=True,
        comment="Accounts or submitter remarks and notes",
    )

    submitted_by_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "user_master.user_id",
            ondelete="RESTRICT",
            name="fk_payment_transaction_submitted_by",
        ),
        nullable=False,
        index=True,
        comment="User who entered the collection record",
    )

    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Timestamp when collection entry was submitted",
    )

    verification_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        server_default=text("'PENDING_VERIFICATION'"),
        index=True,
        comment="Verification status: VERIFIED, PENDING_VERIFICATION, REJECTED, REVERSED",
    )

    verified_by_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "user_master.user_id",
            ondelete="RESTRICT",
            name="fk_payment_transaction_verified_by",
        ),
        nullable=True,
        comment="Accounts user who verified the payment",
    )

    verified_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp when payment was verified by Accounts",
    )

    reversal_reason: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Mandatory explanation when a verified payment is reversed",
    )

    reversed_by_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "user_master.user_id",
            ondelete="RESTRICT",
            name="fk_payment_transaction_reversed_by",
        ),
        nullable=True,
        comment="Accounts supervisor who authorized the reversal",
    )

    reversed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp when payment reversal was executed",
    )

    is_opening_balance: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
        comment="Flag indicating whether this represents a legacy opening advance",
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
    sales_order: Mapped["SalesOrder"] = relationship("SalesOrder", back_populates="payment_transactions")
    submitted_by: Mapped["User"] = relationship("User", foreign_keys=[submitted_by_user_id])
    verified_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[verified_by_user_id])
    reversed_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[reversed_by_user_id])
