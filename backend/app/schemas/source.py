"""Pydantic schemas for Source Master."""
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class SourceCreate(BaseModel):
    """Schema for creating a new lead source in Source Master."""
    source_code: str = Field(..., min_length=2, max_length=50, description="Unique code, e.g. GOOGLE_ADS")
    source_name: str = Field(..., min_length=2, max_length=100, description="Display name, e.g. Google Ads")
    description: Optional[str] = Field(None, max_length=500, description="Optional description")
    status: str = Field(default="ACTIVE", description="ACTIVE or INACTIVE")

    @field_validator("source_code", mode="before")
    @classmethod
    def normalize_code(cls, v: str) -> str:
        if isinstance(v, str):
            v = v.strip().upper().replace(" ", "_").replace("-", "_")
        return v

    @field_validator("source_name", mode="before")
    @classmethod
    def normalize_name(cls, v: str) -> str:
        if isinstance(v, str):
            v = v.strip()
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        v_upper = v.strip().upper()
        if v_upper not in ("ACTIVE", "INACTIVE"):
            raise ValueError("Status must be ACTIVE or INACTIVE")
        return v_upper


class SourceUpdate(BaseModel):
    """Schema for updating an existing source."""
    source_name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    status: Optional[str] = Field(None)

    @field_validator("source_name", mode="before")
    @classmethod
    def normalize_name(cls, v: Optional[str]) -> Optional[str]:
        if isinstance(v, str):
            v = v.strip()
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v_upper = v.strip().upper()
            if v_upper not in ("ACTIVE", "INACTIVE"):
                raise ValueError("Status must be ACTIVE or INACTIVE")
            return v_upper
        return v


class SourceRead(BaseModel):
    """Schema for returning source details."""
    model_config = ConfigDict(from_attributes=True)

    source_id: uuid.UUID
    source_code: str
    source_name: str
    description: Optional[str] = None
    status: str
    is_system: bool
    created_at: datetime
    updated_at: datetime

