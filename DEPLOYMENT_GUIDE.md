# GOCOMPLIANCE CRM - Hostinger VPS Deployment Guide

This guide walks you through deploying **GOCOMPLIANCE CRM** onto your Hostinger Ubuntu VPS using **Docker**, **Docker Compose**, **Nginx Reverse Proxy**, and **Let's Encrypt SSL**.

---

## Architecture Overview

```
                      Internet (Port 80 / 443)
                                 │
                                 ▼
                     ┌───────────────────────┐
                     │   Nginx SSL Gateway   │
                     │  (Let's Encrypt /443) │
                     └───────────┬───────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
         ▼                       ▼                       ▼
┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐
│  FastAPI Backend │   │  CRM Frontend    │   │  Admin Frontend  │
│  (:8000 /api)    │   │  (:80 SPA)       │   │  (:80 SPA)       │
└────────┬─────────┘   └──────────────────┘   └──────────────────┘
         │
         ▼
┌──────────────────┐
│  PostgreSQL 16   │
│  (Docker Volume) │
└──────────────────┘
```

---

## Step 1: DNS Setup in Hostinger DNS Manager

Before generating free SSL certificates with Let's Encrypt, you must point your domain names to your Hostinger VPS IP address:

1. Log in to your **Hostinger Dashboard** -> **Domains** -> **DNS / Nameservers**.
2. Add or update the following **A Records**:

| Type | Name / Host | Points to (Value) | TTL |
| :--- | :--- | :--- | :--- |
| **A** | `workflow` | `187.126.124.74` | 300 / 1/2 hour |
| **A** | `admin` | `187.126.124.74` | 300 / 1/2 hour |

*Example results: `workflow.gocompliances.com` and `admin.gocompliances.com` both resolve to `187.126.124.74`.*

---

## Step 2: Connect to your Hostinger VPS & Clone Code

You already have an SSH session active to your VPS:
```bash
ssh root@187.126.124.74
```

On your VPS, clone your repository (or transfer files via `git` / `rsync`):

```bash
# Recommended destination: /var/www/gocompliance-crm
mkdir -p /var/www
cd /var/www

# Clone your repository:
git clone <YOUR_GIT_REPO_URL> gocompliance-crm
cd gocompliance-crm
```

*(Alternatively, if you haven't pushed to Git yet, you can rsync from your local machine:)*
```bash
# Run this from your local Mac terminal:
rsync -avz --exclude 'node_modules' --exclude '.venv' --exclude 'dist' \
  /Users/abhishekmahto/Desktop/gocompliance-crm/ root@187.126.124.74:/var/www/gocompliance-crm/
```

---

## Step 3: Run Automated VPS Setup

On your VPS inside `/var/www/gocompliance-crm`, run the setup script:

```bash
chmod +x deploy/setup-vps.sh deploy/init-ssl.sh
./deploy/setup-vps.sh
```

This script automatically:
1. Installs Docker Engine & Docker Compose plugin (if not installed).
2. Configures the firewall (ports 22, 80, 443).
3. Creates `.env` and generates secure random `POSTGRES_PASSWORD` and `JWT_SECRET_KEY`.

---

## Step 4: Configure Your Domain Names

Edit your `.env` file on the VPS:

```bash
nano .env
```

Set your actual domain names and your email address:
```env
MAIN_DOMAIN=workflow.gocompliances.com
ADMIN_DOMAIN=admin.gocompliances.com
CERTBOT_EMAIL=your-email@gocompliances.com
```

Save and exit (`Ctrl+O`, `Enter`, `Ctrl+X`).

---

## Step 5: Launch the Application & Obtain SSL

Run the SSL initialization script:

```bash
./deploy/init-ssl.sh
```

This script:
1. Generates temporary SSL certificates so Nginx can start immediately.
2. Builds and starts all Docker containers (`db`, `backend`, `frontend`, `admin-frontend`, `nginx`, `certbot`).
3. Runs Alembic database migrations automatically (`alembic upgrade head`).
4. Contacts Let's Encrypt to issue genuine SSL certificates.
5. Reloads Nginx with HTTPS enabled.

---

## Step 6: Seed Database & Create Super Admin Account

Once the containers are running, seed the initial database masters:

```bash
# 1. Seed base system modules, departments, designations, companies, and services:
docker compose exec backend sh seed.sh

# 2. Create the first Super Admin account:
docker compose exec backend python -m app.scripts.bootstrap_super_admin create \
  --email "admin@gocompliances.com" \
  --first-name "Admin" \
  --last-name "User" \
  --phone "9876543210" \
  --company-code "GOCOMPLIANCES" \
  --department-code "ADMINISTRATION" \
  --designation-code "DIRECTOR"
```
*(You will be securely prompted in the terminal to set a strong password.)*

---

## Step 7: Access Your Deployed Applications

Your CRM is now fully deployed and secure:

- **Main CRM Portal:** `https://workflow.gocompliances.com`
- **Admin Portal:** `https://admin.gocompliances.com`
- **Interactive Swagger Docs:** `https://workflow.gocompliances.com/docs`

---

## Useful Day-to-Day Maintenance Commands

### Check Service Status
```bash
docker compose ps
```

### View Live Logs
```bash
# View backend logs
docker compose logs -f backend

# View Nginx web access & error logs
docker compose logs -f nginx
```

### Restart All Services
```bash
docker compose restart
```

### Deploying Future Code Updates
When you push code updates:
```bash
cd /var/www/gocompliance-crm
git pull
docker compose build
docker compose up -d
```
*(Migrations run automatically on container startup).*

### Backup Database
```bash
docker compose exec -T db pg_dump -U gocompliance is_gocompliance_db > backup_$(date +%F).sql
```
