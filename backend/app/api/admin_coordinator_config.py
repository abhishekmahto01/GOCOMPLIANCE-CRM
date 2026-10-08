"""Admin API endpoints for managing Operations Coordinator Configuration."""
import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, require_module_permission
from app.database.session import get_db
from app.models.user import User
from app.schemas.coordinator_config import (
    EligibleCoordinatorOption,
    OperationsCoordinatorConfigRead,
    OperationsCoordinatorConfigUpdate,
)
from app.services import coordinator_config_service

router = APIRouter(prefix="/admin/coordinator-configs", tags=["Admin Operations Coordinator Config"])


@router.get(
    "",
    response_model=List[OperationsCoordinatorConfigRead],
    status_code=status.HTTP_200_OK,
    summary="List Operations Coordinator Configurations",
    description="Retrieve Operations coordinator mapping for all companies.",
    dependencies=[Depends(require_module_permission("ADMIN", "view"))],
)
def list_coordinator_configs_endpoint(
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
) -> List[OperationsCoordinatorConfigRead]:
    """Retrieve coordinator configuration for each company."""
    return coordinator_config_service.list_coordinator_configs(session)


@router.get(
    "/eligible-coordinators",
    response_model=List[EligibleCoordinatorOption],
    status_code=status.HTTP_200_OK,
    summary="List Eligible Operations Coordinators",
    description="Retrieve all active Operations team members eligible to be assigned as Operations coordinators.",
    dependencies=[Depends(require_module_permission("ADMIN", "view"))],
)
def list_eligible_coordinators_endpoint(
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
) -> List[EligibleCoordinatorOption]:
    """Retrieve dropdown of eligible Operations coordinators."""
    return coordinator_config_service.get_eligible_coordinators(session)


@router.put(
    "/{company_id}",
    response_model=OperationsCoordinatorConfigRead,
    status_code=status.HTTP_200_OK,
    summary="Update Operations Coordinator for a Company",
    description="Update or assign the default Operations coordinator for a specific company.",
    dependencies=[Depends(require_module_permission("ADMIN", "edit"))],
)
def update_coordinator_config_endpoint(
    company_id: uuid.UUID,
    payload: OperationsCoordinatorConfigUpdate,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
) -> OperationsCoordinatorConfigRead:
    """Update coordinator mapping for a company."""
    try:
        return coordinator_config_service.update_coordinator_config(
            session=session,
            company_id=company_id,
            coordinator_user_id=payload.coordinator_user_id,
            updated_by=current_user,
        )
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err),
        )
