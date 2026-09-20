"""User / Employee domain service and repository logic."""
import uuid
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.company import Company
from app.models.department import Department
from app.models.designation import Designation
from app.models.user import User
from app.schemas.user import UserCreate
from app.services.employee_code import generate_employee_code


def validate_user_cross_company_integrity(
    session: Session,
    company_id: uuid.UUID,
    department_id: uuid.UUID,
    designation_id: uuid.UUID,
    manager_user_id: Optional[uuid.UUID] = None,
    current_user_id: Optional[uuid.UUID] = None,
) -> None:
    """Validate cross-entity organizational integrity for an employee.

    Enforces business rules:
    1. Department must belong to the selected Company and be ACTIVE.
    2. Designation must belong to the selected Company and be ACTIVE.
    3. Reporting Manager (if provided) must belong to the same Company and cannot be the user themselves.

    Args:
        session: Active SQLAlchemy session.
        company_id: UUID of the company.
        department_id: UUID of the department.
        designation_id: UUID of the designation.
        manager_user_id: Optional UUID of the reporting manager.
        current_user_id: Optional UUID of the user being validated (for self-manager check).

    Raises:
        ValueError: If any integrity constraint is violated.
    """
    # 1. Validate Department
    dept = session.execute(
        select(Department).where(Department.department_id == department_id)
    ).scalar_one_or_none()

    if not dept:
        raise ValueError(f"Department with ID '{department_id}' not found")
    if dept.company_id != company_id:
        raise ValueError(
            f"Department '{dept.department_name}' ({dept.department_code}) does not belong to the selected company"
        )
    if dept.status != "ACTIVE":
        raise ValueError(f"Department '{dept.department_name}' is inactive")

    # 2. Validate Designation
    desig = session.execute(
        select(Designation).where(Designation.designation_id == designation_id)
    ).scalar_one_or_none()

    if not desig:
        raise ValueError(f"Designation with ID '{designation_id}' not found")
    if desig.company_id != company_id:
        raise ValueError(
            f"Designation '{desig.designation_name}' ({desig.designation_code}) does not belong to the selected company"
        )
    if desig.status != "ACTIVE":
        raise ValueError(f"Designation '{desig.designation_name}' is inactive")

    # 3. Validate Reporting Manager (if supplied)
    if manager_user_id is not None:
        if current_user_id and manager_user_id == current_user_id:
            raise ValueError("An employee cannot be their own reporting manager")

        manager = session.execute(
            select(User).where(User.user_id == manager_user_id)
        ).scalar_one_or_none()

        if not manager:
            raise ValueError(f"Reporting manager with ID '{manager_user_id}' not found")
        if manager.company_id != company_id:
            raise ValueError(
                f"Reporting manager '{manager.first_name} {manager.last_name}' does not belong to the selected company"
            )


def create_user(session: Session, user_in: UserCreate) -> User:
    """Atomically validate, generate employee code, and create a new User record.

    Steps:
    1. Cross-company integrity validation (Department, Designation, Manager).
    2. Uniqueness check for official email (case-insensitive).
    3. Row-level locked employee code generation on Company.
    4. User record insertion.
    5. Atomic transaction commit.

    Args:
        session: Active SQLAlchemy session.
        user_in: Validated UserCreate schema.

    Returns:
        The newly created User model instance.

    Raises:
        ValueError: If cross-company validation fails or duplicate email exists.
    """
    try:
        # Step 1: Cross-company validation
        validate_user_cross_company_integrity(
            session=session,
            company_id=user_in.company_id,
            department_id=user_in.department_id,
            designation_id=user_in.designation_id,
            manager_user_id=user_in.manager_user_id,
        )

        # Step 2: Check official email uniqueness (case-insensitive)
        normalized_email = user_in.official_email.lower()
        existing_email = session.execute(
            select(User.user_id).where(
                func.lower(User.official_email) == normalized_email
            )
        ).scalar_one_or_none()

        if existing_email:
            raise ValueError(
                f"Official email '{user_in.official_email}' is already registered"
            )

        # Step 3: Lock company and generate employee code
        employee_code = generate_employee_code(
            session=session,
            company_id=user_in.company_id,
        )

        # Step 4: Create User ORM instance
        user = User(
            user_id=uuid.uuid4(),
            employee_code=employee_code,
            company_id=user_in.company_id,
            department_id=user_in.department_id,
            designation_id=user_in.designation_id,
            manager_user_id=user_in.manager_user_id,
            first_name=user_in.first_name,
            middle_name=user_in.middle_name,
            last_name=user_in.last_name,
            official_email=normalized_email,
            personal_email=user_in.personal_email.lower() if user_in.personal_email else None,
            mobile_number=user_in.mobile_number,
            date_of_joining=user_in.date_of_joining,
            employment_type=user_in.employment_type,
            account_status=user_in.account_status,
        )

        session.add(user)
        session.flush()
        session.commit()
        session.refresh(user)
        return user

    except Exception:
        session.rollback()
        raise
