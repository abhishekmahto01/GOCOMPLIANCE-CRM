# Gocompliances CRM - Backend

Production-ready FastAPI backend foundation for Gocompliances CRM.

## Current Stage Scope: Stage 2 (PostgreSQL Connectivity)

This stage establishes secure, production-grade PostgreSQL database connectivity:
- SQLAlchemy 2.x declarative base (`Base`) and session factory (`SessionLocal`).
- Psycopg 3 (`psycopg[binary]`) driver integration.
- Connection pooling with `pool_pre_ping=True` and configurable timeouts.
- Request-scoped database session dependency (`get_db`) with guaranteed `try/finally` cleanup.
- Centralized configuration via `pydantic-settings` with credentials masking.
- Database health checking service and dedicated endpoint (`GET /api/health/database`).
- Complete automated unit tests with database isolation and mock fixtures.

> **Note on Database Models & Migrations:**
> In Stage 2, only database connectivity and health monitoring are established. **No tables, ORM business models, or Alembic migrations are created.** Schema definitions and migrations will begin in **Stage 3**.

---

## Getting Started (macOS Setup)

### 1. Prerequisites
- Python 3.11+
- PostgreSQL server running locally on port `5432` with database `is_gocompliance_db`
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

#### Database URL Format:

* **With password authentication:**
  ```env
  DATABASE_URL=postgresql+psycopg://YOUR_USERNAME:YOUR_PASSWORD@localhost:5432/is_gocompliance_db
  ```

* **Without password (macOS local / peer trust):**
  ```env
  DATABASE_URL=postgresql+psycopg://YOUR_USERNAME@localhost:5432/is_gocompliance_db
  ```

> **Special Characters & URL-Encoding:**
> If your password contains special characters (such as `@`, `:`, `/`, `?`, `#`, `%`), URL-encode them (for example, `%20` for space, `%40` for `@`).
> In Python:
> ```python
> from urllib.parse import quote_plus
> encoded_password = quote_plus("your@password#")
> ```

---

## Running the Applications

### 1. Main CRM API (Port 8000)

Run the main application server:

```bash
uvicorn app.main:app --reload --port 8000
```

- **API Health Check Endpoint:** [http://localhost:8000/api/health](http://localhost:8000/api/health)
- **Database Health Endpoint:** [http://localhost:8000/api/health/database](http://localhost:8000/api/health/database)
- **Interactive Swagger Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Documentation:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **OpenAPI JSON:** [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

**Expected API Health Response (`GET /api/health`):**
```json
{
  "status": "healthy",
  "service": "gocompliance-api"
}
```

**Expected Database Health Response (`GET /api/health/database`):**
```json
{
  "status": "healthy",
  "service": "postgresql",
  "database": "is_gocompliance_db",
  "detail": null
}
```

*(If unreachable, returns HTTP `503 Service Unavailable` with `status: unhealthy` and a safe message without leaking credentials).*

### 2. Admin Panel Placeholder (Port 8001)

Run the independent admin application:

```bash
uvicorn app.admin_app:app --reload --port 8001
```

- **Health Check Endpoint:** [http://localhost:8001/health](http://localhost:8001/health)
- **Interactive Swagger Docs:** [http://localhost:8001/docs](http://localhost:8001/docs)

---

## Running Automated Tests

Execute the test suite using `pytest`:

```bash
pytest -v
```

All 10 tests run in isolation using mocking (no real database connection required for unit tests).

---

## Troubleshooting

### `FATAL: role "postgres" does not exist`
On macOS (Homebrew PostgreSQL), the default role is typically your macOS system username rather than `postgres`.

Check your current PostgreSQL username:
```bash
psql -d is_gocompliance_db -Atc "SELECT current_user;"
```

Then update `DATABASE_URL` in `backend/.env` with that username:
```env
DATABASE_URL=postgresql+psycopg://YOUR_ACTUAL_USERNAME@localhost:5432/is_gocompliance_db
```

---

## Project Structure

```text
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                   # Main CRM FastAPI application (Port 8000)
│   ├── admin_app.py              # Database Admin placeholder application (Port 8001)
│   ├── api/
│   │   ├── __init__.py
│   │   └── health.py             # Health check endpoints (/api/health, /api/health/database)
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py             # Pydantic BaseSettings with credentials masking
│   ├── database/
│   │   ├── __init__.py
│   │   ├── base.py               # SQLAlchemy 2 DeclarativeBase
│   │   └── session.py            # Engine, SessionLocal factory, and get_db dependency
│   ├── models/
│   │   └── __init__.py           # Models placeholder (Stage 3)
│   └── services/
│       ├── __init__.py
│       └── database_health.py    # Safe database health checking service
├── tests/
│   ├── __init__.py
│   ├── test_database.py          # Session, config, and database health unit tests
│   └── test_health.py            # API and admin health check tests
├── .env                          # Local uncommitted environment configuration
├── .env.example                  # Safe environment variable template
├── .gitignore                    # Backend gitignore rules
├── requirements.txt              # Backend dependencies
└── README.md                     # Backend documentation
```
