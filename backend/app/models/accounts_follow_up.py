"""Accounts Follow-Up and Debt Collection Remarks model."""
import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
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


class AccountsFollowUp(Base):
    """Follow-up records and collection remarks on outstanding Sales Orders."""

    __tablename__ = "accounts_follow_up"
    __table_args__ = (
        {"comment": "Follow-up history and debtor remarks for Accounts module"},
    )

    follow_up_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="Unique identifier for the follow-up entry (UUIDv4)",
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "company_master.company_id",
            ondelete="RESTRICT",
            name="fk_accounts_follow_up_company_id",
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
            name="fk_accounts_follow_up_sales_order_id",
        ),
        nullable=False,
        index=True,
        comment="Foreign key referencing sales_order.order_id",
    )

    follow_up_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
        comment="Date on which client was contacted for collection",
    )

    next_follow_up_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
        index=True,
        comment="Promised payment date or scheduled next follow-up date",
    )

    contact_channel: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        server_default=text("'PHONE'"),
        comment="Contact channel: PHONE, EMAIL, WHATSAPP, IN_PERSON, OTHER",
    )

    contact_person: Mapped[Optional[str]] = mapped_column(
        String(150),
        nullable=True,
        comment="Name or designation of client representative spoken to",
    )

    remark_text: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
        comment="Summary of communication and client commitment",
    )

    created_by_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "user_master.user_id",
            ondelete="RESTRICT",
            name="fk_accounts_follow_up_created_by",
        ),
        nullable=False,
        index=True,
        comment="User who logged this follow-up",
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
    sales_order: Mapped["SalesOrder"] = relationship("SalesOrder", back_populates="accounts_follow_ups")
    created_by: Mapped["User"] = relationship("User", foreign_keys=[created_by_user_id])
