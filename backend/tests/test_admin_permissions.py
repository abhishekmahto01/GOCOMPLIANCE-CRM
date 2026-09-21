"""Unit and integration tests for Admin Permission Management, Catalog, Scoping, and Audit."""
import uuid
from datetime import date, datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.api.deps import get_current_active_user, get_db, require_fully_activated_user
from app.main import app
from app.models.company import Company
from app.models.department import Department
from app.models.designation import Designation
from app.models.module import Module
from app.models.permission_audit import PermissionAuditLog
from app.models.user import User
from app.models.user_module_permission import UserModulePermission
from app.schemas.permission import (
    AccessibleModuleRead,
    CatalogModuleItem,
    CatalogPageItem,
    PageActionPermission,
    PermissionCatalogResponse,
    UserPermissionsSaveRequest,
    UserSettingsUpdate,
)
from app.services import permissions
from app.services.permissions import (
    PAGE_CATALOG_CONFIG,
    copy_user_permissions,
    get_permission_catalog,
    get_user_effective_permissions_bundle,
    get_user_permissions_bundle,
    has_permission,
    has_permission_slug,
    save_user_permissions_bundle,
)


@pytest.fixture
def client() -> TestClient:
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def mock_db() -> MagicMock:
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
def admin_user(test_company_id: uuid.UUID, test_department_id: uuid.UUID, test_designation_id: uuid.UUID) -> User:
    return User(
        user_id=uuid.uuid4(),
        employee_code="GC0001",
        company_id=test_company_id,
        department_id=test_department_id,
        designation_id=test_designation_id,
        first_name="Super",
        last_name="Admin",
        official_email="admin@gocompliances.in",
        mobile_number="+919876543210",
        date_of_joining=date(2026, 1, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        must_change_password=False,
    )


@pytest.fixture
def standard_employee(test_company_id: uuid.UUID, test_department_id: uuid.UUID, test_designation_id: uuid.UUID) -> User:
    return User(
        user_id=uuid.uuid4(),
        employee_code="GC0002",
        company_id=test_company_id,
        department_id=test_department_id,
        designation_id=test_designation_id,
        first_name="Aadarsh",
        last_name="Kumar",
        official_email="aadarsh@gocompliances.in",
        mobile_number="+919876543211",
        date_of_joining=date(2026, 1, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        must_change_password=False,
    )


# ==============================================================================
# Catalog Tests
# ==============================================================================

def test_permission_catalog_structure(mock_db: MagicMock) -> None:
    """Verify catalog generates Sales (6 pages) and Operations (8 pages) with exact actions."""
    catalog = get_permission_catalog(mock_db)
    assert len(catalog.modules) == 2

    sales_mod = next(m for m in catalog.modules if m.module_code == "SALES")
    op_mod = next(m for m in catalog.modules if m.module_code == "OPERATIONS")

    assert len(sales_mod.pages) == 6
    assert len(op_mod.pages) == 8

    # Sales pages check
    sales_pages_dict = {p.page_code: p for p in sales_mod.pages}
    assert "SALES_DASHBOARD" in sales_pages_dict
    assert sales_pages_dict["SALES_DASHBOARD"].supported_actions == ["read", "export"]
    assert sales_pages_dict["SALES_DASHBOARD"].action_slugs["read"] == "sales.dashboard.read"
    assert sales_pages_dict["SALES_DASHBOARD"].action_slugs["export"] == "sales.dashboard.export"

    assert "SALES_CONFIRMED_ORDER" in sales_pages_dict
    assert sales_pages_dict["SALES_CONFIRMED_ORDER"].supported_actions == ["read", "write", "update"]

    assert "SALES_ALL_ORDERS" in sales_pages_dict
    assert sales_pages_dict["SALES_ALL_ORDERS"].supported_actions == ["read", "update", "delete", "export"]

    assert "SALES_CLIENT_MASTER" in sales_pages_dict
    assert sales_pages_dict["SALES_CLIENT_MASTER"].supported_actions == ["read", "write", "update", "delete"]

    # Operation pages check
    op_pages_dict = {p.page_code: p for p in op_mod.pages}
    assert "OPERATION_DASHBOARD" in op_pages_dict
    assert op_pages_dict["OPERATION_DASHBOARD"].supported_actions == ["read", "export"]

    assert "OPERATION_UNASSIGNED_ORDERS" in op_pages_dict
    assert op_pages_dict["OPERATION_UNASSIGNED_ORDERS"].supported_actions == ["read", "assign"]

    assert "OPERATION_TASK_ASSIGNMENT" in op_pages_dict
    assert op_pages_dict["OPERATION_TASK_ASSIGNMENT"].supported_actions == ["read", "assign", "reassign"]

    assert "OPERATION_ALL_TASKS" in op_pages_dict
    assert op_pages_dict["OPERATION_ALL_TASKS"].supported_actions == ["read", "update", "assign", "reassign"]


def test_permission_catalog_endpoint(
    client: TestClient,
    mock_db: MagicMock,
    admin_user: User,
) -> None:
    """Verify GET /api/admin/permission-catalog endpoint returns 200 for admin."""
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_active_user] = lambda: admin_user
    app.dependency_overrides[require_fully_activated_user] = lambda: admin_user

    with patch("app.services.permissions.has_permission", return_value=True):
        resp = client.get("/api/admin/permission-catalog")
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert "modules" in data
        assert len(data["modules"]) == 2

    app.dependency_overrides.clear()


def test_permission_catalog_unauthorized(
    client: TestClient,
    mock_db: MagicMock,
    standard_employee: User,
) -> None:
    """Verify unauthorized users receive 403 when requesting catalog."""
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_active_user] = lambda: standard_employee
    app.dependency_overrides[require_fully_activated_user] = lambda: standard_employee

    with patch("app.services.permissions.has_permission", return_value=False):
        resp = client.get("/api/admin/permission-catalog")
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    app.dependency_overrides.clear()


# ==============================================================================
# Save and Load Permissions Tests
# ==============================================================================

def test_get_user_permissions_bundle(
    mock_db: MagicMock,
    standard_employee: User,
) -> None:
    """Verify get_user_permissions_bundle loads user details and page permissions."""
    mock_db.get.side_effect = lambda model, pk: {
        (User, standard_employee.user_id): standard_employee,
        (Company, standard_employee.company_id): Company(company_id=standard_employee.company_id, company_name="GoCompliances Org", company_code="GC", employee_code_prefix="GC", status="ACTIVE"),
        (Department, standard_employee.department_id): Department(department_id=standard_employee.department_id, company_id=standard_employee.company_id, department_name="Admin", department_code="ADM", status="ACTIVE"),
        (Designation, standard_employee.designation_id): Designation(designation_id=standard_employee.designation_id, company_id=standard_employee.company_id, designation_name="Exec", designation_code="EXE", level_rank=1, status="ACTIVE"),
    }.get((model, pk))

    mock_db.execute.return_value.all.return_value = []

    bundle = get_user_permissions_bundle(mock_db, standard_employee.user_id)
    assert bundle.employee_code == standard_employee.employee_code
    assert bundle.first_name == "Aadarsh"
    assert len(bundle.permissions) == 14  # 6 Sales + 8 Operation


def test_save_user_permissions_bundle(
    mock_db: MagicMock,
    admin_user: User,
    standard_employee: User,
) -> None:
    """Verify save_user_permissions_bundle saves permissions, user settings, and creates audit log."""
    mock_db.get.side_effect = lambda model, pk: {
        (User, standard_employee.user_id): standard_employee,
        (Company, standard_employee.company_id): Company(company_id=standard_employee.company_id, company_name="GoCompliances Org", company_code="GC", employee_code_prefix="GC", status="ACTIVE"),
        (Department, standard_employee.department_id): Department(department_id=standard_employee.department_id, company_id=standard_employee.company_id, department_name="Admin", department_code="ADM", status="ACTIVE"),
        (Designation, standard_employee.designation_id): Designation(designation_id=standard_employee.designation_id, company_id=standard_employee.company_id, designation_name="Exec", designation_code="EXE", level_rank=1, status="ACTIVE"),
    }.get((model, pk))

    # Mock modules in database
    sales_mod = Module(module_id=uuid.uuid4(), module_code="SALES", module_name="Sales", status="ACTIVE")
    sales_dash_mod = Module(module_id=uuid.uuid4(), module_code="SALES_DASHBOARD", module_name="Sales Dashboard", status="ACTIVE")
    mock_db.execute.return_value.scalars.return_value.all.return_value = [sales_mod, sales_dash_mod]
    mock_db.execute.return_value.all.return_value = []

    save_payload = UserPermissionsSaveRequest(
        permissions=[
            PageActionPermission(
                page_code="SALES_DASHBOARD",
                can_view=True,
                can_export=True,
                data_scope="SELF",
            ),
        ],
        user_settings=UserSettingsUpdate(
            is_hod=True,
            is_reporting_manager=True,
            primary_location="Mumbai",
        ),
    )

    with patch("app.services.permissions.grant_or_update_permission") as mock_grant:
        bundle = save_user_permissions_bundle(
            session=mock_db,
            actor_user=admin_user,
            target_user_id=standard_employee.user_id,
            payload=save_payload,
            ip_address="127.0.0.1",
            user_agent="TestAgent",
        )

        assert mock_grant.called
        assert standard_employee.is_hod is True
        assert standard_employee.is_reporting_manager is True
        assert standard_employee.primary_location == "Mumbai"
        assert mock_db.commit.called


def test_save_unsupported_action_rejected(
    mock_db: MagicMock,
    admin_user: User,
    standard_employee: User,
) -> None:
    """Verify that attempting to assign unsupported actions raises a ValueError."""
    mock_db.get.side_effect = lambda model, pk: {
        (User, standard_employee.user_id): standard_employee,
        (Company, standard_employee.company_id): Company(company_id=standard_employee.company_id, company_name="GoCompliances Org", company_code="GC", employee_code_prefix="GC", status="ACTIVE"),
        (Department, standard_employee.department_id): Department(department_id=standard_employee.department_id, company_id=standard_employee.company_id, department_name="Admin", department_code="ADM", status="ACTIVE"),
        (Designation, standard_employee.designation_id): Designation(designation_id=standard_employee.designation_id, company_id=standard_employee.company_id, designation_name="Exec", designation_code="EXE", level_rank=1, status="ACTIVE"),
    }.get((model, pk))

    mock_db.execute.return_value.all.return_value = []

    # SALES_DASHBOARD only supports read and export, NOT delete
    save_payload = UserPermissionsSaveRequest(
        permissions=[
            PageActionPermission(
                page_code="SALES_DASHBOARD",
                can_view=True,
                can_delete=True,
            ),
        ],
    )

    with pytest.raises(ValueError) as exc:
        save_user_permissions_bundle(
            session=mock_db,
            actor_user=admin_user,
            target_user_id=standard_employee.user_id,
            payload=save_payload,
        )
    assert "not supported for page 'SALES_DASHBOARD'" in str(exc.value)


def test_copy_user_permissions_service(
    mock_db: MagicMock,
    admin_user: User,
    standard_employee: User,
) -> None:
    """Verify copy_user_permissions duplicates permissions from source to target and writes audit log."""
    target_user = User(
        user_id=uuid.uuid4(),
        employee_code="GC0003",
        company_id=standard_employee.company_id,
        department_id=standard_employee.department_id,
        designation_id=standard_employee.designation_id,
        first_name="Priya",
        last_name="Sharma",
        official_email="priya@gocompliances.in",
        mobile_number="+919876543212",
        date_of_joining=date(2026, 1, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
    )

    mock_db.get.side_effect = lambda model, pk: {
        (User, standard_employee.user_id): standard_employee,
        (User, target_user.user_id): target_user,
        (Company, standard_employee.company_id): Company(company_id=standard_employee.company_id, company_name="GoCompliances Org", company_code="GC", employee_code_prefix="GC", status="ACTIVE"),
        (Department, standard_employee.department_id): Department(department_id=standard_employee.department_id, company_id=standard_employee.company_id, department_name="Admin", department_code="ADM", status="ACTIVE"),
        (Designation, standard_employee.designation_id): Designation(designation_id=standard_employee.designation_id, company_id=standard_employee.company_id, designation_name="Exec", designation_code="EXE", level_rank=1, status="ACTIVE"),
    }.get((model, pk))

    mock_db.execute.return_value.all.return_value = []
    mock_db.execute.return_value.scalars.return_value.all.return_value = []

    with patch("app.services.permissions.save_user_permissions_bundle") as mock_save:
        res = copy_user_permissions(
            session=mock_db,
            actor_user=admin_user,
            source_user_id=standard_employee.user_id,
            target_user_id=target_user.user_id,
            ip_address="127.0.0.1",
            user_agent="TestAgent",
        )
        assert mock_save.called
        assert res.source_user_id == standard_employee.user_id
        assert res.target_user_id == target_user.user_id
        assert mock_db.commit.called


def test_effective_permissions_bundle_and_slugs(
    mock_db: MagicMock,
    standard_employee: User,
) -> None:
    """Verify get_user_effective_permissions_bundle maps permission flags to exact slug strings."""
    mock_db.get.return_value = standard_employee

    # Mock accessible modules
    accessible_page = AccessibleModuleRead(
        module_id=uuid.uuid4(),
        module_code="SALES_DASHBOARD",
        module_name="Sales Dashboard",
        route="/sales/dashboard",
        display_order=10,
        is_navigation=True,
        can_view=True,
        can_create=False,
        can_edit=False,
        can_delete=False,
        can_approve=False,
        can_assign=False,
        can_reassign=False,
        can_export=True,
        data_scope="SELF",
    )

    with patch("app.services.permissions.get_accessible_modules", return_value=[accessible_page]):
        effective = get_user_effective_permissions_bundle(mock_db, standard_employee.user_id)
        assert effective.permissions["sales.dashboard.read"] is True
        assert effective.permissions["sales.dashboard.export"] is True
        assert effective.permissions["sales.all_orders.delete"] is False


def test_api_routes_integration(
    client: TestClient,
    mock_db: MagicMock,
    admin_user: User,
    standard_employee: User,
) -> None:
    """Verify GET, PUT, POST endpoints on /api/admin/users/{id}/permissions."""
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_active_user] = lambda: admin_user
    app.dependency_overrides[require_fully_activated_user] = lambda: admin_user

    mock_db.get.return_value = standard_employee

    scope_mock = MagicMock()
    scope_mock.is_user_permitted.return_value = True

    with patch("app.services.permissions.has_permission", return_value=True), \
         patch("app.services.permissions.resolve_data_scope_context", return_value=scope_mock):

        # 1. GET user permissions
        with patch("app.services.permissions.get_user_permissions_bundle") as mock_get:
            mock_get.return_value = permissions.UserPermissionsDetailResponse(
                user_id=standard_employee.user_id,
                employee_code="GC0002",
                first_name="Aadarsh",
                last_name="Kumar",
                official_email="aadarsh@test.com",
                company_id=standard_employee.company_id,
                department_id=standard_employee.department_id,
                designation_id=standard_employee.designation_id,
                is_active=True,
                is_hod=False,
                is_reporting_manager=False,
                manager_user_id=None,
                manager_name=None,
                primary_location=None,
                permissions=[],
            )
            resp = client.get(f"/api/admin/users/{standard_employee.user_id}/permissions")
            assert resp.status_code == status.HTTP_200_OK

        # 2. PUT user permissions
        with patch("app.services.permissions.save_user_permissions_bundle") as mock_save:
            mock_save.return_value = permissions.UserPermissionsDetailResponse(
                user_id=standard_employee.user_id,
                employee_code="GC0002",
                first_name="Aadarsh",
                last_name="Kumar",
                official_email="aadarsh@test.com",
                company_id=standard_employee.company_id,
                department_id=standard_employee.department_id,
                designation_id=standard_employee.designation_id,
                is_active=True,
                is_hod=True,
                is_reporting_manager=False,
                manager_user_id=None,
                manager_name=None,
                primary_location="Delhi",
                permissions=[],
            )
            resp = client.put(
                f"/api/admin/users/{standard_employee.user_id}/permissions",
                json={"permissions": [], "user_settings": {"is_hod": True, "primary_location": "Delhi"}},
            )
            assert resp.status_code == status.HTTP_200_OK

        # 3. POST copy permissions
        with patch("app.services.permissions.copy_user_permissions") as mock_copy:
            source_id = uuid.uuid4()
            mock_copy.return_value = permissions.CopyPermissionsResponse(
                message="Copied successfully",
                copied_count=14,
                source_user_id=source_id,
                target_user_id=standard_employee.user_id,
            )
            resp = client.post(
                f"/api/admin/users/{standard_employee.user_id}/permissions/copy",
                json={"source_user_id": str(source_id)},
            )
            assert resp.status_code == status.HTTP_200_OK

    app.dependency_overrides.clear()
