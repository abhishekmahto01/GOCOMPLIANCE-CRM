"""Unit tests for Department Master model, schemas, migration, and seed logic."""
import ast
import uuid
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError
from sqlalchemy.dialects.postgresql import UUID

from alembic.config import Config
from alembic.script import ScriptDirectory
from app.database.base import Base
from app.models.company import Company
from app.models.department import Department
from app.schemas.department import (
    DepartmentCreate,
    DepartmentRead,
    DepartmentUpdate,
)
from app.scripts.seed_departments import (
    DEFAULT_DEPARTMENTS,
    REQUIRED_COMPANY_CODES,
    generate_department_uuid,
    seed_departments,
)


# ==============================================================================
# Model Tests
# ==============================================================================

def test_department_model_table_name_and_metadata() -> None:
    """Verify table name and metadata registration for department_master."""
    assert Department.__tablename__ == "department_master"
    assert "department_master" in Base.metadata.tables
    assert set(Base.metadata.tables.keys()) == {"company_master", "department_master"}


def test_department_model_columns() -> None:
    """Verify department_master columns, types, and primary key."""
    table = Department.__table__
    columns = table.columns

    expected_columns = {
        "department_id",
        "company_id",
        "department_code",
        "department_name",
        "description",
        "status",
        "created_at",
        "updated_at",
    }
    assert set(columns.keys()) == expected_columns

    # Primary key
    pk_cols = [col.name for col in table.primary_key.columns]
    assert pk_cols == ["department_id"]

    # Types and Nullability
    assert isinstance(columns["department_id"].type, UUID)
    assert isinstance(columns["company_id"].type, UUID)
    assert columns["company_id"].nullable is False
    assert columns["department_code"].nullable is False
    assert columns["department_name"].nullable is False
    assert columns["description"].nullable is True
    assert columns["status"].nullable is False
    assert columns["created_at"].nullable is False
    assert columns["updated_at"].nullable is False


def test_department_model_foreign_key_and_constraints() -> None:
    """Verify foreign key ON DELETE RESTRICT and unique/check constraints."""
    table = Department.__table__

    # Foreign Key
    fk_list = list(table.foreign_keys)
    assert len(fk_list) == 1
    fk = fk_list[0]
    assert fk.column.table.name == "company_master"
    assert fk.column.name == "company_id"
    assert fk.ondelete == "RESTRICT"

    # Composite Unique constraints
    unique_col_sets = []
    for uc in table.constraints:
        if hasattr(uc, "columns") and not getattr(uc, "primary_key", False):
            unique_col_sets.append({c.name for c in uc.columns})

    assert {"company_id", "department_code"} in unique_col_sets
    assert {"company_id", "department_name"} in unique_col_sets

    # Check constraints
    ck_names = {ck.name for ck in table.constraints if hasattr(ck, "sqltext")}
    assert "chk_department_status_valid" in ck_names
    assert "chk_department_code_format" in ck_names


def test_department_orm_relationships() -> None:
    """Verify bi-directional ORM relationship between Company and Department."""
    company_mapper = Company.__mapper__
    dept_mapper = Department.__mapper__

    assert "departments" in company_mapper.relationships
    assert "company" in dept_mapper.relationships

    assert company_mapper.relationships["departments"].back_populates == "company"
    assert dept_mapper.relationships["company"].back_populates == "departments"


# ==============================================================================
# Pydantic Schema Tests
# ==============================================================================

def test_department_create_normalization_and_validation() -> None:
    """Verify normalization of department codes and valid schema creation."""
    comp_id = uuid.uuid4()
    dept = DepartmentCreate(
        company_id=comp_id,
        department_code="  sales_ops  ",
        department_name="  Sales & Operations  ",
        description="  Lead acquisition and compliance casework  ",
        status="active",
    )
    assert dept.company_id == comp_id
    assert dept.department_code == "SALES_OPS"
    assert dept.department_name == "Sales & Operations"
    assert dept.description == "Lead acquisition and compliance casework"
    assert dept.status == "ACTIVE"


def test_department_schema_invalid_code() -> None:
    """Verify that invalid department codes with numbers/special chars are rejected."""
    comp_id = uuid.uuid4()

    # Code with invalid character '-'
    with pytest.raises(ValidationError):
        DepartmentCreate(
            company_id=comp_id,
            department_code="SALES-OPS",
            department_name="Sales Operations",
        )

    # Code with numbers
    with pytest.raises(ValidationError):
        DepartmentCreate(
            company_id=comp_id,
            department_code="SALES123",
            department_name="Sales Operations",
        )

    # Blank department name
    with pytest.raises(ValidationError):
        DepartmentCreate(
            company_id=comp_id,
            department_code="SALES",
            department_name="   ",
        )

    # Invalid status
    with pytest.raises(ValidationError):
        DepartmentCreate(
            company_id=comp_id,
            department_code="SALES",
            department_name="Sales",
            status="ARCHIVED",
        )


def test_department_update_schema() -> None:
    """Verify DepartmentUpdate optional fields and validation."""
    update_data = DepartmentUpdate(
        department_name="Updated Department Name",
        status="inactive",
    )
    assert update_data.department_name == "Updated Department Name"
    assert update_data.status == "INACTIVE"
    assert update_data.description is None


def test_department_read_schema() -> None:
    """Verify DepartmentRead schema attributes."""
    dept_id = uuid.uuid4()
    comp_id = uuid.uuid4()
    dept_read = DepartmentRead(
        department_id=dept_id,
        company_id=comp_id,
        department_code="RND",
        department_name="R&D",
        description="Research and Development",
        status="ACTIVE",
        created_at="2026-09-20T12:00:00Z",
        updated_at="2026-09-20T12:00:00Z",
    )
    assert dept_read.department_id == dept_id
    assert dept_read.company_id == comp_id
    assert dept_read.department_code == "RND"


# ==============================================================================
# Migration Safety Tests
# ==============================================================================

def test_department_migration_creates_only_department_master() -> None:
    """Verify that the Stage 5 migration touches only department_master table."""
    backend_dir = Path(__file__).resolve().parent.parent
    ini_path = backend_dir / "alembic.ini"
    cfg = Config(str(ini_path))
    cfg.set_main_option("script_location", str(backend_dir / "alembic"))

    script_dir = ScriptDirectory.from_config(cfg)
    revisions = list(script_dir.walk_revisions())

    dept_rev = next((r for r in revisions if "create_department_master" in (r.doc or "")), None)
    assert dept_rev is not None, "create_department_master revision must exist"

    # Verify down_revision is Stage 4 revision
    company_rev = next((r for r in revisions if "create_company_master" in (r.doc or "")), None)
    assert dept_rev.down_revision == company_rev.revision

    migration_file = Path(dept_rev.path)
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

    assert created_tables == ["department_master"]
    assert dropped_tables == ["department_master"]
    assert "fk_department_company_id" in content
    assert "RESTRICT" in content


# ==============================================================================
# Seed Logic Tests
# ==============================================================================

def test_deterministic_department_uuid() -> None:
    """Verify deterministic UUIDs produce consistent IDs for (company, dept) pairs."""
    id1 = generate_department_uuid("GOCOMPLIANCES", "SALES")
    id2 = generate_department_uuid("gocompliances", "sales")
    id3 = generate_department_uuid("ENTERPERNERSHIP", "SALES")

    assert id1 == id2, "UUID generation must be case-insensitive and deterministic"
    assert id1 != id3, "Same department under different companies must have distinct UUIDs"


def test_seed_departments_idempotency_and_missing_company_guard() -> None:
    """Verify seed function inserts 12 records on run 1, skips on run 2, and fails if company is missing."""
    companies_mock = {
        code: Company(
            company_id=uuid.uuid5(uuid.NAMESPACE_DNS, code),
            company_code=code,
            company_name=code.capitalize(),
            employee_code_prefix=code[:2],
        )
        for code in REQUIRED_COMPANY_CODES
    }

    dept_storage: dict = {}

    class MockSession:
        def __init__(self, provide_companies=True):
            self.provide_companies = provide_companies
            self.added = []
            self.committed = False
            self.rolled_back = False

        def execute(self, statement):
            mock_result = MagicMock()
            params = statement.compile().params

            # If querying Company
            if "company_master" in str(statement) or any(c in str(params) for c in REQUIRED_COMPANY_CODES):
                code = None
                for v in params.values():
                    if v in companies_mock:
                        code = v
                        break
                mock_result.scalar_one_or_none.return_value = (
                    companies_mock.get(code) if self.provide_companies else None
                )
                return mock_result

            # If querying Department
            target_key = None
            for comp_id, comp_obj in companies_mock.items():
                for dept_def in DEFAULT_DEPARTMENTS:
                    d_code = dept_def["department_code"]
                    if d_code in str(params.values()):
                        target_key = (params.get("company_id_1"), d_code)

            mock_result.scalar_one_or_none.return_value = dept_storage.get(target_key)
            return mock_result

        def add(self, entity):
            key = (entity.company_id, entity.department_code)
            dept_storage[key] = entity
            self.added.append(entity)

        def commit(self):
            self.committed = True

        def rollback(self):
            self.rolled_back = True

    # Test Missing Company Guard
    missing_comp_db = MockSession(provide_companies=False)
    with pytest.raises(ValueError) as exc_info:
        seed_departments(missing_comp_db)
    assert "Required company" in str(exc_info.value)

    # First Run (Full Insert of 12)
    mock_db = MockSession(provide_companies=True)
    inserted, skipped = seed_departments(mock_db)
    assert inserted == 12
    assert skipped == 0
    assert len(dept_storage) == 12

    # Second Run (Full Skip of 12)
    mock_db2 = MockSession(provide_companies=True)
    inserted2, skipped2 = seed_departments(mock_db2)
    assert inserted2 == 0
    assert skipped2 == 12
    assert len(dept_storage) == 12
