"""Admin Company Master API routes."""
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, require_module_permission
from app.database.session import get_db
from app.models.user import User
from app.schemas.company import CompanyCreate, CompanyRead, CompanyUpdate
from app.services import company_service

router = APIRouter(prefix="/admin/companies", tags=["Company Master"])


@router.get(
    "",
    response_model=List[CompanyRead],
    status_code=status.HTTP_200_OK,
    summary="List Companies",
    description="Retrieve all companies in company_master with optional search and status filters.",
    dependencies=[Depends(require_module_permission("ADMIN", "view"))],
)
def list_companies_endpoint(
    search: Optional[str] = Query(None, description="Search by code, name, legal name, or prefix"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (ACTIVE/INACTIVE)"),
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
) -> List[CompanyRead]:
    """Retrieve list of companies."""
    companies = company_service.list_companies(
        session=session,
        search=search,
        status_filter=status_filter,
    )
    return [CompanyRead.model_validate(c) for c in companies]


@router.post(
    "",
    response_model=CompanyRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create Company",
    description="Create a new corporate entity record with unique code, name, and prefix.",
    dependencies=[Depends(require_module_permission("ADMIN", "create"))],
)
def create_company_endpoint(
    company_in: CompanyCreate,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
) -> CompanyRead:
    """Create a new company master record."""
    try:
        new_company = company_service.create_company(session, company_in)
        return CompanyRead.model_validate(new_company)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get(
    "/{company_id}",
    response_model=CompanyRead,
    status_code=status.HTTP_200_OK,
    summary="Get Company Details",
    description="Retrieve details for a single company by UUID.",
    dependencies=[Depends(require_module_permission("ADMIN", "view"))],
)
def get_company_endpoint(
    company_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
) -> CompanyRead:
    """Retrieve single company by ID."""
    company = company_service.get_company_by_id(session, company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with ID '{company_id}' not found",
        )
    return CompanyRead.model_validate(company)


@router.patch(
    "/{company_id}",
    response_model=CompanyRead,
    status_code=status.HTTP_200_OK,
    summary="Update Company",
    description="Update company display name, legal name, or operational status.",
    dependencies=[Depends(require_module_permission("ADMIN", "edit"))],
)
def update_company_endpoint(
    company_id: uuid.UUID,
    update_in: CompanyUpdate,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
) -> CompanyRead:
    """Update an existing company master record."""
    target_company = company_service.get_company_by_id(session, company_id)
    if not target_company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with ID '{company_id}' not found",
        )

    try:
        updated = company_service.update_company(session, target_company, update_in)
        return CompanyRead.model_validate(updated)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.delete(
    "/{company_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete Company",
    description="Delete a company master record if no dependencies (users, departments, orders) exist.",
    dependencies=[Depends(require_module_permission("ADMIN", "delete"))],
)
def delete_company_endpoint(
    company_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
) -> dict:
    """Delete a company master record."""
    target_company = company_service.get_company_by_id(session, company_id)
    if not target_company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with ID '{company_id}' not found",
        )

    try:
        company_service.delete_company(session, target_company)
        return {
            "message": f"Company '{target_company.company_name}' was successfully deleted.",
            "company_id": str(company_id),
        }
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

