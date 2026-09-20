"""Services package."""
from app.services.auth_service import (
    authenticate_user,
    change_user_password,
    logout_user,
    refresh_access_token,
)
from app.services.database_health import check_database_health
from app.services.employee_code import generate_employee_code
from app.services.permissions import (
    DataScopeContext,
    GrantorEscalationError,
    PermissionDeniedError,
    deactivate_permission,
    get_accessible_modules,
    get_effective_scope,
    get_team_user_ids,
    get_user_module_permission,
    grant_or_update_permission,
    has_permission,
    require_permission,
    resolve_data_scope_context,
)
from app.services.user_service import (
    create_user,
    get_employee_by_id,
    list_employees,
    serialize_employee_read,
    update_employee,
    update_employee_status,
    validate_user_cross_company_integrity,
)

__all__ = [
    "DataScopeContext",
    "GrantorEscalationError",
    "PermissionDeniedError",
    "authenticate_user",
    "change_user_password",
    "check_database_health",
    "create_user",
    "deactivate_permission",
    "generate_employee_code",
    "get_accessible_modules",
    "get_effective_scope",
    "get_employee_by_id",
    "get_team_user_ids",
    "get_user_module_permission",
    "grant_or_update_permission",
    "has_permission",
    "list_employees",
    "logout_user",
    "refresh_access_token",
    "require_permission",
    "resolve_data_scope_context",
    "serialize_employee_read",
    "update_employee",
    "update_employee_status",
    "validate_user_cross_company_integrity",
]
