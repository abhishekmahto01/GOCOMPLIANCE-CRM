"""Pydantic schemas for Department entity."""
import re
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class DepartmentBase(BaseModel):
    """Base schema with common Department fields."""

    company_id: uuid.UUID = Field(
        ...,
        description="Foreign key ID of the parent company",
    )
    department_code: str = Field(
        ...,
        min_length=2,
        max_length=30,
        description="Uppercase department code unique per company (e.g. ADMINISTRATION, SALES)",
    )
    department_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Display name of the department (e.g. Administration, Sales, R&D)",
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Optional description of the department",
    )
    status: str = Field(
        default="ACTIVE",
        description="Operational status (ACTIVE or INACTIVE)",
    )

    @field_validator("department_code", mode="before")
    @classmethod
    def normalize_department_code(cls, v: str) -> str:
        if isinstance(v, str):
            v = v.strip().upper()
            if not re.match(r"^[A-Z_]+$", v):
                raise ValueError(
                    "department_code must contain only uppercase letters and underscores (A-Z, _)"
                )
            return v
        return v

    @field_validator("department_name", mode="before")
    @classmethod
    def normalize_department_name(cls, v: str) -> str:
        if isinstance(v, str):
            v = v.strip()
            if not v:
                raise ValueError("department_name cannot be blank")
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
            if v not in {"ACTIVE", "INACTIVE"}:
                raise ValueError("status must be either 'ACTIVE' or 'INACTIVE'")
            return v
        return v


class DepartmentCreate(DepartmentBase):
    """Schema for creating a new Department."""
    pass


class DepartmentUpdate(BaseModel):
    """Schema for updating an existing Department."""

    department_name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    status: Optional[str] = None

    @field_validator("department_name", mode="before")
    @classmethod
    def normalize_department_name(cls, v: Optional[str]) -> Optional[str]:
        if isinstance(v, str):
            v = v.strip()
            if not v:
                raise ValueError("department_name cannot be blank")
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
            if v not in {"ACTIVE", "INACTIVE"}:
                raise ValueError("status must be either 'ACTIVE' or 'INACTIVE'")
            return v
        return v


class DepartmentRead(DepartmentBase):
    """Schema for reading Department data from API / database."""

    department_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
