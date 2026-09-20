"""Unit tests for Designation Master model, schemas, migration, and seed logic."""
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
from app.models.designation import Designation
from app.schemas.designation import (
    DesignationCreate,
    DesignationRead,
    DesignationUpdate,
)
from app.scripts.seed_designations import (
    DEFAULT_DESIGNATIONS,
    REQUIRED_COMPANY_CODES,
    generate_designation_uuid,
    seed_designations,
)


# ==============================================================================
# Model Tests
# ==============================================================================

def test_designation_model_table_name_and_metadata() -> None:
    """Verify table name and metadata registration for designation_master."""
    assert Designation.__tablename__ == "designation_master"
    assert "designation_master" in Base.metadata.tables
    assert set(Base.metadata.tables.keys()) == {
        "company_master",
        "department_master",
        "designation_master",
        "user_master",
        "auth_refresh_token",
        "module_master",
        "user_module_permission",
    }


def test_designation_model_columns() -> None:
    """Verify designation_master columns, types, primary key, and absence of department/permission fields."""
    table = Designation.__table__
    columns = table.columns

    expected_columns = {
        "designation_id",
        "company_id",
        "designation_code",
        "designation_name",
        "level_rank",
        "is_managerial",
        "description",
        "status",
        "created_at",
        "updated_at",
    }
    assert set(columns.keys()) == expected_columns

    # Primary key
    pk_cols = [col.name for col in table.primary_key.columns]
    assert pk_cols == ["designation_id"]

    # Ensure no department or permission coupling
    assert "department_id" not in columns
    assert "permission" not in "".join(columns.keys())
    assert "role" not in "".join(columns.keys())

    # Types and Nullability
    assert isinstance(columns["designation_id"].type, UUID)
    assert isinstance(columns["company_id"].type, UUID)
    assert columns["company_id"].nullable is False
    assert columns["designation_code"].nullable is False
    assert columns["designation_name"].nullable is False
    assert columns["level_rank"].nullable is False
    assert columns["is_managerial"].nullable is False
    assert columns["description"].nullable is True
    assert columns["status"].nullable is False
    assert columns["created_at"].nullable is False
    assert columns["updated_at"].nullable is False


def test_designation_model_foreign_key_and_constraints() -> None:
    """Verify foreign key ON DELETE RESTRICT and unique/check constraints."""
    table = Designation.__table__

    # Foreign Key (to company_master only)
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

    assert {"company_id", "designation_code"} in unique_col_sets
    assert {"company_id", "designation_name"} in unique_col_sets

    # Check constraints
    ck_names = {ck.name for ck in table.constraints if hasattr(ck, "sqltext")}
    assert "chk_designation_level_rank_positive" in ck_names
    assert "chk_designation_status_valid" in ck_names
    assert "chk_designation_code_format" in ck_names


def test_designation_orm_relationships() -> None:
    """Verify bi-directional ORM relationship between Company and Designation."""
    company_mapper = Company.__mapper__
    desig_mapper = Designation.__mapper__

    assert "designations" in company_mapper.relationships
    assert "company" in desig_mapper.relationships

    assert company_mapper.relationships["designations"].back_populates == "company"
    assert desig_mapper.relationships["company"].back_populates == "designations"

    # Ensure no department relationship on Designation
    assert "department" not in desig_mapper.relationships
    assert "departments" not in desig_mapper.relationships


# ==============================================================================
# Pydantic Schema Tests
# ==============================================================================

def test_designation_create_normalization_and_validation() -> None:
    """Verify normalization of designation codes and valid schema creation."""
    comp_id = uuid.uuid4()
    desig = DesignationCreate(
        company_id=comp_id,
        designation_code="  senior_manager  ",
        designation_name="  Senior Manager  ",
        level_rank=45,
        is_managerial=True,
        description="  Supervises multiple teams  ",
        status="active",
    )
    assert desig.company_id == comp_id
    assert desig.designation_code == "SENIOR_MANAGER"
    assert desig.designation_name == "Senior Manager"
    assert desig.level_rank == 45
    assert desig.is_managerial is True
    assert desig.description == "Supervises multiple teams"
    assert desig.status == "ACTIVE"


def test_designation_schema_invalid_code_and_rank() -> None:
    """Verify that invalid designation codes and zero/negative ranks are rejected."""
    comp_id = uuid.uuid4()

    # Code with invalid character '-'
    with pytest.raises(ValidationError):
        DesignationCreate(
            company_id=comp_id,
            designation_code="SR-MANAGER",
            designation_name="Senior Manager",
            level_rank=40,
        )

    # Blank designation name
    with pytest.raises(ValidationError):
        DesignationCreate(
            company_id=comp_id,
            designation_code="MANAGER",
            designation_name="   ",
            level_rank=40,
        )

    # Zero level_rank
    with pytest.raises(ValidationError):
        DesignationCreate(
            company_id=comp_id,
            designation_code="MANAGER",
            designation_name="Manager",
            level_rank=0,
        )

    # Negative level_rank
    with pytest.raises(ValidationError):
        DesignationCreate(
            company_id=comp_id,
            designation_code="MANAGER",
            designation_name="Manager",
            level_rank=-10,
        )

    # Invalid status
    with pytest.raises(ValidationError):
        DesignationCreate(
            company_id=comp_id,
            designation_code="MANAGER",
            designation_name="Manager",
            level_rank=40,
            status="PENDING",
        )


def test_designation_update_schema() -> None:
    """Verify DesignationUpdate optional fields and validation."""
    update_data = DesignationUpdate(
        designation_name="Principal Manager",
        level_rank=48,
        is_managerial=True,
        status="inactive",
    )
    assert update_data.designation_name == "Principal Manager"
    assert update_data.level_rank == 48
    assert update_data.is_managerial is True
    assert update_data.status == "INACTIVE"
    assert update_data.description is None


def test_designation_read_schema() -> None:
    """Verify DesignationRead schema attributes and from_attributes compatibility."""
    desig_id = uuid.uuid4()
    comp_id = uuid.uuid4()
    desig_read = DesignationRead(
        designation_id=desig_id,
        company_id=comp_id,
        designation_code="DIRECTOR",
        designation_name="Director",
        level_rank=60,
        is_managerial=True,
        description="Executive business director",
        status="ACTIVE",
        created_at="2026-09-20T12:00:00Z",
        updated_at="2026-09-20T12:00:00Z",
    )
    assert desig_read.designation_id == desig_id
    assert desig_read.company_id == comp_id
    assert desig_read.designation_code == "DIRECTOR"
    assert desig_read.is_managerial is True


# ==============================================================================
# Migration Safety Tests
# ==============================================================================

def test_designation_migration_creates_only_designation_master() -> None:
    """Verify that the Stage 6 migration touches only designation_master table."""
    backend_dir = Path(__file__).resolve().parent.parent
    ini_path = backend_dir / "alembic.ini"
    cfg = Config(str(ini_path))
    cfg.set_main_option("script_location", str(backend_dir / "alembic"))

    script_dir = ScriptDirectory.from_config(cfg)
    revisions = list(script_dir.walk_revisions())

    desig_rev = next((r for r in revisions if "create_designation_master" in (r.doc or "")), None)
    assert desig_rev is not None, "create_designation_master revision must exist"

    # Verify down_revision is Stage 5 revision
    dept_rev = next((r for r in revisions if "create_department_master" in (r.doc or "")), None)
    assert desig_rev.down_revision == dept_rev.revision

    migration_file = Path(desig_rev.path)
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

    assert created_tables == ["designation_master"]
    assert dropped_tables == ["designation_master"]
    assert "fk_designation_company_id" in content
    assert "RESTRICT" in content


# ==============================================================================
# Seed Logic Tests
# ==============================================================================

def test_deterministic_designation_uuid() -> None:
    """Verify deterministic UUIDs produce consistent IDs for (company, designation) pairs."""
    id1 = generate_designation_uuid("GOCOMPLIANCES", "MANAGER")
    id2 = generate_designation_uuid("gocompliances", "manager")
    id3 = generate_designation_uuid("ENTERPERNERSHIP", "MANAGER")

    assert id1 == id2, "UUID generation must be case-insensitive and deterministic"
    assert id1 != id3, "Same designation under different companies must have distinct UUIDs"


def test_seed_designations_ranks_and_managerial_flags() -> None:
    """Verify DEFAULT_DESIGNATIONS contains 6 titles with correct ranks and managerial flags."""
    assert len(DEFAULT_DESIGNATIONS) == 6
    ranks = [d["level_rank"] for d in DEFAULT_DESIGNATIONS]
    assert ranks == [10, 20, 30, 40, 50, 60]

    # Check managerial flags
    assert DEFAULT_DESIGNATIONS[0]["is_managerial"] is False  # EXECUTIVE
    assert DEFAULT_DESIGNATIONS[1]["is_managerial"] is False  # SENIOR_EXECUTIVE
    assert DEFAULT_DESIGNATIONS[2]["is_managerial"] is True   # ASSISTANT_MANAGER
    assert DEFAULT_DESIGNATIONS[3]["is_managerial"] is True   # MANAGER
    assert DEFAULT_DESIGNATIONS[4]["is_managerial"] is True   # HEAD
    assert DEFAULT_DESIGNATIONS[5]["is_managerial"] is True   # DIRECTOR


def test_seed_designations_idempotency_and_missing_company_guard() -> None:
    """Verify seed function inserts 18 records on run 1, skips on run 2, and fails if company is missing."""
    companies_mock = {
        code: Company(
            company_id=uuid.uuid5(uuid.NAMESPACE_DNS, code),
            company_code=code,
            company_name=code.capitalize(),
            employee_code_prefix=code[:2],
        )
        for code in REQUIRED_COMPANY_CODES
    }

    desig_storage: dict = {}

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

            # If querying Designation
            target_key = None
            for comp_id, comp_obj in companies_mock.items():
                for desig_def in DEFAULT_DESIGNATIONS:
                    d_code = desig_def["designation_code"]
                    if d_code in str(params.values()):
                        target_key = (params.get("company_id_1"), d_code)

            mock_result.scalar_one_or_none.return_value = desig_storage.get(target_key)
            return mock_result

        def add(self, entity):
            key = (entity.company_id, entity.designation_code)
            desig_storage[key] = entity
            self.added.append(entity)

        def commit(self):
            self.committed = True

        def rollback(self):
            self.rolled_back = True

    # Test Missing Company Guard
    missing_comp_db = MockSession(provide_companies=False)
    with pytest.raises(ValueError) as exc_info:
        seed_designations(missing_comp_db)
    assert "Required company" in str(exc_info.value)

    # First Run (Full Insert of 18)
    mock_db = MockSession(provide_companies=True)
    inserted, skipped = seed_designations(mock_db)
    assert inserted == 18
    assert skipped == 0
    assert len(desig_storage) == 18

    # Second Run (Full Skip of 18)
    mock_db2 = MockSession(provide_companies=True)
    inserted2, skipped2 = seed_designations(mock_db2)
    assert inserted2 == 0
    assert skipped2 == 18
    assert len(desig_storage) == 18
