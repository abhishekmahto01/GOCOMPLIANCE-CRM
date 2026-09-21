"""add_page_permissions_and_audit

Revision ID: 7a8e9f101112
Revises: 50c6c543b4db
Create Date: 2026-09-22 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '7a8e9f101112'
down_revision: Union[str, None] = '50c6c543b4db'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add assign, reassign, export columns to user_module_permission
    op.add_column(
        'user_module_permission',
        sa.Column(
            'can_assign',
            sa.Boolean(),
            server_default=sa.text('false'),
            nullable=False,
            comment='Permission to assign orders/tasks in module (requires can_view=true)',
        ),
    )
    op.add_column(
        'user_module_permission',
        sa.Column(
            'can_reassign',
            sa.Boolean(),
            server_default=sa.text('false'),
            nullable=False,
            comment='Permission to reassign orders/tasks in module (requires can_view=true)',
        ),
    )
    op.add_column(
        'user_module_permission',
        sa.Column(
            'can_export',
            sa.Boolean(),
            server_default=sa.text('false'),
            nullable=False,
            comment='Permission to export reports/records in module (requires can_view=true)',
        ),
    )

    # 2. Update check constraint on user_module_permission
    op.drop_constraint('chk_permission_action_requires_view', 'user_module_permission', type_='check')
    op.create_check_constraint(
        'chk_permission_action_requires_view',
        'user_module_permission',
        "can_view = true OR (can_create = false AND can_edit = false AND can_delete = false AND can_approve = false AND can_assign = false AND can_reassign = false AND can_export = false)",
    )

    # 3. Add is_hod, is_reporting_manager, primary_location to user_master
    op.add_column(
        'user_master',
        sa.Column(
            'is_hod',
            sa.Boolean(),
            server_default=sa.text('false'),
            nullable=False,
            comment='Whether user is designated as Head of Department (HOD)',
        ),
    )
    op.add_column(
        'user_master',
        sa.Column(
            'is_reporting_manager',
            sa.Boolean(),
            server_default=sa.text('false'),
            nullable=False,
            comment='Whether user is designated as a Reporting Manager',
        ),
    )
    op.add_column(
        'user_master',
        sa.Column(
            'primary_location',
            sa.String(length=100),
            nullable=True,
            comment='Primary operating location / branch of the employee',
        ),
    )

    # 4. Create permission_audit_log table
    op.create_table(
        'permission_audit_log',
        sa.Column('audit_id', sa.UUID(), nullable=False, comment='Unique identifier for the audit log entry (UUIDv4)'),
        sa.Column('actor_user_id', sa.UUID(), nullable=True, comment='User ID of the administrator/user performing the action (ON DELETE SET NULL)'),
        sa.Column('target_user_id', sa.UUID(), nullable=False, comment='User ID of the employee whose permissions were modified (ON DELETE CASCADE)'),
        sa.Column('action_type', sa.String(length=50), nullable=False, comment='Audit action type: PERMISSION_UPDATE, PERMISSION_COPY, USER_SETTINGS_UPDATE'),
        sa.Column('before_state', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='State of permissions/settings prior to modification'),
        sa.Column('after_state', postgresql.JSONB(astext_type=sa.Text()), nullable=False, comment='State of permissions/settings after modification'),
        sa.Column('ip_address', sa.String(length=50), nullable=True, comment='IP address of the client that triggered the action'),
        sa.Column('user_agent', sa.String(length=255), nullable=True, comment='User agent header from client request'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the change was executed (UTC)'),
        sa.ForeignKeyConstraint(['actor_user_id'], ['user_master.user_id'], name='fk_permission_audit_actor_user_id', ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['target_user_id'], ['user_master.user_id'], name='fk_permission_audit_target_user_id', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('audit_id'),
        comment='Immutable audit trail for permission changes and user access modifications',
    )
    op.create_index(op.f('ix_permission_audit_log_action_type'), 'permission_audit_log', ['action_type'], unique=False)
    op.create_index(op.f('ix_permission_audit_log_actor_user_id'), 'permission_audit_log', ['actor_user_id'], unique=False)
    op.create_index(op.f('ix_permission_audit_log_created_at'), 'permission_audit_log', ['created_at'], unique=False)
    op.create_index(op.f('ix_permission_audit_log_target_user_id'), 'permission_audit_log', ['target_user_id'], unique=False)
    op.create_index('ix_permission_audit_actor_created', 'permission_audit_log', ['actor_user_id', 'created_at'], unique=False)
    op.create_index('ix_permission_audit_target_created', 'permission_audit_log', ['target_user_id', 'created_at'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_permission_audit_target_created', table_name='permission_audit_log')
    op.drop_index('ix_permission_audit_actor_created', table_name='permission_audit_log')
    op.drop_index(op.f('ix_permission_audit_log_target_user_id'), table_name='permission_audit_log')
    op.drop_index(op.f('ix_permission_audit_log_created_at'), table_name='permission_audit_log')
    op.drop_index(op.f('ix_permission_audit_log_actor_user_id'), table_name='permission_audit_log')
    op.drop_index(op.f('ix_permission_audit_log_action_type'), table_name='permission_audit_log')
    op.drop_table('permission_audit_log')

    op.drop_column('user_master', 'primary_location')
    op.drop_column('user_master', 'is_reporting_manager')
    op.drop_column('user_master', 'is_hod')

    op.drop_constraint('chk_permission_action_requires_view', 'user_module_permission', type_='check')
    op.create_check_constraint(
        'chk_permission_action_requires_view',
        'user_module_permission',
        "can_view = true OR (can_create = false AND can_edit = false AND can_delete = false AND can_approve = false)",
    )

    op.drop_column('user_module_permission', 'can_export')
    op.drop_column('user_module_permission', 'can_reassign')
    op.drop_column('user_module_permission', 'can_assign')
