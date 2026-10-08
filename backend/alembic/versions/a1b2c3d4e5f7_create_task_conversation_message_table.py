"""create_task_conversation_message_table

Revision ID: a1b2c3d4e5f7
Revises: f6a7b8c9d0e1
Create Date: 2026-10-08 22:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f7"
down_revision: Union[str, None] = "f6a7b8c9d0e1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create task_conversation_message table
    op.create_table(
        "task_conversation_message",
        sa.Column("message_id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "sales_order_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("sales_order.order_id", ondelete="CASCADE", name="fk_task_conv_msg_sales_order_id"),
            nullable=False,
        ),
        sa.Column(
            "author_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("user_master.user_id", ondelete="SET NULL", name="fk_task_conv_msg_author_user_id"),
            nullable=True,
        ),
        sa.Column("message_type", sa.String(30), server_default=sa.text("'COMMENT'"), nullable=False),
        sa.Column("message_text", sa.Text(), nullable=False),
        sa.Column("author_name", sa.String(150), server_default=sa.text("'System'"), nullable=False),
        sa.Column("author_employee_code", sa.String(30), nullable=True),
        sa.Column("author_department_name", sa.String(100), nullable=True),
        sa.Column("author_role_name", sa.String(100), nullable=True),
        sa.Column("event_type", sa.String(50), nullable=True),
        sa.Column("event_metadata", sa.Text(), nullable=True),
        sa.Column("idempotency_key", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("message_type IN ('COMMENT', 'SYSTEM_EVENT')", name="chk_task_conv_msg_type_valid"),
        comment="Unified append-only conversation timeline across Sales, Operations, and Accounts",
    )

    op.create_index("ix_task_conversation_message_sales_order_id", "task_conversation_message", ["sales_order_id"])
    op.create_index("ix_task_conversation_message_author_user_id", "task_conversation_message", ["author_user_id"])
    op.create_index("ix_task_conversation_message_message_type", "task_conversation_message", ["message_type"])
    op.create_index("ix_task_conversation_message_event_type", "task_conversation_message", ["event_type"])
    op.create_index("ix_task_conversation_message_created_at", "task_conversation_message", ["created_at"])
    op.create_index(
        "ix_task_conv_msg_order_created",
        "task_conversation_message",
        ["sales_order_id", "created_at"],
    )
    op.create_index(
        "ix_task_conv_msg_order_idempotency",
        "task_conversation_message",
        ["sales_order_id", "idempotency_key"],
        unique=True,
        postgresql_where=sa.text("idempotency_key IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_index("ix_task_conv_msg_order_idempotency", table_name="task_conversation_message")
    op.drop_index("ix_task_conv_msg_order_created", table_name="task_conversation_message")
    op.drop_index("ix_task_conversation_message_created_at", table_name="task_conversation_message")
    op.drop_index("ix_task_conversation_message_event_type", table_name="task_conversation_message")
    op.drop_index("ix_task_conversation_message_message_type", table_name="task_conversation_message")
    op.drop_index("ix_task_conversation_message_author_user_id", table_name="task_conversation_message")
    op.drop_index("ix_task_conversation_message_sales_order_id", table_name="task_conversation_message")
    op.drop_table("task_conversation_message")
