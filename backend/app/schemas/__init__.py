"""Pydantic schemas package."""
from app.schemas.auth import (
    ChangePasswordRequest,
    CurrentUserRead,
    LoginRequest,
    LogoutRequest,
    RefreshTokenRequest,
    TokenResponse,
)
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
from app.schemas.lookup import (
    CompanyLookupRead,
    DepartmentLookupRead,
    DesignationLookupRead,
    ManagerLookupRead,
)
from app.schemas.module import (
    ModuleBase,
    ModuleCreate,
    ModuleRead,
    ModuleTreeRead,
    ModuleUpdate,
)
from app.schemas.permission import (
    AccessibleModuleRead,
    UserModulePermissionBase,
    UserModulePermissionCreate,
    UserModulePermissionRead,
    UserModulePermissionUpdate,
)
from app.schemas.user import (
    EmployeeRead,
    EmployeeStatusUpdate,
    PaginatedEmployeesResponse,
    UserBase,
    UserCreate,
    UserRead,
    UserUpdate,
)

__all__ = [
    "AccessibleModuleRead",
    "ChangePasswordRequest",
    "CompanyBase",
    "CompanyCreate",
    "CompanyLookupRead",
    "CompanyRead",
    "CompanyUpdate",
    "CurrentUserRead",
    "DepartmentBase",
    "DepartmentCreate",
    "DepartmentLookupRead",
    "DepartmentRead",
    "DepartmentUpdate",
    "DesignationBase",
    "DesignationCreate",
    "DesignationLookupRead",
    "DesignationRead",
    "DesignationUpdate",
    "EmployeeRead",
    "EmployeeStatusUpdate",
    "LoginRequest",
    "LogoutRequest",
    "ManagerLookupRead",
    "ModuleBase",
    "ModuleCreate",
    "ModuleRead",
    "ModuleTreeRead",
    "ModuleUpdate",
    "PaginatedEmployeesResponse",
    "RefreshTokenRequest",
    "TokenResponse",
    "UserBase",
    "UserCreate",
    "UserModulePermissionBase",
    "UserModulePermissionCreate",
    "UserModulePermissionRead",
    "UserModulePermissionUpdate",
    "UserRead",
    "UserUpdate",
]
