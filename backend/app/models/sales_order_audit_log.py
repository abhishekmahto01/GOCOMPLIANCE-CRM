"""Sales Order Audit Log model for tracking sales entry deletion and lifecycle overrides."""
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    DateTime,
    ForeignKey,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.sales_order import SalesOrder
    from app.models.user import User


class SalesOrderAuditLog(Base):
    """Immutable audit trail for sales order deletions, cancellations, and Super Admin overrides."""

    __tablename__ = "sales_order_audit_log"
    __table_args__ = (
        {"comment": "Immutable audit log tracking sales order soft-deletions and lifecycle overrides"},
    )

    audit_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="Unique identifier for the audit record (UUIDv4)",
    )

    sales_order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "sales_order.order_id",
            ondelete="CASCADE",
            name="fk_sales_order_audit_order_id",
        ),
        nullable=False,
        index=True,
        comment="Foreign key referencing sales_order.order_id",
    )

    actor_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "user_master.user_id",
            ondelete="RESTRICT",
            name="fk_sales_order_audit_actor_id",
        ),
        nullable=False,
        index=True,
        comment="Foreign key referencing user_master.user_id who performed the deletion",
    )

    action_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="Audit classification: SOFT_DELETE, SUPER_ADMIN_OVERRIDE_DELETE",
    )

    linked_task_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        index=True,
        comment="Linked OperationApplication application_id at time of deletion",
    )

    previous_status: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Previous status string (e.g. order:CONFIRMED|task:APPROVED)",
    )

    deletion_reason: Mapped[Optional[str]] = mapped_column(
        String(1000),
        nullable=True,
        comment="Required or provided deletion justification reason",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
        comment="Timestamp when audit log was recorded (UTC)",
    )

    # Relationships
    sales_order: Mapped["SalesOrder"] = relationship(
        "SalesOrder",
        foreign_keys=[sales_order_id],
        back_populates="audit_logs",
    )

    actor: Mapped["User"] = relationship(
        "User",
        foreign_keys=[actor_user_id],
    )

    def __repr__(self) -> str:
        return (
            f"<SalesOrderAuditLog(id='{self.audit_id}', "
            f"order_id='{self.sales_order_id}', "
            f"action='{self.action_type}', "
            f"actor='{self.actor_user_id}')>"
        )
