"""Admin Permission Management API routes."""
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, require_module_permission
from app.database.session import get_db
from app.models.user import User
from app.schemas.permission import (
    CopyPermissionsRequest,
    CopyPermissionsResponse,
    PermissionCatalogResponse,
    UserPermissionsDetailResponse,
    UserPermissionsSaveRequest,
)
from app.services import permissions

router = APIRouter(prefix="/admin", tags=["Admin Permissions Management"])


@router.get(
    "/permission-catalog",
    response_model=PermissionCatalogResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Permission Catalog",
    description="Retrieve the complete catalog of Sales and Operation modules and pages with supported actions.",
    dependencies=[Depends(require_module_permission("ADMIN_ACCESS", "view"))],
)
def get_permission_catalog_endpoint(
    session: Session = Depends(get_db),
) -> PermissionCatalogResponse:
    """Return the structured catalog of modules, pages, and actions."""
    return permissions.get_permission_catalog(session)


@router.get(
    "/users/{user_id}/permissions",
    response_model=UserPermissionsDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Employee Permissions Bundle",
    description="Retrieve the page-level action permissions and user settings for an employee.",
    dependencies=[Depends(require_module_permission("ADMIN_ACCESS", "view"))],
)
def get_user_permissions_endpoint(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
) -> UserPermissionsDetailResponse:
    """Retrieve an employee's permissions and user settings within authorized company scope."""
    target_user = session.get(User, user_id)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID '{user_id}' not found",
        )

    scope_ctx = permissions.resolve_data_scope_context(session, current_user, "ADMIN_ACCESS")
    if not scope_ctx.is_user_permitted(target_user.user_id, target_user.company_id, target_user.department_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Employee is outside your authorized company scope.",
        )

    try:
        return permissions.get_user_permissions_bundle(session, user_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.put(
    "/users/{user_id}/permissions",
    response_model=UserPermissionsDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Save Employee Permissions",
    description="Save page-level permissions and user settings for an employee transactionally.",
    dependencies=[Depends(require_module_permission("ADMIN_ACCESS", "edit"))],
)
def save_user_permissions_endpoint(
    user_id: uuid.UUID,
    payload: UserPermissionsSaveRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
) -> UserPermissionsDetailResponse:
    """Save employee permissions and settings with validation, anti-escalation, and audit logging."""
    target_user = session.get(User, user_id)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID '{user_id}' not found",
        )

    scope_ctx = permissions.resolve_data_scope_context(session, current_user, "ADMIN_ACCESS")
    if not scope_ctx.is_user_permitted(target_user.user_id, target_user.company_id, target_user.department_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Cannot modify permissions for an employee outside your authorized company scope.",
        )

    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    try:
        return permissions.save_user_permissions_bundle(
            session=session,
            actor_user=current_user,
            target_user_id=user_id,
            payload=payload,
            ip_address=client_ip,
            user_agent=user_agent,
        )
    except permissions.GrantorEscalationError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except ValueError as exc:
        err_msg = str(exc)
        if "not found" in err_msg.lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=err_msg)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err_msg)


@router.post(
    "/users/{user_id}/permissions/copy",
    response_model=CopyPermissionsResponse,
    status_code=status.HTTP_200_OK,
    summary="Copy Employee Permissions",
    description="Copy Sales and Operation permissions from a source employee to the target employee.",
    dependencies=[Depends(require_module_permission("ADMIN_ACCESS", "edit"))],
)
def copy_user_permissions_endpoint(
    user_id: uuid.UUID,
    copy_in: CopyPermissionsRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
) -> CopyPermissionsResponse:
    """Copy permissions from source employee to target employee."""
    target_user = session.get(User, user_id)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Target employee with ID '{user_id}' not found",
        )

    source_user = session.get(User, copy_in.source_user_id)
    if not source_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source employee with ID '{copy_in.source_user_id}' not found",
        )

    scope_ctx = permissions.resolve_data_scope_context(session, current_user, "ADMIN_ACCESS")
    if not scope_ctx.is_user_permitted(target_user.user_id, target_user.company_id, target_user.department_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Target employee is outside your authorized company scope.",
        )
    if not scope_ctx.is_user_permitted(source_user.user_id, source_user.company_id, source_user.department_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Source employee is outside your authorized company scope.",
        )

    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    try:
        return permissions.copy_user_permissions(
            session=session,
            actor_user=current_user,
            source_user_id=copy_in.source_user_id,
            target_user_id=user_id,
            ip_address=client_ip,
            user_agent=user_agent,
        )
    except permissions.PermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except ValueError as exc:
        err_msg = str(exc)
        if "not found" in err_msg.lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=err_msg)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err_msg)
