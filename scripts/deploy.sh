#!/usr/bin/env bash
# ==============================================================================
# GOCOMPLIANCE CRM - One-Command Local Deploy Script
# Usage: npm run deploy
# What it does:
#   1. Rsyncs local code to Hostinger VPS (excludes node_modules, .venv, dist)
#   2. SSH into VPS and runs: docker compose build + up -d
#   3. Runs any pending database migrations (via entrypoint.sh auto-migration)
# ==============================================================================

set -eo pipefail

# ── Configuration ─────────────────────────────────────────────────────────────
VPS_USER="root"
VPS_HOST="187.126.124.74"
VPS_PATH="/var/www/gocompliance-crm"
LOCAL_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/"

# ── Colors ────────────────────────────────────────────────────────────────────
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m' # No Color

log()    { echo -e "${CYAN}[deploy]${NC} $*"; }
success(){ echo -e "${GREEN}[✔ done]${NC} $*"; }
warn()   { echo -e "${YELLOW}[  warn]${NC} $*"; }
error()  { echo -e "${RED}[ error]${NC} $*"; exit 1; }

echo ""
echo -e "${CYAN}══════════════════════════════════════════════${NC}"
echo -e "${CYAN}    GOCOMPLIANCE CRM  —  Deploy to VPS        ${NC}"
echo -e "${CYAN}══════════════════════════════════════════════${NC}"
echo ""

# ── Step 1: Sync code to VPS ───────────────────────────────────────────────────
log "Step 1/3 — Syncing code to ${VPS_USER}@${VPS_HOST}:${VPS_PATH} ..."

rsync -avz --delete \
  --exclude '.git' \
  --exclude '.venv' \
  --exclude 'node_modules' \
  --exclude 'dist' \
  --exclude '__pycache__' \
  --exclude '*.pyc' \
  --exclude '.pytest_cache' \
  --exclude 'backend/uploads' \
  --exclude 'deploy/certbot' \
  --exclude 'backend/backups' \
  --exclude '.env' \
  "${LOCAL_PATH}" "${VPS_USER}@${VPS_HOST}:${VPS_PATH}/"

success "Code synced."

# ── Step 2: Rebuild & restart containers on VPS ────────────────────────────────
log "Step 2/3 — Building Docker images & restarting containers on VPS..."

ssh "${VPS_USER}@${VPS_HOST}" bash -s << 'REMOTE_SCRIPT'
set -e
cd /var/www/gocompliance-crm

# Guard: ensure .env exists before proceeding
if [ ! -f .env ]; then
  echo "[-] ERROR: .env file not found at /var/www/gocompliance-crm/.env"
  echo "    Please create it first (see DEPLOYMENT_GUIDE.md Step 4)"
  exit 1
fi

echo "--> .env found. Verified variables:"
grep -E "^(MAIN_DOMAIN|ADMIN_DOMAIN|POSTGRES_USER|POSTGRES_DB)=" .env || true

# Guard: MAIN_DOMAIN must be the main CRM domain (e.g. workflow.*), never the admin.* subdomain.
# A swapped value makes nginx serve the wrong app on each domain.
MAIN_DOMAIN_VALUE=$(grep -E "^MAIN_DOMAIN=" .env | head -1 | cut -d= -f2- | tr -d "\"' ")
ADMIN_DOMAIN_VALUE=$(grep -E "^ADMIN_DOMAIN=" .env | head -1 | cut -d= -f2- | tr -d "\"' ")
case "$MAIN_DOMAIN_VALUE" in
  admin.*|"")
    echo "[-] ERROR: MAIN_DOMAIN='${MAIN_DOMAIN_VALUE}' looks wrong. It must be the main CRM domain (e.g. workflow.gocompliances.com)."
    echo "    ADMIN_DOMAIN is currently '${ADMIN_DOMAIN_VALUE}'. Fix .env on the server and run deploy again."
    exit 1
    ;;
esac

echo "--> Building updated Docker images..."
docker compose --env-file .env build --parallel

echo "--> Restarting containers (zero-downtime rolling update)..."
docker compose --env-file .env up -d --remove-orphans

# nginx renders deploy/nginx/templates/*.template only when the container starts, and
# `up -d` does not recreate it when only the mounted template changed. Force-recreate it
# so routing changes are always applied.
echo "--> Recreating nginx to apply the latest routing config..."
docker compose --env-file .env up -d --force-recreate --no-deps nginx
sleep 3
if ! docker compose --env-file .env exec -T nginx nginx -t; then
  echo "[-] ERROR: nginx config test failed. Check: docker compose logs nginx"
  exit 1
fi

echo "--> Waiting for backend to be healthy..."
sleep 5
docker compose --env-file .env ps
REMOTE_SCRIPT

success "Containers rebuilt and running."

# ── Step 3: Show live status ───────────────────────────────────────────────────
log "Step 3/3 — Live container status:"

ssh "${VPS_USER}@${VPS_HOST}" bash -s << 'REMOTE_SCRIPT'
cd /var/www/gocompliance-crm
docker compose --env-file .env ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
REMOTE_SCRIPT

echo ""
echo -e "${GREEN}══════════════════════════════════════════════${NC}"
echo -e "${GREEN}  ✔  Deploy complete! Your app is live.       ${NC}"
echo -e "${GREEN}══════════════════════════════════════════════${NC}"
echo ""

# Load MAIN_DOMAIN/ADMIN_DOMAIN from local .env if available to print URLs
if [ -f "$(dirname "${BASH_SOURCE[0]}")/../.env" ]; then
  # shellcheck disable=SC1090
  set -a; . "$(dirname "${BASH_SOURCE[0]}")/../.env"; set +a
fi

if [ -n "$MAIN_DOMAIN" ]; then
  echo -e "  ${CYAN}Main CRM:${NC}     https://${MAIN_DOMAIN}"
  echo -e "  ${CYAN}Admin Portal:${NC} https://${ADMIN_DOMAIN}"
  echo -e "  ${CYAN}API Docs:${NC}     https://${MAIN_DOMAIN}/docs"
else
  echo -e "  ${CYAN}Main CRM:${NC}     https://workflow.gocompliances.com"
  echo -e "  ${CYAN}Admin Portal:${NC} https://admin.gocompliances.com"
  echo -e "  ${CYAN}API Docs:${NC}     https://workflow.gocompliances.com/docs"
fi

echo ""
