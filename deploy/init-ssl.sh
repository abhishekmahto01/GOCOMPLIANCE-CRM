#!/bin/bash
set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if [ ! -f .env ]; then
    echo "[-] ERROR: .env file not found in root directory!"
    echo "    Please copy .env.production.example to .env and configure your domains."
    exit 1
fi

# Load variables from .env
set -a
. ./.env
set +a

if [ -z "$MAIN_DOMAIN" ] || [ -z "$ADMIN_DOMAIN" ] || [ -z "$CERTBOT_EMAIL" ]; then
    echo "[-] ERROR: MAIN_DOMAIN, ADMIN_DOMAIN, and CERTBOT_EMAIL must be defined in .env"
    exit 1
fi

DOMAINS=("$MAIN_DOMAIN" "$ADMIN_DOMAIN")
CERTBOT_DIR="./deploy/certbot"
CONF_DIR="$CERTBOT_DIR/conf"
WWW_DIR="$CERTBOT_DIR/www"

mkdir -p "$CONF_DIR" "$WWW_DIR"

echo "==> Step 1: Checking SSL certificate placeholders..."
for domain in "${DOMAINS[@]}"; do
    live_dir="$CONF_DIR/live/$domain"
    if [ ! -f "$live_dir/fullchain.pem" ]; then
        echo "--> Generating temporary certificate for $domain to allow initial Nginx start..."
        mkdir -p "$live_dir"
        openssl req -x509 -nodes -newkey rsa:2048 -days 1 \
            -keyout "$live_dir/privkey.pem" \
            -out "$live_dir/fullchain.pem" \
            -subj "/CN=localhost"
    else
        echo "--> Certificate already exists for $domain"
    fi
done

echo "==> Step 2: Starting Nginx..."
docker compose --env-file .env up -d nginx

echo "==> Step 3: Requesting genuine Let's Encrypt certificates..."
for domain in "${DOMAINS[@]}"; do
    live_dir="$CONF_DIR/live/$domain"
    # Check if the existing cert is self-signed (CN=localhost) before removing
    if [ -f "$live_dir/fullchain.pem" ]; then
        if openssl x509 -in "$live_dir/fullchain.pem" -noout -subject 2>/dev/null | grep -q "localhost"; then
            echo "--> Removing temporary dummy cert for $domain..."
            rm -rf "$live_dir"
        fi
    fi

    echo "--> Requesting SSL certificate for $domain..."
    docker compose --env-file .env run --rm --entrypoint "\
        certbot certonly --webroot -w /var/www/certbot \
        --email $CERTBOT_EMAIL \
        -d $domain \
        --rsa-key-size 4096 \
        --agree-tos \
        --non-interactive" certbot
done

echo "==> Step 4: Reloading Nginx with new certificates..."
docker compose --env-file .env exec nginx nginx -s reload

echo ""
echo "=============================================================="
echo "[+] SUCCESS: SSL certificates installed and Nginx active!"
echo "    Main CRM:     https://$MAIN_DOMAIN"
echo "    Admin Portal: https://$ADMIN_DOMAIN"
echo "=============================================================="
