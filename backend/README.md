# Gocompliances CRM - Backend

Production-ready FastAPI backend foundation for Gocompliances CRM.

## Current Stage Scope: Stage 6 (Designation Master)

This stage establishes the company-specific organizational designation framework (`designation_master`):
- SQLAlchemy 2 typed model `Designation` mapped to `designation_master` with foreign key `ON DELETE RESTRICT` to `company_master`.
- Bi-directional ORM relationship `Company.designations` <-> `Designation.company`.
- Clear conceptual separation between Company, Department, Designation, and Permissions.
- Composite unique constraints guaranteeing title uniqueness *within* a company while permitting identical titles across companies.
- Seniority ranking (`level_rank > 0`) and classification metadata (`is_managerial`).
- Pydantic v2 schemas (`DesignationBase`, `DesignationCreate`, `DesignationUpdate`, `DesignationRead`) with normalization and validation.
- Alembic schema migration `da18e31ab374_create_designation_master.py`.
- Idempotent seed script (`app/scripts/seed_designations.py`) seeding 6 standard designations per company (18 total) using deterministic UUIDs.
- Automated unit test suite with 48 tests covering models, schemas, relationships, migrations, and seeds.

> **Note on Permissions & CRUD APIs:**
> **Designations do NOT grant software access or permissions.** Permissions will be governed separately in future stages. Designation CRUD endpoints and Admin UI will be introduced in subsequent stages.

---

## Conceptual Architecture: Company vs Department vs Designation vs Permission

In Gocompliances CRM, organizational concepts are decoupled:

| Concept | Question Answered | Example | Note |
| :--- | :--- | :--- | :--- |
| **Company** | Employee kis company mein hai? | `Gocompliances`, `Enterpernership`, `Brandmingo` | Top-level entity |
| **Department** | Employee kis team/vertical mein kaam karta hai? | `Sales`, `Operations`, `R&D`, `Administration` | Company-specific team |
| **Designation** | Employee ki official position/seniority kya hai? | `Executive`, `Manager`, `Director` | Company-specific job title |
| **Permission** | Software mein employee kya access kar sakta hai? | *Can view leads*, *Can approve invoices* | Governed by security roles, **NOT** designation |

$$\text{Employee} = \text{Company} + \text{Department} + \text{Designation} \quad [\text{Permissions via dedicated ACL}]$$

### Initial Standard Designations (6 per company)

| Designation Code | Designation Name | Level Rank | Managerial | Description |
| :--- | :--- | :---: | :---: | :--- |
| `EXECUTIVE` | Executive | 10 | No (`false`) | Entry-level operational professional |
| `SENIOR_EXECUTIVE` | Senior Executive | 20 | No (`false`) | Experienced operational specialist |
| `ASSISTANT_MANAGER` | Assistant Manager | 30 | Yes (`true`) | Supervisory / junior management |
| `MANAGER` | Manager | 40 | Yes (`true`) | Functional team leader |
| `HEAD` | Head | 50 | Yes (`true`) | Departmental head |
| `DIRECTOR` | Director | 60 | Yes (`true`) | Executive business director |

* **Level Rank Meaning:** Integer counter ($>0$) indicating corporate hierarchy. Higher value represents higher seniority.
* **`is_managerial` Flag:** Informational metadata only used for organizational charts and reporting. It does **not** grant software permissions.

---

### `designation_master` Column Specifications

| Column | Type | Constraints / Defaults | Description |
| :--- | :--- | :--- | :--- |
| `designation_id` | `UUID` | Primary Key, `NOT NULL` | Unique identifier (UUIDv4/v5) |
| `company_id` | `UUID` | Foreign Key (`company_master.company_id`), `ON DELETE RESTRICT`, `NOT NULL`, Index | Parent company reference |
| `designation_code` | `VARCHAR(50)` | `NOT NULL`, Check Constraint (`^[A-Z_]+$`) | Uppercase code unique per company |
| `designation_name` | `VARCHAR(100)` | `NOT NULL` | Display title unique per company |
| `level_rank` | `INTEGER` | `NOT NULL`, Index, Check: `level_rank > 0` | Seniority level counter |
| `is_managerial` | `BOOLEAN` | `NOT NULL`, Default: `false` | Managerial classification indicator |
| `description` | `VARCHAR(500)` | `NULLABLE` | Optional description of responsibilities |
| `status` | `VARCHAR(20)` | `NOT NULL`, Default: `'ACTIVE'`, Index | Operational status (`ACTIVE`, `INACTIVE`) |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL`, Default: `now()` | Record creation timestamp (UTC) |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL`, Default: `now()` | Record update timestamp (UTC) |

**Composite Constraints:**
* `UNIQUE(company_id, designation_code)`
* `UNIQUE(company_id, designation_name)`
* `CHECK(level_rank > 0)`
* `CHECK(status IN ('ACTIVE', 'INACTIVE'))`
* `CHECK(designation_code ~ '^[A-Z_]+$')`

---

## Database Migration & Seeding Commands

All commands are run from the `backend/` directory with `.venv` activated:

```bash
cd backend
source .venv/bin/activate
```

### 1. Apply Database Migration
Apply all pending schema migrations (including `designation_master`):
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
3. **Seed Designations (18 records):**
   ```bash
   python3 -m app.scripts.seed_designations
   ```

* **Idempotent Seeding Behavior:**
  * First run: Inserts 18 default designations (6 per company).
  * Subsequent runs: Skips existing designations without creating duplicates or modifying existing data.
  * Dependency Guard: Fails safely and rolls back completely if any required company is missing.

### 3. Verify Seeded Records via PostgreSQL

* **List all designations with rank and managerial flag:**
  ```bash
  psql -d is_gocompliance_db -c "SELECT c.company_code, d.designation_code, d.designation_name, d.level_rank, d.is_managerial, d.status FROM designation_master d JOIN company_master c ON c.company_id = d.company_id ORDER BY c.company_code, d.level_rank;"
  ```

* **Count total designations (Expected: 18):**
  ```bash
  psql -d is_gocompliance_db -c "SELECT COUNT(*) FROM designation_master;"
  ```

* **Verify company-wise distribution (Expected: 6 each):**
  ```bash
  psql -d is_gocompliance_db -c "SELECT c.company_code, COUNT(*) AS designation_count FROM designation_master d JOIN company_master c ON c.company_id = d.company_id GROUP BY c.company_code ORDER BY c.company_code;"
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

All 48 unit tests run in isolation using mocking (no real database connection required for unit tests).

---

## Project Structure

```text
backend/
├── alembic/
│   ├── versions/
│   │   ├── f6d28a5264ee_baseline_database.py             # Baseline revision
│   │   ├── b445258097c2_create_company_master.py         # Company Master migration
│   │   ├── 38b03f32afa9_create_department_master.py      # Department Master migration
│   │   └── da18e31ab374_create_designation_master.py     # Designation Master migration
│   ├── env.py                                            # Alembic environment with Base.metadata & settings binding
│   ├── script.py.mako                                    # Migration template
│   └── README
├── alembic.ini                                           # Alembic configuration without secrets
├── app/
│   ├── __init__.py
│   ├── main.py                                           # Main CRM FastAPI application (Port 8000)
│   ├── admin_app.py                                      # Database Admin placeholder application (Port 8001)
│   ├── api/
│   │   ├── __init__.py
│   │   └── health.py                                     # Health check endpoints (/api/health, /api/health/database)
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py                                     # Pydantic BaseSettings with credentials masking
│   ├── database/
│   │   ├── __init__.py
│   │   ├── base.py                                       # SQLAlchemy 2 DeclarativeBase
│   │   └── session.py                                    # Engine, SessionLocal factory, and get_db dependency
│   ├── models/
│   │   ├── __init__.py                                   # Model exports (Company, Department, Designation)
│   │   ├── company.py                                    # Company model (company_master)
│   │   ├── department.py                                 # Department model (department_master)
│   │   └── designation.py                                # Designation model (designation_master)
│   ├── schemas/
│   │   ├── __init__.py                                   # Schema exports
│   │   ├── company.py                                    # Company schemas
│   │   ├── department.py                                 # Department schemas
│   │   └── designation.py                                # Designation schemas (Base, Create, Update, Read)
│   ├── scripts/
│   │   ├── __init__.py
│   │   ├── seed_companies.py                             # Idempotent company seeding script (3 records)
│   │   ├── seed_departments.py                           # Idempotent department seeding script (12 records)
│   │   └── seed_designations.py                          # Idempotent designation seeding script (18 records)
│   └── services/
│       ├── __init__.py
│       └── database_health.py                            # Safe database health checking service
├── tests/
│   ├── __init__.py
│   ├── test_alembic.py                                   # Alembic configuration and baseline safety tests
│   ├── test_company.py                                   # Company model, schemas, migration, and seed tests
│   ├── test_database.py                                  # Session, config, and database health unit tests
│   ├── test_department.py                                # Department model, schemas, migration, and seed tests
│   ├── test_designation.py                               # Designation model, schemas, migration, and seed tests
│   └── test_health.py                                    # API and admin health check tests
├── .env                                                  # Local uncommitted environment configuration
├── .env.example                                          # Safe environment variable template
├── .gitignore                                            # Backend gitignore rules
├── requirements.txt                                      # Backend dependencies
└── README.md                                             # Backend documentation
```
