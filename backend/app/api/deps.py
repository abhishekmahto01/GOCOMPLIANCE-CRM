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
