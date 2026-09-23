"""Sales Order model definition."""
import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    CheckConstraint,
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
    from app.models.client import ClientMaster
    from app.models.company import Company
    from app.models.operation_application import OperationApplication
    from app.models.service import ServiceMaster
    from app.models.user import User


class SalesOrder(Base):
    """Sales Order entity representing confirmed and pipeline client orders."""

    __tablename__ = "sales_order"
    __table_args__ = (
        CheckConstraint(
            "order_value >= 0",
            name="chk_sales_order_value_non_negative",
        ),
        CheckConstraint(
            "amount_received >= 0",
            name="chk_sales_order_received_non_negative",
        ),
        CheckConstraint(
            "amount_received <= order_value",
            name="chk_sales_order_advance_le_total",
        ),
        CheckConstraint(
            "balance_amount >= 0",
            name="chk_sales_order_balance_non_negative",
        ),
        CheckConstraint(
            "govt_fees >= 0",
            name="chk_sales_order_govt_fees_non_negative",
        ),
        CheckConstraint(
            "incidental_cost >= 0",
            name="chk_sales_order_incidental_cost_non_negative",
        ),
        CheckConstraint(
            "payment_status IN ('FULLY_PAID', 'PARTIALLY_PAID', 'PENDING', 'OVERDUE')",
            name="chk_sales_order_payment_status_valid",
        ),
        CheckConstraint(
            "confirmation_status IN ('DRAFT', 'CONFIRMED', 'CANCELLED')",
            name="chk_sales_order_confirmation_status_valid",
        ),
        {"comment": "Master registry for client sales orders and collection tracking"},
    )

    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="Unique identifier for the sales order (UUIDv4)",
    )

    order_number: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique formatted order code (e.g. SO-2025-0048)",
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "company_master.company_id",
            ondelete="RESTRICT",
            name="fk_sales_order_company_id",
        ),
        nullable=False,
        index=True,
        comment="Foreign key referencing company_master.company_id",
    )

    client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "client_master.client_id",
            ondelete="RESTRICT",
            name="fk_sales_order_client_id",
        ),
        nullable=False,
        index=True,
        comment="Foreign key referencing client_master.client_id",
    )

    service_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "service_master.service_id",
            ondelete="RESTRICT",
            name="fk_sales_order_service_id",
        ),
        nullable=False,
        index=True,
        comment="Foreign key referencing service_master.service_id",
    )

    salesperson_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "user_master.user_id",
            ondelete="RESTRICT",
            name="fk_sales_order_salesperson_id",
        ),
        nullable=False,
        index=True,
        comment="Foreign key referencing sales employee who closed the order",
    )

    lead_source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        server_default=text("'DIRECT'"),
        index=True,
        comment="Lead acquisition channel: WEBSITE, REFERRAL, DIRECT, OTHERS",
    )

    order_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
        comment="Date when order was placed",
    )

    order_value: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        comment="Total order contract value in INR",
    )

    amount_received: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        server_default=text("0.00"),
        comment="Total amount collected/received in INR",
    )

    balance_amount: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        server_default=text("0.00"),
        comment="Outstanding balance amount in INR (order_value - amount_received)",
    )

    payment_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=text("'PENDING'"),
        index=True,
        comment="Payment collection status: FULLY_PAID, PARTIALLY_PAID, PENDING, OVERDUE",
    )

    confirmation_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=text("'DRAFT'"),
        index=True,
        comment="Order confirmation workflow state: DRAFT, CONFIRMED, CANCELLED",
    )

    confirmed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        comment="Timestamp when order was confirmed and handed over to operations",
    )

    proforma_invoice_no: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        comment="Proforma invoice reference code",
    )

    tax_invoice_no: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        comment="Final tax invoice reference code",
    )

    reimbursement_note: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Reimbursement note or expense instructions",
    )

    govt_fees: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        server_default=text("0.00"),
        comment="Government statutory / filing fees in INR",
    )

    incidental_cost: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        server_default=text("0.00"),
        comment="Incidental / operational expenses in INR",
    )

    profit_amount: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        server_default=text("0.00"),
        comment="Net profit in INR (order_value - govt_fees - incidental_cost)",
    )

    notes: Mapped[Optional[str]] = mapped_column(
        String(1000),
        nullable=True,
        comment="Order notes or instructions from sales team",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Timestamp when order record was created (UTC)",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="Timestamp when order record was last updated (UTC)",
    )

    # Relationships
    company: Mapped["Company"] = relationship(
        "Company",
        back_populates="sales_orders",
    )

    client: Mapped["ClientMaster"] = relationship(
        "ClientMaster",
        back_populates="sales_orders",
    )

    service: Mapped["ServiceMaster"] = relationship(
        "ServiceMaster",
        back_populates="sales_orders",
    )

    salesperson: Mapped["User"] = relationship(
        "User",
        foreign_keys=[salesperson_user_id],
        back_populates="sales_orders",
    )

    application: Mapped[Optional["OperationApplication"]] = relationship(
        "OperationApplication",
        back_populates="sales_order",
        uselist=False,
        cascade="save-update, merge",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return (
            f"<SalesOrder(number='{self.order_number}', "
            f"value={self.order_value}, "
            f"payment='{self.payment_status}', "
            f"confirmed='{self.confirmation_status}')>"
        )
