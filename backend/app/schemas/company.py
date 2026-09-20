"""Pydantic schemas for Company entity."""
import re
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CompanyBase(BaseModel):
    """Base schema with common Company fields."""

    company_code: str = Field(
        ...,
        min_length=2,
        max_length=20,
        description="Unique business identifier code (e.g. GOCOMPLIANCES)",
    )
    company_name: str = Field(
        ...,
        min_length=2,
        max_length=150,
        description="Primary display name of the company",
    )
    legal_name: Optional[str] = Field(
        None,
        max_length=200,
        description="Registered legal/corporate name",
    )
    employee_code_prefix: str = Field(
        ...,
        min_length=2,
        max_length=5,
        description="2-5 character uppercase prefix for employee IDs (e.g. CG, EP, BM)",
    )
    next_employee_number: int = Field(
        default=1,
        gt=0,
        description="Next sequential employee number (must be > 0)",
    )
    status: str = Field(
        default="ACTIVE",
        description="Operational status (ACTIVE or INACTIVE)",
    )

    @field_validator("company_code", mode="before")
    @classmethod
    def normalize_company_code(cls, v: str) -> str:
        if isinstance(v, str):
            v = v.strip().upper()
            if not v:
                raise ValueError("company_code cannot be empty")
            return v
        return v

    @field_validator("company_name", mode="before")
    @classmethod
    def normalize_company_name(cls, v: str) -> str:
        if isinstance(v, str):
            v = v.strip()
            if not v:
                raise ValueError("company_name cannot be empty")
            return v
        return v

    @field_validator("legal_name", mode="before")
    @classmethod
    def normalize_legal_name(cls, v: Optional[str]) -> Optional[str]:
        if isinstance(v, str):
            v = v.strip()
            return v if v else None
        return v

    @field_validator("employee_code_prefix", mode="before")
    @classmethod
    def normalize_employee_code_prefix(cls, v: str) -> str:
        if isinstance(v, str):
            v = v.strip().upper()
            if not re.match(r"^[A-Z]{2,5}$", v):
                raise ValueError(
                    "employee_code_prefix must consist of 2 to 5 uppercase letters (A-Z)"
                )
            return v
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


class CompanyCreate(CompanyBase):
    """Schema for creating a new Company."""
    pass


class CompanyUpdate(BaseModel):
    """Schema for updating an existing Company."""

    company_name: Optional[str] = Field(None, min_length=2, max_length=150)
    legal_name: Optional[str] = Field(None, max_length=200)
    status: Optional[str] = None

    @field_validator("company_name", mode="before")
    @classmethod
    def normalize_company_name(cls, v: Optional[str]) -> Optional[str]:
        if isinstance(v, str):
            v = v.strip()
            return v if v else None
        return v

    @field_validator("legal_name", mode="before")
    @classmethod
    def normalize_legal_name(cls, v: Optional[str]) -> Optional[str]:
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


class CompanyRead(CompanyBase):
    """Schema for reading Company data from API / database."""

    company_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
