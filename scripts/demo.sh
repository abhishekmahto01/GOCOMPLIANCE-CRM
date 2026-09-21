#!/usr/bin/env bash

# ==============================================================================
# GOCOMPLIANCE CRM - Public Demo Launcher (Cloudflare Quick Tunnels)
# Exposes Main CRM (5173) and Admin UI (8001) via public trycloudflare.com URLs
# Frontend requests proxy /api calls internally to local FastAPI (8000).
# ==============================================================================

set -eo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

BACKEND_PID=""
FRONTEND_PID=""
ADMIN_PID=""
MAIN_TUNNEL_PID=""
ADMIN_TUNNEL_PID=""
STACK_PRE_EXISTING=false
DEMO_TMP_DIR=""

# Helper function: Check if a command exists in PATH
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Helper function: Check if a port is currently in use
is_port_in_use() {
    local port="$1"
    lsof -i ":$port" -sTCP:LISTEN -P >/dev/null 2>&1
}

# Helper function: Check if an HTTP service is responding
check_http_service() {
    local url="$1"
    local status
    status=$(curl -s -m 2 -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || true)
    if [ "$status" = "200" ] || [ "$status" = "301" ] || [ "$status" = "302" ] || [ "$status" = "307" ]; then
        return 0
    fi
    return 1
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
    echo "Stopping Cloudflare demo tunnels..."
    [ -n "$MAIN_TUNNEL_PID" ] && kill_tree "$MAIN_TUNNEL_PID"
    [ -n "$ADMIN_TUNNEL_PID" ] && kill_tree "$ADMIN_TUNNEL_PID"
    wait "$MAIN_TUNNEL_PID" 2>/dev/null || true
    wait "$ADMIN_TUNNEL_PID" 2>/dev/null || true

    if [ "$STACK_PRE_EXISTING" = false ]; then
        echo "Stopping locally launched CRM services..."
        [ -n "$BACKEND_PID" ] && kill_tree "$BACKEND_PID"
        [ -n "$FRONTEND_PID" ] && kill_tree "$FRONTEND_PID"
        [ -n "$ADMIN_PID" ] && kill_tree "$ADMIN_PID"
        wait "$BACKEND_PID" 2>/dev/null || true
        wait "$FRONTEND_PID" 2>/dev/null || true
        wait "$ADMIN_PID" 2>/dev/null || true
    else
        echo "Preserving pre-existing local development services on ports 8000, 5173, and 8001."
    fi

    if [ -n "$DEMO_TMP_DIR" ] && [ -d "$DEMO_TMP_DIR" ]; then
        rm -rf "$DEMO_TMP_DIR"
    fi

    echo "Demo stopped cleanly."
    exit "$exit_code"
}

# Print help message
show_help() {
    echo "GOCOMPLIANCE CRM Cloudflare Quick Tunnel Demo Launcher"
    echo ""
    echo "Usage:"
    echo "  npm run demo         Start or reuse dev stack and create public Cloudflare Quick Tunnels"
    echo "  npm run demo:check   Validate prerequisites for demo mode without starting tunnels"
    echo ""
    echo "Prerequisites:"
    echo "  - cloudflared CLI (brew install cloudflared)"
    echo "  - Node.js & npm"
    echo "  - Python 3.11+ virtual environment with uvicorn"
    echo "  - Running PostgreSQL instance"
    echo ""
    echo "Note:"
    echo "  Both frontends proxy API requests (/api) internally to local FastAPI."
    echo "  FastAPI is not exposed publicly."
    echo "  Press Ctrl+C to stop the demo."
}

# Run all pre-flight prerequisite checks
run_checks() {
    local has_error=0

    echo "========================================"
    echo " GOCOMPLIANCE CRM DEMO PRE-FLIGHT CHECK"
    echo "========================================"

    # 1. System Executables & cloudflared
    echo -n "Checking system executables (bash, node, npm, lsof, curl)... "
    local missing_execs=()
    if ! command_exists bash; then missing_execs+=("bash"); fi
    if ! command_exists node; then missing_execs+=("node"); fi
    if ! command_exists npm; then missing_execs+=("npm"); fi
    if ! command_exists lsof; then missing_execs+=("lsof"); fi
    if ! command_exists curl; then missing_execs+=("curl"); fi

    if [ ${#missing_execs[@]} -ne 0 ]; then
        echo "FAILED"
        echo "  Error: Missing required executables: ${missing_execs[*]}"
        echo "  Fix: Please install missing executables and ensure they are in your PATH."
        has_error=1
    else
        echo "OK"
    fi

    echo -n "Checking cloudflared executable... "
    if ! command_exists cloudflared; then
        echo "FAILED"
        echo "  Error: 'cloudflared' CLI is not installed or not in PATH."
        echo "  Fix: Install cloudflared on macOS using Homebrew:"
        echo "       brew install cloudflared"
        has_error=1
    else
        local cf_ver
        cf_ver=$(cloudflared --version 2>/dev/null || echo "installed")
        echo "OK ($cf_ver)"
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

    # 3. Backend Python Virtual Environment
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

    # 4. Backend .env & Database Connectivity
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

    # 5. Frontend dependencies
    echo -n "Checking frontend dependencies (frontend/ & admin-frontend/)... "
    if [ ! -d "frontend/node_modules" ] || [ ! -d "admin-frontend/node_modules" ]; then
        echo "FAILED"
        echo "  Error: node_modules missing in frontend or admin-frontend."
        echo "  Fix: Run 'cd frontend && npm install' and 'cd admin-frontend && npm install'"
        has_error=1
    else
        echo "OK"
    fi

    echo "========================================"

    if [ "$has_error" -ne 0 ]; then
        echo "Demo pre-flight checks failed. Please address the issues above."
        return 1
    fi

    echo "All pre-flight checks passed."
    return 0
}

# Start or reuse local application stack and launch Cloudflare Quick Tunnels
start_demo() {
    trap cleanup SIGINT SIGTERM EXIT

    DEMO_TMP_DIR=$(mktemp -d -t gocompliance_demo.XXXXXX)
    local main_tunnel_log="$DEMO_TMP_DIR/main_tunnel.log"
    local admin_tunnel_log="$DEMO_TMP_DIR/admin_tunnel.log"

    echo ""
    echo "========================================"
    echo " INITIALIZING DEMO STACK"
    echo "========================================"

    # Check if services are already running and responding
    local backend_ready=false
    local frontend_ready=false
    local admin_ready=false

    if check_http_service "http://localhost:8000/api/health" || check_http_service "http://localhost:8000/docs"; then
        backend_ready=true
    fi
    if check_http_service "http://localhost:5173"; then
        frontend_ready=true
    fi
    if check_http_service "http://localhost:8001"; then
        admin_ready=true
    fi

    if [ "$backend_ready" = true ] && [ "$frontend_ready" = true ] && [ "$admin_ready" = true ]; then
        STACK_PRE_EXISTING=true
        echo "Detected responding development stack on ports 8000, 5173, and 8001."
        echo "Reusing existing application stack."
    else
        STACK_PRE_EXISTING=false
        echo "Starting local application stack..."

        # Verify ports before starting
        if [ "$backend_ready" = false ] && is_port_in_use 8000; then
            echo "Error: Port 8000 is in use by another process that is not responding as expected."
            echo "Please stop the process on port 8000 before running 'npm run demo'."
            exit 1
        fi
        if [ "$frontend_ready" = false ] && is_port_in_use 5173; then
            echo "Error: Port 5173 is in use by another process that is not responding as expected."
            echo "Please stop the process on port 5173 before running 'npm run demo'."
            exit 1
        fi
        if [ "$admin_ready" = false ] && is_port_in_use 8001; then
            echo "Error: Port 8001 is in use by another process that is not responding as expected."
            echo "Please stop the process on port 8001 before running 'npm run demo'."
            exit 1
        fi

        # Start backend if not already ready
        if [ "$backend_ready" = false ]; then
            (
                cd "$REPO_ROOT/backend"
                exec .venv/bin/python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
            ) > >(awk '{ print "[backend]  " $0; fflush(); }') 2>&1 &
            BACKEND_PID=$!
        fi

        # Start main frontend with relative API proxying enabled
        if [ "$frontend_ready" = false ]; then
            (
                cd "$REPO_ROOT/frontend"
                export VITE_API_BASE_URL=""
                exec npm run dev
            ) > >(awk '{ print "[frontend] " $0; fflush(); }') 2>&1 &
            FRONTEND_PID=$!
        fi

        # Start admin frontend with relative API proxying enabled
        if [ "$admin_ready" = false ]; then
            (
                cd "$REPO_ROOT/admin-frontend"
                export VITE_API_BASE_URL=""
                exec npm run dev
            ) > >(awk '{ print "[admin]    " $0; fflush(); }') 2>&1 &
            ADMIN_PID=$!
        fi

        echo -n "Waiting for local services to respond on ports 8000, 5173, 8001... "
        local wait_secs=0
        while [ $wait_secs -lt 30 ]; do
            if check_http_service "http://localhost:8000/api/health" && check_http_service "http://localhost:5173" && check_http_service "http://localhost:8001"; then
                echo "OK"
                break
            fi
            sleep 1
            wait_secs=$((wait_secs + 1))
        done

        if [ $wait_secs -ge 30 ]; then
            echo "FAILED"
            echo "Timed out waiting for local services to start."
            exit 1
        fi
    fi

    echo ""
    echo "Starting Cloudflare Quick Tunnels..."
    echo "  Main CRM -> http://localhost:5173"
    echo "  Admin UI -> http://localhost:8001"

    # Start Main CRM tunnel
    cloudflared tunnel \
        --protocol http2 \
        --url http://localhost:5173 \
        --loglevel info > "$main_tunnel_log" 2>&1 &
    MAIN_TUNNEL_PID=$!

    # Start Admin UI tunnel
    cloudflared tunnel \
        --protocol http2 \
        --url http://localhost:8001 \
        --loglevel info > "$admin_tunnel_log" 2>&1 &
    ADMIN_TUNNEL_PID=$!

    echo -n "Acquiring public tunnel URLs from Cloudflare... "
    local main_url=""
    local admin_url=""
    local elapsed=0

    while [ $elapsed -lt 30 ]; do
        if [ -z "$main_url" ] && [ -f "$main_tunnel_log" ]; then
            main_url=$(grep -Eo 'https://[a-zA-Z0-9-]+\.trycloudflare\.com' "$main_tunnel_log" | head -n 1 || true)
        fi
        if [ -z "$admin_url" ] && [ -f "$admin_tunnel_log" ]; then
            admin_url=$(grep -Eo 'https://[a-zA-Z0-9-]+\.trycloudflare\.com' "$admin_tunnel_log" | head -n 1 || true)
        fi

        if [ -n "$main_url" ] && [ -n "$admin_url" ]; then
            echo "OK"
            break
        fi

        # Check if tunnels died early
        if ! kill -0 "$MAIN_TUNNEL_PID" 2>/dev/null; then
            echo "FAILED (Main CRM tunnel exited unexpectedly)"
            cat "$main_tunnel_log"
            exit 1
        fi
        if ! kill -0 "$ADMIN_TUNNEL_PID" 2>/dev/null; then
            echo "FAILED (Admin UI tunnel exited unexpectedly)"
            cat "$admin_tunnel_log"
            exit 1
        fi

        sleep 1
        elapsed=$((elapsed + 1))
    done

    if [ -z "$main_url" ] || [ -z "$admin_url" ]; then
        echo "FAILED"
        echo "Could not capture public URLs from cloudflared within 30 seconds."
        [ -f "$main_tunnel_log" ] && echo "Main Tunnel Log:" && cat "$main_tunnel_log"
        [ -f "$admin_tunnel_log" ] && echo "Admin Tunnel Log:" && cat "$admin_tunnel_log"
        exit 1
    fi

    echo ""
    echo "=================================================================="
    echo " GOCOMPLIANCE CRM DEMO IS READY"
    echo "=================================================================="
    echo ""
    echo " Local:"
    echo "   Main CRM:  http://localhost:5173"
    echo "   Admin UI:  http://localhost:8001"
    echo "   FastAPI:   http://localhost:8000"
    echo "   API Docs:  http://localhost:8000/docs"
    echo ""
    echo " Public (Cloudflare Quick Tunnels):"
    echo "   Main CRM:  $main_url"
    echo "   Admin UI:  $admin_url"
    echo ""
    echo " Security & Architecture:"
    echo "   • Main CRM and Admin UI are accessible via unique public URLs."
    echo "   • Frontends proxy browser API calls (/api) internally to local FastAPI."
    echo "   • FastAPI is never exposed publicly."
    echo "   • All CRM authentication, roles, and page permissions remain enforced."
    echo ""
    echo " Press Ctrl+C to stop the demo."
    echo "=================================================================="
    echo ""

    # Monitor processes
    while true; do
        if ! kill -0 "$MAIN_TUNNEL_PID" 2>/dev/null; then
            echo ""
            echo "Main CRM tunnel process exited."
            exit 1
        fi
        if ! kill -0 "$ADMIN_TUNNEL_PID" 2>/dev/null; then
            echo ""
            echo "Admin UI tunnel process exited."
            exit 1
        fi
        if [ "$STACK_PRE_EXISTING" = false ]; then
            if [ -n "$BACKEND_PID" ] && ! kill -0 "$BACKEND_PID" 2>/dev/null; then
                echo ""
                echo "[backend] Service process exited."
                exit 1
            fi
            if [ -n "$FRONTEND_PID" ] && ! kill -0 "$FRONTEND_PID" 2>/dev/null; then
                echo ""
                echo "[frontend] Service process exited."
                exit 1
            fi
            if [ -n "$ADMIN_PID" ] && ! kill -0 "$ADMIN_PID" 2>/dev/null; then
                echo ""
                echo "[admin] Service process exited."
                exit 1
            fi
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
    -c|--check|check|demo-check|demo:check)
        run_checks "check_only"
        exit $?
        ;;
    *)
        if ! run_checks "start"; then
            exit 1
        fi
        start_demo
        ;;
esac
