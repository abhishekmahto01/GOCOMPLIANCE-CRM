# GOCOMPLIANCE CRM

Enterprise-grade multi-company Customer Relationship Management (CRM) and Operations platform built for compliance, legal, tax, and corporate services firms (handling GST, Private Limited Company registration, Trademark filings, ISO certifications, Audits, and Accounting).

Designed with centralized administration, strict hierarchical Role-Based Access Control (RBAC), multi-tenant department management, and automated workflow handoffs between **Sales**, **Operations**, and **Accounts & Finance**.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB.svg?logo=python&logoColor=white)](https://python.org)
[![React](https://img.shields.io/badge/React-19.2-61DAFB.svg?logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178C6.svg?logo=typescript&logoColor=white)](https://typescriptlang.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1.svg?logo=postgresql&logoColor=white)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg?logo=docker&logoColor=white)](https://docker.com)
[![Nginx](https://img.shields.io/badge/Nginx-Reverse_Proxy-009639.svg?logo=nginx&logoColor=white)](https://nginx.org)
[![Let's Encrypt](https://img.shields.io/badge/SSL-Let's_Encrypt-003A70.svg?logo=letsencrypt&logoColor=white)](https://letsencrypt.org)

---

## Table of Contents

1. [Live Production Deployment (Hostinger VPS)](#-live-production-deployment-hostinger-vps)
2. [Production Architecture](#-production-architecture)
3. [Deployment & Server Management Guide](#-deployment--server-management-guide)
4. [Local Development Quick Start](#-local-development-quick-start)
5. [Core Architecture & Business Modules](#-core-architecture--business-modules)
6. [Project Directory Layout](#-project-directory-layout)
7. [Environment Variables Reference](#-environment-variables-reference)
8. [Database Management & Seeding](#-database-management--seeding)
9. [Available CLI Scripts](#-available-cli-scripts)
10. [Detailed Documentation Links](#-detailed-documentation-links)

---

## 🌐 Live Production Deployment (Hostinger VPS)

The application is deployed on an Ubuntu VPS running on **Hostinger** utilizing Docker Compose, an Nginx reverse proxy with SSL termination, and automated Let's Encrypt certificate renewal.

| Portal | Production URL | Description |
| :--- | :--- | :--- |
| **Main CRM Application** | [https://workflow.gocompliances.com](https://workflow.gocompliances.com) | Core CRM for Sales, Operations, Accounts & Managers |
| **System Admin Portal** | [https://admin.gocompliances.com](https://admin.gocompliances.com) | Central system administration & user permissions portal |
| **Interactive API Documentation** | [https://workflow.gocompliances.com/docs](https://workflow.gocompliances.com/docs) | OpenAPI / Swagger interactive API docs |
| **Alternative API Specs** | [https://workflow.gocompliances.com/redoc](https://workflow.gocompliances.com/redoc) | ReDoc formatted API documentation |

---

## 🏗️ Production Architecture

```
                                  Internet (HTTP :80 / HTTPS :443)
                                                 │
                                                 ▼
                             ┌───────────────────────────────────────┐
                             │       Nginx SSL Gateway Container     │
                             │   (Let's Encrypt Auto-Renewal / 443)   │
                             └───────────────────┬───────────────────┘
                                                 │
                   ┌─────────────────────────────┼─────────────────────────────┐
                   │                             │                             │
                   ▼                             ▼                             ▼
       ┌────────────────────────┐    ┌────────────────────────┐    ┌────────────────────────┐
       │   FastAPI Backend      │    │    CRM Frontend        │    │    Admin Frontend      │
       │   (Port 8000 internally│    │    (Nginx static SPA   │    │    (Nginx static SPA   │
       │    Routes: /api/*,     │    │     Port 80 internally │    │     Port 80 internally │
       │    /docs, /redoc)      │    │     workflow.gocomp...)│    │     admin.gocomp...)   │
       └───────────┬────────────┘    └────────────────────────┘    └────────────────────────┘
                   │
                   ▼
       ┌────────────────────────┐
       │   PostgreSQL 16 DB     │
       │   (Persistent Volume:  │
       │    pgdata)             │
       └────────────────────────┘
```

---

## 🚀 Deployment & Server Management Guide

### One-Command Deployment from Local Machine
If you have SSH access to your Hostinger VPS, you can sync local code, rebuild images, and restart services with a single command from your Mac/development machine:

```bash
# Deploys local updates directly to Hostinger VPS (187.126.124.74)
npm run deploy

# Stream live production container logs
npm run deploy:logs
```

---

### Initial Hostinger VPS Setup (Step-by-Step)

If setting up a fresh VPS or configuring a new server from scratch:

#### Step 1: DNS Configuration (Hostinger DNS Manager)
Create or update two **A Records** in your DNS provider pointing to your Hostinger VPS IP:

| Type | Host / Name | Points To (IP) | TTL |
| :--- | :--- | :--- | :--- |
| **A** | `workflow` | `187.126.124.74` | 300 (or Automatic) |
| **A** | `admin` | `187.126.124.74` | 300 (or Automatic) |

*Wait 5–15 minutes for DNS propagation.*

#### Step 2: Connect to VPS & Clone Repository
```bash
ssh root@187.126.124.74

# Navigate to application destination directory
mkdir -p /var/www
cd /var/www

# Clone repository
git clone <YOUR_GIT_REPO_URL> gocompliance-crm
cd gocompliance-crm
```

*(Alternatively, transfer files from your local Mac using rsync:)*
```bash
rsync -avz --exclude 'node_modules' --exclude '.venv' --exclude 'dist' \
  /Users/abhishekmahto/Desktop/gocompliance-crm/ root@187.126.124.74:/var/www/gocompliance-crm/
```

#### Step 3: Run the Automated VPS Provisioning Script
```bash
chmod +x deploy/setup-vps.sh deploy/init-ssl.sh
./deploy/setup-vps.sh
```
This automated script:
1. Installs Docker Engine, Docker Compose plugin, Git, UFW, OpenSSL, and utilities.
2. Configures the firewall (allowing SSH port 22, HTTP 80, and HTTPS 443).
3. Generates `.env` from template with cryptographically secure random `POSTGRES_PASSWORD` and `JWT_SECRET_KEY`.

#### Step 4: Verify Domain Configuration in `.env`
Edit `.env` on your VPS:
```bash
nano .env
```
Ensure domain and email settings match your configuration:
```env
MAIN_DOMAIN=workflow.gocompliances.com
ADMIN_DOMAIN=admin.gocompliances.com
CERTBOT_EMAIL=your-email@gocompliances.com
```

#### Step 5: Initialize SSL & Launch Containers
```bash
./deploy/init-ssl.sh
```
This script:
1. Configures initial temporary dummy certificates to bootstrap Nginx.
2. Starts Docker containers (`db`, `backend`, `frontend`, `admin-frontend`, `nginx`, `certbot`).
3. Executes database schema migrations (`alembic upgrade head`).
4. Solves Let's Encrypt ACME webroot challenge and installs genuine SSL certificates.
5. Reloads Nginx with HTTPS enabled.

#### Step 6: Seed Database & Create Super Admin Account
Once the containers are running:
```bash
# 1. Seed base master data (Modules, Departments, Designations, Companies, Services)
docker compose exec backend sh seed.sh

# 2. Bootstrap the first Super Admin user account
docker compose exec backend python -m app.scripts.bootstrap_super_admin create \
  --email "admin@gocompliances.com" \
  --first-name "Admin" \
  --last-name "User" \
  --phone "9876543210" \
  --company-code "GOCOMPLIANCES" \
  --department-code "ADMINISTRATION" \
  --designation-code "DIRECTOR"
```
*(Enter your secure password when prompted).*

---

### Day-to-Day VPS Maintenance Commands

| Action | Command |
| :--- | :--- |
| **Check container status** | `docker compose ps` |
| **Stream backend logs** | `docker compose logs -f backend` |
| **Stream Nginx logs** | `docker compose logs -f nginx` |
| **Restart all services** | `docker compose restart` |
| **Apply pending DB migrations** | `docker compose exec backend alembic upgrade head` |
| **Create database backup** | `docker compose exec -T db pg_dump -U gocompliance is_gocompliance_db > backup_$(date +%F).sql` |
| **Restore database backup** | `cat backup.sql \| docker compose exec -T db psql -U gocompliance -d is_gocompliance_db` |
| **Test SSL certificate renewal** | `docker compose run --rm certbot renew --dry-run` |

---

## 💻 Local Development Quick Start

### Single-Command Unified Launcher
Launch all 3 development services (FastAPI, CRM Frontend, and Admin Frontend) concurrently with pre-flight prerequisite checks:

```bash
npm run dev
```

### Local Services & Ports

| Service | Local URL | Description | Default Port |
| :--- | :--- | :--- | :--- |
| **Main CRM UI** | `http://localhost:5173` | React 19 Frontend (Sales, Ops, Accounts) | `5173` |
| **FastAPI Backend** | `http://localhost:8000` | REST API service | `8000` |
| **Interactive API Docs** | `http://localhost:8000/docs` | Swagger UI documentation | `8000` |
| **Admin UI Portal** | `http://localhost:8001` | Dedicated System Administration portal | `8001` |

### Validate Prerequisites Without Starting Services
```bash
npm run dev:check
```

### Stopping Local Services
* Press **`Ctrl+C`** in the terminal running `npm run dev`. All child processes are gracefully terminated and ports are freed automatically.

---

### Local Development Prerequisites
1. **Node.js**: v18+ & npm
2. **Python**: v3.10+ (v3.11+ recommended)
3. **PostgreSQL**: v14+ running locally on port `5432`
4. **Bash & lsof**: macOS/Linux standard

---

### Initial Local Repository Setup

#### 1. Backend Setup
```bash
cd backend

# Create & activate Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your local PostgreSQL credentials:
# DATABASE_URL=postgresql+psycopg://username:password@localhost:5432/is_gocompliance_db
# JWT_SECRET_KEY=your_secure_random_key_at_least_32_chars

# Run migrations and seed data
alembic upgrade head
sh seed.sh
```

#### 2. Main Frontend Setup
```bash
cd frontend
npm install
```

#### 3. Admin Frontend Setup
```bash
cd admin-frontend
npm install
```

---

### Individual Service Manual Startup

If you prefer running services in separate terminal tabs:

```bash
# Terminal 1: FastAPI Backend
cd backend
.venv/bin/python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Terminal 2: Main CRM UI
cd frontend
npm run dev

# Terminal 3: Admin UI
cd admin-frontend
npm run dev
```

---

## 🧩 Core Architecture & Business Modules

GoCompliance CRM solves end-to-end departmental handoffs for legal and corporate compliance firms:

```
┌──────────────┐     Confirmed      ┌──────────────────┐    Billing & P&L    ┌──────────────────┐
│    SALES     │ ─────────────────► │    OPERATIONS    │ ──────────────────► │ ACCOUNTS/FINANCE │
│ Lead ➔ Order │      Order         │ Docs ➔ Filings   │     Receipts/GST    │ Invoices ➔ Due   │
└──────────────┘                    └──────────────────┘                     └──────────────────┘
```

### 1. Multi-Company Group Architecture
* Supports multiple corporate entities under a single parent umbrella (e.g., *GoCompliances*, *Enterpernership*, *BrandMingo*).
* Distinct company prefixes, invoice numbering formats, letterheads, and branding.

### 2. Hierarchical Role-Based Access Control (RBAC) & Scopes
Granular action permissions (`view`, `create`, `edit`, `delete`) combined with **5 Data Visibility Scopes**:
* **Global**: Unrestricted access across all companies and departments (Director / Super Admin).
* **Company**: Visibility bounded to the user's assigned group company.
* **Department**: Visibility bounded to the user's department within a company.
* **Team**: Managers see their own and their subordinates' records.
* **Own**: Individual employees only access records assigned to them or created by them.

### 3. Sales Module
* **Lead Ingestion & Qualification**: Contact details, service interests, budget, and follow-ups.
* **Quotations & Sales Orders**: Advance payment tracking, billing details, and automatic conversion to operations orders.

### 4. Operations & Compliance Tracking
* **Task Lifecycle**: Unassigned Pool ➔ Assignment to Executive ➔ Document Verification ➔ Government Portal Filing ➔ Query Resolution ➔ Completion.
* **Document Checklists**: Mandatory vs. optional statutory document verification (PAN, Aadhaar, MOA, etc.).
* **Remarks & Audit Trail**: Real-time remarks with internal conversations and timestamps on every state transition.

### 5. Accounts & Finance Module
* **Billing Register**: Auto-generated sales orders ready for billing approval.
* **Invoices**: Proforma Invoices and GST Tax Invoices with SAC codes, CGST/SGST/IGST breakdown.
* **Real-time Profitability**: Net margin calculation factoring statutory government fees vs. company fees.

### 6. Central Administration Portal
* Master data management for Companies, Departments, Designations, License types, and Services.
* Employee lifecycle management with role assignments and password management.
* Granular module permissions configuration and operational coordinator mappings.

---

## 📁 Project Directory Layout

```
gocompliance-crm/
├── README.md                      # Primary project documentation (this file)
├── DEPLOYMENT_GUIDE.md            # Detailed VPS deployment manual & troubleshooting
├── PROJECT_EXPLANATION.md         # Full architectural deep-dive & interview guide
├── docker-compose.yml             # Production multi-container Docker compose definition
├── .env.production.example        # Production environment template
├── package.json                   # Root scripts orchestration (npm run dev, deploy, demo)
│
├── deploy/                        # Production deployment configurations
│   ├── setup-vps.sh               # Hostinger VPS automated installation script
│   ├── init-ssl.sh                # Let's Encrypt SSL generation & Nginx restart
│   └── nginx/
│       └── templates/
│           └── default.conf.template  # Nginx reverse proxy SSL configuration
│
├── scripts/                       # Local orchestration and demo scripts
│   ├── dev.sh                     # Local development multi-service launcher
│   ├── deploy.sh                  # One-command VPS deploy script (npm run deploy)
│   └── demo.sh                    # Cloudflare Quick Tunnel public demo script
│
├── backend/                       # Core FastAPI REST Backend
│   ├── Dockerfile                 # Production backend Docker container
│   ├── entrypoint.sh              # Container startup & auto-migration execution
│   ├── requirements.txt           # Python package dependencies
│   ├── alembic/                   # Alembic schema migration files
│   ├── app/
│   │   ├── main.py                # FastAPI entry point & router registrations
│   │   ├── api/                   # REST API route handlers
│   │   ├── core/                  # Security, JWT, RBAC guards, config
│   │   ├── models/                # SQLAlchemy ORM models
│   │   ├── schemas/               # Pydantic schemas (request/response)
│   │   ├── services/              # Business logic layers
│   │   └── scripts/               # Seeding & admin bootstrap scripts
│   └── seed.sh                    # Base system data seed script
│
├── frontend/                      # Main CRM Frontend (Sales, Ops, Accounts)
│   ├── Dockerfile                 # Multi-stage production build container
│   ├── package.json               # React 19, Vite, Tailwind CSS, Lucide dependencies
│   └── src/                       # Components, pages, hooks, contexts
│
└── admin-frontend/                # Dedicated System Admin Portal
    ├── Dockerfile                 # Multi-stage production build container
    ├── package.json               # React 19, Vite, Tailwind CSS dependencies
    └── src/                       # Admin modules, user permissions, master setups
```

---

## ⚙️ Environment Variables Reference

### Production Environment (`.env` in Root)

```env
# Domain Configuration
MAIN_DOMAIN=workflow.gocompliances.com
ADMIN_DOMAIN=admin.gocompliances.com

# SSL Certificate Email
CERTBOT_EMAIL=admin@gocompliances.com

# PostgreSQL Database
POSTGRES_DB=is_gocompliance_db
POSTGRES_USER=gocompliance
POSTGRES_PASSWORD=<strong_random_database_password>

# Security Secrets
JWT_SECRET_KEY=<strong_random_jwt_secret_minimum_32_chars>
```

### Local Development Environment (`backend/.env`)

```env
PROJECT_NAME="GoCompliance CRM API"
ENVIRONMENT="development"

# PostgreSQL Local Connection
DATABASE_URL=postgresql+psycopg://username:password@localhost:5432/is_gocompliance_db

# JWT & Authentication
JWT_SECRET_KEY=your_secure_random_key_at_least_32_chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480

# CORS Origins (Include local dev ports)
CORS_ORIGINS=["http://localhost:5173","http://localhost:8001","http://127.0.0.1:5173","http://127.0.0.1:8001"]
FRONTEND_ORIGIN="http://localhost:5173"
ADMIN_FRONTEND_ORIGIN="http://localhost:8001"
```

---

## 🗄️ Database Management & Seeding

### Migrations with Alembic

```bash
# Run latest migrations
alembic upgrade head

# Create a new auto-generated migration after model changes
alembic revision --autogenerate -m "describe_changes_here"

# Roll back one migration
alembic downgrade -1
```

### Seeding Master Data

Seed base modules, departments, designations, companies, and service catalogs:

```bash
# In local development:
cd backend
sh seed.sh

# In production Docker:
docker compose exec backend sh seed.sh
```

### Creating Initial Super Admin

```bash
# In local development:
python -m app.scripts.bootstrap_super_admin create \
  --email "admin@gocompliances.com" \
  --first-name "Admin" \
  --last-name "User" \
  --phone "9876543210" \
  --company-code "GOCOMPLIANCES" \
  --department-code "ADMINISTRATION" \
  --designation-code "DIRECTOR"

# In production Docker:
docker compose exec backend python -m app.scripts.bootstrap_super_admin create \
  --email "admin@gocompliances.com" \
  --first-name "Admin" \
  --last-name "User" \
  --phone "9876543210" \
  --company-code "GOCOMPLIANCES" \
  --department-code "ADMINISTRATION" \
  --designation-code "DIRECTOR"
```

---

## ⚡ Available CLI Scripts

Run these from the workspace root directory:

| Script | Command | Purpose |
| :--- | :--- | :--- |
| **Local Dev** | `npm run dev` | Runs pre-flight checks and launches Backend (:8000), Frontend (:5173), and Admin (:8001) concurrently |
| **Dev Pre-check** | `npm run dev:check` | Validates dependencies, database, virtual environment, and ports without starting services |
| **Deploy to VPS** | `npm run deploy` | Syncs code via rsync, rebuilds Docker containers, and executes zero-downtime rolling update on VPS |
| **VPS Live Logs** | `npm run deploy:logs` | Streams live Docker container logs from the Hostinger VPS |
| **Public Demo** | `npm run demo` | Launches local stack and creates secure public Cloudflare Quick Tunnels for remote presentations |
| **Demo Pre-check** | `npm run demo:check` | Validates prerequisites and Cloudflare `cloudflared` binary availability |

---

## 📚 Detailed Documentation Links

* **[Hostinger VPS Deployment Guide](file:///Users/abhishekmahto/Desktop/gocompliance-crm/DEPLOYMENT_GUIDE.md)**: Deep dive into firewall setup, Let's Encrypt rate limits, zero-downtime updates, and production troubleshooting.
* **[Comprehensive Architecture & Project Explanation](file:///Users/abhishekmahto/Desktop/gocompliance-crm/PROJECT_EXPLANATION.md)**: Detailed technical manual covering FastAPI architecture, SQLAlchemy ORM relationships, RBAC security design, and presentation guides.
* **[Backend Readme](file:///Users/abhishekmahto/Desktop/gocompliance-crm/backend/README.md)**: FastAPI backend technical documentation and API specifications.
