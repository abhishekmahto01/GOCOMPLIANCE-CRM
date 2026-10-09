"""Department domain service and repository logic."""
import uuid
from typing import List, Optional
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.department import Department
from app.models.user import User
from app.schemas.department import DepartmentCreate, DepartmentUpdate


def list_departments(
    session: Session,
    company_id: Optional[uuid.UUID] = None,
    search: Optional[str] = None,
    status_filter: Optional[str] = None,
) -> List[Department]:
    """Retrieve all global departments with optional search and status filtering.

    Args:
        session: Active SQLAlchemy session.
        company_id: Ignored parameter for backwards compatibility (departments are global).
        search: Optional search term for code or name.
        status_filter: Optional status ('ACTIVE' or 'INACTIVE').

    Returns:
        List of Department instances.
    """
    stmt = select(Department)

    if status_filter and status_filter.strip().upper() in {"ACTIVE", "INACTIVE"}:
        stmt = stmt.where(Department.status == status_filter.strip().upper())

    if search and search.strip():
        term = f"%{search.strip()}%"
        stmt = stmt.where(
            or_(
                Department.department_code.ilike(term),
                Department.department_name.ilike(term),
                Department.description.ilike(term),
            )
        )

    stmt = stmt.order_by(Department.department_name.asc())
    return list(session.execute(stmt).scalars().all())


def get_department_by_id(session: Session, department_id: uuid.UUID) -> Optional[Department]:
    """Retrieve a single department by UUID primary key."""
    stmt = select(Department).where(Department.department_id == department_id)
    return session.execute(stmt).scalar_one_or_none()


def create_department(session: Session, dept_in: DepartmentCreate) -> Department:
    """Create a new global department record ensuring global uniqueness.

    Args:
        session: Active SQLAlchemy session.
        dept_in: Validated DepartmentCreate schema payload.

    Returns:
        The newly created Department instance.

    Raises:
        ValueError: If department code or name already exists globally.
    """
    norm_code = dept_in.department_code.strip().upper()
    norm_name = dept_in.department_name.strip()

    # 1. Uniqueness check for department_code globally
    existing_code = session.execute(
        select(Department.department_id).where(
            func.upper(Department.department_code) == norm_code,
        )
    ).scalar_one_or_none()
    if existing_code:
        raise ValueError(f"Department code '{norm_code}' is already registered.")

    # 2. Uniqueness check for department_name globally
    existing_name = session.execute(
        select(Department.department_id).where(
            func.lower(Department.department_name) == norm_name.lower(),
        )
    ).scalar_one_or_none()
    if existing_name:
        raise ValueError(f"Department name '{norm_name}' is already registered.")

    new_dept = Department(
        department_id=uuid.uuid4(),
        department_code=norm_code,
        department_name=norm_name,
        description=dept_in.description.strip() if dept_in.description else None,
        status=dept_in.status or "ACTIVE",
    )

    session.add(new_dept)
    session.commit()
    session.refresh(new_dept)
    return new_dept


def update_department(
    session: Session,
    target_dept: Department,
    update_in: DepartmentUpdate,
) -> Department:
    """Update an existing department record with conflict checking.

    Args:
        session: Active SQLAlchemy session.
        target_dept: The existing Department entity to update.
        update_in: Validated DepartmentUpdate schema payload.

    Returns:
        The updated Department instance.

    Raises:
        ValueError: If updated department_name collides with another department globally.
    """
    if update_in.department_name is not None:
        norm_name = update_in.department_name.strip()
        existing = session.execute(
            select(Department.department_id).where(
                func.lower(Department.department_name) == norm_name.lower(),
                Department.department_id != target_dept.department_id,
            )
        ).scalar_one_or_none()
        if existing:
            raise ValueError(f"Department name '{norm_name}' is already in use by another department.")
        target_dept.department_name = norm_name

    if update_in.description is not None:
        target_dept.description = update_in.description.strip() if update_in.description else None

    if update_in.status is not None:
        norm_status = update_in.status.strip().upper()
        if norm_status in {"ACTIVE", "INACTIVE"}:
            target_dept.status = norm_status

    session.add(target_dept)
    session.commit()
    session.refresh(target_dept)
    return target_dept


def delete_department(session: Session, target_dept: Department) -> None:
    """Delete a department if no employees are assigned to it.

    Args:
        session: Active SQLAlchemy session.
        target_dept: Department instance to delete.

    Raises:
        ValueError: If one or more active employees are assigned to this department.
    """
    assigned_count = session.execute(
        select(func.count(User.user_id)).where(User.department_id == target_dept.department_id)
    ).scalar_one()

    if assigned_count > 0:
        raise ValueError(
            f"Cannot delete department '{target_dept.department_name}' because {assigned_count} "
            f"employee(s) are assigned to it. Please deactivate the department instead."
        )

    session.delete(target_dept)
    session.commit()
