"""Pydantic schemas for User Module Permissions, Page-wise Permissions Catalog and Data Scopes."""
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

VALID_DATA_SCOPES: Set[str] = {"SELF", "TEAM", "DEPARTMENT", "COMPANY", "ALL"}
VALID_PERMISSION_STATUSES: Set[str] = {"ACTIVE", "INACTIVE"}

# All supported granular action names across the system
ALL_SUPPORTED_ACTIONS: Set[str] = {
    "read",
    "write",
    "create",
    "update",
    "edit",
    "delete",
    "assign",
    "reassign",
    "export",
    "approve",
}


class UserModulePermissionBase(BaseModel):
    """Base schema for per-user module/page permission."""

    can_view: bool = Field(
        default=False,
        description="Whether user can view module page and query records within scope (Read)",
    )
    can_create: bool = Field(
        default=False,
        description="Whether user can create records in module (Write/Create, requires can_view=true)",
    )
    can_edit: bool = Field(
        default=False,
        description="Whether user can edit records in module (Update, requires can_view=true)",
    )
    can_delete: bool = Field(
        default=False,
        description="Whether user can delete/deactivate records in module (requires can_view=true)",
    )
    can_approve: bool = Field(
        default=False,
        description="Whether user can approve workflows in module (requires can_view=true)",
    )
    can_assign: bool = Field(
        default=False,
        description="Whether user can assign orders/tasks (requires can_view=true)",
    )
    can_reassign: bool = Field(
        default=False,
        description="Whether user can reassign orders/tasks (requires can_view=true)",
    )
    can_export: bool = Field(
        default=False,
        description="Whether user can export records/reports (requires can_view=true)",
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
            or self.can_assign
            or self.can_reassign
            or self.can_export
        )
        if has_action and not self.can_view:
            raise ValueError(
                "can_view must be true when create, edit, delete, approve, assign, reassign, or export is enabled"
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
        description="Updated can_view flag (Read)",
    )
    can_create: Optional[bool] = Field(
        default=None,
        description="Updated can_create flag (Write/Create)",
    )
    can_edit: Optional[bool] = Field(
        default=None,
        description="Updated can_edit flag (Update)",
    )
    can_delete: Optional[bool] = Field(
        default=None,
        description="Updated can_delete flag (Delete)",
    )
    can_approve: Optional[bool] = Field(
        default=None,
        description="Updated can_approve flag",
    )
    can_assign: Optional[bool] = Field(
        default=None,
        description="Updated can_assign flag (Assign)",
    )
    can_reassign: Optional[bool] = Field(
        default=None,
        description="Updated can_reassign flag (Reassign)",
    )
    can_export: Optional[bool] = Field(
        default=None,
        description="Updated can_export flag (Export)",
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
                or self.can_assign is True
                or self.can_reassign is True
                or self.can_export is True
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
    can_assign: bool = False
    can_reassign: bool = False
    can_export: bool = False
    data_scope: str

    model_config = ConfigDict(from_attributes=True)


# ==============================================================================
# Catalog & Granular Page-Action Schemas
# ==============================================================================

class CatalogPageItem(BaseModel):
    """Catalog metadata for an individual page inside a module."""

    page_code: str
    page_name: str
    route: Optional[str] = None
    supported_actions: List[str]
    action_slugs: Dict[str, str]
    display_order: int


class CatalogModuleItem(BaseModel):
    """Catalog metadata for a root module containing pages."""

    module_code: str
    module_name: str
    pages: List[CatalogPageItem]


class PermissionCatalogResponse(BaseModel):
    """Full catalog response containing Sales and Operation modules and pages."""

    modules: List[CatalogModuleItem]


class PageActionPermission(BaseModel):
    """Granular action permissions assigned to a specific page."""

    page_code: str
    can_view: bool = False       # Read
    can_create: bool = False     # Write / Create
    can_edit: bool = False       # Update
    can_delete: bool = False     # Delete
    can_assign: bool = False     # Assign
    can_reassign: bool = False   # Reassign
    can_export: bool = False     # Export
    can_approve: bool = False    # Approve
    data_scope: str = "SELF"
    status: str = "ACTIVE"

    @field_validator("page_code", mode="before")
    @classmethod
    def normalize_page_code(cls, v: str) -> str:
        return v.strip().upper()

    @field_validator("data_scope", mode="before")
    @classmethod
    def normalize_scope(cls, v: str) -> str:
        s = v.strip().upper() if isinstance(v, str) else "SELF"
        if s not in VALID_DATA_SCOPES:
            raise ValueError(f"Invalid data scope '{v}'")
        return s


class UserSettingsUpdate(BaseModel):
    """User-level settings update schema."""

    is_active: Optional[bool] = None
    is_hod: Optional[bool] = None
    is_reporting_manager: Optional[bool] = None
    manager_user_id: Optional[uuid.UUID] = None
    primary_location: Optional[str] = None


class UserPermissionsDetailResponse(BaseModel):
    """Complete permissions and user settings bundle for an employee."""

    user_id: uuid.UUID
    employee_code: str
    first_name: str
    last_name: str
    official_email: str
    company_id: uuid.UUID
    company_name: Optional[str] = None
    department_id: uuid.UUID
    department_name: Optional[str] = None
    designation_id: uuid.UUID
    designation_name: Optional[str] = None
    is_active: bool
    is_hod: bool
    is_reporting_manager: bool
    manager_user_id: Optional[uuid.UUID] = None
    manager_name: Optional[str] = None
    primary_location: Optional[str] = None
    permissions: List[PageActionPermission]


class UserPermissionsSaveRequest(BaseModel):
    """Payload for saving an employee's permissions and user settings."""

    permissions: List[PageActionPermission]
    user_settings: Optional[UserSettingsUpdate] = None


class CopyPermissionsRequest(BaseModel):
    """Payload for copying permissions from a source employee."""

    source_user_id: uuid.UUID


class CopyPermissionsResponse(BaseModel):
    """Response returned after copying permissions."""

    message: str
    copied_count: int
    source_user_id: uuid.UUID
    target_user_id: uuid.UUID


class UserEffectivePermissionsResponse(BaseModel):
    """Effective permissions bundle for the currently logged-in user."""

    user_id: uuid.UUID
    employee_code: str
    official_email: str
    first_name: str
    last_name: str
    company_id: uuid.UUID
    department_id: uuid.UUID
    permissions: Dict[str, bool]  # Slug -> True/False (e.g., "sales.dashboard.read": True)
    accessible_pages: List[AccessibleModuleRead]
