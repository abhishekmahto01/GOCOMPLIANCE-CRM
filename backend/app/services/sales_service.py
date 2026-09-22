"""Sales service layer handling orders, sequential IDs, calculation, and operations handoff."""
import uuid
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.client import ClientMaster
from app.models.company import Company
from app.models.operation_application import (
    ApplicationActivityLog,
    ApplicationAssignmentHistory,
    ApplicationDocument,
    OperationApplication,
)
from app.models.sales_order import SalesOrder
from app.models.service import ServiceMaster, ServiceRequiredDocument
from app.models.user import User
from app.schemas.sales_order import SalesOrderConfirmResponse, SalesOrderCreate
from app.services import permissions


class SalesOrderNotFoundError(Exception):
    """Raised when requested sales order is not found."""
    pass


class SalesOrderPermissionError(Exception):
    """Raised when user is not authorized to access or modify sales order."""
    pass


def generate_sales_order_number(session: Session, order_date: Optional[date] = None) -> str:
    """Generate a unique sequential Sales Order ID (e.g. SO-2025-0001) for the given year."""
    target_year = (order_date or date.today()).year
    prefix = f"SO-{target_year}-"

    # Query highest sequence number for this year
    stmt = (
        select(SalesOrder.order_number)
        .where(SalesOrder.order_number.like(f"{prefix}%"))
        .order_by(SalesOrder.order_number.desc())
        .limit(1)
    )
    latest = session.execute(stmt).scalar_one_or_none()

    if latest:
        try:
            seq_part = latest[len(prefix):]
            next_num = int(seq_part) + 1
        except ValueError:
            # Fallback count
            next_num = session.query(SalesOrder).filter(SalesOrder.order_number.like(f"{prefix}%")).count() + 1
    else:
        next_num = 1

    return f"{prefix}{next_num:04d}"


def generate_application_number(session: Session, app_date: Optional[date] = None) -> str:
    """Generate a unique sequential Application ID (e.g. AP-2025-0001) for the given year."""
    target_year = (app_date or date.today()).year
    prefix = f"AP-{target_year}-"

    stmt = (
        select(OperationApplication.application_number)
        .where(OperationApplication.application_number.like(f"{prefix}%"))
        .order_by(OperationApplication.application_number.desc())
        .limit(1)
    )
    latest = session.execute(stmt).scalar_one_or_none()

    if latest:
        try:
            seq_part = latest[len(prefix):]
            next_num = int(seq_part) + 1
        except ValueError:
            next_num = session.query(OperationApplication).filter(OperationApplication.application_number.like(f"{prefix}%")).count() + 1
    else:
        next_num = 1

    return f"{prefix}{next_num:04d}"


def create_sales_order(
    session: Session,
    data: SalesOrderCreate,
    current_user: User,
) -> SalesOrder:
    """Create a new sales order with computed balance and optional auto-confirmation."""
    # Validate company exists
    company = session.get(Company, data.company_id)
    if not company or company.status != "ACTIVE":
        raise ValueError(f"Active company with ID '{data.company_id}' not found.")

    # Validate client exists and belongs to company
    client = session.get(ClientMaster, data.client_id)
    if not client or client.status != "ACTIVE":
        raise ValueError(f"Active client with ID '{data.client_id}' not found.")
    if client.company_id != data.company_id:
        raise ValueError("Client does not belong to specified company.")

    # Validate service exists
    service = session.get(ServiceMaster, data.service_id)
    if not service or service.status != "ACTIVE":
        raise ValueError(f"Active service with ID '{data.service_id}' not found.")

    # Validate salesperson exists
    salesperson = session.get(User, data.salesperson_user_id)
    if not salesperson or salesperson.account_status != "ACTIVE":
        raise ValueError(f"Active salesperson with ID '{data.salesperson_user_id}' not found.")

    order_num = generate_sales_order_number(session, data.order_date)
    val = Decimal(str(data.order_value))
    rcvd = Decimal(str(data.amount_received))
    bal = max(Decimal("0.00"), val - rcvd)

    order = SalesOrder(
        order_number=order_num,
        company_id=data.company_id,
        client_id=data.client_id,
        service_id=data.service_id,
        salesperson_user_id=data.salesperson_user_id,
        lead_source=data.lead_source,
        order_date=data.order_date,
        order_value=val,
        amount_received=rcvd,
        balance_amount=bal,
        payment_status=data.payment_status,
        confirmation_status="DRAFT",
        notes=data.notes,
    )
    session.add(order)
    session.flush()

    if data.auto_confirm:
        confirm_sales_order(session, order.order_id, current_user)

    return order


def confirm_sales_order(
    session: Session,
    order_id: uuid.UUID,
    current_user: User,
) -> SalesOrderConfirmResponse:
    """Confirm a sales order and execute idempotent transactional handoff to Operations."""
    order = session.get(SalesOrder, order_id)
    if not order:
        raise SalesOrderNotFoundError(f"Sales order with ID '{order_id}' not found.")

    # Check if already confirmed (idempotency check)
    existing_app = session.execute(
        select(OperationApplication).where(OperationApplication.sales_order_id == order_id)
    ).scalar_one_or_none()

    if existing_app and order.confirmation_status == "CONFIRMED":
        # Already confirmed; return existing state idempotently
        doc_count = session.query(ApplicationDocument).filter(
            ApplicationDocument.application_id == existing_app.application_id
        ).count()
        return SalesOrderConfirmResponse(
            order_id=order.order_id,
            order_number=order.order_number,
            confirmation_status=order.confirmation_status,
            confirmed_at=order.confirmed_at or datetime.now(timezone.utc),
            application_id=existing_app.application_id,
            application_number=existing_app.application_number,
            application_status=existing_app.application_status,
            assigned_to_user_id=existing_app.assigned_to_user_id,
            documents_count=doc_count,
        )

    # Transition order state
    now_utc = datetime.now(timezone.utc)
    order.confirmation_status = "CONFIRMED"
    order.confirmed_at = now_utc

    # Generate application number
    app_num = generate_application_number(session, order.order_date)

    # Create Operation Application in UNASSIGNED state
    new_app = OperationApplication(
        application_number=app_num,
        sales_order_id=order.order_id,
        company_id=order.company_id,
        client_id=order.client_id,
        service_id=order.service_id,
        assigned_to_user_id=None,
        assigned_by_user_id=None,
        assigned_at=None,
        priority="MEDIUM",
        application_status="UNASSIGNED",
        target_due_date=None,
        assignment_notes=order.notes,
    )
    session.add(new_app)
    session.flush()

    # Copy required documents from service master
    required_docs = session.execute(
        select(ServiceRequiredDocument)
        .where(ServiceRequiredDocument.service_id == order.service_id)
        .order_by(ServiceRequiredDocument.display_order.asc())
    ).scalars().all()

    doc_count = 0
    for r_doc in required_docs:
        app_doc = ApplicationDocument(
            application_id=new_app.application_id,
            document_code=r_doc.document_code,
            document_name=r_doc.document_name,
            is_mandatory=r_doc.is_mandatory,
            status="PENDING",
        )
        session.add(app_doc)
        doc_count += 1

    # Create initial entry in application activity log
    activity = ApplicationActivityLog(
        application_id=new_app.application_id,
        actor_user_id=current_user.user_id,
        action_type="STATUS_CHANGE",
        old_value="NONE",
        new_value="UNASSIGNED",
        comment=f"Order '{order.order_number}' confirmed and handed over from Sales.",
    )
    session.add(activity)
    session.flush()

    return SalesOrderConfirmResponse(
        order_id=order.order_id,
        order_number=order.order_number,
        confirmation_status=order.confirmation_status,
        confirmed_at=order.confirmed_at,
        application_id=new_app.application_id,
        application_number=new_app.application_number,
        application_status=new_app.application_status,
        assigned_to_user_id=None,
        documents_count=doc_count,
    )
