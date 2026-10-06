"""add_impersonation_tables

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
Create Date: 2026-10-07 02:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "f6a7b8c9d0e1"
down_revision: Union[str, None] = "e5f6a7b8c9d0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create impersonation_sessions table
    op.create_table(
        "impersonation_sessions",
        sa.Column("session_id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("actor_admin_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("user_master.user_id", ondelete="CASCADE", name="fk_impersonation_actor_admin_id"), nullable=False),
        sa.Column("target_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("user_master.user_id", ondelete="CASCADE", name="fk_impersonation_target_user_id"), nullable=False),
        sa.Column("impersonation_token_jti", sa.String(64), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ended_reason", sa.String(50), nullable=True),
        sa.Column("created_ip", sa.String(50), nullable=True),
        sa.Column("user_agent", sa.String(255), nullable=True),
        comment="Registry of Super Admin employee impersonation sessions",
    )
    op.create_index("ix_impersonation_sessions_actor_admin_id", "impersonation_sessions", ["actor_admin_id"])
    op.create_index("ix_impersonation_sessions_target_user_id", "impersonation_sessions", ["target_user_id"])
    op.create_index("ix_impersonation_sessions_impersonation_token_jti", "impersonation_sessions", ["impersonation_token_jti"])
    op.create_index("ix_impersonation_sessions_is_active", "impersonation_sessions", ["is_active"])
    op.create_index("ix_impersonation_sessions_created_at", "impersonation_sessions", ["created_at"])
    op.create_index("ix_impersonation_sessions_expires_at", "impersonation_sessions", ["expires_at"])
    op.create_index("ix_impersonation_sessions_admin_target", "impersonation_sessions", ["actor_admin_id", "target_user_id"])
    op.create_index("ix_impersonation_sessions_active_expiry", "impersonation_sessions", ["is_active", "expires_at"])

    # 2. Create impersonation_audit_logs table
    op.create_table(
        "impersonation_audit_logs",
        sa.Column("audit_id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("impersonation_sessions.session_id", ondelete="SET NULL", name="fk_imp_audit_session_id"), nullable=True),
        sa.Column("actor_admin_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("user_master.user_id", ondelete="SET NULL", name="fk_imp_audit_actor_admin_id"), nullable=True),
        sa.Column("target_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("user_master.user_id", ondelete="CASCADE", name="fk_imp_audit_target_user_id"), nullable=False),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column("details", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("ip_address", sa.String(50), nullable=True),
        sa.Column("user_agent", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        comment="Immutable audit log of impersonation starts, exits, and actions",
    )
    op.create_index("ix_impersonation_audit_logs_session_id", "impersonation_audit_logs", ["session_id"])
    op.create_index("ix_impersonation_audit_logs_actor_admin_id", "impersonation_audit_logs", ["actor_admin_id"])
    op.create_index("ix_impersonation_audit_logs_target_user_id", "impersonation_audit_logs", ["target_user_id"])
    op.create_index("ix_impersonation_audit_logs_action", "impersonation_audit_logs", ["action"])
    op.create_index("ix_impersonation_audit_logs_created_at", "impersonation_audit_logs", ["created_at"])
    op.create_index("ix_imp_audit_actor_created", "impersonation_audit_logs", ["actor_admin_id", "created_at"])
    op.create_index("ix_imp_audit_target_created", "impersonation_audit_logs", ["target_user_id", "created_at"])


def downgrade() -> None:
    op.drop_table("impersonation_audit_logs")
    op.drop_table("impersonation_sessions")
