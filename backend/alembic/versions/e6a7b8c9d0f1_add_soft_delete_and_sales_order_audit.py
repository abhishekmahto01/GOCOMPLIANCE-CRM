"""add_soft_delete_and_sales_order_audit

Revision ID: e6a7b8c9d0f1
Revises: d4e5f6a7b8c0
Create Date: 2026-10-19 12:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'e6a7b8c9d0f1'
down_revision: Union[str, None] = 'd4e5f6a7b8c0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add soft-delete columns to sales_order
    op.add_column(
        'sales_order',
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True, comment='Timestamp when sales order was soft-deleted (UTC)'),
    )
    op.add_column(
        'sales_order',
        sa.Column('deleted_by', postgresql.UUID(as_uuid=True), nullable=True, comment='Foreign key referencing user who soft-deleted the order'),
    )
    op.add_column(
        'sales_order',
        sa.Column('deletion_reason', sa.String(length=1000), nullable=True, comment='Required or provided deletion justification reason'),
    )
    op.create_index(op.f('ix_sales_order_deleted_at'), 'sales_order', ['deleted_at'], unique=False)
    op.create_index(op.f('ix_sales_order_deleted_by'), 'sales_order', ['deleted_by'], unique=False)
    op.create_foreign_key(
        'fk_sales_order_deleted_by',
        'sales_order',
        'user_master',
        ['deleted_by'],
        ['user_id'],
        ondelete='SET NULL',
    )

    # 2. Add soft-delete columns to operation_application
    op.add_column(
        'operation_application',
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True, comment='Timestamp when linked sales order was soft-deleted (UTC)'),
    )
    op.add_column(
        'operation_application',
        sa.Column('deleted_by', postgresql.UUID(as_uuid=True), nullable=True, comment='Foreign key referencing user who soft-deleted the linked sales order'),
    )
    op.add_column(
        'operation_application',
        sa.Column('deletion_reason', sa.String(length=1000), nullable=True, comment='Required or provided deletion justification reason'),
    )
    op.create_index(op.f('ix_op_app_deleted_at'), 'operation_application', ['deleted_at'], unique=False)
    op.create_index(op.f('ix_op_app_deleted_by'), 'operation_application', ['deleted_by'], unique=False)
    op.create_foreign_key(
        'fk_op_app_deleted_by',
        'operation_application',
        'user_master',
        ['deleted_by'],
        ['user_id'],
        ondelete='SET NULL',
    )

    # 3. Create sales_order_audit_log table
    op.create_table(
        'sales_order_audit_log',
        sa.Column('audit_id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            'sales_order_id',
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey('sales_order.order_id', ondelete='CASCADE', name='fk_sales_order_audit_order_id'),
            nullable=False,
            index=True,
        ),
        sa.Column(
            'actor_user_id',
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey('user_master.user_id', ondelete='RESTRICT', name='fk_sales_order_audit_actor_id'),
            nullable=False,
            index=True,
        ),
        sa.Column('action_type', sa.String(length=50), nullable=False, index=True),
        sa.Column('linked_task_id', postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column('previous_status', sa.String(length=100), nullable=True),
        sa.Column('deletion_reason', sa.String(length=1000), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False, index=True),
    )


def downgrade() -> None:
    # 1. Drop sales_order_audit_log table
    op.drop_table('sales_order_audit_log')

    # 2. Drop columns and foreign keys from operation_application
    op.drop_constraint('fk_op_app_deleted_by', 'operation_application', type_='foreignkey')
    op.drop_index(op.f('ix_op_app_deleted_by'), table_name='operation_application')
    op.drop_index(op.f('ix_op_app_deleted_at'), table_name='operation_application')
    op.drop_column('operation_application', 'deletion_reason')
    op.drop_column('operation_application', 'deleted_by')
    op.drop_column('operation_application', 'deleted_at')

    # 3. Drop columns and foreign keys from sales_order
    op.drop_constraint('fk_sales_order_deleted_by', 'sales_order', type_='foreignkey')
    op.drop_index(op.f('ix_sales_order_deleted_by'), table_name='sales_order')
    op.drop_index(op.f('ix_sales_order_deleted_at'), table_name='sales_order')
    op.drop_column('sales_order', 'deletion_reason')
    op.drop_column('sales_order', 'deleted_by')
    op.drop_column('sales_order', 'deleted_at')
