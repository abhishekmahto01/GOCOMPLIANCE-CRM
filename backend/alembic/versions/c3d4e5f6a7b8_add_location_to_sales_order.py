"""add_location_to_sales_order

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-09-30 10:55:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add location column to sales_order
    op.add_column(
        'sales_order',
        sa.Column(
            'location',
            sa.String(length=200),
            nullable=True,
            comment='Branch / City / Work location for multi-location clients',
        ),
    )
    op.create_index(op.f('ix_sales_order_location'), 'sales_order', ['location'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_sales_order_location'), table_name='sales_order')
    op.drop_column('sales_order', 'location')
