#!/usr/bin/env bash
# ==============================================================================
# GOCOMPLIANCE CRM - Hostinger VPS Automated Setup Script
# Run this on your Ubuntu VPS (ssh root@187.126.124.74)
# ==============================================================================

set -eo pipefail

echo "=============================================================="
echo "    GOCOMPLIANCE CRM - Hostinger VPS Setup & Installation    "
echo "=============================================================="

# Ensure running as root
if [ "$EUID" -ne 0 ]; then
  echo "[-] Please run this script as root (sudo ./deploy/setup-vps.sh)"
  exit 1
fi

echo "--> [1/5] Updating system packages..."
apt-get update -y
apt-get install -y ca-certificates curl gnupg lsb-release openssl git ufw

echo "--> [2/5] Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    echo "    Installing Docker Engine and Docker Compose Plugin..."
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
    systemctl start docker
    echo "    [✔] Docker installed successfully."
else
    echo "    [✔] Docker is already installed."
fi

echo "--> [3/5] Configuring firewall (UFW)..."
ufw allow 22/tcp comment 'SSH' || true
ufw allow 80/tcp comment 'HTTP' || true
ufw allow 443/tcp comment 'HTTPS' || true
ufw --force enable || true

echo "--> [4/5] Preparing environment configuration..."
if [ ! -f .env ]; then
    echo "    Creating .env from .env.production.example..."
    cp .env.production.example .env

    # Automatically generate strong cryptographically secure secrets
    DB_PASS=$(openssl rand -hex 20)
    JWT_KEY=$(openssl rand -base64 48)

    sed -i "s|replace_with_a_strong_database_password|$DB_PASS|g" .env
    sed -i "s|replace_with_a_secure_jwt_secret_minimum_32_characters|$JWT_KEY|g" .env

    echo "    [✔] Generated secure POSTGRES_PASSWORD and JWT_SECRET_KEY."
    echo ""
    echo "=============================================================="
    echo " [!] ACTION REQUIRED: Configure your domain names in .env"
    echo "     Open .env and set MAIN_DOMAIN, ADMIN_DOMAIN, and CERTBOT_EMAIL."
    echo "     Example: nano .env"
    echo "=============================================================="
else
    echo "    [✔] Existing .env found."
fi

echo "--> [5/5] Setup script completed."
echo "Next step: Review .env and then run:"
echo "    ./deploy/init-ssl.sh"
