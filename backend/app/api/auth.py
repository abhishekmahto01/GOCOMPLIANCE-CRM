"""Authentication API routes."""
from typing import Dict, List

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.auth import (
    ChangePasswordRequest,
    CurrentUserRead,
    LoginRequest,
    LogoutRequest,
    RefreshTokenRequest,
    TokenResponse,
)
from app.schemas.permission import AccessibleModuleRead
from app.services import permissions
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
    description="Revoke the supplied refresh token to terminate the session.",
)
def logout(
    logout_data: LogoutRequest,
    session: Session = Depends(get_db),
) -> Dict[str, str]:
    """Revoke refresh token and invalidate current session."""
    logout_user(session=session, raw_refresh_token=logout_data.refresh_token)
    return {"message": "Successfully logged out"}


@router.get(
    "/me",
    response_model=CurrentUserRead,
    status_code=status.HTTP_200_OK,
    summary="Get Current User Profile",
    description="Retrieve the authenticated employee's safe profile details.",
)
def get_current_user_profile(
    current_user: User = Depends(get_current_active_user),
) -> CurrentUserRead:
    """Return identity and organizational details of the authenticated user."""
    return CurrentUserRead.model_validate(current_user)


@router.get(
    "/me/modules",
    response_model=List[AccessibleModuleRead],
    status_code=status.HTTP_200_OK,
    summary="Get Current User Accessible Modules",
    description="Retrieve the list of accessible modules and granular action permissions for the authenticated employee.",
)
def get_current_user_modules(
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_db),
) -> List[AccessibleModuleRead]:
    """Return navigation hierarchy and permission flags for the authenticated user."""
    return permissions.get_accessible_modules(session, current_user.user_id)


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
