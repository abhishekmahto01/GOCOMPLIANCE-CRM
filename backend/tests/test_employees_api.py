"""Comprehensive tests for authorized Employee CRUD API endpoints (Stage 7C)."""
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
from app.models.user_module_permission import UserModulePermission
from app.schemas.user import EmployeeRead, PaginatedEmployeesResponse, UserCreate


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
def active_admin_user(test_company_id: uuid.UUID, test_department_id: uuid.UUID, test_designation_id: uuid.UUID) -> User:
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


# ==============================================================================
# Authentication & Permission Gate Tests
# ==============================================================================

def test_unauthenticated_requests_rejected(client: TestClient) -> None:
    """Verify all employee endpoints return 401 Unauthorized without auth headers."""
    random_id = uuid.uuid4()

    assert client.post("/api/admin/employees", json={}).status_code == status.HTTP_401_UNAUTHORIZED
    assert client.get("/api/admin/employees").status_code == status.HTTP_401_UNAUTHORIZED
    assert client.get(f"/api/admin/employees/{random_id}").status_code == status.HTTP_401_UNAUTHORIZED
    assert client.patch(f"/api/admin/employees/{random_id}", json={}).status_code == status.HTTP_401_UNAUTHORIZED
    assert client.patch(f"/api/admin/employees/{random_id}/status", json={}).status_code == status.HTTP_401_UNAUTHORIZED


def test_missing_module_permission_rejected(
    client: TestClient,
    active_admin_user: User,
    mock_db_session: MagicMock,
) -> None:
    """Verify requests return 403 Forbidden if user lacks ADMIN_EMPLOYEES permission."""
    app.dependency_overrides[get_current_active_user] = lambda: active_admin_user
    app.dependency_overrides[get_db] = lambda: mock_db_session

    with patch("app.services.permissions.has_permission", return_value=False):
        response = client.get("/api/admin/employees")
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Access denied for module 'ADMIN_EMPLOYEES'" in response.json()["detail"]

    app.dependency_overrides.clear()


def test_missing_specific_action_permission_rejected(
    client: TestClient,
    active_admin_user: User,
    mock_db_session: MagicMock,
) -> None:
    """Verify 403 Forbidden when user has view but lacks create, edit, or approve."""
    app.dependency_overrides[get_current_active_user] = lambda: active_admin_user
    app.dependency_overrides[get_db] = lambda: mock_db_session

    # 1. User has view=True, create=False -> POST fails
    def mock_has_perm(session, user, mod, action):
        return action == "view"

    with patch("app.services.permissions.has_permission", side_effect=mock_has_perm):
        # Create fails
        res_create = client.post("/api/admin/employees", json={})
        assert res_create.status_code == status.HTTP_403_FORBIDDEN

        # Edit fails
        res_edit = client.patch(f"/api/admin/employees/{uuid.uuid4()}", json={"first_name": "New"})
        assert res_edit.status_code == status.HTTP_403_FORBIDDEN

        # Approve/status fails
        res_status = client.patch(f"/api/admin/employees/{uuid.uuid4()}/status", json={"account_status": "INACTIVE"})
        assert res_status.status_code == status.HTTP_403_FORBIDDEN

    app.dependency_overrides.clear()


# ==============================================================================
# Employee Creation Tests (POST /api/admin/employees)
# ==============================================================================

def test_successful_employee_creation(
    client: TestClient,
    active_admin_user: User,
    mock_db_session: MagicMock,
    test_company_id: uuid.UUID,
    test_department_id: uuid.UUID,
    test_designation_id: uuid.UUID,
) -> None:
    """Verify successful employee creation with generated employee code and relation labels."""
    app.dependency_overrides[get_current_active_user] = lambda: active_admin_user
    app.dependency_overrides[get_db] = lambda: mock_db_session

    created_user_id = uuid.uuid4()
    mock_company = Company(
        company_id=test_company_id,
        company_code="GOCOMPLIANCES",
        company_name="Gocompliances",
        employee_code_prefix="CG",
        next_employee_number=2,
        status="ACTIVE",
    )
    mock_dept = Department(
        department_id=test_department_id,
        company_id=test_company_id,
        department_code="SALES",
        department_name="Sales",
        status="ACTIVE",
    )
    mock_desig = Designation(
        designation_id=test_designation_id,
        company_id=test_company_id,
        designation_code="EXECUTIVE",
        designation_name="Sales Executive",
        level_rank=1,
        status="ACTIVE",
    )
    mock_created_user = User(
        user_id=created_user_id,
        employee_code="CG0002",
        company_id=test_company_id,
        department_id=test_department_id,
        designation_id=test_designation_id,
        first_name="Rohan",
        last_name="Verma",
        official_email="rohan@gocompliances.in",
        mobile_number="+919876543299",
        date_of_joining=date(2026, 2, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        company=mock_company,
        department=mock_dept,
        designation=mock_desig,
    )

    payload = {
        "company_id": str(test_company_id),
        "department_id": str(test_department_id),
        "designation_id": str(test_designation_id),
        "first_name": "Rohan",
        "last_name": "Verma",
        "official_email": "rohan@gocompliances.in",
        "mobile_number": "+919876543299",
        "date_of_joining": "2026-02-01",
        "employment_type": "FULL_TIME",
        "account_status": "ACTIVE",
    }

    with patch("app.services.permissions.has_permission", return_value=True), \
         patch("app.services.user_service.create_user", return_value=mock_created_user), \
         patch("app.services.user_service.get_employee_by_id", return_value=mock_created_user):
        response = client.post("/api/admin/employees", json=payload)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["employee_code"] == "CG0002"
        assert data["first_name"] == "Rohan"
        assert data["official_email"] == "rohan@gocompliances.in"
        assert data["company_name"] == "Gocompliances"
        assert data["department_name"] == "Sales"
        assert data["designation_name"] == "Sales Executive"
        assert "password_hash" not in data

    app.dependency_overrides.clear()


def test_employee_creation_rejects_client_employee_code(
    client: TestClient,
    active_admin_user: User,
    mock_db_session: MagicMock,
    test_company_id: uuid.UUID,
    test_department_id: uuid.UUID,
    test_designation_id: uuid.UUID,
) -> None:
    """Verify that client cannot supply employee_code during creation."""
    app.dependency_overrides[get_current_active_user] = lambda: active_admin_user
    app.dependency_overrides[get_db] = lambda: mock_db_session

    payload = {
        "employee_code": "CUSTOM01",  # Forbidden field
        "company_id": str(test_company_id),
        "department_id": str(test_department_id),
        "designation_id": str(test_designation_id),
        "first_name": "Rohan",
        "last_name": "Verma",
        "official_email": "rohan@gocompliances.in",
        "mobile_number": "+919876543299",
        "date_of_joining": "2026-02-01",
        "employment_type": "FULL_TIME",
        "account_status": "ACTIVE",
    }

    with patch("app.services.permissions.has_permission", return_value=True):
        response = client.post("/api/admin/employees", json=payload)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    app.dependency_overrides.clear()


def test_employee_creation_duplicate_email_409(
    client: TestClient,
    active_admin_user: User,
    mock_db_session: MagicMock,
    test_company_id: uuid.UUID,
    test_department_id: uuid.UUID,
    test_designation_id: uuid.UUID,
) -> None:
    """Verify duplicate official email raises 409 Conflict."""
    app.dependency_overrides[get_current_active_user] = lambda: active_admin_user
    app.dependency_overrides[get_db] = lambda: mock_db_session

    payload = {
        "company_id": str(test_company_id),
        "department_id": str(test_department_id),
        "designation_id": str(test_designation_id),
        "first_name": "Rohan",
        "last_name": "Verma",
        "official_email": "director@gocompliances.in",
        "mobile_number": "+919876543299",
        "date_of_joining": "2026-02-01",
        "employment_type": "FULL_TIME",
        "account_status": "ACTIVE",
    }

    with patch("app.services.permissions.has_permission", return_value=True), \
         patch("app.services.user_service.create_user", side_effect=ValueError("Official email 'director@gocompliances.in' is already registered")):
        response = client.post("/api/admin/employees", json=payload)
        assert response.status_code == status.HTTP_409_CONFLICT
        assert "already registered" in response.json()["detail"]

    app.dependency_overrides.clear()


# ==============================================================================
# Employee Listing Tests (GET /api/admin/employees)
# ==============================================================================

def test_list_employees_pagination_and_scoping(
    client: TestClient,
    active_admin_user: User,
    mock_db_session: MagicMock,
    test_company_id: uuid.UUID,
    test_department_id: uuid.UUID,
    test_designation_id: uuid.UUID,
) -> None:
    """Verify GET /api/admin/employees returns PaginatedEmployeesResponse."""
    app.dependency_overrides[get_current_active_user] = lambda: active_admin_user
    app.dependency_overrides[get_db] = lambda: mock_db_session

    mock_scope_ctx = MagicMock(scope="ALL")

    with patch("app.services.permissions.has_permission", return_value=True), \
         patch("app.services.permissions.resolve_data_scope_context", return_value=mock_scope_ctx), \
         patch("app.services.user_service.list_employees", return_value=([active_admin_user], 1, 1)):
        response = client.get("/api/admin/employees?page=1&page_size=20")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 20
        assert data["total"] == 1
        assert data["pages"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["employee_code"] == "CG0001"

    app.dependency_overrides.clear()


# ==============================================================================
# Employee Detail Tests (GET /api/admin/employees/{user_id})
# ==============================================================================

def test_get_employee_detail_success_404_and_403(
    client: TestClient,
    active_admin_user: User,
    mock_db_session: MagicMock,
) -> None:
    """Verify detail endpoint returns 200 within scope, 404 for missing, and 403 for out-of-scope."""
    app.dependency_overrides[get_current_active_user] = lambda: active_admin_user
    app.dependency_overrides[get_db] = lambda: mock_db_session

    other_user_id = uuid.uuid4()
    other_user = User(
        user_id=other_user_id,
        employee_code="EP0001",
        company_id=uuid.uuid4(),
        department_id=uuid.uuid4(),
        designation_id=uuid.uuid4(),
        first_name="Other",
        last_name="Person",
        official_email="other@enterpernership.in",
        mobile_number="+919999999999",
        date_of_joining=date(2026, 1, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    # 1. 404 Not Found
    with patch("app.services.permissions.has_permission", return_value=True), \
         patch("app.services.user_service.get_employee_by_id", return_value=None):
        res_404 = client.get(f"/api/admin/employees/{uuid.uuid4()}")
        assert res_404.status_code == status.HTTP_404_NOT_FOUND

    # 2. 403 Forbidden (Exists but outside caller's scope)
    mock_scope_ctx_self = MagicMock()
    mock_scope_ctx_self.is_user_permitted.return_value = False

    with patch("app.services.permissions.has_permission", return_value=True), \
         patch("app.services.user_service.get_employee_by_id", return_value=other_user), \
         patch("app.services.permissions.resolve_data_scope_context", return_value=mock_scope_ctx_self):
        res_403 = client.get(f"/api/admin/employees/{other_user_id}")
        assert res_403.status_code == status.HTTP_403_FORBIDDEN
        assert "outside your authorized data scope" in res_403.json()["detail"]

    # 3. 200 OK (Within scope)
    mock_scope_ctx_all = MagicMock()
    mock_scope_ctx_all.is_user_permitted.return_value = True

    with patch("app.services.permissions.has_permission", return_value=True), \
         patch("app.services.user_service.get_employee_by_id", return_value=active_admin_user), \
         patch("app.services.permissions.resolve_data_scope_context", return_value=mock_scope_ctx_all):
        res_200 = client.get(f"/api/admin/employees/{active_admin_user.user_id}")
        assert res_200.status_code == status.HTTP_200_OK
        assert res_200.json()["employee_code"] == "CG0001"

    app.dependency_overrides.clear()


# ==============================================================================
# Employee Update Tests (PATCH /api/admin/employees/{user_id})
# ==============================================================================

def test_update_employee_profile_partial_and_immutability(
    client: TestClient,
    active_admin_user: User,
    mock_db_session: MagicMock,
) -> None:
    """Verify PATCH /api/admin/employees/{id} supports partial updates and rejects company changes."""
    app.dependency_overrides[get_current_active_user] = lambda: active_admin_user
    app.dependency_overrides[get_db] = lambda: mock_db_session

    mock_scope_ctx = MagicMock()
    mock_scope_ctx.is_user_permitted.return_value = True

    # 1. Successful partial update
    updated_user = active_admin_user
    updated_user.first_name = "Alexander"

    with patch("app.services.permissions.has_permission", return_value=True), \
         patch("app.services.user_service.get_employee_by_id", return_value=active_admin_user), \
         patch("app.services.permissions.resolve_data_scope_context", return_value=mock_scope_ctx), \
         patch("app.services.user_service.update_employee", return_value=updated_user):
        res = client.patch(
            f"/api/admin/employees/{active_admin_user.user_id}",
            json={"first_name": "Alexander"},
        )
        assert res.status_code == status.HTTP_200_OK
        assert res.json()["first_name"] == "Alexander"

    # 2. Company modification rejected
    with patch("app.services.permissions.has_permission", return_value=True), \
         patch("app.services.user_service.get_employee_by_id", return_value=active_admin_user), \
         patch("app.services.permissions.resolve_data_scope_context", return_value=mock_scope_ctx), \
         patch("app.services.user_service.update_employee", side_effect=ValueError("Company cannot be modified for an existing employee")):
        res_comp = client.patch(
            f"/api/admin/employees/{active_admin_user.user_id}",
            json={"company_id": str(uuid.uuid4())},
        )
        assert res_comp.status_code == status.HTTP_400_BAD_REQUEST
        assert "Company cannot be modified" in res_comp.json()["detail"]

    # 3. Employee code in body forbidden (422)
    with patch("app.services.permissions.has_permission", return_value=True):
        res_code = client.patch(
            f"/api/admin/employees/{active_admin_user.user_id}",
            json={"employee_code": "CG9999"},
        )
        assert res_code.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    app.dependency_overrides.clear()


# ==============================================================================
# Employee Status Update Tests (PATCH /api/admin/employees/{user_id}/status)
# ==============================================================================

def test_update_employee_status_endpoint(
    client: TestClient,
    active_admin_user: User,
    mock_db_session: MagicMock,
) -> None:
    """Verify PATCH /api/admin/employees/{id}/status updates operational status."""
    app.dependency_overrides[get_current_active_user] = lambda: active_admin_user
    app.dependency_overrides[get_db] = lambda: mock_db_session

    mock_scope_ctx = MagicMock()
    mock_scope_ctx.is_user_permitted.return_value = True

    deactivated_user = active_admin_user
    deactivated_user.account_status = "INACTIVE"

    with patch("app.services.permissions.has_permission", return_value=True), \
         patch("app.services.user_service.get_employee_by_id", return_value=active_admin_user), \
         patch("app.services.permissions.resolve_data_scope_context", return_value=mock_scope_ctx), \
         patch("app.services.user_service.update_employee_status", return_value=deactivated_user):
        res = client.patch(
            f"/api/admin/employees/{active_admin_user.user_id}/status",
            json={"account_status": "INACTIVE"},
        )
        assert res.status_code == status.HTTP_200_OK
        assert res.json()["account_status"] == "INACTIVE"

    # Invalid status rejected by schema (422)
    with patch("app.services.permissions.has_permission", return_value=True):
        res_inv = client.patch(
            f"/api/admin/employees/{active_admin_user.user_id}/status",
            json={"account_status": "BANNED"},
        )
        assert res_inv.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    app.dependency_overrides.clear()


def test_create_employee_cross_company_validation_error_responses(
    client: TestClient,
    active_admin_user: User,
    mock_db_session: MagicMock,
    test_company_id: uuid.UUID,
    test_department_id: uuid.UUID,
    test_designation_id: uuid.UUID,
) -> None:
    """Verify cross-company validation errors return 400 Bad Request."""
    app.dependency_overrides[get_current_active_user] = lambda: active_admin_user
    app.dependency_overrides[get_db] = lambda: mock_db_session

    payload = {
        "company_id": str(test_company_id),
        "department_id": str(test_department_id),
        "designation_id": str(test_designation_id),
        "first_name": "Rohan",
        "last_name": "Verma",
        "official_email": "rohan@gocompliances.in",
        "mobile_number": "+919876543299",
        "date_of_joining": "2026-02-01",
        "employment_type": "FULL_TIME",
        "account_status": "ACTIVE",
    }

    # Department mismatch
    with patch("app.services.permissions.has_permission", return_value=True), \
         patch("app.services.user_service.create_user", side_effect=ValueError("Department does not belong to the selected company")):
        res = client.post("/api/admin/employees", json=payload)
        assert res.status_code == status.HTTP_400_BAD_REQUEST
        assert "Department does not belong" in res.json()["detail"]

    # Inactive designation
    with patch("app.services.permissions.has_permission", return_value=True), \
         patch("app.services.user_service.create_user", side_effect=ValueError("Designation is inactive")):
        res = client.post("/api/admin/employees", json=payload)
        assert res.status_code == status.HTTP_400_BAD_REQUEST
        assert "Designation is inactive" in res.json()["detail"]

    app.dependency_overrides.clear()


def test_update_employee_circular_hierarchy_rejected(
    client: TestClient,
    active_admin_user: User,
    mock_db_session: MagicMock,
) -> None:
    """Verify circular reporting hierarchy on update returns 400 Bad Request."""
    app.dependency_overrides[get_current_active_user] = lambda: active_admin_user
    app.dependency_overrides[get_db] = lambda: mock_db_session

    mock_scope_ctx = MagicMock()
    mock_scope_ctx.is_user_permitted.return_value = True

    subordinate_id = uuid.uuid4()

    with patch("app.services.permissions.has_permission", return_value=True), \
         patch("app.services.user_service.get_employee_by_id", return_value=active_admin_user), \
         patch("app.services.permissions.resolve_data_scope_context", return_value=mock_scope_ctx), \
         patch(
             "app.services.user_service.update_employee",
             side_effect=ValueError("Circular reporting hierarchy detected: the selected manager reports to this employee"),
         ):
        res = client.patch(
            f"/api/admin/employees/{active_admin_user.user_id}",
            json={"manager_user_id": str(subordinate_id)},
        )
        assert res.status_code == status.HTTP_400_BAD_REQUEST
        assert "Circular reporting hierarchy detected" in res.json()["detail"]

    app.dependency_overrides.clear()


def test_update_employee_duplicate_email_409(
    client: TestClient,
    active_admin_user: User,
    mock_db_session: MagicMock,
) -> None:
    """Verify updating to an existing official email raises 409 Conflict."""
    app.dependency_overrides[get_current_active_user] = lambda: active_admin_user
    app.dependency_overrides[get_db] = lambda: mock_db_session

    mock_scope_ctx = MagicMock()
    mock_scope_ctx.is_user_permitted.return_value = True

    with patch("app.services.permissions.has_permission", return_value=True), \
         patch("app.services.user_service.get_employee_by_id", return_value=active_admin_user), \
         patch("app.services.permissions.resolve_data_scope_context", return_value=mock_scope_ctx), \
         patch(
             "app.services.user_service.update_employee",
             side_effect=ValueError("Official email 'other@gocompliances.in' is already registered"),
         ):
        res = client.patch(
            f"/api/admin/employees/{active_admin_user.user_id}",
            json={"official_email": "other@gocompliances.in"},
        )
        assert res.status_code == status.HTTP_409_CONFLICT
        assert "already registered" in res.json()["detail"]

    app.dependency_overrides.clear()


# ==============================================================================
# Security & Absence of Delete Route
# ==============================================================================

def test_no_hard_delete_route(client: TestClient, active_admin_user: User) -> None:
    """Verify DELETE /api/admin/employees/{id} does not exist (405 Method Not Allowed)."""
    app.dependency_overrides[get_current_active_user] = lambda: active_admin_user

    response = client.delete(f"/api/admin/employees/{uuid.uuid4()}")
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    app.dependency_overrides.clear()
