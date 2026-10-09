"""Unit tests for Department Master model, schemas, and seed logic."""
import uuid
from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError
from sqlalchemy.dialects.postgresql import UUID

from app.database.base import Base
from app.models.department import Department
from app.models.user import User
from app.schemas.department import (
    DepartmentCreate,
    DepartmentRead,
    DepartmentUpdate,
)
from app.scripts.seed_departments import (
    DEFAULT_DEPARTMENTS,
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


def test_department_model_columns() -> None:
    """Verify department_master columns, types, and primary key."""
    table = Department.__table__
    columns = table.columns

    expected_columns = {
        "department_id",
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
    assert columns["department_code"].nullable is False
    assert columns["department_name"].nullable is False
    assert columns["description"].nullable is True
    assert columns["status"].nullable is False
    assert columns["created_at"].nullable is False
    assert columns["updated_at"].nullable is False


def test_department_model_foreign_key_and_constraints() -> None:
    """Verify unique/check constraints and absence of company foreign key."""
    table = Department.__table__

    # No Foreign Key on Department Master
    fk_list = list(table.foreign_keys)
    assert len(fk_list) == 0

    # Unique constraints
    unique_col_sets = []
    for uc in table.constraints:
        if hasattr(uc, "columns") and not getattr(uc, "primary_key", False):
            unique_col_sets.append({c.name for c in uc.columns})

    assert {"department_code"} in unique_col_sets
    assert {"department_name"} in unique_col_sets

    # Check constraints
    ck_names = {ck.name for ck in table.constraints if hasattr(ck, "sqltext")}
    assert "chk_department_status_valid" in ck_names
    assert "chk_department_code_format" in ck_names


def test_department_orm_relationships() -> None:
    """Verify ORM relationship between Department and User."""
    dept_mapper = Department.__mapper__
    assert "users" in dept_mapper.relationships
    assert dept_mapper.relationships["users"].back_populates == "department"


# ==============================================================================
# Pydantic Schema Tests
# ==============================================================================

def test_department_create_normalization_and_validation() -> None:
    """Verify normalization of department codes and valid schema creation."""
    dept = DepartmentCreate(
        department_code="  sales_ops  ",
        department_name="  Sales & Operations  ",
        description="  Lead acquisition and compliance casework  ",
        status="active",
    )
    assert dept.department_code == "SALES_OPS"
    assert dept.department_name == "Sales & Operations"
    assert dept.description == "Lead acquisition and compliance casework"
    assert dept.status == "ACTIVE"


def test_department_schema_invalid_code() -> None:
    """Verify that invalid department codes with numbers/special chars are rejected."""
    # Code with invalid character '-'
    with pytest.raises(ValidationError):
        DepartmentCreate(
            department_code="SALES-OPS",
            department_name="Sales Operations",
        )

    # Code with numbers
    with pytest.raises(ValidationError):
        DepartmentCreate(
            department_code="SALES123",
            department_name="Sales Operations",
        )

    # Blank department name
    with pytest.raises(ValidationError):
        DepartmentCreate(
            department_code="SALES",
            department_name="   ",
        )

    # Invalid status
    with pytest.raises(ValidationError):
        DepartmentCreate(
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
    dept_read = DepartmentRead(
        department_id=dept_id,
        department_code="RND",
        department_name="R&D",
        description="Research and Development",
        status="ACTIVE",
        created_at="2026-09-20T12:00:00Z",
        updated_at="2026-09-20T12:00:00Z",
    )
    assert dept_read.department_id == dept_id
    assert dept_read.department_code == "RND"


# ==============================================================================
# Seed Logic Tests
# ==============================================================================

def test_deterministic_department_uuid() -> None:
    """Verify deterministic UUIDs produce consistent IDs for department codes."""
    id1 = generate_department_uuid("SALES")
    id2 = generate_department_uuid("sales")
    id3 = generate_department_uuid("OPERATIONS")

    assert id1 == id2, "UUID generation must be case-insensitive and deterministic"
    assert id1 != id3, "Different departments must have distinct UUIDs"


def test_seed_departments_idempotency() -> None:
    """Verify seed function inserts records on run 1, skips on run 2."""
    dept_storage: dict = {}

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
                if isinstance(v, str) and any(d["department_code"] == v for d in DEFAULT_DEPARTMENTS):
                    target_code = v
                    break

            mock_result.scalar_one_or_none.return_value = dept_storage.get(target_code)
            return mock_result

        def add(self, entity):
            dept_storage[entity.department_code] = entity
            self.added.append(entity)

        def commit(self):
            self.committed = True

        def rollback(self):
            self.rolled_back = True

    # First Run (Full Insert of DEFAULT_DEPARTMENTS)
    mock_db = MockSession()
    inserted, skipped = seed_departments(mock_db)
    assert inserted == len(DEFAULT_DEPARTMENTS)
    assert skipped == 0
    assert len(dept_storage) == len(DEFAULT_DEPARTMENTS)

    # Second Run (Full Skip)
    mock_db2 = MockSession()
    inserted2, skipped2 = seed_departments(mock_db2)
    assert inserted2 == 0
    assert skipped2 == len(DEFAULT_DEPARTMENTS)
    assert len(dept_storage) == len(DEFAULT_DEPARTMENTS)
