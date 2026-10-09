"""Task Conversation Read State model for per-user read/unread tracking."""
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.sales_order import SalesOrder
    from app.models.task_conversation import TaskConversationMessage
    from app.models.user import User


class TaskConversationReadState(Base):
    """Per-user read receipt tracking which messages have been rendered/viewed by each user."""

    __tablename__ = "task_conversation_read_state"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "message_id",
            name="uq_task_conv_read_user_message",
        ),
        Index(
            "ix_task_conv_read_user_order",
            "user_id",
            "sales_order_id",
        ),
        Index(
            "ix_task_conv_read_user_time",
            "user_id",
            "read_at",
        ),
        {"comment": "Per-user independent read receipt tracking for shared task conversations"},
    )

    read_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="Unique identifier for the read receipt (UUIDv4)",
    )

    message_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "task_conversation_message.message_id",
            ondelete="CASCADE",
            name="fk_task_conv_read_message_id",
        ),
        nullable=False,
        index=True,
        comment="Foreign key referencing task_conversation_message.message_id (ON DELETE CASCADE)",
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "user_master.user_id",
            ondelete="CASCADE",
            name="fk_task_conv_read_user_id",
        ),
        nullable=False,
        index=True,
        comment="Authenticated user who read the message (derived from session, not client-chosen)",
    )

    sales_order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "sales_order.order_id",
            ondelete="CASCADE",
            name="fk_task_conv_read_sales_order_id",
        ),
        nullable=False,
        index=True,
        comment="Foreign key referencing root sales_order.order_id (ON DELETE CASCADE)",
    )

    read_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Server timestamp when the message was marked read by the user",
    )

    # Relationships
    message: Mapped["TaskConversationMessage"] = relationship(
        "TaskConversationMessage",
        back_populates="read_states",
    )

    user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[user_id],
    )

    sales_order: Mapped["SalesOrder"] = relationship(
        "SalesOrder",
        foreign_keys=[sales_order_id],
    )

    def __repr__(self) -> str:
        return (
            f"<TaskConversationReadState(id='{self.read_id}', "
            f"user_id='{self.user_id}', "
            f"message_id='{self.message_id}')>"
        )
