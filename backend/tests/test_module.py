"""Tests for Module Master model, schemas, migrations, and seeding."""
import ast
from pathlib import Path
from unittest.mock import MagicMock
import uuid
from datetime import datetime, timezone

import pytest
from alembic.config import Config
from alembic.script import ScriptDirectory
from pydantic import ValidationError
from sqlalchemy.dialects.postgresql import UUID

from app.database.base import Base
from app.models.module import Module
from app.schemas.module import (
    ModuleCreate,
    ModuleRead,
    ModuleTreeRead,
    ModuleUpdate,
)
from app.scripts.seed_modules import (
    INITIAL_MODULES,
    get_deterministic_module_uuid,
    seed_modules,
)


# ==============================================================================
# Model Tests
# ==============================================================================

def test_module_model_table_name_and_metadata() -> None:
    """Verify table name and metadata registration for module_master."""
    assert Module.__tablename__ == "module_master"
    assert "module_master" in Base.metadata.tables


def test_module_model_columns() -> None:
    """Verify module_master columns, types, primary key, and nullability."""
    table = Module.__table__
    columns = table.columns

    expected_columns = {
        "module_id",
        "module_code",
        "module_name",
        "parent_module_id",
        "route",
        "description",
        "display_order",
        "is_navigation",
        "status",
        "created_at",
        "updated_at",
    }
    assert set(columns.keys()) == expected_columns

    # Primary key
    assert columns["module_id"].primary_key is True
    assert isinstance(columns["module_id"].type, UUID)

    # Nullability
    assert columns["module_code"].nullable is False
    assert columns["module_name"].nullable is False
    assert columns["parent_module_id"].nullable is True
    assert columns["route"].nullable is True
    assert columns["description"].nullable is True
    assert columns["display_order"].nullable is False
    assert columns["is_navigation"].nullable is False
    assert columns["status"].nullable is False


def test_module_model_foreign_key_and_constraints() -> None:
    """Verify self-referencing foreign key, RESTRICT deletion, and check constraints."""
    table = Module.__table__

    # Foreign key
    fks = {fk.name: fk for fk in table.foreign_key_constraints}
    assert "fk_module_parent_module_id" in fks
    fk = fks["fk_module_parent_module_id"]
    assert fk.ondelete == "RESTRICT"
    assert "module_master.module_id" in [c.target_fullname for c in fk.elements]

    # Check constraints
    checks = {c.name: c for c in table.constraints if hasattr(c, "name")}
    assert "chk_module_code_format" in checks
    assert "chk_module_route_format" in checks
    assert "chk_module_display_order_non_negative" in checks
    assert "chk_module_status_valid" in checks
    assert "chk_module_self_parent" in checks


def test_module_orm_relationships() -> None:
    """Verify self-referencing ORM relationships (parent / children)."""
    assert hasattr(Module, "parent")
    assert hasattr(Module, "children")

    rel_parent = Module.parent.property
    assert rel_parent.back_populates == "children"

    rel_children = Module.children.property
    assert rel_children.back_populates == "parent"


# ==============================================================================
# Schema Tests
# ==============================================================================

def test_module_create_normalization_and_validation() -> None:
    """Verify ModuleCreate normalizes codes, routes, and trims whitespace."""
    parent_id = uuid.uuid4()
    mod = ModuleCreate(
        module_code="  admin_companies  ",
        module_name="  Companies Management  ",
        parent_module_id=parent_id,
        route=" /admin/companies ",
        description="  Manage company entities  ",
        display_order=10,
        is_navigation=True,
        status="active",
    )

    assert mod.module_code == "ADMIN_COMPANIES"
    assert mod.module_name == "Companies Management"
    assert mod.parent_module_id == parent_id
    assert mod.route == "/admin/companies"
    assert mod.description == "Manage company entities"
    assert mod.display_order == 10
    assert mod.is_navigation is True
    assert mod.status == "ACTIVE"


def test_module_schema_invalid_code() -> None:
    """Verify module_code with invalid characters raises ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        ModuleCreate(
            module_code="admin-companies",  # Hyphen is invalid (only A-Z and _)
            module_name="Companies",
        )
    assert "module_code must contain only uppercase letters and underscores" in str(exc_info.value)


def test_module_schema_invalid_route() -> None:
    """Verify route not starting with '/' raises ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        ModuleCreate(
            module_code="ADMIN",
            module_name="Admin",
            route="admin",  # Missing leading slash
        )
    assert "route must start with a forward slash" in str(exc_info.value)


def test_module_schema_invalid_status() -> None:
    """Verify invalid status string raises ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        ModuleCreate(
            module_code="ADMIN",
            module_name="Admin",
            status="PENDING",
        )
    assert "status must be one of: ACTIVE, INACTIVE" in str(exc_info.value)


def test_module_schema_negative_display_order() -> None:
    """Verify negative display_order raises ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        ModuleCreate(
            module_code="ADMIN",
            module_name="Admin",
            display_order=-1,
        )
    assert "display_order" in str(exc_info.value)


def test_module_update_schema() -> None:
    """Verify optional fields in ModuleUpdate schema."""
    update = ModuleUpdate(
        module_name="  Updated Admin  ",
        display_order=15,
        status="inactive",
    )
    assert update.module_name == "Updated Admin"
    assert update.display_order == 15
    assert update.status == "INACTIVE"
    assert update.route is None


def test_module_read_and_tree_schema() -> None:
    """Verify ModuleRead and ModuleTreeRead serialization with hierarchical children."""
    parent_id = uuid.uuid4()
    child_id = uuid.uuid4()
    now = datetime.now(timezone.utc)

    parent_obj = Module(
        module_id=parent_id,
        module_code="ADMIN",
        module_name="Admin",
        parent_module_id=None,
        route="/admin",
        description="Root Admin",
        display_order=10,
        is_navigation=True,
        status="ACTIVE",
        created_at=now,
        updated_at=now,
    )

    child_obj = Module(
        module_id=child_id,
        module_code="ADMIN_COMPANIES",
        module_name="Companies",
        parent_module_id=parent_id,
        route="/admin/companies",
        description="Company Management",
        display_order=10,
        is_navigation=True,
        status="ACTIVE",
        created_at=now,
        updated_at=now,
    )

    child_tree = ModuleTreeRead.model_validate(child_obj)
    assert child_tree.module_code == "ADMIN_COMPANIES"
    assert child_tree.children == []

    parent_tree = ModuleTreeRead(
        module_id=parent_obj.module_id,
        module_code=parent_obj.module_code,
        module_name=parent_obj.module_name,
        parent_module_id=parent_obj.parent_module_id,
        route=parent_obj.route,
        description=parent_obj.description,
        display_order=parent_obj.display_order,
        is_navigation=parent_obj.is_navigation,
        status=parent_obj.status,
        created_at=parent_obj.created_at,
        updated_at=parent_obj.updated_at,
        children=[child_tree],
    )
    assert len(parent_tree.children) == 1
    assert parent_tree.children[0].module_code == "ADMIN_COMPANIES"


# ==============================================================================
# Migration Safety Tests
# ==============================================================================

def test_module_migration_creates_only_module_master() -> None:
    """Verify Stage 8 migration touches only module_master and references Stage 7B revision."""
    backend_dir = Path(__file__).resolve().parent.parent
    ini_path = backend_dir / "alembic.ini"
    cfg = Config(str(ini_path))
    cfg.set_main_option("script_location", str(backend_dir / "alembic"))

    script_dir = ScriptDirectory.from_config(cfg)
    revisions = list(script_dir.walk_revisions())

    module_rev = next((r for r in revisions if "create_module_master" in (r.doc or "")), None)
    assert module_rev is not None, "create_module_master revision must exist"

    # Verify down_revision is Stage 7B revision (add_authentication_foundation)
    auth_rev = next((r for r in revisions if "add_authentication_foundation" in (r.doc or "")), None)
    assert module_rev.down_revision == auth_rev.revision

    migration_file = Path(module_rev.path)
    content = migration_file.read_text(encoding="utf-8")

    tree = ast.parse(content)
    created_tables = []
    dropped_tables = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr == "create_table" and node.args:
                if isinstance(node.args[0], ast.Constant):
                    created_tables.append(node.args[0].value)
            elif node.func.attr == "drop_table" and node.args:
                if isinstance(node.args[0], ast.Constant):
                    dropped_tables.append(node.args[0].value)

    assert created_tables == ["module_master"]
    assert dropped_tables == ["module_master"]


# ==============================================================================
# Seed Tests
# ==============================================================================

def test_deterministic_module_uuid() -> None:
    """Verify deterministic module UUID generation is consistent and unique."""
    id_admin1 = get_deterministic_module_uuid("ADMIN")
    id_admin2 = get_deterministic_module_uuid("admin")
    id_sales = get_deterministic_module_uuid("SALES")

    assert id_admin1 == id_admin2
    assert id_admin1 != id_sales
    assert isinstance(id_admin1, uuid.UUID)


def test_seed_modules_idempotency_and_hierarchy() -> None:
    """Verify seed_modules inserts 8 records on initial run and skips on subsequent runs."""
    mock_session = MagicMock()

    # Pass 1: Empty DB -> 8 inserts
    mock_session.scalars.return_value.all.return_value = []
    mock_session.scalar.side_effect = [
        get_deterministic_module_uuid("ADMIN"),  # for ADMIN_COMPANIES
        get_deterministic_module_uuid("ADMIN"),  # for ADMIN_DEPARTMENTS
        get_deterministic_module_uuid("ADMIN"),  # for ADMIN_DESIGNATIONS
        get_deterministic_module_uuid("ADMIN"),  # for ADMIN_EMPLOYEES
        get_deterministic_module_uuid("ADMIN"),  # for ADMIN_ACCESS
    ]

    inserted, skipped = seed_modules(mock_session)
    assert inserted == 8
    assert skipped == 0
    assert mock_session.commit.call_count == 1

    # Pass 2: All 8 modules exist -> 8 skipped, 0 inserted
    mock_session.reset_mock()
    all_codes = [m["module_code"] for m in INITIAL_MODULES]
    mock_session.scalars.return_value.all.return_value = all_codes

    inserted, skipped = seed_modules(mock_session)
    assert inserted == 0
    assert skipped == 8
    assert mock_session.commit.call_count == 1


def test_seed_modules_missing_parent_guard() -> None:
    """Verify seed_modules raises ValueError when parent module cannot be resolved."""
    mock_session = MagicMock()

    mock_session.scalars.return_value.all.return_value = []
    # Parent module lookup returns None (missing parent)
    mock_session.scalar.return_value = None

    with pytest.raises(ValueError) as exc_info:
        seed_modules(mock_session)
    assert "could not be resolved for child module" in str(exc_info.value)
