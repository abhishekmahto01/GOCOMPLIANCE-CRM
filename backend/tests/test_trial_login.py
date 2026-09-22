"""Tests for Stage B: Trial Employee Login Provisioning with Mandatory First-Login Password Change."""
import uuid
from datetime import date

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.security import hash_password, verify_password
from app.database.session import get_db
from app.main import app
from app.models.company import Company
from app.models.department import Department
from app.models.designation import Designation
from app.models.module import Module
from app.models.user import User
from app.services.permissions import grant_or_update_permission




@pytest.fixture
def test_org_setup(db_session):
    """Fixture providing a fresh company, department, designation, and super admin."""
    # Ensure modules exist
    admin_mod = db_session.query(Module).filter(Module.module_code == "ADMIN").first()
    if not admin_mod:
        admin_mod = Module(
            module_id=uuid.uuid4(),
            module_code="ADMIN",
            module_name="Administration",
            route="/admin",
            status="ACTIVE",
            display_order=1,
        )
        db_session.add(admin_mod)
        db_session.flush()

    emp_mod = db_session.query(Module).filter(Module.module_code == "ADMIN_EMPLOYEES").first()
    if not emp_mod:
        emp_mod = Module(
            module_id=uuid.uuid4(),
            module_code="ADMIN_EMPLOYEES",
            module_name="Employee Management",
            parent_module_id=admin_mod.module_id,
            route="/admin/employees",
            status="ACTIVE",
            display_order=2,
        )
        db_session.add(emp_mod)
    # Company
    import random
    import string
    prefix = "".join(random.choices(string.ascii_uppercase, k=5))
    c_code = "".join(random.choices(string.ascii_uppercase, k=5))
    company = Company(
        company_id=uuid.uuid4(),
        company_name=f"Trial Org {uuid.uuid4().hex[:6]}",
        company_code=c_code,
        employee_code_prefix=prefix,
        status="ACTIVE",
    )
    db_session.add(company)
    db_session.flush()

    dept = Department(
        department_id=uuid.uuid4(),
        company_id=company.company_id,
        department_name="Engineering",
        department_code="ENG",
        status="ACTIVE",
    )
    db_session.add(dept)
    db_session.flush()

    desig = Designation(
        designation_id=uuid.uuid4(),
        company_id=company.company_id,
        designation_name="Software Engineer",
        designation_code="SE",
        level_rank=1,
        status="ACTIVE",
    )
    db_session.add(desig)
    db_session.flush()

    # Admin User
    admin = User(
        user_id=uuid.uuid4(),
        employee_code=f"TA{uuid.uuid4().hex[:4].upper()}",
        company_id=company.company_id,
        department_id=dept.department_id,
        designation_id=desig.designation_id,
        first_name="Admin",
        last_name="Tester",
        official_email=f"admin.{uuid.uuid4().hex[:6]}@trialorg.com",
        mobile_number="+919876543210",
        date_of_joining=date(2025, 1, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        password_hash=hash_password("AdminSecure@2026"),
        must_change_password=False,
    )
    db_session.add(admin)
    db_session.flush()

    # Grant ALL permissions on ADMIN_EMPLOYEES to admin
    grant_or_update_permission(
        session=db_session,
        user_id=admin.user_id,
        module_id=emp_mod.module_id,
        can_view=True,
        can_create=True,
        can_edit=True,
        can_delete=True,
        can_approve=True,
        data_scope="ALL",
        granted_by_user_id=admin.user_id,
        is_bootstrap=True,
    )
    db_session.commit()

    return {
        "company": company,
        "department": dept,
        "designation": desig,
        "admin": admin,
        "admin_module": admin_mod,
        "employees_module": emp_mod,
    }


def get_admin_headers(client: TestClient, admin: User) -> dict:
    """Helper to authenticate as admin and return Bearer headers."""
    resp = client.post(
        "/api/auth/login",
        json={"identifier": admin.official_email, "password": "AdminSecure@2026"},
    )
    assert resp.status_code == 200, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_new_employee_creation_with_trial_password_mode(client: TestClient, db_session, test_org_setup, monkeypatch):
    """Test creating employee when trial default password mode is enabled."""
    monkeypatch.setattr(settings, "TRIAL_DEFAULT_PASSWORD_ENABLED", True)
    monkeypatch.setattr(settings, "TRIAL_DEFAULT_PASSWORD", "12345")
    monkeypatch.setattr(settings, "ENVIRONMENT", "development")
    monkeypatch.setattr(settings, "APP_ENV", None)

    admin = test_org_setup["admin"]
    headers = get_admin_headers(client, admin)

    test_email = f"rohan.{uuid.uuid4().hex[:6]}@trialorg.com"
    payload = {
        "company_id": str(test_org_setup["company"].company_id),
        "department_id": str(test_org_setup["department"].department_id),
        "designation_id": str(test_org_setup["designation"].designation_id),
        "first_name": "Rohan",
        "last_name": "Sharma",
        "official_email": test_email,
        "mobile_number": "+919811122233",
        "date_of_joining": "2026-03-01",
        "employment_type": "FULL_TIME",
        "account_status": "ACTIVE",
    }

    resp = client.post("/api/admin/employees", json=payload, headers=headers)
    assert resp.status_code == 201, resp.text
    data = resp.json()

    # 1. API response must NEVER contain password or password_hash
    assert "password" not in data
    assert "password_hash" not in data

    # 2. Safe flags returned
    assert data["credentials_initialized"] is True
    assert data["must_change_password"] is True
    assert data["login_status"] == "Password Change Required"
    assert data["credentials_initialized_at"] is not None

    # 3. Database inspection: verify plaintext 12345 is NOT stored, but Argon2 hash is
    created_user = db_session.query(User).filter(User.official_email == test_email).one()
    assert created_user.password_hash != "12345"
    assert created_user.password_hash.startswith("$argon2id$")
    assert verify_password("12345", created_user.password_hash) is True
    assert created_user.must_change_password is True
    assert created_user.credentials_initialized_at is not None


def test_initialize_trial_login_existing_uninitialized_employee(client: TestClient, db_session, test_org_setup, monkeypatch):
    """Test initializing trial login for an existing employee without credentials."""
    monkeypatch.setattr(settings, "TRIAL_DEFAULT_PASSWORD_ENABLED", True)
    monkeypatch.setattr(settings, "TRIAL_DEFAULT_PASSWORD", "12345")
    monkeypatch.setattr(settings, "ENVIRONMENT", "development")

    # Create uninitialized employee directly
    uninit_emp = User(
        user_id=uuid.uuid4(),
        employee_code=f"UN{uuid.uuid4().hex[:4].upper()}",
        company_id=test_org_setup["company"].company_id,
        department_id=test_org_setup["department"].department_id,
        designation_id=test_org_setup["designation"].designation_id,
        first_name="Pooja",
        last_name="Verma",
        official_email=f"pooja.{uuid.uuid4().hex[:6]}@trialorg.com",
        mobile_number="+919822233344",
        date_of_joining=date(2026, 2, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        password_hash=None,
        must_change_password=True,
    )
    db_session.add(uninit_emp)
    db_session.commit()

    headers = get_admin_headers(client, test_org_setup["admin"])

    # 1. Initialize trial login
    resp = client.post(f"/api/admin/employees/{uninit_emp.user_id}/initialize-trial-login", headers=headers)
    assert resp.status_code == 200, resp.text
    res_data = resp.json()

    assert res_data["credentials_initialized"] is True
    assert res_data["must_change_password"] is True
    assert res_data["login_status"] == "Password Change Required"
    assert "password" not in res_data
    assert "password_hash" not in res_data

    # 2. Cannot re-initialize (reject overwriting)
    re_resp = client.post(f"/api/admin/employees/{uninit_emp.user_id}/initialize-trial-login", headers=headers)
    assert re_resp.status_code == 400
    assert "already initialized" in re_resp.json()["detail"].lower()


def test_initialize_trial_login_rejects_inactive_employee(client: TestClient, db_session, test_org_setup, monkeypatch):
    """Test that inactive or suspended employees cannot have trial login initialized."""
    monkeypatch.setattr(settings, "TRIAL_DEFAULT_PASSWORD_ENABLED", True)
    monkeypatch.setattr(settings, "TRIAL_DEFAULT_PASSWORD", "12345")

    inactive_emp = User(
        user_id=uuid.uuid4(),
        employee_code=f"IN{uuid.uuid4().hex[:4].upper()}",
        company_id=test_org_setup["company"].company_id,
        department_id=test_org_setup["department"].department_id,
        designation_id=test_org_setup["designation"].designation_id,
        first_name="Inactive",
        last_name="User",
        official_email=f"inactive.{uuid.uuid4().hex[:6]}@trialorg.com",
        mobile_number="+919833344455",
        date_of_joining=date(2026, 2, 1),
        employment_type="FULL_TIME",
        account_status="INACTIVE",
        password_hash=None,
        must_change_password=True,
    )
    db_session.add(inactive_emp)
    db_session.commit()

    headers = get_admin_headers(client, test_org_setup["admin"])
    resp = client.post(f"/api/admin/employees/{inactive_emp.user_id}/initialize-trial-login", headers=headers)
    assert resp.status_code == 400
    assert "must be active" in resp.json()["detail"].lower()


def test_initialize_trial_login_refused_in_production(client: TestClient, db_session, test_org_setup, monkeypatch):
    """Test that trial initialization is strictly refused in production environment."""
    monkeypatch.setattr(settings, "TRIAL_DEFAULT_PASSWORD_ENABLED", True)
    monkeypatch.setattr(settings, "TRIAL_DEFAULT_PASSWORD", "12345")
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")

    headers = get_admin_headers(client, test_org_setup["admin"])

    # Create dummy user
    dummy_emp = User(
        user_id=uuid.uuid4(),
        employee_code=f"DM{uuid.uuid4().hex[:4].upper()}",
        company_id=test_org_setup["company"].company_id,
        department_id=test_org_setup["department"].department_id,
        designation_id=test_org_setup["designation"].designation_id,
        first_name="Dummy",
        last_name="Prod",
        official_email=f"dummy.{uuid.uuid4().hex[:6]}@trialorg.com",
        mobile_number="+919844455566",
        date_of_joining=date(2026, 2, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        password_hash=None,
        must_change_password=True,
    )
    db_session.add(dummy_emp)
    db_session.commit()

    resp = client.post(f"/api/admin/employees/{dummy_emp.user_id}/initialize-trial-login", headers=headers)
    assert resp.status_code == 400
    assert "production" in resp.json()["detail"].lower()


def test_trial_login_restricted_mode_and_mandatory_password_change(client: TestClient, db_session, test_org_setup, monkeypatch):
    """Full lifecycle test:
    1. Employee created with trial password '12345'.
    2. Employee logs in with '12345' -> receives must_change_password=True.
    3. Restricted session is blocked from CRM modules (/me/modules, /admin/employees) -> 403 Forbidden.
    4. /me is accessible.
    5. Employee changes password to strong password 'MySecure#Pass2026!'.
    6. Old temporary password '12345' no longer works.
    7. Employee logs in with new password -> must_change_password=False.
    8. Full CRM access is granted.
    """
    monkeypatch.setattr(settings, "TRIAL_DEFAULT_PASSWORD_ENABLED", True)
    monkeypatch.setattr(settings, "TRIAL_DEFAULT_PASSWORD", "12345")
    monkeypatch.setattr(settings, "ENVIRONMENT", "development")

    # 1. Create employee
    admin_headers = get_admin_headers(client, test_org_setup["admin"])
    emp_payload = {
        "company_id": str(test_org_setup["company"].company_id),
        "department_id": str(test_org_setup["department"].department_id),
        "designation_id": str(test_org_setup["designation"].designation_id),
        "first_name": "Aakash",
        "last_name": "Gupta",
        "official_email": f"aakash.{uuid.uuid4().hex[:6]}@trialorg.com",
        "mobile_number": "+919855566677",
        "date_of_joining": "2026-03-01",
        "employment_type": "FULL_TIME",
        "account_status": "ACTIVE",
    }
    create_resp = client.post("/api/admin/employees", json=emp_payload, headers=admin_headers)
    assert create_resp.status_code == 201, create_resp.text
    emp_data = create_resp.json()
    emp_id = emp_data["user_id"]
    emp_code = emp_data["employee_code"]

    # Also grant Aakash view permission on ADMIN_EMPLOYEES for later test
    grant_or_update_permission(
        session=db_session,
        user_id=uuid.UUID(emp_id),
        module_id=test_org_setup["employees_module"].module_id,
        can_view=True,
        can_create=False,
        can_edit=False,
        can_delete=False,
        can_approve=False,
        data_scope="SELF",
        granted_by_user_id=test_org_setup["admin"].user_id,
        is_bootstrap=True,
    )
    db_session.commit()

    # 2. Login with temporary trial password
    login_resp = client.post(
        "/api/auth/login",
        json={"identifier": emp_code, "password": "12345"},
    )
    assert login_resp.status_code == 200, login_resp.text
    login_data = login_resp.json()
    assert login_data["must_change_password"] is True
    restricted_token = login_data["access_token"]
    restricted_headers = {"Authorization": f"Bearer {restricted_token}"}

    # 3. Restricted session is blocked from business endpoints
    # Check /me/modules -> 403
    mod_resp = client.get("/api/auth/me/modules", headers=restricted_headers)
    assert mod_resp.status_code == 403
    assert "password change required" in mod_resp.json()["detail"].lower()

    # Check /admin/employees -> 403
    list_resp = client.get("/api/admin/employees", headers=restricted_headers)
    assert list_resp.status_code == 403
    assert "password change required" in list_resp.json()["detail"].lower()

    # 4. /me is accessible
    me_resp = client.get("/api/auth/me", headers=restricted_headers)
    assert me_resp.status_code == 200
    assert me_resp.json()["employee_code"] == emp_code
    assert me_resp.json()["must_change_password"] is True

    # 5. Weak new password is rejected (too short -> 422, lacking complexity -> 400)
    short_resp = client.post(
        "/api/auth/change-initial-password",
        json={"new_password": "weak", "confirm_password": "weak"},
        headers=restricted_headers,
    )
    assert short_resp.status_code == 422

    weak_complexity_resp = client.post(
        "/api/auth/change-initial-password",
        json={"new_password": "weakpasswordhere", "confirm_password": "weakpasswordhere"},
        headers=restricted_headers,
    )
    assert weak_complexity_resp.status_code == 400
    assert "complexity" in weak_complexity_resp.json()["detail"].lower() or "password" in weak_complexity_resp.json()["detail"].lower()

    # Same/default password is rejected
    same_resp = client.post(
        "/api/auth/change-initial-password",
        json={"new_password": "12345", "confirm_password": "12345"},
        headers=restricted_headers,
    )
    assert same_resp.status_code in {400, 422}

    # Mismatched confirmation is rejected
    mismatch_resp = client.post(
        "/api/auth/change-initial-password",
        json={"new_password": "AakashSecure@2026", "confirm_password": "DifferentPassword#1"},
        headers=restricted_headers,
    )
    assert mismatch_resp.status_code == 400

    # Valid change initial password
    change_resp = client.post(
        "/api/auth/change-initial-password",
        json={
            "current_password": "12345",
            "new_password": "AakashSecure@2026",
            "confirm_password": "AakashSecure@2026",
        },
        headers=restricted_headers,
    )
    assert change_resp.status_code == 200, change_resp.text

    # 6. Old temporary password '12345' no longer works
    old_login = client.post(
        "/api/auth/login",
        json={"identifier": emp_code, "password": "12345"},
    )
    assert old_login.status_code == 401

    # 7. New password works and must_change_password is False
    new_login = client.post(
        "/api/auth/login",
        json={"identifier": emp_code, "password": "AakashSecure@2026"},
    )
    assert new_login.status_code == 200
    new_data = new_login.json()
    assert new_data["must_change_password"] is False
    active_token = new_data["access_token"]
    active_headers = {"Authorization": f"Bearer {active_token}"}

    # 8. Full CRM access now works
    active_mod_resp = client.get("/api/auth/me/modules", headers=active_headers)
    assert active_mod_resp.status_code == 200
    modules = active_mod_resp.json()
    assert len(modules) > 0

    active_emp_list = client.get("/api/admin/employees", headers=active_headers)
    assert active_emp_list.status_code == 200
    assert active_emp_list.json()["total"] >= 1


def test_super_admin_unaffected_by_trial_mode(client: TestClient, test_org_setup, monkeypatch):
    """Test that Super Admin with pre-existing password logs in directly with must_change_password=False."""
    monkeypatch.setattr(settings, "TRIAL_DEFAULT_PASSWORD_ENABLED", True)
    monkeypatch.setattr(settings, "TRIAL_DEFAULT_PASSWORD", "12345")

    admin = test_org_setup["admin"]
    resp = client.post(
        "/api/auth/login",
        json={"identifier": admin.official_email, "password": "AdminSecure@2026"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["must_change_password"] is False

    # Super admin can directly access protected modules
    headers = {"Authorization": f"Bearer {data['access_token']}"}
    emp_list = client.get("/api/admin/employees", headers=headers)
    assert emp_list.status_code == 200
