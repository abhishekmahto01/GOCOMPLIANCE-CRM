"""Integration and unit tests for Sales Order to Operations Handoff Engine."""
import uuid
from datetime import date, datetime, timezone
from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.client import ClientMaster
from app.models.company import Company
from app.models.department import Department
from app.models.designation import Designation
from app.models.operation_application import (
    ApplicationActivityLog,
    ApplicationAssignmentHistory,
    ApplicationDocument,
    OperationApplication,
)
from app.models.sales_order import SalesOrder
from app.models.service import ServiceMaster, ServiceRequiredDocument
from app.models.user import User
from app.schemas.sales_order import SalesOrderCreate
from app.services.operation_service import (
    ApplicationNotFoundError,
    InvalidStatusTransitionError,
    assign_task,
    reassign_task,
    update_application_status,
    update_document_status,
)
from app.services.sales_service import (
    confirm_sales_order,
    create_sales_order,
    generate_application_number,
    generate_sales_order_number,
)


@pytest.fixture
def test_setup_entities(db_session: Session):
    """Create basic company, department, designation, users, and service for tests."""
    company = Company(
        company_code="TESTCORP",
        company_name="Test Corporation",
        employee_code_prefix="TC",
        status="ACTIVE",
    )
    db_session.add(company)
    db_session.flush()

    dept_sales = Department(
        company_id=company.company_id,
        department_code="SALES",
        department_name="Sales Department",
        status="ACTIVE",
    )
    dept_ops = Department(
        company_id=company.company_id,
        department_code="OPERATIONS",
        department_name="Operations Department",
        status="ACTIVE",
    )
    db_session.add_all([dept_sales, dept_ops])
    db_session.flush()

    desig = Designation(
        company_id=company.company_id,
        designation_code="EXECUTIVE",
        designation_name="Executive",
        level_rank=1,
        status="ACTIVE",
    )
    db_session.add(desig)
    db_session.flush()

    sales_user = User(
        employee_code="TC0001",
        company_id=company.company_id,
        department_id=dept_sales.department_id,
        designation_id=desig.designation_id,
        first_name="Amit",
        last_name="Sharma",
        official_email="amit.sharma@testcorp.com",
        mobile_number="+919876543210",
        date_of_joining=date(2024, 1, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
    )
    ops_manager = User(
        employee_code="TC0002",
        company_id=company.company_id,
        department_id=dept_ops.department_id,
        designation_id=desig.designation_id,
        first_name="Pooja",
        last_name="Singh",
        official_email="pooja.singh@testcorp.com",
        mobile_number="+919876543211",
        date_of_joining=date(2024, 1, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        is_reporting_manager=True,
    )
    ops_user1 = User(
        employee_code="TC0003",
        company_id=company.company_id,
        department_id=dept_ops.department_id,
        designation_id=desig.designation_id,
        manager_user_id=ops_manager.user_id,
        first_name="Deepak",
        last_name="Thapliya",
        official_email="deepak.t@testcorp.com",
        mobile_number="+919876543212",
        date_of_joining=date(2024, 1, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
    )
    ops_user2 = User(
        employee_code="TC0004",
        company_id=company.company_id,
        department_id=dept_ops.department_id,
        designation_id=desig.designation_id,
        manager_user_id=ops_manager.user_id,
        first_name="Sonal",
        last_name="Gupta",
        official_email="sonal.g@testcorp.com",
        mobile_number="+919876543213",
        date_of_joining=date(2024, 1, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
    )
    db_session.add_all([sales_user, ops_manager, ops_user1, ops_user2])
    db_session.flush()

    service = ServiceMaster(
        service_code="TRADE_LICENSE",
        service_name="Trade License",
        category="LICENCE",
        base_price=Decimal("15000.00"),
        govt_fee=Decimal("2500.00"),
        standard_turnaround_days=15,
        status="ACTIVE",
    )
    db_session.add(service)
    db_session.flush()

    doc1 = ServiceRequiredDocument(
        service_id=service.service_id,
        document_code="PAN",
        document_name="PAN Card",
        is_mandatory=True,
        display_order=10,
    )
    doc2 = ServiceRequiredDocument(
        service_id=service.service_id,
        document_code="AADHAAR",
        document_name="Aadhaar Card",
        is_mandatory=True,
        display_order=20,
    )
    doc3 = ServiceRequiredDocument(
        service_id=service.service_id,
        document_code="RENT_AGREEMENT",
        document_name="Rent Agreement",
        is_mandatory=True,
        display_order=30,
    )
    db_session.add_all([doc1, doc2, doc3])
    db_session.flush()

    client = ClientMaster(
        company_id=company.company_id,
        client_name="Sharma Enterprises",
        entity_type="Private Limited",
        contact_person="Raj Sharma",
        contact_email="raj@sharmaenterprises.com",
        contact_phone="+919811122233",
        created_by_user_id=sales_user.user_id,
        status="ACTIVE",
    )
    db_session.add(client)
    db_session.flush()

    return {
        "company": company,
        "sales_user": sales_user,
        "ops_manager": ops_manager,
        "ops_user1": ops_user1,
        "ops_user2": ops_user2,
        "service": service,
        "client": client,
    }


def test_sales_order_number_and_app_number_format(db_session: Session):
    """Verify formatted sequential number generation."""
    curr_year = date.today().year
    so_num = generate_sales_order_number(db_session)
    assert so_num.startswith(f"SO-{curr_year}-")
    assert len(so_num) >= 12

    app_num = generate_application_number(db_session)
    assert app_num.startswith(f"AP-{curr_year}-")
    assert len(app_num) >= 12


def test_create_sales_order_balance_calculation(db_session: Session, test_setup_entities):
    """Verify sales order creation with automatic balance amount calculation."""
    entities = test_setup_entities
    dto = SalesOrderCreate(
        company_id=entities["company"].company_id,
        client_id=entities["client"].client_id,
        service_id=entities["service"].service_id,
        salesperson_user_id=entities["sales_user"].user_id,
        lead_source="WEBSITE",
        order_date=date(2025, 3, 15),
        order_value=Decimal("60000.00"),
        amount_received=Decimal("40000.00"),
        payment_status="PARTIALLY_PAID",
        notes="Urgent trade license processing",
    )

    order = create_sales_order(db_session, dto, entities["sales_user"])
    assert order.order_id is not None
    assert order.order_number.startswith("SO-2025-")
    assert order.balance_amount == Decimal("20000.00")
    assert order.confirmation_status == "DRAFT"
    assert order.application is None


def test_confirm_sales_order_automatic_handoff(db_session: Session, test_setup_entities):
    """Verify confirmed order automatically creates an unassigned operations application with documents."""
    entities = test_setup_entities
    dto = SalesOrderCreate(
        company_id=entities["company"].company_id,
        client_id=entities["client"].client_id,
        service_id=entities["service"].service_id,
        salesperson_user_id=entities["sales_user"].user_id,
        order_date=date(2025, 3, 20),
        order_value=Decimal("50000.00"),
        amount_received=Decimal("50000.00"),
        payment_status="FULLY_PAID",
    )
    order = create_sales_order(db_session, dto, entities["sales_user"])

    # Confirm order
    result = confirm_sales_order(db_session, order.order_id, entities["sales_user"])
    assert result.confirmation_status == "CONFIRMED"
    assert result.application_id is not None
    assert result.application_number.startswith("AP-2025-")
    assert result.application_status == "ASSIGNED"
    assert result.assigned_to_user_id == entities["ops_manager"].user_id
    assert result.documents_count == 3

    # Check database state
    app = db_session.get(OperationApplication, result.application_id)
    assert app is not None
    assert app.sales_order_id == order.order_id
    assert app.client_id == entities["client"].client_id
    assert app.service_id == entities["service"].service_id
    assert app.priority == "MEDIUM"

    # Check documents copied
    docs = db_session.query(ApplicationDocument).filter(ApplicationDocument.application_id == app.application_id).all()
    assert len(docs) == 3
    doc_codes = {d.document_code for d in docs}
    assert doc_codes == {"PAN", "AADHAAR", "RENT_AGREEMENT"}
    assert all(d.status == "PENDING" for d in docs)

    # Check initial activity log
    activity = db_session.query(ApplicationActivityLog).filter(ApplicationActivityLog.application_id == app.application_id).all()
    assert len(activity) == 1
    assert activity[0].action_type == "ASSIGNMENT_CHANGE"
    assert "Pooja Singh" in activity[0].new_value


def test_confirm_sales_order_idempotency(db_session: Session, test_setup_entities):
    """Verify repeated confirmation calls return the same application without duplicating."""
    entities = test_setup_entities
    dto = SalesOrderCreate(
        company_id=entities["company"].company_id,
        client_id=entities["client"].client_id,
        service_id=entities["service"].service_id,
        salesperson_user_id=entities["sales_user"].user_id,
        order_date=date(2025, 3, 20),
        order_value=Decimal("30000.00"),
        amount_received=Decimal("15000.00"),
        payment_status="PARTIALLY_PAID",
    )
    order = create_sales_order(db_session, dto, entities["sales_user"])

    res1 = confirm_sales_order(db_session, order.order_id, entities["sales_user"])
    res2 = confirm_sales_order(db_session, order.order_id, entities["sales_user"])

    assert res1.application_id == res2.application_id
    assert res1.application_number == res2.application_number

    # Ensure strictly 1 application exists in DB
    apps = db_session.query(OperationApplication).filter(OperationApplication.sales_order_id == order.order_id).all()
    assert len(apps) == 1


def test_operation_application_unique_constraint(db_session: Session, test_setup_entities):
    """Verify database-level unique constraint prevents multiple applications for same order."""
    entities = test_setup_entities
    dto = SalesOrderCreate(
        company_id=entities["company"].company_id,
        client_id=entities["client"].client_id,
        service_id=entities["service"].service_id,
        salesperson_user_id=entities["sales_user"].user_id,
        order_date=date(2025, 3, 20),
        order_value=Decimal("30000.00"),
    )
    order = create_sales_order(db_session, dto, entities["sales_user"])
    confirm_sales_order(db_session, order.order_id, entities["sales_user"])

    # Attempt manual insert of duplicate application for same sales_order_id
    dup_app = OperationApplication(
        application_number="AP-2025-9999",
        sales_order_id=order.order_id,
        company_id=order.company_id,
        client_id=order.client_id,
        service_id=order.service_id,
        application_status="UNASSIGNED",
    )
    db_session.add(dup_app)
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()


def test_task_assignment_and_reassignment_history(db_session: Session, test_setup_entities):
    """Verify assignment and reassignment correctly update assignee and log history."""
    entities = test_setup_entities
    dto = SalesOrderCreate(
        company_id=entities["company"].company_id,
        client_id=entities["client"].client_id,
        service_id=entities["service"].service_id,
        salesperson_user_id=entities["sales_user"].user_id,
        order_date=date(2025, 3, 22),
        order_value=Decimal("45000.00"),
        auto_confirm=True,
    )
    order = create_sales_order(db_session, dto, entities["sales_user"])
    app = order.application
    assert app.application_status == "ASSIGNED"
    assert app.assigned_to_user_id == entities["ops_manager"].user_id

    # 1. Reassign task to Deepak (ops_user1)
    assigned_app = reassign_task(
        db_session,
        application_id=app.application_id,
        new_assignee_user_id=entities["ops_user1"].user_id,
        reason="Assigned to specialist Deepak",
        reassigned_by=entities["ops_manager"],
        priority="HIGH",
        target_due_date=date(2025, 3, 28),
    )

    assert assigned_app.assigned_to_user_id == entities["ops_user1"].user_id
    assert assigned_app.assigned_by_user_id == entities["ops_manager"].user_id
    assert assigned_app.application_status == "ASSIGNED"
    assert assigned_app.priority == "HIGH"
    assert assigned_app.target_due_date == date(2025, 3, 28)

    # Check history record
    hist1 = db_session.query(ApplicationAssignmentHistory).filter(
        ApplicationAssignmentHistory.application_id == app.application_id
    ).all()
    assert len(hist1) == 2
    assert hist1[1].previous_assignee_user_id == entities["ops_manager"].user_id
    assert hist1[1].new_assignee_user_id == entities["ops_user1"].user_id
    assert hist1[1].assigned_by_user_id == entities["ops_manager"].user_id

    # 2. Reassign task to Sonal (ops_user2)
    reassigned_app = reassign_task(
        db_session,
        application_id=app.application_id,
        new_assignee_user_id=entities["ops_user2"].user_id,
        reason="Deepak on medical leave, workload rebalancing",
        reassigned_by=entities["ops_manager"],
        priority="URGENT",
    )

    assert reassigned_app.assigned_to_user_id == entities["ops_user2"].user_id
    assert reassigned_app.priority == "URGENT"

    # Check updated history
    hist2 = db_session.query(ApplicationAssignmentHistory).filter(
        ApplicationAssignmentHistory.application_id == app.application_id
    ).order_by(ApplicationAssignmentHistory.assigned_at.asc()).all()
    assert len(hist2) == 3
    assert hist2[2].previous_assignee_user_id == entities["ops_user1"].user_id
    assert hist2[2].new_assignee_user_id == entities["ops_user2"].user_id
    assert "medical leave" in hist2[2].reason


def test_status_transitions_valid_and_invalid(db_session: Session, test_setup_entities):
    """Verify application status lifecycle transitions and rejection of invalid jumps."""
    entities = test_setup_entities
    dto = SalesOrderCreate(
        company_id=entities["company"].company_id,
        client_id=entities["client"].client_id,
        service_id=entities["service"].service_id,
        salesperson_user_id=entities["sales_user"].user_id,
        order_date=date(2025, 3, 25),
        order_value=Decimal("60000.00"),
        auto_confirm=True,
    )
    order = create_sales_order(db_session, dto, entities["sales_user"])
    app = order.application
    assert app.application_status == "ASSIGNED"

    # Invalid jump from ASSIGNED to SUBMITTED should fail
    with pytest.raises(InvalidStatusTransitionError):
        update_application_status(db_session, app.application_id, "SUBMITTED", entities["ops_manager"])

    # Valid step 1: ASSIGNED -> IN_PROGRESS
    update_application_status(db_session, app.application_id, "IN_PROGRESS", entities["ops_user1"])
    assert app.application_status == "IN_PROGRESS"

    # Valid step 2: IN_PROGRESS -> PENDING_DOCUMENTS
    update_application_status(db_session, app.application_id, "PENDING_DOCUMENTS", entities["ops_user1"])
    assert app.application_status == "PENDING_DOCUMENTS"

    # Valid step 3: PENDING_DOCUMENTS -> READY_FOR_SUBMISSION
    update_application_status(db_session, app.application_id, "READY_FOR_SUBMISSION", entities["ops_user1"])
    assert app.application_status == "READY_FOR_SUBMISSION"

    # Valid step 4: READY_FOR_SUBMISSION -> SUBMITTED
    update_application_status(db_session, app.application_id, "SUBMITTED", entities["ops_user1"], "Filed with MC portal ref 12345")
    assert app.application_status == "SUBMITTED"

    # Valid step 5: SUBMITTED -> APPROVED
    update_application_status(db_session, app.application_id, "APPROVED", entities["ops_manager"], "License certificate received")
    assert app.application_status == "APPROVED"
    assert app.completion_date == date.today()


def test_document_verification_workflow(db_session: Session, test_setup_entities):
    """Verify document verification status updates and activity logging."""
    entities = test_setup_entities
    dto = SalesOrderCreate(
        company_id=entities["company"].company_id,
        client_id=entities["client"].client_id,
        service_id=entities["service"].service_id,
        salesperson_user_id=entities["sales_user"].user_id,
        order_date=date(2025, 3, 26),
        order_value=Decimal("40000.00"),
        auto_confirm=True,
    )
    order = create_sales_order(db_session, dto, entities["sales_user"])
    app = order.application

    docs = db_session.query(ApplicationDocument).filter(ApplicationDocument.application_id == app.application_id).all()
    pan_doc = next(d for d in docs if d.document_code == "PAN")

    # Mark as VERIFIED
    updated_pan = update_document_status(
        db_session,
        app_doc_id=pan_doc.app_doc_id,
        new_status="VERIFIED",
        actor=entities["ops_user1"],
    )
    assert updated_pan.status == "VERIFIED"
    assert updated_pan.verified_by_user_id == entities["ops_user1"].user_id
    assert updated_pan.verified_at is not None

    # Mark another doc as REJECTED
    rent_doc = next(d for d in docs if d.document_code == "RENT_AGREEMENT")
    updated_rent = update_document_status(
        db_session,
        app_doc_id=rent_doc.app_doc_id,
        new_status="REJECTED",
        actor=entities["ops_user1"],
        rejection_reason="Rent agreement expired on 31 Dec 2024. Please submit renewed deed.",
    )
    assert updated_rent.status == "REJECTED"
    assert "expired" in updated_rent.rejection_reason
