"""Unit tests for Authentication APIs, services, lockout protection, and refresh token rotation."""
import ast
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import MagicMock
import uuid

import pytest
from alembic.config import Config
from alembic.script import ScriptDirectory
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    hash_refresh_token,
)
from app.main import app
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.schemas.auth import (
    ChangePasswordRequest,
    CurrentUserRead,
    LoginRequest,
    LogoutRequest,
    RefreshTokenRequest,
    TokenResponse,
)
from app.services.auth_service import (
    authenticate_user,
    change_user_password,
    logout_user,
    refresh_access_token,
)

client = TestClient(app)


def test_auth_refresh_token_model_structure() -> None:
    """Verify RefreshToken model columns and foreign key cascade behavior."""
    table = RefreshToken.__table__
    cols = table.columns

    assert "refresh_token_id" in cols
    assert "user_id" in cols
    assert "jti" in cols
    assert "token_hash" in cols
    assert "issued_at" in cols
    assert "expires_at" in cols
    assert "revoked_at" in cols
    assert "replaced_by_jti" in cols
    assert "created_ip" in cols
    assert "user_agent" in cols

    fks = {fk.name: fk for fk in table.foreign_key_constraints}
    assert "fk_refresh_token_user_id" in fks
    assert fks["fk_refresh_token_user_id"].ondelete == "CASCADE"


def test_user_model_auth_columns_and_constraints() -> None:
    """Verify User model has all required Stage 7B authentication fields and check constraints."""
    table = User.__table__
    cols = table.columns

    assert cols["password_hash"].nullable is True
    assert cols["must_change_password"].nullable is False
    assert cols["failed_login_attempts"].nullable is False
    assert cols["locked_until"].nullable is True
    assert cols["last_login_at"].nullable is True
    assert cols["password_changed_at"].nullable is True
    assert cols["token_version"].nullable is False

    checks = {c.name: c for c in table.constraints if hasattr(c, "name")}
    assert "chk_user_failed_login_attempts_non_negative" in checks
    assert "chk_user_token_version_positive" in checks


def test_authenticate_user_by_email_and_employee_code() -> None:
    """Verify successful authentication with both email and employee code (case-insensitive)."""
    mock_session = MagicMock()
    user_id = uuid.uuid4()
    plain_pw = "ValidPassword123!@"
    user = User(
        user_id=user_id,
        employee_code="CG0001",
        official_email="director@gocompliances.in",
        first_name="Amit",
        last_name="Sharma",
        password_hash=hash_password(plain_pw),
        account_status="ACTIVE",
        must_change_password=True,
        failed_login_attempts=0,
        locked_until=None,
        token_version=1,
    )

    # 1. Login with official_email
    mock_session.execute.return_value.scalar_one_or_none.return_value = user
    auth_user, token_resp = authenticate_user(
        session=mock_session,
        identifier="  DIRECTOR@GoCompliances.IN  ",
        password=plain_pw,
        client_ip="127.0.0.1",
        user_agent="pytest-client",
    )
    assert auth_user.user_id == user_id
    assert token_resp.access_token is not None
    assert token_resp.refresh_token is not None
    assert token_resp.must_change_password is True
    assert mock_session.commit.call_count == 1

    # 2. Login with employee_code
    mock_session.reset_mock()
    mock_session.execute.return_value.scalar_one_or_none.return_value = user
    auth_user, token_resp = authenticate_user(
        session=mock_session,
        identifier="  cg0001 ",
        password=plain_pw,
    )
    assert auth_user.user_id == user_id
    assert token_resp.access_token is not None


def test_authenticate_user_invalid_credentials_and_lockout() -> None:
    """Verify wrong password increments failed attempts and locks account at threshold."""
    mock_session = MagicMock()
    plain_pw = "CorrectPass123!@"
    user = User(
        user_id=uuid.uuid4(),
        employee_code="CG0001",
        official_email="director@gocompliances.in",
        password_hash=hash_password(plain_pw),
        account_status="ACTIVE",
        failed_login_attempts=4,  # Next failure triggers lockout
        locked_until=None,
        token_version=1,
    )
    mock_session.execute.return_value.scalar_one_or_none.return_value = user

    # Attempt 5: wrong password
    with pytest.raises(HTTPException) as exc_info:
        authenticate_user(
            session=mock_session,
            identifier="CG0001",
            password="WrongPassword123!",
        )
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid credentials"
    assert user.failed_login_attempts == 5
    assert user.locked_until is not None  # Locked!

    # Attempt while locked
    with pytest.raises(HTTPException) as exc_info:
        authenticate_user(
            session=mock_session,
            identifier="CG0001",
            password=plain_pw,
        )
    assert exc_info.value.status_code == 401
    assert "temporarily locked" in exc_info.value.detail


def test_authenticate_user_inactive_or_unactivated_rejection() -> None:
    """Verify inactive/pending accounts or accounts without password cannot log in."""
    mock_session = MagicMock()
    plain_pw = "ValidPass123!@"

    # Inactive account
    inactive_user = User(
        user_id=uuid.uuid4(),
        employee_code="CG0002",
        official_email="inactive@gocompliances.in",
        password_hash=hash_password(plain_pw),
        account_status="INACTIVE",
        failed_login_attempts=0,
        locked_until=None,
    )
    mock_session.execute.return_value.scalar_one_or_none.return_value = inactive_user

    with pytest.raises(HTTPException) as exc_info:
        authenticate_user(
            session=mock_session,
            identifier="CG0002",
            password=plain_pw,
        )
    assert exc_info.value.status_code == 401
    assert "Account is not active" in exc_info.value.detail

    # Unactivated account (no password_hash)
    unactivated_user = User(
        user_id=uuid.uuid4(),
        employee_code="CG0003",
        official_email="new@gocompliances.in",
        password_hash=None,
        account_status="ACTIVE",
    )
    mock_session.execute.return_value.scalar_one_or_none.return_value = unactivated_user
    with pytest.raises(HTTPException) as exc_info:
        authenticate_user(
            session=mock_session,
            identifier="CG0003",
            password=plain_pw,
        )
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid credentials"


def test_refresh_token_rotation_and_revocation() -> None:
    """Verify refresh token rotation issues a new token pair and marks previous token revoked."""
    mock_session = MagicMock()
    user_id = uuid.uuid4()
    user = User(
        user_id=user_id,
        employee_code="CG0001",
        account_status="ACTIVE",
        token_version=1,
        must_change_password=False,
    )

    raw_refresh, jti, expires_at = create_refresh_token(user_id=user_id, token_version=1)
    db_token = RefreshToken(
        refresh_token_id=uuid.uuid4(),
        user_id=user_id,
        jti=jti,
        token_hash=hash_refresh_token(raw_refresh),
        expires_at=expires_at,
        revoked_at=None,
    )

    mock_session.get.return_value = user
    mock_session.execute.return_value.scalar_one_or_none.return_value = db_token

    rotated = refresh_access_token(
        session=mock_session,
        raw_refresh_token=raw_refresh,
    )
    assert rotated.access_token is not None
    assert rotated.refresh_token != raw_refresh
    assert db_token.revoked_at is not None
    assert db_token.replaced_by_jti is not None
    assert mock_session.commit.call_count == 1


def test_refresh_token_reuse_attack_detection() -> None:
    """Verify presenting an already revoked token triggers reuse detection and revokes all user sessions."""
    mock_session = MagicMock()
    user_id = uuid.uuid4()
    user = User(
        user_id=user_id,
        employee_code="CG0001",
        account_status="ACTIVE",
        token_version=1,
    )

    raw_refresh, jti, expires_at = create_refresh_token(user_id=user_id, token_version=1)
    # Already revoked token
    db_token = RefreshToken(
        refresh_token_id=uuid.uuid4(),
        user_id=user_id,
        jti=jti,
        token_hash=hash_refresh_token(raw_refresh),
        expires_at=expires_at,
        revoked_at=datetime.now(timezone.utc),
    )

    mock_session.get.return_value = user
    mock_session.execute.return_value.scalar_one_or_none.return_value = db_token

    with pytest.raises(HTTPException) as exc_info:
        refresh_access_token(
            session=mock_session,
            raw_refresh_token=raw_refresh,
        )
    assert exc_info.value.status_code == 401
    assert "Revoked refresh token presented" in exc_info.value.detail
    assert user.token_version == 2  # Incremented to invalidate all active sessions!


def test_logout_revokes_token() -> None:
    """Verify logout updates revoked_at on the active refresh token."""
    mock_session = MagicMock()
    user_id = uuid.uuid4()
    raw_refresh, jti, _ = create_refresh_token(user_id=user_id, token_version=1)

    logout_user(session=mock_session, raw_refresh_token=raw_refresh)
    assert mock_session.execute.call_count == 1
    assert mock_session.commit.call_count == 1


def test_change_user_password_success_and_session_invalidation() -> None:
    """Verify password change updates hash, sets must_change_password=False, and increments token_version."""
    mock_session = MagicMock()
    old_pw = "OldPassword123!@"
    new_pw = "NewPassword2026!#"
    user = User(
        user_id=uuid.uuid4(),
        employee_code="CG0001",
        password_hash=hash_password(old_pw),
        must_change_password=True,
        token_version=1,
    )

    change_user_password(
        session=mock_session,
        user=user,
        current_password=old_pw,
        new_password=new_pw,
    )

    assert user.must_change_password is False
    assert user.token_version == 2
    assert user.password_changed_at is not None
    assert mock_session.commit.call_count == 1


def test_change_user_password_rejects_same_password() -> None:
    """Verify change_password rejects new password identical to current password."""
    mock_session = MagicMock()
    pw = "IdenticalPass123!@"
    user = User(
        user_id=uuid.uuid4(),
        employee_code="CG0001",
        password_hash=hash_password(pw),
        must_change_password=True,
        token_version=1,
    )

    with pytest.raises(HTTPException) as exc_info:
        change_user_password(
            session=mock_session,
            user=user,
            current_password=pw,
            new_password=pw,
        )
    assert exc_info.value.status_code == 400
    assert "cannot be identical" in exc_info.value.detail


def test_auth_api_routes_registered() -> None:
    """Verify that all Stage 7B authentication routes are mounted on the FastAPI application."""
    openapi_paths = app.openapi()["paths"]
    assert "/api/auth/login" in openapi_paths
    assert "/api/auth/refresh" in openapi_paths
    assert "/api/auth/logout" in openapi_paths
    assert "/api/auth/me" in openapi_paths
    assert "/api/auth/change-password" in openapi_paths


def test_auth_migration_creates_only_auth_objects() -> None:
    """Verify that the Stage 7B migration touches only auth_refresh_token and user_master auth fields."""
    backend_dir = Path(__file__).resolve().parent.parent
    ini_path = backend_dir / "alembic.ini"
    cfg = Config(str(ini_path))
    cfg.set_main_option("script_location", str(backend_dir / "alembic"))

    script_dir = ScriptDirectory.from_config(cfg)
    revisions = list(script_dir.walk_revisions())

    auth_rev = next((r for r in revisions if "add_authentication_foundation" in (r.doc or "")), None)
    assert auth_rev is not None, "add_authentication_foundation revision must exist"

    # Verify down_revision is Stage 7A revision (create_user_master)
    user_rev = next((r for r in revisions if "create_user_master" in (r.doc or "")), None)
    assert auth_rev.down_revision == user_rev.revision

    migration_file = Path(auth_rev.path)
    content = migration_file.read_text(encoding="utf-8")

    tree = ast.parse(content)
    created_tables = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr == "create_table" and node.args:
                if isinstance(node.args[0], ast.Constant):
                    created_tables.append(node.args[0].value)

    assert created_tables == ["auth_refresh_token"]


def test_bootstrap_admin_script_import_safety() -> None:
    """Verify bootstrap_admin script imports safely without executing automatically."""
    import app.scripts.bootstrap_admin as bootstrap_module
    assert hasattr(bootstrap_module, "bootstrap_admin")


def test_auth_me_returns_department_info() -> None:
    """Verify /api/auth/me returns resolved department, company, and designation info."""
    from app.api.deps import get_current_active_user, get_db
    from app.models.company import Company
    from app.models.department import Department
    from app.models.designation import Designation

    dept_id = uuid.uuid4()
    comp_id = uuid.uuid4()
    desig_id = uuid.uuid4()

    mock_dept = Department(department_id=dept_id, department_code="SALES", department_name="Sales")
    mock_comp = Company(company_id=comp_id, company_code="GOCOMP", company_name="GoCompliance")
    mock_desig = Designation(designation_id=desig_id, designation_code="SR_EXEC", designation_name="Senior Executive")

    mock_user = User(
        user_id=uuid.uuid4(),
        employee_code="CG0004",
        first_name="Karishma",
        last_name="Upadhyay",
        official_email="karishma@gocompliances.in",
        department_id=dept_id,
        company_id=comp_id,
        designation_id=desig_id,
        account_status="ACTIVE",
        must_change_password=False,
    )

    mock_session = MagicMock()
    def mock_get(entity, entity_id):
        if entity == Department and entity_id == dept_id:
            return mock_dept
        if entity == Company and entity_id == comp_id:
            return mock_comp
        if entity == Designation and entity_id == desig_id:
            return mock_desig
        return None

    mock_session.get.side_effect = mock_get

    app.dependency_overrides[get_current_active_user] = lambda: mock_user
    app.dependency_overrides[get_db] = lambda: mock_session

    try:
        response = client.get("/api/auth/me")
        assert response.status_code == 200
        data = response.json()

        assert data["employee_code"] == "CG0004"
        assert data["first_name"] == "Karishma"
        assert data["last_name"] == "Upadhyay"
        assert data["department_name"] == "Sales"
        assert data["department_code"] == "SALES"
        assert data["department"] == {
            "id": str(dept_id),
            "code": "SALES",
            "name": "Sales",
        }
        assert data["company"]["name"] == "GoCompliance"
        assert data["designation"]["name"] == "Senior Executive"
    finally:
        app.dependency_overrides.clear()


def test_auth_me_missing_department_returns_null_safe() -> None:
    """Verify /api/auth/me returns null for department when unassigned, never defaulting to Administration."""
    from app.api.deps import get_current_active_user, get_db

    mock_user = User(
        user_id=uuid.uuid4(),
        employee_code="CG9999",
        first_name="Unassigned",
        last_name="Employee",
        official_email="unassigned@gocompliances.in",
        department_id=None,
        company_id=None,
        designation_id=None,
        account_status="ACTIVE",
        must_change_password=False,
    )

    mock_session = MagicMock()
    mock_session.get.return_value = None

    app.dependency_overrides[get_current_active_user] = lambda: mock_user
    app.dependency_overrides[get_db] = lambda: mock_session

    try:
        response = client.get("/api/auth/me")
        assert response.status_code == 200
        data = response.json()

        assert data["employee_code"] == "CG9999"
        assert data["department"] is None
        assert data["department_name"] is None
        assert data["department_code"] is None
        assert data["company"] is None
        assert data["designation"] is None
    finally:
        app.dependency_overrides.clear()
