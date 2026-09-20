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
from app.schemas.company import (
    CompanyCreate,
    CompanyRead,
    CompanyUpdate,
)
from app.scripts.seed_companies import (
    INITIAL_COMPANIES,
    generate_company_uuid,
    seed_companies,
)


# ==============================================================================
# Model Tests
# ==============================================================================

def test_company_model_table_name_and_metadata() -> None:
    """Verify table name and that only company_master is in Base.metadata for Stage 4."""
    assert Company.__tablename__ == "company_master"
    assert "company_master" in Base.metadata.tables
    assert len(Base.metadata.tables) == 1, "Only company_master should be registered in Base.metadata in Stage 4"


def test_company_model_columns() -> None:
    """Verify company_master table columns and primary key."""
    table = Company.__table__
    columns = table.columns

    # Column existence
    expected_columns = {
        "company_id",
        "company_code",
        "company_name",
        "legal_name",
        "employee_code_prefix",
        "next_employee_number",
        "status",
        "created_at",
        "updated_at",
    }
    assert set(columns.keys()) == expected_columns

    # Primary key
    pk_cols = [col.name for col in table.primary_key.columns]
    assert pk_cols == ["company_id"]

    # Types and Nullability
    assert isinstance(columns["company_id"].type, UUID)
    assert columns["company_code"].nullable is False
    assert columns["company_name"].nullable is False
    assert columns["legal_name"].nullable is True
    assert columns["employee_code_prefix"].nullable is False
    assert columns["next_employee_number"].nullable is False
    assert columns["status"].nullable is False
    assert columns["created_at"].nullable is False
    assert columns["updated_at"].nullable is False


def test_company_model_constraints() -> None:
    """Verify unique constraints and check constraints on company_master."""
    table = Company.__table__

    # Unique constraints / indexes
    assert columns_are_unique(table, "company_code")
    assert columns_are_unique(table, "company_name")
    assert columns_are_unique(table, "employee_code_prefix")

    # Check constraints
    ck_names = {ck.name for ck in table.constraints if hasattr(ck, "sqltext")}
    assert "chk_company_next_employee_number_positive" in ck_names
    assert "chk_company_status_valid" in ck_names
    assert "chk_company_employee_code_prefix_format" in ck_names


def columns_are_unique(table, col_name: str) -> bool:
    for uc in table.constraints:
        if hasattr(uc, "columns") and [c.name for c in uc.columns] == [col_name]:
            return True
    for idx in table.indexes:
        if idx.unique and [c.name for c in idx.columns] == [col_name]:
            return True
    return False


# ==============================================================================
# Pydantic Schema Tests
# ==============================================================================

def test_company_create_normalization_and_validation() -> None:
    """Verify normalization of codes, prefixes, and valid data creation."""
    company = CompanyCreate(
        company_code="  gocompliances  ",
        company_name="  Gocompliances Private Limited  ",
        employee_code_prefix="  cg  ",
        next_employee_number=1,
        status="active",
    )
    assert company.company_code == "GOCOMPLIANCES"
    assert company.company_name == "Gocompliances Private Limited"
    assert company.employee_code_prefix == "CG"
    assert company.status == "ACTIVE"
    assert company.next_employee_number == 1
    assert company.legal_name is None


def test_company_schema_invalid_prefix() -> None:
    """Verify that invalid employee prefixes are rejected."""
    # Prefix too short (< 2 chars)
    with pytest.raises(ValidationError):
        CompanyCreate(
            company_code="TEST",
            company_name="Test Company",
            employee_code_prefix="C",
        )

    # Prefix too long (> 5 chars)
    with pytest.raises(ValidationError):
        CompanyCreate(
            company_code="TEST",
            company_name="Test Company",
            employee_code_prefix="TOOLONG",
        )

    # Prefix with numbers/symbols
    with pytest.raises(ValidationError):
        CompanyCreate(
            company_code="TEST",
            company_name="Test Company",
            employee_code_prefix="C1",
        )


def test_company_schema_invalid_number_and_status() -> None:
    """Verify next_employee_number <= 0 and invalid status are rejected."""
    # Zero next_employee_number
    with pytest.raises(ValidationError):
        CompanyCreate(
            company_code="TEST",
            company_name="Test Company",
            employee_code_prefix="TC",
            next_employee_number=0,
        )

    # Negative next_employee_number
    with pytest.raises(ValidationError):
        CompanyCreate(
            company_code="TEST",
            company_name="Test Company",
            employee_code_prefix="TC",
            next_employee_number=-5,
        )

    # Invalid status
    with pytest.raises(ValidationError):
        CompanyCreate(
            company_code="TEST",
            company_name="Test Company",
            employee_code_prefix="TC",
            status="PENDING",
        )


def test_company_update_schema() -> None:
    """Verify CompanyUpdate optional fields and validation."""
    update_data = CompanyUpdate(
        company_name="Updated Name",
        status="inactive",
    )
    assert update_data.company_name == "Updated Name"
    assert update_data.status == "INACTIVE"
    assert update_data.legal_name is None


def test_company_read_schema() -> None:
    """Verify CompanyRead schema attributes and from_attributes compatibility."""
    comp_id = uuid.uuid4()
    company_read = CompanyRead(
        company_id=comp_id,
        company_code="BRANDMINGO",
        company_name="Brandmingo",
        employee_code_prefix="BM",
        next_employee_number=1,
        status="ACTIVE",
        created_at="2026-09-20T12:00:00Z",
        updated_at="2026-09-20T12:00:00Z",
    )
    assert company_read.company_id == comp_id
    assert company_read.company_code == "BRANDMINGO"


# ==============================================================================
# Migration Safety Tests
# ==============================================================================

def test_company_migration_creates_only_company_master() -> None:
    """Verify that the Stage 4 migration touches only company_master table."""
    backend_dir = Path(__file__).resolve().parent.parent
    ini_path = backend_dir / "alembic.ini"
    cfg = Config(str(ini_path))
    cfg.set_main_option("script_location", str(backend_dir / "alembic"))

    script_dir = ScriptDirectory.from_config(cfg)
    revisions = list(script_dir.walk_revisions())

    # Find the create_company_master revision
    company_rev = next((r for r in revisions if "create_company_master" in (r.doc or "")), None)
    assert company_rev is not None, "create_company_master revision must exist"

    migration_file = Path(company_rev.path)
    content = migration_file.read_text(encoding="utf-8")

    # Inspect created tables in the migration AST
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

    assert created_tables == ["company_master"], f"Only company_master must be created, got: {created_tables}"
    assert dropped_tables == ["company_master"], f"Only company_master must be dropped, got: {dropped_tables}"


# ==============================================================================
# Seed Logic Tests
# ==============================================================================

def test_deterministic_company_uuid() -> None:
    """Verify deterministic UUIDs produce consistent IDs for identical codes."""
    id1 = generate_company_uuid("GOCOMPLIANCES")
    id2 = generate_company_uuid("gocompliances")
    id3 = generate_company_uuid("ENTERPERNERSHIP")

    assert id1 == id2, "UUID generation must be case-insensitive and deterministic"
    assert id1 != id3, "Different companies must have distinct UUIDs"


def test_seed_companies_idempotency() -> None:
    """Verify seed function inserts 3 records on run 1, and skips existing on run 2."""
    storage: dict = {}

    class MockSession:
        def __init__(self):
            self.added = []
            self.committed = False

        def execute(self, statement):
            mock_result = MagicMock()
            params = statement.compile().params
            target_code = None
            if params:
                for v in params.values():
                    if isinstance(v, str) and v.isupper():
                        target_code = v
                        break

            found = storage.get(target_code)
            mock_result.scalar_one_or_none.return_value = found
            return mock_result

        def add(self, entity):
            storage[entity.company_code] = entity
            self.added.append(entity)

        def commit(self):
            self.committed = True

        def rollback(self):
            pass

    # First run: should insert 3
    mock_db = MockSession()
    inserted, skipped = seed_companies(mock_db)
    assert inserted == 3
    assert skipped == 0
    assert len(storage) == 3
    assert "GOCOMPLIANCES" in storage
    assert "ENTERPERNERSHIP" in storage
    assert "BRANDMINGO" in storage

    # Second run: should skip all 3
    mock_db2 = MockSession()
    inserted2, skipped2 = seed_companies(mock_db2)
    assert inserted2 == 0
    assert skipped2 == 3
    assert len(storage) == 3
