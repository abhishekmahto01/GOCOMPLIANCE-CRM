"""create_task_conversation_read_state_table

Revision ID: c3d4e5f6a7b9
Revises: b2c3d4e5f6a8
Create Date: 2026-10-09 02:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "c3d4e5f6a7b9"
down_revision: Union[str, None] = "b2c3d4e5f6a8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add originating_module column to task_conversation_message if not present
    op.add_column(
        "task_conversation_message",
        sa.Column("originating_module", sa.String(30), nullable=True),
    )
    op.create_index(
        "ix_task_conversation_message_originating_module",
        "task_conversation_message",
        ["originating_module"],
    )

    # 2. Create task_conversation_read_state table
    op.create_table(
        "task_conversation_read_state",
        sa.Column("read_id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "message_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("task_conversation_message.message_id", ondelete="CASCADE", name="fk_task_conv_read_message_id"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("user_master.user_id", ondelete="CASCADE", name="fk_task_conv_read_user_id"),
            nullable=False,
        ),
        sa.Column(
            "sales_order_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("sales_order.order_id", ondelete="CASCADE", name="fk_task_conv_read_sales_order_id"),
            nullable=False,
        ),
        sa.Column("read_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("user_id", "message_id", name="uq_task_conv_read_user_message"),
        comment="Per-user independent read receipt tracking for shared task conversations",
    )

    op.create_index("ix_task_conversation_read_state_message_id", "task_conversation_read_state", ["message_id"])
    op.create_index("ix_task_conversation_read_state_user_id", "task_conversation_read_state", ["user_id"])
    op.create_index("ix_task_conversation_read_state_sales_order_id", "task_conversation_read_state", ["sales_order_id"])
    op.create_index("ix_task_conv_read_user_order", "task_conversation_read_state", ["user_id", "sales_order_id"])
    op.create_index("ix_task_conv_read_user_time", "task_conversation_read_state", ["user_id", "read_at"])


def downgrade() -> None:
    op.drop_index("ix_task_conv_read_user_time", table_name="task_conversation_read_state")
    op.drop_index("ix_task_conv_read_user_order", table_name="task_conversation_read_state")
    op.drop_index("ix_task_conversation_read_state_sales_order_id", table_name="task_conversation_read_state")
    op.drop_index("ix_task_conversation_read_state_user_id", table_name="task_conversation_read_state")
    op.drop_index("ix_task_conversation_read_state_message_id", table_name="task_conversation_read_state")
    op.drop_table("task_conversation_read_state")

    op.drop_index("ix_task_conversation_message_originating_module", table_name="task_conversation_message")
    op.drop_column("task_conversation_message", "originating_module")
