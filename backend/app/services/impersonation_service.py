"""Domain service for Super Admin employee impersonation ("Login as Employee")."""
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
import uuid

from fastapi import HTTPException, status
from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_refresh_token,
)
from app.models.impersonation_session import ImpersonationAuditLog, ImpersonationSession
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.schemas.impersonation import (
    ImpersonationMetadata,
    ImpersonationStatusResponse,
    ImpersonationTokenResponse,
    ReturnToAdminResponse,
)
from app.services import permissions


def start_impersonation(
    session: Session,
    admin_user: User,
    employee_code: str,
    client_ip: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> ImpersonationTokenResponse:
    """Initiate an impersonation session for an employee by employee code.

    Args:
        session: Active database session.
        admin_user: Currently authenticated Super Admin user.
        employee_code: Uppercase target employee code.
        client_ip: Client IP address.
        user_agent: Client user-agent string.

    Returns:
        ImpersonationTokenResponse with scoped JWT tokens and metadata.

    Raises:
        HTTPException: If feature is disabled, user is unauthorized, or target is invalid.
    """
    # 1. Feature setting enforcement
    if not settings.ENABLE_ADMIN_IMPERSONATION:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin impersonation feature is currently disabled on the server.",
        )

    # 2. Prevent nested impersonation
    if getattr(admin_user, "_is_impersonated", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nested impersonation is not permitted. Return to Admin first.",
        )

    # 3. Super Admin authorization check
    if not permissions.is_super_admin_user(session, admin_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Only Super Admin users can initiate employee impersonation.",
        )

    # 4. Target employee resolution and validation
    clean_code = employee_code.strip().upper()
    stmt = select(User).where(User.employee_code == clean_code)
    target_user = session.execute(stmt).scalar_one_or_none()

    if not target_user:
        # Fallback 1: Support legacy / updated company prefix mapping (CG <-> GC)
        alt_code = None
        if clean_code.startswith("CG"):
            alt_code = "GC" + clean_code[2:]
        elif clean_code.startswith("GC"):
            alt_code = "CG" + clean_code[2:]
        elif clean_code.isdigit():
            alt_code = f"GC{int(clean_code):04d}"

        if alt_code:
            stmt = select(User).where(User.employee_code == alt_code)
            target_user = session.execute(stmt).scalar_one_or_none()

    if not target_user and clean_code.isdigit():
        stmt = select(User).where(User.employee_code == f"CG{int(clean_code):04d}")
        target_user = session.execute(stmt).scalar_one_or_none()

    if not target_user and "@" in clean_code:
        stmt = select(User).where(func.lower(User.official_email) == clean_code.lower())
        target_user = session.execute(stmt).scalar_one_or_none()

    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with code '{clean_code}' was not found.",
        )

    # Cannot impersonate self
    if target_user.user_id == admin_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot impersonate your own Super Admin account.",
        )

    # Must be active
    if target_user.account_status != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot impersonate employee '{clean_code}' because the account status is {target_user.account_status}.",
        )

    # Cannot impersonate another Super Admin
    if permissions.is_super_admin_user(session, target_user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot impersonate another Super Admin account.",
        )

    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=30)  # Capped at 30 minutes
    session_id = uuid.uuid4()

    # 5. Create token pair with impersonation claims
    access_token = create_access_token(
        user_id=target_user.user_id,
        token_version=target_user.token_version,
        expires_delta=timedelta(minutes=30),
        is_impersonated=True,
        impersonation_session_id=session_id,
        actor_admin_id=admin_user.user_id,
    )
    raw_refresh_token, jti, refresh_expires_at = create_refresh_token(
        user_id=target_user.user_id,
        token_version=target_user.token_version,
        expires_delta=timedelta(minutes=30),
        is_impersonated=True,
        impersonation_session_id=session_id,
        actor_admin_id=admin_user.user_id,
    )

    # 6. Create ImpersonationSession record
    imp_session = ImpersonationSession(
        session_id=session_id,
        actor_admin_id=admin_user.user_id,
        target_user_id=target_user.user_id,
        impersonation_token_jti=jti,
        is_active=True,
        created_at=now,
        expires_at=expires_at,
        created_ip=client_ip,
        user_agent=user_agent,
    )
    session.add(imp_session)
    session.flush()

    # Store refresh token
    db_refresh = RefreshToken(
        user_id=target_user.user_id,
        jti=jti,
        token_hash=hash_refresh_token(raw_refresh_token),
        expires_at=refresh_expires_at,
        created_ip=client_ip,
        user_agent=user_agent,
    )
    session.add(db_refresh)

    # 7. Write audit log entry
    audit_entry = ImpersonationAuditLog(
        audit_id=uuid.uuid4(),
        session_id=session_id,
        actor_admin_id=admin_user.user_id,
        target_user_id=target_user.user_id,
        action="IMPERSONATION_START",
        details={
            "target_employee_code": target_user.employee_code,
            "target_name": f"{target_user.first_name} {target_user.last_name}".strip(),
            "actor_employee_code": admin_user.employee_code,
            "actor_name": f"{admin_user.first_name} {admin_user.last_name}".strip(),
        },
        ip_address=client_ip,
        user_agent=user_agent,
        created_at=now,
    )
    session.add(audit_entry)
    session.commit()

    metadata = ImpersonationMetadata(
        session_id=session_id,
        actor_admin_id=admin_user.user_id,
        actor_name=f"{admin_user.first_name} {admin_user.last_name}".strip() or admin_user.employee_code,
        actor_employee_code=admin_user.employee_code,
        target_user_id=target_user.user_id,
        target_name=f"{target_user.first_name} {target_user.last_name}".strip() or target_user.employee_code,
        target_employee_code=target_user.employee_code,
        expires_at=expires_at,
    )

    return ImpersonationTokenResponse(
        access_token=access_token,
        refresh_token=raw_refresh_token,
        token_type="bearer",
        expires_in=1800,
        is_impersonated=True,
        impersonation=metadata,
    )


def get_impersonation_status(
    session: Session,
    token_payload: Dict[str, Any],
) -> ImpersonationStatusResponse:
    """Retrieve current impersonation metadata for the active session.

    Args:
        session: Active database session.
        token_payload: Decoded JWT claims dict.

    Returns:
        ImpersonationStatusResponse.
    """
    is_impersonated = bool(token_payload.get("is_impersonated", False))
    if not is_impersonated:
        return ImpersonationStatusResponse(is_impersonated=False, impersonation=None)

    if not settings.ENABLE_ADMIN_IMPERSONATION:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin impersonation feature is currently disabled.",
        )

    session_id_str = token_payload.get("impersonation_session_id")
    if not session_id_str:
        return ImpersonationStatusResponse(is_impersonated=False, impersonation=None)

    imp_session = session.get(ImpersonationSession, uuid.UUID(session_id_str))
    now = datetime.now(timezone.utc)
    if not imp_session or not imp_session.is_active or imp_session.expires_at < now:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Impersonation session has expired or been revoked.",
        )

    admin_user = session.get(User, imp_session.actor_admin_id)
    target_user = session.get(User, imp_session.target_user_id)

    if not admin_user or not target_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid impersonation user records.",
        )

    metadata = ImpersonationMetadata(
        session_id=imp_session.session_id,
        actor_admin_id=admin_user.user_id,
        actor_name=f"{admin_user.first_name} {admin_user.last_name}".strip() or admin_user.employee_code,
        actor_employee_code=admin_user.employee_code,
        target_user_id=target_user.user_id,
        target_name=f"{target_user.first_name} {target_user.last_name}".strip() or target_user.employee_code,
        target_employee_code=target_user.employee_code,
        expires_at=imp_session.expires_at,
    )

    return ImpersonationStatusResponse(
        is_impersonated=True,
        impersonation=metadata,
    )


def return_to_admin(
    session: Session,
    token_payload: Dict[str, Any],
    client_ip: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> ReturnToAdminResponse:
    """Terminate the active impersonation session and restore the Super Admin session.

    Args:
        session: Active database session.
        token_payload: Decoded claims of the impersonated JWT.
        client_ip: Client IP address.
        user_agent: Client user-agent.

    Returns:
        ReturnToAdminResponse with fresh Super Admin tokens.

    Raises:
        HTTPException: If token is not impersonated or original Admin session cannot be restored.
    """
    is_impersonated = bool(token_payload.get("is_impersonated", False))
    if not is_impersonated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not currently in an impersonated session.",
        )

    session_id_str = token_payload.get("impersonation_session_id")
    if not session_id_str:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing impersonation session identifier in token.",
        )

    imp_session = session.get(ImpersonationSession, uuid.UUID(session_id_str))
    if not imp_session or not imp_session.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Impersonation session is already expired or inactive.",
        )

    admin_user = session.get(User, imp_session.actor_admin_id)
    if not admin_user or admin_user.account_status != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Original Admin account is no longer active. Please log in normally.",
        )

    if not permissions.is_super_admin_user(session, admin_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Original account no longer possesses Super Admin privileges.",
        )

    now = datetime.now(timezone.utc)

    # 1. Invalidate impersonation session
    imp_session.is_active = False
    imp_session.ended_at = now
    imp_session.ended_reason = "RETURN_TO_ADMIN"

    # 2. Revoke the impersonation refresh token
    stmt_revoke = (
        update(RefreshToken)
        .where(
            RefreshToken.jti == imp_session.impersonation_token_jti,
            RefreshToken.revoked_at.is_(None),
        )
        .values(revoked_at=now)
    )
    session.execute(stmt_revoke)

    # 3. Write audit log
    audit_entry = ImpersonationAuditLog(
        audit_id=uuid.uuid4(),
        session_id=imp_session.session_id,
        actor_admin_id=admin_user.user_id,
        target_user_id=imp_session.target_user_id,
        action="IMPERSONATION_END",
        details={
            "reason": "RETURN_TO_ADMIN",
            "actor_employee_code": admin_user.employee_code,
        },
        ip_address=client_ip,
        user_agent=user_agent,
        created_at=now,
    )
    session.add(audit_entry)

    # 4. Generate fresh standard tokens for Super Admin
    admin_access_token = create_access_token(
        user_id=admin_user.user_id,
        token_version=admin_user.token_version,
    )
    admin_raw_refresh, admin_jti, admin_refresh_expires = create_refresh_token(
        user_id=admin_user.user_id,
        token_version=admin_user.token_version,
    )

    db_admin_refresh = RefreshToken(
        user_id=admin_user.user_id,
        jti=admin_jti,
        token_hash=hash_refresh_token(admin_raw_refresh),
        expires_at=admin_refresh_expires,
        created_ip=client_ip,
        user_agent=user_agent,
    )
    session.add(db_admin_refresh)
    session.commit()

    return ReturnToAdminResponse(
        access_token=admin_access_token,
        refresh_token=admin_raw_refresh,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        message="Successfully returned to Super Admin session",
    )


def end_impersonation_on_logout(
    session: Session,
    token_payload: Dict[str, Any],
    client_ip: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> None:
    """End the active impersonation session when logout is invoked.

    Args:
        session: Active database session.
        token_payload: Decoded JWT claims dict.
        client_ip: Optional client IP.
        user_agent: Optional user agent.
    """
    if not token_payload.get("is_impersonated"):
        return

    session_id_str = token_payload.get("impersonation_session_id")
    if not session_id_str:
        return

    try:
        session_id = uuid.UUID(session_id_str)
        imp_session = session.get(ImpersonationSession, session_id)
        if imp_session and imp_session.is_active:
            now = datetime.now(timezone.utc)
            imp_session.is_active = False
            imp_session.ended_at = now
            imp_session.ended_reason = "LOGOUT"

            # Revoke refresh token
            stmt_revoke = (
                update(RefreshToken)
                .where(
                    RefreshToken.jti == imp_session.impersonation_token_jti,
                    RefreshToken.revoked_at.is_(None),
                )
                .values(revoked_at=now)
            )
            session.execute(stmt_revoke)

            # Write audit
            audit_entry = ImpersonationAuditLog(
                audit_id=uuid.uuid4(),
                session_id=imp_session.session_id,
                actor_admin_id=imp_session.actor_admin_id,
                target_user_id=imp_session.target_user_id,
                action="IMPERSONATION_END",
                details={"reason": "LOGOUT"},
                ip_address=client_ip,
                user_agent=user_agent,
                created_at=now,
            )
            session.add(audit_entry)
            session.commit()
    except Exception:
        pass
