"""Task Conversation Message model for shared cross-departmental CRM communication."""
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.sales_order import SalesOrder
    from app.models.user import User


class TaskConversationMessage(Base):
    """Durable conversation message record linked to root SalesOrder."""

    __tablename__ = "task_conversation_message"
    __table_args__ = (
        CheckConstraint(
            "message_type IN ('COMMENT', 'SYSTEM_EVENT')",
            name="chk_task_conv_msg_type_valid",
        ),
        Index(
            "ix_task_conv_msg_order_created",
            "sales_order_id",
            "created_at",
        ),
        Index(
            "ix_task_conv_msg_order_idempotency",
            "sales_order_id",
            "idempotency_key",
            unique=True,
            postgresql_where=text("idempotency_key IS NOT NULL"),
        ),
        {"comment": "Unified append-only conversation timeline across Sales, Operations, and Accounts"},
    )

    message_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="Unique identifier for the conversation message (UUIDv4)",
    )

    sales_order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "sales_order.order_id",
            ondelete="CASCADE",
            name="fk_task_conv_msg_sales_order_id",
        ),
        nullable=False,
        index=True,
        comment="Foreign key referencing root sales_order.order_id (ON DELETE CASCADE)",
    )

    author_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "user_master.user_id",
            ondelete="SET NULL",
            name="fk_task_conv_msg_author_user_id",
        ),
        nullable=True,
        index=True,
        comment="User who authored the message (null for system events or legacy remarks)",
    )

    message_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        server_default=text("'COMMENT'"),
        default="COMMENT",
        index=True,
        comment="Message classification: COMMENT (human remark) or SYSTEM_EVENT (lifecycle audit)",
    )

    message_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Message body or event description text",
    )

    author_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        server_default=text("'System'"),
        default="System",
        comment="Snapshot of author full name at posting time",
    )

    author_employee_code: Mapped[Optional[str]] = mapped_column(
        String(30),
        nullable=True,
        comment="Snapshot of author employee code (e.g. CG0001) at posting time",
    )

    author_department_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Snapshot of author department name at posting time",
    )

    author_role_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Snapshot of author designation / role at posting time",
    )

    event_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        index=True,
        comment="Event classification for SYSTEM_EVENT: SALES_CREATED, ASSIGNMENT_CHANGE, STATUS_CHANGE, etc.",
    )

    event_metadata: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="JSON-serialized metadata dictionary for system events",
    )

    idempotency_key: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Client request idempotency key preventing duplicate message posts on retry",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
        comment="Server-generated UTC timestamp when message was created",
    )

    # Relationships
    sales_order: Mapped["SalesOrder"] = relationship(
        "SalesOrder",
        back_populates="conversation_messages",
    )

    author: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[author_user_id],
    )

    def __repr__(self) -> str:
        return (
            f"<TaskConversationMessage(id='{self.message_id}', "
            f"order_id='{self.sales_order_id}', "
            f"type='{self.message_type}', "
            f"author='{self.author_name}')>"
        )
