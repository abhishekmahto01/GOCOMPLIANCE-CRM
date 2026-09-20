# Gocompliances CRM - Backend

Production-ready FastAPI backend foundation for Gocompliances CRM.

## Current Stage Scope: Stage 9 (Per-User Module Permissions and Data Scopes)

Stage 9 implements granular, per-user authorization matrix and data scope visibility boundaries:
- **SQLAlchemy 2 Typed Model `UserModulePermission`** mapped to `user_module_permission` table.
- **Granular Action Flags:** Independent boolean switches (`can_view`, `can_create`, `can_edit`, `can_delete`, `can_approve`) with enforced prerequisite (`can_view=True` required for any action).
- **Multi-Tier Data Scopes:** `SELF`, `TEAM`, `DEPARTMENT`, `COMPANY`, `ALL`.
- **Recursive CTE Hierarchy Resolution:** Cycle-safe PostgreSQL CTE query to resolve complete reporting lines with depth limits for `TEAM` scope.
- **Pydantic v2 Validation Schemas** (`UserModulePermissionBase`, `UserModulePermissionCreate`, `UserModulePermissionUpdate`, `UserModulePermissionRead`, `AccessibleModuleRead`).
- **Alembic Schema Migration** `65ff8484468e_create_user_module_permission.py` with unique user/module constraints, check constraints (`chk_permission_data_scope_valid`, `chk_permission_status_valid`, `chk_permission_action_requires_view`, `chk_permission_expires_after_granted`), and indexes.
- **Permission Evaluation Service & FastAPI Dependency** (`require_module_permission`, `has_permission`, `get_accessible_modules`, `resolve_data_scope_context`).
- **Bootstrap CLI Utility** (`app/scripts/grant_bootstrap_permissions.py`) for one-time administrative provisioning (unexecuted during Stage 9).
- **Automated Unit & Integration Test Suite** with 126 passing tests.

---

## Core Security & Permission Principles

1. **Default Deny:** Users have zero access until an explicit, active, and non-expired permission row is assigned.
2. **Action Flag Invariant:** Non-view actions (`can_create`, `can_edit`, `can_delete`, `can_approve`) strictly require `can_view=True`. Enforced both at schema validation and PostgreSQL database constraint levels.
3. **No Role-Based Implicit Access:** Designations and Departments never automatically grant module permissions. Every permission is explicitly bound to a user.
4. **Grantor Escalation Prevention:** Users cannot grant permissions or broader data scopes than they themselves possess.
5. **Temporary Expiration:** Permissions with an `expires_at` timestamp in the past are automatically denied access.
6. **Parent-Child Navigation Preservation:** In `get_accessible_modules`, parent modules are included for UI navigation structure when an accessible child exists, without granting child actions or unrelated submodules.

---

## Data Scope Definitions

| Data Scope | Meaning & Record Access Boundary | Resolution Strategy |
| :--- | :--- | :--- |
| `SELF` | Records owned by or associated with the current user. | `user_id == current_user.user_id` |
| `TEAM` | Records owned by the current user and all direct/indirect recursive subordinates. | PostgreSQL Recursive CTE on `user_master` (`manager_user_id`) with cycle path tracking and depth bounds. |
| `DEPARTMENT` | Records within the user's company and assigned department. | `company_id == user.company_id AND department_id == user.department_id` |
| `COMPANY` | Records within the user's assigned company. | `company_id == user.company_id` |
| `ALL` | All records across permitted company and system scopes. | Global / administrative access. |

---

## `user_module_permission` Column Specifications

| Column | Type | Constraints / Defaults | Description |
| :--- | :--- | :--- | :--- |
| `permission_id` | `UUID` | Primary Key, `NOT NULL` | Unique permission grant ID (UUIDv4) |
| `user_id` | `UUID` | Foreign Key (`user_master.user_id`), `ON DELETE CASCADE`, `NOT NULL`, Index | Target employee user ID |
| `module_id` | `UUID` | Foreign Key (`module_master.module_id`), `ON DELETE RESTRICT`, `NOT NULL`, Index | Target module ID |
| `can_view` | `BOOLEAN` | `NOT NULL`, Default: `false` | Read/view access to module records |
| `can_create` | `BOOLEAN` | `NOT NULL`, Default: `false` | Creation rights (requires `can_view=true`) |
| `can_edit` | `BOOLEAN` | `NOT NULL`, Default: `false` | Update rights (requires `can_view=true`) |
| `can_delete` | `BOOLEAN` | `NOT NULL`, Default: `false` | Delete/deactivate rights (requires `can_view=true`) |
| `can_approve` | `BOOLEAN` | `NOT NULL`, Default: `false` | Workflow approval rights (requires `can_view=true`) |
| `data_scope` | `VARCHAR(20)` | `NOT NULL`, Default: `'SELF'`, Check Constraint | `SELF`, `TEAM`, `DEPARTMENT`, `COMPANY`, `ALL` |
| `status` | `VARCHAR(20)` | `NOT NULL`, Default: `'ACTIVE'`, Index, Check Constraint | `ACTIVE`, `INACTIVE` |
| `granted_by_user_id` | `UUID` | Foreign Key (`user_master.user_id`), `ON DELETE SET NULL`, `NULLABLE`, Index | Grantor user audit reference |
| `granted_at` | `TIMESTAMPTZ` | `NOT NULL`, Default: `now()` | Timestamp when permission was assigned (UTC) |
| `expires_at` | `TIMESTAMPTZ` | `NULLABLE`, Index, Check: `expires_at > granted_at` | Optional future expiration timestamp (UTC) |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL`, Default: `now()` | Timestamp when permission was updated (UTC) |

Unique constraint: `UNIQUE(user_id, module_id)` (`uq_user_module_permission_user_module`).

---

## FastAPI Authorization Dependency Usage

```python
from fastapi import APIRouter, Depends
from app.api.deps import require_module_permission
from app.models.user_module_permission import UserModulePermission

router = APIRouter(prefix="/employees", tags=["Employees"])

@router.get(
    "/",
    dependencies=[Depends(require_module_permission("ADMIN_EMPLOYEES", "view"))],
)
def list_employees():
    return {"message": "Access granted"}

@router.post(
    "/",
    dependencies=[Depends(require_module_permission("ADMIN_EMPLOYEES", "create"))],
)
def create_employee():
    return {"message": "Employee created"}
```

- Unauthenticated requests receive `401 Unauthorized`.
- Authenticated requests lacking the required permission or action receive `403 Forbidden`.

---

## Administrative Bootstrap CLI Utility

When a real Director / Super Admin employee is provisioned in `user_master`, initial permissions can be granted using:

```bash
cd backend
source .venv/bin/activate

# Grant ALL scope and view/create/edit/approve access across all active modules:
python3 -m app.scripts.grant_bootstrap_permissions --employee-code CG0001 --scope ALL

# Optionally grant delete rights as well:
python3 -m app.scripts.grant_bootstrap_permissions --employee-code CG0001 --scope ALL --allow-delete
```

> **IMPORTANT:**
> - The bootstrap script is an administrative tool only. It was **NOT** executed during Stage 9.
> - No test or fake permission records exist in the production database.

---

## Verification & Test Commands

Run the complete test suite:

```bash
cd backend
source .venv/bin/activate
pytest -v
```

Verify table counts in PostgreSQL:

```bash
psql -d is_gocompliance_db -c "
SELECT COUNT(*) AS total_permissions FROM user_module_permission;
SELECT COUNT(*) AS total_users FROM user_master;
SELECT COUNT(*) AS total_modules FROM module_master;
"
```
**Expected Output:**
- `total_permissions` = 0
- `total_users` = 0
- `total_modules` = 8

---

## Upcoming Stages
- **Stage 7C:** Employee Management HTTP CRUD APIs with permission enforcement and data scoping.
- **Stage 7D:** Manager & Employee Management React UI integration.
