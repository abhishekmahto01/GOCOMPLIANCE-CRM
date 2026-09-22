"""Client Master model definition."""
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import (
    CheckConstraint,
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
    from app.models.operation_application import OperationApplication
    from app.models.sales_order import SalesOrder
    from app.models.user import User


class ClientMaster(Base):
    """Client Master table representing corporate and individual customers in Gocompliances CRM."""

    __tablename__ = "client_master"
    __table_args__ = (
        CheckConstraint(
            "status IN ('ACTIVE', 'INACTIVE')",
            name="chk_client_status_valid",
        ),
        {"comment": "Master registry for corporate and individual clients in Gocompliances CRM"},
    )

    client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="Unique identifier for the client (UUIDv4)",
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "company_master.company_id",
            ondelete="RESTRICT",
            name="fk_client_company_id",
        ),
        nullable=False,
        index=True,
        comment="Foreign key referencing company_master.company_id (ON DELETE RESTRICT)",
    )

    client_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True,
        comment="Business or individual trade name (e.g. Sharma Enterprises, Gupta Traders)",
    )

    entity_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Entity type: Private Limited, LLP, One Person Company, Partnership, Proprietorship, Individual",
    )

    contact_person: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        comment="Primary contact person name",
    )

    contact_email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Primary contact email address",
    )

    contact_phone: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Primary contact phone / mobile number",
    )

    pan_number: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="Income Tax PAN number of the client entity",
    )

    gstin: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="GST Identification Number (GSTIN) if applicable",
    )

    city: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Operating city",
    )

    state: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Operating state / union territory",
    )

    created_by_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "user_master.user_id",
            ondelete="RESTRICT",
            name="fk_client_created_by_user_id",
        ),
        nullable=False,
        index=True,
        comment="Foreign key referencing user who onboarded this client",
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=text("'ACTIVE'"),
        index=True,
        comment="Operational status: ACTIVE or INACTIVE",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Timestamp when client record was created (UTC)",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="Timestamp when client record was last updated (UTC)",
    )

    # Relationships
    company: Mapped["Company"] = relationship(
        "Company",
        back_populates="clients",
    )

    created_by: Mapped["User"] = relationship(
        "User",
        foreign_keys=[created_by_user_id],
        back_populates="clients_created",
    )

    sales_orders: Mapped[List["SalesOrder"]] = relationship(
        "SalesOrder",
        back_populates="client",
        cascade="save-update, merge",
        passive_deletes=True,
    )

    applications: Mapped[List["OperationApplication"]] = relationship(
        "OperationApplication",
        back_populates="client",
        cascade="save-update, merge",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return (
            f"<ClientMaster(name='{self.client_name}', "
            f"entity='{self.entity_type}', "
            f"email='{self.contact_email}', "
            f"status='{self.status}')>"
        )
