# Gocompliances CRM - Backend

Production-ready FastAPI backend foundation for Gocompliances CRM.

## Current Stage Scope: Stage 8 (Module Master)

Stage 8 establishes the central module and navigation framework (`module_master`) to govern system features, navigation hierarchy, and access boundaries:
- **SQLAlchemy 2 Typed Model `Module`** mapped to `module_master` with self-referencing foreign key (`fk_module_parent_module_id`) with `ON DELETE RESTRICT`.
- **Hierarchical Module Support:** Self-referencing bi-directional ORM relationships (`Module.parent` <-> `Module.children`).
- **Pydantic v2 Schemas** (`ModuleBase`, `ModuleCreate`, `ModuleUpdate`, `ModuleRead`, `ModuleTreeRead`) with route format validation, uppercase code normalization, and recursive tree serialization.
- **Alembic Schema Migration** `f46f50205034_create_module_master.py` with unique constraints, indexes on routes/codes, and check constraints (`chk_module_self_parent`, `chk_module_route_format`, `chk_module_code_format`, `chk_module_display_order_non_negative`, `chk_module_status_valid`).
- **Idempotent Initial Seeding Script** (`app/scripts/seed_modules.py`) that provisions the 8 core system modules (3 top-level, 5 sub-modules) with deterministic UUIDv5 identifiers.
- **Automated Unit Test Suite** with 104 passing tests covering models, constraints, tree serialization, migrations, and seeding idempotency.

> **Note on Stage 8 Scope & Access Boundaries:**
> - **Navigation vs Access:** The `is_navigation` flag indicates whether a module appears in UI navigation; it **does NOT** grant user permissions.
> - **Permissions in Stage 9:** User-specific module permissions (`user_module_permission`) and access matrices will be implemented in Stage 9.
> - **Employee UI & Module CRUD Endpoints:** Administrative UI and module CRUD endpoints will be delivered in subsequent sub-stages.

---

## Initial System Module Hierarchy (8 Records)

| Module Code | Module Name | Parent Module | Route | Display Order | Navigation | Description |
| :--- | :--- | :---: | :--- | :---: | :---: | :--- |
| `ADMIN` | Admin | *None* | `/admin` | 10 | `true` | Administrative settings, company management, and access controls |
| `ADMIN_COMPANIES` | Companies | `ADMIN` | `/admin/companies` | 10 | `true` | Corporate entities and company code prefixes |
| `ADMIN_DEPARTMENTS` | Departments | `ADMIN` | `/admin/departments` | 20 | `true` | Company-specific department configuration |
| `ADMIN_DESIGNATIONS` | Designations | `ADMIN` | `/admin/designations` | 30 | `true` | Company-specific employee designations and seniority ranks |
| `ADMIN_EMPLOYEES` | Employees | `ADMIN` | `/admin/employees` | 40 | `true` | Employee master records and organizational hierarchy |
| `ADMIN_ACCESS` | Access Control | `ADMIN` | `/admin/access` | 50 | `true` | User module permissions and role authorization |
| `SALES` | Sales | *None* | `/sales` | 20 | `true` | Sales pipeline, lead management, and customer conversions |
| `OPERATIONS` | Operations | *None* | `/operations` | 30 | `true` | Client compliance workflows, task execution, and delivery |

---

## `module_master` Column Specifications

| Column | Type | Constraints / Defaults | Description |
| :--- | :--- | :--- | :--- |
| `module_id` | `UUID` | Primary Key, `NOT NULL` | Unique module identifier (UUIDv4/v5) |
| `module_code` | `VARCHAR(60)` | `NOT NULL`, Unique Index, Check Constraint (`^[A-Z_]+$`) | Uppercase immutable system identifier |
| `module_name` | `VARCHAR(100)` | `NOT NULL` | Human-readable module name |
| `parent_module_id` | `UUID` | Foreign Key (`module_master.module_id`), `ON DELETE RESTRICT`, `NULLABLE`, Index | Parent module reference (null for root) |
| `route` | `VARCHAR(200)` | `NULLABLE`, Unique Index, Check Constraint (`^/.*`) | Frontend route path starting with `/` |
| `description` | `VARCHAR(500)` | `NULLABLE` | Optional description of module features |
| `display_order` | `INTEGER` | `NOT NULL`, Default: `0`, Index, Check: `>= 0` | UI display sorting order |
| `is_navigation` | `BOOLEAN` | `NOT NULL`, Default: `true` | Navigation visibility indicator |
| `status` | `VARCHAR(20)` | `NOT NULL`, Default: `'ACTIVE'`, Index, Check Constraint | `ACTIVE`, `INACTIVE` |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL`, Default: `now()` | Record creation timestamp (UTC) |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL`, Default: `now()` | Record update timestamp (UTC) |

---

## Database Migration & Seeding Commands

All commands are run from the `backend/` directory with `.venv` activated:

```bash
cd backend
source .venv/bin/activate
```

### 1. Apply Database Migration
```bash
alembic upgrade head
```

### 2. Seed Initial System Modules (8 records)
```bash
python3 -m app.scripts.seed_modules
```

### 3. Verify Database Records in PostgreSQL
```bash
psql -d is_gocompliance_db -c "
SELECT
    child.module_code,
    child.module_name,
    parent.module_code AS parent_code,
    child.route,
    child.display_order,
    child.status
FROM module_master child
LEFT JOIN module_master parent
    ON parent.module_id = child.parent_module_id
ORDER BY
    COALESCE(parent.module_code, child.module_code),
    child.display_order;

SELECT COUNT(*) AS total_modules FROM module_master;
SELECT COUNT(*) AS root_modules FROM module_master WHERE parent_module_id IS NULL;
SELECT COUNT(*) AS admin_children FROM module_master child JOIN module_master parent ON parent.module_id = child.parent_module_id WHERE parent.module_code = 'ADMIN';
"
```
**Expected Counts:**
- `total_modules` = 8
- `root_modules` = 3 (`ADMIN`, `SALES`, `OPERATIONS`)
- `admin_children` = 5 (`ADMIN_COMPANIES`, `ADMIN_DEPARTMENTS`, `ADMIN_DESIGNATIONS`, `ADMIN_EMPLOYEES`, `ADMIN_ACCESS`)

---

## Running Automated Tests

Execute the full test suite using `pytest`:

```bash
pytest -v
```

All 104 unit tests run in isolation using mocking (no destructive database mutations).

---

## Roadmap / Upcoming Stages
- **Stage 9:** User Module Permissions (`user_module_permission`), Granular Access Control, and Permission Evaluation Dependencies.
- **Stage 10:** Employee Management HTTP CRUD APIs, Admin UI, and Navigation Integration.
