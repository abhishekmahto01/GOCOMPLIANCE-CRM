"""create_source_master

Revision ID: f7b8c9d0e1f2
Revises: e6a7b8c9d0f1
Create Date: 2026-11-01 19:00:00.000000

"""
import uuid
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'f7b8c9d0e1f2'
down_revision: Union[str, None] = 'e6a7b8c9d0f1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create source_master table
    source_master_table = op.create_table(
        'source_master',
        sa.Column('source_id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('source_code', sa.String(length=50), nullable=False, comment='Uppercase unique identifier for source, e.g. WEBSITE, JUSTDIAL'),
        sa.Column('source_name', sa.String(length=100), nullable=False, comment='Display name for source, e.g. Website, Justdial, IndiaMART'),
        sa.Column('description', sa.Text(), nullable=True, comment='Optional description of the acquisition source'),
        sa.Column('status', sa.String(length=20), server_default=sa.text("'ACTIVE'"), nullable=False, comment='ACTIVE or INACTIVE'),
        sa.Column('is_system', sa.Boolean(), server_default=sa.text('false'), nullable=False, comment='Flag indicating system-seeded default source'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint("source_code ~ '^[A-Z0-9_]+$'", name='chk_source_code_format'),
        sa.CheckConstraint("status IN ('ACTIVE', 'INACTIVE')", name='chk_source_status_valid'),
        sa.PrimaryKeyConstraint('source_id'),
        sa.UniqueConstraint('source_code', name='uq_source_code'),
        sa.UniqueConstraint('source_name', name='uq_source_name'),
        comment='Master registry for lead acquisition sources and marketing channels'
    )
    op.create_index(op.f('ix_source_master_source_code'), 'source_master', ['source_code'], unique=False)

    # 2. Seed initial default sources
    initial_sources = [
        {
            'source_id': uuid.uuid4(),
            'source_code': 'WEBSITE',
            'source_name': 'Website',
            'description': 'Direct enquiries from company website',
            'status': 'ACTIVE',
            'is_system': True,
        },
        {
            'source_id': uuid.uuid4(),
            'source_code': 'REFERRAL',
            'source_name': 'Referral',
            'description': 'Client referrals and partner recommendations',
            'status': 'ACTIVE',
            'is_system': True,
        },
        {
            'source_id': uuid.uuid4(),
            'source_code': 'DIRECT',
            'source_name': 'Direct',
            'description': 'Direct walk-in or outbound sales contact',
            'status': 'ACTIVE',
            'is_system': True,
        },
        {
            'source_id': uuid.uuid4(),
            'source_code': 'JUSTDIAL',
            'source_name': 'Justdial',
            'description': 'Lead acquisition via Justdial platform',
            'status': 'ACTIVE',
            'is_system': True,
        },
        {
            'source_id': uuid.uuid4(),
            'source_code': 'INDIAMART',
            'source_name': 'IndiaMART',
            'description': 'Lead acquisition via IndiaMART marketplace',
            'status': 'ACTIVE',
            'is_system': True,
        },
        {
            'source_id': uuid.uuid4(),
            'source_code': 'OTHERS',
            'source_name': 'Others',
            'description': 'Other miscellaneous acquisition channels',
            'status': 'ACTIVE',
            'is_system': True,
        },
    ]
    op.bulk_insert(source_master_table, initial_sources)


def downgrade() -> None:
    op.drop_index(op.f('ix_source_master_source_code'), table_name='source_master')
    op.drop_table('source_master')

