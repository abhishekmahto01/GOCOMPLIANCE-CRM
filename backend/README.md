# Gocompliances CRM - Backend

Production-ready FastAPI backend foundation for Gocompliances CRM.

## Current Stage Scope: Stage 4 (Company Master)

This stage establishes the multi-entity company foundation (`company_master`) required for company-specific employee code generation and organization hierarchy:
- SQLAlchemy 2 typed model `Company` mapped to table `company_master`.
- Pydantic v2 schemas (`CompanyBase`, `CompanyCreate`, `CompanyUpdate`, `CompanyRead`) with normalization and validation.
- Alembic schema migration `b445258097c2_create_company_master.py` with unique constraints, check constraints, and indexes.
- Idempotent database seeding script (`app/scripts/seed_companies.py`) using deterministic UUIDs.
- Automated unit test suite with full coverage of models, schemas, migration safety, and seeding.

> **Note on Employee Code Generation & CRUD APIs:**
> Stage 4 establishes the schema and seed data for the 3 operating companies. **Employee code generation logic, Department/User tables, and Company CRUD/Admin UI endpoints will be implemented in subsequent stages.**

---

## Company Master Data Architecture

Gocompliances CRM currently supports three business entities:

| Company Code | Company Name | Employee Code Prefix | Initial Counter (`next_employee_number`) | Status | Sample Future Employee Code |
| :--- | :--- | :---: | :---: | :---: | :--- |
| `GOCOMPLIANCES` | `Gocompliances` | `CG` | `1` | `ACTIVE` | `CG0001`, `CG0002`... |
| `ENTERPERNERSHIP` | `Enterpernership` | `EP` | `1` | `ACTIVE` | `EP0001`, `EP0002`... |
| `BRANDMINGO` | `Brandmingo` | `BM` | `1` | `ACTIVE` | `BM0001`, `BM0002`... |

### `company_master` Column Specifications

| Column | Type | Constraints / Defaults | Description |
| :--- | :--- | :--- | :--- |
| `company_id` | `UUID` | Primary Key, `NOT NULL` | Unique identifier (UUIDv4/v5) |
| `company_code` | `VARCHAR(20)` | `UNIQUE`, `NOT NULL`, Index | Uppercase business identifier code |
| `company_name` | `VARCHAR(150)` | `UNIQUE`, `NOT NULL`, Index | Primary trade / display name |
| `legal_name` | `VARCHAR(200)` | `NULLABLE` | Registered legal corporate entity name |
| `employee_code_prefix` | `VARCHAR(5)` | `UNIQUE`, `NOT NULL`, Check Constraint | 2–5 uppercase letters (`^[A-Z]{2,5}$`) |
| `next_employee_number` | `INTEGER` | `NOT NULL`, Default: `1`, Check: `> 0` | Sequential counter for next employee code |
| `status` | `VARCHAR(20)` | `NOT NULL`, Default: `'ACTIVE'`, Index | Operational status (`ACTIVE`, `INACTIVE`) |
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
Apply all pending schema migrations (including `company_master`):
```bash
alembic upgrade head
```

### 2. Seed Initial Companies
Run the idempotent seeding script:
```bash
python3 -m app.scripts.seed_companies
```

* **Idempotent Seeding Behavior:**
  * First run: Inserts the 3 default company entities.
  * Subsequent runs: Skips existing companies without duplicating or overwriting data.

### 3. Verify Seeded Records via PostgreSQL
```bash
psql -d is_gocompliance_db -c "SELECT company_code, company_name, employee_code_prefix, next_employee_number, status FROM company_master ORDER BY company_code;"
```

---

## Getting Started (macOS Setup)

### 1. Prerequisites
- Python 3.11+
- PostgreSQL running locally on port `5432` with database `is_gocompliance_db`
- Virtual environment tool (`venv`)

### 2. Setup Virtual Environment and Install Dependencies

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Environment Configuration (`.env`)

Copy `.env.example` to create your local `.env` configuration:

```bash
cp .env.example .env
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

All 25 unit tests run in isolation using mocking (no real database connection required for unit tests).

---

## Project Structure

```text
backend/
├── alembic/
│   ├── versions/
│   │   ├── f6d28a5264ee_baseline_database.py       # Empty baseline revision
│   │   └── b445258097c2_create_company_master.py   # Company Master migration
│   ├── env.py                                      # Alembic environment with Base.metadata & settings binding
│   ├── script.py.mako                              # Migration template
│   └── README
├── alembic.ini                                     # Alembic configuration without secrets
├── app/
│   ├── __init__.py
│   ├── main.py                                     # Main CRM FastAPI application (Port 8000)
│   ├── admin_app.py                                # Database Admin placeholder application (Port 8001)
│   ├── api/
│   │   ├── __init__.py
│   │   └── health.py                               # Health check endpoints (/api/health, /api/health/database)
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py                               # Pydantic BaseSettings with credentials masking
│   ├── database/
│   │   ├── __init__.py
│   │   ├── base.py                                 # SQLAlchemy 2 DeclarativeBase
│   │   └── session.py                              # Engine, SessionLocal factory, and get_db dependency
│   ├── models/
│   │   ├── __init__.py                             # Model exports
│   │   └── company.py                              # Company SQLAlchemy 2 model (company_master)
│   ├── schemas/
│   │   ├── __init__.py                             # Schema exports
│   │   └── company.py                              # Company Pydantic schemas (Base, Create, Update, Read)
│   ├── scripts/
│   │   ├── __init__.py
│   │   └── seed_companies.py                       # Idempotent company seeding script
│   └── services/
│       ├── __init__.py
│       └── database_health.py                      # Safe database health checking service
├── tests/
│   ├── __init__.py
│   ├── test_alembic.py                             # Alembic configuration and baseline safety tests
│   ├── test_company.py                             # Company model, schemas, migration, and seed tests
│   ├── test_database.py                            # Session, config, and database health unit tests
│   └── test_health.py                              # API and admin health check tests
├── .env                                            # Local uncommitted environment configuration
├── .env.example                                    # Safe environment variable template
├── .gitignore                                      # Backend gitignore rules
├── requirements.txt                                # Backend dependencies
└── README.md                                       # Backend documentation
```
