"""Admin lookup endpoints for dropdowns and selectors."""
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, require_module_permission
from app.database.session import get_db
from app.models.company import Company
from app.models.department import Department
from app.models.designation import Designation
from app.models.user import User
from app.schemas.lookup import (
    CompanyLookupRead,
    DepartmentLookupRead,
    DesignationLookupRead,
    ManagerLookupRead,
)
from app.services import permissions

router = APIRouter(prefix="/admin/lookup", tags=["Admin Lookups"])


@router.get(
    "/companies",
    response_model=List[CompanyLookupRead],
    status_code=status.HTTP_200_OK,
    summary="Lookup Companies",
    description="Retrieve active companies accessible within the current user's data scope for form dropdowns.",
    dependencies=[Depends(require_module_permission("ADMIN_EMPLOYEES", "view"))],
)
def lookup_companies(
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
) -> List[CompanyLookupRead]:
    """Return active companies, scoped by user's permission data scope."""
    scope_ctx = permissions.resolve_data_scope_context(session, current_user, "ADMIN_EMPLOYEES")
    
    stmt = select(Company).where(Company.status == "ACTIVE")
    if scope_ctx.scope in ("COMPANY", "DEPARTMENT", "TEAM", "SELF"):
        stmt = stmt.where(Company.company_id == current_user.company_id)
    
    stmt = stmt.order_by(Company.company_name.asc())
    companies = session.execute(stmt).scalars().all()
    return [CompanyLookupRead.model_validate(c) for c in companies]


@router.get(
    "/departments",
    response_model=List[DepartmentLookupRead],
    status_code=status.HTTP_200_OK,
    summary="Lookup Departments",
    description="Retrieve active departments, optionally filtered by company ID.",
    dependencies=[Depends(require_module_permission("ADMIN_EMPLOYEES", "view"))],
)
def lookup_departments(
    company_id: Optional[uuid.UUID] = Query(None, description="Filter departments by parent company"),
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
) -> List[DepartmentLookupRead]:
    """Return active departments belonging to the requested company."""
    scope_ctx = permissions.resolve_data_scope_context(session, current_user, "ADMIN_EMPLOYEES")
    
    stmt = select(Department).where(Department.status == "ACTIVE")
    
    if company_id:
        if scope_ctx.scope in ("COMPANY", "DEPARTMENT", "TEAM", "SELF") and company_id != current_user.company_id:
            return []
        stmt = stmt.where(Department.company_id == company_id)
    elif scope_ctx.scope in ("COMPANY", "DEPARTMENT", "TEAM", "SELF"):
        stmt = stmt.where(Department.company_id == current_user.company_id)
        
    stmt = stmt.order_by(Department.department_name.asc())
    departments = session.execute(stmt).scalars().all()
    return [DepartmentLookupRead.model_validate(d) for d in departments]


@router.get(
    "/designations",
    response_model=List[DesignationLookupRead],
    status_code=status.HTTP_200_OK,
    summary="Lookup Designations",
    description="Retrieve active designations, optionally filtered by company ID.",
    dependencies=[Depends(require_module_permission("ADMIN_EMPLOYEES", "view"))],
)
def lookup_designations(
    company_id: Optional[uuid.UUID] = Query(None, description="Filter designations by parent company"),
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
) -> List[DesignationLookupRead]:
    """Return active designations belonging to the requested company."""
    scope_ctx = permissions.resolve_data_scope_context(session, current_user, "ADMIN_EMPLOYEES")
    
    stmt = select(Designation).where(Designation.status == "ACTIVE")
    
    if company_id:
        if scope_ctx.scope in ("COMPANY", "DEPARTMENT", "TEAM", "SELF") and company_id != current_user.company_id:
            return []
        stmt = stmt.where(Designation.company_id == company_id)
    elif scope_ctx.scope in ("COMPANY", "DEPARTMENT", "TEAM", "SELF"):
        stmt = stmt.where(Designation.company_id == current_user.company_id)
        
    stmt = stmt.order_by(Designation.level_rank.desc(), Designation.designation_name.asc())
    designations = session.execute(stmt).scalars().all()
    return [DesignationLookupRead.model_validate(d) for d in designations]


@router.get(
    "/managers",
    response_model=List[ManagerLookupRead],
    status_code=status.HTTP_200_OK,
    summary="Lookup Reporting Managers",
    description="Retrieve active employees eligible to act as reporting managers for a company.",
    dependencies=[Depends(require_module_permission("ADMIN_EMPLOYEES", "view"))],
)
def lookup_managers(
    company_id: Optional[uuid.UUID] = Query(None, description="Filter managers by company ID"),
    exclude_user_id: Optional[uuid.UUID] = Query(None, description="Exclude a specific user (e.g. self)"),
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
) -> List[ManagerLookupRead]:
    """Return active employees who can be assigned as reporting manager."""
    scope_ctx = permissions.resolve_data_scope_context(session, current_user, "ADMIN_EMPLOYEES")
    
    stmt = (
        select(
            User.user_id,
            User.employee_code,
            User.first_name,
            User.middle_name,
            User.last_name,
            User.official_email,
            Department.department_name,
            Designation.designation_name,
        )
        .outerjoin(Department, User.department_id == Department.department_id)
        .outerjoin(Designation, User.designation_id == Designation.designation_id)
        .where(User.account_status == "ACTIVE")
    )
    
    if company_id:
        if scope_ctx.scope in ("COMPANY", "DEPARTMENT", "TEAM", "SELF") and company_id != current_user.company_id:
            return []
        stmt = stmt.where(User.company_id == company_id)
    elif scope_ctx.scope in ("COMPANY", "DEPARTMENT", "TEAM", "SELF"):
        stmt = stmt.where(User.company_id == current_user.company_id)
        
    if exclude_user_id:
        stmt = stmt.where(User.user_id != exclude_user_id)
        
    stmt = stmt.order_by(User.first_name.asc(), User.last_name.asc())
    rows = session.execute(stmt).all()
    
    return [
        ManagerLookupRead(
            user_id=row.user_id,
            employee_code=row.employee_code,
            first_name=row.first_name,
            middle_name=row.middle_name,
            last_name=row.last_name,
            official_email=row.official_email,
            department_name=row.department_name,
            designation_name=row.designation_name,
        )
        for row in rows
    ]
