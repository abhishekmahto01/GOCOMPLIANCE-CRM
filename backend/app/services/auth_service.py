"""Authentication domain service for login, token refresh, logout, and password management."""
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple

import jwt
from fastapi import HTTPException, status
from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_and_validate_token,
    hash_password,
    hash_refresh_token,
    validate_password_strength,
    verify_password,
)
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.schemas.auth import TokenResponse

# Dummy hash for constant-time comparison when user is not found (prevents timing attacks)
DUMMY_HASH = "$argon2id$v=19$m=65536,t=3,p=4$q1W2e3R4t5Y6u7I8o9P0$dummyhashdummyhashdummyhashdummyhashdummyhash"


def authenticate_user(
    session: Session,
    identifier: str,
    password: str,
    client_ip: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> Tuple[User, TokenResponse]:
    """Authenticate user with official email or employee code, enforcing lockouts and status checks.

    Args:
        session: Active database session.
        identifier: User email or employee code.
        password: Raw plaintext password.
        client_ip: Client IP address.
        user_agent: Client user-agent.

    Returns:
        Tuple of (authenticated User instance, TokenResponse payload).

    Raises:
        HTTPException: On invalid credentials, account lock, or inactive account.
    """
    clean_id = identifier.strip()

    # Case-insensitive lookup against both official_email and employee_code
    stmt = select(User).where(
        (func.lower(User.official_email) == clean_id.lower())
        | (func.upper(User.employee_code) == clean_id.upper())
    )
    user = session.execute(stmt).scalar_one_or_none()

    if not user:
        # Constant-time dummy verification to avoid timing side-channels
        verify_password("dummy", DUMMY_HASH)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    now = datetime.now(timezone.utc)

    # 1. Check account temporary lockout
    if user.locked_until and user.locked_until > now:
        remaining_secs = int((user.locked_until - now).total_seconds())
        remaining_mins = max(1, remaining_secs // 60)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Account is temporarily locked due to multiple failed login attempts. Please try again in {remaining_mins} minute(s).",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2. Check account status (Only ACTIVE accounts are permitted to log in)
    if user.account_status != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is not active. Please contact system administrator.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Check if password hash exists (unactivated accounts cannot log in)
    if not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 4. Verify password in constant time
    if not verify_password(password, user.password_hash):
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= settings.MAX_FAILED_LOGIN_ATTEMPTS:
            user.locked_until = now + timedelta(minutes=settings.LOGIN_LOCK_MINUTES)
        session.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 5. Success: reset failed attempts, clear locks, and record login timestamp
    user.failed_login_attempts = 0
    user.locked_until = None
    user.last_login_at = now

    # 6. Issue access and refresh tokens
    access_token = create_access_token(
        user_id=user.user_id,
        token_version=user.token_version,
    )
    raw_refresh_token, jti, expires_at = create_refresh_token(
        user_id=user.user_id,
        token_version=user.token_version,
    )

    # Store hashed refresh token in database
    db_refresh_token = RefreshToken(
        user_id=user.user_id,
        jti=jti,
        token_hash=hash_refresh_token(raw_refresh_token),
        expires_at=expires_at,
        created_ip=client_ip,
        user_agent=user_agent,
    )
    session.add(db_refresh_token)
    session.commit()

    token_response = TokenResponse(
        access_token=access_token,
        refresh_token=raw_refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        must_change_password=user.must_change_password,
    )

    return user, token_response


def refresh_access_token(
    session: Session,
    raw_refresh_token: str,
    client_ip: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> TokenResponse:
    """Rotate an active refresh token and issue a new access/refresh token pair.

    Args:
        session: Active database session.
        raw_refresh_token: The incoming plaintext refresh token.
        client_ip: Client IP address.
        user_agent: Client user-agent.

    Returns:
        New TokenResponse containing rotated tokens.

    Raises:
        HTTPException: If token is expired, invalid, revoked, or compromised (reuse detection).
    """
    try:
        payload = decode_and_validate_token(raw_refresh_token, expected_type="refresh")
    except (jwt.PyJWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = uuid.UUID(payload["sub"])
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token claims",
            headers={"WWW-Authenticate": "Bearer"},
        )

    jti = payload["jti"]
    token_version = payload["token_version"]

    user = session.get(User, user_id)
    if not user or user.account_status != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive or not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user's token version changed (e.g. password was changed)
    if user.token_version != token_version:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session has been revoked. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Fetch token from registry
    stmt = select(RefreshToken).where(RefreshToken.jti == jti)
    db_token = session.execute(stmt).scalar_one_or_none()

    now = datetime.now(timezone.utc)

    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Token reuse detection: if a revoked token is presented again, invalidate all user sessions
    if db_token.revoked_at is not None:
        user.token_version += 1
        session.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Revoked refresh token presented. All active sessions have been terminated for security.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check token expiration
    if db_token.expires_at < now:
        db_token.revoked_at = now
        session.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify hash match
    expected_hash = hash_refresh_token(raw_refresh_token)
    if db_token.token_hash != expected_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Rotate token: generate new pair
    new_raw_refresh, new_jti, new_expires_at = create_refresh_token(
        user_id=user.user_id,
        token_version=user.token_version,
    )
    new_access_token = create_access_token(
        user_id=user.user_id,
        token_version=user.token_version,
    )

    # Revoke old token and mark replacement
    db_token.revoked_at = now
    db_token.replaced_by_jti = new_jti

    # Store new token record
    new_db_token = RefreshToken(
        user_id=user.user_id,
        jti=new_jti,
        token_hash=hash_refresh_token(new_raw_refresh),
        expires_at=new_expires_at,
        created_ip=client_ip,
        user_agent=user_agent,
    )
    session.add(new_db_token)
    session.commit()

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_raw_refresh,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        must_change_password=user.must_change_password,
    )


def logout_user(session: Session, raw_refresh_token: str) -> None:
    """Explicitly revoke an active refresh token on logout (safe and idempotent).

    Args:
        session: Active database session.
        raw_refresh_token: Plaintext refresh token to revoke.
    """
    try:
        payload = decode_and_validate_token(raw_refresh_token, expected_type="refresh")
        jti = payload.get("jti")
        if jti:
            now = datetime.now(timezone.utc)
            stmt = (
                update(RefreshToken)
                .where(RefreshToken.jti == jti, RefreshToken.revoked_at.is_(None))
                .values(revoked_at=now)
            )
            session.execute(stmt)
            session.commit()
    except Exception:
        # Logout is idempotent and safely succeeds even if token was already expired or malformed
        pass


def change_user_password(
    session: Session,
    user: User,
    current_password: str,
    new_password: str,
) -> None:
    """Validate current password, verify new password complexity, update hash, and invalidate all sessions.

    Args:
        session: Active database session.
        user: Current authenticated user entity.
        current_password: User's existing plaintext password.
        new_password: User's proposed new plaintext password.

    Raises:
        HTTPException: If current password is wrong, new password is weak or identical to old.
    """
    if not user.password_hash or not verify_password(current_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    # Validate complexity
    try:
        validate_password_strength(new_password)
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err),
        )

    if current_password == new_password or verify_password(new_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password cannot be identical to the current password",
        )

    # Reject setting new password to the temporary trial password
    trial_pwd = settings.TRIAL_DEFAULT_PASSWORD
    if (trial_pwd and new_password == trial_pwd.strip()) or new_password == "12345":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password cannot be the trial default temporary password",
        )

    now = datetime.now(timezone.utc)
    user.password_hash = hash_password(new_password)
    user.must_change_password = False
    user.password_changed_at = now
    user.token_version += 1  # Invalidates all existing access and refresh tokens globally

    # Revoke all existing refresh tokens for this user in the database
    stmt = (
        update(RefreshToken)
        .where(RefreshToken.user_id == user.user_id, RefreshToken.revoked_at.is_(None))
        .values(revoked_at=now)
    )
    session.execute(stmt)
    session.commit()
