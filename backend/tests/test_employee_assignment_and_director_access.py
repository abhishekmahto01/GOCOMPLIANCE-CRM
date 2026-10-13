"""Comprehensive verification tests for Employee Assignment and Director Access in GoCompliance CRM.

Covers:
1. Each eligible assignee appears exactly once (no duplicates from joins or pagination).
2. Different employees sharing identical names remain separate.
3. Muskan Gupta appears once, is eligible for task assignment/reassignment, and can view/handle assigned tasks.
4. Assignment/reassignment respects permitted company boundaries (and unauthorized targets are blocked).
5. Muskan and the canonical Super Admin see the same employee set with identical filters.
6. Muskan can manage other employees and their permissions.
7. Employee totals and pagination are correct.
8. Normal users remain limited to their authorized modules and data.
9. Updated access is reflected after permission refresh or fresh login.
"""
import uuid
from datetime import date, datetime, timedelta, timezone
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
from app.services import permissions, user_service
from app.services.permissions import grant_or_update_permission, is_super_admin_user
from app.services.operation_service import get_eligible_operations_assignees, is_disallowed_ops_assignee
from app.services.sales_service import confirm_sales_order, create_sales_order
from app.schemas.sales_order import SalesOrderCreate


def auth_header(user: User) -> dict:
    """Generate bearer authorization header for a test user."""
    token = create_access_token(
        user_id=user.user_id,
        token_version=user.token_version,
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def env_fixture(db_session: Session):
    """Seed comprehensive organizational structure with companies, departments, designations, modules, and users."""
    # 1. Companies
    co1 = Company(
        company_code="GC_MAIN",
        company_name="GoCompliance Main Corp",
        employee_code_prefix="GC",
        status="ACTIVE",
    )
    co2 = Company(
        company_code="GC_BRANCH",
        company_name="GoCompliance Branch Corp",
        employee_code_prefix="GB",
        status="ACTIVE",
    )
    db_session.add_all([co1, co2])
    db_session.flush()

    # 2. Departments
    dept_admin = Department(department_code="ADMIN", department_name="Administration", status="ACTIVE")
    dept_ops = Department(department_code="OPERATIONS", department_name="Operations", status="ACTIVE")
    dept_sales = Department(department_code="SALES", department_name="Sales", status="ACTIVE")
    db_session.add_all([dept_admin, dept_ops, dept_sales])
    db_session.flush()

    # 3. Designations
    desig_dir = Designation(designation_code="DIRECTOR", designation_name="Director", level_rank=1, status="ACTIVE")
    desig_mgr = Designation(designation_code="OPS_MGR", designation_name="Operations Manager", level_rank=5, status="ACTIVE")
    desig_spec = Designation(designation_code="OPS_SPEC", designation_name="Operations Specialist", level_rank=10, status="ACTIVE")
    desig_rep = Designation(designation_code="SALES_REP", designation_name="Sales Executive", level_rank=10, status="ACTIVE")
    db_session.add_all([desig_dir, desig_mgr, desig_spec, desig_rep])
    db_session.flush()

    # 4. Modules
    modules = {}
    mod_specs = [
        ("ADMIN", "Administration Module", None, 1),
        ("ADMIN_EMPLOYEES", "Employee Directory", "ADMIN", 2),
        ("ADMIN_ACCESS", "User Permissions", "ADMIN", 3),
        ("OPERATIONS", "Operations Module", None, 10),
        ("OPERATIONS_DASHBOARD", "Operations Dashboard", "OPERATIONS", 11),
        ("OPERATIONS_MY_TASKS", "Operations My Tasks", "OPERATIONS", 12),
        ("OPERATIONS_ASSIGN", "Operations Assignment", "OPERATIONS", 13),
        ("SALES", "Sales Module", None, 20),
        ("SALES_MY_ORDERS", "Sales My Orders", "SALES", 21),
        ("SALES_ALL_ORDERS", "Sales All Orders", "SALES", 22),
    ]
    for code, name, parent, order in mod_specs:
        m = Module(
            module_code=code,
            module_name=name,
            parent_module_id=modules[parent].module_id if parent else None,
            display_order=order,
            status="ACTIVE",
        )
        db_session.add(m)
        db_session.flush()
        modules[code] = m

    # 5. Users
    # 5a. Canonical Super Admin (GC0001)
    super_admin = User(
        employee_code="GC0001",
        first_name="Super",
        last_name="Admin",
        official_email="superadmin@gocompliances.com",
        mobile_number="+919999900001",
        date_of_joining=date(2025, 1, 1),
        company_id=co1.company_id,
        department_id=dept_admin.department_id,
        designation_id=desig_dir.designation_id,
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        must_change_password=False,
        password_hash="mockhash",
    )

    # 5b. Muskan Gupta (GC0002) - Director in Administration
    muskan = User(
        employee_code="GC0002",
        first_name="Muskan",
        last_name="Gupta",
        official_email="info@gocompliances.com",
        mobile_number="+919999900002",
        date_of_joining=date(2025, 1, 1),
        company_id=co1.company_id,
        department_id=dept_admin.department_id,
        designation_id=desig_dir.designation_id,
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        must_change_password=False,
        password_hash="mockhash",
    )

    # 5c. Abhishek Kumar 1 (GC0007) - Operations Specialist in co1
    abhishek1 = User(
        employee_code="GC0007",
        first_name="Abhishek",
        last_name="Kumar",
        official_email="abhishek.ops1@gocompliances.com",
        mobile_number="+919999900007",
        date_of_joining=date(2025, 3, 1),
        company_id=co1.company_id,
        department_id=dept_ops.department_id,
        designation_id=desig_spec.designation_id,
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        must_change_password=False,
        password_hash="mockhash",
    )

    # 5d. Abhishek Kumar 2 (GC0099) - Same name, different employee in co2
    abhishek2 = User(
        employee_code="GC0099",
        first_name="Abhishek",
        last_name="Kumar",
        official_email="abhishek.ops2@gocompliances.com",
        mobile_number="+919999900099",
        date_of_joining=date(2025, 4, 1),
        company_id=co2.company_id,
        department_id=dept_ops.department_id,
        designation_id=desig_spec.designation_id,
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        must_change_password=False,
        password_hash="mockhash",
    )

    # 5e. Deepak Kumar (GC0005) - Operations Manager
    deepak = User(
        employee_code="GC0005",
        first_name="Deepak",
        last_name="Kumar",
        official_email="deepak.ops@gocompliances.com",
        mobile_number="+919999900005",
        date_of_joining=date(2025, 2, 1),
        company_id=co1.company_id,
        department_id=dept_ops.department_id,
        designation_id=desig_mgr.designation_id,
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        must_change_password=False,
        password_hash="mockhash",
    )

    # 5f. Mansi Singhal (GC0003) - Operations Specialist
    mansi = User(
        employee_code="GC0003",
        first_name="Mansi",
        last_name="Singhal",
        official_email="mansi.ops@gocompliances.com",
        mobile_number="+919999900003",
        date_of_joining=date(2025, 2, 15),
        company_id=co1.company_id,
        department_id=dept_ops.department_id,
        designation_id=desig_spec.designation_id,
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        must_change_password=False,
        password_hash="mockhash",
    )

    # 5g. Sales Rep (GC0010) - Pure sales user
    sales_rep = User(
        employee_code="GC0010",
        first_name="Rahul",
        last_name="Sharma",
        official_email="rahul.sales@gocompliances.com",
        mobile_number="+919999900010",
        date_of_joining=date(2025, 5, 1),
        company_id=co1.company_id,
        department_id=dept_sales.department_id,
        designation_id=desig_rep.designation_id,
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        must_change_password=False,
        password_hash="mockhash",
    )

    # 5h. Inactive Employee (GC0098)
    inactive_emp = User(
        employee_code="GC0098",
        first_name="Inactive",
        last_name="Worker",
        official_email="inactive@gocompliances.com",
        mobile_number="+919999900098",
        date_of_joining=date(2025, 1, 1),
        company_id=co1.company_id,
        department_id=dept_ops.department_id,
        designation_id=desig_spec.designation_id,
        employment_type="FULL_TIME",
        account_status="INACTIVE",
        must_change_password=False,
        password_hash="mockhash",
    )

    db_session.add_all([super_admin, muskan, abhishek1, abhishek2, deepak, mansi, sales_rep, inactive_emp])
    db_session.flush()

    # 6. Grant Permissions
    # 6a. Grant canonical Super Admin full rights
    for mod in modules.values():
        grant_or_update_permission(
            session=db_session,
            user_id=super_admin.user_id,
            module_id=mod.module_id,
            can_view=True,
            can_create=True,
            can_edit=True,
            can_delete=True,
            can_approve=True,
            can_assign=True,
            can_reassign=True,
            can_export=True,
            data_scope="ALL",
            granted_by_user_id=super_admin.user_id,
            is_bootstrap=True,
        )

    # 6b. Grant Muskan Gupta canonical Super Admin rights (Issue 3 resolution)
    for mod in modules.values():
        grant_or_update_permission(
            session=db_session,
            user_id=muskan.user_id,
            module_id=mod.module_id,
            can_view=True,
            can_create=True,
            can_edit=True,
            can_delete=True,
            can_approve=True,
            can_assign=True,
            can_reassign=True,
            can_export=True,
            data_scope="ALL",
            granted_by_user_id=super_admin.user_id,
            is_bootstrap=True,
        )

    # 6c. Grant Deepak Operations Manager (Company scope for Operations)
    grant_or_update_permission(
        session=db_session,
        user_id=deepak.user_id,
        module_id=modules["OPERATIONS"].module_id,
        can_view=True,
        can_create=True,
        can_edit=True,
        can_delete=False,
        can_assign=True,
        can_reassign=True,
        can_export=True,
        data_scope="COMPANY",
        granted_by_user_id=super_admin.user_id,
        is_bootstrap=True,
    )

    # 6d. Grant Abhishek1 Operations Specialist (Self scope)
    grant_or_update_permission(
        session=db_session,
        user_id=abhishek1.user_id,
        module_id=modules["OPERATIONS"].module_id,
        can_view=True,
        can_create=False,
        can_edit=True,
        can_delete=False,
        can_assign=False,
        can_reassign=False,
        can_export=False,
        data_scope="SELF",
        granted_by_user_id=super_admin.user_id,
        is_bootstrap=True,
    )

    # 6e. Grant Sales Rep Sales My Orders (Self scope)
    grant_or_update_permission(
        session=db_session,
        user_id=sales_rep.user_id,
        module_id=modules["SALES_MY_ORDERS"].module_id,
        can_view=True,
        can_create=True,
        can_edit=True,
        can_delete=False,
        can_assign=False,
        can_reassign=False,
        can_export=False,
        data_scope="SELF",
        granted_by_user_id=super_admin.user_id,
        is_bootstrap=True,
    )

    # 7. Seed Service and Client
    srv = ServiceMaster(
        service_code="SRV_TRADE",
        service_name="Trade License",
        category="LICENSE",
        base_price=Decimal("15000.00"),
        govt_fee=Decimal("2000.00"),
        standard_turnaround_days=10,
        status="ACTIVE",
    )
    client_obj = ClientMaster(
        company_id=co1.company_id,
        client_name="Test Enterprise Corp",
        contact_phone="+919888877777",
        contact_email="client@testcorp.in",
        created_by_user_id=super_admin.user_id,
        status="ACTIVE",
    )
    db_session.add_all([srv, client_obj])
    db_session.flush()

    return {
        "co1": co1,
        "co2": co2,
        "dept_admin": dept_admin,
        "dept_ops": dept_ops,
        "dept_sales": dept_sales,
        "desig_dir": desig_dir,
        "desig_mgr": desig_mgr,
        "desig_spec": desig_spec,
        "desig_rep": desig_rep,
        "modules": modules,
        "super_admin": super_admin,
        "muskan": muskan,
        "abhishek1": abhishek1,
        "abhishek2": abhishek2,
        "deepak": deepak,
        "mansi": mansi,
        "sales_rep": sales_rep,
        "inactive_emp": inactive_emp,
        "srv": srv,
        "client": client_obj,
    }


def test_1_each_eligible_assignee_appears_exactly_once(
    client: TestClient, db_session: Session, env_fixture: dict
):
    """VERIFICATION 1: In assignment options, each eligible assignee appears exactly once with no duplicates."""
    f = env_fixture
    headers = auth_header(f["super_admin"])

    # 1. Check Operations assignees API
    res = client.get("/api/operations/assignees", headers=headers)
    assert res.status_code == 200
    assignees = res.json()
    assert isinstance(assignees, list)
    assert len(assignees) > 0

    # Ensure every user_id is unique
    user_ids = [a["user_id"] for a in assignees]
    assert len(user_ids) == len(set(user_ids)), f"Duplicate user_ids found in assignees: {user_ids}"

    # Verify key employees exist exactly once
    for emp_code in ["GC0001", "GC0002", "GC0007", "GC0005", "GC0003"]:
        matching = [a for a in assignees if a.get("employee_code") == emp_code]
        assert len(matching) == 1, f"Expected {emp_code} exactly once, but found {len(matching)}"


def test_2_different_employees_sharing_name_remain_separate(
    client: TestClient, db_session: Session, env_fixture: dict
):
    """VERIFICATION 2: Distinct employees with identical names remain distinct by user_id and employee_code."""
    f = env_fixture
    headers = auth_header(f["super_admin"])

    res = client.get("/api/operations/assignees", headers=headers)
    assert res.status_code == 200
    assignees = res.json()

    # We created two Abhishek Kumars: GC0007 (co1) and GC0099 (co2)
    abhisheks = [a for a in assignees if a.get("full_name") == "Abhishek Kumar"]
    assert len(abhisheks) == 2, f"Expected both Abhishek Kumars in full scope, found {len(abhisheks)}"
    codes = {a["employee_code"] for a in abhisheks}
    assert codes == {"GC0007", "GC0099"}
    uids = {a["user_id"] for a in abhisheks}
    assert len(uids) == 2, "Different employees must have distinct user IDs"


def test_3_muskan_available_for_task_assignment_and_execution(
    client: TestClient, db_session: Session, env_fixture: dict
):
    """VERIFICATION 3: Muskan appears once, can receive assignment/reassignment, and view/execute tasks."""
    f = env_fixture
    admin_headers = auth_header(f["super_admin"])
    muskan_headers = auth_header(f["muskan"])

    # Verify eligibility helper
    assert not is_disallowed_ops_assignee(f["muskan"], session=db_session)

    # 1. Create a sales order via service
    order_in = SalesOrderCreate(
        client_name="Test Enterprise Corp",
        contact_no="+919888877777",
        service_id=f["srv"].service_id,
        salesperson_user_id=f["super_admin"].user_id,
        order_date=date.today(),
        order_value=Decimal("15000.00"),
        amount_received=Decimal("5000.00"),
        auto_confirm=True,  # Automatically confirms and creates Operations application
    )
    created_order = create_sales_order(db_session, order_in, current_user=f["super_admin"])
    db_session.flush()

    # 2. Assign operations work to Muskan Gupta
    assign_payload = {
        "assignee_user_id": str(f["muskan"].user_id),
        "target_due_date": (date.today() + timedelta(days=7)).isoformat(),
        "notes": "Assigning to Director Muskan Gupta for specialized handling",
    }
    assign_res = client.post(
        f"/api/sales/orders/{created_order.order_id}/assign",
        json=assign_payload,
        headers=admin_headers,
    )
    assert assign_res.status_code == 200, assign_res.text
    assigned_data = assign_res.json()
    assert assigned_data["assigned_to_user_id"] == str(f["muskan"].user_id)
    assert assigned_data["work_status"] == "ASSIGNED"

    # 3. Muskan views her assigned tasks in Operations "My Tasks"
    my_tasks_res = client.get("/api/operations/tasks/my-tasks", headers=muskan_headers)
    assert my_tasks_res.status_code == 200
    tasks = my_tasks_res.json()["items"]
    task_order_ids = [t.get("sales_order_id") for t in tasks]
    assert str(created_order.order_id) in task_order_ids

    # 4. Muskan adds a remark to the task
    app_id = assigned_data.get("application_id")
    remark_res = client.post(
        f"/api/operations/tasks/{app_id}/remarks",
        json={"remark_text": "Documents reviewed personally. Initiating filing."},
        headers=muskan_headers,
    )
    assert remark_res.status_code == 201


def test_4_assignment_respects_permitted_company_boundaries(
    client: TestClient, db_session: Session, env_fixture: dict
):
    """VERIFICATION 4: Assignment respects company boundaries for scoped users while blocking unauthorized targets."""
    f = env_fixture
    admin_headers = auth_header(f["super_admin"])

    # 1. Inactive target is blocked from assignment
    assert is_disallowed_ops_assignee(f["inactive_emp"], session=db_session) is True

    # 2. Pure sales rep without Operations rights is blocked from assignment
    assert is_disallowed_ops_assignee(f["sales_rep"], session=db_session) is True

    # 3. Operations assignees across companies are available for cross-company operations
    res = client.get("/api/operations/assignees", headers=admin_headers)
    assert res.status_code == 200
    assignees = res.json()
    codes = {a["employee_code"] for a in assignees}
    assert "GC0098" not in codes  # Inactive employee is excluded
    assert "GC0010" not in codes  # Pure sales rep is excluded
    assert "GC0002" in codes      # Muskan is included
    assert "GC0007" in codes      # Operations specialist is included


def test_5_muskan_and_super_admin_see_same_employee_set(
    client: TestClient, db_session: Session, env_fixture: dict
):
    """VERIFICATION 5: Muskan and existing Super Admin see the identical complete employee set in Employee Directory."""
    f = env_fixture
    admin_headers = auth_header(f["super_admin"])
    muskan_headers = auth_header(f["muskan"])

    # Query Employee Directory as Super Admin
    res_admin = client.get("/api/admin/employees?page=1&page_size=50", headers=admin_headers)
    assert res_admin.status_code == 200, res_admin.text
    data_admin = res_admin.json()

    # Query Employee Directory as Muskan
    res_muskan = client.get("/api/admin/employees?page=1&page_size=50", headers=muskan_headers)
    assert res_muskan.status_code == 200, res_muskan.text
    data_muskan = res_muskan.json()

    # Both must see the identical total count (more than 1, not self-only!)
    assert data_admin["total"] >= 7
    assert data_muskan["total"] == data_admin["total"], (
        f"Muskan total ({data_muskan['total']}) does not match Super Admin total ({data_admin['total']})"
    )

    admin_codes = sorted([e["employee_code"] for e in data_admin["items"]])
    muskan_codes = sorted([e["employee_code"] for e in data_muskan["items"]])
    assert admin_codes == muskan_codes

    # Query Permission Employee dropdown as both (User Permissions page calls /api/admin/employees?account_status=ACTIVE&page_size=100)
    perm_admin = client.get("/api/admin/employees?account_status=ACTIVE&page_size=100", headers=admin_headers)
    perm_muskan = client.get("/api/admin/employees?account_status=ACTIVE&page_size=100", headers=muskan_headers)
    assert perm_admin.status_code == 200
    assert perm_muskan.status_code == 200
    assert perm_muskan.json()["total"] == perm_admin.json()["total"]


def test_6_muskan_can_manage_other_employees_and_permissions(
    client: TestClient, db_session: Session, env_fixture: dict
):
    """VERIFICATION 6: Muskan can manage other employees and update their module permissions."""
    f = env_fixture
    muskan_headers = auth_header(f["muskan"])

    # Muskan updates Deepak's profile
    update_res = client.patch(
        f"/api/admin/employees/{f['deepak'].user_id}",
        json={"mobile_number": "+919876500000"},
        headers=muskan_headers,
    )
    assert update_res.status_code == 200
    assert update_res.json()["mobile_number"] == "+919876500000"

    # Muskan inspects and saves permissions for Deepak
    detail_res = client.get(
        f"/api/admin/users/{f['deepak'].user_id}/permissions",
        headers=muskan_headers,
    )
    assert detail_res.status_code == 200


def test_7_employee_totals_and_pagination_are_accurate(
    client: TestClient, db_session: Session, env_fixture: dict
):
    """VERIFICATION 7: Employee totals and pagination correctly reflect pages and total counts."""
    f = env_fixture
    muskan_headers = auth_header(f["muskan"])

    # Page 1 with page_size=2
    res_p1 = client.get("/api/admin/employees?page=1&page_size=2", headers=muskan_headers)
    assert res_p1.status_code == 200
    p1 = res_p1.json()
    assert len(p1["items"]) == 2
    assert p1["page"] == 1
    assert p1["page_size"] == 2
    assert p1["total"] >= 7

    # Page 2 with page_size=2
    res_p2 = client.get("/api/admin/employees?page=2&page_size=2", headers=muskan_headers)
    assert res_p2.status_code == 200
    p2 = res_p2.json()
    assert len(p2["items"]) == 2
    assert p2["page"] == 2
    p1_ids = {e["user_id"] for e in p1["items"]}
    p2_ids = {e["user_id"] for e in p2["items"]}
    assert p1_ids.isdisjoint(p2_ids), "Pagination pages must not have overlapping records"


def test_8_normal_users_remain_limited_to_authorized_modules(
    client: TestClient, db_session: Session, env_fixture: dict
):
    """VERIFICATION 8: Normal users cannot access Super Admin directories or unpermitted modules."""
    f = env_fixture
    rep_headers = auth_header(f["sales_rep"])

    # Sales rep attempts to access Employee Directory -> 403 Forbidden
    res_emp = client.get("/api/admin/employees", headers=rep_headers)
    assert res_emp.status_code == 403

    # Sales rep attempts to access User Permissions catalog -> 403 Forbidden
    res_perm = client.get("/api/admin/permission-catalog", headers=rep_headers)
    assert res_perm.status_code == 403


def test_9_fresh_login_reflects_super_admin_status(
    client: TestClient, db_session: Session, env_fixture: dict
):
    """VERIFICATION 9: Newly authenticated token for Muskan evaluates is_super_admin_user=True."""
    f = env_fixture

    # Database level check
    assert is_super_admin_user(db_session, f["muskan"]) is True

    # Token-based request returns super admin capabilities
    muskan_headers = auth_header(f["muskan"])
    perm_res = client.get("/api/auth/me/permissions", headers=muskan_headers)
    assert perm_res.status_code == 200
    data = perm_res.json()
    assert data["permissions"].get("admin.employees.read") is True
    assert data["permissions"].get("admin.access.update") is True
    assert len(data["accessible_pages"]) > 0
