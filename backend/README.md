# Gocompliances CRM - Backend

Production-ready FastAPI backend foundation for Gocompliances CRM.

## Current Stage Scope: Stage 5 (Department Master)

This stage establishes the company-specific organizational department framework (`department_master`):
- SQLAlchemy 2 typed model `Department` mapped to `department_master` with foreign key `ON DELETE RESTRICT` to `company_master`.
- Bi-directional ORM relationship `Company.departments` <-> `Department.company`.
- Composite unique constraints guaranteeing department uniqueness *within* a company while permitting identical department codes across companies.
- Pydantic v2 schemas (`DepartmentBase`, `DepartmentCreate`, `DepartmentUpdate`, `DepartmentRead`) with normalization and validation.
- Alembic schema migration `38b03f32afa9_create_department_master.py`.
- Idempotent seed script (`app/scripts/seed_departments.py`) seeding 4 departments per company (12 total) using deterministic UUIDs.
- Automated unit test suite with 36 tests covering models, schemas, relationships, migrations, and seeds.

> **Note on Department Head & CRUD APIs:**
> `department_head_user_id` will be introduced in a future controlled migration after `user_master` is created. **Department/Company CRUD endpoints and Admin UI will be added in subsequent stages.**

---

## Organization Data Architecture

Every employee in Gocompliances CRM will belong to:
$$\text{Company} \longrightarrow \text{Department} \longrightarrow \text{Designation}$$

### Why Departments are Company-Specific
Departments are isolated per company entity (via composite unique constraints `company_id + department_code` and `company_id + department_name`). This allows `SALES` or `OPERATIONS` to exist under multiple companies while preventing duplication within the same company:

```text
Gocompliances (GOCOMPLIANCES / CG)
├── Administration (ADMINISTRATION)
├── Sales (SALES)
├── Operations (OPERATIONS)
└── R&D (RND)

Enterpernership (ENTERPERNERSHIP / EP)
├── Administration (ADMINISTRATION)
├── Sales (SALES)
├── Operations (OPERATIONS)
└── R&D (RND)

Brandmingo (BRANDMINGO / BM)
├── Administration (ADMINISTRATION)
├── Sales (SALES)
├── Operations (OPERATIONS)
└── R&D (RND)
```

---

### `department_master` Column Specifications

| Column | Type | Constraints / Defaults | Description |
| :--- | :--- | :--- | :--- |
| `department_id` | `UUID` | Primary Key, `NOT NULL` | Unique identifier (UUIDv4/v5) |
| `company_id` | `UUID` | Foreign Key (`company_master.company_id`), `ON DELETE RESTRICT`, `NOT NULL`, Index | Parent company reference |
| `department_code` | `VARCHAR(30)` | `NOT NULL`, Check Constraint (`^[A-Z_]+$`) | Uppercase code unique per company |
| `department_name` | `VARCHAR(100)` | `NOT NULL` | Display name unique per company |
| `description` | `VARCHAR(500)` | `NULLABLE` | Optional description of functional scope |
| `status` | `VARCHAR(20)` | `NOT NULL`, Default: `'ACTIVE'`, Index | Operational status (`ACTIVE`, `INACTIVE`) |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL`, Default: `now()` | Record creation timestamp (UTC) |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL`, Default: `now()` | Record update timestamp (UTC) |

**Composite Constraints:**
* `UNIQUE(company_id, department_code)`
* `UNIQUE(company_id, department_name)`
* `CHECK(status IN ('ACTIVE', 'INACTIVE'))`
* `CHECK(department_code ~ '^[A-Z_]+$')`

---

## Database Migration & Seeding Commands

All commands are run from the `backend/` directory with `.venv` activated:

```bash
cd backend
source .venv/bin/activate
```

### 1. Apply Database Migration
Apply all pending schema migrations (including `department_master`):
```bash
alembic upgrade head
```

### 2. Seed Initial Records
1. **Seed Companies (3 records):**
   ```bash
   python3 -m app.scripts.seed_companies
   ```
2. **Seed Departments (12 records):**
   ```bash
   python3 -m app.scripts.seed_departments
   ```

* **Idempotent Seeding Behavior:**
  * First run: Inserts 12 default departments (4 per company).
  * Subsequent runs: Skips existing departments without creating duplicates or modifying existing data.
  * Dependency Guard: Fails safely and rolls back completely if any required company is missing.

### 3. Verify Seeded Records via PostgreSQL

* **List all departments by company:**
  ```bash
  psql -d is_gocompliance_db -c "SELECT c.company_code, d.department_code, d.department_name, d.status FROM department_master d JOIN company_master c ON c.company_id = d.company_id ORDER BY c.company_code, d.department_code;"
  ```

* **Count total departments (Expected: 12):**
  ```bash
  psql -d is_gocompliance_db -c "SELECT COUNT(*) FROM department_master;"
  ```

* **Verify company-wise distribution (Expected: 4 each):**
  ```bash
  psql -d is_gocompliance_db -c "SELECT c.company_code, COUNT(*) AS department_count FROM department_master d JOIN company_master c ON c.company_id = d.company_id GROUP BY c.company_code ORDER BY c.company_code;"
  ```

---

## Running the Applications

### 1. Main CRM API (Port 8000)

```bash
uvicorn app.main:app --reload --port 8000
```

- **API Health Check Endpoint:** [http://localhost:8000/api/health](http://localhost:8000/api/health)
- **Database Health Endpoint:** [http://localhost:8000/api/health/database](http://localhost:8000/api/health/database)
- **Interactive Swagger Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

### 2. Admin Panel Placeholder (Port 8001)

```bash
uvicorn app.admin_app:app --reload --port 8001
```

- **Health Check Endpoint:** [http://localhost:8001/health](http://localhost:8001/health)

---

## Running Automated Tests

Execute the full test suite using `pytest`:

```bash
pytest -v
```

All 36 unit tests run in isolation using mocking (no real database connection required for unit tests).

---

## Project Structure

```text
backend/
├── alembic/
│   ├── versions/
│   │   ├── f6d28a5264ee_baseline_database.py          # Baseline revision
│   │   ├── b445258097c2_create_company_master.py      # Company Master migration
│   │   └── 38b03f32afa9_create_department_master.py   # Department Master migration
│   ├── env.py                                         # Alembic environment with Base.metadata & settings binding
│   ├── script.py.mako                                 # Migration template
│   └── README
├── alembic.ini                                        # Alembic configuration without secrets
├── app/
│   ├── __init__.py
│   ├── main.py                                        # Main CRM FastAPI application (Port 8000)
│   ├── admin_app.py                                   # Database Admin placeholder application (Port 8001)
│   ├── api/
│   │   ├── __init__.py
│   │   └── health.py                                  # Health check endpoints (/api/health, /api/health/database)
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py                                  # Pydantic BaseSettings with credentials masking
│   ├── database/
│   │   ├── __init__.py
│   │   ├── base.py                                    # SQLAlchemy 2 DeclarativeBase
│   │   └── session.py                                 # Engine, SessionLocal factory, and get_db dependency
│   ├── models/
│   │   ├── __init__.py                                # Model exports (Company, Department)
│   │   ├── company.py                                 # Company model (company_master)
│   │   └── department.py                              # Department model (department_master)
│   ├── schemas/
│   │   ├── __init__.py                                # Schema exports
│   │   ├── company.py                                 # Company schemas
│   │   └── department.py                              # Department schemas (Base, Create, Update, Read)
│   ├── scripts/
│   │   ├── __init__.py
│   │   ├── seed_companies.py                          # Idempotent company seeding script (3 records)
│   │   └── seed_departments.py                        # Idempotent department seeding script (12 records)
│   └── services/
│       ├── __init__.py
│       └── database_health.py                         # Safe database health checking service
├── tests/
│   ├── __init__.py
│   ├── test_alembic.py                                # Alembic configuration and baseline safety tests
│   ├── test_company.py                                # Company model, schemas, migration, and seed tests
│   ├── test_database.py                               # Session, config, and database health unit tests
│   ├── test_department.py                             # Department model, schemas, migration, and seed tests
│   └── test_health.py                                 # API and admin health check tests
├── .env                                               # Local uncommitted environment configuration
├── .env.example                                       # Safe environment variable template
├── .gitignore                                         # Backend gitignore rules
├── requirements.txt                                   # Backend dependencies
└── README.md                                          # Backend documentation
```
