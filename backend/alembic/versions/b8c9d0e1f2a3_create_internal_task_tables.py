"""create_internal_task_tables

Adds the R&D / Internal Tasks feature (tasks not linked to Sales orders) with its own chat.
Purely additive: creates two new tables and one sequence. No existing table is modified.

Revision ID: b8c9d0e1f2a3
Revises: a2b3c4d5e6f7
Create Date: 2026-11-13 12:00:00.000000

"""
import uuid
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'b8c9d0e1f2a3'
down_revision: Union[str, None] = 'a2b3c4d5e6f7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

MODULE_CODE = 'OPERATION_INTERNAL_TASKS'


def upgrade() -> None:
    op.execute(sa.schema.CreateSequence(sa.Sequence('internal_task_number_seq')))

    op.create_table(
        'internal_task',
        sa.Column('task_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('task_number', sa.String(length=30), nullable=False, comment='Human readable number e.g. RND-0001'),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('task_type', sa.String(length=20), nullable=False),
        sa.Column('priority', sa.String(length=20), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('assigned_to_user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_by_user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('due_date', sa.Date(), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint("task_type IN ('RESEARCH', 'VENDOR', 'OTHER')", name='chk_internal_task_type_valid'),
        sa.CheckConstraint("status IN ('PENDING', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED')", name='chk_internal_task_status_valid'),
        sa.CheckConstraint("priority IN ('LOW', 'MEDIUM', 'HIGH', 'URGENT')", name='chk_internal_task_priority_valid'),
        sa.ForeignKeyConstraint(['company_id'], ['company_master.company_id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['assigned_to_user_id'], ['user_master.user_id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['user_master.user_id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('task_id'),
        sa.UniqueConstraint('task_number'),
        comment='Internal (non-sales) tasks such as R&D research and vendor work',
    )
    op.create_index('ix_internal_task_company_id', 'internal_task', ['company_id'])
    op.create_index('ix_internal_task_status', 'internal_task', ['status'])
    op.create_index('ix_internal_task_assigned_to_user_id', 'internal_task', ['assigned_to_user_id'])
    op.create_index('ix_internal_task_created_by_user_id', 'internal_task', ['created_by_user_id'])
    op.create_index('ix_internal_task_company_status', 'internal_task', ['company_id', 'status'])

    op.create_table(
        'internal_task_message',
        sa.Column('message_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('author_user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('message_type', sa.String(length=20), nullable=False),
        sa.Column('message_text', sa.Text(), nullable=False),
        sa.Column('author_name', sa.String(length=200), nullable=True),
        sa.Column('author_employee_code', sa.String(length=50), nullable=True),
        sa.Column('author_department_name', sa.String(length=150), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint("message_type IN ('COMMENT', 'SYSTEM_EVENT')", name='chk_internal_task_msg_type_valid'),
        sa.ForeignKeyConstraint(['task_id'], ['internal_task.task_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['author_user_id'], ['user_master.user_id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('message_id'),
        comment='Append-only conversation timeline for internal tasks',
    )
    op.create_index('ix_internal_task_msg_task_created', 'internal_task_message', ['task_id', 'created_at'])

    # Register the page in module_master so it appears in navigation and the permissions screen.
    # Idempotent: only inserted when missing; parent is the existing OPERATIONS module (if present).
    module_id = uuid.uuid5(uuid.uuid5(uuid.NAMESPACE_DNS, "gocompliance.crm.modules"), MODULE_CODE)
    op.get_bind().execute(
        sa.text(
            """
            INSERT INTO module_master
                (module_id, module_code, module_name, parent_module_id, route, description,
                 display_order, is_navigation, status, created_at, updated_at)
            SELECT CAST(:module_id AS uuid), CAST(:code AS varchar), CAST(:name AS varchar),
                   (SELECT module_id FROM module_master WHERE module_code = 'OPERATIONS' LIMIT 1),
                   CAST(:route AS varchar), CAST(:description AS text), 75, TRUE, 'ACTIVE', now(), now()
            WHERE NOT EXISTS (
                SELECT 1 FROM module_master WHERE module_code = CAST(:code AS varchar)
            )
            """
        ),
        {
            "module_id": module_id,
            "code": MODULE_CODE,
            "name": "R&D / Internal Tasks",
            "route": "/operations/internal-tasks",
            "description": "Internal (non-sales) tasks: R&D research, vendor work and other assignments",
        },
    )


def downgrade() -> None:
    bind = op.get_bind()
    bind.execute(
        sa.text(
            "DELETE FROM user_module_permission WHERE module_id IN "
            "(SELECT module_id FROM module_master WHERE module_code = :code)"
        ),
        {"code": MODULE_CODE},
    )
    bind.execute(sa.text("DELETE FROM module_master WHERE module_code = :code"), {"code": MODULE_CODE})

    op.drop_index('ix_internal_task_msg_task_created', table_name='internal_task_message')
    op.drop_table('internal_task_message')
    op.drop_index('ix_internal_task_company_status', table_name='internal_task')
    op.drop_index('ix_internal_task_created_by_user_id', table_name='internal_task')
    op.drop_index('ix_internal_task_assigned_to_user_id', table_name='internal_task')
    op.drop_index('ix_internal_task_status', table_name='internal_task')
    op.drop_index('ix_internal_task_company_id', table_name='internal_task')
    op.drop_table('internal_task')
    op.execute(sa.schema.DropSequence(sa.Sequence('internal_task_number_seq')))
