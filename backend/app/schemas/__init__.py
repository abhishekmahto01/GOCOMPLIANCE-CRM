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
from app.schemas.module import (
    ModuleBase,
    ModuleCreate,
    ModuleRead,
    ModuleTreeRead,
    ModuleUpdate,
)
from app.schemas.user import (
    UserBase,
    UserCreate,
    UserRead,
    UserUpdate,
)

__all__ = [
    "ChangePasswordRequest",
    "CompanyBase",
    "CompanyCreate",
    "CompanyRead",
    "CompanyUpdate",
    "CurrentUserRead",
    "DepartmentBase",
    "DepartmentCreate",
    "DepartmentRead",
    "DepartmentUpdate",
    "DesignationBase",
    "DesignationCreate",
    "DesignationRead",
    "DesignationUpdate",
    "LoginRequest",
    "LogoutRequest",
    "ModuleBase",
    "ModuleCreate",
    "ModuleRead",
    "ModuleTreeRead",
    "ModuleUpdate",
    "RefreshTokenRequest",
    "TokenResponse",
    "UserBase",
    "UserCreate",
    "UserRead",
    "UserUpdate",
]
