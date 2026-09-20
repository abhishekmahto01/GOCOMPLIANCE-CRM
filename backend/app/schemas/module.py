"""Pydantic schemas for Module entity."""
import re
import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

MODULE_CODE_REGEX = re.compile(r"^[A-Z_]+$")
ALLOWED_STATUSES = {"ACTIVE", "INACTIVE"}


class ModuleBase(BaseModel):
    """Base schema with common Module fields."""

    module_code: str = Field(
        ...,
        min_length=2,
        max_length=60,
        description="Uppercase unique system identifier (e.g. ADMIN, ADMIN_COMPANIES)",
    )
    module_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Display name of the module",
    )
    parent_module_id: Optional[uuid.UUID] = Field(
        None,
        description="Foreign key ID of the parent module (null for top-level modules)",
    )
    route: Optional[str] = Field(
        None,
        max_length=200,
        description="Frontend route path starting with '/' (e.g. /admin/companies)",
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Optional description of the module features",
    )
    display_order: int = Field(
        default=0,
        ge=0,
        description="Sorting order index (>= 0)",
    )
    is_navigation: bool = Field(
        default=True,
        description="Flag determining if module appears in UI navigation",
    )
    status: str = Field(
        default="ACTIVE",
        description="Operational status (ACTIVE or INACTIVE)",
    )

    @field_validator("module_code", mode="before")
    @classmethod
    def validate_module_code(cls, v: str) -> str:
        if isinstance(v, str):
            v = v.strip().upper()
            if not MODULE_CODE_REGEX.match(v):
                raise ValueError(
                    "module_code must contain only uppercase letters and underscores (A-Z, _)"
                )
            return v
        return v

    @field_validator("module_name", mode="before")
    @classmethod
    def validate_module_name(cls, v: str) -> str:
        if isinstance(v, str):
            v = v.strip()
            if not v:
                raise ValueError("module_name cannot be blank")
            return v
        return v

    @field_validator("route", mode="before")
    @classmethod
    def validate_route(cls, v: Optional[str]) -> Optional[str]:
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return None
            if not v.startswith("/"):
                raise ValueError("route must start with a forward slash ('/')")
            return v
        return v

    @field_validator("description", mode="before")
    @classmethod
    def normalize_description(cls, v: Optional[str]) -> Optional[str]:
        if isinstance(v, str):
            v = v.strip()
            return v if v else None
        return v

    @field_validator("status", mode="before")
    @classmethod
    def validate_status(cls, v: str) -> str:
        if isinstance(v, str):
            v = v.strip().upper()
            if v not in ALLOWED_STATUSES:
                raise ValueError(
                    f"status must be one of: {', '.join(sorted(ALLOWED_STATUSES))}"
                )
            return v
        return v


class ModuleCreate(ModuleBase):
    """Schema for creating a new Module."""
    pass


class ModuleUpdate(BaseModel):
    """Schema for updating an existing Module."""

    module_name: Optional[str] = Field(None, min_length=1, max_length=100)
    parent_module_id: Optional[uuid.UUID] = None
    route: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    display_order: Optional[int] = Field(None, ge=0)
    is_navigation: Optional[bool] = None
    status: Optional[str] = None

    @field_validator("module_name", mode="before")
    @classmethod
    def validate_module_name(cls, v: Optional[str]) -> Optional[str]:
        if isinstance(v, str):
            v = v.strip()
            if not v:
                raise ValueError("module_name cannot be blank")
            return v
        return v

    @field_validator("route", mode="before")
    @classmethod
    def validate_route(cls, v: Optional[str]) -> Optional[str]:
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return None
            if not v.startswith("/"):
                raise ValueError("route must start with a forward slash ('/')")
            return v
        return v

    @field_validator("description", mode="before")
    @classmethod
    def normalize_description(cls, v: Optional[str]) -> Optional[str]:
        if isinstance(v, str):
            v = v.strip()
            return v if v else None
        return v

    @field_validator("status", mode="before")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if isinstance(v, str):
            v = v.strip().upper()
            if v not in ALLOWED_STATUSES:
                raise ValueError(
                    f"status must be one of: {', '.join(sorted(ALLOWED_STATUSES))}"
                )
            return v
        return v


class ModuleRead(ModuleBase):
    """Schema for reading Module data from API / database."""

    module_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ModuleTreeRead(ModuleRead):
    """Schema for hierarchical recursive representation of a module and its children."""

    children: List["ModuleTreeRead"] = []

    model_config = ConfigDict(from_attributes=True)
