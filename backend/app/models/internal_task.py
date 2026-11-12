"""Internal (non-sales) task models: R&D research, vendor work and other internal assignments.

These tasks are fully independent of Sales orders. They live in their own tables so that the
existing Sales / Operations / Accounts workflows and data are never affected.
"""
import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Sequence,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.company import Company
    from app.models.user import User


INTERNAL_TASK_TYPES = ("RESEARCH", "VENDOR", "OTHER")
INTERNAL_TASK_STATUSES = ("PENDING", "IN_PROGRESS", "COMPLETED", "CANCELLED")
INTERNAL_TASK_PRIORITIES = ("LOW", "MEDIUM", "HIGH", "URGENT")

# Database sequence used to generate race-free human readable numbers (RND-0001, RND-0002, ...)
internal_task_number_seq = Sequence("internal_task_number_seq", metadata=Base.metadata)


class InternalTask(Base):
    """An internal task assigned to any employee (not linked to a Sales order)."""

    __tablename__ = "internal_task"
    __table_args__ = (
        CheckConstraint(
            "task_type IN ('RESEARCH', 'VENDOR', 'OTHER')",
            name="chk_internal_task_type_valid",
        ),
        CheckConstraint(
            "status IN ('PENDING', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED')",
            name="chk_internal_task_status_valid",
        ),
        CheckConstraint(
            "priority IN ('LOW', 'MEDIUM', 'HIGH', 'URGENT')",
            name="chk_internal_task_priority_valid",
        ),
        Index("ix_internal_task_company_status", "company_id", "status"),
        {"comment": "Internal (non-sales) tasks such as R&D research and vendor work"},
    )

    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    task_number: Mapped[str] = mapped_column(
        String(30), unique=True, nullable=False, comment="Human readable number e.g. RND-0001"
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("company_master.company_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    task_type: Mapped[str] = mapped_column(String(20), nullable=False, default="RESEARCH")
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default="MEDIUM")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="PENDING", index=True)
    assigned_to_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user_master.user_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    created_by_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user_master.user_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    company: Mapped["Company"] = relationship("Company", lazy="joined")
    assigned_to: Mapped[Optional["User"]] = relationship(
        "User", foreign_keys=[assigned_to_user_id], lazy="joined"
    )
    created_by: Mapped[Optional["User"]] = relationship(
        "User", foreign_keys=[created_by_user_id], lazy="joined"
    )
    messages: Mapped[List["InternalTaskMessage"]] = relationship(
        "InternalTaskMessage",
        back_populates="task",
        cascade="all, delete-orphan",
        order_by="InternalTaskMessage.created_at",
    )


class InternalTaskMessage(Base):
    """Chat message / system event on an internal task (same style as the Sales task chat)."""

    __tablename__ = "internal_task_message"
    __table_args__ = (
        CheckConstraint(
            "message_type IN ('COMMENT', 'SYSTEM_EVENT')",
            name="chk_internal_task_msg_type_valid",
        ),
        Index("ix_internal_task_msg_task_created", "task_id", "created_at"),
        {"comment": "Append-only conversation timeline for internal tasks"},
    )

    message_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("internal_task.task_id", ondelete="CASCADE"),
        nullable=False,
    )
    author_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user_master.user_id", ondelete="SET NULL"),
        nullable=True,
    )
    message_type: Mapped[str] = mapped_column(String(20), nullable=False, default="COMMENT")
    message_text: Mapped[str] = mapped_column(Text, nullable=False)
    author_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    author_employee_code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    author_department_name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    task: Mapped["InternalTask"] = relationship("InternalTask", back_populates="messages")
