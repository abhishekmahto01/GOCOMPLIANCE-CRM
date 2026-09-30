"""create_accounts_module_tables

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-10-01 01:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd4e5f6a7b8c9'
down_revision: Union[str, None] = 'c3d4e5f6a7b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create payment_transaction table
    op.create_table(
        'payment_transaction',
        sa.Column('payment_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sales_order_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('payment_number', sa.String(length=50), nullable=False),
        sa.Column('amount', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('payment_date', sa.Date(), nullable=False),
        sa.Column('payment_mode', sa.String(length=50), server_default=sa.text("'BANK_TRANSFER'"), nullable=False),
        sa.Column('transaction_reference', sa.String(length=100), nullable=True),
        sa.Column('receiving_account', sa.String(length=100), nullable=True),
        sa.Column('proof_attachment_path', sa.String(length=500), nullable=True),
        sa.Column('proof_attachment_name', sa.String(length=255), nullable=True),
        sa.Column('remark', sa.String(length=1000), nullable=True),
        sa.Column('submitted_by_user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('submitted_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('verification_status', sa.String(length=30), server_default=sa.text("'PENDING_VERIFICATION'"), nullable=False),
        sa.Column('verified_by_user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('reversal_reason', sa.String(length=500), nullable=True),
        sa.Column('reversed_by_user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('reversed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_opening_balance', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['company_master.company_id'], name='fk_payment_transaction_company_id', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['sales_order_id'], ['sales_order.order_id'], name='fk_payment_transaction_sales_order_id', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['submitted_by_user_id'], ['user_master.user_id'], name='fk_payment_transaction_submitted_by', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['verified_by_user_id'], ['user_master.user_id'], name='fk_payment_transaction_verified_by', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['reversed_by_user_id'], ['user_master.user_id'], name='fk_payment_transaction_reversed_by', ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('payment_id'),
        sa.UniqueConstraint('payment_number', name='uq_payment_transaction_number'),
        comment='Payment receipts and collections ledger for Accounts module'
    )
    op.create_index(op.f('ix_payment_transaction_company_id'), 'payment_transaction', ['company_id'], unique=False)
    op.create_index(op.f('ix_payment_transaction_sales_order_id'), 'payment_transaction', ['sales_order_id'], unique=False)
    op.create_index(op.f('ix_payment_transaction_payment_number'), 'payment_transaction', ['payment_number'], unique=True)
    op.create_index(op.f('ix_payment_transaction_payment_date'), 'payment_transaction', ['payment_date'], unique=False)
    op.create_index(op.f('ix_payment_transaction_transaction_reference'), 'payment_transaction', ['transaction_reference'], unique=False)
    op.create_index(op.f('ix_payment_transaction_submitted_by_user_id'), 'payment_transaction', ['submitted_by_user_id'], unique=False)
    op.create_index(op.f('ix_payment_transaction_verification_status'), 'payment_transaction', ['verification_status'], unique=False)

    # 2. Create accounts_follow_up table
    op.create_table(
        'accounts_follow_up',
        sa.Column('follow_up_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sales_order_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('follow_up_date', sa.Date(), nullable=False),
        sa.Column('next_follow_up_date', sa.Date(), nullable=True),
        sa.Column('contact_channel', sa.String(length=50), server_default=sa.text("'PHONE'"), nullable=False),
        sa.Column('contact_person', sa.String(length=150), nullable=True),
        sa.Column('remark_text', sa.String(length=1000), nullable=False),
        sa.Column('created_by_user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['company_master.company_id'], name='fk_accounts_follow_up_company_id', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['sales_order_id'], ['sales_order.order_id'], name='fk_accounts_follow_up_sales_order_id', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['user_master.user_id'], name='fk_accounts_follow_up_created_by', ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('follow_up_id'),
        comment='Follow-up history and debtor remarks for Accounts module'
    )
    op.create_index(op.f('ix_accounts_follow_up_company_id'), 'accounts_follow_up', ['company_id'], unique=False)
    op.create_index(op.f('ix_accounts_follow_up_sales_order_id'), 'accounts_follow_up', ['sales_order_id'], unique=False)
    op.create_index(op.f('ix_accounts_follow_up_follow_up_date'), 'accounts_follow_up', ['follow_up_date'], unique=False)
    op.create_index(op.f('ix_accounts_follow_up_next_follow_up_date'), 'accounts_follow_up', ['next_follow_up_date'], unique=False)
    op.create_index(op.f('ix_accounts_follow_up_created_by_user_id'), 'accounts_follow_up', ['created_by_user_id'], unique=False)

    # 3. Create accounts_invoice table
    op.create_table(
        'accounts_invoice',
        sa.Column('invoice_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sales_order_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('invoice_type', sa.String(length=30), nullable=False),
        sa.Column('invoice_number', sa.String(length=100), nullable=False),
        sa.Column('invoice_date', sa.Date(), nullable=False),
        sa.Column('due_date', sa.Date(), nullable=True),
        sa.Column('amount', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('taxable_amount', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('cgst_amount', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('sgst_amount', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('igst_amount', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('status', sa.String(length=30), server_default=sa.text("'ISSUED'"), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=True),
        sa.Column('file_name', sa.String(length=255), nullable=True),
        sa.Column('notes', sa.String(length=1000), nullable=True),
        sa.Column('created_by_user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['company_master.company_id'], name='fk_accounts_invoice_company_id', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['sales_order_id'], ['sales_order.order_id'], name='fk_accounts_invoice_sales_order_id', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['user_master.user_id'], name='fk_accounts_invoice_created_by', ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('invoice_id'),
        sa.UniqueConstraint('company_id', 'invoice_type', 'invoice_number', name='uq_accounts_invoice_company_type_number'),
        comment='Invoice metadata and document attachments for Accounts module'
    )
    op.create_index(op.f('ix_accounts_invoice_company_id'), 'accounts_invoice', ['company_id'], unique=False)
    op.create_index(op.f('ix_accounts_invoice_sales_order_id'), 'accounts_invoice', ['sales_order_id'], unique=False)
    op.create_index(op.f('ix_accounts_invoice_invoice_type'), 'accounts_invoice', ['invoice_type'], unique=False)
    op.create_index(op.f('ix_accounts_invoice_invoice_number'), 'accounts_invoice', ['invoice_number'], unique=False)
    op.create_index(op.f('ix_accounts_invoice_invoice_date'), 'accounts_invoice', ['invoice_date'], unique=False)
    op.create_index(op.f('ix_accounts_invoice_created_by_user_id'), 'accounts_invoice', ['created_by_user_id'], unique=False)

    # 4. Create accounts_expense table
    op.create_table(
        'accounts_expense',
        sa.Column('expense_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sales_order_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('expense_number', sa.String(length=50), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('amount', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('expense_date', sa.Date(), nullable=False),
        sa.Column('payee_name', sa.String(length=200), nullable=False),
        sa.Column('paid_by_type', sa.String(length=30), server_default=sa.text("'COMPANY'"), nullable=False),
        sa.Column('paid_by_user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('payment_mode', sa.String(length=50), server_default=sa.text("'BANK_TRANSFER'"), nullable=False),
        sa.Column('transaction_reference', sa.String(length=100), nullable=True),
        sa.Column('bill_attachment_path', sa.String(length=500), nullable=True),
        sa.Column('bill_attachment_name', sa.String(length=255), nullable=True),
        sa.Column('remark', sa.String(length=1000), nullable=True),
        sa.Column('approval_status', sa.String(length=30), server_default=sa.text("'PENDING_APPROVAL'"), nullable=False),
        sa.Column('approved_by_user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('rejection_reason', sa.String(length=500), nullable=True),
        sa.Column('settlement_status', sa.String(length=30), server_default=sa.text("'NOT_APPLICABLE'"), nullable=False),
        sa.Column('settled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('settled_by_user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('settlement_reference', sa.String(length=100), nullable=True),
        sa.Column('created_by_user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['company_master.company_id'], name='fk_accounts_expense_company_id', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['sales_order_id'], ['sales_order.order_id'], name='fk_accounts_expense_sales_order_id', ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['paid_by_user_id'], ['user_master.user_id'], name='fk_accounts_expense_paid_by_user', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['approved_by_user_id'], ['user_master.user_id'], name='fk_accounts_expense_approved_by', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['settled_by_user_id'], ['user_master.user_id'], name='fk_accounts_expense_settled_by', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['user_master.user_id'], name='fk_accounts_expense_created_by', ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('expense_id'),
        sa.UniqueConstraint('expense_number', name='uq_accounts_expense_number'),
        comment='Direct costs and employee reimbursements ledger for Accounts module'
    )
    op.create_index(op.f('ix_accounts_expense_company_id'), 'accounts_expense', ['company_id'], unique=False)
    op.create_index(op.f('ix_accounts_expense_sales_order_id'), 'accounts_expense', ['sales_order_id'], unique=False)
    op.create_index(op.f('ix_accounts_expense_expense_number'), 'accounts_expense', ['expense_number'], unique=True)
    op.create_index(op.f('ix_accounts_expense_category'), 'accounts_expense', ['category'], unique=False)
    op.create_index(op.f('ix_accounts_expense_expense_date'), 'accounts_expense', ['expense_date'], unique=False)
    op.create_index(op.f('ix_accounts_expense_approval_status'), 'accounts_expense', ['approval_status'], unique=False)
    op.create_index(op.f('ix_accounts_expense_settlement_status'), 'accounts_expense', ['settlement_status'], unique=False)
    op.create_index(op.f('ix_accounts_expense_paid_by_user_id'), 'accounts_expense', ['paid_by_user_id'], unique=False)
    op.create_index(op.f('ix_accounts_expense_created_by_user_id'), 'accounts_expense', ['created_by_user_id'], unique=False)

    # 5. Create accounts_audit_log table
    op.create_table(
        'accounts_audit_log',
        sa.Column('audit_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('entity_type', sa.String(length=50), nullable=False),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('actor_user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('old_values', sa.Text(), nullable=True),
        sa.Column('new_values', sa.Text(), nullable=True),
        sa.Column('reason', sa.String(length=500), nullable=True),
        sa.Column('ip_address', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['company_master.company_id'], name='fk_accounts_audit_log_company_id', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['actor_user_id'], ['user_master.user_id'], name='fk_accounts_audit_log_actor_user_id', ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('audit_id'),
        comment='Immutable financial audit logs for Accounts module'
    )
    op.create_index(op.f('ix_accounts_audit_log_company_id'), 'accounts_audit_log', ['company_id'], unique=False)
    op.create_index(op.f('ix_accounts_audit_log_entity_type'), 'accounts_audit_log', ['entity_type'], unique=False)
    op.create_index(op.f('ix_accounts_audit_log_entity_id'), 'accounts_audit_log', ['entity_id'], unique=False)
    op.create_index(op.f('ix_accounts_audit_log_action'), 'accounts_audit_log', ['action'], unique=False)
    op.create_index(op.f('ix_accounts_audit_log_actor_user_id'), 'accounts_audit_log', ['actor_user_id'], unique=False)
    op.create_index(op.f('ix_accounts_audit_log_created_at'), 'accounts_audit_log', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_table('accounts_audit_log')
    op.drop_table('accounts_expense')
    op.drop_table('accounts_invoice')
    op.drop_table('accounts_follow_up')
    op.drop_table('payment_transaction')
