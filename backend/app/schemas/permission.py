"""Pydantic schemas for User Module Permissions and Data Scopes."""
import uuid
from datetime import datetime, timezone
from typing import Optional, Set

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

VALID_DATA_SCOPES: Set[str] = {"SELF", "TEAM", "DEPARTMENT", "COMPANY", "ALL"}
VALID_PERMISSION_STATUSES: Set[str] = {"ACTIVE", "INACTIVE"}


class UserModulePermissionBase(BaseModel):
    """Base schema for per-user module permission."""

    can_view: bool = Field(
        default=False,
        description="Whether user can view module page and query records within scope",
    )
    can_create: bool = Field(
        default=False,
        description="Whether user can create records in module (requires can_view=true)",
    )
    can_edit: bool = Field(
        default=False,
        description="Whether user can edit records in module (requires can_view=true)",
    )
    can_delete: bool = Field(
        default=False,
        description="Whether user can delete/deactivate records in module (requires can_view=true)",
    )
    can_approve: bool = Field(
        default=False,
        description="Whether user can approve workflows in module (requires can_view=true)",
    )
    data_scope: str = Field(
        default="SELF",
        description="Data visibility scope: SELF, TEAM, DEPARTMENT, COMPANY, ALL",
    )
    status: str = Field(
        default="ACTIVE",
        description="Operational status: ACTIVE or INACTIVE",
    )
    expires_at: Optional[datetime] = Field(
        default=None,
        description="Optional future UTC timestamp when permission expires",
    )

    @field_validator("data_scope", mode="before")
    @classmethod
    def validate_data_scope(cls, value: str) -> str:
        """Validate and normalize data_scope."""
        if not isinstance(value, str):
            raise ValueError("Data scope must be a string")
        normalized = value.strip().upper()
        if normalized not in VALID_DATA_SCOPES:
            raise ValueError(
                f"Invalid data scope '{value}'. Must be one of: {sorted(VALID_DATA_SCOPES)}"
            )
        return normalized

    @field_validator("status", mode="before")
    @classmethod
    def validate_status(cls, value: str) -> str:
        """Validate and normalize status."""
        if not isinstance(value, str):
            raise ValueError("Status must be a string")
        normalized = value.strip().upper()
        if normalized not in VALID_PERMISSION_STATUSES:
            raise ValueError(
                f"Invalid status '{value}'. Must be one of: {sorted(VALID_PERMISSION_STATUSES)}"
            )
        return normalized

    @model_validator(mode="after")
    def validate_action_view_prerequisite(self) -> "UserModulePermissionBase":
        """Enforce that non-view action flags require can_view=true."""
        has_action = (
            self.can_create
            or self.can_edit
            or self.can_delete
            or self.can_approve
        )
        if has_action and not self.can_view:
            raise ValueError(
                "can_view must be true when can_create, can_edit, can_delete, or can_approve is enabled"
            )
        return self


class UserModulePermissionCreate(UserModulePermissionBase):
    """Schema for creating a new user module permission assignment."""

    user_id: uuid.UUID = Field(
        ...,
        description="Target user ID for permission grant",
    )
    module_id: uuid.UUID = Field(
        ...,
        description="Target module ID for permission grant",
    )

    @field_validator("expires_at")
    @classmethod
    def validate_future_expiry(cls, value: Optional[datetime]) -> Optional[datetime]:
        """Ensure expires_at is in the future if supplied."""
        if value is not None:
            now_utc = datetime.now(timezone.utc)
            val_utc = value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)
            if val_utc <= now_utc:
                raise ValueError("expires_at must be in the future")
        return value


class UserModulePermissionUpdate(BaseModel):
    """Schema for updating an existing user module permission."""

    can_view: Optional[bool] = Field(
        default=None,
        description="Updated can_view flag",
    )
    can_create: Optional[bool] = Field(
        default=None,
        description="Updated can_create flag",
    )
    can_edit: Optional[bool] = Field(
        default=None,
        description="Updated can_edit flag",
    )
    can_delete: Optional[bool] = Field(
        default=None,
        description="Updated can_delete flag",
    )
    can_approve: Optional[bool] = Field(
        default=None,
        description="Updated can_approve flag",
    )
    data_scope: Optional[str] = Field(
        default=None,
        description="Updated data visibility scope",
    )
    status: Optional[str] = Field(
        default=None,
        description="Updated status: ACTIVE or INACTIVE",
    )
    expires_at: Optional[datetime] = Field(
        default=None,
        description="Updated future expiration timestamp (or None to clear)",
    )

    @field_validator("data_scope", mode="before")
    @classmethod
    def validate_data_scope(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        if not isinstance(value, str):
            raise ValueError("Data scope must be a string")
        normalized = value.strip().upper()
        if normalized not in VALID_DATA_SCOPES:
            raise ValueError(
                f"Invalid data scope '{value}'. Must be one of: {sorted(VALID_DATA_SCOPES)}"
            )
        return normalized

    @field_validator("status", mode="before")
    @classmethod
    def validate_status(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        if not isinstance(value, str):
            raise ValueError("Status must be a string")
        normalized = value.strip().upper()
        if normalized not in VALID_PERMISSION_STATUSES:
            raise ValueError(
                f"Invalid status '{value}'. Must be one of: {sorted(VALID_PERMISSION_STATUSES)}"
            )
        return normalized

    @model_validator(mode="after")
    def validate_action_consistency(self) -> "UserModulePermissionUpdate":
        """If can_view is explicitly set to False, other flags cannot be explicitly True."""
        if self.can_view is False:
            if (
                self.can_create is True
                or self.can_edit is True
                or self.can_delete is True
                or self.can_approve is True
            ):
                raise ValueError(
                    "can_view cannot be false when other action flags are set to true"
                )
        return self


class UserModulePermissionRead(UserModulePermissionBase):
    """Schema for reading user module permission records."""

    permission_id: uuid.UUID
    user_id: uuid.UUID
    module_id: uuid.UUID
    granted_by_user_id: Optional[uuid.UUID] = None
    granted_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AccessibleModuleRead(BaseModel):
    """Schema representing an accessible module in UI navigation or authorization summary."""

    module_id: uuid.UUID
    module_code: str
    module_name: str
    parent_module_id: Optional[uuid.UUID] = None
    route: Optional[str] = None
    display_order: int
    is_navigation: bool
    can_view: bool
    can_create: bool
    can_edit: bool
    can_delete: bool
    can_approve: bool
    data_scope: str

    model_config = ConfigDict(from_attributes=True)
