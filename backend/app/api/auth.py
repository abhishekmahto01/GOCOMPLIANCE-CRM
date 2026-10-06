"""Authentication API routes."""
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.api.deps import (
    get_current_active_user,
    oauth2_scheme,
    require_fully_activated_user,
    require_super_admin,
)
from app.core.config import settings
from app.core.security import decode_and_validate_token
from app.database.session import get_db
from app.models.company import Company
from app.models.department import Department
from app.models.designation import Designation
from app.models.user import User
from app.schemas.auth import (
    ChangeInitialPasswordRequest,
    ChangePasswordRequest,
    CompanyInfo,
    CurrentUserRead,
    DepartmentInfo,
    DesignationInfo,
    LoginRequest,
    LogoutRequest,
    RefreshTokenRequest,
    TokenResponse,
)
from app.schemas.impersonation import (
    ImpersonateStartRequest,
    ImpersonationStatusResponse,
    ImpersonationTokenResponse,
    ReturnToAdminResponse,
)
from app.schemas.permission import AccessibleModuleRead, UserEffectivePermissionsResponse
from app.services import impersonation_service, permissions
from app.services.auth_service import (
    authenticate_user,
    change_user_password,
    logout_user,
    refresh_access_token,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="User Login",
    description="Authenticate with employee code or official email and password to receive JWT tokens.",
)
def login(
    login_data: LoginRequest,
    request: Request,
    session: Session = Depends(get_db),
) -> TokenResponse:
    """Authenticate user credentials and return signed access and refresh tokens."""
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    _, token_response = authenticate_user(
        session=session,
        identifier=login_data.identifier,
        password=login_data.password,
        client_ip=client_ip,
        user_agent=user_agent,
    )
    return token_response


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh Access Token",
    description="Rotate the provided refresh token and receive a new access and refresh token pair.",
)
def refresh_token(
    refresh_data: RefreshTokenRequest,
    request: Request,
    session: Session = Depends(get_db),
) -> TokenResponse:
    """Rotate refresh token and issue a fresh access token."""
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    return refresh_access_token(
        session=session,
        raw_refresh_token=refresh_data.refresh_token,
        client_ip=client_ip,
        user_agent=user_agent,
    )


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="User Logout",
    description="Revoke the supplied refresh token and any active impersonation session.",
)
def logout(
    logout_data: LogoutRequest,
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme),
    session: Session = Depends(get_db),
) -> Dict[str, str]:
    """Revoke refresh token and invalidate current session."""
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    if token:
        try:
            payload = decode_and_validate_token(token, expected_type="access")
            if payload.get("is_impersonated"):
                impersonation_service.end_impersonation_on_logout(
                    session=session,
                    token_payload=payload,
                    client_ip=client_ip,
                    user_agent=user_agent,
                )
        except Exception:
            pass

    logout_user(session=session, raw_refresh_token=logout_data.refresh_token)
    return {"message": "Successfully logged out"}


@router.post(
    "/impersonate",
    response_model=ImpersonationTokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Start Employee Impersonation",
    description="Allows an authenticated Super Admin to temporarily log in as a target employee.",
)
def start_impersonate(
    data: ImpersonateStartRequest,
    request: Request,
    current_user: User = Depends(require_super_admin),
    session: Session = Depends(get_db),
) -> ImpersonationTokenResponse:
    """Switch active context to target employee for Super Admin."""
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    return impersonation_service.start_impersonation(
        session=session,
        admin_user=current_user,
        employee_code=data.employee_code,
        client_ip=client_ip,
        user_agent=user_agent,
    )


@router.get(
    "/impersonate/status",
    response_model=ImpersonationStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Impersonation Status",
    description="Check whether the active bearer token is an impersonation session and return metadata.",
)
def get_impersonate_status(
    token: Optional[str] = Depends(oauth2_scheme),
    session: Session = Depends(get_db),
) -> ImpersonationStatusResponse:
    """Check if current session is impersonated."""
    if not token:
        return ImpersonationStatusResponse(is_impersonated=False)

    try:
        payload = decode_and_validate_token(token, expected_type="access")
        return impersonation_service.get_impersonation_status(
            session=session,
            token_payload=payload,
        )
    except Exception:
        return ImpersonationStatusResponse(is_impersonated=False)


@router.post(
    "/impersonate/exit",
    response_model=ReturnToAdminResponse,
    status_code=status.HTTP_200_OK,
    summary="Return to Super Admin Session",
    description="Terminate active impersonation session and restore originating Super Admin credentials.",
)
def exit_impersonate(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme),
    session: Session = Depends(get_db),
) -> ReturnToAdminResponse:
    """Restore Super Admin session from active impersonation."""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    payload = decode_and_validate_token(token, expected_type="access")
    return impersonation_service.return_to_admin(
        session=session,
        token_payload=payload,
        client_ip=client_ip,
        user_agent=user_agent,
    )


@router.post(
    "/impersonate/return",
    response_model=ReturnToAdminResponse,
    status_code=status.HTTP_200_OK,
    summary="Return to Super Admin Session (Alias)",
    description="Alias for /impersonate/exit.",
)
def return_impersonate(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme),
    session: Session = Depends(get_db),
) -> ReturnToAdminResponse:
    """Alias for exit_impersonate."""
    return exit_impersonate(request=request, token=token, session=session)


@router.get(
    "/me",
    response_model=CurrentUserRead,
    status_code=status.HTTP_200_OK,
    summary="Get Current User Profile",
    description="Retrieve the authenticated employee's safe profile details.",
)
def get_current_user_profile(
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
) -> CurrentUserRead:
    """Return identity and organizational details of the authenticated user."""
    dept = session.get(Department, current_user.department_id) if current_user.department_id else None
    comp = session.get(Company, current_user.company_id) if current_user.company_id else None
    desig = session.get(Designation, current_user.designation_id) if current_user.designation_id else None

    dept_info = (
        DepartmentInfo(
            id=dept.department_id,
            code=dept.department_code,
            name=dept.department_name,
        )
        if dept
        else None
    )
    comp_info = (
        CompanyInfo(
            id=comp.company_id,
            code=comp.company_code,
            name=comp.company_name,
        )
        if comp
        else None
    )
    desig_info = (
        DesignationInfo(
            id=desig.designation_id,
            code=desig.designation_code,
            name=desig.designation_name,
        )
        if desig
        else None
    )

    return CurrentUserRead(
        user_id=current_user.user_id,
        employee_code=current_user.employee_code,
        first_name=current_user.first_name,
        middle_name=current_user.middle_name,
        last_name=current_user.last_name,
        official_email=current_user.official_email,
        personal_email=current_user.personal_email,
        mobile_number=current_user.mobile_number,
        company_id=current_user.company_id,
        department_id=current_user.department_id,
        designation_id=current_user.designation_id,
        manager_user_id=current_user.manager_user_id,
        account_status=current_user.account_status,
        must_change_password=current_user.must_change_password,
        is_hod=bool(getattr(current_user, "is_hod", False)),
        is_reporting_manager=bool(getattr(current_user, "is_reporting_manager", False)),
        primary_location=getattr(current_user, "primary_location", None),
        last_login_at=current_user.last_login_at,
        department_name=dept.department_name if dept else None,
        department_code=dept.department_code if dept else None,
        company_name=comp.company_name if comp else None,
        company_code=comp.company_code if comp else None,
        designation_name=desig.designation_name if desig else None,
        designation_code=desig.designation_code if desig else None,
        department=dept_info,
        company=comp_info,
        designation=desig_info,
    )



@router.get(
    "/me/modules",
    response_model=List[AccessibleModuleRead],
    status_code=status.HTTP_200_OK,
    summary="Get Current User Accessible Modules",
    description="Retrieve the list of accessible modules and granular action permissions for the authenticated employee.",
)
def get_current_user_modules(
    current_user: User = Depends(require_fully_activated_user),
    session: Session = Depends(get_db),
) -> List[AccessibleModuleRead]:
    """Return navigation hierarchy and permission flags for the authenticated user."""
    return permissions.get_accessible_modules(session, current_user.user_id)


@router.get(
    "/me/permissions",
    response_model=UserEffectivePermissionsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Current User Effective Permissions Bundle",
    description="Retrieve the effective permission slugs mapping and accessible pages for the authenticated employee.",
)
def get_current_user_effective_permissions(
    current_user: User = Depends(require_fully_activated_user),
    session: Session = Depends(get_db),
) -> UserEffectivePermissionsResponse:
    """Return effective permission slugs map and accessible pages for the authenticated user."""
    return permissions.get_user_effective_permissions_bundle(session, current_user.user_id)


@router.post(
    "/change-password",
    status_code=status.HTTP_200_OK,
    summary="Change Password",
    description="Change password for the authenticated user and invalidate all active sessions.",
)
def change_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
) -> Dict[str, str]:
    """Update password, clear must_change_password flag, and revoke all sessions."""
    change_user_password(
        session=session,
        user=current_user,
        current_password=password_data.current_password,
        new_password=password_data.new_password,
    )
    return {
        "message": "Password changed successfully. All active sessions have been terminated. Please log in with your new password."
    }


@router.post(
    "/change-initial-password",
    status_code=status.HTTP_200_OK,
    summary="Change Initial Password",
    description="Mandatory first-login password change for newly initialized accounts.",
)
def change_initial_password(
    password_data: ChangeInitialPasswordRequest,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
) -> Dict[str, str]:
    """Change temporary password on mandatory first login."""
    if password_data.confirm_password and password_data.new_password != password_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password and password confirmation do not match",
        )

    current_pwd = password_data.current_password or (settings.TRIAL_DEFAULT_PASSWORD or "12345")
    change_user_password(
        session=session,
        user=current_user,
        current_password=current_pwd,
        new_password=password_data.new_password,
    )
    return {
        "message": "Password changed successfully. All active sessions have been terminated. Please log in with your new password."
    }

