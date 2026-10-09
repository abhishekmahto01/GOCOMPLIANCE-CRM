"""Comprehensive tests for Super Admin Employee Impersonation ("Login as Employee")."""
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
import uuid
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token
from app.models.company import Company
from app.models.department import Department
from app.models.designation import Designation
from app.models.impersonation_session import ImpersonationAuditLog, ImpersonationSession
from app.models.module import Module
from app.models.user import User
from app.models.user_module_permission import UserModulePermission
from app.services import permissions


@pytest.fixture
def impersonation_test_data(db_session: Session):
    """Fixture providing isolated company, roles, super admin, and multiple employee targets."""
    # 1. Company
    comp = Company(
        company_id=uuid.uuid4(),
        company_code="CMP_IMP",
        company_name="Impersonation Test Corp",
        legal_name="Impersonation Test Corp Private Limited",
        employee_code_prefix="IMP",
        status="ACTIVE",
    )
    db_session.add(comp)
    db_session.flush()

    # 2. Departments
    dept_admin = Department(
        department_id=uuid.uuid4(),
        department_code="DEPT_ADM",
        department_name="Administration",
        status="ACTIVE",
    )
    dept_sales = Department(
        department_id=uuid.uuid4(),
        department_code="DEPT_SALES",
        department_name="Sales & Marketing",
        status="ACTIVE",
    )
    db_session.add_all([dept_admin, dept_sales])
    db_session.flush()

    # 3. Designations
    desig_sa = Designation(
        designation_id=uuid.uuid4(),
        designation_code="SUPER_ADMIN_IMP",
        designation_name="Super Admin Impersonation",
        level_rank=1,
        status="ACTIVE",
    )
    desig_sales = Designation(
        designation_id=uuid.uuid4(),
        designation_code="SALES_EXEC_IMP",
        designation_name="Sales Executive Impersonation",
        level_rank=2,
        status="ACTIVE",
    )
    db_session.add_all([desig_sa, desig_sales])
    db_session.flush()

    # 4. Super Admin User
    admin_user = User(
        user_id=uuid.uuid4(),
        employee_code="CG0001",
        official_email="superadmin.imp@gocompliances.com",
        first_name="Super",
        last_name="Admin",
        mobile_number="+919876543210",
        date_of_joining=date(2024, 1, 1),
        employment_type="FULL_TIME",
        company_id=comp.company_id,
        department_id=dept_admin.department_id,
        designation_id=desig_sa.designation_id,
        account_status="ACTIVE",
        must_change_password=False,
        password_hash="$argon2id$v=19$m=65536,t=3,p=4$dummyhashdummyhashdummyhashdummyhashdummyhash",
        token_version=1,
    )

    # 5. Regular Sales Employee (CG0004)
    sales_employee = User(
        user_id=uuid.uuid4(),
        employee_code="CG0004",
        official_email="sales.emp@gocompliances.com",
        first_name="Rohan",
        last_name="Sharma",
        mobile_number="+919876543211",
        date_of_joining=date(2024, 1, 1),
        employment_type="FULL_TIME",
        company_id=comp.company_id,
        department_id=dept_sales.department_id,
        designation_id=desig_sales.designation_id,
        account_status="ACTIVE",
        must_change_password=False,
        password_hash="$argon2id$v=19$m=65536,t=3,p=4$dummyhashdummyhashdummyhashdummyhashdummyhash",
        token_version=1,
    )

    # 6. Inactive Employee (CG0099)
    inactive_employee = User(
        user_id=uuid.uuid4(),
        employee_code="CG0099",
        official_email="inactive.emp@gocompliances.com",
        first_name="Inactive",
        last_name="User",
        mobile_number="+919876543212",
        date_of_joining=date(2024, 1, 1),
        employment_type="FULL_TIME",
        company_id=comp.company_id,
        department_id=dept_sales.department_id,
        designation_id=desig_sales.designation_id,
        account_status="INACTIVE",
        must_change_password=False,
        password_hash="$argon2id$v=19$m=65536,t=3,p=4$dummyhashdummyhashdummyhashdummyhashdummyhash",
        token_version=1,
    )

    # 7. Another Super Admin (CG0002)
    second_admin = User(
        user_id=uuid.uuid4(),
        employee_code="CG0002",
        official_email="second.admin@gocompliances.com",
        first_name="Second",
        last_name="SuperAdmin",
        mobile_number="+919876543213",
        date_of_joining=date(2024, 1, 1),
        employment_type="FULL_TIME",
        company_id=comp.company_id,
        department_id=dept_admin.department_id,
        designation_id=desig_sa.designation_id,
        account_status="ACTIVE",
        must_change_password=False,
        password_hash="$argon2id$v=19$m=65536,t=3,p=4$dummyhashdummyhashdummyhashdummyhashdummyhash",
        token_version=1,
    )

    # 8. Regular non-admin user trying to impersonate
    regular_user = User(
        user_id=uuid.uuid4(),
        employee_code="EP0001",
        official_email="regular.user@gocompliances.com",
        first_name="Regular",
        last_name="User",
        mobile_number="+919876543214",
        date_of_joining=date(2024, 1, 1),
        employment_type="FULL_TIME",
        company_id=comp.company_id,
        department_id=dept_sales.department_id,
        designation_id=desig_sales.designation_id,
        account_status="ACTIVE",
        must_change_password=False,
        password_hash="$argon2id$v=19$m=65536,t=3,p=4$dummyhashdummyhashdummyhashdummyhashdummyhash",
        token_version=1,
    )

    db_session.add_all([admin_user, sales_employee, inactive_employee, second_admin, regular_user])
    db_session.commit()

    return {
        "admin": admin_user,
        "sales_emp": sales_employee,
        "inactive_emp": inactive_employee,
        "second_admin": second_admin,
        "regular_user": regular_user,
    }


def test_impersonation_start_success(client: TestClient, impersonation_test_data, monkeypatch):
    """Test authenticated Super Admin successfully impersonates active employee."""
    monkeypatch.setattr(settings, "ENABLE_ADMIN_IMPERSONATION", True)
    admin = impersonation_test_data["admin"]
    sales_emp = impersonation_test_data["sales_emp"]

    admin_token = create_access_token(user_id=admin.user_id, token_version=admin.token_version)

    response = client.post(
        "/api/auth/impersonate",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"employee_code": "CG0004"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["is_impersonated"] is True
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["impersonation"]["actor_employee_code"] == "CG0001"
    assert data["impersonation"]["target_employee_code"] == "CG0004"
    assert data["impersonation"]["target_name"] == "Rohan Sharma"

    # Using the impersonated token, /auth/me returns the sales employee!
    imp_token = data["access_token"]
    me_resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {imp_token}"})
    assert me_resp.status_code == status.HTTP_200_OK
    me_data = me_resp.json()
    assert me_data["employee_code"] == "CG0004"
    assert me_data["first_name"] == "Rohan"


def test_impersonation_feature_disabled(client: TestClient, impersonation_test_data, monkeypatch):
    """Test start and existing impersonation sessions are rejected when feature is disabled."""
    monkeypatch.setattr(settings, "ENABLE_ADMIN_IMPERSONATION", False)
    admin = impersonation_test_data["admin"]
    sales_emp = impersonation_test_data["sales_emp"]

    admin_token = create_access_token(user_id=admin.user_id, token_version=admin.token_version)

    # 1. Start rejected
    response = client.post(
        "/api/auth/impersonate",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"employee_code": "CG0004"},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "disabled" in response.json()["detail"].lower()

    # 2. Existing impersonated token rejected when feature disabled
    fake_session_id = uuid.uuid4()
    imp_token = create_access_token(
        user_id=sales_emp.user_id,
        token_version=sales_emp.token_version,
        is_impersonated=True,
        impersonation_session_id=fake_session_id,
        actor_admin_id=admin.user_id,
    )
    me_resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {imp_token}"})
    assert me_resp.status_code == status.HTTP_401_UNAUTHORIZED
    assert "disabled" in me_resp.json()["detail"].lower()


def test_regular_user_cannot_impersonate(client: TestClient, impersonation_test_data, monkeypatch):
    """Test ordinary non-Super-Admin user cannot start impersonation."""
    monkeypatch.setattr(settings, "ENABLE_ADMIN_IMPERSONATION", True)
    reg_user = impersonation_test_data["regular_user"]
    reg_token = create_access_token(user_id=reg_user.user_id, token_version=reg_user.token_version)

    response = client.post(
        "/api/auth/impersonate",
        headers={"Authorization": f"Bearer {reg_token}"},
        json={"employee_code": "CG0004"},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_impersonate_invalid_targets(client: TestClient, impersonation_test_data, monkeypatch):
    """Test rejecting non-existent, inactive, self, or Super Admin targets."""
    monkeypatch.setattr(settings, "ENABLE_ADMIN_IMPERSONATION", True)
    admin = impersonation_test_data["admin"]
    admin_token = create_access_token(user_id=admin.user_id, token_version=admin.token_version)

    # 1. Non-existent employee code
    r1 = client.post(
        "/api/auth/impersonate",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"employee_code": "NON_EXISTENT_999"},
    )
    assert r1.status_code == status.HTTP_404_NOT_FOUND

    # 2. Inactive employee
    r2 = client.post(
        "/api/auth/impersonate",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"employee_code": "CG0099"},
    )
    assert r2.status_code == status.HTTP_400_BAD_REQUEST
    assert "status is INACTIVE" in r2.json()["detail"]

    # 3. Cannot impersonate another Super Admin
    r3 = client.post(
        "/api/auth/impersonate",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"employee_code": "CG0002"},
    )
    assert r3.status_code == status.HTTP_400_BAD_REQUEST
    assert "Cannot impersonate another Super Admin" in r3.json()["detail"]

    # 4. Cannot impersonate self
    r4 = client.post(
        "/api/auth/impersonate",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"employee_code": "CG0001"},
    )
    assert r4.status_code == status.HTTP_400_BAD_REQUEST


def test_no_admin_privilege_leakage(client: TestClient, impersonation_test_data, monkeypatch):
    """Test target employee does not inherit Super Admin privileges during impersonation."""
    monkeypatch.setattr(settings, "ENABLE_ADMIN_IMPERSONATION", True)
    admin = impersonation_test_data["admin"]
    admin_token = create_access_token(user_id=admin.user_id, token_version=admin.token_version)

    # Start impersonation
    resp = client.post(
        "/api/auth/impersonate",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"employee_code": "CG0004"},
    )
    imp_token = resp.json()["access_token"]

    # Attempting to access Super Admin restricted endpoints (like delete employee) must fail with 403
    admin_action_resp = client.delete(
        f"/api/admin/employees/{admin.user_id}",
        headers={"Authorization": f"Bearer {imp_token}"},
    )
    assert admin_action_resp.status_code == status.HTTP_403_FORBIDDEN


def test_return_to_admin_restores_session(client: TestClient, impersonation_test_data, monkeypatch, db_session: Session):
    """Test Return to Admin terminates impersonation and restores Super Admin session."""
    monkeypatch.setattr(settings, "ENABLE_ADMIN_IMPERSONATION", True)
    admin = impersonation_test_data["admin"]
    admin_token = create_access_token(user_id=admin.user_id, token_version=admin.token_version)

    # 1. Start impersonation
    start_resp = client.post(
        "/api/auth/impersonate",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"employee_code": "CG0004"},
    )
    imp_token = start_resp.json()["access_token"]

    # 2. Check status
    status_resp = client.get(
        "/api/auth/impersonate/status",
        headers={"Authorization": f"Bearer {imp_token}"},
    )
    assert status_resp.status_code == status.HTTP_200_OK
    assert status_resp.json()["is_impersonated"] is True

    # 3. Return to Admin
    exit_resp = client.post(
        "/api/auth/impersonate/exit",
        headers={"Authorization": f"Bearer {imp_token}"},
    )
    assert exit_resp.status_code == status.HTTP_200_OK
    restored_data = exit_resp.json()
    assert "access_token" in restored_data
    restored_admin_token = restored_data["access_token"]

    # 4. Restored token identifies as Super Admin
    me_resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {restored_admin_token}"})
    assert me_resp.status_code == status.HTTP_200_OK
    assert me_resp.json()["employee_code"] == "CG0001"

    # 5. Old impersonation token is now rejected
    old_imp_resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {imp_token}"})
    assert old_imp_resp.status_code == status.HTTP_401_UNAUTHORIZED

    # 6. Audit logs verify START and END actions
    logs = db_session.query(ImpersonationAuditLog).order_by(ImpersonationAuditLog.created_at.asc()).all()
    assert len(logs) >= 2
    assert logs[-2].action == "IMPERSONATION_START"
    assert logs[-1].action == "IMPERSONATION_END"
    assert logs[-1].details.get("reason") == "RETURN_TO_ADMIN"


def test_logout_terminates_impersonation(client: TestClient, impersonation_test_data, monkeypatch, db_session: Session):
    """Test logging out while impersonating terminates the active impersonation session."""
    monkeypatch.setattr(settings, "ENABLE_ADMIN_IMPERSONATION", True)
    admin = impersonation_test_data["admin"]
    admin_token = create_access_token(user_id=admin.user_id, token_version=admin.token_version)

    # 1. Start impersonation
    start_resp = client.post(
        "/api/auth/impersonate",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"employee_code": "CG0004"},
    )
    assert start_resp.status_code == status.HTTP_200_OK
    imp_data = start_resp.json()
    imp_access = imp_data["access_token"]
    imp_refresh = imp_data["refresh_token"]

    # 2. Call logout with the impersonated token
    logout_resp = client.post(
        "/api/auth/logout",
        headers={"Authorization": f"Bearer {imp_access}"},
        json={"refresh_token": imp_refresh},
    )
    assert logout_resp.status_code == status.HTTP_200_OK

    # 3. Subsequent request with impersonation token is rejected
    me_resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {imp_access}"})
    assert me_resp.status_code == status.HTTP_401_UNAUTHORIZED


def test_switching_impersonation_allowed_and_regular_user_blocked(client: TestClient, impersonation_test_data, monkeypatch):
    """Test switching impersonation directly to another employee is permitted for Super Admin sessions, while regular users are blocked."""
    monkeypatch.setattr(settings, "ENABLE_ADMIN_IMPERSONATION", True)
    admin = impersonation_test_data["admin"]
    sales_emp = impersonation_test_data["sales_emp"]
    admin_token = create_access_token(user_id=admin.user_id, token_version=admin.token_version)
    sales_emp_token = create_access_token(user_id=sales_emp.user_id, token_version=sales_emp.token_version)

    # 1. Non-admin regular user cannot initiate impersonation
    non_admin_resp = client.post(
        "/api/auth/impersonate",
        headers={"Authorization": f"Bearer {sales_emp_token}"},
        json={"employee_code": "EP0001"},
    )
    assert non_admin_resp.status_code == status.HTTP_403_FORBIDDEN

    # 2. Start impersonation of CG0004
    start_resp = client.post(
        "/api/auth/impersonate",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"employee_code": "CG0004"},
    )
    assert start_resp.status_code == status.HTTP_200_OK
    imp_token = start_resp.json()["access_token"]

    # 3. Switching directly to EP0001 using the impersonated token works seamlessly
    switch_resp = client.post(
        "/api/auth/impersonate",
        headers={"Authorization": f"Bearer {imp_token}"},
        json={"employee_code": "EP0001"},
    )
    assert switch_resp.status_code == status.HTTP_200_OK
    new_imp_token = switch_resp.json()["access_token"]

    # 4. Status reflects EP0001 as target and CG0001 as actor
    status_resp = client.get(
        "/api/auth/impersonate/status",
        headers={"Authorization": f"Bearer {new_imp_token}"},
    )
    assert status_resp.status_code == status.HTTP_200_OK
    assert status_resp.json()["impersonation"]["target_employee_code"] == "EP0001"
    assert status_resp.json()["impersonation"]["actor_employee_code"] == "CG0001"


def test_token_refresh_during_impersonation_preserves_impersonation_claims(
    client: TestClient, impersonation_test_data, monkeypatch
):
    """Test refreshing an impersonated session rotates tokens and preserves impersonation status."""
    monkeypatch.setattr(settings, "ENABLE_ADMIN_IMPERSONATION", True)
    admin = impersonation_test_data["admin"]
    admin_token = create_access_token(user_id=admin.user_id, token_version=admin.token_version)

    # 1. Start impersonation of CG0004
    start_resp = client.post(
        "/api/auth/impersonate",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"employee_code": "CG0004"},
    )
    assert start_resp.status_code == status.HTTP_200_OK
    imp_data = start_resp.json()
    imp_refresh = imp_data["refresh_token"]

    # 2. Refresh token using the impersonation refresh token
    refresh_resp = client.post(
        "/api/auth/refresh",
        json={"refresh_token": imp_refresh},
    )
    assert refresh_resp.status_code == status.HTTP_200_OK
    refreshed_data = refresh_resp.json()
    new_access = refreshed_data["access_token"]
    assert refreshed_data["expires_in"] <= 1800

    # 3. Check status with the new access token
    status_resp = client.get(
        "/api/auth/impersonate/status",
        headers={"Authorization": f"Bearer {new_access}"},
    )
    assert status_resp.status_code == status.HTTP_200_OK
    status_data = status_resp.json()
    assert status_data["is_impersonated"] is True
    assert status_data["impersonation"]["target_employee_code"] == "CG0004"
    assert status_data["impersonation"]["actor_employee_code"] == "CG0001"


