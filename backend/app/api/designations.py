"""Admin Designation Master API routes."""
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import (
    get_current_active_user,
    require_module_permission,
    require_super_admin,
)
from app.database.session import get_db
from app.models.user import User
from app.schemas.designation import DesignationCreate, DesignationRead, DesignationUpdate
from app.services import designation_service

router = APIRouter(prefix="/admin/designations", tags=["Designation Master"])


@router.get(
    "",
    response_model=List[DesignationRead],
    status_code=status.HTTP_200_OK,
    summary="List Designations",
    description="Retrieve all designations in designation_master with optional company, search, and status filters.",
    dependencies=[Depends(require_module_permission("ADMIN", "view"))],
)
def list_designations_endpoint(
    company_id: Optional[uuid.UUID] = Query(None, description="Filter by company ID"),
    search: Optional[str] = Query(None, description="Search by code, title, or description"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (ACTIVE/INACTIVE)"),
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
) -> List[DesignationRead]:
    """Retrieve list of designations."""
    designations = designation_service.list_designations(
        session=session,
        company_id=company_id,
        search=search,
        status_filter=status_filter,
    )
    return [DesignationRead.model_validate(d) for d in designations]


@router.post(
    "",
    response_model=DesignationRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create Designation",
    description="Create a new designation master record.",
    dependencies=[Depends(require_module_permission("ADMIN", "create"))],
)
def create_designation_endpoint(
    desig_in: DesignationCreate,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
) -> DesignationRead:
    """Create a new designation."""
    try:
        new_desig = designation_service.create_designation(session, desig_in)
        return DesignationRead.model_validate(new_desig)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get(
    "/{designation_id}",
    response_model=DesignationRead,
    status_code=status.HTTP_200_OK,
    summary="Get Designation Details",
    description="Retrieve details for a single designation by UUID.",
    dependencies=[Depends(require_module_permission("ADMIN", "view"))],
)
def get_designation_endpoint(
    designation_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
) -> DesignationRead:
    """Retrieve single designation by ID."""
    desig = designation_service.get_designation_by_id(session, designation_id)
    if not desig:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Designation with ID '{designation_id}' not found",
        )
    return DesignationRead.model_validate(desig)


@router.patch(
    "/{designation_id}",
    response_model=DesignationRead,
    status_code=status.HTTP_200_OK,
    summary="Update Designation",
    description="Update designation title, level rank, managerial flag, description, or operational status.",
    dependencies=[Depends(require_module_permission("ADMIN", "edit"))],
)
def update_designation_endpoint(
    designation_id: uuid.UUID,
    update_in: DesignationUpdate,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
) -> DesignationRead:
    """Update an existing designation master record."""
    target_desig = designation_service.get_designation_by_id(session, designation_id)
    if not target_desig:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Designation with ID '{designation_id}' not found",
        )
    try:
        updated = designation_service.update_designation(session, target_desig, update_in)
        return DesignationRead.model_validate(updated)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.delete(
    "/{designation_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete Designation",
    description="Delete a designation if no employees are assigned. Restricted to Super Admin.",
    dependencies=[Depends(require_super_admin)],
)
def delete_designation_endpoint(
    designation_id: uuid.UUID,
    current_user: User = Depends(require_super_admin),
    session: Session = Depends(get_db),
) -> dict:
    """Delete an existing designation master record (Super Admin only)."""
    target_desig = designation_service.get_designation_by_id(session, designation_id)
    if not target_desig:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Designation with ID '{designation_id}' not found",
        )
    try:
        designation_service.delete_designation(session, target_desig)
        return {
            "success": True,
            "message": f"Designation '{target_desig.designation_name}' was successfully deleted.",
            "deleted_id": str(designation_id),
        }
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
