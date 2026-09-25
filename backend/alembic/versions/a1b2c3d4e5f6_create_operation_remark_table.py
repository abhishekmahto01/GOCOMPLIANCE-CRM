"""create_operation_remark_table

Revision ID: a1b2c3d4e5f6
Revises: 9c0f1e234567
Create Date: 2026-09-26 01:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '9c0f1e234567'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'operation_remark',
        sa.Column('remark_id', sa.UUID(), nullable=False, comment='Unique identifier for the operation remark (UUIDv4)'),
        sa.Column('application_id', sa.UUID(), nullable=False, comment='Foreign key referencing operation_application.application_id (ON DELETE CASCADE)'),
        sa.Column('author_user_id', sa.UUID(), nullable=False, comment='User who authored this operation remark'),
        sa.Column('remark_text', sa.String(length=2000), nullable=False, comment='Remark explanation or status update text'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when remark was recorded (UTC)'),
        sa.ForeignKeyConstraint(['application_id'], ['operation_application.application_id'], name='fk_op_remark_application_id', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['author_user_id'], ['user_master.user_id'], name='fk_op_remark_author_user_id', ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('remark_id'),
        comment='Operations remarks history tracking reasons for delays, blockers, or progress context',
    )
    op.create_index(op.f('ix_operation_remark_application_id'), 'operation_remark', ['application_id'], unique=False)
    op.create_index(op.f('ix_operation_remark_author_user_id'), 'operation_remark', ['author_user_id'], unique=False)
    op.create_index(op.f('ix_operation_remark_created_at'), 'operation_remark', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_operation_remark_created_at'), table_name='operation_remark')
    op.drop_index(op.f('ix_operation_remark_author_user_id'), table_name='operation_remark')
    op.drop_index(op.f('ix_operation_remark_application_id'), table_name='operation_remark')
    op.drop_table('operation_remark')
