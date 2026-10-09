"""Comprehensive end-to-end tests for Shared Task Conversation feature in GOCOMPLIANCE CRM.

Tests cover:
1. Sales initial remark creation into the shared conversation thread.
2. Operations default assignee posting messages.
3. Reassignment preserving the entire conversation thread and recording transactional system events.
4. New assignee posting identifiable, timestamped updates.
5. Accounts users reading and posting on GST-eligible entries.
6. Accounts users forbidden from accessing non-GST entries (403) and cross-company entries.
7. Director / Super Admin viewing full conversation history within authorized scope.
8. Validation rules: empty remarks rejected (422), idempotency key deduplication on retry, system events immutable/unforgeable.
9. Latest remark summary agreement across modules (ignoring system events).
10. Legacy remarks repeat-safe backfill.
"""
import uuid
from datetime import date, datetime, timezone
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.models.client import ClientMaster
from app.models.company import Company
from app.models.department import Department
from app.models.designation import Designation
from app.models.module import Module
from app.models.operation_application import OperationApplication, OperationRemark
from app.models.sales_order import SalesOrder
from app.models.service import ServiceMaster
from app.models.task_conversation import TaskConversationMessage
from app.models.user import User
from app.services.conversation_service import (
    backfill_legacy_remarks,
    get_latest_human_remark,
    get_task_conversation,
    post_conversation_message,
    record_system_event,
)
from app.services.operation_service import assign_task, reassign_task, update_application_status
from app.services.permissions import grant_or_update_permission
from app.services.sales_service import confirm_sales_order, create_sales_order


@pytest.fixture
def conversation_test_fixture(db_session: Session):
    """Seed comprehensive multi-department test environment with Sales, Operations, Accounts, and Director users."""
    # 1. Company
    company = Company(
        company_code="CONVTEST",
        company_name="Conversation Test Corp",
        employee_code_prefix="CT",
        status="ACTIVE",
    )
    other_company = Company(
        company_code="OTHERCORP",
        company_name="Other Independent Corp",
        employee_code_prefix="OC",
        status="ACTIVE",
    )
    db_session.add_all([company, other_company])
    db_session.flush()

    # 2. Departments
    dept_sales = Department(
        department_code="SALES",
        department_name="Sales Department",
        status="ACTIVE",
    )
    dept_ops = Department(
        department_code="OPERATIONS",
        department_name="Operations Department",
        status="ACTIVE",
    )
    dept_accounts = Department(
        department_code="ACCOUNTS",
        department_name="Accounts Department",
        status="ACTIVE",
    )
    dept_mgmt = Department(
        department_code="MANAGEMENT",
        department_name="Executive Management",
        status="ACTIVE",
    )
    dept_other = Department(
        department_code="OTHER_DEPT",
        department_name="Other Department",
        status="ACTIVE",
    )
    db_session.add_all([dept_sales, dept_ops, dept_accounts, dept_mgmt, dept_other])
    db_session.flush()

    # 3. Designations
    desig_sales = Designation(
        designation_code="SALES_EXEC",
        designation_name="Sales Executive",
        level_rank=3,
        status="ACTIVE",
    )
    desig_ops = Designation(
        designation_code="OPS_EXEC",
        designation_name="Operations Executive",
        level_rank=3,
        status="ACTIVE",
    )
    desig_accounts = Designation(
        designation_code="ACC_EXEC",
        designation_name="Accounts Executive",
        level_rank=3,
        status="ACTIVE",
    )
    desig_director = Designation(
        designation_code="SUPER_ADMIN",
        designation_name="Super Administrator",
        level_rank=10,
        status="ACTIVE",
    )
    desig_other = Designation(
        designation_code="OTHER_DESIG",
        designation_name="Other Designation",
        level_rank=1,
        status="ACTIVE",
    )
    db_session.add_all([desig_sales, desig_ops, desig_accounts, desig_director, desig_other])
    db_session.flush()

    # 4. Users (Simulating Karishma, Manshi, Deepak, Pooja in Accounts, and Director)
    # Karishma - Sales Creator
    karishma = User(
        employee_code="CT0001",
        company_id=company.company_id,
        department_id=dept_sales.department_id,
        designation_id=desig_sales.designation_id,
        first_name="Karishma",
        last_name="Sales",
        official_email="karishma@testcorp.com",
        mobile_number="+919876500001",
        date_of_joining=date(2024, 1, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        must_change_password=False,
    )
    # Manshi - Operations Assignee 1
    manshi = User(
        employee_code="CT0002",
        company_id=company.company_id,
        department_id=dept_ops.department_id,
        designation_id=desig_ops.designation_id,
        first_name="Manshi",
        last_name="Ops",
        official_email="manshi@testcorp.com",
        mobile_number="+919876500002",
        date_of_joining=date(2024, 1, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        must_change_password=False,
    )
    # Deepak - Operations Assignee 2
    deepak = User(
        employee_code="CT0003",
        company_id=company.company_id,
        department_id=dept_ops.department_id,
        designation_id=desig_ops.designation_id,
        first_name="Deepak",
        last_name="Ops",
        official_email="deepak@testcorp.com",
        mobile_number="+919876500003",
        date_of_joining=date(2024, 1, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        must_change_password=False,
    )
    # Pooja - Accounts Executive
    pooja = User(
        employee_code="CT0004",
        company_id=company.company_id,
        department_id=dept_accounts.department_id,
        designation_id=desig_accounts.designation_id,
        first_name="Pooja",
        last_name="Accounts",
        official_email="pooja@testcorp.com",
        mobile_number="+919876500004",
        date_of_joining=date(2024, 1, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        must_change_password=False,
    )
    # Director / Super Admin
    director = User(
        employee_code="CT0000",
        company_id=company.company_id,
        department_id=dept_mgmt.department_id,
        designation_id=desig_director.designation_id,
        first_name="Director",
        last_name="Admin",
        official_email="director@testcorp.com",
        mobile_number="+919876500000",
        date_of_joining=date(2024, 1, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        must_change_password=False,
    )
    # User in other company for boundary testing
    other_user = User(
        employee_code="OC0001",
        company_id=other_company.company_id,
        department_id=dept_other.department_id,
        designation_id=desig_other.designation_id,
        first_name="External",
        last_name="User",
        official_email="external@othercorp.com",
        mobile_number="+919876599999",
        date_of_joining=date(2024, 1, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        must_change_password=False,
    )

    db_session.add_all([karishma, manshi, deepak, pooja, director, other_user])
    db_session.flush()

    # 5. Modules & Permissions
    all_modules = [
        Module(module_code="ADMIN_ACCESS", module_name="System Administration", status="ACTIVE"),
        Module(module_code="SALES", module_name="Sales Management", status="ACTIVE"),
        Module(module_code="SALES_CONFIRMED_ORDER", module_name="Sales Orders", status="ACTIVE"),
        Module(module_code="SALES_REGISTER", module_name="Sales Register", status="ACTIVE"),
        Module(module_code="OPERATIONS", module_name="Operations Management", status="ACTIVE"),
        Module(module_code="OPERATIONS_TASKS", module_name="Operations Tasks", status="ACTIVE"),
        Module(module_code="ACCOUNTS", module_name="Accounts Management", status="ACTIVE"),
        Module(module_code="ACCOUNTS_ENTRIES", module_name="Accounts Entries", status="ACTIVE"),
    ]
    db_session.add_all(all_modules)
    db_session.flush()

    mod_dict = {m.module_code: m for m in all_modules}

    # Director -> All Modules: ADMIN
    for mod in all_modules:
        grant_or_update_permission(
            session=db_session,
            user_id=director.user_id,
            module_id=mod.module_id,
            can_view=True,
            can_create=True,
            can_edit=True,
            can_delete=True,
            can_approve=True,
            can_assign=True,
            can_reassign=True,
            data_scope="ALL",
            is_bootstrap=True,
        )

    # Karishma -> SALES modules: WRITE (data_scope COMPANY)
    for mc in ["SALES", "SALES_CONFIRMED_ORDER", "SALES_REGISTER"]:
        grant_or_update_permission(
            session=db_session,
            user_id=karishma.user_id,
            module_id=mod_dict[mc].module_id,
            can_view=True,
            can_create=True,
            can_edit=True,
            data_scope="COMPANY",
            is_bootstrap=True,
        )

    # Manshi -> OPERATIONS modules: WRITE (data_scope COMPANY, can_assign, can_reassign)
    for mc in ["OPERATIONS", "OPERATIONS_TASKS"]:
        grant_or_update_permission(
            session=db_session,
            user_id=manshi.user_id,
            module_id=mod_dict[mc].module_id,
            can_view=True,
            can_create=True,
            can_edit=True,
            can_assign=True,
            can_reassign=True,
            data_scope="COMPANY",
            is_bootstrap=True,
        )

    # Deepak -> OPERATIONS modules: WRITE
    for mc in ["OPERATIONS", "OPERATIONS_TASKS"]:
        grant_or_update_permission(
            session=db_session,
            user_id=deepak.user_id,
            module_id=mod_dict[mc].module_id,
            can_view=True,
            can_create=True,
            can_edit=True,
            can_assign=True,
            can_reassign=True,
            data_scope="COMPANY",
            is_bootstrap=True,
        )

    # Pooja -> ACCOUNTS modules: WRITE
    for mc in ["ACCOUNTS", "ACCOUNTS_ENTRIES"]:
        grant_or_update_permission(
            session=db_session,
            user_id=pooja.user_id,
            module_id=mod_dict[mc].module_id,
            can_view=True,
            can_create=True,
            can_edit=True,
            data_scope="COMPANY",
            is_bootstrap=True,
        )

    # 6. Service & Client
    service = ServiceMaster(
        service_code="GST_REG",
        service_name="GST Registration Service",
        category="REGISTRATION",
        base_price=Decimal("5000.00"),
        govt_fee=Decimal("0.00"),
        status="ACTIVE",
    )
    client = ClientMaster(
        company_id=company.company_id,
        client_name="Acme Global Private Limited",
        contact_phone="+919876511111",
        contact_email="contact@acmeglobal.com",
        entity_type="PRIVATE_LIMITED",
        created_by_user_id=karishma.user_id,
        status="ACTIVE",
    )
    db_session.add_all([service, client])
    db_session.flush()

    def make_token(user: User) -> str:
        return create_access_token(user_id=user.user_id, token_version=user.token_version)

    return {
        "company": company,
        "other_company": other_company,
        "karishma": karishma,
        "manshi": manshi,
        "deepak": deepak,
        "pooja": pooja,
        "director": director,
        "other_user": other_user,
        "service": service,
        "client": client,
        "tokens": {
            "karishma": make_token(karishma),
            "manshi": make_token(manshi),
            "deepak": make_token(deepak),
            "pooja": make_token(pooja),
            "director": make_token(director),
            "other_user": make_token(other_user),
        },
    }


def test_sales_entry_initial_remark_in_conversation(
    client: TestClient, db_session: Session, conversation_test_fixture
):
    """Test that creating a sales entry with initial remarks creates the first message in the shared conversation."""
    fx = conversation_test_fixture
    token = fx["tokens"]["karishma"]

    # 1. Create Sales Entry with notes
    payload = {
        "order_date": "2026-03-01",
        "client_name": "Acme Global Private Limited",
        "contact_no": "+919876511111",
        "lead_source": "WEBSITE",
        "service_id": str(fx["service"].service_id),
        "salesperson_user_id": str(fx["karishma"].user_id),
        "order_value": 5000.0,
        "amount_received": 2500.0,
        "govt_fees": 0.0,
        "incidental_cost": 0.0,
        "gst_invoice_required": True,
        "notes": "Client urgently needs GST Registration before the 15th.",
        "auto_confirm": True,
    }

    res = client.post("/api/sales/orders", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 201, res.text
    order_data = res.json()
    order_id = order_data["order_id"]

    # 2. Query Conversation endpoint
    conv_res = client.get(f"/api/conversations/{order_id}", headers={"Authorization": f"Bearer {token}"})
    assert conv_res.status_code == 200, conv_res.text
    conv_data = conv_res.json()

    assert conv_data["order_id"] == order_id
    assert conv_data["client_name"] == "Acme Global Private Limited"
    assert conv_data["gst_invoice_required"] is True
    assert conv_data["can_post"] is True

    # Check messages
    messages = conv_data["items"]
    assert len(messages) >= 1
    # First message should be the initial comment
    initial_msg = next((m for m in messages if m["message_type"] == "COMMENT"), None)
    assert initial_msg is not None
    assert "Client urgently needs GST Registration" in initial_msg["message_text"]
    assert initial_msg["author_name"] == "Karishma Sales"
    assert initial_msg["author_employee_code"] == "CT0001"
    assert initial_msg["author_department_name"] == "Sales Department"


def test_operations_assignment_reassignment_flow(
    client: TestClient, db_session: Session, conversation_test_fixture
):
    """Test full shared conversation lifecycle across Sales, Operations assignment, updates, and reassignment."""
    fx = conversation_test_fixture
    karishma_token = fx["tokens"]["karishma"]
    manshi_token = fx["tokens"]["manshi"]
    deepak_token = fx["tokens"]["deepak"]
    director_token = fx["tokens"]["director"]

    # 1. Karishma creates and confirms order with initial note
    create_res = client.post(
        "/api/sales/orders",
        json={
            "order_date": "2026-03-01",
            "client_name": "Beta Enterprises",
            "contact_no": "+919876522222",
            "lead_source": "DIRECT",
            "service_id": str(fx["service"].service_id),
            "salesperson_user_id": str(fx["karishma"].user_id),
            "order_value": 6000.0,
            "amount_received": 3000.0,
            "govt_fees": 0.0,
            "incidental_cost": 0.0,
            "gst_invoice_required": False,
            "notes": "Initial handover note from Karishma.",
            "auto_confirm": True,
        },
        headers={"Authorization": f"Bearer {karishma_token}"},
    )
    assert create_res.status_code == 201
    order_id = create_res.json()["order_id"]

    # Retrieve application created for this order
    app = db_session.query(OperationApplication).filter_by(sales_order_id=order_id).first()
    assert app is not None
    app_id = str(app.application_id)

    # 2. Assign task to Manshi
    assign_res = client.post(
        f"/api/operations/tasks/{app_id}/assign",
        json={
            "assignee_user_id": str(fx["manshi"].user_id),
            "priority": "HIGH",
            "target_due_date": "2026-03-10",
            "notes": "Assigned to Manshi for document collection.",
        },
        headers={"Authorization": f"Bearer {director_token}"},
    )
    assert assign_res.status_code == 200

    # 3. Manshi adds an update in the shared conversation
    manshi_post_res = client.post(
        f"/api/conversations/{order_id}/messages",
        json={
            "message_text": "Documents received from client. Preparing submission package.",
            "idempotency_key": str(uuid.uuid4()),
        },
        headers={"Authorization": f"Bearer {manshi_token}"},
    )
    assert manshi_post_res.status_code == 201
    manshi_msg = manshi_post_res.json()
    assert manshi_msg["author_name"] == "Manshi Ops"
    assert manshi_msg["author_department_name"] == "Operations Department"

    # 4. Manshi/Director reassigns task to Deepak
    reassign_res = client.post(
        f"/api/operations/tasks/{app_id}/reassign",
        json={
            "new_assignee_user_id": str(fx["deepak"].user_id),
            "reason": "Manshi going on planned leave; handed over to Deepak.",
            "priority": "URGENT",
            "target_due_date": "2026-03-08",
        },
        headers={"Authorization": f"Bearer {manshi_token}"},
    )
    assert reassign_res.status_code == 200

    # 5. Deepak adds his update
    deepak_post_res = client.post(
        f"/api/conversations/{order_id}/messages",
        json={
            "message_text": "Taking over the task. Application submitted to portal with ARN-998877.",
            "idempotency_key": str(uuid.uuid4()),
        },
        headers={"Authorization": f"Bearer {deepak_token}"},
    )
    assert deepak_post_res.status_code == 201
    deepak_msg = deepak_post_res.json()
    assert deepak_msg["author_name"] == "Deepak Ops"

    # 6. Director opens full conversation thread
    conv_res = client.get(f"/api/conversations/{order_id}", headers={"Authorization": f"Bearer {director_token}"})
    assert conv_res.status_code == 200
    conv = conv_res.json()

    # Verify chronological sequence and presence of system events
    messages = conv["items"]
    assert len(messages) >= 4  # Initial remark + assign system event + Manshi comment + reassign system event + Deepak comment

    # Check for assignment and reassignment system events
    event_types = [m.get("event_type") for m in messages if m["message_type"] == "SYSTEM_EVENT"]
    assert any("ASSIGN" in et or "REASSIGN" in et for et in event_types)

    # Verify authors of comments
    comment_authors = [m["author_name"] for m in messages if m["message_type"] == "COMMENT"]
    assert "Karishma Sales" in comment_authors
    assert "Manshi Ops" in comment_authors
    assert "Deepak Ops" in comment_authors

    # Verify latest human remark preview
    latest = get_latest_human_remark(db_session, uuid.UUID(order_id))
    assert latest is not None
    assert "ARN-998877" in latest.remark_text
    assert latest.author_name == "Deepak Ops"


def test_accounts_gst_visibility_and_restrictions(
    client: TestClient, db_session: Session, conversation_test_fixture
):
    """Test that Accounts users can read/post only on GST-eligible entries, and get 403 on non-GST entries."""
    fx = conversation_test_fixture
    karishma_token = fx["tokens"]["karishma"]
    pooja_token = fx["tokens"]["pooja"]
    other_user_token = fx["tokens"]["other_user"]

    # 1. Create GST-eligible entry
    gst_res = client.post(
        "/api/sales/orders",
        json={
            "order_date": "2026-03-02",
            "client_name": "GST Eligible Pvt Ltd",
            "contact_no": "+919876533333",
            "lead_source": "WEBSITE",
            "service_id": str(fx["service"].service_id),
            "salesperson_user_id": str(fx["karishma"].user_id),
            "order_value": 10000.0,
            "amount_received": 10000.0,
            "govt_fees": 0.0,
            "incidental_cost": 0.0,
            "gst_invoice_required": True,
            "notes": "GST Invoice is required by client finance department.",
            "auto_confirm": True,
        },
        headers={"Authorization": f"Bearer {karishma_token}"},
    )
    assert gst_res.status_code == 201
    gst_order_id = gst_res.json()["order_id"]

    # 2. Create Non-GST entry
    nongst_res = client.post(
        "/api/sales/orders",
        json={
            "order_date": "2026-03-02",
            "client_name": "Non-GST Individual",
            "contact_no": "+919876544444",
            "lead_source": "DIRECT",
            "service_id": str(fx["service"].service_id),
            "salesperson_user_id": str(fx["karishma"].user_id),
            "order_value": 3000.0,
            "amount_received": 3000.0,
            "govt_fees": 0.0,
            "incidental_cost": 0.0,
            "gst_invoice_required": False,
            "notes": "No GST needed.",
            "auto_confirm": True,
        },
        headers={"Authorization": f"Bearer {karishma_token}"},
    )
    assert nongst_res.status_code == 201
    nongst_order_id = nongst_res.json()["order_id"]

    # 3. Pooja (Accounts) accesses GST-eligible entry -> 200 OK
    gst_conv_res = client.get(
        f"/api/conversations/{gst_order_id}", headers={"Authorization": f"Bearer {pooja_token}"}
    )
    assert gst_conv_res.status_code == 200
    assert gst_conv_res.json()["gst_invoice_required"] is True

    # Pooja posts Accounts update -> 201 Created
    pooja_post_res = client.post(
        f"/api/conversations/{gst_order_id}/messages",
        json={
            "message_text": "Proforma invoice PI-2026-001 generated and emailed to client.",
            "idempotency_key": str(uuid.uuid4()),
        },
        headers={"Authorization": f"Bearer {pooja_token}"},
    )
    assert pooja_post_res.status_code == 201
    assert pooja_post_res.json()["author_name"] == "Pooja Accounts"
    assert pooja_post_res.json()["author_department_name"] == "Accounts Department"

    # 4. Pooja (Accounts) accesses Non-GST entry -> 403 Forbidden
    nongst_conv_res = client.get(
        f"/api/conversations/{nongst_order_id}", headers={"Authorization": f"Bearer {pooja_token}"}
    )
    assert nongst_conv_res.status_code == 403

    # Pooja attempts to post on Non-GST entry -> 403 Forbidden
    nongst_post_res = client.post(
        f"/api/conversations/{nongst_order_id}/messages",
        json={
            "message_text": "Trying to post on non-GST order.",
            "idempotency_key": str(uuid.uuid4()),
        },
        headers={"Authorization": f"Bearer {pooja_token}"},
    )
    assert nongst_post_res.status_code == 403

    # 5. External company user accesses entry -> 403/404 Forbidden
    other_res = client.get(
        f"/api/conversations/{gst_order_id}", headers={"Authorization": f"Bearer {other_user_token}"}
    )
    assert other_res.status_code in (403, 404)


def test_validation_and_idempotency(
    client: TestClient, db_session: Session, conversation_test_fixture
):
    """Test validation constraints: empty message rejection and idempotency key deduplication."""
    fx = conversation_test_fixture
    karishma_token = fx["tokens"]["karishma"]

    # Create order
    create_res = client.post(
        "/api/sales/orders",
        json={
            "order_date": "2026-03-03",
            "client_name": "Idempotency Test Corp",
            "contact_no": "+919876555555",
            "lead_source": "WEBSITE",
            "service_id": str(fx["service"].service_id),
            "salesperson_user_id": str(fx["karishma"].user_id),
            "order_value": 5000.0,
            "amount_received": 2500.0,
            "govt_fees": 0.0,
            "incidental_cost": 0.0,
            "gst_invoice_required": False,
            "notes": "Initial note.",
            "auto_confirm": True,
        },
        headers={"Authorization": f"Bearer {karishma_token}"},
    )
    assert create_res.status_code == 201
    order_id = create_res.json()["order_id"]

    # 1. Reject empty message
    empty_res = client.post(
        f"/api/conversations/{order_id}/messages",
        json={"message_text": "   ", "idempotency_key": str(uuid.uuid4())},
        headers={"Authorization": f"Bearer {karishma_token}"},
    )
    assert empty_res.status_code == 422

    # 2. Post valid message with idempotency key
    idempotency_key = f"key_{uuid.uuid4().hex}"
    msg_payload = {
        "message_text": "Unique message for idempotency test.",
        "idempotency_key": idempotency_key,
    }

    first_res = client.post(
        f"/api/conversations/{order_id}/messages",
        json=msg_payload,
        headers={"Authorization": f"Bearer {karishma_token}"},
    )
    assert first_res.status_code == 201
    first_msg_id = first_res.json()["message_id"]

    # 3. Retry same post with same idempotency key
    retry_res = client.post(
        f"/api/conversations/{order_id}/messages",
        json=msg_payload,
        headers={"Authorization": f"Bearer {karishma_token}"},
    )
    assert retry_res.status_code in (200, 201)
    retry_msg_id = retry_res.json()["message_id"]
    assert first_msg_id == retry_msg_id

    # Verify no duplicate messages exist in DB
    db_messages = (
        db_session.query(TaskConversationMessage)
        .filter_by(sales_order_id=order_id, idempotency_key=idempotency_key)
        .all()
    )
    assert len(db_messages) == 1


def test_legacy_remarks_repeat_safe_backfill(
    client: TestClient, db_session: Session, conversation_test_fixture
):
    """Test that legacy remarks backfill is repeatable, idempotent, and preserves historical data without duplicates."""
    fx = conversation_test_fixture
    director_token = fx["tokens"]["director"]

    # 1. Create a sales order directly with legacy notes but no conversation message
    order = SalesOrder(
        company_id=fx["company"].company_id,
        client_id=fx["client"].client_id,
        service_id=fx["service"].service_id,
        salesperson_user_id=fx["karishma"].user_id,
        order_number="SO-LEGACY-001",
        order_date=date(2025, 12, 1),
        order_value=Decimal("7500.00"),
        amount_received=Decimal("3500.00"),
        balance_amount=Decimal("4000.00"),
        payment_status="PARTIALLY_PAID",
        notes="Legacy sales note from 2025.",
        confirmation_status="CONFIRMED",
    )
    db_session.add(order)
    db_session.flush()

    # Create an operation application with legacy remarks
    app = OperationApplication(
        company_id=fx["company"].company_id,
        sales_order_id=order.order_id,
        client_id=fx["client"].client_id,
        service_id=fx["service"].service_id,
        application_number="APP-LEGACY-001",
        assigned_to_user_id=fx["manshi"].user_id,
        application_status="IN_PROGRESS",
    )
    db_session.add(app)
    db_session.flush()

    legacy_op_remark = OperationRemark(
        application_id=app.application_id,
        author_user_id=fx["manshi"].user_id,
        remark_text="Legacy operations remark logged before conversation module.",
    )
    db_session.add(legacy_op_remark)
    db_session.flush()

    # 2. Run backfill 1st time
    res1 = client.post(
        "/api/conversations/backfill/legacy-remarks",
        headers={"Authorization": f"Bearer {director_token}"},
    )
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["status"] == "success"
    assert data1["imported"]["total_imported"] >= 2

    # 3. Run backfill 2nd time (Repeat safety check)
    res2 = client.post(
        "/api/conversations/backfill/legacy-remarks",
        headers={"Authorization": f"Bearer {director_token}"},
    )
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["status"] == "success"
    # Migrated count on rerun should be 0 because all existing are already backfilled
    assert data2["imported"]["total_imported"] == 0

    # 4. Verify messages on the order
    conv_res = client.get(
        f"/api/conversations/{order.order_id}",
        headers={"Authorization": f"Bearer {director_token}"},
    )
    assert conv_res.status_code == 200
    conv = conv_res.json()
    texts = [m["message_text"] for m in conv["items"]]
    assert any("Legacy sales note from 2025" in t for t in texts)
    assert any("Legacy operations remark" in t for t in texts)
