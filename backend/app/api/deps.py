"""FastAPI authentication and security dependencies."""
from datetime import datetime, timezone
import uuid
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import decode_and_validate_token
from app.database.session import get_db
from app.models.impersonation_session import ImpersonationSession
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/login",
    auto_error=False,
)


def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    session: Session = Depends(get_db),
) -> User:
    """Validate JWT access token and return the current User entity.

    For impersonated sessions, validates the active ImpersonationSession record,
    ensures the feature is enabled, verifies the originating Super Admin is active,
    and returns the target employee with impersonation metadata bound to the instance.

    Args:
        token: Bearer JWT string extracted from Authorization header.
        session: Active database session.

    Returns:
        The authenticated User model instance (target employee if impersonating).

    Raises:
        HTTPException: 401 Unauthorized if token is missing, invalid, expired, or revoked.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decode_and_validate_token(token, expected_type="access")
    except (jwt.PyJWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = uuid.UUID(payload["sub"])
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token subject identifier",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_version = payload.get("token_version")
    is_impersonated = bool(payload.get("is_impersonated", False))

    imp_session_obj = None
    if is_impersonated:
        # 1. Reject if impersonation feature flag is disabled
        if not settings.ENABLE_ADMIN_IMPERSONATION:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Admin impersonation feature is currently disabled.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 2. Server-side validation of active ImpersonationSession
        session_id_str = payload.get("impersonation_session_id")
        if not session_id_str:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Malformed impersonation token payload.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        try:
            session_id = uuid.UUID(session_id_str)
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid impersonation session identifier.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        imp_session_obj = session.get(ImpersonationSession, session_id)
        now = datetime.now(timezone.utc)
        if not imp_session_obj or not imp_session_obj.is_active or imp_session_obj.expires_at < now:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Impersonation session has expired or been revoked. Please log in again.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 3. Ensure originating Super Admin account is still active
        admin_user = session.get(User, imp_session_obj.actor_admin_id)
        if not admin_user or admin_user.account_status != "ACTIVE":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Originating Admin account is no longer active.",
                headers={"WWW-Authenticate": "Bearer"},
            )

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.token_version != token_version:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session has been invalidated. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Attach impersonation attributes for runtime RBAC & audit logging
    if is_impersonated and imp_session_obj:
        user._is_impersonated = True
        user._actor_admin_id = imp_session_obj.actor_admin_id
        user._impersonation_session_id = imp_session_obj.session_id
    else:
        user._is_impersonated = False
        user._actor_admin_id = None
        user._impersonation_session_id = None

    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Ensure the authenticated user is currently in ACTIVE status.

    Args:
        current_user: User instance from get_current_user.

    Returns:
        The validated active User instance.

    Raises:
        HTTPException: 403 Forbidden if the account is PENDING, INACTIVE, or SUSPENDED.
    """
    if current_user.account_status != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive or suspended",
        )
    return current_user


def require_fully_activated_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Ensure the user is active AND has completed mandatory first-login password change.

    Users with must_change_password=True are in restricted trial session and cannot access
    business modules until they establish a new permanent password.
    When a Super Admin impersonates an employee, inspection is permitted without changing password.

    Args:
        current_user: Active User instance from get_current_active_user.

    Returns:
        The validated fully activated User instance.

    Raises:
        HTTPException: 403 Forbidden if user still must change their temporary password.
    """
    if current_user.must_change_password and not getattr(current_user, "_is_impersonated", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Mandatory password change required before accessing CRM modules.",
        )
    return current_user


def require_module_permission(
    module_code: str,
    action: str = "view",
):
    """FastAPI authorization dependency factory enforcing per-user module permissions.

    Usage:
        @router.get("/employees", dependencies=[Depends(require_module_permission("ADMIN_EMPLOYEES", "view"))])
        def list_employees(...): ...

    Args:
        module_code: The uppercase code of the module (e.g., 'ADMIN_EMPLOYEES', 'SALES').
        action: The requested action ('view', 'create', 'edit', 'delete', 'approve').

    Returns:
        Callable FastAPI dependency that resolves to the UserModulePermission instance.

    Raises:
        HTTPException: 403 Forbidden if the user lacks active permission for the action
                       or has not completed mandatory password change.
    """
    from app.services import permissions

    def _permission_dependency(
        current_user: User = Depends(require_fully_activated_user),
        session: Session = Depends(get_db),
    ):
        if not permissions.has_permission(session, current_user, module_code, action):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied for module '{module_code}'. Insufficient privileges.",
            )
        permission = permissions.get_user_module_permission(session, current_user.user_id, module_code)
        return permission

    return _permission_dependency


def require_super_admin(
    current_user: User = Depends(require_fully_activated_user),
    session: Session = Depends(get_db),
) -> User:
    """Ensure the authenticated user is a Super Admin.

    Master delete operations and critical global configurations are strictly restricted
    to Super Admin users. Super Admin operations are blocked during employee impersonation.

    Raises:
        HTTPException: 403 Forbidden if user is not a Super Admin or is impersonating.
    """
    if getattr(current_user, "_is_impersonated", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super Admin operations are not permitted during employee impersonation.",
        )

    from app.services import permissions

    if not permissions.is_super_admin_user(session, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Only Super Admin has permission to perform this action.",
        )
    return current_user


