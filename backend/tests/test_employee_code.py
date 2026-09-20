"""Tests for Employee Code generation, concurrency locking, and user creation services."""
import uuid
from datetime import date
from unittest.mock import MagicMock

import pytest
from sqlalchemy.orm import Session

from app.models.company import Company
from app.models.department import Department
from app.models.designation import Designation
from app.models.user import User
from app.schemas.user import UserCreate
from app.services.employee_code import generate_employee_code
from app.services.user_service import (
    create_user,
    validate_user_cross_company_integrity,
)


def test_employee_code_formatting_and_padding() -> None:
    """Verify employee code formatting with 4-digit padding and prefix."""
    mock_session = MagicMock(spec=Session)

    # Test CG0001
    comp_cg = Company(
        company_id=uuid.uuid4(),
        company_code="GOCOMPLIANCES",
        company_name="Gocompliances",
        employee_code_prefix="CG",
        next_employee_number=1,
        status="ACTIVE",
    )
    mock_session.execute.return_value.scalar_one_or_none.return_value = comp_cg

    code = generate_employee_code(mock_session, comp_cg.company_id)
    assert code == "CG0001"
    assert comp_cg.next_employee_number == 2

    # Test EP0042
    comp_ep = Company(
        company_id=uuid.uuid4(),
        company_code="ENTERPERNERSHIP",
        company_name="Enterpernership",
        employee_code_prefix="EP",
        next_employee_number=42,
        status="ACTIVE",
    )
    mock_session.execute.return_value.scalar_one_or_none.return_value = comp_ep

    code = generate_employee_code(mock_session, comp_ep.company_id)
    assert code == "EP0042"
    assert comp_ep.next_employee_number == 43

    # Test BM0999
    comp_bm = Company(
        company_id=uuid.uuid4(),
        company_code="BRANDMINGO",
        company_name="Brandmingo",
        employee_code_prefix="BM",
        next_employee_number=999,
        status="ACTIVE",
    )
    mock_session.execute.return_value.scalar_one_or_none.return_value = comp_bm

    code = generate_employee_code(mock_session, comp_bm.company_id)
    assert code == "BM0999"
    assert comp_bm.next_employee_number == 1000


def test_employee_code_numbers_above_9999() -> None:
    """Verify employee code formatting for counters exceeding 9999."""
    mock_session = MagicMock(spec=Session)

    comp = Company(
        company_id=uuid.uuid4(),
        company_code="GOCOMPLIANCES",
        company_name="Gocompliances",
        employee_code_prefix="CG",
        next_employee_number=10000,
        status="ACTIVE",
    )
    mock_session.execute.return_value.scalar_one_or_none.return_value = comp

    code = generate_employee_code(mock_session, comp.company_id)
    assert code == "CG10000"
    assert comp.next_employee_number == 10001


def test_employee_code_inactive_or_missing_company() -> None:
    """Verify error raised when company is not found or is inactive."""
    mock_session = MagicMock(spec=Session)

    # Missing company
    mock_session.execute.return_value.scalar_one_or_none.return_value = None
    with pytest.raises(ValueError) as exc_info:
        generate_employee_code(mock_session, uuid.uuid4())
    assert "not found" in str(exc_info.value)

    # Inactive company
    comp_inactive = Company(
        company_id=uuid.uuid4(),
        company_code="INACTIVE_CO",
        company_name="Inactive Co",
        employee_code_prefix="IC",
        next_employee_number=1,
        status="INACTIVE",
    )
    mock_session.execute.return_value.scalar_one_or_none.return_value = comp_inactive
    with pytest.raises(ValueError) as exc_info:
        generate_employee_code(mock_session, comp_inactive.company_id)
    assert "inactive company" in str(exc_info.value)


def test_cross_company_validation_department_mismatch() -> None:
    """Verify department belonging to a different company is rejected."""
    mock_session = MagicMock(spec=Session)

    comp_id = uuid.uuid4()
    other_comp_id = uuid.uuid4()
    dept_id = uuid.uuid4()
    desig_id = uuid.uuid4()

    # Department belongs to other_comp_id
    dept = Department(
        department_id=dept_id,
        company_id=other_comp_id,
        department_code="SALES",
        department_name="Sales",
        status="ACTIVE",
    )
    mock_session.execute.return_value.scalar_one_or_none.return_value = dept

    with pytest.raises(ValueError) as exc_info:
        validate_user_cross_company_integrity(
            session=mock_session,
            company_id=comp_id,
            department_id=dept_id,
            designation_id=desig_id,
        )
    assert "does not belong to the selected company" in str(exc_info.value)


def test_cross_company_validation_designation_mismatch() -> None:
    """Verify designation belonging to a different company is rejected."""
    mock_session = MagicMock(spec=Session)

    comp_id = uuid.uuid4()
    other_comp_id = uuid.uuid4()
    dept_id = uuid.uuid4()
    desig_id = uuid.uuid4()

    dept = Department(
        department_id=dept_id,
        company_id=comp_id,
        department_code="SALES",
        department_name="Sales",
        status="ACTIVE",
    )
    desig = Designation(
        designation_id=desig_id,
        company_id=other_comp_id,
        designation_code="MANAGER",
        designation_name="Manager",
        level_rank=5,
        status="ACTIVE",
    )

    # First scalar_one_or_none returns dept, second returns desig
    mock_session.execute.return_value.scalar_one_or_none.side_effect = [dept, desig]

    with pytest.raises(ValueError) as exc_info:
        validate_user_cross_company_integrity(
            session=mock_session,
            company_id=comp_id,
            department_id=dept_id,
            designation_id=desig_id,
        )
    assert "Designation 'Manager' (MANAGER) does not belong to the selected company" in str(exc_info.value)


def test_cross_company_validation_manager_mismatch() -> None:
    """Verify manager belonging to a different company is rejected."""
    mock_session = MagicMock(spec=Session)

    comp_id = uuid.uuid4()
    other_comp_id = uuid.uuid4()
    dept_id = uuid.uuid4()
    desig_id = uuid.uuid4()
    manager_id = uuid.uuid4()

    dept = Department(
        department_id=dept_id,
        company_id=comp_id,
        department_code="SALES",
        department_name="Sales",
        status="ACTIVE",
    )
    desig = Designation(
        designation_id=desig_id,
        company_id=comp_id,
        designation_code="EXECUTIVE",
        designation_name="Executive",
        level_rank=1,
        status="ACTIVE",
    )
    manager = User(
        user_id=manager_id,
        employee_code="EP0001",
        company_id=other_comp_id,  # Different company!
        first_name="Rohan",
        last_name="Verma",
        official_email="rohan@enterpernership.in",
        mobile_number="+919876543210",
        date_of_joining=date(2025, 1, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
    )

    mock_session.execute.return_value.scalar_one_or_none.side_effect = [dept, desig, manager]

    with pytest.raises(ValueError) as exc_info:
        validate_user_cross_company_integrity(
            session=mock_session,
            company_id=comp_id,
            department_id=dept_id,
            designation_id=desig_id,
            manager_user_id=manager_id,
        )
    assert "Reporting manager 'Rohan Verma' does not belong to the selected company" in str(exc_info.value)


def test_cross_company_validation_self_manager() -> None:
    """Verify employee cannot be assigned as their own reporting manager."""
    mock_session = MagicMock(spec=Session)

    comp_id = uuid.uuid4()
    dept_id = uuid.uuid4()
    desig_id = uuid.uuid4()
    user_id = uuid.uuid4()

    dept = Department(
        department_id=dept_id,
        company_id=comp_id,
        department_code="SALES",
        department_name="Sales",
        status="ACTIVE",
    )
    desig = Designation(
        designation_id=desig_id,
        company_id=comp_id,
        designation_code="EXECUTIVE",
        designation_name="Executive",
        level_rank=1,
        status="ACTIVE",
    )

    mock_session.execute.return_value.scalar_one_or_none.side_effect = [dept, desig]

    with pytest.raises(ValueError) as exc_info:
        validate_user_cross_company_integrity(
            session=mock_session,
            company_id=comp_id,
            department_id=dept_id,
            designation_id=desig_id,
            manager_user_id=user_id,
            current_user_id=user_id,
        )
    assert "cannot be their own reporting manager" in str(exc_info.value)


def test_create_user_service_success_and_rollback_on_failure() -> None:
    """Verify atomic user creation and rollback on validation failure."""
    mock_session = MagicMock(spec=Session)

    comp_id = uuid.uuid4()
    dept_id = uuid.uuid4()
    desig_id = uuid.uuid4()

    dept = Department(
        department_id=dept_id,
        company_id=comp_id,
        department_code="SALES",
        department_name="Sales",
        status="ACTIVE",
    )
    desig = Designation(
        designation_id=desig_id,
        company_id=comp_id,
        designation_code="EXECUTIVE",
        designation_name="Executive",
        level_rank=1,
        status="ACTIVE",
    )
    comp = Company(
        company_id=comp_id,
        company_code="GOCOMPLIANCES",
        company_name="Gocompliances",
        employee_code_prefix="CG",
        next_employee_number=1,
        status="ACTIVE",
    )

    # 1. Successful creation
    # Calls to scalar_one_or_none: 1. dept, 2. desig, 3. email_check (None), 4. company for code
    mock_session.execute.return_value.scalar_one_or_none.side_effect = [
        dept,
        desig,
        None,
        comp,
    ]

    user_in = UserCreate(
        company_id=comp_id,
        department_id=dept_id,
        designation_id=desig_id,
        first_name="Amit",
        last_name="Sharma",
        official_email="amit@gocompliances.in",
        mobile_number="9876543210",
        date_of_joining=date(2026, 1, 15),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
    )

    user = create_user(mock_session, user_in)
    assert user.employee_code == "CG0001"
    assert user.official_email == "amit@gocompliances.in"
    assert mock_session.commit.call_count == 1

    # 2. Rollback when duplicate email is encountered
    mock_session.reset_mock()
    existing_user_id = uuid.uuid4()
    mock_session.execute.return_value.scalar_one_or_none.side_effect = [
        dept,
        desig,
        existing_user_id,  # Email already exists
    ]

    with pytest.raises(ValueError) as exc_info:
        create_user(mock_session, user_in)
    assert "already registered" in str(exc_info.value)
    assert mock_session.rollback.call_count == 1
    assert mock_session.commit.call_count == 0
