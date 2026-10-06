"""add_gst_invoice_required_to_sales_order

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-10-07 01:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e5f6a7b8c9d0'
down_revision: Union[str, None] = 'd4e5f6a7b8c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add gst_invoice_required column to sales_order with false default
    op.add_column(
        'sales_order',
        sa.Column(
            'gst_invoice_required',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('false'),
            comment='Routing flag: True if GST invoice is required and should appear in Accounts',
        ),
    )
    op.create_index(
        op.f('ix_sales_order_gst_invoice_required'),
        'sales_order',
        ['gst_invoice_required'],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f('ix_sales_order_gst_invoice_required'), table_name='sales_order')
    op.drop_column('sales_order', 'gst_invoice_required')
