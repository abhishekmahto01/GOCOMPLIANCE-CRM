"""Automated integration tests verifying Operations task visibility and reassignment integrity.

Test Case 1 (Visibility after Reassignment):
    Operations Lead (Mansi) reassigns a task from themselves to an Operations member ->
    Verify task remains visible in Operations Lead's task list endpoint, dashboard, and task detail.

Test Case 2 (Member Boundary Check):
    Verify that the newly assigned member can see the task, but unrelated members in other
    departments or non-assigned peers cannot.

Test Case 3 (Department Integrity):
    Verify that updating/reassigning a task does not mutate or nullify department_id or
    other core relational fields (company_id, client_id, service_id, sales_order_id),
    and creates zero duplicate task records.
"""
import uuid
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.models.client import ClientMaster
from app.models.company import Company
from app.models.department import Department
from app.models.designation import Designation
from app.models.module import Module
from app.models.operation_application import (
    ApplicationActivityLog,
    ApplicationAssignmentHistory,
    ApplicationDocument,
    OperationApplication,
)
from app.models.operations_coordinator_config import OperationsCoordinatorConfig
from app.models.sales_order import SalesOrder
from app.models.service import ServiceMaster, ServiceRequiredDocument
from app.models.user import User
from app.models.user_module_permission import UserModulePermission
from app.services.permissions import grant_or_update_permission


def auth_header(user: User) -> dict:
    """Generate bearer authorization header for a test user."""
    token = create_access_token(
        user_id=user.user_id,
        token_version=user.token_version,
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def visibility_fixture(db_session: Session):
    """Seed companies, departments, designations, users, services, modules, and permissions."""
    # 1. Company
    company = Company(
        company_code="GC_VIS",
        company_name="GoCompliance Visibility Corp",
        employee_code_prefix="GV",
        status="ACTIVE",
    )
    db_session.add(company)
    db_session.flush()

    # 2. Departments
    dept_ops = Department(
        department_code="OPERATIONS",
        department_name="Operations Department",
        status="ACTIVE",
    )
    dept_sales = Department(
        department_code="SALES",
        department_name="Sales Department",
        status="ACTIVE",
    )
    db_session.add_all([dept_ops, dept_sales])
    db_session.flush()

    # 3. Designations
    desig_lead = Designation(
        designation_code="OPERATIONS_LEAD",
        designation_name="Operations Lead",
        level_rank=40,
        is_managerial=True,
        status="ACTIVE",
    )
    desig_exec = Designation(
        designation_code="OPERATIONS_EXECUTIVE",
        designation_name="Operations Executive",
        level_rank=10,
        is_managerial=False,
        status="ACTIVE",
    )
    desig_sales_rep = Designation(
        designation_code="SALES_EXECUTIVE",
        designation_name="Sales Executive",
        level_rank=10,
        is_managerial=False,
        status="ACTIVE",
    )
    db_session.add_all([desig_lead, desig_exec, desig_sales_rep])
    db_session.flush()

    # 4. Users
    # Mansi: Operations Lead / Coordinator
    mansi_lead = User(
        employee_code="GV0001",
        company_id=company.company_id,
        department_id=dept_ops.department_id,
        designation_id=desig_lead.designation_id,
        first_name="Mansi",
        last_name="Singhal",
        official_email="mansi.lead@testcorp.com",
        mobile_number="+919876500001",
        date_of_joining=date(2024, 1, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        must_change_password=False,
    )
    # Deepak: Operations Executive (new assignee)
    deepak_exec = User(
        employee_code="GV0002",
        company_id=company.company_id,
        department_id=dept_ops.department_id,
        designation_id=desig_exec.designation_id,
        first_name="Deepak",
        last_name="Kumar",
        official_email="deepak.ops@testcorp.com",
        mobile_number="+919876500002",
        date_of_joining=date(2024, 1, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        must_change_password=False,
    )
    # Peer: Unrelated peer in Operations (not assigned)
    peer_exec = User(
        employee_code="GV0003",
        company_id=company.company_id,
        department_id=dept_ops.department_id,
        designation_id=desig_exec.designation_id,
        first_name="Peer",
        last_name="Sharma",
        official_email="peer.ops@testcorp.com",
        mobile_number="+919876500003",
        date_of_joining=date(2024, 1, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        must_change_password=False,
    )
    # Sales Rep: Unrelated employee in Sales department
    sales_rep = User(
        employee_code="GV0004",
        company_id=company.company_id,
        department_id=dept_sales.department_id,
        designation_id=desig_sales_rep.designation_id,
        first_name="Rohan",
        last_name="Sales",
        official_email="rohan.sales@testcorp.com",
        mobile_number="+919876500004",
        date_of_joining=date(2024, 1, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        must_change_password=False,
    )
    db_session.add_all([mansi_lead, deepak_exec, peer_exec, sales_rep])
    db_session.flush()

    # Coordinator config mapping company to Mansi
    coord_cfg = OperationsCoordinatorConfig(
        company_id=company.company_id,
        coordinator_user_id=mansi_lead.user_id,
        updated_by_user_id=mansi_lead.user_id,
    )
    db_session.add(coord_cfg)
    db_session.flush()

    # 5. Modules
    mod_ops = Module(
        module_code="OPERATIONS",
        module_name="Operations Module",
        display_order=20,
        status="ACTIVE",
    )
    mod_sales = Module(
        module_code="SALES",
        module_name="Sales Module",
        display_order=10,
        status="ACTIVE",
    )
    db_session.add_all([mod_ops, mod_sales])
    db_session.flush()

    # Permissions
    # Mansi: Operations Lead with view, edit, assign, reassign
    grant_or_update_permission(
        session=db_session,
        user_id=mansi_lead.user_id,
        module_id=mod_ops.module_id,
        can_view=True,
        can_create=True,
        can_edit=True,
        can_delete=False,
        can_assign=True,
        can_reassign=True,
        can_export=True,
        data_scope="SELF",  # Test with SELF to ensure Lead logic overrides restrictive SELF scope
        granted_by_user_id=mansi_lead.user_id,
        is_bootstrap=True,
    )
    # Deepak: Operations Executive with view, edit, SELF scope
    grant_or_update_permission(
        session=db_session,
        user_id=deepak_exec.user_id,
        module_id=mod_ops.module_id,
        can_view=True,
        can_create=False,
        can_edit=True,
        can_delete=False,
        can_assign=False,
        can_reassign=False,
        can_export=True,
        data_scope="SELF",
        granted_by_user_id=mansi_lead.user_id,
        is_bootstrap=True,
    )
    # Peer: Operations Executive with view, edit, SELF scope (non-assigned peer)
    grant_or_update_permission(
        session=db_session,
        user_id=peer_exec.user_id,
        module_id=mod_ops.module_id,
        can_view=True,
        can_create=False,
        can_edit=True,
        can_delete=False,
        can_assign=False,
        can_reassign=False,
        can_export=True,
        data_scope="SELF",
        granted_by_user_id=mansi_lead.user_id,
        is_bootstrap=True,
    )
    # Sales Rep: Sales only (NO Operations module permission)
    grant_or_update_permission(
        session=db_session,
        user_id=sales_rep.user_id,
        module_id=mod_sales.module_id,
        can_view=True,
        can_create=True,
        can_edit=True,
        can_delete=False,
        can_assign=False,
        can_reassign=False,
        can_export=True,
        data_scope="SELF",
        granted_by_user_id=mansi_lead.user_id,
        is_bootstrap=True,
    )

    # 6. Service & Client
    service = ServiceMaster(
        service_code="SRV_FSSAI_VIS",
        service_name="FSSAI Food License Registration",
        category="LICENCE",
        base_price=Decimal("15000.00"),
        govt_fee=Decimal("5000.00"),
        status="ACTIVE",
    )
    client = ClientMaster(
        company_id=company.company_id,
        client_name="Gourmet Global Foods Pvt Ltd",
        contact_person="Sunil Verma",
        contact_email="sunil@gourmetglobal.com",
        contact_phone="+919811223344",
        city="Mumbai",
        state="Maharashtra",
        created_by_user_id=mansi_lead.user_id,
        status="ACTIVE",
    )
    db_session.add_all([service, client])
    db_session.flush()

    # 7. Sales Order & Operation Application initially assigned to Mansi
    sales_order = SalesOrder(
        order_number="SO-VIS-0001",
        company_id=company.company_id,
        client_id=client.client_id,
        service_id=service.service_id,
        salesperson_user_id=sales_rep.user_id,
        order_date=date.today(),
        order_value=Decimal("20000.00"),
        amount_received=Decimal("10000.00"),
        balance_amount=Decimal("10000.00"),
        govt_fees=Decimal("5000.00"),
        incidental_cost=Decimal("0.00"),
        lead_source="WEBSITE",
        payment_status="PARTIALLY_PAID",
        confirmation_status="CONFIRMED",
    )
    db_session.add(sales_order)
    db_session.flush()

    now_utc = datetime.now(timezone.utc)
    app = OperationApplication(
        application_number="AP-VIS-0001",
        sales_order_id=sales_order.order_id,
        company_id=company.company_id,
        client_id=client.client_id,
        service_id=service.service_id,
        department_id=dept_ops.department_id,
        assigned_to_user_id=mansi_lead.user_id,
        assigned_by_user_id=mansi_lead.user_id,
        assigned_at=now_utc,
        priority="HIGH",
        application_status="IN_PROGRESS",
        target_due_date=date.today() + timedelta(days=10),
        assignment_notes="Initial task assigned to Mansi for client dossier preparation",
    )
    db_session.add(app)
    db_session.flush()

    hist = ApplicationAssignmentHistory(
        application_id=app.application_id,
        assigned_by_user_id=mansi_lead.user_id,
        previous_assignee_user_id=None,
        new_assignee_user_id=mansi_lead.user_id,
        reason="Initial assignment to Operations Lead",
        assigned_at=now_utc,
    )
    db_session.add(hist)
    db_session.commit()

    return {
        "company": company,
        "dept_ops": dept_ops,
        "mansi_lead": mansi_lead,
        "deepak_exec": deepak_exec,
        "peer_exec": peer_exec,
        "sales_rep": sales_rep,
        "app": app,
        "sales_order": sales_order,
    }


def test_case_1_visibility_after_reassignment(client: TestClient, db_session: Session, visibility_fixture: dict):
    """Test Case 1: Operations Lead (Mansi) reassigns task to Operations member ->
    Verify task remains continuously visible in Operations Lead's task list endpoint,
    Operations Dashboard, and task details.
    """
    f = visibility_fixture
    mansi = f["mansi_lead"]
    deepak = f["deepak_exec"]
    app = f["app"]

    mansi_headers = auth_header(mansi)

    # 1. Before reassignment: verify task is visible to Mansi
    initial_tasks = client.get("/api/operations/tasks", headers=mansi_headers)
    assert initial_tasks.status_code == 200
    initial_items = initial_tasks.json()["items"]
    assert any(t["application_id"] == str(app.application_id) for t in initial_items)

    # 2. Mansi reassigns the task from herself to Deepak
    reassign_payload = {
        "new_assignee_user_id": str(deepak.user_id),
        "reason": "Reassigning to Deepak for statutory documentation and physical filing.",
        "priority": "HIGH",
        "target_due_date": (date.today() + timedelta(days=7)).isoformat(),
    }
    reassign_res = client.post(
        f"/api/operations/tasks/{app.application_id}/reassign",
        json=reassign_payload,
        headers=mansi_headers,
    )
    assert reassign_res.status_code == 200
    reassign_data = reassign_res.json()
    assert reassign_data["assigned_to_user_id"] == str(deepak.user_id)
    assert reassign_data["assigned_to_name"] == f"{deepak.first_name} {deepak.last_name}"

    # 3. CRITICAL VERIFICATION: Task REMAINS visible in Mansi's task list endpoint
    lead_tasks_res = client.get("/api/operations/tasks", headers=mansi_headers)
    assert lead_tasks_res.status_code == 200
    lead_task_items = lead_tasks_res.json()["items"]
    matching_in_list = [t for t in lead_task_items if t["application_id"] == str(app.application_id)]
    assert len(matching_in_list) == 1, "Task vanished from Operations Lead's task list after reassignment!"
    assert matching_in_list[0]["assigned_to_user_id"] == str(deepak.user_id)

    # 4. CRITICAL VERIFICATION: Task REMAINS visible on Mansi's Operations Dashboard
    lead_dash_res = client.get("/api/operations/dashboard", headers=mansi_headers)
    assert lead_dash_res.status_code == 200
    dash_data = lead_dash_res.json()
    assert dash_data["kpis"]["total_applications"] >= 1
    # Check priority queue or recent applications on dashboard includes the reassigned task
    dash_app_ids = [t["application_id"] for t in dash_data.get("recent_applications", [])] + [
        t["application_id"] for t in dash_data.get("priority_queue", [])
    ]
    assert str(app.application_id) in dash_app_ids, "Task vanished from Operations Lead's dashboard after reassignment!"

    # 5. CRITICAL VERIFICATION: Mansi can retrieve task details with full assignment history
    detail_res = client.get(f"/api/operations/tasks/{app.application_id}", headers=mansi_headers)
    assert detail_res.status_code == 200
    detail_data = detail_res.json()
    assert detail_data["application_id"] == str(app.application_id)
    assert detail_data["assigned_to_user_id"] == str(deepak.user_id)
    assert len(detail_data["assignment_history"]) >= 2
    assert detail_data["assignment_history"][0]["new_assignee_user_id"] == str(deepak.user_id)
    assert detail_data["assignment_history"][0]["reason"] == reassign_payload["reason"]

    # 6. Verify "My Assigned Tasks" reflects that it's no longer assigned to Mansi
    mansi_my_tasks = client.get("/api/operations/tasks/my-tasks", headers=mansi_headers)
    assert mansi_my_tasks.status_code == 200
    my_task_items = mansi_my_tasks.json()["items"]
    assert not any(t["application_id"] == str(app.application_id) for t in my_task_items), \
        "Task should not be in Mansi's personal 'My Assigned Tasks' queue once reassigned to Deepak."


def test_case_2_member_boundary_check(client: TestClient, db_session: Session, visibility_fixture: dict):
    """Test Case 2 (Member Boundary Check):
    Verify that the newly assigned member (Deepak) can see the task, but unrelated
    members in other departments (Sales) or non-assigned peers (Peer) cannot.
    """
    f = visibility_fixture
    mansi = f["mansi_lead"]
    deepak = f["deepak_exec"]
    peer = f["peer_exec"]
    sales_rep = f["sales_rep"]
    app = f["app"]

    mansi_headers = auth_header(mansi)
    deepak_headers = auth_header(deepak)
    peer_headers = auth_header(peer)
    sales_headers = auth_header(sales_rep)

    # 1. Reassign task to Deepak
    client.post(
        f"/api/operations/tasks/{app.application_id}/reassign",
        json={
            "new_assignee_user_id": str(deepak.user_id),
            "reason": "Transferring ownership to Deepak for execution",
        },
        headers=mansi_headers,
    )

    # 2. Check Newly Assigned Member (Deepak):
    # - Deepak sees it in "My Assigned Tasks"
    deepak_my_tasks = client.get("/api/operations/tasks/my-tasks", headers=deepak_headers)
    assert deepak_my_tasks.status_code == 200
    assert any(t["application_id"] == str(app.application_id) for t in deepak_my_tasks.json()["items"])

    # - Deepak sees it in task list endpoint
    deepak_all_tasks = client.get("/api/operations/tasks", headers=deepak_headers)
    assert deepak_all_tasks.status_code == 200
    assert any(t["application_id"] == str(app.application_id) for t in deepak_all_tasks.json()["items"])

    # - Deepak can view task detail
    deepak_detail = client.get(f"/api/operations/tasks/{app.application_id}", headers=deepak_headers)
    assert deepak_detail.status_code == 200
    assert deepak_detail.json()["assigned_to_user_id"] == str(deepak.user_id)

    # 3. Check Unrelated Member in Other Department (Sales Rep):
    # - Sales rep has no OPERATIONS permission -> strictly denied 403 Forbidden
    sales_tasks_res = client.get("/api/operations/tasks", headers=sales_headers)
    assert sales_tasks_res.status_code == 403

    sales_dash_res = client.get("/api/operations/dashboard", headers=sales_headers)
    assert sales_dash_res.status_code == 403

    # 4. Check Non-Assigned Peer in Operations (Peer with SELF scope):
    # - Peer checks "My Assigned Tasks" -> does NOT see Deepak's task
    peer_my_tasks = client.get("/api/operations/tasks/my-tasks", headers=peer_headers)
    assert peer_my_tasks.status_code == 200
    assert not any(t["application_id"] == str(app.application_id) for t in peer_my_tasks.json()["items"])

    # - Peer checks task list endpoint -> does NOT see Deepak's task
    peer_all_tasks = client.get("/api/operations/tasks", headers=peer_headers)
    assert peer_all_tasks.status_code == 200
    assert not any(t["application_id"] == str(app.application_id) for t in peer_all_tasks.json()["items"])

    # - Peer attempts to access Deepak's task detail -> strictly denied 403 Forbidden
    peer_detail_res = client.get(f"/api/operations/tasks/{app.application_id}", headers=peer_headers)
    assert peer_detail_res.status_code == 403


def test_case_3_department_and_relational_integrity(client: TestClient, db_session: Session, visibility_fixture: dict):
    """Test Case 3 (Department Integrity):
    Verify that updating/reassigning a task does not mutate or nullify department_id
    or other core relational fields, and creates zero duplicate task records.
    """
    f = visibility_fixture
    mansi = f["mansi_lead"]
    deepak = f["deepak_exec"]
    app = f["app"]
    dept_ops = f["dept_ops"]
    company = f["company"]
    order = f["sales_order"]

    mansi_headers = auth_header(mansi)

    # Record baseline state
    initial_app_count = db_session.query(OperationApplication).count()
    orig_dept_id = str(dept_ops.department_id)
    orig_company_id = str(company.company_id)
    orig_client_id = str(app.client_id)
    orig_service_id = str(app.service_id)
    orig_order_id = str(order.order_id)
    orig_app_number = app.application_number

    # 1. Reassign task via POST
    reassign_res = client.post(
        f"/api/operations/tasks/{app.application_id}/reassign",
        json={
            "new_assignee_user_id": str(deepak.user_id),
            "reason": "Department integrity verification reassignment",
            "priority": "URGENT",
        },
        headers=mansi_headers,
    )
    assert reassign_res.status_code == 200
    res_data = reassign_res.json()

    # Verify relational fields in response
    assert str(res_data["department_id"]) == orig_dept_id
    assert res_data["department_name"] == "Operations Department"
    assert str(res_data["company_id"]) == orig_company_id
    assert str(res_data["client_id"]) == orig_client_id
    assert str(res_data["service_id"]) == orig_service_id
    assert str(res_data["sales_order_id"]) == orig_order_id
    assert res_data["application_number"] == orig_app_number

    # 2. Update task via PATCH endpoint
    patch_res = client.patch(
        f"/api/operations/tasks/{app.application_id}",
        json={
            "priority": "HIGH",
            "notes": "Updated instructions without mutating department",
        },
        headers=mansi_headers,
    )
    assert patch_res.status_code == 200
    patch_data = patch_res.json()
    assert str(patch_data["department_id"]) == orig_dept_id
    assert str(patch_data["company_id"]) == orig_company_id
    assert str(patch_data["client_id"]) == orig_client_id
    assert str(patch_data["service_id"]) == orig_service_id
    assert str(patch_data["sales_order_id"]) == orig_order_id

    # 3. Direct Database Query Verification: Ensure database state matches
    db_session.expire_all()
    db_app = db_session.get(OperationApplication, app.application_id)
    assert db_app is not None
    assert str(db_app.department_id) == orig_dept_id, "department_id was corrupted or nullified!"
    assert str(db_app.company_id) == orig_company_id, "company_id was mutated!"
    assert str(db_app.client_id) == orig_client_id, "client_id was mutated!"
    assert str(db_app.service_id) == orig_service_id, "service_id was mutated!"
    assert str(db_app.sales_order_id) == orig_order_id, "sales_order_id was mutated!"
    assert db_app.application_number == orig_app_number

    # 4. Zero Data Loss & Zero Duplication Check: Total task count must remain identical
    final_app_count = db_session.query(OperationApplication).count()
    assert final_app_count == initial_app_count, f"Duplicate task records created! Expected {initial_app_count}, got {final_app_count}"
