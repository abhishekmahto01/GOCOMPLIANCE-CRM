"""Pydantic schemas for Service Master and Document Requirements."""
import uuid
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ServiceRequiredDocBase(BaseModel):
    """Base schema for service document requirement."""

    document_code: str = Field(..., min_length=2, max_length=60, description="System document code")
    document_name: str = Field(..., min_length=2, max_length=150, description="Document display name")
    is_mandatory: bool = Field(default=True, description="Mandatory for filing")
    display_order: int = Field(default=0, ge=0, description="Display sorting order")

    @field_validator("document_code", mode="before")
    @classmethod
    def normalize_doc_code(cls, v: str) -> str:
        if isinstance(v, str):
            v = v.strip().upper()
            if not v:
                raise ValueError("document_code cannot be empty")
        return v


class ServiceRequiredDocCreate(ServiceRequiredDocBase):
    """Schema for adding document requirement."""
    pass


class ServiceRequiredDocRead(ServiceRequiredDocBase):
    """Read schema for document requirement."""
    doc_config_id: uuid.UUID
    service_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ServiceBase(BaseModel):
    """Base schema for Service Master."""

    service_code: str = Field(..., min_length=2, max_length=60, description="Unique uppercase service code")
    service_name: str = Field(..., min_length=2, max_length=150, description="Display name of the service")
    category: str = Field(..., min_length=2, max_length=50, description="LICENCE, REGISTRATION, INCORPORATION, COMPLIANCE")
    description: Optional[str] = Field(None, max_length=500)
    base_price: Decimal = Field(default=Decimal("0.00"), ge=0, description="Base service fee in INR")
    govt_fee: Decimal = Field(default=Decimal("0.00"), ge=0, description="Estimated government fee in INR")
    standard_turnaround_days: int = Field(default=15, gt=0, description="Turnaround SLA in days")
    status: str = Field(default="ACTIVE", description="ACTIVE or INACTIVE")

    @field_validator("service_code", mode="before")
    @classmethod
    def normalize_service_code(cls, v: str) -> str:
        if isinstance(v, str):
            v = v.strip().upper()
            if not v:
                raise ValueError("service_code cannot be empty")
        return v

    @field_validator("category", mode="before")
    @classmethod
    def normalize_category(cls, v: str) -> str:
        if isinstance(v, str):
            v = v.strip().upper()
        return v


class ServiceCreate(ServiceBase):
    """Schema for creating a new service."""
    required_documents: Optional[List[ServiceRequiredDocCreate]] = Field(default_factory=list)


class ServiceUpdate(BaseModel):
    """Schema for updating an existing service."""

    service_name: Optional[str] = Field(None, min_length=2, max_length=150)
    category: Optional[str] = Field(None, min_length=2, max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    base_price: Optional[Decimal] = Field(None, ge=0)
    govt_fee: Optional[Decimal] = Field(None, ge=0)
    standard_turnaround_days: Optional[int] = Field(None, gt=0)
    status: Optional[str] = Field(None)


class ServiceRead(ServiceBase):
    """Lightweight read schema for Service."""
    service_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ServiceDetailRead(ServiceRead):
    """Detailed read schema with required document checklist."""
    required_documents: List[ServiceRequiredDocRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
