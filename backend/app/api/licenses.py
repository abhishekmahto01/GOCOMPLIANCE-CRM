"""Admin License & Service Master API routes."""
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
from app.schemas.service import ServiceCreate, ServiceDetailRead, ServiceRead, ServiceUpdate
from app.services import service_service

router = APIRouter(prefix="/admin/licenses", tags=["License Master"])


@router.get(
    "",
    response_model=List[ServiceRead],
    status_code=status.HTTP_200_OK,
    summary="List Licenses & Services",
    description="Retrieve all licenses/services in service_master with optional search, category, and status filters.",
    dependencies=[Depends(require_module_permission("ADMIN", "view"))],
)
def list_licenses_endpoint(
    search: Optional[str] = Query(None, description="Search by code, name, category, or description"),
    category: Optional[str] = Query(None, description="Filter by category (LICENCE, REGISTRATION, INCORPORATION, COMPLIANCE)"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (ACTIVE/INACTIVE)"),
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
) -> List[ServiceRead]:
    """Retrieve list of services/licenses."""
    services = service_service.list_services(
        session=session,
        search=search,
        category=category,
        status_filter=status_filter,
    )
    return [ServiceRead.model_validate(s) for s in services]


@router.post(
    "",
    response_model=ServiceRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create License/Service",
    description="Create a new compliance license or statutory service master record.",
    dependencies=[Depends(require_module_permission("ADMIN", "create"))],
)
def create_license_endpoint(
    service_in: ServiceCreate,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
) -> ServiceRead:
    """Create a new license/service master record."""
    try:
        new_service = service_service.create_service(session, service_in)
        return ServiceRead.model_validate(new_service)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get(
    "/{license_id}",
    response_model=ServiceRead,
    status_code=status.HTTP_200_OK,
    summary="Get License Details",
    description="Retrieve details for a single license by UUID.",
    dependencies=[Depends(require_module_permission("ADMIN", "view"))],
)
def get_license_endpoint(
    license_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
) -> ServiceRead:
    """Retrieve single license by ID."""
    service = service_service.get_service_by_id(session, license_id)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"License with ID '{license_id}' not found",
        )
    return ServiceRead.model_validate(service)


@router.patch(
    "/{license_id}",
    response_model=ServiceRead,
    status_code=status.HTTP_200_OK,
    summary="Update License/Service",
    description="Update license display name, category, description, SLA days, fees, or operational status.",
    dependencies=[Depends(require_module_permission("ADMIN", "edit"))],
)
def update_license_endpoint(
    license_id: uuid.UUID,
    update_in: ServiceUpdate,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
) -> ServiceRead:
    """Update an existing license master record."""
    target_service = service_service.get_service_by_id(session, license_id)
    if not target_service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"License with ID '{license_id}' not found",
        )

    try:
        updated = service_service.update_service(session, target_service, update_in)
        return ServiceRead.model_validate(updated)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.delete(
    "/{license_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete License/Service",
    description="Delete a license master record if no dependencies (sales orders, operations applications) exist. Restricted to Super Admin.",
    dependencies=[Depends(require_super_admin)],
)
def delete_license_endpoint(
    license_id: uuid.UUID,
    current_user: User = Depends(require_super_admin),
    session: Session = Depends(get_db),
) -> dict:
    """Delete a license master record (Super Admin only)."""
    target_service = service_service.get_service_by_id(session, license_id)
    if not target_service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"License with ID '{license_id}' not found",
        )

    try:
        service_service.delete_service(session, target_service)
        return {
            "message": f"License '{target_service.service_name}' was successfully deleted.",
            "license_id": str(license_id),
        }
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
