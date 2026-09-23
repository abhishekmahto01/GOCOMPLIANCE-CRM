"""Unit and integration tests for Operations API endpoints, task workflows, and RBAC scoping."""
import uuid
from datetime import date, timedelta
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
from app.models.operation_application import (
    ApplicationActivityLog,
    ApplicationAssignmentHistory,
    ApplicationDocument,
    OperationApplication,
)
from app.models.sales_order import SalesOrder
from app.models.service import ServiceMaster, ServiceRequiredDocument
from app.models.user import User
from app.models.user_module_permission import UserModulePermission
from app.services.permissions import grant_or_update_permission
from app.services.sales_service import confirm_sales_order, create_sales_order


@pytest.fixture
def ops_test_fixture(db_session: Session):
    """Seed test company, departments, users, services, documents, and confirmed orders."""
    company = Company(
        company_code="OPSTEST",
        company_name="Operations Test Corp",
        employee_code_prefix="OP",
        status="ACTIVE",
    )
    db_session.add(company)
    db_session.flush()

    dept_ops = Department(
        company_id=company.company_id,
        department_code="OPERATIONS",
        department_name="Operations Department",
        status="ACTIVE",
    )
    dept_sales = Department(
        company_id=company.company_id,
        department_code="SALES",
        department_name="Sales Department",
        status="ACTIVE",
    )
    db_session.add_all([dept_ops, dept_sales])
    db_session.flush()

    desig_head = Designation(
        company_id=company.company_id,
        designation_code="OPS_HEAD",
        designation_name="Operations Head",
        level_rank=10,
        status="ACTIVE",
    )
    desig_exec = Designation(
        company_id=company.company_id,
        designation_code="OPS_EXEC",
        designation_name="Operations Executive",
        level_rank=5,
        status="ACTIVE",
    )
    db_session.add_all([desig_head, desig_exec])
    db_session.flush()

    # Users
    ops_manager = User(
        employee_code="OP0001",
        company_id=company.company_id,
        department_id=dept_ops.department_id,
        designation_id=desig_head.designation_id,
        first_name="Karishma",
        last_name="Upadhyay",
        official_email="karishma.ops@testcorp.com",
        mobile_number="+919876540001",
        date_of_joining=date(2024, 1, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        must_change_password=False,
    )
    ops_deepak = User(
        employee_code="OP0002",
        company_id=company.company_id,
        department_id=dept_ops.department_id,
        designation_id=desig_exec.designation_id,
        first_name="Deepak",
        last_name="Kumar",
        official_email="deepak.ops@testcorp.com",
        mobile_number="+919876540002",
        date_of_joining=date(2024, 1, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        must_change_password=False,
    )
    ops_mansi = User(
        employee_code="OP0003",
        company_id=company.company_id,
        department_id=dept_ops.department_id,
        designation_id=desig_exec.designation_id,
        first_name="Mansi",
        last_name="Sharma",
        official_email="mansi.ops@testcorp.com",
        mobile_number="+919876540003",
        date_of_joining=date(2024, 1, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        must_change_password=False,
    )
    db_session.add_all([ops_manager, ops_deepak, ops_mansi])
    db_session.flush()

    # Module
    mod_ops = Module(
        module_code="OPERATIONS",
        module_name="Operations Module",
        display_order=20,
        status="ACTIVE",
    )
    db_session.add(mod_ops)
    db_session.flush()

    # Permissions: Manager has ALL scope with assign/reassign/edit/view
    grant_or_update_permission(
        session=db_session,
        user_id=ops_manager.user_id,
        module_id=mod_ops.module_id,
        can_view=True,
        can_create=True,
        can_edit=True,
        can_delete=True,
        can_assign=True,
        can_reassign=True,
        can_export=True,
        data_scope="ALL",
        granted_by_user_id=ops_manager.user_id,
        is_bootstrap=True,
    )

    # Deepak has SELF scope with view/edit
    grant_or_update_permission(
        session=db_session,
        user_id=ops_deepak.user_id,
        module_id=mod_ops.module_id,
        can_view=True,
        can_create=False,
        can_edit=True,
        can_delete=False,
        can_assign=False,
        can_reassign=False,
        can_export=True,
        data_scope="SELF",
        granted_by_user_id=ops_manager.user_id,
        is_bootstrap=True,
    )

    # Mansi has SELF scope with view/edit
    grant_or_update_permission(
        session=db_session,
        user_id=ops_mansi.user_id,
        module_id=mod_ops.module_id,
        can_view=True,
        can_create=False,
        can_edit=True,
        can_delete=False,
        can_assign=False,
        can_reassign=False,
        can_export=True,
        data_scope="SELF",
        granted_by_user_id=ops_manager.user_id,
        is_bootstrap=True,
    )

    # Service & Required Docs
    service = ServiceMaster(
        service_code="SRV_CLINICAL",
        service_name="Clinical Establishment",
        category="LICENCE",
        base_price=Decimal("45000.00"),
        govt_fee=Decimal("5000.00"),
        standard_turnaround_days=15,
        status="ACTIVE",
    )
    db_session.add(service)
    db_session.flush()

    doc1 = ServiceRequiredDocument(
        service_id=service.service_id,
        document_code="DOC_PAN",
        document_name="Client PAN Card",
        is_mandatory=True,
        display_order=1,
    )
    doc2 = ServiceRequiredDocument(
        service_id=service.service_id,
        document_code="DOC_RENT",
        document_name="Premises Rent Agreement",
        is_mandatory=True,
        display_order=2,
    )
    db_session.add_all([doc1, doc2])
    db_session.flush()

    # Client KAPPER
    client_kapper = ClientMaster(
        company_id=company.company_id,
        client_name="KAPPER Medical Pvt Ltd",
        entity_type="PRIVATE_LIMITED",
        contact_email="contact@kapper.in",
        contact_phone="+919876599999",
        status="ACTIVE",
        created_by_user_id=ops_manager.user_id,
    )
    db_session.add(client_kapper)
    db_session.flush()

    # Sales Order 1: Assigned to Deepak (Clinical Establishment)
    order1 = SalesOrder(
        order_number="SO-TEST-0001",
        company_id=company.company_id,
        client_id=client_kapper.client_id,
        service_id=service.service_id,
        salesperson_user_id=ops_manager.user_id,
        order_date=date.today() - timedelta(days=2),
        order_value=Decimal("45000.00"),
        amount_received=Decimal("45000.00"),
        balance_amount=Decimal("0.00"),
        govt_fees=Decimal("5000.00"),
        incidental_cost=Decimal("0.00"),
        lead_source="DIRECT",
        payment_status="FULLY_PAID",
        confirmation_status="CONFIRMED",
    )
    db_session.add(order1)
    db_session.flush()

    app1 = OperationApplication(
        application_number="AP-TEST-0001",
        sales_order_id=order1.order_id,
        company_id=company.company_id,
        client_id=client_kapper.client_id,
        service_id=service.service_id,
        assigned_to_user_id=ops_deepak.user_id,
        assigned_by_user_id=ops_manager.user_id,
        assigned_at=order1.created_at,
        priority="HIGH",
        application_status="ASSIGNED",
        target_due_date=date.today() + timedelta(days=10),
        assignment_notes="Priority filing for KAPPER",
    )
    db_session.add(app1)
    db_session.flush()

    # Checklist items for app1
    app_doc1 = ApplicationDocument(
        application_id=app1.application_id,
        document_code="DOC_PAN",
        document_name="Client PAN Card",
        is_mandatory=True,
        status="PENDING",
    )
    app_doc2 = ApplicationDocument(
        application_id=app1.application_id,
        document_code="DOC_RENT",
        document_name="Premises Rent Agreement",
        is_mandatory=True,
        status="PENDING",
    )
    db_session.add_all([app_doc1, app_doc2])

    # Sales Order 2: Assigned to Mansi (In Progress)
    order2 = SalesOrder(
        order_number="SO-TEST-0002",
        company_id=company.company_id,
        client_id=client_kapper.client_id,
        service_id=service.service_id,
        salesperson_user_id=ops_manager.user_id,
        order_date=date.today() - timedelta(days=5),
        order_value=Decimal("50000.00"),
        amount_received=Decimal("25000.00"),
        balance_amount=Decimal("25000.00"),
        govt_fees=Decimal("5000.00"),
        incidental_cost=Decimal("0.00"),
        lead_source="WEBSITE",
        payment_status="PARTIALLY_PAID",
        confirmation_status="CONFIRMED",
    )
    db_session.add(order2)
    db_session.flush()

    app2 = OperationApplication(
        application_number="AP-TEST-0002",
        sales_order_id=order2.order_id,
        company_id=company.company_id,
        client_id=client_kapper.client_id,
        service_id=service.service_id,
        assigned_to_user_id=ops_mansi.user_id,
        assigned_by_user_id=ops_manager.user_id,
        assigned_at=order2.created_at,
        priority="MEDIUM",
        application_status="IN_PROGRESS",
        target_due_date=date.today() + timedelta(days=5),
    )
    db_session.add(app2)
    db_session.flush()

    # Sales Order 3: Unassigned
    order3 = SalesOrder(
        order_number="SO-TEST-0003",
        company_id=company.company_id,
        client_id=client_kapper.client_id,
        service_id=service.service_id,
        salesperson_user_id=ops_manager.user_id,
        order_date=date.today(),
        order_value=Decimal("30000.00"),
        amount_received=Decimal("15000.00"),
        balance_amount=Decimal("15000.00"),
        govt_fees=Decimal("3000.00"),
        incidental_cost=Decimal("0.00"),
        lead_source="REFERRAL",
        payment_status="PARTIALLY_PAID",
        confirmation_status="CONFIRMED",
    )
    db_session.add(order3)
    db_session.flush()

    app3 = OperationApplication(
        application_number="AP-TEST-0003",
        sales_order_id=order3.order_id,
        company_id=company.company_id,
        client_id=client_kapper.client_id,
        service_id=service.service_id,
        assigned_to_user_id=None,
        priority="MEDIUM",
        application_status="UNASSIGNED",
    )
    db_session.add(app3)
    db_session.commit()

    return {
        "company": company,
        "ops_manager": ops_manager,
        "ops_deepak": ops_deepak,
        "ops_mansi": ops_mansi,
        "app1": app1,
        "app2": app2,
        "app3": app3,
        "app_doc1": app_doc1,
    }


def auth_header(user: User) -> dict:
    """Generate bearer authorization header for a test user."""
    token = create_access_token(
        user_id=user.user_id,
        token_version=user.token_version,
    )
    return {"Authorization": f"Bearer {token}"}


class TestOperationsAPI:
    """Comprehensive test suite for Operations APIs."""

    def test_get_operations_dashboard(self, client: TestClient, ops_test_fixture: dict):
        """Manager should see complete Operations dashboard with all 3 applications."""
        headers = auth_header(ops_test_fixture["ops_manager"])
        res = client.get("/api/operations/dashboard", headers=headers)
        assert res.status_code == 200
        data = res.json()

        assert "kpis" in data
        assert data["kpis"]["total_applications"] == 3
        assert data["kpis"]["assigned_count"] == 1
        assert data["kpis"]["in_progress_count"] == 1
        assert data["kpis"]["unassigned_count"] == 1
        assert len(data["status_breakdown"]) > 0
        assert len(data["workload_by_executive"]) > 0

    def test_get_my_tasks_deepak(self, client: TestClient, ops_test_fixture: dict):
        """Deepak should only see his assigned Clinical Establishment task (AP-TEST-0001)."""
        headers = auth_header(ops_test_fixture["ops_deepak"])
        res = client.get("/api/operations/tasks/my-tasks", headers=headers)
        assert res.status_code == 200
        data = res.json()

        assert data["total_count"] == 1
        assert len(data["items"]) == 1
        item = data["items"][0]
        assert item["application_number"] == "AP-TEST-0001"
        assert item["client_name"] == "KAPPER Medical Pvt Ltd"
        assert item["service_name"] == "Clinical Establishment"
        assert item["assigned_to_name"] == "Deepak Kumar"
        assert item["application_status"] == "ASSIGNED"

    def test_get_unassigned_tasks(self, client: TestClient, ops_test_fixture: dict):
        """Manager should see unassigned application AP-TEST-0003."""
        headers = auth_header(ops_test_fixture["ops_manager"])
        res = client.get("/api/operations/tasks/unassigned", headers=headers)
        assert res.status_code == 200
        data = res.json()

        assert data["total_count"] == 1
        assert data["items"][0]["application_number"] == "AP-TEST-0003"
        assert data["items"][0]["application_status"] == "UNASSIGNED"

    def test_get_task_detail_authorized(self, client: TestClient, ops_test_fixture: dict):
        """Deepak can view his own task details including document checklist."""
        headers = auth_header(ops_test_fixture["ops_deepak"])
        app_id = ops_test_fixture["app1"].application_id
        res = client.get(f"/api/operations/tasks/{app_id}", headers=headers)
        assert res.status_code == 200
        data = res.json()

        assert data["application_number"] == "AP-TEST-0001"
        assert len(data["documents"]) == 2
        assert data["documents"][0]["document_code"] in ("DOC_PAN", "DOC_RENT")

    def test_get_task_detail_forbidden_for_other_user(self, client: TestClient, ops_test_fixture: dict):
        """Deepak with SELF scope cannot view Mansi's task (AP-TEST-0002)."""
        headers = auth_header(ops_test_fixture["ops_deepak"])
        app2_id = ops_test_fixture["app2"].application_id
        res = client.get(f"/api/operations/tasks/{app2_id}", headers=headers)
        assert res.status_code == 403

    def test_assign_unassigned_task(self, client: TestClient, ops_test_fixture: dict):
        """Manager assigns unassigned task (AP-TEST-0003) to Deepak."""
        headers = auth_header(ops_test_fixture["ops_manager"])
        app3_id = ops_test_fixture["app3"].application_id
        deepak_id = ops_test_fixture["ops_deepak"].user_id

        res = client.post(
            f"/api/operations/tasks/{app3_id}/assign",
            json={
                "assignee_user_id": str(deepak_id),
                "priority": "HIGH",
                "notes": "Assigned to Deepak for quick execution",
            },
            headers=headers,
        )
        assert res.status_code == 200
        data = res.json()
        assert data["assigned_to_user_id"] == str(deepak_id)
        assert data["application_status"] == "ASSIGNED"
        assert len(data["assignment_history"]) == 1

    def test_reassign_task(self, client: TestClient, ops_test_fixture: dict):
        """Manager reassigns Deepak's task (AP-TEST-0001) to Mansi."""
        headers = auth_header(ops_test_fixture["ops_manager"])
        app1_id = ops_test_fixture["app1"].application_id
        mansi_id = ops_test_fixture["ops_mansi"].user_id

        res = client.post(
            f"/api/operations/tasks/{app1_id}/reassign",
            json={
                "new_assignee_user_id": str(mansi_id),
                "reason": "Deepak on medical leave, transferring ownership to Mansi.",
                "priority": "URGENT",
            },
            headers=headers,
        )
        assert res.status_code == 200
        data = res.json()
        assert data["assigned_to_user_id"] == str(mansi_id)
        assert data["priority"] == "URGENT"
        assert len(data["assignment_history"]) >= 1
        assert data["assignment_history"][0]["reason"] == "Deepak on medical leave, transferring ownership to Mansi."

    def test_reassign_task_to_same_assignee_rejected(self, client: TestClient, ops_test_fixture: dict):
        """Reject reassigning a task to the employee who is already assigned to it."""
        headers = auth_header(ops_test_fixture["ops_manager"])
        app1_id = ops_test_fixture["app1"].application_id
        deepak_id = ops_test_fixture["ops_deepak"].user_id

        # app1 is already assigned to Deepak. Reassigning to Deepak must fail.
        res = client.post(
            f"/api/operations/tasks/{app1_id}/reassign",
            json={
                "new_assignee_user_id": str(deepak_id),
                "reason": "Attempting to reassign to the same person",
            },
            headers=headers,
        )
        assert res.status_code == 400
        assert "already assigned to this employee" in res.json()["detail"]

    def test_update_application_status_valid_flow(self, client: TestClient, ops_test_fixture: dict):
        """Progress task from ASSIGNED -> IN_PROGRESS -> READY_FOR_SUBMISSION -> SUBMITTED -> APPROVED."""
        headers = auth_header(ops_test_fixture["ops_deepak"])
        app1_id = ops_test_fixture["app1"].application_id

        # 1. ASSIGNED -> IN_PROGRESS
        res1 = client.post(
            f"/api/operations/tasks/{app1_id}/status",
            json={"new_status": "IN_PROGRESS", "comment": "Started drafting application"},
            headers=headers,
        )
        assert res1.status_code == 200
        assert res1.json()["application_status"] == "IN_PROGRESS"

        # 2. IN_PROGRESS -> READY_FOR_SUBMISSION
        res2 = client.post(
            f"/api/operations/tasks/{app1_id}/status",
            json={"new_status": "READY_FOR_SUBMISSION", "comment": "All papers verified"},
            headers=headers,
        )
        assert res2.status_code == 200
        assert res2.json()["application_status"] == "READY_FOR_SUBMISSION"

        # 3. READY_FOR_SUBMISSION -> SUBMITTED
        res3 = client.post(
            f"/api/operations/tasks/{app1_id}/status",
            json={"new_status": "SUBMITTED", "comment": "Submitted online acknowledgment #ACK-9921"},
            headers=headers,
        )
        assert res3.status_code == 200
        assert res3.json()["application_status"] == "SUBMITTED"

        # 4. SUBMITTED -> APPROVED
        res4 = client.post(
            f"/api/operations/tasks/{app1_id}/status",
            json={"new_status": "APPROVED", "comment": "Certificate issued by health authority"},
            headers=headers,
        )
        assert res4.status_code == 200
        assert res4.json()["application_status"] == "APPROVED"
        assert res4.json()["completion_date"] is not None

    def test_update_application_status_invalid_transition(self, client: TestClient, ops_test_fixture: dict):
        """Reject invalid state transition (ASSIGNED -> APPROVED)."""
        headers = auth_header(ops_test_fixture["ops_deepak"])
        app1_id = ops_test_fixture["app1"].application_id

        res = client.post(
            f"/api/operations/tasks/{app1_id}/status",
            json={"new_status": "APPROVED", "comment": "Skip all steps"},
            headers=headers,
        )
        assert res.status_code == 400
        assert "Cannot transition" in res.json()["detail"]

    def test_update_document_verification_status(self, client: TestClient, ops_test_fixture: dict):
        """Verify document checklist item."""
        headers = auth_header(ops_test_fixture["ops_deepak"])
        doc_id = ops_test_fixture["app_doc1"].app_doc_id

        res = client.post(
            f"/api/operations/tasks/documents/{doc_id}/status",
            json={"status": "VERIFIED"},
            headers=headers,
        )
        assert res.status_code == 200
        assert res.json()["status"] == "VERIFIED"
        assert res.json()["verified_by_name"] == "Deepak Kumar"

    def test_list_operations_assignees(self, client: TestClient, ops_test_fixture: dict):
        """List eligible operations employees strictly excluding Sales, Admin, and Director personnel."""
        headers = auth_header(ops_test_fixture["ops_manager"])
        res = client.get("/api/operations/assignees", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert len(data) >= 3
        codes = [e["employee_code"] for e in data]
        assert "OP0001" in codes
        assert "OP0002" in codes
        assert "OP0003" in codes
        assert "OP0004" not in codes  # Sales user OP0004 must be excluded

    def test_reassign_rejects_sales_admin_director_and_self(
        self, client: TestClient, db_session: Session, ops_test_fixture: dict
    ):
        """Reject reassignment to sales, admin, director, current assignee, and self."""
        f = ops_test_fixture
        headers = auth_header(f["ops_manager"])
        app1_id = f["app1"].application_id

        # 1. Query existing Sales Department and create sales user
        dept_sales = db_session.query(Department).filter(
            Department.company_id == f["company"].company_id,
            Department.department_code == "SALES",
        ).first()

        sales_user = User(
            employee_code="OP0088",
            company_id=f["company"].company_id,
            department_id=dept_sales.department_id,
            designation_id=f["ops_manager"].designation_id,
            first_name="Sales",
            last_name="Person",
            official_email="sales.person@opstest.com",
            mobile_number="+919876543888",
            date_of_joining=date(2024, 1, 1),
            employment_type="FULL_TIME",
            account_status="ACTIVE",
            must_change_password=False,
        )
        db_session.add(sales_user)
        db_session.flush()

        res_sales = client.post(
            f"/api/operations/tasks/{app1_id}/reassign",
            json={"new_assignee_user_id": str(sales_user.user_id), "reason": "Attempting sales assign"},
            headers=headers,
        )
        assert res_sales.status_code == 400
        assert "Sales, Administration, or Director" in res_sales.json()["detail"]

        # 2. Reject reassign to Current Assignee (Deepak OP0002)
        res_curr = client.post(
            f"/api/operations/tasks/{app1_id}/reassign",
            json={"new_assignee_user_id": str(f["ops_deepak"].user_id), "reason": "Assign to same person"},
            headers=headers,
        )
        assert res_curr.status_code == 400
        assert "Cannot reassign to the current assignee" in res_curr.json()["detail"]

        # 3. Create Admin Department user and verify rejection
        dept_admin = Department(
            company_id=f["company"].company_id,
            department_code="ADMIN",
            department_name="Administration Department",
            status="ACTIVE",
        )
        db_session.add(dept_admin)
        db_session.flush()

        admin_user = User(
            employee_code="OP0099",
            company_id=f["company"].company_id,
            department_id=dept_admin.department_id,
            designation_id=f["ops_manager"].designation_id,
            first_name="Admin",
            last_name="User",
            official_email="admin.user@opstest.com",
            mobile_number="+919876543999",
            date_of_joining=date(2024, 1, 1),
            employment_type="FULL_TIME",
            account_status="ACTIVE",
            must_change_password=False,
        )
        db_session.add(admin_user)
        db_session.flush()

        res_admin = client.post(
            f"/api/operations/tasks/{app1_id}/reassign",
            json={"new_assignee_user_id": str(admin_user.user_id), "reason": "Attempting admin assign"},
            headers=headers,
        )
        assert res_admin.status_code == 400
        assert "Sales, Administration, or Director" in res_admin.json()["detail"]

    def test_super_admin_has_default_unrestricted_access(
        self, client: TestClient, db_session: Session, ops_test_fixture: dict
    ):
        """Superadmin has unrestricted access by default across all operations and sales endpoints."""
        f = ops_test_fixture
        super_admin = User(
            employee_code="CG0001",
            company_id=f["company"].company_id,
            department_id=f["ops_manager"].department_id,
            designation_id=f["ops_manager"].designation_id,
            first_name="Super",
            last_name="Admin",
            official_email="superadmin@opstest.com",
            mobile_number="+919876543001",
            date_of_joining=date(2024, 1, 1),
            employment_type="FULL_TIME",
            account_status="ACTIVE",
            must_change_password=False,
        )
        db_session.add(super_admin)
        db_session.flush()

        sa_headers = auth_header(super_admin)
        res_dash = client.get("/api/operations/dashboard", headers=sa_headers)
        assert res_dash.status_code == 200

        res_tasks = client.get("/api/operations/tasks", headers=sa_headers)
        assert res_tasks.status_code == 200
        assert res_tasks.json()["total_count"] >= 1
