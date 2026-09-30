"""Accounts Audit Log model for financial compliance and data safety."""
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    DateTime,
    ForeignKey,
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


class AccountsAuditLog(Base):
    """Immutable audit trail for financial actions, verifications, reversals, and adjustments."""

    __tablename__ = "accounts_audit_log"
    __table_args__ = (
        {"comment": "Immutable financial audit logs for Accounts module"},
    )

    audit_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="Unique identifier for the audit entry (UUIDv4)",
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "company_master.company_id",
            ondelete="RESTRICT",
            name="fk_accounts_audit_log_company_id",
        ),
        nullable=False,
        index=True,
        comment="Foreign key referencing company_master.company_id",
    )

    entity_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="Entity type: PAYMENT, EXPENSE, INVOICE, FOLLOW_UP, COMMERCIAL_CHANGE",
    )

    entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="UUID of the modified financial entity",
    )

    action: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="Action performed: CREATE, VERIFY, REJECT, REVERSE, APPROVE, SETTLE, UPDATE_COMMERCIAL, DELETE",
    )

    actor_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "user_master.user_id",
            ondelete="RESTRICT",
            name="fk_accounts_audit_log_actor_user_id",
        ),
        nullable=False,
        index=True,
        comment="User who performed the financial action",
    )

    old_values: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Serialized JSON of previous state before mutation",
    )

    new_values: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Serialized JSON of new state after mutation",
    )

    reason: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Business justification or reversal explanation",
    )

    ip_address: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Client IP address for security auditing",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
        comment="Audit record timestamp (UTC)",
    )

    # Relationships
    company: Mapped["Company"] = relationship("Company")
    actor: Mapped["User"] = relationship("User", foreign_keys=[actor_user_id])
