"""Pydantic schemas for Client Master entity."""
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class ClientBase(BaseModel):
    """Base schema for client fields."""

    company_id: uuid.UUID
    client_name: str = Field(..., min_length=2, max_length=200, description="Business / client name")
    entity_type: str = Field(..., min_length=2, max_length=50, description="Entity type")
    contact_person: str = Field(..., min_length=2, max_length=150, description="Contact person name")
    contact_email: EmailStr = Field(..., description="Contact email address")
    contact_phone: str = Field(..., min_length=7, max_length=20, description="Contact telephone/mobile number")
    pan_number: Optional[str] = Field(None, max_length=20)
    gstin: Optional[str] = Field(None, max_length=20)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    status: str = Field(default="ACTIVE", description="ACTIVE or INACTIVE")

    @field_validator("client_name", "contact_person", mode="before")
    @classmethod
    def strip_strings(cls, v: str) -> str:
        if isinstance(v, str):
            v = v.strip()
            if not v:
                raise ValueError("Value cannot be empty")
        return v

    @field_validator("pan_number", "gstin", mode="before")
    @classmethod
    def normalize_tax_ids(cls, v: Optional[str]) -> Optional[str]:
        if isinstance(v, str):
            v = v.strip().upper()
            return v if v else None
        return v


class ClientCreate(ClientBase):
    """Schema for client creation."""
    pass


class ClientUpdate(BaseModel):
    """Schema for updating an existing client."""

    client_name: Optional[str] = Field(None, min_length=2, max_length=200)
    entity_type: Optional[str] = Field(None, min_length=2, max_length=50)
    contact_person: Optional[str] = Field(None, min_length=2, max_length=150)
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = Field(None, min_length=7, max_length=20)
    pan_number: Optional[str] = Field(None, max_length=20)
    gstin: Optional[str] = Field(None, max_length=20)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    status: Optional[str] = None


class ClientRead(ClientBase):
    """Read schema for Client."""
    client_id: uuid.UUID
    created_by_user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
