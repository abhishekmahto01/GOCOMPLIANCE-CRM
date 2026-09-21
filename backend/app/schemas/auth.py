"""Authentication Pydantic schemas."""
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class LoginRequest(BaseModel):
    """Schema for user login credentials."""

    identifier: str = Field(
        ...,
        min_length=2,
        max_length=255,
        description="Official email address or employee code (e.g. CG0001)",
    )
    password: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="User password",
    )

    @field_validator("identifier", mode="before")
    @classmethod
    def validate_identifier(cls, v: str) -> str:
        if isinstance(v, str):
            v = v.strip()
            if not v:
                raise ValueError("Identifier cannot be blank")
            return v
        return v


class TokenResponse(BaseModel):
    """Schema for JWT access and refresh token responses."""

    access_token: str = Field(..., description="Signed JWT access token")
    refresh_token: str = Field(..., description="Signed JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type specification")
    expires_in: int = Field(
        default=900,
        description="Access token expiration window in seconds",
    )
    must_change_password: bool = Field(
        default=False,
        description="Flag indicating if user must change password before full access",
    )


class RefreshTokenRequest(BaseModel):
    """Schema for requesting a new token pair with a refresh token."""

    refresh_token: str = Field(
        ...,
        min_length=10,
        description="Active signed JWT refresh token",
    )


class LogoutRequest(BaseModel):
    """Schema for logging out and revoking an active refresh token."""

    refresh_token: str = Field(
        ...,
        min_length=10,
        description="Refresh token to be revoked upon logout",
    )


class ChangePasswordRequest(BaseModel):
    """Schema for authenticated user password change."""

    current_password: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="Current account password for verification",
    )
    new_password: str = Field(
        ...,
        min_length=10,
        max_length=128,
        description="New password meeting complexity criteria",
    )


class ChangeInitialPasswordRequest(BaseModel):
    """Schema for mandatory first-login password change."""

    current_password: Optional[str] = Field(
        None,
        max_length=128,
        description="Current temporary password if supplied",
    )
    new_password: str = Field(
        ...,
        min_length=10,
        max_length=128,
        description="New password meeting complexity criteria",
    )
    confirm_password: Optional[str] = Field(
        None,
        max_length=128,
        description="Confirmation of new password",
    )


class DepartmentInfo(BaseModel):
    """Safe department information."""

    id: uuid.UUID
    code: str
    name: str

    model_config = ConfigDict(from_attributes=True)


class CompanyInfo(BaseModel):
    """Safe company information."""

    id: uuid.UUID
    code: str
    name: str

    model_config = ConfigDict(from_attributes=True)


class DesignationInfo(BaseModel):
    """Safe designation information."""

    id: uuid.UUID
    code: str
    name: str

    model_config = ConfigDict(from_attributes=True)


class CurrentUserRead(BaseModel):
    """Schema for currently authenticated user profile information (/api/auth/me)."""

    user_id: uuid.UUID
    employee_code: str
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    official_email: str
    personal_email: Optional[str] = None
    mobile_number: Optional[str] = None
    company_id: Optional[uuid.UUID] = None
    department_id: Optional[uuid.UUID] = None
    designation_id: Optional[uuid.UUID] = None
    manager_user_id: Optional[uuid.UUID] = None
    account_status: str
    must_change_password: bool
    is_hod: bool = False
    is_reporting_manager: bool = False
    primary_location: Optional[str] = None
    last_login_at: Optional[datetime] = None

    department_name: Optional[str] = None
    department_code: Optional[str] = None
    company_name: Optional[str] = None
    company_code: Optional[str] = None
    designation_name: Optional[str] = None
    designation_code: Optional[str] = None

    department: Optional[DepartmentInfo] = None
    company: Optional[CompanyInfo] = None
    designation: Optional[DesignationInfo] = None

    model_config = ConfigDict(from_attributes=True)
