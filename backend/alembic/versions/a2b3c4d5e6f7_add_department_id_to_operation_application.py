"""add_department_id_to_operation_application

Revision ID: a2b3c4d5e6f7
Revises: f7b8c9d0e1f2
Create Date: 2026-11-02 22:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'a2b3c4d5e6f7'
down_revision: Union[str, None] = 'f7b8c9d0e1f2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add department_id column to operation_application (additive, non-destructive)
    op.add_column(
        'operation_application',
        sa.Column(
            'department_id',
            postgresql.UUID(as_uuid=True),
            nullable=True,
            comment='Foreign key referencing department_master.department_id (Operations department)',
        ),
    )

    # 2. Add foreign key constraint
    op.create_foreign_key(
        'fk_op_app_department_id',
        'operation_application',
        'department_master',
        ['department_id'],
        ['department_id'],
        ondelete='SET NULL',
    )

    # 3. Create index for fast query filtering
    op.create_index(
        'ix_operation_application_department_id',
        'operation_application',
        ['department_id'],
        unique=False,
    )

    # 4. Safe additive backfill: populate existing records with Operations department ID
    bind = op.get_bind()
    bind.execute(
        sa.text(
            """
            UPDATE operation_application
            SET department_id = (
                SELECT department_id FROM department_master
                WHERE department_code IN ('OPERATIONS', 'OP', 'OPS')
                LIMIT 1
            )
            WHERE department_id IS NULL
            """
        )
    )


def downgrade() -> None:
    op.drop_index('ix_operation_application_department_id', table_name='operation_application')
    op.drop_constraint('fk_op_app_department_id', 'operation_application', type_='foreignkey')
    op.drop_column('operation_application', 'department_id')

