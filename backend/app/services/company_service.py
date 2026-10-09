"""Company domain service and repository logic."""
import re
import uuid
from typing import List, Optional
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.company import Company
from app.schemas.company import CompanyCreate, CompanyUpdate


def list_companies(
    session: Session,
    search: Optional[str] = None,
    status_filter: Optional[str] = None,
) -> List[Company]:
    """Retrieve all companies with optional search and status filtering.

    Args:
        session: Active SQLAlchemy session.
        search: Optional search term for code, name, legal name, or prefix.
        status_filter: Optional status ('ACTIVE' or 'INACTIVE').

    Returns:
        List of Company instances ordered by company_name ASC.
    """
    stmt = select(Company)

    if status_filter and status_filter.strip().upper() in {"ACTIVE", "INACTIVE"}:
        stmt = stmt.where(Company.status == status_filter.strip().upper())

    if search and search.strip():
        term = f"%{search.strip()}%"
        stmt = stmt.where(
            or_(
                Company.company_code.ilike(term),
                Company.company_name.ilike(term),
                Company.legal_name.ilike(term),
                Company.employee_code_prefix.ilike(term),
            )
        )

    stmt = stmt.order_by(Company.company_name.asc())
    return list(session.execute(stmt).scalars().all())


def get_company_by_id(session: Session, company_id: uuid.UUID) -> Optional[Company]:
    """Retrieve a single company by UUID primary key."""
    stmt = select(Company).where(Company.company_id == company_id)
    return session.execute(stmt).scalar_one_or_none()


def create_company(session: Session, company_in: CompanyCreate) -> Company:
    """Create a new company record ensuring uniqueness of code, name, and prefix.

    Args:
        session: Active SQLAlchemy session.
        company_in: Validated CompanyCreate schema payload.

    Returns:
        The newly created Company instance.

    Raises:
        ValueError: If company code, name, or employee code prefix already exists.
    """
    norm_code = company_in.company_code.strip().upper()
    norm_name = company_in.company_name.strip()
    norm_prefix = company_in.employee_code_prefix.strip().upper()

    # 1. Uniqueness check for company_code
    existing_code = session.execute(
        select(Company.company_id).where(func.upper(Company.company_code) == norm_code)
    ).scalar_one_or_none()
    if existing_code:
        raise ValueError(f"Company code '{norm_code}' is already registered.")

    # 2. Uniqueness check for company_name
    existing_name = session.execute(
        select(Company.company_id).where(func.lower(Company.company_name) == norm_name.lower())
    ).scalar_one_or_none()
    if existing_name:
        raise ValueError(f"Company name '{norm_name}' is already registered.")

    # 3. Uniqueness check for employee_code_prefix
    existing_prefix = session.execute(
        select(Company.company_id).where(func.upper(Company.employee_code_prefix) == norm_prefix)
    ).scalar_one_or_none()
    if existing_prefix:
        raise ValueError(f"Employee code prefix '{norm_prefix}' is already in use by another company.")

    new_company = Company(
        company_id=uuid.uuid4(),
        company_code=norm_code,
        company_name=norm_name,
        legal_name=company_in.legal_name.strip() if company_in.legal_name else None,
        employee_code_prefix=norm_prefix,
        next_employee_number=company_in.next_employee_number or 1,
        status=company_in.status or "ACTIVE",
    )

    try:
        session.add(new_company)
        session.flush()
        session.commit()
        session.refresh(new_company)
        return new_company
    except Exception:
        session.rollback()
        raise


def update_company(
    session: Session,
    target_company: Company,
    update_data: CompanyUpdate,
) -> Company:
    """Update an existing company's display name, legal name, employee code prefix, or operational status.

    Args:
        session: Active SQLAlchemy session.
        target_company: Company model instance to update.
        update_data: CompanyUpdate schema payload.

    Returns:
        The refreshed Company instance.

    Raises:
        ValueError: If company name or employee code prefix conflicts with another company.
    """
    from app.models.user import User

    try:
        if update_data.company_name is not None:
            norm_name = update_data.company_name.strip()
            if norm_name.lower() != target_company.company_name.lower():
                existing = session.execute(
                    select(Company.company_id).where(
                        func.lower(Company.company_name) == norm_name.lower(),
                        Company.company_id != target_company.company_id,
                    )
                ).scalar_one_or_none()
                if existing:
                    raise ValueError(f"Company name '{norm_name}' is already taken.")
                target_company.company_name = norm_name

        if update_data.employee_code_prefix is not None:
            norm_prefix = update_data.employee_code_prefix.strip().upper()
            if not re.match(r"^[A-Z]{2,5}$", norm_prefix):
                raise ValueError("employee_code_prefix must consist of 2 to 5 uppercase letters (A-Z).")
            if norm_prefix != target_company.employee_code_prefix:
                existing_prefix = session.execute(
                    select(Company.company_id).where(
                        func.upper(Company.employee_code_prefix) == norm_prefix,
                        Company.company_id != target_company.company_id,
                    )
                ).scalar_one_or_none()
                if existing_prefix:
                    raise ValueError(
                        f"Employee code prefix '{norm_prefix}' is already in use by another company."
                    )

                old_prefix = target_company.employee_code_prefix
                target_company.employee_code_prefix = norm_prefix

                # Migrate existing employees' codes to new prefix
                users = session.execute(
                    select(User).where(User.company_id == target_company.company_id)
                ).scalars().all()
                for u in users:
                    if u.employee_code and u.employee_code.startswith(old_prefix):
                        seq_suffix = u.employee_code[len(old_prefix):]
                        u.employee_code = f"{norm_prefix}{seq_suffix}"

        if "legal_name" in update_data.model_fields_set:
            target_company.legal_name = (
                update_data.legal_name.strip() if update_data.legal_name else None
            )

        if update_data.status is not None:
            norm_status = update_data.status.strip().upper()
            if norm_status not in {"ACTIVE", "INACTIVE"}:
                raise ValueError("Status must be either 'ACTIVE' or 'INACTIVE'.")
            target_company.status = norm_status

        session.flush()
        session.commit()
        session.refresh(target_company)
        return target_company
    except Exception:
        session.rollback()
        raise


def delete_company(session: Session, target_company: Company) -> None:
    """Delete a company record ensuring no dependent users, departments, or orders exist.

    Args:
        session: Active SQLAlchemy session.
        target_company: Company instance to delete.

    Raises:
        ValueError: If company has associated employees, departments, designations, or orders.
    """
    from app.models.user import User
    from app.models.department import Department
    from app.models.designation import Designation
    from app.models.sales_order import SalesOrder
    from app.models.client import ClientMaster
    from app.models.operation_application import OperationApplication

    # 1. Check for assigned employees / users
    user_count = session.execute(
        select(func.count(User.user_id)).where(User.company_id == target_company.company_id)
    ).scalar() or 0
    if user_count > 0:
        raise ValueError(
            f"Cannot delete company '{target_company.company_name}' because {user_count} employee(s) are assigned to it. Please reassign or remove employees first, or mark the company as INACTIVE."
        )

    # 2. Check for linked departments
    dept_count = session.execute(
        select(func.count(Department.department_id)).where(Department.company_id == target_company.company_id)
    ).scalar() or 0
    if dept_count > 0:
        raise ValueError(
            f"Cannot delete company '{target_company.company_name}' because {dept_count} department(s) are configured under it."
        )

    # 3. Check for linked designations
    desig_count = session.execute(
        select(func.count(Designation.designation_id)).where(Designation.company_id == target_company.company_id)
    ).scalar() or 0
    if desig_count > 0:
        raise ValueError(
            f"Cannot delete company '{target_company.company_name}' because {desig_count} designation(s) are configured under it."
        )

    # 4. Check for sales orders
    order_count = session.execute(
        select(func.count(SalesOrder.order_id)).where(SalesOrder.company_id == target_company.company_id)
    ).scalar() or 0
    if order_count > 0:
        raise ValueError(
            f"Cannot delete company '{target_company.company_name}' because {order_count} sales order(s) are linked to it."
        )

    # 5. Check for clients
    client_count = session.execute(
        select(func.count(ClientMaster.client_id)).where(ClientMaster.company_id == target_company.company_id)
    ).scalar() or 0
    if client_count > 0:
        raise ValueError(
            f"Cannot delete company '{target_company.company_name}' because {client_count} client(s) are linked to it."
        )

    # 6. Check for operations applications
    op_count = session.execute(
        select(func.count(OperationApplication.application_id)).where(OperationApplication.company_id == target_company.company_id)
    ).scalar() or 0
    if op_count > 0:
        raise ValueError(
            f"Cannot delete company '{target_company.company_name}' because {op_count} operations application(s) are linked to it."
        )

    try:
        session.delete(target_company)
        session.flush()
        session.commit()
    except Exception:
        session.rollback()
        raise

