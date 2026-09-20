"""Pydantic schemas for Designation entity."""
import re
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class DesignationBase(BaseModel):
    """Base schema with common Designation fields."""

    company_id: uuid.UUID = Field(
        ...,
        description="Foreign key ID of the parent company",
    )
    designation_code: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Uppercase designation code unique per company (e.g. EXECUTIVE, MANAGER)",
    )
    designation_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Display job title of the designation (e.g. Executive, Manager, Director)",
    )
    level_rank: int = Field(
        ...,
        gt=0,
        description="Seniority rank (>0; lower number = lower seniority)",
    )
    is_managerial: bool = Field(
        default=False,
        description="Managerial position indicator (informational only; does not grant permissions)",
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Optional description of designation responsibilities",
    )
    status: str = Field(
        default="ACTIVE",
        description="Operational status (ACTIVE or INACTIVE)",
    )

    @field_validator("designation_code", mode="before")
    @classmethod
    def normalize_designation_code(cls, v: str) -> str:
        if isinstance(v, str):
            v = v.strip().upper()
            if not re.match(r"^[A-Z_]+$", v):
                raise ValueError(
                    "designation_code must contain only uppercase letters and underscores (A-Z, _)"
                )
            return v
        return v

    @field_validator("designation_name", mode="before")
    @classmethod
    def normalize_designation_name(cls, v: str) -> str:
        if isinstance(v, str):
            v = v.strip()
            if not v:
                raise ValueError("designation_name cannot be blank")
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


class DesignationCreate(DesignationBase):
    """Schema for creating a new Designation."""
    pass


class DesignationUpdate(BaseModel):
    """Schema for updating an existing Designation."""

    designation_name: Optional[str] = Field(None, min_length=1, max_length=100)
    level_rank: Optional[int] = Field(None, gt=0)
    is_managerial: Optional[bool] = None
    description: Optional[str] = Field(None, max_length=500)
    status: Optional[str] = None

    @field_validator("designation_name", mode="before")
    @classmethod
    def normalize_designation_name(cls, v: Optional[str]) -> Optional[str]:
        if isinstance(v, str):
            v = v.strip()
            if not v:
                raise ValueError("designation_name cannot be blank")
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


class DesignationRead(DesignationBase):
    """Schema for reading Designation data from API / database."""

    designation_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
