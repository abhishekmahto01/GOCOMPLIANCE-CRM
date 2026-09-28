"""Tests for License Master / Service Master APIs and Sales Form Option integration."""
import uuid
from decimal import Decimal
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
from app.models.service import ServiceMaster
from app.models.user import User
from app.models.user_module_permission import UserModulePermission


@pytest.fixture
def admin_fixture(db_session: Session):
    """Seed test company, admin user with ADMIN and SALES permissions, and auth headers."""
    company = Company(
        company_code="LIC_TEST_CO",
        company_name="License Test Corp",
        employee_code_prefix="LTC",
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
        employee_code="LTC001",
        company_id=company.company_id,
        department_id=dept.department_id,
        designation_id=desig.designation_id,
        first_name="Admin",
        last_name="Super",
        official_email="superadmin@licensetest.com",
        mobile_number="+919999900001",
        date_of_joining=date(2023, 1, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        must_change_password=False,
    )
    db_session.add(admin_user)
    db_session.flush()

    # Modules
    admin_mod = db_session.query(Module).filter(Module.module_code == "ADMIN").first()
    if not admin_mod:
        admin_mod = Module(module_code="ADMIN", module_name="Administration", route="/admin", status="ACTIVE")
        db_session.add(admin_mod)
        db_session.flush()

    sales_mod = db_session.query(Module).filter(Module.module_code == "SALES").first()
    if not sales_mod:
        sales_mod = Module(module_code="SALES", module_name="Sales", route="/sales", status="ACTIVE")
        db_session.add(sales_mod)
        db_session.flush()

    sales_entry_mod = db_session.query(Module).filter(Module.module_code == "SALES_CONFIRMED_ORDER").first()
    if not sales_entry_mod:
        sales_entry_mod = Module(
            module_code="SALES_CONFIRMED_ORDER",
            module_name="Sales Entry",
            parent_module_id=sales_mod.module_id,
            route="/sales/entry",
            status="ACTIVE",
        )
        db_session.add(sales_entry_mod)
        db_session.flush()

    for m in [admin_mod, sales_mod, sales_entry_mod]:
        existing_p = (
            db_session.query(UserModulePermission)
            .filter(
                UserModulePermission.user_id == admin_user.user_id,
                UserModulePermission.module_id == m.module_id,
            )
            .first()
        )
        if not existing_p:
            perm = UserModulePermission(
                user_id=admin_user.user_id,
                module_id=m.module_id,
                can_view=True,
                can_create=True,
                can_edit=True,
                can_delete=True,
                can_export=True,
                data_scope="ALL",
                status="ACTIVE",
            )
            db_session.add(perm)

    db_session.commit()

    token = create_access_token(user_id=admin_user.user_id, token_version=admin_user.token_version)
    headers = {"Authorization": f"Bearer {token}"}

    return {
        "admin_user": admin_user,
        "headers": headers,
    }


def test_list_licenses_endpoint(client: TestClient, admin_fixture: dict):
    """Super admin can list all registered licenses / services."""
    headers = admin_fixture["headers"]
    response = client.get("/api/admin/licenses", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        first = data[0]
        assert "service_id" in first
        assert "service_code" in first
        assert "service_name" in first
        assert "status" in first


def test_create_and_update_license_endpoint(client: TestClient, admin_fixture: dict):
    """Super admin can create a new license and update it."""
    headers = admin_fixture["headers"]
    random_suffix = uuid.uuid4().hex[:6].upper()
    license_code = f"TEST_LIC_{random_suffix}"
    license_name = f"Test Compliance License {random_suffix}"

    # 1. Create
    payload = {
        "service_code": license_code,
        "service_name": license_name,
        "category": "LICENCE",
        "description": "Test license description",
        "base_price": 5000.0,
        "govt_fee": 1000.0,
        "standard_turnaround_days": 10,
        "status": "ACTIVE",
    }
    create_resp = client.post("/api/admin/licenses", json=payload, headers=headers)
    assert create_resp.status_code == status.HTTP_201_CREATED
    created_data = create_resp.json()
    assert created_data["service_code"] == license_code
    assert created_data["service_name"] == license_name
    license_id = created_data["service_id"]

    # 2. Get by ID
    get_resp = client.get(f"/api/admin/licenses/{license_id}", headers=headers)
    assert get_resp.status_code == status.HTTP_200_OK
    assert get_resp.json()["service_name"] == license_name

    # 3. Update
    updated_name = f"Updated License {random_suffix}"
    update_resp = client.patch(
        f"/api/admin/licenses/{license_id}",
        json={"service_name": updated_name, "standard_turnaround_days": 12, "status": "INACTIVE"},
        headers=headers,
    )
    assert update_resp.status_code == status.HTTP_200_OK
    assert update_resp.json()["service_name"] == updated_name
    assert update_resp.json()["standard_turnaround_days"] == 12
    assert update_resp.json()["status"] == "INACTIVE"

    # 4. Activate again
    reactivate_resp = client.patch(
        f"/api/admin/licenses/{license_id}",
        json={"status": "ACTIVE"},
        headers=headers,
    )
    assert reactivate_resp.status_code == status.HTTP_200_OK
    assert reactivate_resp.json()["status"] == "ACTIVE"

    # 5. Delete
    delete_resp = client.delete(f"/api/admin/licenses/{license_id}", headers=headers)
    assert delete_resp.status_code == status.HTTP_200_OK

    # 6. Verify Not Found after deletion
    get_after_delete = client.get(f"/api/admin/licenses/{license_id}", headers=headers)
    assert get_after_delete.status_code == status.HTTP_404_NOT_FOUND


def test_sales_form_options_reflects_license_master(client: TestClient, admin_fixture: dict):
    """Verify that newly created active license dynamically appears in sales form options."""
    headers = admin_fixture["headers"]
    random_suffix = uuid.uuid4().hex[:6].upper()
    license_code = f"DYN_LIC_{random_suffix}"
    license_name = f"Dynamic License {random_suffix}"

    # Create new active license
    payload = {
        "service_code": license_code,
        "service_name": license_name,
        "category": "LICENCE",
        "description": "Dynamic test for sales dropdown",
        "base_price": 7500.0,
        "govt_fee": 1500.0,
        "standard_turnaround_days": 7,
        "status": "ACTIVE",
    }
    create_resp = client.post("/api/admin/licenses", json=payload, headers=headers)
    assert create_resp.status_code == status.HTTP_201_CREATED
    license_id = create_resp.json()["service_id"]

    try:
        # Check sales form options
        options_resp = client.get("/api/sales/form-options", headers=headers)
        assert options_resp.status_code == status.HTTP_200_OK
        services = options_resp.json()["services"]
        found = any(s["service_code"] == license_code and s["service_name"] == license_name for s in services)
        assert found is True, f"Created license {license_code} must appear in /sales/form-options services dropdown"

        # Now deactivate license
        client.patch(
            f"/api/admin/licenses/{license_id}",
            json={"status": "INACTIVE"},
            headers=headers,
        )

        # Check sales form options again - should NOT appear when inactive
        options_resp2 = client.get("/api/sales/form-options", headers=headers)
        assert options_resp2.status_code == status.HTTP_200_OK
        services2 = options_resp2.json()["services"]
        found_inactive = any(s["service_code"] == license_code for s in services2)
        assert found_inactive is False, "Inactive license must NOT appear in sales form-options"
    finally:
        # Cleanup
        client.delete(f"/api/admin/licenses/{license_id}", headers=headers)
