"""Permission checking, catalog management, and data scope resolution service."""
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

from sqlalchemy import func, or_, select, text
from sqlalchemy.orm import Session

from app.models.company import Company
from app.models.department import Department
from app.models.designation import Designation
from app.models.module import Module
from app.models.permission_audit import PermissionAuditLog
from app.models.user import User
from app.models.user_module_permission import UserModulePermission
from app.schemas.permission import (
    AccessibleModuleRead,
    CatalogModuleItem,
    CatalogPageItem,
    CopyPermissionsResponse,
    PageActionPermission,
    PermissionCatalogResponse,
    UserEffectivePermissionsResponse,
    UserPermissionsDetailResponse,
    UserPermissionsSaveRequest,
    UserSettingsUpdate,
    VALID_DATA_SCOPES,
    VALID_PERMISSION_STATUSES,
)

SUPPORTED_ACTIONS = {
    "view",
    "read",
    "create",
    "write",
    "edit",
    "update",
    "delete",
    "approve",
    "assign",
    "reassign",
    "export",
}

# Normalized action key mapping
ACTION_FIELD_MAP = {
    "read": "can_view",
    "view": "can_view",
    "write": "can_create",
    "create": "can_create",
    "update": "can_edit",
    "edit": "can_edit",
    "delete": "can_delete",
    "approve": "can_approve",
    "assign": "can_assign",
    "reassign": "can_reassign",
    "export": "can_export",
}

# Exact supported actions specified per page by requirement
PAGE_CATALOG_CONFIG: Dict[str, Dict[str, Any]] = {
    # Sales Module Pages
    "SALES_DASHBOARD": {
        "module_code": "SALES",
        "page_name": "Sales Dashboard",
        "route": "/sales/dashboard",
        "display_order": 10,
        "supported_actions": ["read", "export"],
        "slugs": {
            "read": "sales.dashboard.read",
            "export": "sales.dashboard.export",
        },
    },
    "SALES_CONFIRMED_ORDER": {
        "module_code": "SALES",
        "page_name": "Create Confirmed Order",
        "route": "/sales/confirmed-order",
        "display_order": 20,
        "supported_actions": ["read", "write", "update"],
        "slugs": {
            "read": "sales.confirmed_order.read",
            "write": "sales.confirmed_order.create",
            "update": "sales.confirmed_order.update",
        },
    },
    "SALES_MY_ORDERS": {
        "module_code": "SALES",
        "page_name": "My Sales Orders",
        "route": "/sales/my-orders",
        "display_order": 30,
        "supported_actions": ["read", "update", "delete", "export"],
        "slugs": {
            "read": "sales.my_orders.read",
            "update": "sales.my_orders.update",
            "delete": "sales.my_orders.delete",
            "export": "sales.my_orders.export",
        },
    },
    "SALES_ALL_ORDERS": {
        "module_code": "SALES",
        "page_name": "All Sales Orders",
        "route": "/sales/all-orders",
        "display_order": 40,
        "supported_actions": ["read", "update", "delete", "export"],
        "slugs": {
            "read": "sales.all_orders.read",
            "update": "sales.all_orders.update",
            "delete": "sales.all_orders.delete",
            "export": "sales.all_orders.export",
        },
    },
    "SALES_CLIENT_MASTER": {
        "module_code": "SALES",
        "page_name": "Client Master",
        "route": "/sales/clients",
        "display_order": 50,
        "supported_actions": ["read", "write", "update", "delete"],
        "slugs": {
            "read": "sales.client_master.read",
            "write": "sales.client_master.create",
            "update": "sales.client_master.update",
            "delete": "sales.client_master.delete",
        },
    },
    "SALES_REPORTS": {
        "module_code": "SALES",
        "page_name": "Sales Reports",
        "route": "/sales/reports",
        "display_order": 60,
        "supported_actions": ["read", "export"],
        "slugs": {
            "read": "sales.reports.read",
            "export": "sales.reports.export",
        },
    },
    # Operation Module Pages
    "OPERATION_DASHBOARD": {
        "module_code": "OPERATIONS",
        "page_name": "Operation Dashboard",
        "route": "/operations/dashboard",
        "display_order": 10,
        "supported_actions": ["read", "export"],
        "slugs": {
            "read": "operation.dashboard.read",
            "export": "operation.dashboard.export",
        },
    },
    "OPERATION_UNASSIGNED_ORDERS": {
        "module_code": "OPERATIONS",
        "page_name": "Unassigned Orders",
        "route": "/operations/unassigned-orders",
        "display_order": 20,
        "supported_actions": ["read", "assign"],
        "slugs": {
            "read": "operation.unassigned_orders.read",
            "assign": "operation.unassigned_orders.assign",
        },
    },
    "OPERATION_TASK_ASSIGNMENT": {
        "module_code": "OPERATIONS",
        "page_name": "Task Assignment",
        "route": "/operations/task-assignment",
        "display_order": 30,
        "supported_actions": ["read", "assign", "reassign"],
        "slugs": {
            "read": "operation.task_assignment.read",
            "assign": "operation.task_assignment.assign",
            "reassign": "operation.task_assignment.reassign",
        },
    },
    "OPERATION_MY_TASKS": {
        "module_code": "OPERATIONS",
        "page_name": "My Assigned Tasks",
        "route": "/operations/my-tasks",
        "display_order": 40,
        "supported_actions": ["read", "update"],
        "slugs": {
            "read": "operation.my_tasks.read",
            "update": "operation.my_tasks.update",
        },
    },
    "OPERATION_ALL_TASKS": {
        "module_code": "OPERATIONS",
        "page_name": "All Operation Tasks",
        "route": "/operations/all-tasks",
        "display_order": 50,
        "supported_actions": ["read", "update", "assign", "reassign"],
        "slugs": {
            "read": "operation.all_tasks.read",
            "update": "operation.all_tasks.update",
            "assign": "operation.all_tasks.assign",
            "reassign": "operation.all_tasks.reassign",
        },
    },
    "OPERATION_DOCUMENTS": {
        "module_code": "OPERATIONS",
        "page_name": "Required Documents",
        "route": "/operations/documents",
        "display_order": 60,
        "supported_actions": ["read", "write", "update", "delete"],
        "slugs": {
            "read": "operation.documents.read",
            "write": "operation.documents.create",
            "update": "operation.documents.update",
            "delete": "operation.documents.delete",
        },
    },
    "OPERATION_APPLICATION_STATUS": {
        "module_code": "OPERATIONS",
        "page_name": "Application Status",
        "route": "/operations/application-status",
        "display_order": 70,
        "supported_actions": ["read", "update"],
        "slugs": {
            "read": "operation.application_status.read",
            "update": "operation.application_status.update",
        },
    },
    "OPERATION_REPORTS": {
        "module_code": "OPERATIONS",
        "page_name": "Operation Reports",
        "route": "/operations/reports",
        "display_order": 80,
        "supported_actions": ["read", "export"],
        "slugs": {
            "read": "operation.reports.read",
            "export": "operation.reports.export",
        },
    },
}

# Reverse lookup for slugs: slug -> (page_code, action)
SLUG_TO_PAGE_ACTION: Dict[str, Tuple[str, str]] = {}
for p_code, conf in PAGE_CATALOG_CONFIG.items():
    for act, slug_str in conf["slugs"].items():
        SLUG_TO_PAGE_ACTION[slug_str] = (p_code, act)


class PermissionDeniedError(Exception):
    """Raised when an operation is denied due to missing or insufficient permission."""
    pass


class GrantorEscalationError(Exception):
    """Raised when a grantor attempts to grant permissions or scopes they do not possess."""
    pass


@dataclass
class DataScopeContext:
    """Resolved data visibility scope and scoping identifiers for an authenticated user."""

    scope: str
    user_id: uuid.UUID
    company_id: uuid.UUID
    department_id: uuid.UUID
    team_user_ids: List[uuid.UUID] = field(default_factory=list)

    def is_user_permitted(
        self,
        target_user_id: uuid.UUID,
        target_company_id: Optional[uuid.UUID] = None,
        target_department_id: Optional[uuid.UUID] = None,
    ) -> bool:
        """Helper to check if a specific target record owner falls within this data scope."""
        if self.scope == "ALL":
            return True
        if self.scope == "COMPANY":
            return target_company_id == self.company_id if target_company_id else False
        if self.scope == "DEPARTMENT":
            return (
                target_company_id == self.company_id
                and target_department_id == self.department_id
                if target_company_id and target_department_id
                else False
            )
        if self.scope == "TEAM":
            return target_user_id in self.team_user_ids
        if self.scope == "SELF":
            return target_user_id == self.user_id
        return False


def get_user_module_permission(
    session: Session,
    user_id: uuid.UUID,
    module_code: str,
) -> Optional[UserModulePermission]:
    """Load the UserModulePermission record for a specific user and module code.
    If not found directly and the module has a parent module, check the parent module."""
    code_norm = module_code.strip().upper()
    stmt = (
        select(UserModulePermission)
        .join(Module, UserModulePermission.module_id == Module.module_id)
        .where(
            UserModulePermission.user_id == user_id,
            Module.module_code == code_norm,
        )
    )
    perm = session.execute(stmt).scalar_one_or_none()
    if perm:
        return perm

    # Fallback to parent module from PAGE_CATALOG_CONFIG if available
    parent_code = PAGE_CATALOG_CONFIG.get(code_norm, {}).get("module_code")
    if parent_code and parent_code != code_norm:
        stmt_parent = (
            select(UserModulePermission)
            .join(Module, UserModulePermission.module_id == Module.module_id)
            .where(
                UserModulePermission.user_id == user_id,
                Module.module_code == parent_code,
            )
        )
        parent_perm = session.execute(stmt_parent).scalar_one_or_none()
        if parent_perm:
            return parent_perm

    # Fallback to module's parent_module_id in Module table
    mod_stmt = select(Module).where(Module.module_code == code_norm)
    mod = session.execute(mod_stmt).scalar_one_or_none()
    if mod and mod.parent_module_id:
        stmt_parent_id = (
            select(UserModulePermission)
            .where(
                UserModulePermission.user_id == user_id,
                UserModulePermission.module_id == mod.parent_module_id,
            )
        )
        parent_id_perm = session.execute(stmt_parent_id).scalar_one_or_none()
        if parent_id_perm:
            return parent_id_perm

    # Super Admin fallback: generate full access permission
    user = session.get(User, user_id)
    if is_super_admin_user(session, user):
        mod_id = mod.module_id if mod else uuid.uuid4()
        return UserModulePermission(
            permission_id=uuid.uuid4(),
            user_id=user_id,
            module_id=mod_id,
            can_view=True,
            can_create=True,
            can_edit=True,
            can_delete=True,
            can_approve=True,
            can_assign=True,
            can_reassign=True,
            can_export=True,
            data_scope="ALL",
            status="ACTIVE",
        )

    return None


def is_super_admin_user(session: Optional[Session], user: Optional[User]) -> bool:
    """Check whether an authenticated user is a Super Admin who has global unrestricted rights."""
    if not user or user.account_status != "ACTIVE":
        return False
    if getattr(user, "is_super_admin", False) or getattr(user, "role_type", "") == "SUPER_ADMIN":
        return True
    if getattr(user, "employee_code", "") == "CG0001":
        return True
    if hasattr(user, "designation") and user.designation:
        desig = getattr(user.designation, "designation_name", "").lower()
        if "super admin" in desig:
            return True
    return False


def is_permission_active_and_valid(
    permission: Optional[UserModulePermission],
    now_utc: Optional[datetime] = None,
) -> bool:
    """Check whether a permission record is non-null, ACTIVE, and not expired."""
    if not permission:
        return False
    if permission.status != "ACTIVE":
        return False
    if permission.expires_at is not None:
        current_time = now_utc or datetime.now(timezone.utc)
        expiry = permission.expires_at
        if expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=timezone.utc)
        if expiry <= current_time:
            return False
    return True


def has_permission(
    session: Session,
    user: User,
    module_code: str,
    action: str = "view",
) -> bool:
    """Evaluate whether an authenticated user has explicit permission to perform an action on a module."""
    if not user or user.account_status != "ACTIVE":
        return False

    action_norm = action.strip().lower()
    if action_norm not in SUPPORTED_ACTIONS:
        return False

    # Super Admin default full access across all modules and actions
    if is_super_admin_user(session, user):
        return True

    module_code_norm = module_code.strip().upper()
    module = session.execute(
        select(Module).where(Module.module_code == module_code_norm)
    ).scalar_one_or_none()

    if not module or module.status != "ACTIVE":
        parent_code = PAGE_CATALOG_CONFIG.get(module_code_norm, {}).get("module_code")
        if parent_code and parent_code != module_code_norm:
            return has_permission(session, user, parent_code, action)
        return False

    permission = session.execute(
        select(UserModulePermission).where(
            UserModulePermission.user_id == user.user_id,
            UserModulePermission.module_id == module.module_id,
        )
    ).scalar_one_or_none()

    if not is_permission_active_and_valid(permission):
        parent_code = PAGE_CATALOG_CONFIG.get(module_code_norm, {}).get("module_code")
        if parent_code and parent_code != module_code_norm:
            return has_permission(session, user, parent_code, action)
        p_id = getattr(module, "parent_module_id", None)
        if isinstance(p_id, uuid.UUID):
            parent_mod = session.get(Module, p_id)
            if parent_mod and parent_mod.module_code != module_code_norm:
                return has_permission(session, user, parent_mod.module_code, action)
        return False

    # All actions require can_view=True
    if not permission.can_view:
        return False

    field_name = ACTION_FIELD_MAP.get(action_norm)
    if field_name and hasattr(permission, field_name):
        if bool(getattr(permission, field_name, False)):
            return True

    # Check Operations workflow actions for active Operations team members or managers
    if module_code_norm in ("OPERATIONS", "OPS_APPLICATIONS") or module_code_norm.startswith("OPERATION_"):
        dept_name = user.department.department_name.lower() if user.department else ""
        dept_code = user.department.department_code.upper() if user.department else ""
        is_ops_dept = "operat" in dept_name or "operat" in dept_code or dept_code in ("OP", "OPS", "OPERATIONS") or "admin" in dept_name
        is_mgr = bool(getattr(user, "is_reporting_manager", False) or getattr(user, "is_hod", False))
        if action_norm in ("assign", "reassign", "edit", "update"):
            if permission.can_edit or permission.can_assign or permission.can_reassign or is_ops_dept or is_mgr:
                return True

    # For SALES_MY_ORDERS, also inherit permissions from SALES_ALL_ORDERS or parent SALES module
    if module_code_norm == "SALES_MY_ORDERS":
        all_orders_perm = get_user_module_permission(session, user.user_id, "SALES_ALL_ORDERS")
        if all_orders_perm and is_permission_active_and_valid(all_orders_perm):
            if field_name and hasattr(all_orders_perm, field_name) and bool(getattr(all_orders_perm, field_name, False)):
                return True
        parent_sales_perm = get_user_module_permission(session, user.user_id, "SALES")
        if parent_sales_perm and is_permission_active_and_valid(parent_sales_perm):
            if field_name and hasattr(parent_sales_perm, field_name) and bool(getattr(parent_sales_perm, field_name, False)):
                return True

    return False


def has_permission_slug(
    session: Session,
    user: User,
    slug: str,
) -> bool:
    """Evaluate whether user has permission corresponding to a unique slug."""
    slug_norm = slug.strip().lower()
    if slug_norm not in SLUG_TO_PAGE_ACTION:
        return False
    page_code, action = SLUG_TO_PAGE_ACTION[slug_norm]
    return has_permission(session, user, page_code, action)


def require_permission(
    session: Session,
    user: User,
    module_code: str,
    action: str = "view",
) -> UserModulePermission:
    """Validate permission and return the UserModulePermission record, or raise PermissionDeniedError."""
    if not has_permission(session, user, module_code, action):
        raise PermissionDeniedError(
            f"User '{user.employee_code}' is not authorized to perform '{action}' on module '{module_code}'."
        )

    permission = get_user_module_permission(session, user.user_id, module_code)
    if not permission:
        if is_super_admin_user(session, user):
            mod = session.execute(
                select(Module).where(Module.module_code == module_code.strip().upper())
            ).scalar_one_or_none()
            return UserModulePermission(
                user_id=user.user_id,
                module_id=mod.module_id if mod else uuid.uuid4(),
                can_view=True,
                can_create=True,
                can_edit=True,
                can_delete=True,
                can_approve=True,
                can_assign=True,
                can_reassign=True,
                can_export=True,
                data_scope="ALL",
                status="ACTIVE",
            )
        raise PermissionDeniedError("Permission record not found.")
    return permission


def get_effective_scope(
    session: Session,
    user: User,
    module_code: str,
) -> Optional[str]:
    """Return the effective data scope ('SELF', 'TEAM', 'DEPARTMENT', 'COMPANY', 'ALL') if permitted, else None."""
    if not user or user.account_status != "ACTIVE":
        return None
    if is_super_admin_user(session, user):
        return "ALL"
    if not has_permission(session, user, module_code, "view"):
        return None

    permission = get_user_module_permission(session, user.user_id, module_code)
    return permission.data_scope if permission else "ALL" if is_super_admin_user(session, user) else None


def get_team_user_ids(
    session: Session,
    manager_user_id: uuid.UUID,
    max_depth: int = 50,
) -> List[uuid.UUID]:
    """Retrieve user IDs of a manager and all recursive direct and indirect reports using a cycle-safe CTE."""
    cte_query = text(
        """
        WITH RECURSIVE subordinates AS (
            SELECT user_id, manager_user_id, 1 AS depth, ARRAY[user_id] AS path
            FROM user_master
            WHERE user_id = :root_id
            UNION ALL
            SELECT u.user_id, u.manager_user_id, s.depth + 1, s.path || u.user_id
            FROM user_master u
            JOIN subordinates s ON u.manager_user_id = s.user_id
            WHERE NOT (u.user_id = ANY(s.path))
              AND s.depth < :max_depth
        )
        SELECT user_id FROM subordinates;
        """
    )
    result = session.execute(cte_query, {"root_id": manager_user_id, "max_depth": max_depth})
    return [uuid.UUID(str(row[0])) for row in result.fetchall()]


def resolve_data_scope_context(
    session: Session,
    user: User,
    module_code: str,
) -> DataScopeContext:
    """Resolve the DataScopeContext for the user on a specific module."""
    scope = get_effective_scope(session, user, module_code)
    if not scope:
        raise PermissionDeniedError(
            f"User '{user.employee_code}' has no view access for module '{module_code}'."
        )

    team_ids: List[uuid.UUID] = []
    if scope == "TEAM":
        team_ids = get_team_user_ids(session, user.user_id)
    elif scope == "SELF":
        team_ids = [user.user_id]

    return DataScopeContext(
        scope=scope,
        user_id=user.user_id,
        company_id=user.company_id,
        department_id=user.department_id,
        team_user_ids=team_ids,
    )


def get_accessible_modules(
    session: Session,
    user_id: uuid.UUID,
) -> List[AccessibleModuleRead]:
    """Retrieve all accessible modules for a user formatted for navigation and UI authorization."""
    user = session.get(User, user_id)
    if not user or user.account_status != "ACTIVE":
        return []

    all_modules = session.execute(
        select(Module).where(Module.status == "ACTIVE").order_by(Module.display_order.asc())
    ).scalars().all()
    modules_by_id = {m.module_id: m for m in all_modules}

    if is_super_admin_user(session, user):
        return [
            AccessibleModuleRead(
                module_id=mod.module_id,
                module_code=mod.module_code,
                module_name=mod.module_name,
                parent_module_id=mod.parent_module_id,
                route=mod.route,
                display_order=mod.display_order,
                is_navigation=mod.is_navigation,
                can_view=True,
                can_create=True,
                can_edit=True,
                can_delete=True,
                can_approve=True,
                can_assign=True,
                can_reassign=True,
                can_export=True,
                data_scope="ALL",
            )
            for mod in all_modules
        ]

    now_utc = datetime.now(timezone.utc)
    permissions = session.execute(
        select(UserModulePermission).where(
            UserModulePermission.user_id == user_id,
            UserModulePermission.status == "ACTIVE",
            UserModulePermission.can_view.is_(True),
        )
    ).scalars().all()

    valid_permissions = [p for p in permissions if is_permission_active_and_valid(p, now_utc)]
    perms_by_module_id = {p.module_id: p for p in valid_permissions}
    accessible_module_ids: Set[uuid.UUID] = set(perms_by_module_id.keys())

    parents_to_add: Set[uuid.UUID] = set()
    for mod_id in accessible_module_ids:
        mod = modules_by_id.get(mod_id)
        curr = mod
        while curr and curr.parent_module_id:
            parent = modules_by_id.get(curr.parent_module_id)
            if parent:
                parents_to_add.add(parent.module_id)
            curr = parent

    result: List[AccessibleModuleRead] = []
    for mod in all_modules:
        if mod.module_id in accessible_module_ids:
            perm = perms_by_module_id[mod.module_id]
            result.append(
                AccessibleModuleRead(
                    module_id=mod.module_id,
                    module_code=mod.module_code,
                    module_name=mod.module_name,
                    parent_module_id=mod.parent_module_id,
                    route=mod.route,
                    display_order=mod.display_order,
                    is_navigation=mod.is_navigation,
                    can_view=perm.can_view,
                    can_create=perm.can_create,
                    can_edit=perm.can_edit,
                    can_delete=perm.can_delete,
                    can_approve=perm.can_approve,
                    can_assign=perm.can_assign,
                    can_reassign=perm.can_reassign,
                    can_export=perm.can_export,
                    data_scope=perm.data_scope,
                )
            )
        elif mod.module_id in parents_to_add and mod.is_navigation:
            result.append(
                AccessibleModuleRead(
                    module_id=mod.module_id,
                    module_code=mod.module_code,
                    module_name=mod.module_name,
                    parent_module_id=mod.parent_module_id,
                    route=mod.route,
                    display_order=mod.display_order,
                    is_navigation=mod.is_navigation,
                    can_view=True,
                    can_create=False,
                    can_edit=False,
                    can_delete=False,
                    can_approve=False,
                    can_assign=False,
                    can_reassign=False,
                    can_export=False,
                    data_scope="SELF",
                )
            )

    return sorted(result, key=lambda x: x.display_order)


SCOPE_HIERARCHY_RANK = {
    "SELF": 1,
    "TEAM": 2,
    "DEPARTMENT": 3,
    "COMPANY": 4,
    "ALL": 5,
}


def grant_or_update_permission(
    session: Session,
    user_id: uuid.UUID,
    module_id: uuid.UUID,
    can_view: bool = True,
    can_create: bool = False,
    can_edit: bool = False,
    can_delete: bool = False,
    can_approve: bool = False,
    can_assign: bool = False,
    can_reassign: bool = False,
    can_export: bool = False,
    data_scope: str = "SELF",
    status: str = "ACTIVE",
    expires_at: Optional[datetime] = None,
    granted_by_user_id: Optional[uuid.UUID] = None,
    is_bootstrap: bool = False,
) -> UserModulePermission:
    """Grant or update a user's permission for a module with transaction safety."""
    has_action = (
        can_create
        or can_edit
        or can_delete
        or can_approve
        or can_assign
        or can_reassign
        or can_export
    )
    if has_action and not can_view:
        raise ValueError(
            "can_view must be true when create, edit, delete, approve, assign, reassign, or export flags are enabled"
        )

    scope_norm = data_scope.strip().upper()
    if scope_norm not in VALID_DATA_SCOPES:
        raise ValueError(f"Invalid data scope '{data_scope}'. Must be one of {sorted(VALID_DATA_SCOPES)}")

    status_norm = status.strip().upper()
    if status_norm not in VALID_PERMISSION_STATUSES:
        raise ValueError(f"Invalid status '{status}'. Must be one of {sorted(VALID_PERMISSION_STATUSES)}")

    target_user = session.get(User, user_id)
    if not target_user:
        raise ValueError(f"Target user with ID {user_id} not found")
    if target_user.account_status != "ACTIVE":
        raise ValueError(f"Target user {target_user.employee_code} is not in ACTIVE status")

    target_module = session.get(Module, module_id)
    if not target_module:
        raise ValueError(f"Target module with ID {module_id} not found")
    if target_module.status != "ACTIVE":
        raise ValueError(f"Target module {target_module.module_code} is not in ACTIVE status")

    # Anti-escalation check if performed by a regular grantor
    if granted_by_user_id and not is_bootstrap:
        if granted_by_user_id == user_id:
            raise GrantorEscalationError("Users cannot grant or modify permissions for themselves")

        grantor = session.get(User, granted_by_user_id)
        if not grantor or grantor.account_status != "ACTIVE":
            raise GrantorEscalationError("Grantor user is inactive or does not exist")

        # Check if grantor has ADMIN_ACCESS permission with ALL scope
        admin_access_perm = get_user_module_permission(session, granted_by_user_id, "ADMIN_ACCESS")
        is_super_admin = (
            admin_access_perm
            and is_permission_active_and_valid(admin_access_perm)
            and admin_access_perm.data_scope == "ALL"
            and admin_access_perm.can_edit
        )

        if not is_super_admin:
            grantor_perm = session.execute(
                select(UserModulePermission).where(
                    UserModulePermission.user_id == granted_by_user_id,
                    UserModulePermission.module_id == module_id,
                )
            ).scalar_one_or_none()

            if not is_permission_active_and_valid(grantor_perm):
                raise GrantorEscalationError(
                    f"Grantor lacks active permission on module '{target_module.module_code}'"
                )

            if can_create and not grantor_perm.can_create:
                raise GrantorEscalationError("Grantor cannot grant 'create' action without possessing it")
            if can_edit and not grantor_perm.can_edit:
                raise GrantorEscalationError("Grantor cannot grant 'edit' action without possessing it")
            if can_delete and not grantor_perm.can_delete:
                raise GrantorEscalationError("Grantor cannot grant 'delete' action without possessing it")
            if can_approve and not grantor_perm.can_approve:
                raise GrantorEscalationError("Grantor cannot grant 'approve' action without possessing it")
            if can_assign and not grantor_perm.can_assign:
                raise GrantorEscalationError("Grantor cannot grant 'assign' action without possessing it")
            if can_reassign and not grantor_perm.can_reassign:
                raise GrantorEscalationError("Grantor cannot grant 'reassign' action without possessing it")
            if can_export and not grantor_perm.can_export:
                raise GrantorEscalationError("Grantor cannot grant 'export' action without possessing it")

            grantor_rank = SCOPE_HIERARCHY_RANK.get(grantor_perm.data_scope, 0)
            target_rank = SCOPE_HIERARCHY_RANK.get(scope_norm, 0)
            if target_rank > grantor_rank:
                raise GrantorEscalationError(
                    f"Grantor with scope '{grantor_perm.data_scope}' cannot grant broader scope '{scope_norm}'"
                )

    existing_perm = session.execute(
        select(UserModulePermission).where(
            UserModulePermission.user_id == user_id,
            UserModulePermission.module_id == module_id,
        )
    ).scalar_one_or_none()

    if existing_perm:
        existing_perm.can_view = can_view
        existing_perm.can_create = can_create
        existing_perm.can_edit = can_edit
        existing_perm.can_delete = can_delete
        existing_perm.can_approve = can_approve
        existing_perm.can_assign = can_assign
        existing_perm.can_reassign = can_reassign
        existing_perm.can_export = can_export
        existing_perm.data_scope = scope_norm
        existing_perm.status = status_norm
        existing_perm.expires_at = expires_at
        existing_perm.granted_by_user_id = granted_by_user_id
        session.flush()
        return existing_perm

    new_perm = UserModulePermission(
        user_id=user_id,
        module_id=module_id,
        can_view=can_view,
        can_create=can_create,
        can_edit=can_edit,
        can_delete=can_delete,
        can_approve=can_approve,
        can_assign=can_assign,
        can_reassign=can_reassign,
        can_export=can_export,
        data_scope=scope_norm,
        status=status_norm,
        expires_at=expires_at,
        granted_by_user_id=granted_by_user_id,
    )
    session.add(new_perm)
    session.flush()
    return new_perm


def deactivate_permission(
    session: Session,
    user_id: uuid.UUID,
    module_id: uuid.UUID,
    updated_by_user_id: Optional[uuid.UUID] = None,
) -> Optional[UserModulePermission]:
    """Deactivate an existing permission assignment (sets status='INACTIVE')."""
    perm = session.execute(
        select(UserModulePermission).where(
            UserModulePermission.user_id == user_id,
            UserModulePermission.module_id == module_id,
        )
    ).scalar_one_or_none()

    if perm:
        perm.status = "INACTIVE"
        if updated_by_user_id:
            perm.granted_by_user_id = updated_by_user_id
        session.flush()
    return perm


# ==============================================================================
# Permission Catalog and Granular Management Services
# ==============================================================================

def get_permission_catalog(session: Session) -> PermissionCatalogResponse:
    """Return the structured catalog of Sales and Operation modules and pages with supported actions."""
    sales_pages: List[CatalogPageItem] = []
    operation_pages: List[CatalogPageItem] = []

    for page_code, config in sorted(PAGE_CATALOG_CONFIG.items(), key=lambda item: item[1]["display_order"]):
        page_item = CatalogPageItem(
            page_code=page_code,
            page_name=config["page_name"],
            route=config["route"],
            supported_actions=config["supported_actions"],
            action_slugs=config["slugs"],
            display_order=config["display_order"],
        )
        if config["module_code"] == "SALES":
            sales_pages.append(page_item)
        elif config["module_code"] == "OPERATIONS":
            operation_pages.append(page_item)

    modules = [
        CatalogModuleItem(
            module_code="SALES",
            module_name="Sales",
            pages=sales_pages,
        ),
        CatalogModuleItem(
            module_code="OPERATIONS",
            module_name="Operation",
            pages=operation_pages,
        ),
    ]
    return PermissionCatalogResponse(modules=modules)


def get_user_permissions_bundle(
    session: Session,
    user_id: uuid.UUID,
) -> UserPermissionsDetailResponse:
    """Load an employee's comprehensive permissions bundle and user-level settings."""
    user = session.get(User, user_id)
    if not user:
        raise ValueError(f"Employee with ID '{user_id}' not found")

    company = session.get(Company, user.company_id)
    dept = session.get(Department, user.department_id)
    desig = session.get(Designation, user.designation_id)
    manager = session.get(User, user.manager_user_id) if user.manager_user_id else None

    # Load all user permissions
    perms = session.execute(
        select(UserModulePermission, Module.module_code)
        .join(Module, UserModulePermission.module_id == Module.module_id)
        .where(UserModulePermission.user_id == user_id)
    ).all()

    perms_by_code: Dict[str, UserModulePermission] = {
        row.module_code: row.UserModulePermission for row in perms
    }

    # Assemble page action permissions for all configured catalog pages
    page_permissions: List[PageActionPermission] = []
    for page_code in PAGE_CATALOG_CONFIG.keys():
        perm_row = perms_by_code.get(page_code)
        if perm_row and perm_row.status == "ACTIVE":
            page_permissions.append(
                PageActionPermission(
                    page_code=page_code,
                    can_view=perm_row.can_view,
                    can_create=perm_row.can_create,
                    can_edit=perm_row.can_edit,
                    can_delete=perm_row.can_delete,
                    can_assign=perm_row.can_assign,
                    can_reassign=perm_row.can_reassign,
                    can_export=perm_row.can_export,
                    can_approve=perm_row.can_approve,
                    data_scope=perm_row.data_scope,
                    status=perm_row.status,
                )
            )
        else:
            page_permissions.append(
                PageActionPermission(
                    page_code=page_code,
                    can_view=False,
                    can_create=False,
                    can_edit=False,
                    can_delete=False,
                    can_assign=False,
                    can_reassign=False,
                    can_export=False,
                    can_approve=False,
                    data_scope="SELF",
                    status="ACTIVE",
                )
            )

    manager_name = f"{manager.first_name} {manager.last_name}" if manager else None

    return UserPermissionsDetailResponse(
        user_id=user.user_id,
        employee_code=user.employee_code,
        first_name=user.first_name,
        last_name=user.last_name,
        official_email=user.official_email,
        company_id=user.company_id,
        company_name=company.company_name if company else None,
        department_id=user.department_id,
        department_name=dept.department_name if dept else None,
        designation_id=user.designation_id,
        designation_name=desig.designation_name if desig else None,
        is_active=bool(user.account_status == "ACTIVE"),
        is_hod=bool(getattr(user, "is_hod", False)),
        is_reporting_manager=bool(getattr(user, "is_reporting_manager", False)),
        manager_user_id=getattr(user, "manager_user_id", None),
        manager_name=manager_name,
        primary_location=getattr(user, "primary_location", None),
        permissions=page_permissions,
    )


def count_active_super_admins(session: Session) -> int:
    """Count number of active Super Admins with access to ADMIN_ACCESS."""
    stmt = (
        select(func.count(User.user_id))
        .join(UserModulePermission, User.user_id == UserModulePermission.user_id)
        .join(Module, UserModulePermission.module_id == Module.module_id)
        .where(
            User.account_status == "ACTIVE",
            Module.module_code == "ADMIN_ACCESS",
            UserModulePermission.status == "ACTIVE",
            UserModulePermission.can_view.is_(True),
            UserModulePermission.can_edit.is_(True),
            UserModulePermission.data_scope == "ALL",
        )
    )
    return session.scalar(stmt) or 0


def save_user_permissions_bundle(
    session: Session,
    actor_user: User,
    target_user_id: uuid.UUID,
    payload: UserPermissionsSaveRequest,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> UserPermissionsDetailResponse:
    """Save an employee's permissions and user-level settings transactionally with audit logging."""
    target_user = session.get(User, target_user_id)
    if not target_user:
        raise ValueError(f"Target employee with ID '{target_user_id}' not found")

    # Capture before-state for audit
    before_detail = get_user_permissions_bundle(session, target_user_id)
    before_state = before_detail.model_dump(mode="json")

    # 1. Update user settings if provided
    if payload.user_settings:
        us = payload.user_settings
        if us.is_active is not None:
            # Protect last active Super Admin from deactivation
            if target_user.account_status == "ACTIVE" and not us.is_active:
                if count_active_super_admins(session) <= 1 and actor_user.user_id == target_user.user_id:
                    raise ValueError("Cannot deactivate the only active Super Administrator account.")
            target_user.account_status = "ACTIVE" if us.is_active else "INACTIVE"
        if us.is_hod is not None:
            target_user.is_hod = us.is_hod
        if us.is_reporting_manager is not None:
            target_user.is_reporting_manager = us.is_reporting_manager
        if us.manager_user_id is not None or "manager_user_id" in us.model_fields_set:
            if us.manager_user_id == target_user_id:
                raise ValueError("An employee cannot be their own reporting manager.")
            if us.manager_user_id:
                mgr = session.get(User, us.manager_user_id)
                if not mgr or mgr.company_id != target_user.company_id:
                    raise ValueError("Reporting manager must be an active employee within the same company.")
            target_user.manager_user_id = us.manager_user_id
        if us.primary_location is not None:
            target_user.primary_location = us.primary_location

    # 2. Resolve module records for the pages
    active_modules = session.execute(
        select(Module).where(Module.status == "ACTIVE")
    ).scalars().all()
    mod_by_code = {m.module_code: m for m in active_modules}

    # Also resolve parent module IDs (SALES, OPERATIONS)
    parent_codes = {"SALES", "OPERATIONS"}
    parent_mods = {c: mod_by_code.get(c) for c in parent_codes}

    sales_has_any_view = False
    operations_has_any_view = False

    # 3. Validate and apply permissions
    for perm_in in payload.permissions:
        code = perm_in.page_code.strip().upper()
        if code not in PAGE_CATALOG_CONFIG:
            raise ValueError(f"Unknown page code '{code}' in permission payload.")

        page_config = PAGE_CATALOG_CONFIG[code]
        supported = set(page_config["supported_actions"])

        # Check unsupported action violations
        if perm_in.can_create and "write" not in supported and "create" not in supported:
            raise ValueError(f"Action 'write' is not supported for page '{code}'.")
        if perm_in.can_edit and "update" not in supported and "edit" not in supported:
            raise ValueError(f"Action 'update' is not supported for page '{code}'.")
        if perm_in.can_delete and "delete" not in supported:
            raise ValueError(f"Action 'delete' is not supported for page '{code}'.")
        if perm_in.can_assign and "assign" not in supported:
            raise ValueError(f"Action 'assign' is not supported for page '{code}'.")
        if perm_in.can_reassign and "reassign" not in supported:
            raise ValueError(f"Action 'reassign' is not supported for page '{code}'.")
        if perm_in.can_export and "export" not in supported:
            raise ValueError(f"Action 'export' is not supported for page '{code}'.")

        # Track parent module view requirement
        if perm_in.can_view:
            if page_config["module_code"] == "SALES":
                sales_has_any_view = True
            elif page_config["module_code"] == "OPERATIONS":
                operations_has_any_view = True

        target_module = mod_by_code.get(code)
        if not target_module:
            raise ValueError(f"Module record for page code '{code}' not found in database.")

        grant_or_update_permission(
            session=session,
            user_id=target_user_id,
            module_id=target_module.module_id,
            can_view=perm_in.can_view,
            can_create=perm_in.can_create if ("write" in supported or "create" in supported) else False,
            can_edit=perm_in.can_edit if ("update" in supported or "edit" in supported) else False,
            can_delete=perm_in.can_delete if "delete" in supported else False,
            can_approve=perm_in.can_approve,
            can_assign=perm_in.can_assign if "assign" in supported else False,
            can_reassign=perm_in.can_reassign if "reassign" in supported else False,
            can_export=perm_in.can_export if "export" in supported else False,
            data_scope=perm_in.data_scope,
            status=perm_in.status,
            granted_by_user_id=actor_user.user_id,
            is_bootstrap=True,
        )

    # 4. Sync parent module (SALES, OPERATIONS) navigation view
    if parent_mods.get("SALES"):
        grant_or_update_permission(
            session=session,
            user_id=target_user_id,
            module_id=parent_mods["SALES"].module_id,
            can_view=sales_has_any_view,
            can_create=False,
            can_edit=False,
            can_delete=False,
            can_approve=False,
            can_assign=False,
            can_reassign=False,
            can_export=False,
            data_scope="SELF",
            status="ACTIVE" if sales_has_any_view else "INACTIVE",
            granted_by_user_id=actor_user.user_id,
            is_bootstrap=True,
        )

    if parent_mods.get("OPERATIONS"):
        grant_or_update_permission(
            session=session,
            user_id=target_user_id,
            module_id=parent_mods["OPERATIONS"].module_id,
            can_view=operations_has_any_view,
            can_create=False,
            can_edit=False,
            can_delete=False,
            can_approve=False,
            can_assign=False,
            can_reassign=False,
            can_export=False,
            data_scope="SELF",
            status="ACTIVE" if operations_has_any_view else "INACTIVE",
            granted_by_user_id=actor_user.user_id,
            is_bootstrap=True,
        )

    session.flush()

    # Capture after-state for audit
    after_detail = get_user_permissions_bundle(session, target_user_id)
    after_state = after_detail.model_dump(mode="json")

    # Create immutable audit entry
    audit_entry = PermissionAuditLog(
        audit_id=uuid.uuid4(),
        actor_user_id=actor_user.user_id,
        target_user_id=target_user_id,
        action_type="PERMISSION_UPDATE",
        before_state=before_state,
        after_state=after_state,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    session.add(audit_entry)
    session.commit()

    return after_detail


def copy_user_permissions(
    session: Session,
    actor_user: User,
    source_user_id: uuid.UUID,
    target_user_id: uuid.UUID,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> CopyPermissionsResponse:
    """Copy Sales and Operation permissions from source employee to target employee transactionally."""
    if source_user_id == target_user_id:
        raise ValueError("Source and target employee cannot be the same.")

    source_user = session.get(User, source_user_id)
    if not source_user:
        raise ValueError(f"Source employee with ID '{source_user_id}' not found.")

    target_user = session.get(User, target_user_id)
    if not target_user:
        raise ValueError(f"Target employee with ID '{target_user_id}' not found.")

    if source_user.company_id != target_user.company_id:
        # Cross company check: requires ALL scope from actor
        scope_ctx = resolve_data_scope_context(session, actor_user, "ADMIN_ACCESS")
        if scope_ctx.scope != "ALL":
            raise PermissionDeniedError("Cannot copy permissions across companies without company-wide authorization.")

    # Capture before-state of target
    before_detail = get_user_permissions_bundle(session, target_user_id)
    before_state = before_detail.model_dump(mode="json")

    # Fetch source permissions for configured catalog pages
    source_detail = get_user_permissions_bundle(session, source_user_id)
    source_perms = {p.page_code: p for p in source_detail.permissions}

    save_payload = UserPermissionsSaveRequest(
        permissions=list(source_perms.values()),
        user_settings=None,
    )

    save_user_permissions_bundle(
        session=session,
        actor_user=actor_user,
        target_user_id=target_user_id,
        payload=save_payload,
        ip_address=ip_address,
        user_agent=user_agent,
    )

    # Add explicit COPY audit entry
    after_detail = get_user_permissions_bundle(session, target_user_id)
    after_state = after_detail.model_dump(mode="json")

    copy_audit = PermissionAuditLog(
        audit_id=uuid.uuid4(),
        actor_user_id=actor_user.user_id,
        target_user_id=target_user_id,
        action_type="PERMISSION_COPY",
        before_state={"source_user_id": str(source_user_id), "target_before": before_state},
        after_state=after_state,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    session.add(copy_audit)
    session.commit()

    return CopyPermissionsResponse(
        message=f"Successfully copied permissions from {source_user.employee_code} to {target_user.employee_code}.",
        copied_count=len(source_perms),
        source_user_id=source_user_id,
        target_user_id=target_user_id,
    )


def get_user_effective_permissions_bundle(
    session: Session,
    user_id: uuid.UUID,
) -> UserEffectivePermissionsResponse:
    """Return effective permission slugs map and accessible pages for current user."""
    user = session.get(User, user_id)
    if not user:
        raise ValueError(f"User with ID '{user_id}' not found")

    accessible_modules = get_accessible_modules(session, user_id)
    accessible_by_code = {m.module_code: m for m in accessible_modules}

    slug_map: Dict[str, bool] = {}
    for page_code, config in PAGE_CATALOG_CONFIG.items():
        mod_perm = accessible_by_code.get(page_code)
        for act, slug_str in config["slugs"].items():
            if not mod_perm or not mod_perm.can_view:
                slug_map[slug_str] = False
                continue

            field_name = ACTION_FIELD_MAP.get(act)
            if field_name and getattr(mod_perm, field_name, False):
                slug_map[slug_str] = True
            else:
                slug_map[slug_str] = False

    return UserEffectivePermissionsResponse(
        user_id=user.user_id,
        employee_code=user.employee_code,
        official_email=user.official_email,
        first_name=user.first_name,
        last_name=user.last_name,
        company_id=user.company_id,
        department_id=user.department_id,
        permissions=slug_map,
        accessible_pages=accessible_modules,
    )
