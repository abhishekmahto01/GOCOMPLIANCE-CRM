"""Permission checking and data scope resolution service."""
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional, Set

from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.module import Module
from app.models.user import User
from app.models.user_module_permission import UserModulePermission
from app.schemas.permission import (
    AccessibleModuleRead,
    VALID_DATA_SCOPES,
    VALID_PERMISSION_STATUSES,
)

SUPPORTED_ACTIONS = {"view", "create", "edit", "delete", "approve"}


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

    def is_user_permitted(self, target_user_id: uuid.UUID, target_company_id: Optional[uuid.UUID] = None, target_department_id: Optional[uuid.UUID] = None) -> bool:
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

    Returns None if no permission row exists or if the module code does not exist.
    """
    stmt = (
        select(UserModulePermission)
        .join(Module, UserModulePermission.module_id == Module.module_id)
        .where(
            UserModulePermission.user_id == user_id,
            Module.module_code == module_code.strip().upper(),
        )
    )
    return session.execute(stmt).scalar_one_or_none()


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
    """Evaluate whether an authenticated user has explicit permission to perform an action on a module.

    Security Rules:
    - User account_status must be 'ACTIVE'.
    - Target module must exist and be 'ACTIVE'.
    - Permission row must exist, have status 'ACTIVE', and must not be expired.
    - can_view must be True for any action.
    - Specific action flag (can_create, can_edit, can_delete, can_approve) must be True.
    - Unknown module or missing permission -> Deny (False).
    - No implicit access from Designation or Department.
    """
    if not user or user.account_status != "ACTIVE":
        return False

    action_norm = action.strip().lower()
    if action_norm not in SUPPORTED_ACTIONS:
        return False

    module_code_norm = module_code.strip().upper()
    module = session.execute(
        select(Module).where(Module.module_code == module_code_norm)
    ).scalar_one_or_none()

    if not module or module.status != "ACTIVE":
        return False

    permission = session.execute(
        select(UserModulePermission).where(
            UserModulePermission.user_id == user.user_id,
            UserModulePermission.module_id == module.module_id,
        )
    ).scalar_one_or_none()

    if not is_permission_active_and_valid(permission):
        return False

    # All actions require can_view=True
    if not permission.can_view:
        return False

    if action_norm == "view":
        return permission.can_view
    elif action_norm == "create":
        return permission.can_create
    elif action_norm == "edit":
        return permission.can_edit
    elif action_norm == "delete":
        return permission.can_delete
    elif action_norm == "approve":
        return permission.can_approve

    return False


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
        raise PermissionDeniedError("Permission record not found.")
    return permission


def get_effective_scope(
    session: Session,
    user: User,
    module_code: str,
) -> Optional[str]:
    """Return the effective data scope ('SELF', 'TEAM', 'DEPARTMENT', 'COMPANY', 'ALL') if permitted, else None."""
    if not has_permission(session, user, module_code, "view"):
        return None

    permission = get_user_module_permission(session, user.user_id, module_code)
    return permission.data_scope if permission else None


def get_team_user_ids(
    session: Session,
    manager_user_id: uuid.UUID,
    max_depth: int = 50,
) -> List[uuid.UUID]:
    """Retrieve user IDs of a manager and all recursive direct and indirect reports using a cycle-safe CTE.

    Uses PostgreSQL recursive CTE with an array path tracking visited user IDs to prevent
    infinite loops from circular hierarchy references.
    """
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
    return [row[0] for row in result.fetchall()]


def resolve_data_scope_context(
    session: Session,
    user: User,
    module_code: str,
) -> DataScopeContext:
    """Resolve the DataScopeContext for the user on a specific module.

    Raises PermissionDeniedError if the user lacks active view permission on the module.
    """
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
    """Retrieve all accessible modules for a user formatted for navigation and UI authorization.

    Parent modules are included for navigation tree structure when an accessible child exists,
    even if the parent module does not have a direct permission row.
    """
    user = session.get(User, user_id)
    if not user or user.account_status != "ACTIVE":
        return []

    # Fetch all active modules
    all_modules = session.execute(
        select(Module).where(Module.status == "ACTIVE").order_by(Module.display_order.asc())
    ).scalars().all()
    modules_by_id = {m.module_id: m for m in all_modules}

    # Fetch active, non-expired permissions for this user
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

    # Collect all modules that have direct view permission
    accessible_module_ids: Set[uuid.UUID] = set(perms_by_module_id.keys())

    # Include parent modules for navigation structure if a child is accessible
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
                    data_scope=perm.data_scope,
                )
            )
        elif mod.module_id in parents_to_add and mod.is_navigation:
            # Parent module included for navigation only; no child actions or data scope
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
    data_scope: str = "SELF",
    status: str = "ACTIVE",
    expires_at: Optional[datetime] = None,
    granted_by_user_id: Optional[uuid.UUID] = None,
    is_bootstrap: bool = False,
) -> UserModulePermission:
    """Grant or update a user's permission for a module with transaction safety and privilege escalation checks.

    Args:
        session: Active database session.
        user_id: Target user UUID.
        module_id: Target module UUID.
        can_view: View action flag.
        can_create: Create action flag (requires can_view=true).
        can_edit: Edit action flag (requires can_view=true).
        can_delete: Delete action flag (requires can_view=true).
        can_approve: Approve action flag (requires can_view=true).
        data_scope: Scope string ('SELF', 'TEAM', 'DEPARTMENT', 'COMPANY', 'ALL').
        status: Permission status ('ACTIVE', 'INACTIVE').
        expires_at: Optional future expiration datetime.
        granted_by_user_id: Authenticated user ID performing the grant (None for system bootstrap).
        is_bootstrap: Flag indicating initial system bootstrap (bypasses grantor escalation checks).

    Returns:
        The created or updated UserModulePermission record.

    Raises:
        ValueError: For invalid action combinations, scopes, or statuses.
        GrantorEscalationError: If the grantor lacks sufficient permissions to grant the requested access.
        IntegrityError: If database constraints are violated.
    """
    # 1. Validate action flags consistency
    has_action = can_create or can_edit or can_delete or can_approve
    if has_action and not can_view:
        raise ValueError("can_view must be true when create, edit, delete, or approve flags are enabled")

    # 2. Validate data_scope and status
    scope_norm = data_scope.strip().upper()
    if scope_norm not in VALID_DATA_SCOPES:
        raise ValueError(f"Invalid data scope '{data_scope}'. Must be one of {sorted(VALID_DATA_SCOPES)}")

    status_norm = status.strip().upper()
    if status_norm not in VALID_PERMISSION_STATUSES:
        raise ValueError(f"Invalid status '{status}'. Must be one of {sorted(VALID_PERMISSION_STATUSES)}")

    # 3. Validate target user and module exist and are ACTIVE
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

    # 4. Check grantor permissions (anti-escalation check)
    if granted_by_user_id and not is_bootstrap:
        if granted_by_user_id == user_id:
            raise GrantorEscalationError("Users cannot grant or modify permissions for themselves")

        grantor = session.get(User, granted_by_user_id)
        if not grantor or grantor.account_status != "ACTIVE":
            raise GrantorEscalationError("Grantor user is inactive or does not exist")

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

        # Grantor cannot grant action flags they do not possess
        if can_create and not grantor_perm.can_create:
            raise GrantorEscalationError("Grantor cannot grant 'create' action without possessing it")
        if can_edit and not grantor_perm.can_edit:
            raise GrantorEscalationError("Grantor cannot grant 'edit' action without possessing it")
        if can_delete and not grantor_perm.can_delete:
            raise GrantorEscalationError("Grantor cannot grant 'delete' action without possessing it")
        if can_approve and not grantor_perm.can_approve:
            raise GrantorEscalationError("Grantor cannot grant 'approve' action without possessing it")

        # Grantor cannot grant broader data scope than their own
        grantor_rank = SCOPE_HIERARCHY_RANK.get(grantor_perm.data_scope, 0)
        target_rank = SCOPE_HIERARCHY_RANK.get(scope_norm, 0)
        if target_rank > grantor_rank:
            raise GrantorEscalationError(
                f"Grantor with scope '{grantor_perm.data_scope}' cannot grant broader scope '{scope_norm}'"
            )

    # 5. Find existing permission or create new (idempotent upsert)
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
