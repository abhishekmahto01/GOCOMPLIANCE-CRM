"""Admin Source Master API routes."""
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, require_module_permission
from app.database.session import get_db
from app.models.user import User
from app.schemas.source import SourceCreate, SourceRead, SourceUpdate
from app.services import source_service

router = APIRouter(prefix="/admin/sources", tags=["Source Master"])


@router.get(
    "",
    response_model=List[SourceRead],
    status_code=status.HTTP_200_OK,
    summary="List Sources",
    description="Retrieve all lead sources in source_master with optional search and status filters.",
    dependencies=[Depends(require_module_permission("ADMIN", "view"))],
)
def list_sources_endpoint(
    search: Optional[str] = Query(None, description="Search by code, name, or description"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (ACTIVE/INACTIVE)"),
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
) -> List[SourceRead]:
    """Retrieve list of lead sources."""
    sources = source_service.list_sources(
        session=session,
        search=search,
        status_filter=status_filter,
    )
    return [SourceRead.model_validate(s) for s in sources]


@router.post(
    "",
    response_model=SourceRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create Source",
    description="Create a new lead source master record.",
    dependencies=[Depends(require_module_permission("ADMIN", "create"))],
)
def create_source_endpoint(
    source_in: SourceCreate,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
) -> SourceRead:
    """Create a new lead source."""
    source = source_service.create_source(session=session, source_in=source_in)
    return SourceRead.model_validate(source)


@router.get(
    "/{source_id}",
    response_model=SourceRead,
    status_code=status.HTTP_200_OK,
    summary="Get Source by ID",
    dependencies=[Depends(require_module_permission("ADMIN", "view"))],
)
def get_source_endpoint(
    source_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
) -> SourceRead:
    """Retrieve single source details."""
    source = source_service.get_source_by_id(session=session, source_id=source_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source not found.",
        )
    return SourceRead.model_validate(source)


@router.put(
    "/{source_id}",
    response_model=SourceRead,
    status_code=status.HTTP_200_OK,
    summary="Update Source",
    dependencies=[Depends(require_module_permission("ADMIN", "edit"))],
)
def update_source_endpoint(
    source_id: uuid.UUID,
    source_in: SourceUpdate,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
) -> SourceRead:
    """Update source details."""
    source = source_service.update_source(
        session=session,
        source_id=source_id,
        source_in=source_in,
    )
    return SourceRead.model_validate(source)


@router.delete(
    "/{source_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete Source",
    dependencies=[Depends(require_module_permission("ADMIN", "edit"))],
)
def delete_source_endpoint(
    source_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
) -> dict:
    """Delete a source if not referenced by sales orders."""
    source_service.delete_source(session=session, source_id=source_id)
    return {
        "success": True,
        "message": "Source deleted successfully.",
        "deleted_id": str(source_id),
    }
