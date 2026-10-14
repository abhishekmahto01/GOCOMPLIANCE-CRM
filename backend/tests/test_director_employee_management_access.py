"""Isolated verification tests for Director/Admin employee management access in GoCompliance CRM.

Covers the 5 required verification points:
1. Admin with ALL scope sees and manages all ordinary employees across configured companies/locations.
2. Admin with restricted scope remains restricted (COMPANY, SELF).
3. Muskan can create an employee, view pending records, and grant permitted access.
4. Direct API requests cannot bypass privilege restrictions (anti-escalation, no Super Admin assignment, no delete, no Super Admin tampering).
5. Existing Super Admin account and privileges remain strictly reserved and protected.
"""
import uuid
from datetime import date
from typing import Dict

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.models.company import Company
from app.models.department import Department
from app.models.designation import Designation
from app.models.module import Module
from app.models.user import User
from app.schemas.permission import PageActionPermission, UserPermissionsSaveRequest
from app.services.permissions import (
    get_effective_scope,
    grant_or_update_permission,
    is_super_admin_user,
)


def auth_header(user: User) -> dict:
    """Generate bearer authorization header for a test user."""
    token = create_access_token(
        user_id=user.user_id,
        token_version=user.token_version,
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def org_fixture(db_session: Session) -> Dict[str, any]:
    """Seed multi-company organization with companies, departments, designations, modules, and users."""
    # 1. Companies
    co1 = Company(
        company_code="GC_CORP",
        company_name="GoCompliance Corp",
        employee_code_prefix="GC",
        status="ACTIVE",
    )
    co2 = Company(
        company_code="GC_VENTURES",
        company_name="GoCompliance Ventures",
        employee_code_prefix="GV",
        status="ACTIVE",
    )
    db_session.add_all([co1, co2])
    db_session.flush()

    # 2. Departments
    dept_admin = Department(department_code="ADMIN", department_name="Administration", status="ACTIVE")
    dept_sales = Department(department_code="SALES", department_name="Sales", status="ACTIVE")
    dept_ops = Department(department_code="OPERATIONS", department_name="Operations", status="ACTIVE")
    db_session.add_all([dept_admin, dept_sales, dept_ops])
    db_session.flush()

    # 3. Designations
    desig_super = Designation(designation_code="SUPER_ADMIN", designation_name="Super Admin", level_rank=1, status="ACTIVE")
    desig_dir = Designation(designation_code="DIRECTOR", designation_name="Director", level_rank=2, status="ACTIVE")
    desig_mgr = Designation(designation_code="MGR", designation_name="Manager", level_rank=5, status="ACTIVE")
    desig_spec = Designation(designation_code="SPEC", designation_name="Specialist", level_rank=10, status="ACTIVE")
    db_session.add_all([desig_super, desig_dir, desig_mgr, desig_spec])
    db_session.flush()

    # 4. Modules
    modules = {}
    mod_specs = [
        ("ADMIN", "Admin Module", None, 1),
        ("ADMIN_EMPLOYEES", "Employees", "ADMIN", 2),
        ("ADMIN_ACCESS", "User Permissions", "ADMIN", 3),
        ("ADMIN_COMPANIES", "Companies", "ADMIN", 4),
        ("SALES", "Sales Module", None, 10),
        ("SALES_MY_ORDERS", "My Orders", "SALES", 11),
        ("SALES_ALL_ORDERS", "All Orders", "SALES", 12),
        ("OPERATIONS", "Operations Module", None, 20),
        ("OPERATIONS_DASHBOARD", "Ops Dashboard", "OPERATIONS", 21),
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
    # 5a. Authentic Super Admin (GC0001, research.rnd.gc@gmail.com)
    super_admin = User(
        employee_code="GC0001",
        first_name="Super",
        last_name="Admin",
        official_email="research.rnd.gc@gmail.com",
        mobile_number="+919999900001",
        date_of_joining=date(2025, 1, 1),
        company_id=co1.company_id,
        department_id=dept_admin.department_id,
        designation_id=desig_super.designation_id,
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        must_change_password=False,
        password_hash="mockhash",
    )

    # 5b. Muskan Gupta (GC0002, info@gocompliances.com, Director - Admin with ALL scope)
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

    # 5c. Restricted Admin (GC0003, company-only scope)
    restricted_admin = User(
        employee_code="GC0003",
        first_name="Restricted",
        last_name="Admin",
        official_email="restricted.admin@gocompliances.com",
        mobile_number="+919999900003",
        date_of_joining=date(2025, 1, 1),
        company_id=co1.company_id,
        department_id=dept_admin.department_id,
        designation_id=desig_mgr.designation_id,
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        must_change_password=False,
        password_hash="mockhash",
    )

    # 5d. Ordinary employee in Company 1
    emp_co1 = User(
        employee_code="GC0004",
        first_name="Vikram",
        last_name="Singh",
        official_email="vikram.singh@gocompliances.com",
        mobile_number="+919999900004",
        date_of_joining=date(2025, 2, 1),
        company_id=co1.company_id,
        department_id=dept_sales.department_id,
        designation_id=desig_spec.designation_id,
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        must_change_password=False,
        password_hash="mockhash",
    )

    # 5e. Ordinary employee in Company 2
    emp_co2 = User(
        employee_code="GV0001",
        first_name="Ananya",
        last_name="Roy",
        official_email="ananya.roy@gcventures.com",
        mobile_number="+919999900005",
        date_of_joining=date(2025, 2, 1),
        company_id=co2.company_id,
        department_id=dept_ops.department_id,
        designation_id=desig_spec.designation_id,
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        must_change_password=False,
        password_hash="mockhash",
    )

    db_session.add_all([super_admin, muskan, restricted_admin, emp_co1, emp_co2])
    db_session.flush()

    # 6. Permissions Setup
    # 6a. Muskan has ALL scope across Admin, Sales, Operations modules
    for m in modules.values():
        grant_or_update_permission(
            session=db_session,
            user_id=muskan.user_id,
            module_id=m.module_id,
            can_view=True,
            can_create=True,
            can_edit=True,
            can_delete=False,  # Delete reserved for Super Admin
            can_approve=True,
            can_assign=True,
            can_reassign=True,
            can_export=True,
            data_scope="ALL",
            status="ACTIVE",
            is_bootstrap=True,
        )

    # 6b. Restricted admin has COMPANY scope
    for m in modules.values():
        grant_or_update_permission(
            session=db_session,
            user_id=restricted_admin.user_id,
            module_id=m.module_id,
            can_view=True,
            can_create=True,
            can_edit=True,
            can_delete=False,
            can_approve=True,
            can_assign=True,
            can_reassign=True,
            can_export=True,
            data_scope="COMPANY",
            status="ACTIVE",
            is_bootstrap=True,
        )

    db_session.commit()

    return {
        "co1": co1,
        "co2": co2,
        "dept_admin": dept_admin,
        "dept_sales": dept_sales,
        "dept_ops": dept_ops,
        "desig_super": desig_super,
        "desig_dir": desig_dir,
        "desig_mgr": desig_mgr,
        "desig_spec": desig_spec,
        "modules": modules,
        "super_admin": super_admin,
        "muskan": muskan,
        "restricted_admin": restricted_admin,
        "emp_co1": emp_co1,
        "emp_co2": emp_co2,
    }


def test_admin_with_all_scope_sees_and_manages_all_ordinary_employees(
    client: TestClient, db_session: Session, org_fixture: dict
):
    """VERIFICATION 1: Admin with ALL scope sees and manages all ordinary employees across companies."""
    f = org_fixture
    muskan_headers = auth_header(f["muskan"])

    # Effective scope is ALL
    assert get_effective_scope(db_session, f["muskan"], "ADMIN_EMPLOYEES") == "ALL"

    # Muskan queries employee list without company filter
    res = client.get("/api/admin/employees?page=1&page_size=50", headers=muskan_headers)
    assert res.status_code == 200
    data = res.json()

    # Pagination total includes employees from BOTH companies
    user_ids = {item["user_id"] for item in data["items"]}
    assert str(f["emp_co1"].user_id) in user_ids
    assert str(f["emp_co2"].user_id) in user_ids
    assert str(f["muskan"].user_id) in user_ids
    assert data["total"] >= 5

    # Muskan can view details of employee in Company 2
    res_emp2 = client.get(f"/api/admin/employees/{f['emp_co2'].user_id}", headers=muskan_headers)
    assert res_emp2.status_code == 200
    assert res_emp2.json()["employee_code"] == f["emp_co2"].employee_code

    # Muskan can edit ordinary employee in Company 2
    edit_res = client.patch(
        f"/api/admin/employees/{f['emp_co2'].user_id}",
        json={"mobile_number": "+919888800000"},
        headers=muskan_headers,
    )
    assert edit_res.status_code == 200
    assert edit_res.json()["mobile_number"] == "+919888800000"


def test_admin_with_restricted_scope_remains_restricted(
    client: TestClient, db_session: Session, org_fixture: dict
):
    """VERIFICATION 2: Admin with restricted COMPANY scope remains restricted to their own company."""
    f = org_fixture
    restricted_headers = auth_header(f["restricted_admin"])

    # Effective scope is COMPANY
    assert get_effective_scope(db_session, f["restricted_admin"], "ADMIN_EMPLOYEES") == "COMPANY"

    # Query employee directory
    res = client.get("/api/admin/employees?page=1&page_size=50", headers=restricted_headers)
    assert res.status_code == 200
    data = res.json()

    # COMPANY 1 employees are visible, COMPANY 2 employees are NOT visible
    user_ids = {item["user_id"] for item in data["items"]}
    assert str(f["emp_co1"].user_id) in user_ids
    assert str(f["restricted_admin"].user_id) in user_ids
    assert str(f["emp_co2"].user_id) not in user_ids

    # Direct access to Company 2 employee is rejected with 403 Forbidden
    detail_res = client.get(f"/api/admin/employees/{f['emp_co2'].user_id}", headers=restricted_headers)
    assert detail_res.status_code == 403

    # Direct edit attempt on Company 2 employee is rejected with 403 Forbidden
    edit_res = client.patch(
        f"/api/admin/employees/{f['emp_co2'].user_id}",
        json={"mobile_number": "+919111100000"},
        headers=restricted_headers,
    )
    assert edit_res.status_code == 403

    # Attempt to create employee in Company 2 is rejected with 403 Forbidden
    create_res = client.post(
        "/api/admin/employees",
        json={
            "company_id": str(f["co2"].company_id),
            "department_id": str(f["dept_ops"].department_id),
            "designation_id": str(f["desig_spec"].designation_id),
            "first_name": "Intruder",
            "last_name": "Employee",
            "official_email": "intruder@gcventures.com",
            "mobile_number": "+919777700000",
            "date_of_joining": "2025-05-01",
            "employment_type": "FULL_TIME",
        },
        headers=restricted_headers,
    )
    assert create_res.status_code == 403


def test_muskan_can_create_employee_and_grant_permitted_access(
    client: TestClient, db_session: Session, org_fixture: dict
):
    """VERIFICATION 3: Muskan can onboard a new employee and manage their permissions."""
    f = org_fixture
    muskan_headers = auth_header(f["muskan"])

    # 1. Muskan creates a new employee
    create_res = client.post(
        "/api/admin/employees",
        json={
            "company_id": str(f["co1"].company_id),
            "department_id": str(f["dept_sales"].department_id),
            "designation_id": str(f["desig_spec"].designation_id),
            "first_name": "New",
            "last_name": "Onboard",
            "official_email": "new.onboard@gocompliances.com",
            "mobile_number": "+919555500000",
            "date_of_joining": "2025-06-01",
            "employment_type": "FULL_TIME",
        },
        headers=muskan_headers,
    )
    assert create_res.status_code == 201
    new_emp = create_res.json()
    new_user_id = new_emp["user_id"]
    assert new_emp["account_status"] == "PENDING"

    # 2. Querying without status filter shows the newly added employee immediately
    list_res = client.get("/api/admin/employees?page_size=100", headers=muskan_headers)
    assert list_res.status_code == 200
    listed_ids = [e["user_id"] for e in list_res.json()["items"]]
    assert new_user_id in listed_ids

    # 3. Muskan inspects the new employee's permissions bundle
    perm_bundle_res = client.get(f"/api/admin/users/{new_user_id}/permissions", headers=muskan_headers)
    assert perm_bundle_res.status_code == 200

    # 4. Muskan grants SALES permissions with COMPANY scope
    save_payload = {
        "user_settings": {
            "is_active": True,
            "is_reporting_manager": False,
            "is_hod": False,
        },
        "permissions": [
            {
                "page_code": "SALES_MY_ORDERS",
                "can_view": True,
                "can_create": False,
                "can_edit": True,
                "can_delete": False,
                "can_assign": False,
                "can_reassign": False,
                "can_export": True,
                "can_approve": False,
                "data_scope": "COMPANY",
                "status": "ACTIVE",
            }
        ],
    }
    save_res = client.put(
        f"/api/admin/users/{new_user_id}/permissions",
        json=save_payload,
        headers=muskan_headers,
    )
    assert save_res.status_code == 200
    updated_bundle = save_res.json()
    assert updated_bundle["is_active"] is True


def test_direct_api_requests_cannot_bypass_privilege_restrictions(
    client: TestClient, db_session: Session, org_fixture: dict
):
    """VERIFICATION 4: Direct API requests cannot bypass privilege restrictions."""
    f = org_fixture
    muskan_headers = auth_header(f["muskan"])

    # A. Muskan cannot assign Super Admin designation
    escalate_desig_res = client.post(
        "/api/admin/employees",
        json={
            "company_id": str(f["co1"].company_id),
            "department_id": str(f["dept_admin"].department_id),
            "designation_id": str(f["desig_super"].designation_id),
            "first_name": "Fake",
            "last_name": "SuperAdmin",
            "official_email": "fake.super@gocompliances.com",
            "mobile_number": "+919444400000",
            "date_of_joining": "2025-06-01",
            "employment_type": "FULL_TIME",
        },
        headers=muskan_headers,
    )
    assert escalate_desig_res.status_code == 403

    # B. Muskan cannot assign reserved Super Admin email
    escalate_email_res = client.post(
        "/api/admin/employees",
        json={
            "company_id": str(f["co1"].company_id),
            "department_id": str(f["dept_admin"].department_id),
            "designation_id": str(f["desig_spec"].designation_id),
            "first_name": "Attempt",
            "last_name": "Escalate",
            "official_email": "superadmin@gocompliances.in",
            "mobile_number": "+919444400001",
            "date_of_joining": "2025-06-01",
            "employment_type": "FULL_TIME",
        },
        headers=muskan_headers,
    )
    assert escalate_email_res.status_code == 403

    # C. Muskan can grant and revoke action permissions (including can_delete) for ordinary employees
    grant_delete_res = client.put(
        f"/api/admin/users/{f['emp_co1'].user_id}/permissions",
        json={
            "permissions": [
                {
                    "page_code": "SALES_MY_ORDERS",
                    "can_view": True,
                    "can_create": False,
                    "can_edit": False,
                    "can_delete": True,
                    "can_assign": False,
                    "can_reassign": False,
                    "can_export": False,
                    "can_approve": False,
                    "data_scope": "SELF",
                    "status": "ACTIVE",
                }
            ]
        },
        headers=muskan_headers,
    )
    assert grant_delete_res.status_code == 200
    perms_dict = {p["page_code"]: p for p in grant_delete_res.json()["permissions"]}
    assert perms_dict["SALES_MY_ORDERS"]["can_delete"] is True

    # C2. Ordinary employee with admin@gocompliances.com (like Mansi) is NOT treated as Super Admin and can be managed
    mansi_user = User(
        user_id=uuid.uuid4(),
        employee_code="GC0099",
        company_id=f["co1"].company_id,
        department_id=f["dept_admin"].department_id,
        designation_id=f["desig_spec"].designation_id,
        first_name="Mansi",
        last_name="Singhal",
        official_email="admin@gocompliances.com",
        mobile_number="+919876543999",
        date_of_joining=date(2025, 2, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
    )
    db_session.add(mansi_user)
    db_session.flush()

    assert not is_super_admin_user(db_session, mansi_user)

    mansi_perm_res = client.put(
        f"/api/admin/users/{mansi_user.user_id}/permissions",
        json={
            "user_settings": {
                "is_active": True,
                "is_hod": True,
                "is_reporting_manager": True,
            },
            "permissions": [
                {
                    "page_code": "SALES_MY_ORDERS",
                    "can_view": True,
                    "can_create": False,
                    "can_edit": True,
                    "can_delete": False,
                    "can_assign": False,
                    "can_reassign": False,
                    "can_export": True,
                    "can_approve": False,
                    "data_scope": "COMPANY",
                    "status": "ACTIVE",
                }
            ],
        },
        headers=muskan_headers,
    )
    assert mansi_perm_res.status_code == 200
    assert mansi_perm_res.json()["is_hod"] is True
    assert mansi_perm_res.json()["is_reporting_manager"] is True

    # D. Restricted admin cannot grant a scope higher than their own (e.g. ALL when grantor has COMPANY)
    restricted_headers = auth_header(f["restricted_admin"])
    scope_escalate_res = client.put(
        f"/api/admin/users/{f['emp_co1'].user_id}/permissions",
        json={
            "permissions": [
                {
                    "page_code": "SALES_MY_ORDERS",
                    "can_view": True,
                    "can_create": False,
                    "can_edit": False,
                    "can_delete": False,
                    "can_assign": False,
                    "can_reassign": False,
                    "can_export": False,
                    "can_approve": False,
                    "data_scope": "ALL",  # Restricted admin has COMPANY, cannot grant ALL
                    "status": "ACTIVE",
                }
            ]
        },
        headers=restricted_headers,
    )
    assert scope_escalate_res.status_code == 403

    # E. Muskan cannot modify permissions or settings of the Super Admin account
    tamper_sa_res = client.put(
        f"/api/admin/users/{f['super_admin'].user_id}/permissions",
        json={
            "user_settings": {"is_active": False},
            "permissions": [],
        },
        headers=muskan_headers,
    )
    assert tamper_sa_res.status_code == 403

    # F. Muskan cannot delete an employee (delete is Super Admin only)
    delete_emp_res = client.delete(
        f"/api/admin/employees/{f['emp_co1'].user_id}",
        headers=muskan_headers,
    )
    assert delete_emp_res.status_code == 403

    # G. Muskan cannot modify her own permissions (anti-self-escalation)
    self_mod_res = client.put(
        f"/api/admin/users/{f['muskan'].user_id}/permissions",
        json={
            "permissions": [
                {
                    "page_code": "SALES_MY_ORDERS",
                    "can_view": True,
                    "can_create": True,
                    "can_edit": True,
                    "can_delete": False,
                    "can_assign": False,
                    "can_reassign": False,
                    "can_export": False,
                    "can_approve": False,
                    "data_scope": "ALL",
                    "status": "ACTIVE",
                }
            ]
        },
        headers=muskan_headers,
    )
    assert self_mod_res.status_code == 403


def test_existing_super_admin_access_remains_unchanged(
    client: TestClient, db_session: Session, org_fixture: dict
):
    """VERIFICATION 5: Authentic Super Admin retains exclusive rights while Muskan is Admin/Director."""
    f = org_fixture
    sa_headers = auth_header(f["super_admin"])

    # 1. Super Admin is authentic Super Admin
    assert is_super_admin_user(db_session, f["super_admin"]) is True

    # 2. Muskan is Admin/Director, NOT Super Admin
    assert is_super_admin_user(db_session, f["muskan"]) is False

    # 3. Super Admin CAN delete an employee
    delete_res = client.delete(
        f"/api/admin/employees/{f['emp_co1'].user_id}",
        headers=sa_headers,
    )
    assert delete_res.status_code == 200
    assert delete_res.json()["message"] == "Employee deleted successfully"

    # 4. Super Admin CAN grant delete permissions
    grant_del_res = client.put(
        f"/api/admin/users/{f['emp_co2'].user_id}/permissions",
        json={
            "permissions": [
                {
                    "page_code": "SALES_MY_ORDERS",
                    "can_view": True,
                    "can_create": False,
                    "can_edit": True,
                    "can_delete": True,
                    "can_assign": False,
                    "can_reassign": False,
                    "can_export": False,
                    "can_approve": False,
                    "data_scope": "ALL",
                    "status": "ACTIVE",
                }
            ]
        },
        headers=sa_headers,
    )
    assert grant_del_res.status_code == 200
