#!/usr/bin/env bash

# ==============================================================================
# GOCOMPLIANCE CRM - Local Development Launcher
# Starts FastAPI Backend (8000), Main CRM Frontend (5173), and Admin UI (8001)
# ==============================================================================

set -eo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

BACKEND_PID=""
FRONTEND_PID=""
ADMIN_PID=""

# Helper function: Check if a command exists in PATH
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Helper function: Check if a port is currently in use
is_port_in_use() {
    local port="$1"
    lsof -i ":$port" -sTCP:LISTEN -P >/dev/null 2>&1
}

# Helper function: Check if package.json has a specified npm script
has_npm_script() {
    local pkg_file="$1"
    local script_name="$2"
    if [ ! -f "$pkg_file" ]; then
        return 1
    fi
    if command_exists node; then
        node -e "try { const pkg=require('./$pkg_file'); process.exit(pkg.scripts && pkg.scripts['$script_name'] ? 0 : 1); } catch(e) { process.exit(1); }" 2>/dev/null
    else
        grep -q "\"$script_name\":" "$pkg_file" 2>/dev/null
    fi
}

# Recursively terminate a process and its child processes
kill_tree() {
    local pid="$1"
    [ -z "$pid" ] && return 0
    local children
    children=$(pgrep -P "$pid" 2>/dev/null || true)
    for child in $children; do
        kill_tree "$child"
    done
    kill -TERM "$pid" 2>/dev/null || true
}

# Cleanup trap handler for graceful shutdown
cleanup() {
    local exit_code=$?
    trap - SIGINT SIGTERM EXIT
    echo ""
    echo "Stopping GOCOMPLIANCE CRM development services..."
    [ -n "$BACKEND_PID" ] && kill_tree "$BACKEND_PID"
    [ -n "$FRONTEND_PID" ] && kill_tree "$FRONTEND_PID"
    [ -n "$ADMIN_PID" ] && kill_tree "$ADMIN_PID"
    wait "$BACKEND_PID" 2>/dev/null || true
    wait "$FRONTEND_PID" 2>/dev/null || true
    wait "$ADMIN_PID" 2>/dev/null || true
    echo "All services stopped cleanly."
    exit "$exit_code"
}

# Print help message
show_help() {
    echo "GOCOMPLIANCE CRM Development Launcher"
    echo ""
    echo "Usage:"
    echo "  npm run dev         Validate prerequisites and start all three services"
    echo "  npm run dev:check   Validate prerequisites and port availability without starting services"
    echo ""
    echo "Services:"
    echo "  FastAPI Backend:   http://localhost:8000"
    echo "  API Documentation: http://localhost:8000/docs"
    echo "  Main CRM Frontend: http://localhost:5173"
    echo "  Admin UI:          http://localhost:8001"
    echo ""
    echo "Note:"
    echo "  Services started with 'npm run dev' can be stopped cleanly by pressing Ctrl+C."
}

# Run all pre-flight prerequisite checks
run_checks() {
    local has_error=0

    echo "========================================"
    echo " GOCOMPLIANCE CRM PRE-FLIGHT CHECK"
    echo "========================================"

    # 1. System Executables
    echo -n "Checking system executables (bash, node, npm, lsof)... "
    local missing_execs=()
    if ! command_exists bash; then missing_execs+=("bash"); fi
    if ! command_exists node; then missing_execs+=("node"); fi
    if ! command_exists npm; then missing_execs+=("npm"); fi
    if ! command_exists lsof; then missing_execs+=("lsof"); fi

    if [ ${#missing_execs[@]} -ne 0 ]; then
        echo "FAILED"
        echo "  Error: Missing required executables: ${missing_execs[*]}"
        echo "  Fix: Please install missing executables and ensure they are in your PATH."
        has_error=1
    else
        echo "OK"
    fi

    # 2. Application Directories
    echo -n "Checking application directories... "
    local missing_dirs=()
    if [ ! -d "backend" ]; then missing_dirs+=("backend/"); fi
    if [ ! -d "frontend" ]; then missing_dirs+=("frontend/"); fi
    if [ ! -d "admin-frontend" ]; then missing_dirs+=("admin-frontend/"); fi

    if [ ${#missing_dirs[@]} -ne 0 ]; then
        echo "FAILED"
        echo "  Error: Missing required directories: ${missing_dirs[*]}"
        echo "  Fix: Ensure you run the script from the repository root."
        has_error=1
    else
        echo "OK"
    fi

    # 3. Backend Python Virtual Environment & Uvicorn
    echo -n "Checking backend Python virtual environment... "
    if [ ! -f "backend/.venv/bin/python" ]; then
        echo "FAILED"
        echo "  Error: backend/.venv/bin/python not found."
        echo "  Fix: Set up backend virtual environment:"
        echo "       (cd backend && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt)"
        has_error=1
    else
        if ! backend/.venv/bin/python -c "import uvicorn" 2>/dev/null; then
            echo "FAILED"
            echo "  Error: Uvicorn cannot be imported in backend/.venv."
            echo "  Fix: Install backend dependencies:"
            echo "       (cd backend && .venv/bin/pip install -r requirements.txt)"
            has_error=1
        else
            echo "OK"
        fi
    fi

    # 4. Backend .env & PostgreSQL configuration
    echo -n "Checking backend environment configuration (.env)... "
    if [ ! -f "backend/.env" ]; then
        echo "FAILED"
        echo "  Error: backend/.env not found."
        echo "  Fix: Create backend/.env with DATABASE_URL and JWT_SECRET_KEY."
        has_error=1
    else
        echo "OK"

        echo -n "Checking PostgreSQL configuration & connectivity... "
        local db_check_out
        db_check_out=$( (cd backend && .venv/bin/python -c "
import sys
try:
    from app.core.config import settings
    from sqlalchemy import text
    from app.database.session import engine
    with engine.connect() as conn:
        conn.execute(text('SELECT 1'))
    print('OK')
except Exception as e:
    err_type = type(e).__name__
    print(f'ERROR:{err_type}')
" ) 2>/dev/null || echo "ERROR:ExecutionFailed" )

        if [ "$db_check_out" = "OK" ]; then
            echo "OK"
        else
            echo "FAILED"
            echo "  Error: Database connection check failed ($db_check_out)."
            echo "  Fix: Ensure PostgreSQL is running on localhost:5432 and credentials in backend/.env are valid."
            has_error=1
        fi
    fi

    # 5. Main CRM Frontend (frontend/)
    echo -n "Checking main CRM frontend dependencies (frontend/)... "
    if [ ! -f "frontend/package.json" ]; then
        echo "FAILED"
        echo "  Error: frontend/package.json missing."
        has_error=1
    elif [ ! -d "frontend/node_modules" ]; then
        echo "FAILED"
        echo "  Error: frontend/node_modules directory missing."
        echo "  Fix: Run '(cd frontend && npm install)'"
        has_error=1
    elif ! has_npm_script "frontend/package.json" "dev"; then
        echo "FAILED"
        echo "  Error: 'dev' script missing in frontend/package.json."
        has_error=1
    else
        echo "OK"
    fi

    # 6. Admin Frontend (admin-frontend/)
    echo -n "Checking admin frontend dependencies (admin-frontend/)... "
    if [ ! -f "admin-frontend/package.json" ]; then
        echo "FAILED"
        echo "  Error: admin-frontend/package.json missing."
        has_error=1
    elif [ ! -d "admin-frontend/node_modules" ]; then
        echo "FAILED"
        echo "  Error: admin-frontend/node_modules directory missing."
        echo "  Fix: Run '(cd admin-frontend && npm install)'"
        has_error=1
    elif ! has_npm_script "admin-frontend/package.json" "dev"; then
        echo "FAILED"
        echo "  Error: 'dev' script missing in admin-frontend/package.json."
        has_error=1
    else
        echo "OK"
    fi

    # 7. Port availability check (8000, 5173, 8001)
    echo -n "Checking port availability (8000, 5173, 8001)... "
    local port_conflicts=()
    if is_port_in_use 8000; then
        port_conflicts+=("Port 8000 is occupied (required by FastAPI backend: http://localhost:8000)")
    fi
    if is_port_in_use 5173; then
        port_conflicts+=("Port 5173 is occupied (required by Main CRM frontend: http://localhost:5173)")
    fi
    if is_port_in_use 8001; then
        port_conflicts+=("Port 8001 is occupied (required by Admin UI: http://localhost:8001)")
    fi

    if [ ${#port_conflicts[@]} -ne 0 ]; then
        echo "FAILED"
        for conflict in "${port_conflicts[@]}"; do
            echo "  Error: $conflict"
        done
        echo "  Fix: Stop the process(es) currently using these ports before running 'npm run dev'."
        has_error=1
    else
        echo "OK"
    fi

    echo "========================================"

    if [ "$has_error" -ne 0 ]; then
        echo "Pre-flight checks failed. Please address the issues above."
        return 1
    fi

    echo "All pre-flight checks passed."
    return 0
}

# Start all three application services
start_services() {
    trap cleanup SIGINT SIGTERM EXIT

    echo ""
    echo "GOCOMPLIANCE CRM DEVELOPMENT"
    echo "----------------------------------------"
    echo "Backend:       http://localhost:8000"
    echo "API Docs:      http://localhost:8000/docs"
    echo "Main CRM:      http://localhost:5173"
    echo "Admin UI:      http://localhost:8001"
    echo "----------------------------------------"
    echo "Press Ctrl+C to stop all services."
    echo ""

    # Start backend
    (
        cd "$REPO_ROOT/backend"
        exec .venv/bin/python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
    ) > >(awk '{ print "[backend]  " $0; fflush(); }') 2>&1 &
    BACKEND_PID=$!

    # Start main frontend
    (
        cd "$REPO_ROOT/frontend"
        exec npm run dev
    ) > >(awk '{ print "[frontend] " $0; fflush(); }') 2>&1 &
    FRONTEND_PID=$!

    # Start admin frontend
    (
        cd "$REPO_ROOT/admin-frontend"
        exec npm run dev
    ) > >(awk '{ print "[admin]    " $0; fflush(); }') 2>&1 &
    ADMIN_PID=$!

    # Monitor child processes: if any exits, terminate remaining services
    while true; do
        if ! kill -0 "$BACKEND_PID" 2>/dev/null; then
            echo ""
            echo "[backend] Service process exited."
            exit 1
        fi
        if ! kill -0 "$FRONTEND_PID" 2>/dev/null; then
            echo ""
            echo "[frontend] Service process exited."
            exit 1
        fi
        if ! kill -0 "$ADMIN_PID" 2>/dev/null; then
            echo ""
            echo "[admin] Service process exited."
            exit 1
        fi
        sleep 1
    done
}

# Main entry point
case "${1:-}" in
    -h|--help|help)
        show_help
        exit 0
        ;;
    -c|--check|check|dev-check|dev:check)
        run_checks "check_only"
        exit $?
        ;;
    *)
        if ! run_checks "start"; then
            exit 1
        fi
        start_services
        ;;
esac
