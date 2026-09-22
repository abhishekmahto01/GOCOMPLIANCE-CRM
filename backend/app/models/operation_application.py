"""Operation Application, Documents, Assignment History, and Activity Log models."""
import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
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
    from app.models.client import ClientMaster
    from app.models.company import Company
    from app.models.sales_order import SalesOrder
    from app.models.service import ServiceMaster
    from app.models.user import User


class OperationApplication(Base):
    """Operations compliance task/application created from confirmed sales orders."""

    __tablename__ = "operation_application"
    __table_args__ = (
        CheckConstraint(
            "priority IN ('LOW', 'MEDIUM', 'HIGH', 'URGENT')",
            name="chk_op_application_priority_valid",
        ),
        CheckConstraint(
            "application_status IN ('UNASSIGNED', 'ASSIGNED', 'IN_PROGRESS', 'PENDING_DOCUMENTS', 'READY_FOR_SUBMISSION', 'SUBMITTED', 'AUTHORITY_QUERY', 'APPROVED', 'CANCELLED')",
            name="chk_op_application_status_valid",
        ),
        {"comment": "Operations workflow application tracking statutory filings and task fulfillment"},
    )

    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="Unique identifier for the operation application (UUIDv4)",
    )

    application_number: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique formatted application code (e.g. AP-2025-0084)",
    )

    sales_order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "sales_order.order_id",
            ondelete="RESTRICT",
            name="fk_op_app_sales_order_id",
        ),
        unique=True,
        nullable=False,
        index=True,
        comment="1-to-1 foreign key to originating sales order (strictly idempotent)",
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "company_master.company_id",
            ondelete="RESTRICT",
            name="fk_op_app_company_id",
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
            name="fk_op_app_client_id",
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
            name="fk_op_app_service_id",
        ),
        nullable=False,
        index=True,
        comment="Foreign key referencing service_master.service_id",
    )

    assigned_to_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "user_master.user_id",
            ondelete="SET NULL",
            name="fk_op_app_assigned_to_id",
        ),
        nullable=True,
        index=True,
        comment="Operations employee currently assigned to this task (nullable when UNASSIGNED)",
    )

    assigned_by_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "user_master.user_id",
            ondelete="SET NULL",
            name="fk_op_app_assigned_by_id",
        ),
        nullable=True,
        comment="Operations Manager / Admin who assigned or reassigned this task",
    )

    assigned_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        comment="Timestamp when task was assigned to current employee",
    )

    priority: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        server_default=text("'MEDIUM'"),
        index=True,
        comment="Task priority: LOW, MEDIUM, HIGH, URGENT",
    )

    application_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        server_default=text("'UNASSIGNED'"),
        index=True,
        comment="Lifecycle status: UNASSIGNED, ASSIGNED, IN_PROGRESS, PENDING_DOCUMENTS, READY_FOR_SUBMISSION, SUBMITTED, AUTHORITY_QUERY, APPROVED, CANCELLED",
    )

    target_due_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
        index=True,
        comment="Target completion due date for statutory filing",
    )

    completion_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
        comment="Actual completion / approval date",
    )

    assignment_notes: Mapped[Optional[str]] = mapped_column(
        String(1000),
        nullable=True,
        comment="Internal handover or assignment instructions",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Timestamp when application record was created (UTC)",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="Timestamp when application record was last updated (UTC)",
    )

    # Relationships
    sales_order: Mapped["SalesOrder"] = relationship(
        "SalesOrder",
        back_populates="application",
    )

    company: Mapped["Company"] = relationship(
        "Company",
        back_populates="applications",
    )

    client: Mapped["ClientMaster"] = relationship(
        "ClientMaster",
        back_populates="applications",
    )

    service: Mapped["ServiceMaster"] = relationship(
        "ServiceMaster",
        back_populates="applications",
    )

    assigned_to: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[assigned_to_user_id],
        back_populates="assigned_applications",
    )

    assigned_by: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[assigned_by_user_id],
        back_populates="applications_assigned_by",
    )

    documents: Mapped[List["ApplicationDocument"]] = relationship(
        "ApplicationDocument",
        back_populates="application",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    assignment_history: Mapped[List["ApplicationAssignmentHistory"]] = relationship(
        "ApplicationAssignmentHistory",
        back_populates="application",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="ApplicationAssignmentHistory.assigned_at.desc()",
    )

    activity_logs: Mapped[List["ApplicationActivityLog"]] = relationship(
        "ApplicationActivityLog",
        back_populates="application",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="ApplicationActivityLog.created_at.desc()",
    )

    def __repr__(self) -> str:
        return (
            f"<OperationApplication(number='{self.application_number}', "
            f"status='{self.application_status}', "
            f"priority='{self.priority}', "
            f"assignee_id='{self.assigned_to_user_id}')>"
        )


class ApplicationDocument(Base):
    """Document checklist item tracking status for a specific compliance application."""

    __tablename__ = "application_document"
    __table_args__ = (
        CheckConstraint(
            "status IN ('PENDING', 'RECEIVED', 'VERIFIED', 'REJECTED', 'NOT_APPLICABLE')",
            name="chk_app_doc_status_valid",
        ),
        {"comment": "Document requirements and verification statuses for an active application"},
    )

    app_doc_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="Unique identifier for the application document requirement (UUIDv4)",
    )

    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "operation_application.application_id",
            ondelete="CASCADE",
            name="fk_app_doc_application_id",
        ),
        nullable=False,
        index=True,
        comment="Foreign key referencing operation_application.application_id (ON DELETE CASCADE)",
    )

    document_code: Mapped[str] = mapped_column(
        String(60),
        nullable=False,
        comment="Document identifier code (e.g. AADHAAR, PAN, RENT_AGREEMENT)",
    )

    document_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        comment="Human-readable document name",
    )

    is_mandatory: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true"),
        default=True,
        comment="Whether this document is required for filing",
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=text("'PENDING'"),
        index=True,
        comment="Document status: PENDING, RECEIVED, VERIFIED, REJECTED, NOT_APPLICABLE",
    )

    rejection_reason: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Reason if document was rejected / defective",
    )

    verified_by_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "user_master.user_id",
            ondelete="SET NULL",
            name="fk_app_doc_verified_by_id",
        ),
        nullable=True,
        comment="Employee who verified/approved the document",
    )

    verified_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp when document was verified",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Timestamp when document item was created (UTC)",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="Timestamp when document item was last updated (UTC)",
    )

    # Relationships
    application: Mapped["OperationApplication"] = relationship(
        "OperationApplication",
        back_populates="documents",
    )

    verified_by: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[verified_by_user_id],
    )

    def __repr__(self) -> str:
        return (
            f"<ApplicationDocument(app_id='{self.application_id}', "
            f"code='{self.document_code}', "
            f"status='{self.status}')>"
        )


class ApplicationAssignmentHistory(Base):
    """Audit log tracking task assignment and reassignment events."""

    __tablename__ = "application_assignment_history"
    __table_args__ = (
        {"comment": "Audit trail for application assignment and reassignment events"},
    )

    history_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="Unique identifier for the assignment history record (UUIDv4)",
    )

    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "operation_application.application_id",
            ondelete="CASCADE",
            name="fk_app_assign_hist_app_id",
        ),
        nullable=False,
        index=True,
        comment="Foreign key referencing operation_application.application_id (ON DELETE CASCADE)",
    )

    assigned_by_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "user_master.user_id",
            ondelete="RESTRICT",
            name="fk_app_assign_hist_assigned_by_id",
        ),
        nullable=False,
        comment="Manager/Admin who performed the assignment",
    )

    previous_assignee_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "user_master.user_id",
            ondelete="SET NULL",
            name="fk_app_assign_hist_prev_assignee_id",
        ),
        nullable=True,
        comment="Employee previously assigned (null if initial assignment)",
    )

    new_assignee_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "user_master.user_id",
            ondelete="SET NULL",
            name="fk_app_assign_hist_new_assignee_id",
        ),
        nullable=True,
        comment="Employee newly assigned (null if unassigned)",
    )

    reason: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Reason or notes provided for assignment/reassignment",
    )

    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Timestamp when assignment was executed (UTC)",
    )

    # Relationships
    application: Mapped["OperationApplication"] = relationship(
        "OperationApplication",
        back_populates="assignment_history",
    )

    assigned_by: Mapped["User"] = relationship(
        "User",
        foreign_keys=[assigned_by_user_id],
    )

    previous_assignee: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[previous_assignee_user_id],
    )

    new_assignee: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[new_assignee_user_id],
    )


class ApplicationActivityLog(Base):
    """Lifecycle activity log and timeline of changes for an application."""

    __tablename__ = "application_activity_log"
    __table_args__ = (
        {"comment": "Timeline and audit log of status changes and operational activities"},
    )

    activity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="Unique identifier for the activity log entry (UUIDv4)",
    )

    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "operation_application.application_id",
            ondelete="CASCADE",
            name="fk_app_activity_application_id",
        ),
        nullable=False,
        index=True,
        comment="Foreign key referencing operation_application.application_id (ON DELETE CASCADE)",
    )

    actor_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "user_master.user_id",
            ondelete="RESTRICT",
            name="fk_app_activity_actor_id",
        ),
        nullable=False,
        comment="User who triggered this operational action",
    )

    action_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="Action classification: STATUS_CHANGE, DOCUMENT_STATUS_CHANGE, PRIORITY_CHANGE, DUE_DATE_CHANGE, NOTE_ADDED, ASSIGNMENT_CHANGE",
    )

    old_value: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Previous attribute value prior to modification",
    )

    new_value: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="New attribute value after modification",
    )

    comment: Mapped[Optional[str]] = mapped_column(
        String(1000),
        nullable=True,
        comment="Descriptive note or reason accompanying the activity",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
        comment="Timestamp when activity occurred (UTC)",
    )

    # Relationships
    application: Mapped["OperationApplication"] = relationship(
        "OperationApplication",
        back_populates="activity_logs",
    )

    actor: Mapped["User"] = relationship(
        "User",
        foreign_keys=[actor_user_id],
    )
