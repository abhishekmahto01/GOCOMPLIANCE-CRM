# GOCOMPLIANCE CRM

Enterprise CRM platform with centralized administration, role-based access control, and multi-tenant department management.

> **Note:** The unified development launcher (`npm run dev`) is intended for **local development only**.

---

## Quick Start (Single Command)

To validate prerequisites and launch all three local development services concurrently:

```bash
cd /Users/abhishekmahto/Desktop/gocompliance-crm
npm run dev
```

### Application Services & URLs

Once started, the application services are accessible at:

| Service | URL | Description |
| :--- | :--- | :--- |
| **Main CRM Frontend** | `http://localhost:5173` | Main CRM web application (Director / Manager / Employee) |
| **FastAPI Backend** | `http://localhost:8000` | Core REST API service |
| **API Documentation** | `http://localhost:8000/docs` | Interactive Swagger UI API docs |
| **Admin UI** | `http://localhost:8001` | System Administration portal (`admin-frontend/`) |

---

## Stopping Services

To stop all running services started by `npm run dev`:
* Press **`Ctrl+C`** in the terminal running `npm run dev`.
* The launcher handles graceful shutdown of all spawned child processes and frees ports automatically.

---

## Development Prerequisites

Ensure the following prerequisites are met before running the launcher:

1. **System Tools**:
   - `bash` (macOS default or newer)
   - `Node.js` (v18+ recommended) & `npm`
   - `Python` (v3.10+ recommended)
   - `PostgreSQL` (v14+ running on port `5432`)
   - `lsof` (standard on macOS)

2. **PostgreSQL Database**:
   - PostgreSQL must already be running locally.
   - The launcher will **not** start/stop PostgreSQL or automatically run destructive database commands.

---

## Initial Workspace Setup

If setting up the repository for the first time:

### 1. Backend Setup

```bash
cd backend

# Create Python virtual environment
python3 -m venv .venv

# Activate and install dependencies
source .venv/bin/activate
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your PostgreSQL credentials and JWT secret key:
# DATABASE_URL=postgresql+psycopg://username:password@localhost:5432/is_gocompliance_db
# JWT_SECRET_KEY=your_secure_random_key_at_least_32_chars
```

### 2. Main CRM Frontend Setup

```bash
cd frontend
npm install
```

### 3. Admin UI Setup

```bash
cd admin-frontend
npm install
```

---

## Available Root Commands

| Command | Description |
| :--- | :--- |
| `npm run dev` | Run pre-flight checks and launch all 3 services concurrently with log prefixes |
| `npm run dev:check` | Validate all directory structures, virtual environments, dependencies, DB connectivity, and ports without starting any service |

---

## Port Conflict Troubleshooting

The development services require ports `8000`, `5173`, and `8001`. If any port is occupied, `npm run dev` will block startup to prevent broken or partial states.

### Inspect Occupied Ports:
```bash
lsof -i :8000 -i :5173 -i :8001 -sTCP:LISTEN -P
```

### Port Mapping:
- **Port 8000**: Required by FastAPI backend (`backend/`)
- **Port 5173**: Required by Main CRM frontend (`frontend/`)
- **Port 8001**: Required by Admin UI (`admin-frontend/`)

If a previous process is still running, terminate that specific process before launching `npm run dev`.

---

## Individual Service Startup Commands

If you need to run or debug services individually:

### FastAPI Backend (`http://localhost:8000`)
```bash
cd backend
.venv/bin/python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Main CRM Frontend (`http://localhost:5173`)
```bash
cd frontend
npm run dev
```

### Admin UI (`http://localhost:8001`)
```bash
cd admin-frontend
npm run dev
```
