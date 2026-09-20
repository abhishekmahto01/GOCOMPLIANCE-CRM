"""FastAPI authentication and security dependencies."""
import uuid
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_and_validate_token
from app.database.session import get_db
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

    Args:
        token: Bearer JWT string extracted from Authorization header.
        session: Active database session.

    Returns:
        The authenticated User model instance.

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

    Args:
        current_user: Active User instance from get_current_active_user.

    Returns:
        The validated fully activated User instance.

    Raises:
        HTTPException: 403 Forbidden if user still must change their temporary password.
    """
    if current_user.must_change_password:
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

