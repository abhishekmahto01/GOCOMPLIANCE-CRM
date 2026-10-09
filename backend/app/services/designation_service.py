"""Designation domain service and repository logic."""
import uuid
from typing import List, Optional
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.designation import Designation
from app.models.user import User
from app.schemas.designation import DesignationCreate, DesignationUpdate


def list_designations(
    session: Session,
    company_id: Optional[uuid.UUID] = None,
    search: Optional[str] = None,
    status_filter: Optional[str] = None,
) -> List[Designation]:
    """Retrieve all global designations with optional search and status filtering.

    Args:
        session: Active SQLAlchemy session.
        company_id: Ignored parameter for backwards compatibility (designations are global).
        search: Optional search term for code, name, or description.
        status_filter: Optional status ('ACTIVE' or 'INACTIVE').

    Returns:
        List of Designation instances.
    """
    stmt = select(Designation)

    if status_filter and status_filter.strip().upper() in {"ACTIVE", "INACTIVE"}:
        stmt = stmt.where(Designation.status == status_filter.strip().upper())

    if search and search.strip():
        term = f"%{search.strip()}%"
        stmt = stmt.where(
            or_(
                Designation.designation_code.ilike(term),
                Designation.designation_name.ilike(term),
                Designation.description.ilike(term),
            )
        )

    stmt = stmt.order_by(Designation.level_rank.asc(), Designation.designation_name.asc())
    return list(session.execute(stmt).scalars().all())


def get_designation_by_id(session: Session, designation_id: uuid.UUID) -> Optional[Designation]:
    """Retrieve a single designation by UUID primary key."""
    stmt = select(Designation).where(Designation.designation_id == designation_id)
    return session.execute(stmt).scalar_one_or_none()


def create_designation(session: Session, desig_in: DesignationCreate) -> Designation:
    """Create a new global designation record ensuring global uniqueness.

    Args:
        session: Active SQLAlchemy session.
        desig_in: Validated DesignationCreate schema payload.

    Returns:
        The newly created Designation instance.

    Raises:
        ValueError: If designation code or name already exists globally.
    """
    norm_code = desig_in.designation_code.strip().upper()
    norm_name = desig_in.designation_name.strip()

    # 1. Uniqueness check for designation_code globally
    existing_code = session.execute(
        select(Designation.designation_id).where(
            func.upper(Designation.designation_code) == norm_code,
        )
    ).scalar_one_or_none()
    if existing_code:
        raise ValueError(f"Designation code '{norm_code}' is already registered.")

    # 2. Uniqueness check for designation_name globally
    existing_name = session.execute(
        select(Designation.designation_id).where(
            func.lower(Designation.designation_name) == norm_name.lower(),
        )
    ).scalar_one_or_none()
    if existing_name:
        raise ValueError(f"Designation title '{norm_name}' is already registered.")

    new_desig = Designation(
        designation_id=uuid.uuid4(),
        designation_code=norm_code,
        designation_name=norm_name,
        level_rank=desig_in.level_rank,
        is_managerial=desig_in.is_managerial,
        description=desig_in.description.strip() if desig_in.description else None,
        status=desig_in.status or "ACTIVE",
    )

    session.add(new_desig)
    session.commit()
    session.refresh(new_desig)
    return new_desig


def update_designation(
    session: Session,
    target_desig: Designation,
    update_in: DesignationUpdate,
) -> Designation:
    """Update an existing designation record with conflict checking.

    Args:
        session: Active SQLAlchemy session.
        target_desig: The existing Designation entity to update.
        update_in: Validated DesignationUpdate schema payload.

    Returns:
        The updated Designation instance.

    Raises:
        ValueError: If updated designation_name collides with another designation globally.
    """
    if update_in.designation_name is not None:
        norm_name = update_in.designation_name.strip()
        existing = session.execute(
            select(Designation.designation_id).where(
                func.lower(Designation.designation_name) == norm_name.lower(),
                Designation.designation_id != target_desig.designation_id,
            )
        ).scalar_one_or_none()
        if existing:
            raise ValueError(f"Designation title '{norm_name}' is already in use by another designation.")
        target_desig.designation_name = norm_name

    if update_in.level_rank is not None:
        target_desig.level_rank = update_in.level_rank

    if update_in.is_managerial is not None:
        target_desig.is_managerial = update_in.is_managerial

    if update_in.description is not None:
        target_desig.description = update_in.description.strip() if update_in.description else None

    if update_in.status is not None:
        norm_status = update_in.status.strip().upper()
        if norm_status in {"ACTIVE", "INACTIVE"}:
            target_desig.status = norm_status

    session.add(target_desig)
    session.commit()
    session.refresh(target_desig)
    return target_desig


def delete_designation(session: Session, target_desig: Designation) -> None:
    """Delete a designation if no employees are assigned to it.

    Args:
        session: Active SQLAlchemy session.
        target_desig: Designation instance to delete.

    Raises:
        ValueError: If one or more active employees are assigned to this designation.
    """
    assigned_count = session.execute(
        select(func.count(User.user_id)).where(User.designation_id == target_desig.designation_id)
    ).scalar_one()

    if assigned_count > 0:
        raise ValueError(
            f"Cannot delete designation '{target_desig.designation_name}' because {assigned_count} "
            f"employee(s) are assigned to it. Please deactivate the designation instead."
        )

    session.delete(target_desig)
    session.commit()
