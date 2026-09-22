"""Service Master and Service Required Document models."""
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
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
    from app.models.operation_application import OperationApplication
    from app.models.sales_order import SalesOrder


class ServiceMaster(Base):
    """Service Master registry representing legal/compliance service and licence catalog."""

    __tablename__ = "service_master"
    __table_args__ = (
        CheckConstraint(
            "service_code ~ '^[A-Z0-9_]+$'",
            name="chk_service_code_format",
        ),
        CheckConstraint(
            "status IN ('ACTIVE', 'INACTIVE')",
            name="chk_service_status_valid",
        ),
        CheckConstraint(
            "base_price >= 0",
            name="chk_service_base_price_non_negative",
        ),
        CheckConstraint(
            "govt_fee >= 0",
            name="chk_service_govt_fee_non_negative",
        ),
        CheckConstraint(
            "standard_turnaround_days > 0",
            name="chk_service_turnaround_positive",
        ),
        {"comment": "Master registry for compliance services, licences, and statutory filings"},
    )

    service_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="Unique identifier for the service (UUIDv4)",
    )

    service_code: Mapped[str] = mapped_column(
        String(60),
        unique=True,
        nullable=False,
        index=True,
        comment="Uppercase unique system identifier (e.g. TRADE_LICENSE, SHOP_ACT, CLRA)",
    )

    service_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        index=True,
        comment="Display name of the service/licence (e.g. Trade License, Shop Act)",
    )

    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="Service classification: LICENCE, REGISTRATION, INCORPORATION, COMPLIANCE",
    )

    description: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Optional service description and statutory scope",
    )

    base_price: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        server_default=text("0.00"),
        comment="Standard professional fee / base price in INR",
    )

    govt_fee: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        server_default=text("0.00"),
        comment="Estimated government statutory fee in INR",
    )

    standard_turnaround_days: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("15"),
        comment="Standard estimated SLA turnaround time in days",
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
        comment="Timestamp when service record was created (UTC)",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="Timestamp when service record was last updated (UTC)",
    )

    # Relationships
    required_documents: Mapped[List["ServiceRequiredDocument"]] = relationship(
        "ServiceRequiredDocument",
        back_populates="service",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    sales_orders: Mapped[List["SalesOrder"]] = relationship(
        "SalesOrder",
        back_populates="service",
        cascade="save-update, merge",
        passive_deletes=True,
    )

    applications: Mapped[List["OperationApplication"]] = relationship(
        "OperationApplication",
        back_populates="service",
        cascade="save-update, merge",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return (
            f"<ServiceMaster(code='{self.service_code}', "
            f"name='{self.service_name}', "
            f"category='{self.category}', "
            f"status='{self.status}')>"
        )


class ServiceRequiredDocument(Base):
    """Configuration mapping required statutory documents to specific compliance services."""

    __tablename__ = "service_required_document"
    __table_args__ = (
        UniqueConstraint(
            "service_id",
            "document_code",
            name="uq_service_required_doc_service_code",
        ),
        CheckConstraint(
            "display_order >= 0",
            name="chk_service_doc_display_order_non_negative",
        ),
        {"comment": "Standard document checklist configuration required for each service"},
    )

    doc_config_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="Unique identifier for the document requirement configuration (UUIDv4)",
    )

    service_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "service_master.service_id",
            ondelete="CASCADE",
            name="fk_service_required_doc_service_id",
        ),
        nullable=False,
        index=True,
        comment="Foreign key referencing service_master.service_id (ON DELETE CASCADE)",
    )

    document_code: Mapped[str] = mapped_column(
        String(60),
        nullable=False,
        comment="System code for document (e.g. AADHAAR, PAN, RENT_AGREEMENT, PROPERTY_TAX)",
    )

    document_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        comment="Human-readable document name (e.g. Aadhaar Card of Applicant)",
    )

    is_mandatory: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true"),
        default=True,
        comment="Whether this document is mandatory for application submission",
    )

    display_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("0"),
        comment="Display sorting order in document checklists",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Timestamp when document configuration was created (UTC)",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="Timestamp when document configuration was last updated (UTC)",
    )

    # Relationships
    service: Mapped["ServiceMaster"] = relationship(
        "ServiceMaster",
        back_populates="required_documents",
    )

    def __repr__(self) -> str:
        return (
            f"<ServiceRequiredDocument(service_id='{self.service_id}', "
            f"code='{self.document_code}', "
            f"name='{self.document_name}', "
            f"mandatory={self.is_mandatory})>"
        )
