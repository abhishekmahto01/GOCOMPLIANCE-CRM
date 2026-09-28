"""Tests for Department and Designation Master CRUD API endpoints."""
import uuid
from datetime import date
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.models.company import Company
from app.models.department import Department
from app.models.designation import Designation
from app.models.module import Module
from app.models.user import User
from app.models.user_module_permission import UserModulePermission


@pytest.fixture
def admin_fixture(db_session: Session):
    """Seed test company, admin user with ADMIN permissions, and auth headers."""
    company = Company(
        company_code=f"MST_TEST_{uuid.uuid4().hex[:4].upper()}",
        company_name="Master Test Corp",
        employee_code_prefix="MTC",
        status="ACTIVE",
    )
    db_session.add(company)
    db_session.flush()

    dept = Department(
        company_id=company.company_id,
        department_code="ADMIN_DEPT",
        department_name="Admin Dept",
        status="ACTIVE",
    )
    db_session.add(dept)
    db_session.flush()

    desig = Designation(
        company_id=company.company_id,
        designation_code="SUPER_ADMIN",
        designation_name="Super Administrator",
        level_rank=1,
        status="ACTIVE",
    )
    db_session.add(desig)
    db_session.flush()

    admin_user = User(
        employee_code=f"MTC{uuid.uuid4().hex[:4].upper()}",
        company_id=company.company_id,
        department_id=dept.department_id,
        designation_id=desig.designation_id,
        first_name="Admin",
        last_name="Super",
        official_email=f"admin_{uuid.uuid4().hex[:6]}@mastertest.com",
        mobile_number="+919999900001",
        date_of_joining=date(2023, 1, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        must_change_password=False,
    )
    db_session.add(admin_user)
    db_session.flush()

    admin_mod = db_session.query(Module).filter(Module.module_code == "ADMIN").first()
    if not admin_mod:
        admin_mod = Module(module_code="ADMIN", module_name="Administration", route="/admin", status="ACTIVE")
        db_session.add(admin_mod)
        db_session.flush()

    perm = UserModulePermission(
        user_id=admin_user.user_id,
        module_id=admin_mod.module_id,
        can_view=True,
        can_create=True,
        can_edit=True,
        can_delete=True,
        data_scope="ALL",
    )
    db_session.add(perm)
    db_session.commit()

    token = create_access_token(user_id=admin_user.user_id, token_version=admin_user.token_version)
    return {
        "headers": {"Authorization": f"Bearer {token}"},
        "company": company,
    }


def test_department_master_crud_flow(client: TestClient, admin_fixture):
    """Test Department listing, creation, update, and deletion endpoints."""
    headers = admin_fixture["headers"]
    company = admin_fixture["company"]

    # 1. Create Department
    create_payload = {
        "company_id": str(company.company_id),
        "department_code": "FINANCE",
        "department_name": "Finance & Audit",
        "description": "Tax and compliance auditing",
        "status": "ACTIVE",
    }
    create_res = client.post(
        "/api/admin/departments",
        json=create_payload,
        headers=headers,
    )
    assert create_res.status_code == status.HTTP_201_CREATED
    dept_data = create_res.json()
    dept_id = dept_data["department_id"]
    assert dept_data["department_code"] == "FINANCE"
    assert dept_data["department_name"] == "Finance & Audit"

    # 2. List Departments
    list_res = client.get(
        f"/api/admin/departments?company_id={company.company_id}",
        headers=headers,
    )
    assert list_res.status_code == status.HTTP_200_OK
    items = list_res.json()
    assert any(d["department_id"] == dept_id for d in items)

    # 3. Update Department
    update_payload = {
        "department_name": "Finance & Tax Audit",
        "description": "Updated description",
        "status": "ACTIVE",
    }
    patch_res = client.patch(
        f"/api/admin/departments/{dept_id}",
        json=update_payload,
        headers=headers,
    )
    assert patch_res.status_code == status.HTTP_200_OK
    assert patch_res.json()["department_name"] == "Finance & Tax Audit"

    # 4. Delete Department
    del_res = client.delete(
        f"/api/admin/departments/{dept_id}",
        headers=headers,
    )
    assert del_res.status_code == status.HTTP_200_OK
    assert del_res.json()["success"] is True


def test_designation_master_crud_flow(client: TestClient, admin_fixture):
    """Test Designation listing, creation, update, and deletion endpoints."""
    headers = admin_fixture["headers"]
    company = admin_fixture["company"]

    # 1. Create Designation
    create_payload = {
        "company_id": str(company.company_id),
        "designation_code": "VP_OPERATIONS",
        "designation_name": "VP Operations",
        "level_rank": 8,
        "is_managerial": True,
        "description": "Senior operations leadership",
        "status": "ACTIVE",
    }
    create_res = client.post(
        "/api/admin/designations",
        json=create_payload,
        headers=headers,
    )
    assert create_res.status_code == status.HTTP_201_CREATED
    desig_data = create_res.json()
    desig_id = desig_data["designation_id"]
    assert desig_data["designation_code"] == "VP_OPERATIONS"
    assert desig_data["level_rank"] == 8
    assert desig_data["is_managerial"] is True

    # 2. List Designations
    list_res = client.get(
        f"/api/admin/designations?company_id={company.company_id}",
        headers=headers,
    )
    assert list_res.status_code == status.HTTP_200_OK
    items = list_res.json()
    assert any(d["designation_id"] == desig_id for d in items)

    # 3. Update Designation
    update_payload = {
        "designation_name": "Vice President Operations",
        "level_rank": 9,
    }
    patch_res = client.patch(
        f"/api/admin/designations/{desig_id}",
        json=update_payload,
        headers=headers,
    )
    assert patch_res.status_code == status.HTTP_200_OK
    assert patch_res.json()["designation_name"] == "Vice President Operations"
    assert patch_res.json()["level_rank"] == 9

    # 4. Delete Designation
    del_res = client.delete(
        f"/api/admin/designations/{desig_id}",
        headers=headers,
    )
    assert del_res.status_code == status.HTTP_200_OK
    assert del_res.json()["success"] is True
