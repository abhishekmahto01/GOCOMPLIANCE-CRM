"""add_sales_entry_register_fields

Revision ID: 9c0f1e234567
Revises: 8b9e0f123456
Create Date: 2026-09-23 23:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9c0f1e234567'
down_revision: Union[str, None] = '8b9e0f123456'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add columns to sales_order
    op.add_column(
        'sales_order',
        sa.Column('proforma_invoice_no', sa.String(length=100), nullable=True, comment='Proforma invoice reference code'),
    )
    op.add_column(
        'sales_order',
        sa.Column('tax_invoice_no', sa.String(length=100), nullable=True, comment='Final tax invoice reference code'),
    )
    op.add_column(
        'sales_order',
        sa.Column('reimbursement_note', sa.String(length=500), nullable=True, comment='Reimbursement note or expense instructions'),
    )
    op.add_column(
        'sales_order',
        sa.Column('govt_fees', sa.Numeric(precision=12, scale=2), server_default=sa.text('0.00'), nullable=False, comment='Government statutory / filing fees in INR'),
    )
    op.add_column(
        'sales_order',
        sa.Column('incidental_cost', sa.Numeric(precision=12, scale=2), server_default=sa.text('0.00'), nullable=False, comment='Incidental / operational expenses in INR'),
    )
    op.add_column(
        'sales_order',
        sa.Column('profit_amount', sa.Numeric(precision=12, scale=2), server_default=sa.text('0.00'), nullable=False, comment='Net profit in INR (order_value - govt_fees - incidental_cost)'),
    )

    # 2. Add indices on invoice numbers
    op.create_index(op.f('ix_sales_order_proforma_invoice_no'), 'sales_order', ['proforma_invoice_no'], unique=False)
    op.create_index(op.f('ix_sales_order_tax_invoice_no'), 'sales_order', ['tax_invoice_no'], unique=False)

    # 3. Add check constraints to sales_order
    op.create_check_constraint('chk_sales_order_advance_le_total', 'sales_order', 'amount_received <= order_value')
    op.create_check_constraint('chk_sales_order_govt_fees_non_negative', 'sales_order', 'govt_fees >= 0')
    op.create_check_constraint('chk_sales_order_incidental_cost_non_negative', 'sales_order', 'incidental_cost >= 0')

    # 4. Make client_master contact_email nullable and add server defaults
    op.alter_column('client_master', 'contact_email', existing_type=sa.String(length=255), nullable=True, server_default=sa.text("''"))
    op.alter_column('client_master', 'entity_type', existing_type=sa.String(length=50), server_default=sa.text("'INDIVIDUAL'"))
    op.alter_column('client_master', 'contact_person', existing_type=sa.String(length=150), server_default=sa.text("''"))


def downgrade() -> None:
    # 1. Revert client_master alterations
    op.alter_column('client_master', 'contact_person', existing_type=sa.String(length=150), server_default=None)
    op.alter_column('client_master', 'entity_type', existing_type=sa.String(length=50), server_default=None)
    op.alter_column('client_master', 'contact_email', existing_type=sa.String(length=255), nullable=False, server_default=None)

    # 2. Drop check constraints
    op.drop_constraint('chk_sales_order_incidental_cost_non_negative', 'sales_order', type_='check')
    op.drop_constraint('chk_sales_order_govt_fees_non_negative', 'sales_order', type_='check')
    op.drop_constraint('chk_sales_order_advance_le_total', 'sales_order', type_='check')

    # 3. Drop indices
    op.drop_index(op.f('ix_sales_order_tax_invoice_no'), table_name='sales_order')
    op.drop_index(op.f('ix_sales_order_proforma_invoice_no'), table_name='sales_order')

    # 4. Drop columns from sales_order
    op.drop_column('sales_order', 'profit_amount')
    op.drop_column('sales_order', 'incidental_cost')
    op.drop_column('sales_order', 'govt_fees')
    op.drop_column('sales_order', 'reimbursement_note')
    op.drop_column('sales_order', 'tax_invoice_no')
    op.drop_column('sales_order', 'proforma_invoice_no')
