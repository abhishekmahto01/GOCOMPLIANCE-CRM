"""Admin Department Master API routes."""
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, require_module_permission
from app.database.session import get_db
from app.models.user import User
from app.schemas.department import DepartmentCreate, DepartmentRead, DepartmentUpdate
from app.services import department_service

router = APIRouter(prefix="/admin/departments", tags=["Department Master"])


@router.get(
    "",
    response_model=List[DepartmentRead],
    status_code=status.HTTP_200_OK,
    summary="List Departments",
    description="Retrieve all departments in department_master with optional company, search, and status filters.",
    dependencies=[Depends(require_module_permission("ADMIN", "view"))],
)
def list_departments_endpoint(
    company_id: Optional[uuid.UUID] = Query(None, description="Filter by company ID"),
    search: Optional[str] = Query(None, description="Search by code, name, or description"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (ACTIVE/INACTIVE)"),
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
) -> List[DepartmentRead]:
    """Retrieve list of departments."""
    departments = department_service.list_departments(
        session=session,
        company_id=company_id,
        search=search,
        status_filter=status_filter,
    )
    return [DepartmentRead.model_validate(d) for d in departments]


@router.post(
    "",
    response_model=DepartmentRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create Department",
    description="Create a new department master record.",
    dependencies=[Depends(require_module_permission("ADMIN", "create"))],
)
def create_department_endpoint(
    dept_in: DepartmentCreate,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
) -> DepartmentRead:
    """Create a new department."""
    try:
        new_dept = department_service.create_department(session, dept_in)
        return DepartmentRead.model_validate(new_dept)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get(
    "/{department_id}",
    response_model=DepartmentRead,
    status_code=status.HTTP_200_OK,
    summary="Get Department Details",
    description="Retrieve details for a single department by UUID.",
    dependencies=[Depends(require_module_permission("ADMIN", "view"))],
)
def get_department_endpoint(
    department_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
) -> DepartmentRead:
    """Retrieve single department by ID."""
    dept = department_service.get_department_by_id(session, department_id)
    if not dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Department with ID '{department_id}' not found",
        )
    return DepartmentRead.model_validate(dept)


@router.patch(
    "/{department_id}",
    response_model=DepartmentRead,
    status_code=status.HTTP_200_OK,
    summary="Update Department",
    description="Update department name, description, or operational status.",
    dependencies=[Depends(require_module_permission("ADMIN", "edit"))],
)
def update_department_endpoint(
    department_id: uuid.UUID,
    update_in: DepartmentUpdate,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
) -> DepartmentRead:
    """Update an existing department master record."""
    target_dept = department_service.get_department_by_id(session, department_id)
    if not target_dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Department with ID '{department_id}' not found",
        )
    try:
        updated = department_service.update_department(session, target_dept, update_in)
        return DepartmentRead.model_validate(updated)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.delete(
    "/{department_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete Department",
    description="Delete a department if no employees are assigned.",
    dependencies=[Depends(require_module_permission("ADMIN", "delete"))],
)
def delete_department_endpoint(
    department_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
) -> dict:
    """Delete an existing department master record."""
    target_dept = department_service.get_department_by_id(session, department_id)
    if not target_dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Department with ID '{department_id}' not found",
        )
    try:
        department_service.delete_department(session, target_dept)
        return {
            "success": True,
            "message": f"Department '{target_dept.department_name}' was successfully deleted.",
            "deleted_id": str(department_id),
        }
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
