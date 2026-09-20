"""Comprehensive tests for Admin Lookup API endpoints and Accessible Modules endpoint."""
import uuid
from datetime import date, datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.api.deps import get_current_active_user, get_db
from app.main import app
from app.models.company import Company
from app.models.department import Department
from app.models.designation import Designation
from app.models.user import User
from app.schemas.permission import AccessibleModuleRead
from app.services.permissions import DataScopeContext


@pytest.fixture
def client() -> TestClient:
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def mock_db_session() -> MagicMock:
    return MagicMock()


@pytest.fixture
def test_company_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def test_department_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def test_designation_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def active_user(test_company_id: uuid.UUID, test_department_id: uuid.UUID, test_designation_id: uuid.UUID) -> User:
    return User(
        user_id=uuid.uuid4(),
        employee_code="CG0001",
        company_id=test_company_id,
        department_id=test_department_id,
        designation_id=test_designation_id,
        first_name="Admin",
        last_name="Director",
        official_email="director@gocompliances.in",
        mobile_number="+919876543210",
        date_of_joining=date(2026, 1, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


def test_lookup_endpoints_require_authentication(client: TestClient) -> None:
    """Verify all lookup endpoints return 401 Unauthorized without auth headers."""
    assert client.get("/api/admin/lookup/companies").status_code == status.HTTP_401_UNAUTHORIZED
    assert client.get("/api/admin/lookup/departments").status_code == status.HTTP_401_UNAUTHORIZED
    assert client.get("/api/admin/lookup/designations").status_code == status.HTTP_401_UNAUTHORIZED
    assert client.get("/api/admin/lookup/managers").status_code == status.HTTP_401_UNAUTHORIZED


def test_lookup_endpoints_require_view_permission(
    client: TestClient,
    active_user: User,
    mock_db_session: MagicMock,
) -> None:
    """Verify lookup endpoints return 403 Forbidden when user lacks ADMIN_EMPLOYEES view permission."""
    app.dependency_overrides[get_current_active_user] = lambda: active_user
    app.dependency_overrides[get_db] = lambda: mock_db_session

    with patch("app.services.permissions.has_permission", return_value=False):
        res = client.get("/api/admin/lookup/companies")
        assert res.status_code == status.HTTP_403_FORBIDDEN

    app.dependency_overrides.clear()


def test_lookup_companies_success(
    client: TestClient,
    active_user: User,
    test_company_id: uuid.UUID,
    mock_db_session: MagicMock,
) -> None:
    """Verify companies lookup returns active companies matching data scope."""
    app.dependency_overrides[get_current_active_user] = lambda: active_user
    app.dependency_overrides[get_db] = lambda: mock_db_session

    mock_company = Company(
        company_id=test_company_id,
        company_code="GOCOMPLIANCES",
        company_name="Gocompliances",
        employee_code_prefix="CG",
        status="ACTIVE",
    )

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_company]
    mock_db_session.execute.return_value = mock_result

    with patch("app.services.permissions.has_permission", return_value=True), \
         patch("app.services.permissions.resolve_data_scope_context", return_value=DataScopeContext(
             scope="ALL",
             user_id=active_user.user_id,
             company_id=test_company_id,
             department_id=active_user.department_id,
         )):
        res = client.get("/api/admin/lookup/companies")
        assert res.status_code == status.HTTP_200_OK
        data = res.json()
        assert len(data) == 1
        assert data[0]["company_code"] == "GOCOMPLIANCES"
        assert data[0]["employee_code_prefix"] == "CG"

    app.dependency_overrides.clear()


def test_lookup_departments_success(
    client: TestClient,
    active_user: User,
    test_company_id: uuid.UUID,
    test_department_id: uuid.UUID,
    mock_db_session: MagicMock,
) -> None:
    """Verify departments lookup returns active departments filtered by company_id."""
    app.dependency_overrides[get_current_active_user] = lambda: active_user
    app.dependency_overrides[get_db] = lambda: mock_db_session

    mock_dept = Department(
        department_id=test_department_id,
        company_id=test_company_id,
        department_code="SALES",
        department_name="Sales",
        status="ACTIVE",
    )

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_dept]
    mock_db_session.execute.return_value = mock_result

    with patch("app.services.permissions.has_permission", return_value=True), \
         patch("app.services.permissions.resolve_data_scope_context", return_value=DataScopeContext(
             scope="ALL",
             user_id=active_user.user_id,
             company_id=test_company_id,
             department_id=test_department_id,
         )):
        res = client.get(f"/api/admin/lookup/departments?company_id={test_company_id}")
        assert res.status_code == status.HTTP_200_OK
        data = res.json()
        assert len(data) == 1
        assert data[0]["department_code"] == "SALES"
        assert data[0]["department_name"] == "Sales"

    app.dependency_overrides.clear()


def test_lookup_designations_success(
    client: TestClient,
    active_user: User,
    test_company_id: uuid.UUID,
    test_designation_id: uuid.UUID,
    mock_db_session: MagicMock,
) -> None:
    """Verify designations lookup returns active designations filtered by company_id."""
    app.dependency_overrides[get_current_active_user] = lambda: active_user
    app.dependency_overrides[get_db] = lambda: mock_db_session

    mock_desig = Designation(
        designation_id=test_designation_id,
        company_id=test_company_id,
        designation_code="MANAGER",
        designation_name="Manager",
        level_rank=5,
        is_managerial=True,
        status="ACTIVE",
    )

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_desig]
    mock_db_session.execute.return_value = mock_result

    with patch("app.services.permissions.has_permission", return_value=True), \
         patch("app.services.permissions.resolve_data_scope_context", return_value=DataScopeContext(
             scope="ALL",
             user_id=active_user.user_id,
             company_id=test_company_id,
             department_id=active_user.department_id,
         )):
        res = client.get(f"/api/admin/lookup/designations?company_id={test_company_id}")
        assert res.status_code == status.HTTP_200_OK
        data = res.json()
        assert len(data) == 1
        assert data[0]["designation_code"] == "MANAGER"
        assert data[0]["is_managerial"] is True

    app.dependency_overrides.clear()


def test_lookup_managers_success(
    client: TestClient,
    active_user: User,
    test_company_id: uuid.UUID,
    mock_db_session: MagicMock,
) -> None:
    """Verify managers lookup returns active managers filtered by company and excluding target user."""
    app.dependency_overrides[get_current_active_user] = lambda: active_user
    app.dependency_overrides[get_db] = lambda: mock_db_session

    manager_id = uuid.uuid4()
    mock_row = MagicMock()
    mock_row.user_id = manager_id
    mock_row.employee_code = "CG0002"
    mock_row.first_name = "Senior"
    mock_row.middle_name = None
    mock_row.last_name = "Leader"
    mock_row.official_email = "leader@gocompliances.in"
    mock_row.department_name = "Administration"
    mock_row.designation_name = "Director"

    mock_result = MagicMock()
    mock_result.all.return_value = [mock_row]
    mock_db_session.execute.return_value = mock_result

    with patch("app.services.permissions.has_permission", return_value=True), \
         patch("app.services.permissions.resolve_data_scope_context", return_value=DataScopeContext(
             scope="ALL",
             user_id=active_user.user_id,
             company_id=test_company_id,
             department_id=active_user.department_id,
         )):
        res = client.get(f"/api/admin/lookup/managers?company_id={test_company_id}&exclude_user_id={active_user.user_id}")
        assert res.status_code == status.HTTP_200_OK
        data = res.json()
        assert len(data) == 1
        assert data[0]["employee_code"] == "CG0002"
        assert data[0]["official_email"] == "leader@gocompliances.in"

    app.dependency_overrides.clear()


def test_get_current_user_accessible_modules(
    client: TestClient,
    active_user: User,
    mock_db_session: MagicMock,
) -> None:
    """Verify GET /api/auth/me/modules returns list of user accessible modules."""
    app.dependency_overrides[get_current_active_user] = lambda: active_user
    app.dependency_overrides[get_db] = lambda: mock_db_session

    mock_module_read = AccessibleModuleRead(
        module_id=uuid.uuid4(),
        module_code="ADMIN_EMPLOYEES",
        module_name="Employee Management",
        parent_module_id=None,
        route="/employees",
        display_order=1,
        is_navigation=True,
        can_view=True,
        can_create=True,
        can_edit=True,
        can_delete=False,
        can_approve=True,
        data_scope="ALL",
    )

    with patch("app.services.permissions.get_accessible_modules", return_value=[mock_module_read]):
        res = client.get("/api/auth/me/modules")
        assert res.status_code == status.HTTP_200_OK
        data = res.json()
        assert len(data) == 1
        assert data[0]["module_code"] == "ADMIN_EMPLOYEES"
        assert data[0]["can_create"] is True
        assert data[0]["can_approve"] is True

    app.dependency_overrides.clear()
