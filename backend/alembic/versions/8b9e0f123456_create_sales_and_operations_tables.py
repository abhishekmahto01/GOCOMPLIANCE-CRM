"""create_sales_and_operations_tables

Revision ID: 8b9e0f123456
Revises: 7a8e9f101112
Create Date: 2026-09-23 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '8b9e0f123456'
down_revision: Union[str, None] = '7a8e9f101112'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. service_master
    op.create_table(
        'service_master',
        sa.Column('service_id', sa.UUID(), nullable=False, comment='Unique identifier for the service (UUIDv4)'),
        sa.Column('service_code', sa.String(length=60), nullable=False, comment='Uppercase unique system identifier (e.g. TRADE_LICENSE, SHOP_ACT, CLRA)'),
        sa.Column('service_name', sa.String(length=150), nullable=False, comment='Display name of the service/licence (e.g. Trade License, Shop Act)'),
        sa.Column('category', sa.String(length=50), nullable=False, comment='Service classification: LICENCE, REGISTRATION, INCORPORATION, COMPLIANCE'),
        sa.Column('description', sa.String(length=500), nullable=True, comment='Optional service description and statutory scope'),
        sa.Column('base_price', sa.Numeric(precision=12, scale=2), server_default=sa.text('0.00'), nullable=False, comment='Standard professional fee / base price in INR'),
        sa.Column('govt_fee', sa.Numeric(precision=12, scale=2), server_default=sa.text('0.00'), nullable=False, comment='Estimated government statutory fee in INR'),
        sa.Column('standard_turnaround_days', sa.Integer(), server_default=sa.text('15'), nullable=False, comment='Standard estimated SLA turnaround time in days'),
        sa.Column('status', sa.String(length=20), server_default=sa.text("'ACTIVE'"), nullable=False, comment='Operational status: ACTIVE or INACTIVE'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when service record was created (UTC)'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when service record was last updated (UTC)'),
        sa.CheckConstraint("service_code ~ '^[A-Z0-9_]+$'", name='chk_service_code_format'),
        sa.CheckConstraint("status IN ('ACTIVE', 'INACTIVE')", name='chk_service_status_valid'),
        sa.CheckConstraint('base_price >= 0', name='chk_service_base_price_non_negative'),
        sa.CheckConstraint('govt_fee >= 0', name='chk_service_govt_fee_non_negative'),
        sa.CheckConstraint('standard_turnaround_days > 0', name='chk_service_turnaround_positive'),
        sa.PrimaryKeyConstraint('service_id'),
        comment='Master registry for compliance services, licences, and statutory filings',
    )
    op.create_index(op.f('ix_service_master_category'), 'service_master', ['category'], unique=False)
    op.create_index(op.f('ix_service_master_service_code'), 'service_master', ['service_code'], unique=True)
    op.create_index(op.f('ix_service_master_service_name'), 'service_master', ['service_name'], unique=False)
    op.create_index(op.f('ix_service_master_status'), 'service_master', ['status'], unique=False)

    # 2. service_required_document
    op.create_table(
        'service_required_document',
        sa.Column('doc_config_id', sa.UUID(), nullable=False, comment='Unique identifier for the document requirement configuration (UUIDv4)'),
        sa.Column('service_id', sa.UUID(), nullable=False, comment='Foreign key referencing service_master.service_id (ON DELETE CASCADE)'),
        sa.Column('document_code', sa.String(length=60), nullable=False, comment='System code for document (e.g. AADHAAR, PAN, RENT_AGREEMENT, PROPERTY_TAX)'),
        sa.Column('document_name', sa.String(length=150), nullable=False, comment='Human-readable document name (e.g. Aadhaar Card of Applicant)'),
        sa.Column('is_mandatory', sa.Boolean(), server_default=sa.text('true'), nullable=False, comment='Whether this document is mandatory for application submission'),
        sa.Column('display_order', sa.Integer(), server_default=sa.text('0'), nullable=False, comment='Display sorting order in document checklists'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when document configuration was created (UTC)'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when document configuration was last updated (UTC)'),
        sa.CheckConstraint('display_order >= 0', name='chk_service_doc_display_order_non_negative'),
        sa.ForeignKeyConstraint(['service_id'], ['service_master.service_id'], name='fk_service_required_doc_service_id', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('doc_config_id'),
        sa.UniqueConstraint('service_id', 'document_code', name='uq_service_required_doc_service_code'),
        comment='Standard document checklist configuration required for each service',
    )
    op.create_index(op.f('ix_service_required_document_service_id'), 'service_required_document', ['service_id'], unique=False)

    # 3. client_master
    op.create_table(
        'client_master',
        sa.Column('client_id', sa.UUID(), nullable=False, comment='Unique identifier for the client (UUIDv4)'),
        sa.Column('company_id', sa.UUID(), nullable=False, comment='Foreign key referencing company_master.company_id (ON DELETE RESTRICT)'),
        sa.Column('client_name', sa.String(length=200), nullable=False, comment='Business or individual trade name (e.g. Sharma Enterprises, Gupta Traders)'),
        sa.Column('entity_type', sa.String(length=50), nullable=False, comment='Entity type: Private Limited, LLP, One Person Company, Partnership, Proprietorship, Individual'),
        sa.Column('contact_person', sa.String(length=150), nullable=False, comment='Primary contact person name'),
        sa.Column('contact_email', sa.String(length=255), nullable=False, comment='Primary contact email address'),
        sa.Column('contact_phone', sa.String(length=20), nullable=False, comment='Primary contact phone / mobile number'),
        sa.Column('pan_number', sa.String(length=20), nullable=True, comment='Income Tax PAN number of the client entity'),
        sa.Column('gstin', sa.String(length=20), nullable=True, comment='GST Identification Number (GSTIN) if applicable'),
        sa.Column('city', sa.String(length=100), nullable=True, comment='Operating city'),
        sa.Column('state', sa.String(length=100), nullable=True, comment='Operating state / union territory'),
        sa.Column('created_by_user_id', sa.UUID(), nullable=False, comment='Foreign key referencing user who onboarded this client'),
        sa.Column('status', sa.String(length=20), server_default=sa.text("'ACTIVE'"), nullable=False, comment='Operational status: ACTIVE or INACTIVE'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when client record was created (UTC)'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when client record was last updated (UTC)'),
        sa.CheckConstraint("status IN ('ACTIVE', 'INACTIVE')", name='chk_client_status_valid'),
        sa.ForeignKeyConstraint(['company_id'], ['company_master.company_id'], name='fk_client_company_id', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['user_master.user_id'], name='fk_client_created_by_user_id', ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('client_id'),
        comment='Master registry for corporate and individual clients in Gocompliances CRM',
    )
    op.create_index(op.f('ix_client_master_client_name'), 'client_master', ['client_name'], unique=False)
    op.create_index(op.f('ix_client_master_company_id'), 'client_master', ['company_id'], unique=False)
    op.create_index(op.f('ix_client_master_created_by_user_id'), 'client_master', ['created_by_user_id'], unique=False)
    op.create_index(op.f('ix_client_master_status'), 'client_master', ['status'], unique=False)

    # 4. sales_order
    op.create_table(
        'sales_order',
        sa.Column('order_id', sa.UUID(), nullable=False, comment='Unique identifier for the sales order (UUIDv4)'),
        sa.Column('order_number', sa.String(length=30), nullable=False, comment='Unique formatted order code (e.g. SO-2025-0048)'),
        sa.Column('company_id', sa.UUID(), nullable=False, comment='Foreign key referencing company_master.company_id'),
        sa.Column('client_id', sa.UUID(), nullable=False, comment='Foreign key referencing client_master.client_id'),
        sa.Column('service_id', sa.UUID(), nullable=False, comment='Foreign key referencing service_master.service_id'),
        sa.Column('salesperson_user_id', sa.UUID(), nullable=False, comment='Foreign key referencing sales employee who closed the order'),
        sa.Column('lead_source', sa.String(length=50), server_default=sa.text("'DIRECT'"), nullable=False, comment='Lead acquisition channel: WEBSITE, REFERRAL, DIRECT, OTHERS'),
        sa.Column('order_date', sa.Date(), nullable=False, comment='Date when order was placed'),
        sa.Column('order_value', sa.Numeric(precision=12, scale=2), nullable=False, comment='Total order contract value in INR'),
        sa.Column('amount_received', sa.Numeric(precision=12, scale=2), server_default=sa.text('0.00'), nullable=False, comment='Total amount collected/received in INR'),
        sa.Column('balance_amount', sa.Numeric(precision=12, scale=2), server_default=sa.text('0.00'), nullable=False, comment='Outstanding balance amount in INR (order_value - amount_received)'),
        sa.Column('payment_status', sa.String(length=20), server_default=sa.text("'PENDING'"), nullable=False, comment='Payment collection status: FULLY_PAID, PARTIALLY_PAID, PENDING, OVERDUE'),
        sa.Column('confirmation_status', sa.String(length=20), server_default=sa.text("'DRAFT'"), nullable=False, comment='Order confirmation workflow state: DRAFT, CONFIRMED, CANCELLED'),
        sa.Column('confirmed_at', sa.DateTime(timezone=True), nullable=True, comment='Timestamp when order was confirmed and handed over to operations'),
        sa.Column('notes', sa.String(length=1000), nullable=True, comment='Order notes or instructions from sales team'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when order record was created (UTC)'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when order record was last updated (UTC)'),
        sa.CheckConstraint('order_value >= 0', name='chk_sales_order_value_non_negative'),
        sa.CheckConstraint('amount_received >= 0', name='chk_sales_order_received_non_negative'),
        sa.CheckConstraint('balance_amount >= 0', name='chk_sales_order_balance_non_negative'),
        sa.CheckConstraint("payment_status IN ('FULLY_PAID', 'PARTIALLY_PAID', 'PENDING', 'OVERDUE')", name='chk_sales_order_payment_status_valid'),
        sa.CheckConstraint("confirmation_status IN ('DRAFT', 'CONFIRMED', 'CANCELLED')", name='chk_sales_order_confirmation_status_valid'),
        sa.ForeignKeyConstraint(['client_id'], ['client_master.client_id'], name='fk_sales_order_client_id', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['company_id'], ['company_master.company_id'], name='fk_sales_order_company_id', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['salesperson_user_id'], ['user_master.user_id'], name='fk_sales_order_salesperson_id', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['service_id'], ['service_master.service_id'], name='fk_sales_order_service_id', ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('order_id'),
        comment='Master registry for client sales orders and collection tracking',
    )
    op.create_index(op.f('ix_sales_order_client_id'), 'sales_order', ['client_id'], unique=False)
    op.create_index(op.f('ix_sales_order_company_id'), 'sales_order', ['company_id'], unique=False)
    op.create_index(op.f('ix_sales_order_confirmation_status'), 'sales_order', ['confirmation_status'], unique=False)
    op.create_index(op.f('ix_sales_order_confirmed_at'), 'sales_order', ['confirmed_at'], unique=False)
    op.create_index(op.f('ix_sales_order_lead_source'), 'sales_order', ['lead_source'], unique=False)
    op.create_index(op.f('ix_sales_order_order_date'), 'sales_order', ['order_date'], unique=False)
    op.create_index(op.f('ix_sales_order_order_number'), 'sales_order', ['order_number'], unique=True)
    op.create_index(op.f('ix_sales_order_payment_status'), 'sales_order', ['payment_status'], unique=False)
    op.create_index(op.f('ix_sales_order_salesperson_user_id'), 'sales_order', ['salesperson_user_id'], unique=False)
    op.create_index(op.f('ix_sales_order_service_id'), 'sales_order', ['service_id'], unique=False)

    # 5. operation_application
    op.create_table(
        'operation_application',
        sa.Column('application_id', sa.UUID(), nullable=False, comment='Unique identifier for the operation application (UUIDv4)'),
        sa.Column('application_number', sa.String(length=30), nullable=False, comment='Unique formatted application code (e.g. AP-2025-0084)'),
        sa.Column('sales_order_id', sa.UUID(), nullable=False, comment='1-to-1 foreign key to originating sales order (strictly idempotent)'),
        sa.Column('company_id', sa.UUID(), nullable=False, comment='Foreign key referencing company_master.company_id'),
        sa.Column('client_id', sa.UUID(), nullable=False, comment='Foreign key referencing client_master.client_id'),
        sa.Column('service_id', sa.UUID(), nullable=False, comment='Foreign key referencing service_master.service_id'),
        sa.Column('assigned_to_user_id', sa.UUID(), nullable=True, comment='Operations employee currently assigned to this task (nullable when UNASSIGNED)'),
        sa.Column('assigned_by_user_id', sa.UUID(), nullable=True, comment='Operations Manager / Admin who assigned or reassigned this task'),
        sa.Column('assigned_at', sa.DateTime(timezone=True), nullable=True, comment='Timestamp when task was assigned to current employee'),
        sa.Column('priority', sa.String(length=10), server_default=sa.text("'MEDIUM'"), nullable=False, comment='Task priority: LOW, MEDIUM, HIGH, URGENT'),
        sa.Column('application_status', sa.String(length=30), server_default=sa.text("'UNASSIGNED'"), nullable=False, comment='Lifecycle status: UNASSIGNED, ASSIGNED, IN_PROGRESS, PENDING_DOCUMENTS, READY_FOR_SUBMISSION, SUBMITTED, AUTHORITY_QUERY, APPROVED, CANCELLED'),
        sa.Column('target_due_date', sa.Date(), nullable=True, comment='Target completion due date for statutory filing'),
        sa.Column('completion_date', sa.Date(), nullable=True, comment='Actual completion / approval date'),
        sa.Column('assignment_notes', sa.String(length=1000), nullable=True, comment='Internal handover or assignment instructions'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when application record was created (UTC)'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when application record was last updated (UTC)'),
        sa.CheckConstraint("priority IN ('LOW', 'MEDIUM', 'HIGH', 'URGENT')", name='chk_op_application_priority_valid'),
        sa.CheckConstraint("application_status IN ('UNASSIGNED', 'ASSIGNED', 'IN_PROGRESS', 'PENDING_DOCUMENTS', 'READY_FOR_SUBMISSION', 'SUBMITTED', 'AUTHORITY_QUERY', 'APPROVED', 'CANCELLED')", name='chk_op_application_status_valid'),
        sa.ForeignKeyConstraint(['assigned_by_user_id'], ['user_master.user_id'], name='fk_op_app_assigned_by_id', ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['assigned_to_user_id'], ['user_master.user_id'], name='fk_op_app_assigned_to_id', ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['client_id'], ['client_master.client_id'], name='fk_op_app_client_id', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['company_id'], ['company_master.company_id'], name='fk_op_app_company_id', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['sales_order_id'], ['sales_order.order_id'], name='fk_op_app_sales_order_id', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['service_id'], ['service_master.service_id'], name='fk_op_app_service_id', ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('application_id'),
        sa.UniqueConstraint('sales_order_id', name='uq_op_app_sales_order_id'),
        comment='Operations workflow application tracking statutory filings and task fulfillment',
    )
    op.create_index(op.f('ix_operation_application_application_number'), 'operation_application', ['application_number'], unique=True)
    op.create_index(op.f('ix_operation_application_application_status'), 'operation_application', ['application_status'], unique=False)
    op.create_index(op.f('ix_operation_application_assigned_at'), 'operation_application', ['assigned_at'], unique=False)
    op.create_index(op.f('ix_operation_application_assigned_to_user_id'), 'operation_application', ['assigned_to_user_id'], unique=False)
    op.create_index(op.f('ix_operation_application_client_id'), 'operation_application', ['client_id'], unique=False)
    op.create_index(op.f('ix_operation_application_company_id'), 'operation_application', ['company_id'], unique=False)
    op.create_index(op.f('ix_operation_application_priority'), 'operation_application', ['priority'], unique=False)
    op.create_index(op.f('ix_operation_application_sales_order_id'), 'operation_application', ['sales_order_id'], unique=True)
    op.create_index(op.f('ix_operation_application_service_id'), 'operation_application', ['service_id'], unique=False)
    op.create_index(op.f('ix_operation_application_target_due_date'), 'operation_application', ['target_due_date'], unique=False)

    # 6. application_document
    op.create_table(
        'application_document',
        sa.Column('app_doc_id', sa.UUID(), nullable=False, comment='Unique identifier for the application document requirement (UUIDv4)'),
        sa.Column('application_id', sa.UUID(), nullable=False, comment='Foreign key referencing operation_application.application_id (ON DELETE CASCADE)'),
        sa.Column('document_code', sa.String(length=60), nullable=False, comment='Document identifier code (e.g. AADHAAR, PAN, RENT_AGREEMENT)'),
        sa.Column('document_name', sa.String(length=150), nullable=False, comment='Human-readable document name'),
        sa.Column('is_mandatory', sa.Boolean(), server_default=sa.text('true'), nullable=False, comment='Whether this document is required for filing'),
        sa.Column('status', sa.String(length=20), server_default=sa.text("'PENDING'"), nullable=False, comment='Document status: PENDING, RECEIVED, VERIFIED, REJECTED, NOT_APPLICABLE'),
        sa.Column('rejection_reason', sa.String(length=500), nullable=True, comment='Reason if document was rejected / defective'),
        sa.Column('verified_by_user_id', sa.UUID(), nullable=True, comment='Employee who verified/approved the document'),
        sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True, comment='Timestamp when document was verified'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when document item was created (UTC)'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when document item was last updated (UTC)'),
        sa.CheckConstraint("status IN ('PENDING', 'RECEIVED', 'VERIFIED', 'REJECTED', 'NOT_APPLICABLE')", name='chk_app_doc_status_valid'),
        sa.ForeignKeyConstraint(['application_id'], ['operation_application.application_id'], name='fk_app_doc_application_id', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['verified_by_user_id'], ['user_master.user_id'], name='fk_app_doc_verified_by_id', ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('app_doc_id'),
        comment='Document requirements and verification statuses for an active application',
    )
    op.create_index(op.f('ix_application_document_application_id'), 'application_document', ['application_id'], unique=False)
    op.create_index(op.f('ix_application_document_status'), 'application_document', ['status'], unique=False)

    # 7. application_assignment_history
    op.create_table(
        'application_assignment_history',
        sa.Column('history_id', sa.UUID(), nullable=False, comment='Unique identifier for the assignment history record (UUIDv4)'),
        sa.Column('application_id', sa.UUID(), nullable=False, comment='Foreign key referencing operation_application.application_id (ON DELETE CASCADE)'),
        sa.Column('assigned_by_user_id', sa.UUID(), nullable=False, comment='Manager/Admin who performed the assignment'),
        sa.Column('previous_assignee_user_id', sa.UUID(), nullable=True, comment='Employee previously assigned (null if initial assignment)'),
        sa.Column('new_assignee_user_id', sa.UUID(), nullable=True, comment='Employee newly assigned (null if unassigned)'),
        sa.Column('reason', sa.String(length=500), nullable=True, comment='Reason or notes provided for assignment/reassignment'),
        sa.Column('assigned_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when assignment was executed (UTC)'),
        sa.ForeignKeyConstraint(['application_id'], ['operation_application.application_id'], name='fk_app_assign_hist_app_id', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['assigned_by_user_id'], ['user_master.user_id'], name='fk_app_assign_hist_assigned_by_id', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['new_assignee_user_id'], ['user_master.user_id'], name='fk_app_assign_hist_new_assignee_id', ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['previous_assignee_user_id'], ['user_master.user_id'], name='fk_app_assign_hist_prev_assignee_id', ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('history_id'),
        comment='Audit trail for application assignment and reassignment events',
    )
    op.create_index(op.f('ix_application_assignment_history_application_id'), 'application_assignment_history', ['application_id'], unique=False)

    # 8. application_activity_log
    op.create_table(
        'application_activity_log',
        sa.Column('activity_id', sa.UUID(), nullable=False, comment='Unique identifier for the activity log entry (UUIDv4)'),
        sa.Column('application_id', sa.UUID(), nullable=False, comment='Foreign key referencing operation_application.application_id (ON DELETE CASCADE)'),
        sa.Column('actor_user_id', sa.UUID(), nullable=False, comment='User who triggered this operational action'),
        sa.Column('action_type', sa.String(length=50), nullable=False, comment='Action classification: STATUS_CHANGE, DOCUMENT_STATUS_CHANGE, PRIORITY_CHANGE, DUE_DATE_CHANGE, NOTE_ADDED, ASSIGNMENT_CHANGE'),
        sa.Column('old_value', sa.String(length=255), nullable=True, comment='Previous attribute value prior to modification'),
        sa.Column('new_value', sa.String(length=255), nullable=True, comment='New attribute value after modification'),
        sa.Column('comment', sa.String(length=1000), nullable=True, comment='Descriptive note or reason accompanying the activity'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when activity occurred (UTC)'),
        sa.ForeignKeyConstraint(['actor_user_id'], ['user_master.user_id'], name='fk_app_activity_actor_id', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['application_id'], ['operation_application.application_id'], name='fk_app_activity_application_id', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('activity_id'),
        comment='Timeline and audit log of status changes and operational activities',
    )
    op.create_index(op.f('ix_application_activity_log_action_type'), 'application_activity_log', ['action_type'], unique=False)
    op.create_index(op.f('ix_application_activity_log_application_id'), 'application_activity_log', ['application_id'], unique=False)
    op.create_index(op.f('ix_application_activity_log_created_at'), 'application_activity_log', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_application_activity_log_created_at'), table_name='application_activity_log')
    op.drop_index(op.f('ix_application_activity_log_application_id'), table_name='application_activity_log')
    op.drop_index(op.f('ix_application_activity_log_action_type'), table_name='application_activity_log')
    op.drop_table('application_activity_log')

    op.drop_index(op.f('ix_application_assignment_history_application_id'), table_name='application_assignment_history')
    op.drop_table('application_assignment_history')

    op.drop_index(op.f('ix_application_document_status'), table_name='application_document')
    op.drop_index(op.f('ix_application_document_application_id'), table_name='application_document')
    op.drop_table('application_document')

    op.drop_index(op.f('ix_operation_application_target_due_date'), table_name='operation_application')
    op.drop_index(op.f('ix_operation_application_service_id'), table_name='operation_application')
    op.drop_index(op.f('ix_operation_application_sales_order_id'), table_name='operation_application')
    op.drop_index(op.f('ix_operation_application_priority'), table_name='operation_application')
    op.drop_index(op.f('ix_operation_application_company_id'), table_name='operation_application')
    op.drop_index(op.f('ix_operation_application_client_id'), table_name='operation_application')
    op.drop_index(op.f('ix_operation_application_assigned_to_user_id'), table_name='operation_application')
    op.drop_index(op.f('ix_operation_application_assigned_at'), table_name='operation_application')
    op.drop_index(op.f('ix_operation_application_application_status'), table_name='operation_application')
    op.drop_index(op.f('ix_operation_application_application_number'), table_name='operation_application')
    op.drop_table('operation_application')

    op.drop_index(op.f('ix_sales_order_service_id'), table_name='sales_order')
    op.drop_index(op.f('ix_sales_order_salesperson_user_id'), table_name='sales_order')
    op.drop_index(op.f('ix_sales_order_payment_status'), table_name='sales_order')
    op.drop_index(op.f('ix_sales_order_order_number'), table_name='sales_order')
    op.drop_index(op.f('ix_sales_order_order_date'), table_name='sales_order')
    op.drop_index(op.f('ix_sales_order_lead_source'), table_name='sales_order')
    op.drop_index(op.f('ix_sales_order_confirmed_at'), table_name='sales_order')
    op.drop_index(op.f('ix_sales_order_confirmation_status'), table_name='sales_order')
    op.drop_index(op.f('ix_sales_order_company_id'), table_name='sales_order')
    op.drop_index(op.f('ix_sales_order_client_id'), table_name='sales_order')
    op.drop_table('sales_order')

    op.drop_index(op.f('ix_client_master_status'), table_name='client_master')
    op.drop_index(op.f('ix_client_master_created_by_user_id'), table_name='client_master')
    op.drop_index(op.f('ix_client_master_company_id'), table_name='client_master')
    op.drop_index(op.f('ix_client_master_client_name'), table_name='client_master')
    op.drop_table('client_master')

    op.drop_index(op.f('ix_service_required_document_service_id'), table_name='service_required_document')
    op.drop_table('service_required_document')

    op.drop_index(op.f('ix_service_master_status'), table_name='service_master')
    op.drop_index(op.f('ix_service_master_service_name'), table_name='service_master')
    op.drop_index(op.f('ix_service_master_service_code'), table_name='service_master')
    op.drop_index(op.f('ix_service_master_category'), table_name='service_master')
    op.drop_table('service_master')
