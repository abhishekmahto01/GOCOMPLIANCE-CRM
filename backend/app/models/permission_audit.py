"""Permission Audit Log model definition."""
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, Optional

from sqlalchemy import DateTime, ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class PermissionAuditLog(Base):
    """Audit log tracking permission updates, permission copies, and user-level authorization changes."""

    __tablename__ = "permission_audit_log"
    __table_args__ = (
        Index("ix_permission_audit_actor_created", "actor_user_id", "created_at"),
        Index("ix_permission_audit_target_created", "target_user_id", "created_at"),
        {"comment": "Immutable audit trail for permission changes and user access modifications"},
    )

    audit_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="Unique identifier for the audit log entry (UUIDv4)",
    )

    actor_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "user_master.user_id",
            ondelete="SET NULL",
            name="fk_permission_audit_actor_user_id",
        ),
        nullable=True,
        index=True,
        comment="User ID of the administrator/user performing the action (ON DELETE SET NULL)",
    )

    target_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "user_master.user_id",
            ondelete="CASCADE",
            name="fk_permission_audit_target_user_id",
        ),
        nullable=False,
        index=True,
        comment="User ID of the employee whose permissions were modified (ON DELETE CASCADE)",
    )

    action_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="Audit action type: PERMISSION_UPDATE, PERMISSION_COPY, USER_SETTINGS_UPDATE",
    )

    before_state: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="State of permissions/settings prior to modification",
    )

    after_state: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        comment="State of permissions/settings after modification",
    )

    ip_address: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="IP address of the client that triggered the action",
    )

    user_agent: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="User agent header from client request",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
        comment="Timestamp when the change was executed (UTC)",
    )

    # Relationships
    actor: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[actor_user_id],
        back_populates="audit_actions_performed",
    )

    target_user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[target_user_id],
        back_populates="audit_logs_received",
    )

    def __repr__(self) -> str:
        return (
            f"<PermissionAuditLog(id='{self.audit_id}', "
            f"actor='{self.actor_user_id}', "
            f"target='{self.target_user_id}', "
            f"action='{self.action_type}', "
            f"created_at='{self.created_at}')>"
        )
