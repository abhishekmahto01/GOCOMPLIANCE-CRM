"""Employee Management API routes for Admin and authorized managers."""
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, require_module_permission
from app.database.session import get_db
from app.models.user import User
from app.schemas.user import (
    EmployeeRead,
    EmployeeStatusUpdate,
    PaginatedEmployeesResponse,
    UserCreate,
    UserUpdate,
)
from app.services import permissions, user_service

router = APIRouter(prefix="/admin/employees", tags=["Employee Management"])


@router.post(
    "",
    response_model=EmployeeRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create Employee",
    description="Create a new employee with an auto-generated, company-specific employee code.",
    dependencies=[Depends(require_module_permission("ADMIN_EMPLOYEES", "create"))],
)
def create_employee_endpoint(
    employee_in: UserCreate,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
) -> EmployeeRead:
    """Create a new employee in the CRM under the target company/department/designation."""
    try:
        user = user_service.create_user(session, employee_in)
        loaded = user_service.get_employee_by_id(session, user.user_id)
        return user_service.serialize_employee_read(loaded or user)
    except ValueError as exc:
        err_msg = str(exc)
        if "already registered" in err_msg:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=err_msg)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err_msg)


@router.get(
    "",
    response_model=PaginatedEmployeesResponse,
    status_code=status.HTTP_200_OK,
    summary="List Employees",
    description="List paginated employees with server-enforced data scope and optional filters.",
    dependencies=[Depends(require_module_permission("ADMIN_EMPLOYEES", "view"))],
)
def list_employees_endpoint(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page (max 100)"),
    search: Optional[str] = Query(None, description="Search by employee code, name, or official email"),
    company_id: Optional[uuid.UUID] = Query(None, description="Filter by company ID"),
    department_id: Optional[uuid.UUID] = Query(None, description="Filter by department ID"),
    designation_id: Optional[uuid.UUID] = Query(None, description="Filter by designation ID"),
    manager_user_id: Optional[uuid.UUID] = Query(None, description="Filter by reporting manager ID"),
    account_status: Optional[str] = Query(None, description="Filter by account status"),
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
) -> PaginatedEmployeesResponse:
    """Retrieve paginated employee records based on the authenticated user's effective data scope."""
    scope_ctx = permissions.resolve_data_scope_context(session, current_user, "ADMIN_EMPLOYEES")
    items, total, pages = user_service.list_employees(
        session=session,
        current_user=current_user,
        scope_context=scope_ctx,
        page=page,
        page_size=page_size,
        search=search,
        company_id=company_id,
        department_id=department_id,
        designation_id=designation_id,
        manager_user_id=manager_user_id,
        account_status=account_status,
    )

    return PaginatedEmployeesResponse(
        items=[user_service.serialize_employee_read(u) for u in items],
        page=page,
        page_size=page_size,
        total=total,
        pages=pages,
    )


@router.get(
    "/{user_id}",
    response_model=EmployeeRead,
    status_code=status.HTTP_200_OK,
    summary="Get Employee Details",
    description="Retrieve comprehensive details for a single employee within the user's data scope.",
    dependencies=[Depends(require_module_permission("ADMIN_EMPLOYEES", "view"))],
)
def get_employee_endpoint(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
) -> EmployeeRead:
    """Retrieve employee details by ID with data scope verification."""
    user = user_service.get_employee_by_id(session, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID '{user_id}' not found",
        )

    scope_ctx = permissions.resolve_data_scope_context(session, current_user, "ADMIN_EMPLOYEES")
    if not scope_ctx.is_user_permitted(user.user_id, user.company_id, user.department_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Employee is outside your authorized data scope.",
        )

    return user_service.serialize_employee_read(user)


@router.patch(
    "/{user_id}",
    response_model=EmployeeRead,
    status_code=status.HTTP_200_OK,
    summary="Update Employee Profile",
    description="Partially update an existing employee profile within the user's data scope.",
    dependencies=[Depends(require_module_permission("ADMIN_EMPLOYEES", "edit"))],
)
def update_employee_endpoint(
    user_id: uuid.UUID,
    update_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
) -> EmployeeRead:
    """Partially update employee profile with integrity and hierarchy cycle checks."""
    user = user_service.get_employee_by_id(session, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID '{user_id}' not found",
        )

    scope_ctx = permissions.resolve_data_scope_context(session, current_user, "ADMIN_EMPLOYEES")
    if not scope_ctx.is_user_permitted(user.user_id, user.company_id, user.department_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Employee is outside your authorized data scope.",
        )

    try:
        updated_user = user_service.update_employee(session, user, update_data)
        return user_service.serialize_employee_read(updated_user)
    except ValueError as exc:
        err_msg = str(exc)
        if "already registered" in err_msg:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=err_msg)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err_msg)


@router.patch(
    "/{user_id}/status",
    response_model=EmployeeRead,
    status_code=status.HTTP_200_OK,
    summary="Update Employee Status",
    description="Update employee account operational status (PENDING, ACTIVE, INACTIVE, SUSPENDED).",
    dependencies=[Depends(require_module_permission("ADMIN_EMPLOYEES", "approve"))],
)
def update_employee_status_endpoint(
    user_id: uuid.UUID,
    status_in: EmployeeStatusUpdate,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
) -> EmployeeRead:
    """Update employee status requiring module approve permission."""
    user = user_service.get_employee_by_id(session, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID '{user_id}' not found",
        )

    scope_ctx = permissions.resolve_data_scope_context(session, current_user, "ADMIN_EMPLOYEES")
    if not scope_ctx.is_user_permitted(user.user_id, user.company_id, user.department_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Employee is outside your authorized data scope.",
        )

    try:
        updated_user = user_service.update_employee_status(session, user, status_in.account_status)
        return user_service.serialize_employee_read(updated_user)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
