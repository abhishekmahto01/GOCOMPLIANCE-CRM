"""Impersonation Session and Audit models."""
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class ImpersonationSession(Base):
    """Tracks active and historical administrative impersonation sessions."""

    __tablename__ = "impersonation_sessions"
    __table_args__ = (
        Index("ix_impersonation_sessions_admin_target", "actor_admin_id", "target_user_id"),
        Index("ix_impersonation_sessions_active_expiry", "is_active", "expires_at"),
        {"comment": "Registry of Super Admin employee impersonation sessions"},
    )

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="Unique identifier for the impersonation session (UUIDv4)",
    )

    actor_admin_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "user_master.user_id",
            ondelete="CASCADE",
            name="fk_impersonation_actor_admin_id",
        ),
        nullable=False,
        index=True,
        comment="User ID of the Super Admin who initiated impersonation",
    )

    target_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "user_master.user_id",
            ondelete="CASCADE",
            name="fk_impersonation_target_user_id",
        ),
        nullable=False,
        index=True,
        comment="User ID of the employee being impersonated",
    )

    impersonation_token_jti: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
        comment="JWT ID of the impersonation refresh token",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        comment="Whether this impersonation session is currently active and valid",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
        comment="Timestamp when impersonation session was created (UTC)",
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="Expiration timestamp (max 30 minutes from creation)",
    )

    ended_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp when impersonation session ended (UTC)",
    )

    ended_reason: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Reason session ended: RETURN_TO_ADMIN, LOGOUT, EXPIRED, REVOKED, FEATURE_DISABLED",
    )

    created_ip: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="IP address from which impersonation was initiated",
    )

    user_agent: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="User agent header from client request",
    )

    # Relationships
    actor_admin: Mapped["User"] = relationship(
        "User",
        foreign_keys=[actor_admin_id],
    )

    target_user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[target_user_id],
    )


class ImpersonationAuditLog(Base):
    """Immutable audit trail for all impersonation events."""

    __tablename__ = "impersonation_audit_logs"
    __table_args__ = (
        Index("ix_imp_audit_actor_created", "actor_admin_id", "created_at"),
        Index("ix_imp_audit_target_created", "target_user_id", "created_at"),
        {"comment": "Immutable audit log of impersonation starts, exits, and actions"},
    )

    audit_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="Unique identifier for the audit record (UUIDv4)",
    )

    session_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "impersonation_sessions.session_id",
            ondelete="SET NULL",
            name="fk_imp_audit_session_id",
        ),
        nullable=True,
        index=True,
        comment="Associated impersonation session ID",
    )

    actor_admin_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "user_master.user_id",
            ondelete="SET NULL",
            name="fk_imp_audit_actor_admin_id",
        ),
        nullable=True,
        index=True,
        comment="Super Admin user ID",
    )

    target_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "user_master.user_id",
            ondelete="CASCADE",
            name="fk_imp_audit_target_user_id",
        ),
        nullable=False,
        index=True,
        comment="Target employee user ID",
    )

    action: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="Action performed: IMPERSONATION_START, IMPERSONATION_END, IMPERSONATION_ACTION",
    )

    details: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Contextual metadata (e.g. employee code, reason, affected entity)",
    )

    ip_address: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )

    user_agent: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
        comment="Timestamp of the audit entry (UTC)",
    )
