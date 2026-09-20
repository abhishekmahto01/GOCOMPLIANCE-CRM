# Gocompliances CRM - Backend

Production-ready FastAPI backend foundation for Gocompliances CRM.

## Current Stage Scope: Stage 1 (FastAPI Backend Foundation)

This repository contains the Stage 1 FastAPI backend setup:
- Modular application structure (`app/main.py`, `app/admin_app.py`, `app/core/`, `app/api/`, `app/database/`, `app/models/`)
- Main CRM API configured with CORS for React frontend (`http://localhost:5173`)
- Independent Admin panel placeholder application
- Centralized configuration via `pydantic-settings`
- Health check endpoints and automated tests with `pytest`

> **Note on Database Connectivity:**
> Stage 1 contains only database architectural placeholders (`app/database/base.py`, `app/database/session.py`). Actual PostgreSQL database connectivity, SQLAlchemy engine/session setup, ORM models, and migrations will be implemented in **Stage 2**.

---

## Getting Started (macOS Setup)

### 1. Prerequisites
- Python 3.11+
- Virtual environment tool (`venv`)

### 2. Setup Virtual Environment and Install Dependencies

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Environment Configuration

Copy `.env.example` to create your local `.env` configuration:

```bash
cp .env.example .env
```

---

## Running the Applications

### 1. Main CRM API (Port 8000)

Run the main application server:

```bash
uvicorn app.main:app --reload --port 8000
```

- **Health Check Endpoint:** [http://localhost:8000/api/health](http://localhost:8000/api/health)
- **Interactive Swagger Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Documentation:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **OpenAPI JSON:** [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

**Expected Health Response:**
```json
{
  "status": "healthy",
  "service": "gocompliance-api"
}
```

### 2. Admin Panel Placeholder (Port 8001)

Run the independent admin application:

```bash
uvicorn app.admin_app:app --reload --port 8001
```

- **Health Check Endpoint:** [http://localhost:8001/health](http://localhost:8001/health)
- **Interactive Swagger Docs:** [http://localhost:8001/docs](http://localhost:8001/docs)
- **ReDoc Documentation:** [http://localhost:8001/redoc](http://localhost:8001/redoc)
- **OpenAPI JSON:** [http://localhost:8001/openapi.json](http://localhost:8001/openapi.json)

**Expected Health Response:**
```json
{
  "status": "healthy",
  "service": "gocompliance-admin"
}
```

---

## Running Tests

Execute the automated test suite with `pytest`:

```bash
pytest -v
```

This verifies:
- `GET /api/health` on the Main API returns HTTP 200 and expected payload.
- `GET /health` on the Admin App returns HTTP 200 and expected payload.

---

## Project Structure

```text
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # Main CRM FastAPI application (Port 8000)
│   ├── admin_app.py         # Database Admin placeholder application (Port 8001)
│   ├── api/
│   │   ├── __init__.py
│   │   └── health.py        # Health check router (/api/health)
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py        # Pydantic BaseSettings configuration
│   ├── database/
│   │   ├── __init__.py
│   │   ├── base.py          # Declarative base placeholder (Stage 2)
│   │   └── session.py       # Session & engine placeholder (Stage 2)
│   └── models/
│       └── __init__.py      # Domain & ORM models placeholder (Stage 2)
├── tests/
│   ├── __init__.py
│   └── test_health.py       # Automated health check tests
├── .env.example             # Safe environment variable template
├── .gitignore               # Backend gitignore rules
├── requirements.txt         # Stage 1 Python dependencies
└── README.md                # Backend documentation
```
