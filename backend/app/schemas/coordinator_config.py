"""Pydantic schemas for Operations Coordinator Configuration."""
import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class OperationsCoordinatorConfigRead(BaseModel):
    """Schema for reading an operations coordinator configuration."""

    config_id: uuid.UUID
    company_id: uuid.UUID
    company_name: str
    company_code: str
    coordinator_user_id: Optional[uuid.UUID] = None
    coordinator_name: Optional[str] = None
    coordinator_employee_code: Optional[str] = None
    coordinator_email: Optional[str] = None
    coordinator_department_name: Optional[str] = None
    updated_by_user_id: Optional[uuid.UUID] = None
    updated_by_name: Optional[str] = None
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OperationsCoordinatorConfigUpdate(BaseModel):
    """Schema for updating a company's default operations coordinator."""

    coordinator_user_id: Optional[uuid.UUID] = Field(
        None,
        description="User ID of the eligible Operations coordinator (or None to unassign)",
    )


class EligibleCoordinatorOption(BaseModel):
    """Option representing an active employee eligible to be an Operations coordinator."""

    user_id: uuid.UUID
    employee_code: str
    full_name: str
    email: str
    company_id: uuid.UUID
    company_name: str
    company_code: str
    department_name: Optional[str] = None
    designation_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
