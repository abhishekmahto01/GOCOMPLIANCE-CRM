"""Pydantic schemas for User / Employee entity."""
import re
import uuid
from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

ALLOWED_EMPLOYMENT_TYPES = {
    "FULL_TIME",
    "PART_TIME",
    "CONTRACT",
    "INTERN",
    "CONSULTANT",
}

ALLOWED_ACCOUNT_STATUSES = {
    "PENDING",
    "ACTIVE",
    "INACTIVE",
    "SUSPENDED",
}

EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)+$"
)

MOBILE_REGEX = re.compile(
    r"^(\+91[\-\s]?)?[6-9]\d{9}$"
)


def normalize_mobile(v: str) -> str:
    """Validate and normalize mobile number (supporting Indian +91 format)."""
    cleaned = re.sub(r"[\s\-]", "", v.strip())
    if not MOBILE_REGEX.match(cleaned):
        raise ValueError(
            "mobile_number must be a valid 10-digit Indian mobile number (e.g., +919876543210 or 9876543210)"
        )
    if cleaned.startswith("+91"):
        return cleaned
    if len(cleaned) == 10:
        return f"+91{cleaned}"
    return cleaned


def normalize_email_address(v: str, field_name: str = "email") -> str:
    """Validate and lowercase email address."""
    email = v.strip().lower()
    if not EMAIL_REGEX.match(email):
        raise ValueError(f"{field_name} must be a valid email address")
    if len(email) > 255:
        raise ValueError(f"{field_name} cannot exceed 255 characters")
    return email


class UserBase(BaseModel):
    """Base schema with common User/Employee fields."""

    company_id: uuid.UUID = Field(
        ...,
        description="Foreign key ID of the parent company",
    )
    department_id: uuid.UUID = Field(
        ...,
        description="Foreign key ID of the department (must belong to company)",
    )
    designation_id: uuid.UUID = Field(
        ...,
        description="Foreign key ID of the designation (must belong to company)",
    )
    manager_user_id: Optional[uuid.UUID] = Field(
        None,
        description="Nullable foreign key ID of reporting manager (must belong to company)",
    )
    first_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Employee first name",
    )
    middle_name: Optional[str] = Field(
        None,
        max_length=100,
        description="Employee middle name (optional)",
    )
    last_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Employee last name",
    )
    official_email: str = Field(
        ...,
        description="Official corporate email address (case-insensitively unique)",
    )
    personal_email: Optional[str] = Field(
        None,
        description="Personal email address (optional)",
    )
    mobile_number: str = Field(
        ...,
        description="Primary contact mobile number (+91 format)",
    )
    date_of_joining: date = Field(
        ...,
        description="Official date of joining",
    )
    employment_type: str = Field(
        ...,
        description="Employment type: FULL_TIME, PART_TIME, CONTRACT, INTERN, CONSULTANT",
    )
    account_status: str = Field(
        default="PENDING",
        description="Operational status: PENDING, ACTIVE, INACTIVE, SUSPENDED",
    )

    @field_validator("first_name", mode="before")
    @classmethod
    def validate_first_name(cls, v: str) -> str:
        if isinstance(v, str):
            v = v.strip()
            if not v:
                raise ValueError("first_name cannot be blank")
            return v
        return v

    @field_validator("middle_name", mode="before")
    @classmethod
    def normalize_middle_name(cls, v: Optional[str]) -> Optional[str]:
        if isinstance(v, str):
            v = v.strip()
            return v if v else None
        return v

    @field_validator("last_name", mode="before")
    @classmethod
    def validate_last_name(cls, v: str) -> str:
        if isinstance(v, str):
            v = v.strip()
            if not v:
                raise ValueError("last_name cannot be blank")
            return v
        return v

    @field_validator("official_email", mode="before")
    @classmethod
    def validate_official_email(cls, v: str) -> str:
        if isinstance(v, str):
            return normalize_email_address(v, "official_email")
        return v

    @field_validator("personal_email", mode="before")
    @classmethod
    def validate_personal_email(cls, v: Optional[str]) -> Optional[str]:
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return None
            return normalize_email_address(v, "personal_email")
        return v

    @field_validator("mobile_number", mode="before")
    @classmethod
    def validate_mobile(cls, v: str) -> str:
        if isinstance(v, str):
            return normalize_mobile(v)
        return v

    @field_validator("employment_type", mode="before")
    @classmethod
    def validate_employment_type(cls, v: str) -> str:
        if isinstance(v, str):
            v = v.strip().upper()
            if v not in ALLOWED_EMPLOYMENT_TYPES:
                raise ValueError(
                    f"employment_type must be one of: {', '.join(sorted(ALLOWED_EMPLOYMENT_TYPES))}"
                )
            return v
        return v

    @field_validator("account_status", mode="before")
    @classmethod
    def validate_account_status(cls, v: str) -> str:
        if isinstance(v, str):
            v = v.strip().upper()
            if v not in ALLOWED_ACCOUNT_STATUSES:
                raise ValueError(
                    f"account_status must be one of: {', '.join(sorted(ALLOWED_ACCOUNT_STATUSES))}"
                )
            return v
        return v


class UserCreate(UserBase):
    """Schema for creating a new User / Employee.
    
    Note: employee_code is generated by the server and cannot be supplied.
    """
    model_config = ConfigDict(extra="forbid")


class UserUpdate(BaseModel):
    """Schema for updating an existing User / Employee."""

    company_id: Optional[uuid.UUID] = None
    department_id: Optional[uuid.UUID] = None
    designation_id: Optional[uuid.UUID] = None
    manager_user_id: Optional[uuid.UUID] = None
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    middle_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    official_email: Optional[str] = None
    personal_email: Optional[str] = None
    mobile_number: Optional[str] = None
    date_of_joining: Optional[date] = None
    employment_type: Optional[str] = None
    account_status: Optional[str] = None

    model_config = ConfigDict(extra="forbid")

    @field_validator("first_name", mode="before")
    @classmethod
    def validate_first_name(cls, v: Optional[str]) -> Optional[str]:
        if isinstance(v, str):
            v = v.strip()
            if not v:
                raise ValueError("first_name cannot be blank")
            return v
        return v

    @field_validator("middle_name", mode="before")
    @classmethod
    def normalize_middle_name(cls, v: Optional[str]) -> Optional[str]:
        if isinstance(v, str):
            v = v.strip()
            return v if v else None
        return v

    @field_validator("last_name", mode="before")
    @classmethod
    def validate_last_name(cls, v: Optional[str]) -> Optional[str]:
        if isinstance(v, str):
            v = v.strip()
            if not v:
                raise ValueError("last_name cannot be blank")
            return v
        return v

    @field_validator("official_email", mode="before")
    @classmethod
    def validate_official_email(cls, v: Optional[str]) -> Optional[str]:
        if isinstance(v, str):
            return normalize_email_address(v, "official_email")
        return v

    @field_validator("personal_email", mode="before")
    @classmethod
    def validate_personal_email(cls, v: Optional[str]) -> Optional[str]:
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return None
            return normalize_email_address(v, "personal_email")
        return v

    @field_validator("mobile_number", mode="before")
    @classmethod
    def validate_mobile(cls, v: Optional[str]) -> Optional[str]:
        if isinstance(v, str):
            return normalize_mobile(v)
        return v

    @field_validator("employment_type", mode="before")
    @classmethod
    def validate_employment_type(cls, v: Optional[str]) -> Optional[str]:
        if isinstance(v, str):
            v = v.strip().upper()
            if v not in ALLOWED_EMPLOYMENT_TYPES:
                raise ValueError(
                    f"employment_type must be one of: {', '.join(sorted(ALLOWED_EMPLOYMENT_TYPES))}"
                )
            return v
        return v

    @field_validator("account_status", mode="before")
    @classmethod
    def validate_account_status(cls, v: Optional[str]) -> Optional[str]:
        if isinstance(v, str):
            v = v.strip().upper()
            if v not in ALLOWED_ACCOUNT_STATUSES:
                raise ValueError(
                    f"account_status must be one of: {', '.join(sorted(ALLOWED_ACCOUNT_STATUSES))}"
                )
            return v
        return v


class UserRead(UserBase):
    """Schema for reading User / Employee data from API / database."""

    user_id: uuid.UUID
    employee_code: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EmployeeRead(UserRead):
    """Rich employee read schema including joined master names, codes, and safe credential status."""

    company_name: Optional[str] = None
    company_code: Optional[str] = None
    department_name: Optional[str] = None
    department_code: Optional[str] = None
    designation_name: Optional[str] = None
    designation_code: Optional[str] = None
    manager_name: Optional[str] = None
    manager_employee_code: Optional[str] = None
    credentials_initialized: bool = False
    must_change_password: bool = True
    login_status: str = "Not Initialized"
    credentials_initialized_at: Optional[datetime] = None
    password_changed_at: Optional[datetime] = None


class TrialLoginInitializeResponse(BaseModel):
    """Safe response payload after initializing trial login credentials."""

    user_id: uuid.UUID
    employee_code: str
    official_email: str
    credentials_initialized: bool = True
    must_change_password: bool = True
    login_status: str = "Password Change Required"
    credentials_initialized_at: Optional[datetime] = None
    message: str = (
        "Trial login credentials have been initialized. The employee must change the temporary password on first login."
    )



class EmployeeStatusUpdate(BaseModel):
    """Schema for updating employee operational status."""

    account_status: str = Field(
        ...,
        description="Target status: PENDING, ACTIVE, INACTIVE, SUSPENDED",
    )

    model_config = ConfigDict(extra="forbid")

    @field_validator("account_status", mode="before")
    @classmethod
    def validate_account_status(cls, v: str) -> str:
        if isinstance(v, str):
            v = v.strip().upper()
            if v not in ALLOWED_ACCOUNT_STATUSES:
                raise ValueError(
                    f"account_status must be one of: {', '.join(sorted(ALLOWED_ACCOUNT_STATUSES))}"
                )
            return v
        return v


class PaginatedEmployeesResponse(BaseModel):
    """Paginated list envelope for employee records."""

    items: List[EmployeeRead]
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, description="Page size limit")
    total: int = Field(..., ge=0, description="Total matching record count")
    pages: int = Field(..., ge=0, description="Total calculated page count")
