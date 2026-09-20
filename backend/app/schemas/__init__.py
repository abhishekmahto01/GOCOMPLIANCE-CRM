"""Pydantic schemas package."""
from app.schemas.company import (
    CompanyBase,
    CompanyCreate,
    CompanyRead,
    CompanyUpdate,
)
from app.schemas.department import (
    DepartmentBase,
    DepartmentCreate,
    DepartmentRead,
    DepartmentUpdate,
)
from app.schemas.designation import (
    DesignationBase,
    DesignationCreate,
    DesignationRead,
    DesignationUpdate,
)

__all__ = [
    "CompanyBase",
    "CompanyCreate",
    "CompanyRead",
    "CompanyUpdate",
    "DepartmentBase",
    "DepartmentCreate",
    "DepartmentRead",
    "DepartmentUpdate",
    "DesignationBase",
    "DesignationCreate",
    "DesignationRead",
    "DesignationUpdate",
]
