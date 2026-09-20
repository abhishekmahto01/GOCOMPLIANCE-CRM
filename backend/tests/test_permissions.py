"""Unit and integration tests for User Module Permissions."""
import ast
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy import CheckConstraint, ForeignKeyConstraint, PrimaryKeyConstraint, UniqueConstraint, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.api.deps import require_module_permission
from app.database.base import Base
from app.models.company import Company
from app.models.department import Department
from app.models.designation import Designation
from app.models.module import Module
from app.models.user import User
from app.models.user_module_permission import UserModulePermission
from app.schemas.permission import (
    AccessibleModuleRead,
    UserModulePermissionBase,
    UserModulePermissionCreate,
    UserModulePermissionRead,
    UserModulePermissionUpdate,
)
from app.services.permissions import (
    GrantorEscalationError,
    PermissionDeniedError,
    deactivate_permission,
    get_accessible_modules,
    get_effective_scope,
    get_user_module_permission,
    grant_or_update_permission,
    has_permission,
    is_permission_active_and_valid,
    require_permission,
)

# ==============================================================================
# Model Tests
# ==============================================================================

def test_user_module_permission_model_table_name_and_metadata() -> None:
    """Verify table name and metadata registration for user_module_permission."""
    assert UserModulePermission.__tablename__ == "user_module_permission"
    assert "user_module_permission" in Base.metadata.tables


def test_user_module_permission_model_columns() -> None:
    """Verify column definitions, types, nullability, defaults and comments."""
    table = UserModulePermission.__table__
    columns = table.c

    expected_cols = {
        "permission_id",
        "user_id",
        "module_id",
        "can_view",
        "can_create",
        "can_edit",
        "can_delete",
        "can_approve",
        "data_scope",
        "status",
        "granted_by_user_id",
        "granted_at",
        "expires_at",
        "updated_at",
    }
    assert set(columns.keys()) == expected_cols

    # Primary key
    assert columns["permission_id"].primary_key is True

    # Foreign keys
    assert columns["user_id"].nullable is False
    assert columns["module_id"].nullable is False
    assert columns["granted_by_user_id"].nullable is True

    # Boolean flags defaults
    assert columns["can_view"].nullable is False
    assert columns["can_create"].nullable is False
    assert columns["can_edit"].nullable is False
    assert columns["can_delete"].nullable is False
    assert columns["can_approve"].nullable is False

    # Scope and status defaults
    assert columns["data_scope"].nullable is False
    assert columns["status"].nullable is False

    # Timestamps
    assert columns["granted_at"].nullable is False
    assert columns["expires_at"].nullable is True
    assert columns["updated_at"].nullable is False


def test_user_module_permission_model_constraints_and_foreign_keys() -> None:
    """Verify foreign keys, delete rules, check constraints and unique constraint."""
    table = UserModulePermission.__table__

    # Foreign Keys
    fks = list(table.foreign_keys)
    fk_dict = {fk.parent.name: fk for fk in fks}

    assert fk_dict["user_id"].target_fullname == "user_master.user_id"
    assert fk_dict["user_id"].ondelete == "CASCADE"

    assert fk_dict["module_id"].target_fullname == "module_master.module_id"
    assert fk_dict["module_id"].ondelete == "RESTRICT"

    assert fk_dict["granted_by_user_id"].target_fullname == "user_master.user_id"
    assert fk_dict["granted_by_user_id"].ondelete == "SET NULL"

    # Unique constraint (user_id, module_id)
    unique_constraints = [c for c in table.constraints if isinstance(c, UniqueConstraint)]
    user_mod_uq = next(
        (c for c in unique_constraints if set(col.name for col in c.columns) == {"user_id", "module_id"}),
        None,
    )
    assert user_mod_uq is not None
    assert user_mod_uq.name == "uq_user_module_permission_user_module"

    # Check constraints
    check_constraints = {c.name: str(c.sqltext) for c in table.constraints if isinstance(c, CheckConstraint)}
    assert "chk_permission_data_scope_valid" in check_constraints
    assert "chk_permission_status_valid" in check_constraints
    assert "chk_permission_action_requires_view" in check_constraints
    assert "chk_permission_expires_after_granted" in check_constraints


def test_user_module_permission_orm_relationships() -> None:
    """Verify ORM relationships between User, Module, and UserModulePermission."""
    from sqlalchemy.orm import class_mapper

    user_mapper = class_mapper(User)
    module_mapper = class_mapper(Module)
    perm_mapper = class_mapper(UserModulePermission)

    # User relationships
    assert "module_permissions" in user_mapper.relationships
    assert user_mapper.relationships["module_permissions"].back_populates == "user"

    assert "permissions_granted" in user_mapper.relationships
    assert user_mapper.relationships["permissions_granted"].back_populates == "granted_by"

    # Module relationships
    assert "user_permissions" in module_mapper.relationships
    assert module_mapper.relationships["user_permissions"].back_populates == "module"

    # UserModulePermission relationships
    assert "user" in perm_mapper.relationships
    assert perm_mapper.relationships["user"].back_populates == "module_permissions"

    assert "module" in perm_mapper.relationships
    assert perm_mapper.relationships["module"].back_populates == "user_permissions"

    assert "granted_by" in perm_mapper.relationships
    assert perm_mapper.relationships["granted_by"].back_populates == "permissions_granted"


# ==============================================================================
# Schema Tests
# ==============================================================================

def test_permission_schema_valid_defaults() -> None:
    """Verify default values and valid instantiation of UserModulePermissionBase."""
    perm = UserModulePermissionBase()
    assert perm.can_view is False
    assert perm.can_create is False
    assert perm.can_edit is False
    assert perm.can_delete is False
    assert perm.can_approve is False
    assert perm.data_scope == "SELF"
    assert perm.status == "ACTIVE"
    assert perm.expires_at is None


def test_permission_schema_invalid_scope_and_status() -> None:
    """Verify validation errors for invalid data scopes and statuses."""
    with pytest.raises(ValidationError) as exc_info:
        UserModulePermissionBase(data_scope="INVALID_SCOPE")
    assert "Invalid data scope" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        UserModulePermissionBase(status="UNKNOWN")
    assert "Invalid status" in str(exc_info.value)


def test_permission_schema_action_flags_require_view() -> None:
    """Verify that enabling any action flag without can_view=True raises a ValidationError."""
    # create without view
    with pytest.raises(ValidationError) as exc:
        UserModulePermissionBase(can_view=False, can_create=True)
    assert "can_view must be true" in str(exc.value)

    # edit without view
    with pytest.raises(ValidationError) as exc:
        UserModulePermissionBase(can_view=False, can_edit=True)
    assert "can_view must be true" in str(exc.value)

    # delete without view
    with pytest.raises(ValidationError) as exc:
        UserModulePermissionBase(can_view=False, can_delete=True)
    assert "can_view must be true" in str(exc.value)

    # approve without view
    with pytest.raises(ValidationError) as exc:
        UserModulePermissionBase(can_view=False, can_approve=True)
    assert "can_view must be true" in str(exc.value)

    # all valid with can_view=True
    valid = UserModulePermissionBase(
        can_view=True,
        can_create=True,
        can_edit=True,
        can_delete=True,
        can_approve=True,
    )
    assert valid.can_view is True
    assert valid.can_delete is True


def test_permission_create_schema_past_expiry_rejected() -> None:
    """Verify that a past expiration date is rejected in create schema."""
    past_time = datetime.now(timezone.utc) - timedelta(hours=1)
    with pytest.raises(ValidationError) as exc:
        UserModulePermissionCreate(
            user_id=uuid.uuid4(),
            module_id=uuid.uuid4(),
            can_view=True,
            expires_at=past_time,
        )
    assert "expires_at must be in the future" in str(exc.value)


def test_permission_update_schema_validation() -> None:
    """Verify partial updates and consistency checks in UserModulePermissionUpdate."""
    update_data = UserModulePermissionUpdate(can_view=True, can_edit=True, data_scope="TEAM")
    assert update_data.can_view is True
    assert update_data.can_edit is True
    assert update_data.data_scope == "TEAM"
    assert update_data.can_delete is None

    # Setting can_view=False while setting an action flag to True
    with pytest.raises(ValidationError) as exc:
        UserModulePermissionUpdate(can_view=False, can_create=True)
    assert "can_view cannot be false when other action flags are set to true" in str(exc.value)


# ==============================================================================
# Service Tests
# ==============================================================================

def test_has_permission_default_deny() -> None:
    """Verify default deny when user has no permission rows."""
    mock_session = MagicMock(spec=Session)
    mock_user = MagicMock(spec=User)
    mock_user.account_status = "ACTIVE"
    mock_user.user_id = uuid.uuid4()

    # Module exists and active
    mock_module = MagicMock(spec=Module)
    mock_module.status = "ACTIVE"
    mock_module.module_id = uuid.uuid4()

    # Module query returns active module, permission query returns None
    mock_session.execute.return_value.scalar_one_or_none.side_effect = [
        mock_module, None,
        mock_module, None,
    ]

    assert has_permission(mock_session, mock_user, "SALES", "view") is False
    assert has_permission(mock_session, mock_user, "SALES", "create") is False


def test_has_permission_inactive_user_or_module_denied() -> None:
    """Verify permission is denied if user or module is not ACTIVE."""
    mock_session = MagicMock(spec=Session)

    # Inactive user
    mock_user_inactive = MagicMock(spec=User)
    mock_user_inactive.account_status = "INACTIVE"
    assert has_permission(mock_session, mock_user_inactive, "SALES", "view") is False

    # Suspended user
    mock_user_suspended = MagicMock(spec=User)
    mock_user_suspended.account_status = "SUSPENDED"
    assert has_permission(mock_session, mock_user_suspended, "SALES", "view") is False

    # Inactive module
    mock_user_active = MagicMock(spec=User)
    mock_user_active.account_status = "ACTIVE"
    mock_module_inactive = MagicMock(spec=Module)
    mock_module_inactive.status = "INACTIVE"
    mock_session.execute.return_value.scalar_one_or_none.return_value = mock_module_inactive

    assert has_permission(mock_session, mock_user_active, "SALES", "view") is False


def test_has_permission_expired_permission_denied() -> None:
    """Verify permission is denied if expires_at is in the past."""
    mock_session = MagicMock(spec=Session)
    mock_user = MagicMock(spec=User)
    mock_user.account_status = "ACTIVE"
    mock_user.user_id = uuid.uuid4()

    mock_module = MagicMock(spec=Module)
    mock_module.status = "ACTIVE"
    mock_module.module_id = uuid.uuid4()

    past_expiry = datetime.now(timezone.utc) - timedelta(minutes=5)
    mock_perm = MagicMock(spec=UserModulePermission)
    mock_perm.status = "ACTIVE"
    mock_perm.can_view = True
    mock_perm.expires_at = past_expiry

    mock_session.execute.return_value.scalar_one_or_none.side_effect = [mock_module, mock_perm]

    assert has_permission(mock_session, mock_user, "SALES", "view") is False


def test_has_permission_each_action_independent() -> None:
    """Verify that view, create, edit, delete, and approve are checked independently."""
    mock_session = MagicMock(spec=Session)
    mock_user = MagicMock(spec=User)
    mock_user.account_status = "ACTIVE"
    mock_user.user_id = uuid.uuid4()

    mock_module = MagicMock(spec=Module)
    mock_module.status = "ACTIVE"
    mock_module.module_id = uuid.uuid4()

    # User has view and edit, but not create, delete or approve
    mock_perm = MagicMock(spec=UserModulePermission)
    mock_perm.status = "ACTIVE"
    mock_perm.can_view = True
    mock_perm.can_create = False
    mock_perm.can_edit = True
    mock_perm.can_delete = False
    mock_perm.can_approve = False
    mock_perm.expires_at = None

    mock_session.execute.return_value.scalar_one_or_none.side_effect = [
        mock_module, mock_perm,
        mock_module, mock_perm,
        mock_module, mock_perm,
        mock_module, mock_perm,
        mock_module, mock_perm,
    ]

    assert has_permission(mock_session, mock_user, "SALES", "view") is True
    assert has_permission(mock_session, mock_user, "SALES", "create") is False
    assert has_permission(mock_session, mock_user, "SALES", "edit") is True
    assert has_permission(mock_session, mock_user, "SALES", "delete") is False
    assert has_permission(mock_session, mock_user, "SALES", "approve") is False


def test_grant_or_update_permission_grantor_escalation_rejected() -> None:
    """Verify that a grantor cannot grant permissions they do not possess."""
    mock_session = MagicMock(spec=Session)

    target_user_id = uuid.uuid4()
    grantor_user_id = uuid.uuid4()
    module_id = uuid.uuid4()

    target_user = MagicMock(spec=User, user_id=target_user_id, account_status="ACTIVE", employee_code="CG0002")
    grantor_user = MagicMock(spec=User, user_id=grantor_user_id, account_status="ACTIVE", employee_code="CG0001")
    target_module = MagicMock(spec=Module, module_id=module_id, module_code="SALES", status="ACTIVE")

    # Grantor has view=True, create=False, scope=SELF
    grantor_perm = MagicMock(
        spec=UserModulePermission,
        user_id=grantor_user_id,
        module_id=module_id,
        status="ACTIVE",
        can_view=True,
        can_create=False,
        can_edit=False,
        can_delete=False,
        can_approve=False,
        data_scope="SELF",
        expires_at=None,
    )

    mock_session.get.side_effect = lambda model, pk: {
        (User, target_user_id): target_user,
        (Module, module_id): target_module,
        (User, grantor_user_id): grantor_user,
    }.get((model, pk))

    mock_session.execute.return_value.scalar_one_or_none.return_value = grantor_perm

    # 1. Grantor tries to grant create (which they don't have)
    with pytest.raises(GrantorEscalationError) as exc:
        grant_or_update_permission(
            session=mock_session,
            user_id=target_user_id,
            module_id=module_id,
            can_view=True,
            can_create=True,
            granted_by_user_id=grantor_user_id,
        )
    assert "Grantor cannot grant 'create' action" in str(exc.value)

    # 2. Grantor tries to grant broader scope (ALL when grantor only has SELF)
    with pytest.raises(GrantorEscalationError) as exc:
        grant_or_update_permission(
            session=mock_session,
            user_id=target_user_id,
            module_id=module_id,
            can_view=True,
            can_create=False,
            data_scope="ALL",
            granted_by_user_id=grantor_user_id,
        )
    assert "cannot grant broader scope" in str(exc.value)

    # 3. Grantor tries to grant to themselves
    with pytest.raises(GrantorEscalationError) as exc:
        grant_or_update_permission(
            session=mock_session,
            user_id=grantor_user_id,
            module_id=module_id,
            can_view=True,
            granted_by_user_id=grantor_user_id,
        )
    assert "cannot grant or modify permissions for themselves" in str(exc.value)


def test_get_accessible_modules_parent_navigation_behavior() -> None:
    """Verify that accessible child modules include parent modules for navigation tree without granting child actions."""
    mock_session = MagicMock(spec=Session)
    user_id = uuid.uuid4()
    parent_id = uuid.uuid4()
    child_id = uuid.uuid4()
    unrelated_id = uuid.uuid4()

    mock_user = MagicMock(spec=User, user_id=user_id, account_status="ACTIVE")
    mock_session.get.return_value = mock_user

    admin_module = MagicMock(
        spec=Module,
        module_id=parent_id,
        module_code="ADMIN",
        module_name="Administration",
        parent_module_id=None,
        route=None,
        display_order=1,
        is_navigation=True,
        status="ACTIVE",
    )
    companies_module = MagicMock(
        spec=Module,
        module_id=child_id,
        module_code="ADMIN_COMPANIES",
        module_name="Companies",
        parent_module_id=parent_id,
        route="/admin/companies",
        display_order=2,
        is_navigation=True,
        status="ACTIVE",
    )
    sales_module = MagicMock(
        spec=Module,
        module_id=unrelated_id,
        module_code="SALES",
        module_name="Sales",
        parent_module_id=None,
        route="/sales",
        display_order=10,
        is_navigation=True,
        status="ACTIVE",
    )

    # User has explicit permission ONLY on ADMIN_COMPANIES
    comp_perm = MagicMock(
        spec=UserModulePermission,
        user_id=user_id,
        module_id=child_id,
        status="ACTIVE",
        can_view=True,
        can_create=True,
        can_edit=False,
        can_delete=False,
        can_approve=False,
        data_scope="COMPANY",
        expires_at=None,
    )

    mock_session.execute.return_value.scalars.return_value.all.side_effect = [
        [admin_module, companies_module, sales_module],  # all modules
        [comp_perm],  # user permissions
    ]

    accessible = get_accessible_modules(mock_session, user_id)
    accessible_codes = {m.module_code for m in accessible}

    # Both child and parent navigation container must be returned
    assert "ADMIN_COMPANIES" in accessible_codes
    assert "ADMIN" in accessible_codes
    assert "SALES" not in accessible_codes

    # Verify parent has navigation view only (no create/edit/delete/approve)
    admin_item = next(m for m in accessible if m.module_code == "ADMIN")
    assert admin_item.can_view is True
    assert admin_item.can_create is False
    assert admin_item.can_delete is False

    # Verify child has granted create permission
    comp_item = next(m for m in accessible if m.module_code == "ADMIN_COMPANIES")
    assert comp_item.can_view is True
    assert comp_item.can_create is True
    assert comp_item.data_scope == "COMPANY"


# ==============================================================================
# FastAPI Authorization Dependency Tests
# ==============================================================================

def test_require_module_permission_dependency() -> None:
    """Verify require_module_permission dependency enforces 401 unauth, 403 denied, and 200 allowed."""
    from app.api.deps import get_current_active_user, get_db

    app = FastAPI()

    test_user_id = uuid.uuid4()
    mock_active_user = MagicMock(
        spec=User,
        user_id=test_user_id,
        account_status="ACTIVE",
        employee_code="CG0001",
        must_change_password=False,
    )
    mock_session = MagicMock(spec=Session)

    @app.get(
        "/test-permission",
        dependencies=[Depends(require_module_permission("ADMIN_EMPLOYEES", "create"))],
    )
    def protected_endpoint():
        return {"message": "success"}

    client = TestClient(app, raise_server_exceptions=False)

    # 1. Unauthenticated (no token, no override) -> 401 Unauthorized
    response_unauth = client.get("/test-permission")
    assert response_unauth.status_code == status.HTTP_401_UNAUTHORIZED

    # 2. Authenticated but lacks permission -> 403 Forbidden
    app.dependency_overrides[get_current_active_user] = lambda: mock_active_user
    app.dependency_overrides[get_db] = lambda: mock_session

    with patch("app.services.permissions.has_permission", return_value=False):
        response_forbidden = client.get("/test-permission")
        assert response_forbidden.status_code == status.HTTP_403_FORBIDDEN
        assert "Access denied for module 'ADMIN_EMPLOYEES'" in response_forbidden.json()["detail"]

    # 3. Authenticated and possesses permission -> 200 OK
    mock_perm = MagicMock(spec=UserModulePermission, user_id=test_user_id, can_view=True, can_create=True)
    with patch("app.services.permissions.has_permission", return_value=True), \
         patch("app.services.permissions.get_user_module_permission", return_value=mock_perm):
        response_ok = client.get("/test-permission")
        assert response_ok.status_code == status.HTTP_200_OK
        assert response_ok.json() == {"message": "success"}

    app.dependency_overrides.clear()


# ==============================================================================
# Migration AST & Integrity Tests
# ==============================================================================

def test_user_module_permission_migration_ast() -> None:
    """Verify user_module_permission migration creates only intended objects and down_revision is f46f50205034."""
    versions_dir = Path(__file__).resolve().parent.parent / "alembic" / "versions"
    migration_files = list(versions_dir.glob("*_create_user_module_permission.py"))
    assert len(migration_files) == 1, "Expected exactly 1 create_user_module_permission migration"

    content = migration_files[0].read_text(encoding="utf-8")
    assert "down_revision: Union[str, None] = 'f46f50205034'" in content or "down_revision = 'f46f50205034'" in content

    tree = ast.parse(content)
    created_tables = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute) and node.func.attr == "create_table":
                if node.args and isinstance(node.args[0], ast.Constant):
                    created_tables.append(node.args[0].value)

    assert created_tables == ["user_module_permission"], f"Migration should create only user_module_permission, got: {created_tables}"
