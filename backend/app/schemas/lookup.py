"""Pydantic schemas for Admin Lookup endpoints."""
import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CompanyLookupRead(BaseModel):
    """Minimal representation of a company for dropdown lookups."""

    company_id: uuid.UUID
    company_code: str
    company_name: str
    employee_code_prefix: str

    model_config = ConfigDict(from_attributes=True)


class DepartmentLookupRead(BaseModel):
    """Minimal representation of a department for dependent dropdown lookups."""

    department_id: uuid.UUID
    company_id: uuid.UUID
    department_code: str
    department_name: str

    model_config = ConfigDict(from_attributes=True)


class DesignationLookupRead(BaseModel):
    """Minimal representation of a designation for dependent dropdown lookups."""

    designation_id: uuid.UUID
    company_id: uuid.UUID
    designation_code: str
    designation_name: str
    level_rank: int
    is_managerial: bool

    model_config = ConfigDict(from_attributes=True)


class ManagerLookupRead(BaseModel):
    """Minimal representation of an employee eligible to be a reporting manager."""

    user_id: uuid.UUID
    employee_code: str
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    official_email: str
    department_name: Optional[str] = None
    designation_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
