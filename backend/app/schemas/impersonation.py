"""Pydantic schemas for Admin Impersonation ("Login as Employee")."""
from datetime import datetime
from typing import Optional
import uuid

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ImpersonateStartRequest(BaseModel):
    """Payload to initiate employee impersonation."""

    employee_code: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Target employee code (e.g. CG0004)",
    )

    @field_validator("employee_code", mode="before")
    @classmethod
    def clean_employee_code(cls, v: str) -> str:
        if isinstance(v, str):
            v = v.strip().upper()
            if not v:
                raise ValueError("Employee code cannot be blank")
            return v
        return v


class ImpersonationMetadata(BaseModel):
    """Metadata details about the active impersonation session."""

    model_config = ConfigDict(from_attributes=True)

    session_id: uuid.UUID
    actor_admin_id: uuid.UUID
    actor_name: str
    actor_employee_code: str
    target_user_id: uuid.UUID
    target_name: str
    target_employee_code: str
    expires_at: datetime


class ImpersonationTokenResponse(BaseModel):
    """Response returned upon successful impersonation initiation."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    is_impersonated: bool = True
    impersonation: ImpersonationMetadata


class ImpersonationStatusResponse(BaseModel):
    """Status check response for active session."""

    is_impersonated: bool
    impersonation: Optional[ImpersonationMetadata] = None


class ReturnToAdminResponse(BaseModel):
    """Response returned when restoring Super Admin session."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    message: str = "Successfully returned to Super Admin session"
