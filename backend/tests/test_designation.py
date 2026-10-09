"""Unit tests for Designation Master model, schemas, and seed logic."""
import uuid
from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError
from sqlalchemy.dialects.postgresql import UUID

from app.database.base import Base
from app.models.designation import Designation
from app.models.user import User
from app.schemas.designation import (
    DesignationCreate,
    DesignationRead,
    DesignationUpdate,
)
from app.scripts.seed_designations import (
    DEFAULT_DESIGNATIONS,
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


def test_designation_model_columns() -> None:
    """Verify designation_master columns, types, primary key, and absence of department/permission fields."""
    table = Designation.__table__
    columns = table.columns

    expected_columns = {
        "designation_id",
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
    assert columns["designation_code"].nullable is False
    assert columns["designation_name"].nullable is False
    assert columns["level_rank"].nullable is False
    assert columns["is_managerial"].nullable is False
    assert columns["description"].nullable is True
    assert columns["status"].nullable is False
    assert columns["created_at"].nullable is False
    assert columns["updated_at"].nullable is False


def test_designation_model_foreign_key_and_constraints() -> None:
    """Verify unique/check constraints and absence of company foreign key."""
    table = Designation.__table__

    # No Foreign Key on Designation Master
    fk_list = list(table.foreign_keys)
    assert len(fk_list) == 0

    # Unique constraints
    unique_col_sets = []
    for uc in table.constraints:
        if hasattr(uc, "columns") and not getattr(uc, "primary_key", False):
            unique_col_sets.append({c.name for c in uc.columns})

    assert {"designation_code"} in unique_col_sets
    assert {"designation_name"} in unique_col_sets

    # Check constraints
    ck_names = {ck.name for ck in table.constraints if hasattr(ck, "sqltext")}
    assert "chk_designation_level_rank_positive" in ck_names
    assert "chk_designation_status_valid" in ck_names
    assert "chk_designation_code_format" in ck_names


def test_designation_orm_relationships() -> None:
    """Verify ORM relationship between Designation and User."""
    desig_mapper = Designation.__mapper__
    assert "users" in desig_mapper.relationships
    assert desig_mapper.relationships["users"].back_populates == "designation"


# ==============================================================================
# Pydantic Schema Tests
# ==============================================================================

def test_designation_create_normalization_and_validation() -> None:
    """Verify normalization of designation codes and valid schema creation."""
    desig = DesignationCreate(
        designation_code="  senior_manager  ",
        designation_name="  Senior Manager  ",
        level_rank=45,
        is_managerial=True,
        description="  Supervises multiple teams  ",
        status="active",
    )
    assert desig.designation_code == "SENIOR_MANAGER"
    assert desig.designation_name == "Senior Manager"
    assert desig.level_rank == 45
    assert desig.is_managerial is True
    assert desig.description == "Supervises multiple teams"
    assert desig.status == "ACTIVE"


def test_designation_schema_invalid_code_and_rank() -> None:
    """Verify that invalid designation codes and zero/negative ranks are rejected."""
    # Code with invalid character '-'
    with pytest.raises(ValidationError):
        DesignationCreate(
            designation_code="SR-MANAGER",
            designation_name="Senior Manager",
            level_rank=40,
        )

    # Blank designation name
    with pytest.raises(ValidationError):
        DesignationCreate(
            designation_code="MANAGER",
            designation_name="   ",
            level_rank=40,
        )

    # Zero level_rank
    with pytest.raises(ValidationError):
        DesignationCreate(
            designation_code="MANAGER",
            designation_name="Manager",
            level_rank=0,
        )

    # Negative level_rank
    with pytest.raises(ValidationError):
        DesignationCreate(
            designation_code="MANAGER",
            designation_name="Manager",
            level_rank=-10,
        )

    # Invalid status
    with pytest.raises(ValidationError):
        DesignationCreate(
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
    desig_read = DesignationRead(
        designation_id=desig_id,
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
    assert desig_read.designation_code == "DIRECTOR"
    assert desig_read.is_managerial is True


# ==============================================================================
# Seed Logic Tests
# ==============================================================================

def test_deterministic_designation_uuid() -> None:
    """Verify deterministic UUIDs produce consistent IDs for designation codes."""
    id1 = generate_designation_uuid("MANAGER")
    id2 = generate_designation_uuid("manager")
    id3 = generate_designation_uuid("DIRECTOR")

    assert id1 == id2, "UUID generation must be case-insensitive and deterministic"
    assert id1 != id3, "Different designations must have distinct UUIDs"


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


def test_seed_designations_idempotency() -> None:
    """Verify seed function inserts records on run 1, skips on run 2."""
    desig_storage: dict = {}

    class MockSession:
        def __init__(self):
            self.added = []
            self.committed = False
            self.rolled_back = False

        def execute(self, statement):
            mock_result = MagicMock()
            params = statement.compile().params

            target_code = None
            for v in params.values():
                if isinstance(v, str) and any(d["designation_code"] == v for d in DEFAULT_DESIGNATIONS):
                    target_code = v
                    break

            mock_result.scalar_one_or_none.return_value = desig_storage.get(target_code)
            return mock_result

        def add(self, entity):
            desig_storage[entity.designation_code] = entity
            self.added.append(entity)

        def commit(self):
            self.committed = True

        def rollback(self):
            self.rolled_back = True

    # First Run (Full Insert of DEFAULT_DESIGNATIONS)
    mock_db = MockSession()
    inserted, skipped = seed_designations(mock_db)
    assert inserted == len(DEFAULT_DESIGNATIONS)
    assert skipped == 0
    assert len(desig_storage) == len(DEFAULT_DESIGNATIONS)

    # Second Run (Full Skip)
    mock_db2 = MockSession()
    inserted2, skipped2 = seed_designations(mock_db2)
    assert inserted2 == 0
    assert skipped2 == len(DEFAULT_DESIGNATIONS)
    assert len(desig_storage) == len(DEFAULT_DESIGNATIONS)
