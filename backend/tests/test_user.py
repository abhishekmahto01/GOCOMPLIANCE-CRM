"""Tests for User model, schemas, and Alembic migration."""
import ast
import glob
import os
import uuid
from datetime import date, datetime, timezone

import pytest
from pydantic import ValidationError
from sqlalchemy import CheckConstraint, ForeignKeyConstraint, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

from app.models.company import Company
from app.models.department import Department
from app.models.designation import Designation
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserRead,
    UserUpdate,
    normalize_email_address,
    normalize_mobile,
)


def test_user_model_table_name_and_metadata() -> None:
    """Verify User model table name, primary key, and registered columns."""
    assert User.__tablename__ == "user_master"
    table = User.__table__

    assert "user_id" in table.columns
    assert table.columns["user_id"].primary_key is True
    assert isinstance(table.columns["user_id"].type, UUID)


def test_user_model_columns() -> None:
    """Verify all required columns exist with proper types and nullability."""
    table = User.__table__
    cols = table.columns

    # Verify column existence and non-nullability
    assert cols["employee_code"].nullable is False
    assert cols["company_id"].nullable is False
    assert cols["department_id"].nullable is False
    assert cols["designation_id"].nullable is False
    assert cols["manager_user_id"].nullable is True
    assert cols["first_name"].nullable is False
    assert cols["middle_name"].nullable is True
    assert cols["last_name"].nullable is False
    assert cols["official_email"].nullable is False
    assert cols["personal_email"].nullable is True
    assert cols["mobile_number"].nullable is False
    assert cols["date_of_joining"].nullable is False
    assert cols["employment_type"].nullable is False
    assert cols["account_status"].nullable is False
    assert cols["created_at"].nullable is False
    assert cols["updated_at"].nullable is False


def test_user_model_foreign_keys_and_constraints() -> None:
    """Verify foreign keys and ondelete behavior on user_master."""
    table = User.__table__

    fks = {fk.name: fk for fk in table.foreign_key_constraints}

    assert "fk_user_company_id" in fks
    assert fks["fk_user_company_id"].ondelete == "RESTRICT"
    assert "company_master.company_id" in [c.target_fullname for c in fks["fk_user_company_id"].elements]

    assert "fk_user_department_id" in fks
    assert fks["fk_user_department_id"].ondelete == "RESTRICT"
    assert "department_master.department_id" in [c.target_fullname for c in fks["fk_user_department_id"].elements]

    assert "fk_user_designation_id" in fks
    assert fks["fk_user_designation_id"].ondelete == "RESTRICT"
    assert "designation_master.designation_id" in [c.target_fullname for c in fks["fk_user_designation_id"].elements]

    assert "fk_user_manager_user_id" in fks
    assert fks["fk_user_manager_user_id"].ondelete == "SET NULL"
    assert "user_master.user_id" in [c.target_fullname for c in fks["fk_user_manager_user_id"].elements]

    # Check constraints
    checks = {c.name: c for c in table.constraints if isinstance(c, CheckConstraint)}
    assert "chk_user_self_manager" in checks
    assert "chk_user_employment_type_valid" in checks
    assert "chk_user_account_status_valid" in checks


def test_user_orm_relationships() -> None:
    """Verify ORM relationships between User, Company, Department, Designation, and Self-Manager."""
    # User side
    assert hasattr(User, "company")
    assert hasattr(User, "department")
    assert hasattr(User, "designation")
    assert hasattr(User, "manager")
    assert hasattr(User, "direct_reports")

    # Reverse relationships on other models
    assert hasattr(Company, "users")
    assert hasattr(Department, "users")
    assert hasattr(Designation, "users")

    user_rel_company = User.company.property
    assert user_rel_company.back_populates == "users"

    user_rel_manager = User.manager.property
    assert user_rel_manager.back_populates == "direct_reports"

    user_rel_reports = User.direct_reports.property
    assert user_rel_reports.back_populates == "manager"


def test_user_create_normalization_and_validation() -> None:
    """Verify UserCreate schema normalizes emails, mobile numbers, names, and validates allowed values."""
    comp_id = uuid.uuid4()
    dept_id = uuid.uuid4()
    desig_id = uuid.uuid4()

    user_in = UserCreate(
        company_id=comp_id,
        department_id=dept_id,
        designation_id=desig_id,
        first_name="  Amit  ",
        middle_name="  Kumar  ",
        last_name="  Sharma  ",
        official_email="  Amit.Sharma@Gocompliances.in  ",
        personal_email="  amit.k@gmail.com  ",
        mobile_number=" 9876543210 ",
        date_of_joining=date(2026, 1, 15),
        employment_type="full_time",
        account_status="pending",
    )

    assert user_in.first_name == "Amit"
    assert user_in.middle_name == "Kumar"
    assert user_in.last_name == "Sharma"
    assert user_in.official_email == "amit.sharma@gocompliances.in"
    assert user_in.personal_email == "amit.k@gmail.com"
    assert user_in.mobile_number == "+919876543210"
    assert user_in.employment_type == "FULL_TIME"
    assert user_in.account_status == "PENDING"


def test_user_create_rejects_employee_code() -> None:
    """Verify UserCreate strictly rejects extra employee_code field (server-generated only)."""
    comp_id = uuid.uuid4()
    dept_id = uuid.uuid4()
    desig_id = uuid.uuid4()

    with pytest.raises(ValidationError) as exc_info:
        UserCreate(
            company_id=comp_id,
            department_id=dept_id,
            designation_id=desig_id,
            first_name="Amit",
            last_name="Sharma",
            official_email="amit@gocompliances.in",
            mobile_number="9876543210",
            date_of_joining=date(2026, 1, 15),
            employment_type="FULL_TIME",
            employee_code="CG0001",  # Extra forbidden field
        )
    assert "Extra inputs are not permitted" in str(exc_info.value)


def test_user_schema_invalid_email_and_mobile() -> None:
    """Verify invalid email format and invalid mobile numbers are rejected."""
    comp_id = uuid.uuid4()
    dept_id = uuid.uuid4()
    desig_id = uuid.uuid4()

    # Invalid official email
    with pytest.raises(ValidationError) as exc_info:
        UserCreate(
            company_id=comp_id,
            department_id=dept_id,
            designation_id=desig_id,
            first_name="Amit",
            last_name="Sharma",
            official_email="not-an-email",
            mobile_number="9876543210",
            date_of_joining=date(2026, 1, 15),
            employment_type="FULL_TIME",
        )
    assert "official_email must be a valid email address" in str(exc_info.value)

    # Invalid mobile (too short / wrong starting digit)
    with pytest.raises(ValidationError) as exc_info:
        UserCreate(
            company_id=comp_id,
            department_id=dept_id,
            designation_id=desig_id,
            first_name="Amit",
            last_name="Sharma",
            official_email="amit@gocompliances.in",
            mobile_number="12345",
            date_of_joining=date(2026, 1, 15),
            employment_type="FULL_TIME",
        )
    assert "mobile_number must be a valid 10-digit Indian mobile number" in str(exc_info.value)


def test_user_schema_invalid_employment_type_and_status() -> None:
    """Verify invalid employment types and account statuses are rejected."""
    comp_id = uuid.uuid4()
    dept_id = uuid.uuid4()
    desig_id = uuid.uuid4()

    with pytest.raises(ValidationError) as exc_info:
        UserCreate(
            company_id=comp_id,
            department_id=dept_id,
            designation_id=desig_id,
            first_name="Amit",
            last_name="Sharma",
            official_email="amit@gocompliances.in",
            mobile_number="9876543210",
            date_of_joining=date(2026, 1, 15),
            employment_type="FREELANCE",  # Invalid
        )
    assert "employment_type must be one of" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        UserCreate(
            company_id=comp_id,
            department_id=dept_id,
            designation_id=desig_id,
            first_name="Amit",
            last_name="Sharma",
            official_email="amit@gocompliances.in",
            mobile_number="9876543210",
            date_of_joining=date(2026, 1, 15),
            employment_type="FULL_TIME",
            account_status="DELETED",  # Invalid
        )
    assert "account_status must be one of" in str(exc_info.value)


def test_user_update_schema() -> None:
    """Verify partial updates in UserUpdate schema."""
    update = UserUpdate(
        first_name="  Vikram  ",
        official_email="  Vikram@Gocompliances.in ",
        employment_type="contract",
        account_status="active",
    )
    assert update.first_name == "Vikram"
    assert update.official_email == "vikram@gocompliances.in"
    assert update.employment_type == "CONTRACT"
    assert update.account_status == "ACTIVE"
    assert update.last_name is None


def test_user_read_schema_from_orm() -> None:
    """Verify UserRead schema serializes from ORM model."""
    uid = uuid.uuid4()
    cid = uuid.uuid4()
    dpid = uuid.uuid4()
    dsid = uuid.uuid4()
    now = datetime.now(timezone.utc)

    user_orm = User(
        user_id=uid,
        employee_code="CG0001",
        company_id=cid,
        department_id=dpid,
        designation_id=dsid,
        manager_user_id=None,
        first_name="Amit",
        middle_name=None,
        last_name="Sharma",
        official_email="amit@gocompliances.in",
        personal_email="amit@gmail.com",
        mobile_number="+919876543210",
        date_of_joining=date(2026, 1, 15),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        created_at=now,
        updated_at=now,
    )

    read_schema = UserRead.model_validate(user_orm)
    assert read_schema.user_id == uid
    assert read_schema.employee_code == "CG0001"
    assert read_schema.first_name == "Amit"
    assert read_schema.official_email == "amit@gocompliances.in"
    assert read_schema.account_status == "ACTIVE"


def test_user_migration_creates_only_user_master() -> None:
    """Verify that the Stage 7A migration touches only user_master table."""
    from pathlib import Path
    from alembic.config import Config
    from alembic.script import ScriptDirectory

    backend_dir = Path(__file__).resolve().parent.parent
    ini_path = backend_dir / "alembic.ini"
    cfg = Config(str(ini_path))
    cfg.set_main_option("script_location", str(backend_dir / "alembic"))

    script_dir = ScriptDirectory.from_config(cfg)
    revisions = list(script_dir.walk_revisions())

    user_rev = next((r for r in revisions if "create_user_master" in (r.doc or "")), None)
    assert user_rev is not None, "create_user_master revision must exist"

    # Verify down_revision is Stage 6 revision (create_designation_master)
    desig_rev = next((r for r in revisions if "create_designation_master" in (r.doc or "")), None)
    assert user_rev.down_revision == desig_rev.revision

    migration_file = Path(user_rev.path)
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

    assert created_tables == ["user_master"]
    assert dropped_tables == ["user_master"]

