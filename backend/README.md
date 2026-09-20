# Gocompliances CRM - Backend

Production-ready FastAPI backend foundation for Gocompliances CRM.

## Current Stage Scope: Stage 7C (Authorized Employee CRUD API)

Stage 7C delivers authorized Employee Management HTTP APIs governed by granular `ADMIN_EMPLOYEES` module permissions and server-enforced data scoping:
- **FastAPI Router `/api/admin/employees`** with full CRUD and operational lifecycle control.
- **Granular Permission Checks:** All endpoints enforced with `require_module_permission("ADMIN_EMPLOYEES", action)`:
  - `POST /api/admin/employees` (`create` action)
  - `GET /api/admin/employees` (`view` action)
  - `GET /api/admin/employees/{user_id}` (`view` action)
  - `PATCH /api/admin/employees/{user_id}` (`edit` action)
  - `PATCH /api/admin/employees/{user_id}/status` (`approve` action)
- **Multi-Tier Data Scopes:** Server-side evaluation of `SELF`, `TEAM` (recursive hierarchy via cycle-safe PostgreSQL CTE), `DEPARTMENT`, `COMPANY`, and `ALL`.
- **Atomic Code Generation:** Automatic company-prefix based employee code assignment on creation (`CG0001`, `EP0001`, `BM0001`). Client-supplied codes are forbidden.
- **Strict Organizational Integrity:** Server validates that department, designation, and reporting manager exist, are `ACTIVE`, and belong to the employee's company.
- **Hierarchy Loop Prevention:** Ensures employees cannot report to themselves or to any subordinate in their reporting subtree.
- **Zero Secret/Password Exposure:** Response schemas strictly exclude `password_hash`, reset tokens, and sensitive authentication internals. Plaintext passwords are never accepted or stored.
- **Automated Unit & Integration Test Suite:** 140 passing tests.

---

## Employee Management Endpoints

All endpoints are mounted under `/api/admin/employees`:

| Method | Route | Required Module & Action | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/admin/employees` | `ADMIN_EMPLOYEES:create` | Create a new employee with an auto-generated employee code. |
| `GET` | `/api/admin/employees` | `ADMIN_EMPLOYEES:view` | List paginated employees within the user's data scope. |
| `GET` | `/api/admin/employees/{user_id}` | `ADMIN_EMPLOYEES:view` | Retrieve detailed employee profile. Returns `404` if not found, `403` if out-of-scope. |
| `PATCH` | `/api/admin/employees/{user_id}` | `ADMIN_EMPLOYEES:edit` | Partially update employee profile with integrity & cycle prevention. |
| `PATCH` | `/api/admin/employees/{user_id}/status` | `ADMIN_EMPLOYEES:approve` | Update employee operational status (`PENDING`, `ACTIVE`, `INACTIVE`, `SUSPENDED`). |

*Note: There is no `DELETE` endpoint. Employee accounts are deactivated or suspended via the status update endpoint.*

---

## Data Scope Visibility Matrix

| Data Scope | Meaning & Record Access Boundary | Resolution Strategy |
| :--- | :--- | :--- |
| `SELF` | Only the authenticated user's own employee record. | `user_id == current_user.user_id` |
| `TEAM` | Current user and all direct/indirect recursive subordinates. | PostgreSQL Recursive CTE on `user_master` (`manager_user_id`) with cycle tracking and depth limit. |
| `DEPARTMENT` | Employees belonging to the same company and department. | `company_id == user.company_id AND department_id == user.department_id` |
| `COMPANY` | Employees belonging to the same company. | `company_id == user.company_id` |
| `ALL` | All employees across all companies and departments. | Global administrative access. |

---

## Available Query Filters for Listing (`GET /api/admin/employees`)

- `page` (integer, default: 1): 1-indexed page number.
- `page_size` (integer, default: 20, max: 100): Items per page.
- `search` (string): Case-insensitive search on employee code, official email, first name, last name, or full name.
- `company_id` (UUID): Filter by company.
- `department_id` (UUID): Filter by department.
- `designation_id` (UUID): Filter by designation.
- `manager_user_id` (UUID): Filter by direct reporting manager.
- `account_status` (string): Filter by `PENDING`, `ACTIVE`, `INACTIVE`, `SUSPENDED`.

---

## Example Request & Response Payloads

### 1. Create Employee (`POST /api/admin/employees`)

**Request:**
```json
{
  "company_id": "07dc4671-4240-4add-bce6-67e3d2bd45c9",
  "department_id": "ff903dd1-eaf1-4da5-8f7b-83f3ca227195",
  "designation_id": "832bb14a-b45b-4833-8db9-d3b3937bb77e",
  "manager_user_id": "18f507b9-f7cf-4513-bfa1-d68a9b1c7dc4",
  "first_name": "Rohan",
  "middle_name": "Kumar",
  "last_name": "Verma",
  "official_email": "rohan.verma@gocompliances.in",
  "personal_email": "rohan.v@example.com",
  "mobile_number": "+919876543210",
  "date_of_joining": "2026-03-01",
  "employment_type": "FULL_TIME",
  "account_status": "ACTIVE"
}
```

**Response (HTTP 201 Created):**
```json
{
  "user_id": "9a7d341b-4f9e-4a6c-94fb-741982b6c12d",
  "employee_code": "CG0002",
  "company_id": "07dc4671-4240-4add-bce6-67e3d2bd45c9",
  "company_name": "Gocompliances",
  "company_code": "GOCOMPLIANCES",
  "department_id": "ff903dd1-eaf1-4da5-8f7b-83f3ca227195",
  "department_name": "Sales",
  "department_code": "SALES",
  "designation_id": "832bb14a-b45b-4833-8db9-d3b3937bb77e",
  "designation_name": "Executive",
  "designation_code": "EXECUTIVE",
  "manager_user_id": "18f507b9-f7cf-4513-bfa1-d68a9b1c7dc4",
  "manager_name": "Amit Sharma",
  "manager_employee_code": "CG0001",
  "first_name": "Rohan",
  "middle_name": "Kumar",
  "last_name": "Verma",
  "official_email": "rohan.verma@gocompliances.in",
  "personal_email": "rohan.v@example.com",
  "mobile_number": "+919876543210",
  "date_of_joining": "2026-03-01",
  "employment_type": "FULL_TIME",
  "account_status": "ACTIVE",
  "created_at": "2026-09-20T20:10:00Z",
  "updated_at": "2026-09-20T20:10:00Z"
}
```

### 2. Paginated List (`GET /api/admin/employees?page=1&page_size=20`)

**Response (HTTP 200 OK):**
```json
{
  "items": [
    {
      "user_id": "9a7d341b-4f9e-4a6c-94fb-741982b6c12d",
      "employee_code": "CG0002",
      "company_name": "Gocompliances",
      "department_name": "Sales",
      "designation_name": "Executive",
      "first_name": "Rohan",
      "last_name": "Verma",
      "official_email": "rohan.verma@gocompliances.in",
      "mobile_number": "+919876543210",
      "date_of_joining": "2026-03-01",
      "employment_type": "FULL_TIME",
      "account_status": "ACTIVE",
      "created_at": "2026-09-20T20:10:00Z",
      "updated_at": "2026-09-20T20:10:00Z"
    }
  ],
  "page": 1,
  "page_size": 20,
  "total": 1,
  "pages": 1
}
```

---

## Running Verification & Tests

Run all unit and integration tests:

```bash
cd backend
source .venv/bin/activate
pytest -v
alembic current
```

---

---

## Stage 10A: Secure First Super Admin Bootstrap CLI

### Security Rationale: Why Bootstrap is CLI-Only
Normal CRM employee creation APIs (`POST /api/admin/employees`) strictly prohibit accepting or exposing client passwords to ensure zero secret leakage and separation of concerns. However, the very first administrator requires initial credentials and full permissions to log into the Admin Panel (`http://localhost:8001`) and configure the CRM.

To maintain strict security:
- **No Public HTTP Endpoint:** Bootstrap is strictly accessible via backend command-line invocation (`python -m app.scripts.bootstrap_super_admin`).
- **No Hardcoded/Default Credentials:** Credentials must never exist in repository code, migration scripts, or configuration files.
- **Secure Password Prompting:** Passwords are requested interactively via `getpass.getpass` with mandatory confirmation and password policy enforcement (Argon2id hashing). Passwords and password hashes are never logged or printed to stdout.
- **Atomic Operations:** Super Admin creation and module permission grants occur within a single database transaction with complete rollback on any error.
- **Safety Guard Against Accidental Duplicate Super Admins:** If an active Super Admin already exists in the system, execution halts by default unless `--allow-additional-super-admin` is explicitly supplied.

---

### Prerequisites
Before running the bootstrap script, ensure the database is up-to-date and all master datasets are populated:

```bash
cd backend
source .venv/bin/activate
alembic upgrade head
python -m app.scripts.seed_companies
python -m app.scripts.seed_departments
python -m app.scripts.seed_designations
python -m app.scripts.seed_modules
```

---

### CLI Command Reference

#### 1. Display Help
```bash
python -m app.scripts.bootstrap_super_admin --help
python -m app.scripts.bootstrap_super_admin create --help
python -m app.scripts.bootstrap_super_admin promote --help
```

#### 2. Mode 1: Create a New Super Admin Employee (`create`)
Creates an active employee record with an atomic employee code (`CG0001`, `EP0001`, etc.), prompts securely for an Argon2 password, and assigns full `ALL` data scope across all active modules.

**Dry-run Validation (No DB writes or password prompt):**
```bash
python -m app.scripts.bootstrap_super_admin create \
  --email admin@gocompliances.in \
  --first-name Admin \
  --last-name User \
  --phone 9876543210 \
  --company-code CG \
  --department-code ADMINISTRATION \
  --designation-code DIRECTOR \
  --dry-run
```

**Interactive Execution:**
```bash
python -m app.scripts.bootstrap_super_admin create \
  --email admin@gocompliances.in \
  --first-name Admin \
  --last-name User \
  --phone 9876543210 \
  --company-code CG \
  --department-code ADMINISTRATION \
  --designation-code DIRECTOR
```

**Non-Interactive / Automation Execution (with confirmation flag):**
```bash
python -m app.scripts.bootstrap_super_admin create \
  --email admin@gocompliances.in \
  --first-name Admin \
  --last-name User \
  --phone 9876543210 \
  --company-code CG \
  --department-code ADMINISTRATION \
  --designation-code DIRECTOR \
  --yes
```

#### 3. Mode 2: Promote an Existing Employee (`promote`)
Promotes an active employee (located via email or employee code) to Super Admin.
- If the employee does not have a password hash, securely prompts for initial credentials.
- If the employee already has a login password, preserves it untouched.

**Dry-run Validation:**
```bash
python -m app.scripts.bootstrap_super_admin promote \
  --email rohan.verma@gocompliances.in \
  --dry-run
```

**Execution:**
```bash
python -m app.scripts.bootstrap_super_admin promote \
  --email rohan.verma@gocompliances.in
```

Or by employee code:
```bash
python -m app.scripts.bootstrap_super_admin promote \
  --employee-code CG0001
```

---

### Advanced Flags & Safety Controls

| Flag | Applicable Mode | Description |
| :--- | :--- | :--- |
| `--dry-run` | `create`, `promote` | Runs all master integrity validations, checks conflicts, and outputs safe summary without mutating the database or prompting for passwords. |
| `--allow-additional-super-admin` | `create`, `promote` | Bypasses safety block when one or more active Super Admins already exist with full `ALL` access to all active modules. |
| `--update-existing-permissions` | `create`, `promote` | Explicitly updates existing `user_module_permission` rows instead of raising a conflict error. |
| `--yes`, `--non-interactive` | `create`, `promote` | Bypasses interactive confirmation typing (`CREATE SUPER ADMIN` / `PROMOTE SUPER ADMIN`). Note: Does NOT bypass password entry. |

---

### Super Admin Permissions & Self-Granting Rationale
For every active module in `module_master`, the bootstrap tool provisions a `UserModulePermission` record configured with:
- `can_view = True`
- `can_create = True`
- `can_edit = True`
- `can_delete = True`
- `can_approve = True`
- `data_scope = "ALL"`
- `status = "ACTIVE"`
- `granted_by_user_id = user.user_id` (Self-referential assignment is valid in the database schema as `user_master` row is flushed prior to permission creation).

---

### Database Verification Queries (Safe & Non-Sensitive)

To verify bootstrap results directly in PostgreSQL without exposing password hashes:

#### 1. Verify Super Admin Employee Record
```sql
SELECT
    employee_code,
    first_name,
    last_name,
    official_email,
    mobile_number,
    employment_type,
    account_status,
    created_at
FROM user_master
WHERE official_email = 'admin@gocompliances.in';
```

#### 2. Verify Full Module Permissions & Data Scope
```sql
SELECT
    m.module_code,
    m.module_name,
    ump.can_view,
    ump.can_create,
    ump.can_edit,
    ump.can_delete,
    ump.can_approve,
    ump.data_scope,
    ump.status
FROM user_module_permission ump
JOIN module_master m ON m.module_id = ump.module_id
JOIN user_master u ON u.user_id = ump.user_id
WHERE u.official_email = 'admin@gocompliances.in'
ORDER BY m.display_order ASC;
```

#### 3. Aggregate Permission Count Check
```sql
SELECT
    u.employee_code,
    u.official_email,
    COUNT(ump.permission_id) AS total_permissions,
    SUM(CASE WHEN ump.data_scope = 'ALL' AND ump.can_view AND ump.can_create AND ump.can_edit AND ump.can_delete AND ump.can_approve THEN 1 ELSE 0 END) AS full_all_permissions
FROM user_master u
LEFT JOIN user_module_permission ump ON u.user_id = ump.user_id AND ump.status = 'ACTIVE'
WHERE u.official_email = 'admin@gocompliances.in'
GROUP BY u.employee_code, u.official_email;
```

> [!CAUTION]
> **Password Security Reminder:** Never paste real credentials or password hashes into source code, Git commits, pull requests, terminal screenshots, or chat channels. Run bootstrap only in secure environments.

