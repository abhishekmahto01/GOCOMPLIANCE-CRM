"""User / Employee domain service and repository logic."""
from datetime import datetime, timezone
import math
import uuid
from typing import List, Optional, Tuple

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.core.config import settings
from app.core.security import hash_password
from app.models.company import Company
from app.models.department import Department
from app.models.designation import Designation
from app.models.user import User
from app.schemas.user import (
    ALLOWED_ACCOUNT_STATUSES,
    EmployeeRead,
    TrialLoginInitializeResponse,
    UserCreate,
    UserUpdate,
)
from app.services.employee_code import generate_employee_code
from app.services.permissions import DataScopeContext, get_team_user_ids


def compute_login_status(user: User) -> str:
    """Derive human-readable login credential status badge."""
    if user.account_status in {"INACTIVE", "SUSPENDED"}:
        return "Disabled"
    if not user.password_hash:
        return "Not Initialized"
    if user.must_change_password:
        return "Password Change Required"
    return "Active Login"


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
        if manager.account_status != "ACTIVE":
            raise ValueError(f"Reporting manager '{manager.first_name} {manager.last_name}' is not in ACTIVE status")


def create_user(session: Session, user_in: UserCreate) -> User:
    """Atomically validate, generate employee code, and create a new User record.

    If trial password mode is enabled in configuration, provisions hashed initial password.

    Steps:
    1. Cross-company integrity validation (Department, Designation, Manager).
    2. Uniqueness check for official email (case-insensitive).
    3. Row-level locked employee code generation on Company.
    4. Optional trial password hashing if trial mode is enabled.
    5. User record insertion.
    6. Atomic transaction commit.

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

        # Step 4: Handle trial credentials provisioning
        trial_password = settings.get_effective_trial_password()
        password_hash = None
        credentials_initialized_at = None
        must_change_password = True
        if trial_password:
            password_hash = hash_password(trial_password)
            credentials_initialized_at = datetime.now(timezone.utc)
            must_change_password = True

        # Step 5: Create User ORM instance
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
            password_hash=password_hash,
            must_change_password=must_change_password,
            credentials_initialized_at=credentials_initialized_at,
        )

        session.add(user)
        session.flush()
        session.commit()
        session.refresh(user)
        return user

    except Exception:
        session.rollback()
        raise


def get_employee_by_id(session: Session, user_id: uuid.UUID) -> Optional[User]:
    """Retrieve an employee by primary key user_id with eager joinedload of related entities."""
    stmt = (
        select(User)
        .options(
            joinedload(User.company),
            joinedload(User.department),
            joinedload(User.designation),
            joinedload(User.manager),
        )
        .where(User.user_id == user_id)
    )
    return session.execute(stmt).unique().scalar_one_or_none()


def serialize_employee_read(user: User) -> EmployeeRead:
    """Convert an ORM User model into an EmployeeRead schema with relation labels and credential statuses."""
    manager_name = None
    manager_code = None
    if user.manager:
        manager_name = f"{user.manager.first_name} {user.manager.last_name}".strip()
        manager_code = user.manager.employee_code

    return EmployeeRead(
        user_id=user.user_id,
        employee_code=user.employee_code,
        company_id=user.company_id,
        company_name=user.company.company_name if user.company else None,
        company_code=user.company.company_code if user.company else None,
        department_id=user.department_id,
        department_name=user.department.department_name if user.department else None,
        department_code=user.department.department_code if user.department else None,
        designation_id=user.designation_id,
        designation_name=user.designation.designation_name if user.designation else None,
        designation_code=user.designation.designation_code if user.designation else None,
        manager_user_id=user.manager_user_id,
        manager_name=manager_name,
        manager_employee_code=manager_code,
        first_name=user.first_name,
        middle_name=user.middle_name,
        last_name=user.last_name,
        official_email=user.official_email,
        personal_email=user.personal_email,
        mobile_number=user.mobile_number,
        date_of_joining=user.date_of_joining,
        employment_type=user.employment_type,
        account_status=user.account_status,
        credentials_initialized=bool(user.password_hash is not None),
        must_change_password=bool(user.must_change_password),
        login_status=compute_login_status(user),
        credentials_initialized_at=user.credentials_initialized_at,
        password_changed_at=user.password_changed_at,
        created_at=user.created_at or datetime.now(timezone.utc),
        updated_at=user.updated_at or datetime.now(timezone.utc),
    )


def initialize_trial_login(
    session: Session,
    user_id: uuid.UUID,
    current_user: User,
    scope_context: DataScopeContext,
) -> TrialLoginInitializeResponse:
    """Initialize trial login credentials for an uninitialized employee.

    Requirements:
    1. Trial mode must be enabled and not in production.
    2. Target employee must exist and be within the caller's data scope.
    3. Target employee must be in ACTIVE account_status.
    4. Target employee must not already have a password.
    5. Hash configured trial password and set must_change_password = True.
    6. Record credentials_initialized_at timestamp.
    7. Commit transaction and return safe TrialLoginInitializeResponse.
    """
    trial_password = settings.get_effective_trial_password()
    if not trial_password:
        raise ValueError(
            "Trial password provisioning is currently disabled or not configured in environment settings."
        )

    target_user = get_employee_by_id(session, user_id)
    if not target_user:
        raise ValueError(f"Employee with ID '{user_id}' not found")

    if not scope_context.is_user_permitted(
        target_user.user_id, target_user.company_id, target_user.department_id
    ):
        raise PermissionError("Access denied. Employee is outside your authorized data scope.")

    if target_user.account_status != "ACTIVE":
        raise ValueError(
            f"Cannot initialize login credentials for employee with '{target_user.account_status}' status. Employee must be ACTIVE."
        )

    if target_user.password_hash is not None:
        raise ValueError(
            f"Login credentials are already initialized for employee '{target_user.employee_code}'."
        )

    now = datetime.now(timezone.utc)
    target_user.password_hash = hash_password(trial_password)
    target_user.must_change_password = True
    target_user.credentials_initialized_at = now

    session.flush()
    session.commit()
    session.refresh(target_user)

    return TrialLoginInitializeResponse(
        user_id=target_user.user_id,
        employee_code=target_user.employee_code,
        official_email=target_user.official_email,
        credentials_initialized=True,
        must_change_password=True,
        login_status="Password Change Required",
        credentials_initialized_at=target_user.credentials_initialized_at,
        message="Trial login credentials have been initialized. The employee must change the temporary password on first login.",
    )



def list_employees(
    session: Session,
    current_user: User,
    scope_context: DataScopeContext,
    page: int = 1,
    page_size: int = 20,
    search: Optional[str] = None,
    company_id: Optional[uuid.UUID] = None,
    department_id: Optional[uuid.UUID] = None,
    designation_id: Optional[uuid.UUID] = None,
    manager_user_id: Optional[uuid.UUID] = None,
    account_status: Optional[str] = None,
) -> Tuple[List[User], int, int]:
    """Retrieve paginated employees enforcing server-side data scoping and optional filters.

    Args:
        session: Active SQLAlchemy session.
        current_user: Authenticated caller User instance.
        scope_context: Evaluated DataScopeContext for ADMIN_EMPLOYEES module.
        page: 1-indexed page number.
        page_size: Page size limit.
        search: Optional search term (employee_code, name, email).
        company_id: Optional filter for company.
        department_id: Optional filter for department.
        designation_id: Optional filter for designation.
        manager_user_id: Optional filter for reporting manager.
        account_status: Optional filter for account status.

    Returns:
        Tuple of (items, total_count, total_pages).
    """
    base_query = select(User)

    # 1. Apply Server-Side Data Scope
    if scope_context.scope == "SELF":
        base_query = base_query.where(User.user_id == current_user.user_id)
    elif scope_context.scope == "TEAM":
        base_query = base_query.where(User.user_id.in_(scope_context.team_user_ids))
    elif scope_context.scope == "DEPARTMENT":
        base_query = base_query.where(
            User.company_id == current_user.company_id,
            User.department_id == current_user.department_id,
        )
    elif scope_context.scope == "COMPANY":
        base_query = base_query.where(User.company_id == current_user.company_id)
    elif scope_context.scope == "ALL":
        pass  # No scope restriction

    # 2. Apply User-Specified Filters
    if company_id:
        base_query = base_query.where(User.company_id == company_id)
    if department_id:
        base_query = base_query.where(User.department_id == department_id)
    if designation_id:
        base_query = base_query.where(User.designation_id == designation_id)
    if manager_user_id:
        base_query = base_query.where(User.manager_user_id == manager_user_id)
    if account_status:
        base_query = base_query.where(User.account_status == account_status.strip().upper())

    # 3. Apply Search Filter
    if search and search.strip():
        term = f"%{search.strip()}%"
        full_name = func.concat(User.first_name, " ", User.last_name)
        base_query = base_query.where(
            or_(
                User.employee_code.ilike(term),
                User.official_email.ilike(term),
                User.first_name.ilike(term),
                User.last_name.ilike(term),
                full_name.ilike(term),
            )
        )

    # 4. Count total matching records
    count_query = select(func.count()).select_from(base_query.subquery())
    total = session.execute(count_query).scalar_one()

    # 5. Apply pagination & eager loading with deterministic ordering
    offset = (page - 1) * page_size
    query = (
        base_query.options(
            joinedload(User.company),
            joinedload(User.department),
            joinedload(User.designation),
            joinedload(User.manager),
        )
        .order_by(User.created_at.desc(), User.employee_code.asc())
        .offset(offset)
        .limit(page_size)
    )

    items = list(session.execute(query).unique().scalars().all())
    pages = math.ceil(total / page_size) if total > 0 else 0

    return items, total, pages


def update_employee(
    session: Session,
    target_user: User,
    update_data: UserUpdate,
) -> User:
    """Partially update an existing employee record with validation and hierarchy cycle prevention.

    Args:
        session: Active SQLAlchemy session.
        target_user: User instance to update.
        update_data: UserUpdate schema payload.

    Returns:
        The refreshed User instance.

    Raises:
        ValueError: For validation failures (duplicate email, circular hierarchy, cross-company mismatch).
    """
    try:
        # Check company immutability
        if update_data.company_id is not None and update_data.company_id != target_user.company_id:
            raise ValueError("Company cannot be modified for an existing employee")

        # Check official email uniqueness if changed
        if update_data.official_email is not None:
            norm_email = update_data.official_email.lower()
            if norm_email != target_user.official_email.lower():
                existing = session.execute(
                    select(User.user_id).where(
                        func.lower(User.official_email) == norm_email,
                        User.user_id != target_user.user_id,
                    )
                ).scalar_one_or_none()
                if existing:
                    raise ValueError(f"Official email '{update_data.official_email}' is already registered")
                target_user.official_email = norm_email

        # Determine if organization structure fields changed
        is_dept_changed = update_data.department_id is not None and update_data.department_id != target_user.department_id
        is_desig_changed = update_data.designation_id is not None and update_data.designation_id != target_user.designation_id
        is_mgr_changed = "manager_user_id" in update_data.model_fields_set and update_data.manager_user_id != target_user.manager_user_id

        if is_dept_changed or is_desig_changed or is_mgr_changed:
            effective_dept_id = update_data.department_id or target_user.department_id
            effective_desig_id = update_data.designation_id or target_user.designation_id
            new_manager_id = target_user.manager_user_id
            if "manager_user_id" in update_data.model_fields_set:
                new_manager_id = update_data.manager_user_id

            # Validate cross-company integrity
            validate_user_cross_company_integrity(
                session=session,
                company_id=target_user.company_id,
                department_id=effective_dept_id,
                designation_id=effective_desig_id,
                manager_user_id=new_manager_id,
                current_user_id=target_user.user_id,
            )

            # Check circular hierarchy if manager is changed
            if new_manager_id is not None and new_manager_id != target_user.manager_user_id:
                if new_manager_id == target_user.user_id:
                    raise ValueError("An employee cannot be their own reporting manager")
                subordinates = get_team_user_ids(session, target_user.user_id)
                if new_manager_id in subordinates:
                    raise ValueError(
                        "Circular reporting hierarchy detected: the selected manager reports to this employee"
                    )

        # Apply updates
        if update_data.department_id is not None:
            target_user.department_id = update_data.department_id
        if update_data.designation_id is not None:
            target_user.designation_id = update_data.designation_id
        if "manager_user_id" in update_data.model_fields_set:
            target_user.manager_user_id = update_data.manager_user_id
        if update_data.first_name is not None:
            target_user.first_name = update_data.first_name
        if "middle_name" in update_data.model_fields_set:
            target_user.middle_name = update_data.middle_name
        if update_data.last_name is not None:
            target_user.last_name = update_data.last_name
        if "personal_email" in update_data.model_fields_set:
            target_user.personal_email = update_data.personal_email.lower() if update_data.personal_email else None
        if update_data.mobile_number is not None:
            target_user.mobile_number = update_data.mobile_number
        if update_data.date_of_joining is not None:
            target_user.date_of_joining = update_data.date_of_joining
        if update_data.employment_type is not None:
            target_user.employment_type = update_data.employment_type

        session.flush()
        session.commit()
        session.refresh(target_user)
        return get_employee_by_id(session, target_user.user_id) or target_user

    except Exception:
        session.rollback()
        raise


def update_employee_status(
    session: Session,
    target_user: User,
    new_status: str,
) -> User:
    """Update employee account operational status.

    If status is changed to INACTIVE or SUSPENDED, increments token_version to invalidate active sessions.

    Args:
        session: Active SQLAlchemy session.
        target_user: User instance to update.
        new_status: Target status ('PENDING', 'ACTIVE', 'INACTIVE', 'SUSPENDED').

    Returns:
        The refreshed User instance.

    Raises:
        ValueError: If status is invalid.
    """
    status_norm = new_status.strip().upper()
    if status_norm not in ALLOWED_ACCOUNT_STATUSES:
        raise ValueError(
            f"Invalid account status '{new_status}'. Must be one of {sorted(ALLOWED_ACCOUNT_STATUSES)}"
        )

    try:
        # Invalidate active JWT sessions when transitioning away from ACTIVE
        if status_norm in {"INACTIVE", "SUSPENDED"} and target_user.account_status == "ACTIVE":
            target_user.token_version += 1

        target_user.account_status = status_norm
        session.flush()
        session.commit()
        session.refresh(target_user)
        return get_employee_by_id(session, target_user.user_id) or target_user

    except Exception:
        session.rollback()
        raise
