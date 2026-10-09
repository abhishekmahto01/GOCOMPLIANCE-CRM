"""Integration tests for Operations Task filters (search, client_name, assignee, status, priority, pagination)."""
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
from app.models.operation_application import OperationApplication
from app.models.sales_order import SalesOrder
from app.models.service import ServiceMaster
from app.models.user import User
from app.models.user_module_permission import UserModulePermission
from app.services.permissions import grant_or_update_permission


def auth_header(user: User) -> dict:
    token = create_access_token(
        user_id=user.user_id,
        token_version=user.token_version,
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def filter_test_fixture(db_session: Session):
    """Seed test company, departments, users, clients, services, and tasks."""
    company1 = Company(
        company_code="GC_FLT",
        company_name="GoCompliance Filters Corp",
        employee_code_prefix="GC",
        status="ACTIVE",
    )
    company2 = Company(
        company_code="ENT_FLT",
        company_name="Enterpernership Filters Corp",
        employee_code_prefix="ENT",
        status="ACTIVE",
    )
    db_session.add_all([company1, company2])
    db_session.flush()

    dept_ops = Department(
        department_code="OPS_F",
        department_name="Operations Filters",
        status="ACTIVE",
    )
    dept_sales = Department(
        department_code="SALES_F",
        department_name="Sales Filters",
        status="ACTIVE",
    )
    db_session.add_all([dept_ops, dept_sales])
    db_session.flush()

    desig_mgr = Designation(
        designation_code="OPS_MGR_F",
        designation_name="Operations Manager Filter",
        level_rank=10,
        status="ACTIVE",
    )
    desig_exec = Designation(
        designation_code="OPS_EXEC_F",
        designation_name="Operations Executive Filter",
        level_rank=5,
        status="ACTIVE",
    )
    db_session.add_all([desig_mgr, desig_exec])
    db_session.flush()

    # Manager User (Company Scope or All Scope)
    manager = User(
        employee_code="GC0101",
        company_id=company1.company_id,
        department_id=dept_ops.department_id,
        designation_id=desig_mgr.designation_id,
        first_name="Operations",
        last_name="Manager",
        official_email="manager.filter@gocompliance.com",
        mobile_number="+919876541101",
        date_of_joining=date(2024, 1, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        must_change_password=False,
    )
    # Executive 1 (Assigned)
    exec1 = User(
        employee_code="GC0102",
        company_id=company1.company_id,
        department_id=dept_ops.department_id,
        designation_id=desig_exec.designation_id,
        first_name="Deepak",
        last_name="Verma",
        official_email="deepak.filter@gocompliance.com",
        mobile_number="+919876541102",
        date_of_joining=date(2024, 1, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        must_change_password=False,
    )
    # Executive 2 (Cross-company or other assignee)
    exec2 = User(
        employee_code="GC0103",
        company_id=company1.company_id,
        department_id=dept_ops.department_id,
        designation_id=desig_exec.designation_id,
        first_name="Mansi",
        last_name="Sharma",
        official_email="mansi.filter@gocompliance.com",
        mobile_number="+919876541103",
        date_of_joining=date(2024, 1, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        must_change_password=False,
    )
    db_session.add_all([manager, exec1, exec2])
    db_session.flush()

    # Grant Operations permissions
    mod_ops = db_session.query(Module).filter(Module.module_code == "OPERATIONS").first()
    if not mod_ops:
        mod_ops = Module(
            module_code="OPERATIONS",
            module_name="Operations Management",
            route="/operations",
            display_order=20,
            status="ACTIVE",
        )
        db_session.add(mod_ops)
        db_session.flush()

    grant_or_update_permission(
        session=db_session,
        user_id=manager.user_id,
        module_id=mod_ops.module_id,
        can_view=True,
        can_create=True,
        can_edit=True,
        can_delete=True,
        can_assign=True,
        can_reassign=True,
        can_export=True,
        data_scope="COMPANY",
        granted_by_user_id=manager.user_id,
        is_bootstrap=True,
    )
    grant_or_update_permission(
        session=db_session,
        user_id=exec1.user_id,
        module_id=mod_ops.module_id,
        can_view=True,
        can_create=False,
        can_edit=True,
        can_delete=False,
        data_scope="SELF",
        granted_by_user_id=manager.user_id,
        is_bootstrap=True,
    )
    grant_or_update_permission(
        session=db_session,
        user_id=exec2.user_id,
        module_id=mod_ops.module_id,
        can_view=True,
        can_create=False,
        can_edit=True,
        can_delete=False,
        data_scope="SELF",
        granted_by_user_id=manager.user_id,
        is_bootstrap=True,
    )

    # Clients
    client_varun = ClientMaster(
        company_id=company1.company_id,
        client_name="Varun (EVTL)",
        entity_type="PRIVATE_LIMITED",
        contact_person="Varun Sharma",
        contact_email="varun@evtl.com",
        contact_phone="+919811111111",
        status="ACTIVE",
        created_by_user_id=manager.user_id,
    )
    client_acme = ClientMaster(
        company_id=company1.company_id,
        client_name="Acme Corp Industries",
        entity_type="PRIVATE_LIMITED",
        contact_person="John Acme",
        contact_email="john@acme.com",
        contact_phone="+919822222222",
        status="ACTIVE",
        created_by_user_id=manager.user_id,
    )
    db_session.add_all([client_varun, client_acme])
    db_session.flush()

    # Services
    srv_fssai = ServiceMaster(
        service_code="SRV_FSSAI_FLT",
        service_name="FSSAI Central License",
        category="LICENCE",
        base_price=Decimal("15000.00"),
        govt_fee=Decimal("2000.00"),
        standard_turnaround_days=10,
        status="ACTIVE",
    )
    srv_gst = ServiceMaster(
        service_code="SRV_GST_FLT",
        service_name="GST Registration",
        category="REGISTRATION",
        base_price=Decimal("5000.00"),
        govt_fee=Decimal("0.00"),
        standard_turnaround_days=5,
        status="ACTIVE",
    )
    db_session.add_all([srv_fssai, srv_gst])
    db_session.flush()

    # Sales Orders
    so1 = SalesOrder(
        company_id=company1.company_id,
        client_id=client_varun.client_id,
        service_id=srv_fssai.service_id,
        salesperson_user_id=manager.user_id,
        order_number="SO-FLT-001",
        order_date=date.today(),
        order_value=Decimal("15000.00"),
        amount_received=Decimal("15000.00"),
        balance_amount=Decimal("0.00"),
        govt_fees=Decimal("2000.00"),
        incidental_cost=Decimal("0.00"),
        lead_source="DIRECT",
        payment_status="FULLY_PAID",
        confirmation_status="CONFIRMED",
    )
    so2 = SalesOrder(
        company_id=company1.company_id,
        client_id=client_varun.client_id,
        service_id=srv_gst.service_id,
        salesperson_user_id=manager.user_id,
        order_number="SO-FLT-002",
        order_date=date.today(),
        order_value=Decimal("5000.00"),
        amount_received=Decimal("5000.00"),
        balance_amount=Decimal("0.00"),
        govt_fees=Decimal("0.00"),
        incidental_cost=Decimal("0.00"),
        lead_source="DIRECT",
        payment_status="FULLY_PAID",
        confirmation_status="CONFIRMED",
    )
    so3 = SalesOrder(
        company_id=company1.company_id,
        client_id=client_acme.client_id,
        service_id=srv_gst.service_id,
        salesperson_user_id=manager.user_id,
        order_number="SO-FLT-003",
        order_date=date.today(),
        order_value=Decimal("5000.00"),
        amount_received=Decimal("5000.00"),
        balance_amount=Decimal("0.00"),
        govt_fees=Decimal("0.00"),
        incidental_cost=Decimal("0.00"),
        lead_source="DIRECT",
        payment_status="FULLY_PAID",
        confirmation_status="CONFIRMED",
    )
    so4 = SalesOrder(
        company_id=company1.company_id,
        client_id=client_acme.client_id,
        service_id=srv_fssai.service_id,
        salesperson_user_id=manager.user_id,
        order_number="SO-FLT-004",
        order_date=date.today(),
        order_value=Decimal("15000.00"),
        amount_received=Decimal("15000.00"),
        balance_amount=Decimal("0.00"),
        govt_fees=Decimal("2000.00"),
        incidental_cost=Decimal("0.00"),
        lead_source="DIRECT",
        payment_status="FULLY_PAID",
        confirmation_status="CONFIRMED",
    )
    db_session.add_all([so1, so2, so3, so4])
    db_session.flush()

    # Operation Applications
    # 1. Varun - IN_PROGRESS, URGENT, assigned to exec1
    app1 = OperationApplication(
        company_id=company1.company_id,
        sales_order_id=so1.order_id,
        client_id=client_varun.client_id,
        service_id=srv_fssai.service_id,
        application_number="APP-FLT-001",
        application_status="IN_PROGRESS",
        priority="URGENT",
        assigned_to_user_id=exec1.user_id,
        assigned_by_user_id=manager.user_id,
        assigned_at=date.today(),
        target_due_date=date.today() + timedelta(days=7),
    )
    # 2. Varun - ASSIGNED, HIGH, assigned to exec2
    app2 = OperationApplication(
        company_id=company1.company_id,
        sales_order_id=so2.order_id,
        client_id=client_varun.client_id,
        service_id=srv_gst.service_id,
        application_number="APP-FLT-002",
        application_status="ASSIGNED",
        priority="HIGH",
        assigned_to_user_id=exec2.user_id,
        assigned_by_user_id=manager.user_id,
        assigned_at=date.today(),
        target_due_date=date.today() + timedelta(days=10),
    )
    # 3. Acme - APPROVED, LOW, assigned to exec1
    app3 = OperationApplication(
        company_id=company1.company_id,
        sales_order_id=so3.order_id,
        client_id=client_acme.client_id,
        service_id=srv_gst.service_id,
        application_number="APP-FLT-003",
        application_status="APPROVED",
        priority="LOW",
        assigned_to_user_id=exec1.user_id,
        assigned_by_user_id=manager.user_id,
        assigned_at=date.today(),
        target_due_date=date.today() + timedelta(days=15),
    )
    # 4. Acme - UNASSIGNED, MEDIUM, no assignee
    app4 = OperationApplication(
        company_id=company1.company_id,
        sales_order_id=so4.order_id,
        client_id=client_acme.client_id,
        service_id=srv_fssai.service_id,
        application_number="APP-FLT-004",
        application_status="UNASSIGNED",
        priority="MEDIUM",
        assigned_to_user_id=None,
        target_due_date=date.today() + timedelta(days=20),
    )
    db_session.add_all([app1, app2, app3, app4])
    db_session.commit()

    return {
        "company1": company1,
        "company2": company2,
        "manager": manager,
        "exec1": exec1,
        "exec2": exec2,
        "client_varun": client_varun,
        "client_acme": client_acme,
        "app1": app1,
        "app2": app2,
        "app3": app3,
        "app4": app4,
    }


class TestOperationsFilters:
    """Test suite verifying filters, search, client_name, and pagination for Operations."""

    def test_search_varun_does_not_crash_and_matches_varun_tasks(
        self, client: TestClient, db_session: Session, filter_test_fixture: dict
    ):
        """Verify that searching for 'varun' returns only Varun tasks without 500 error."""
        manager = filter_test_fixture["manager"]
        headers = auth_header(manager)

        res = client.get("/api/operations/tasks", params={"search": "varun"}, headers=headers)
        assert res.status_code == 200, f"Expected 200 OK, got {res.status_code}: {res.text}"

        data = res.json()
        assert data["total_count"] == 2
        assert len(data["items"]) == 2
        for item in data["items"]:
            assert "Varun" in item["client_name"]

    def test_dedicated_client_name_filter_case_insensitive_and_trimmed(
        self, client: TestClient, db_session: Session, filter_test_fixture: dict
    ):
        """Verify dedicated client_name filter with partial matching, case insensitivity, and trimming."""
        manager = filter_test_fixture["manager"]
        headers = auth_header(manager)

        # 1. Lowercase with whitespace: "   varun   "
        res1 = client.get("/api/operations/tasks", params={"client_name": "   varun   "}, headers=headers)
        assert res1.status_code == 200
        data1 = res1.json()
        assert data1["total_count"] == 2
        assert all("Varun" in item["client_name"] for item in data1["items"])

        # 2. Uppercase: "VARUN"
        res2 = client.get("/api/operations/tasks", params={"client_name": "VARUN"}, headers=headers)
        assert res2.status_code == 200
        data2 = res2.json()
        assert data2["total_count"] == 2

        # 3. Partial match: "EVTL"
        res3 = client.get("/api/operations/tasks", params={"client_name": "evtl"}, headers=headers)
        assert res3.status_code == 200
        data3 = res3.json()
        assert data3["total_count"] == 2

        # 4. Non-matching client name: "nonexistent"
        res4 = client.get("/api/operations/tasks", params={"client_name": "nonexistent"}, headers=headers)
        assert res4.status_code == 200
        data4 = res4.json()
        assert data4["total_count"] == 0
        assert len(data4["items"]) == 0
        assert data4["summary"]["total_tasks"] == 0

    def test_combined_filters_with_and_logic(
        self, client: TestClient, db_session: Session, filter_test_fixture: dict
    ):
        """Verify combining client_name, status, priority, and assignee filters."""
        manager = filter_test_fixture["manager"]
        exec1 = filter_test_fixture["exec1"]
        headers = auth_header(manager)

        # Filter: client_name="varun" AND status="IN_PROGRESS"
        res1 = client.get(
            "/api/operations/tasks",
            params={"client_name": "varun", "status": "IN_PROGRESS"},
            headers=headers,
        )
        assert res1.status_code == 200
        data1 = res1.json()
        assert data1["total_count"] == 1
        assert data1["items"][0]["application_number"] == "APP-FLT-001"
        assert data1["items"][0]["application_status"] == "IN_PROGRESS"

        # Filter: client_name="varun" AND priority="HIGH"
        res2 = client.get(
            "/api/operations/tasks",
            params={"client_name": "varun", "priority": "HIGH"},
            headers=headers,
        )
        assert res2.status_code == 200
        data2 = res2.json()
        assert data2["total_count"] == 1
        assert data2["items"][0]["application_number"] == "APP-FLT-002"

        # Filter: client_name="varun" AND assignee=exec1
        res3 = client.get(
            "/api/operations/tasks",
            params={"client_name": "varun", "assigned_to_user_id": str(exec1.user_id)},
            headers=headers,
        )
        assert res3.status_code == 200
        data3 = res3.json()
        assert data3["total_count"] == 1
        assert data3["items"][0]["application_number"] == "APP-FLT-001"

    def test_general_search_and_dedicated_client_name_combine(
        self, client: TestClient, db_session: Session, filter_test_fixture: dict
    ):
        """Verify that general search (e.g. for service/order/app #) and client_name filter combine consistently."""
        manager = filter_test_fixture["manager"]
        headers = auth_header(manager)

        # General search for "FSSAI" + client_name="varun" -> should match APP-FLT-001 only
        res = client.get(
            "/api/operations/tasks",
            params={"search": "FSSAI", "client_name": "varun"},
            headers=headers,
        )
        assert res.status_code == 200
        data = res.json()
        assert data["total_count"] == 1
        assert data["items"][0]["application_number"] == "APP-FLT-001"

    def test_all_options_do_not_restrict_query(
        self, client: TestClient, db_session: Session, filter_test_fixture: dict
    ):
        """Verify passing 'ALL' for status or priority does not filter out active tasks."""
        manager = filter_test_fixture["manager"]
        headers = auth_header(manager)

        res = client.get(
            "/api/operations/tasks",
            params={"status": "ALL", "priority": "ALL"},
            headers=headers,
        )
        assert res.status_code == 200
        data = res.json()
        # All 4 non-cancelled applications in fixture
        assert data["total_count"] == 4

    def test_pagination_with_filters(
        self, client: TestClient, db_session: Session, filter_test_fixture: dict
    ):
        """Verify pagination with active filters returns correct total_pages and slice."""
        manager = filter_test_fixture["manager"]
        headers = auth_header(manager)

        # 2 varun items, limit=1 -> page 1 has 1 item, page 2 has 1 item, total_pages=2
        res_p1 = client.get(
            "/api/operations/tasks",
            params={"client_name": "varun", "page": 1, "limit": 1},
            headers=headers,
        )
        assert res_p1.status_code == 200
        d1 = res_p1.json()
        assert d1["total_count"] == 2
        assert d1["total_pages"] == 2
        assert len(d1["items"]) == 1

        res_p2 = client.get(
            "/api/operations/tasks",
            params={"client_name": "varun", "page": 2, "limit": 1},
            headers=headers,
        )
        assert res_p2.status_code == 200
        d2 = res_p2.json()
        assert d2["total_count"] == 2
        assert d2["total_pages"] == 2
        assert len(d2["items"]) == 1
        assert d1["items"][0]["application_id"] != d2["items"][0]["application_id"]

    def test_my_tasks_endpoint_supports_filters(
        self, client: TestClient, db_session: Session, filter_test_fixture: dict
    ):
        """Verify /tasks/my-tasks filters strictly to the logged-in user with client_name support."""
        exec1 = filter_test_fixture["exec1"]
        headers = auth_header(exec1)

        # Exec1 has app1 (Varun) and app3 (Acme)
        res_all = client.get("/api/operations/tasks/my-tasks", headers=headers)
        assert res_all.status_code == 200
        assert res_all.json()["total_count"] == 2

        # Filter by client_name="varun"
        res_varun = client.get(
            "/api/operations/tasks/my-tasks",
            params={"client_name": "varun"},
            headers=headers,
        )
        assert res_varun.status_code == 200
        d = res_varun.json()
        assert d["total_count"] == 1
        assert d["items"][0]["application_number"] == "APP-FLT-001"

    def test_unassigned_tasks_endpoint_supports_filters(
        self, client: TestClient, db_session: Session, filter_test_fixture: dict
    ):
        """Verify /tasks/unassigned supports search and client_name filters."""
        manager = filter_test_fixture["manager"]
        headers = auth_header(manager)

        # Initially 1 unassigned item (Acme - APP-FLT-004)
        res1 = client.get("/api/operations/tasks/unassigned", headers=headers)
        assert res1.status_code == 200
        assert res1.json()["total_count"] == 1
        assert res1.json()["items"][0]["application_number"] == "APP-FLT-004"

        # Filter by client_name="acme"
        res2 = client.get(
            "/api/operations/tasks/unassigned",
            params={"client_name": "acme"},
            headers=headers,
        )
        assert res2.status_code == 200
        assert res2.json()["total_count"] == 1

        # Filter by client_name="varun" -> 0 items
        res3 = client.get(
            "/api/operations/tasks/unassigned",
            params={"client_name": "varun"},
            headers=headers,
        )
        assert res3.status_code == 200
        assert res3.json()["total_count"] == 0
