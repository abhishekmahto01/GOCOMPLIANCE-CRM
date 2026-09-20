# Gocompliances CRM - Backend

Production-ready FastAPI backend foundation for Gocompliances CRM.

## Current Stage Scope: Stage 7B (Secure Authentication Foundation)

Stage 7B establishes the enterprise authentication and session architecture:
- **Argon2id Password Hashing:** Modern, secure password hashing using `pwdlib[argon2]` with constant-time verification to prevent timing side-channel attacks.
- **Signed JWT Access Tokens:** Issued with 15-minute expiration, containing `sub` (User UUID), `token_version`, and unique `jti`.
- **Rotating Refresh Tokens:** 7-day expiration, stored only as cryptographic SHA-256 hashes in `auth_refresh_token`. Old tokens are revoked upon rotation, and token replay/reuse automatically terminates all active sessions.
- **Account Lockout Protection:** 5 consecutive failed attempts trigger a 15-minute temporary lockout.
- **Dual Identifier Login:** Accepts either corporate `official_email` or `employee_code` (case-insensitive) with generic 401 responses to prevent account enumeration.
- **Authentication Endpoints:** `/api/auth/login`, `/api/auth/refresh`, `/api/auth/logout`, `/api/auth/me`, and `/api/auth/change-password`.
- **Global Session Invalidation:** Changing password or detecting token reuse increments `token_version` and revokes all active database sessions.
- **Bootstrap Admin Script (`app/scripts/bootstrap_admin.py`):** Interactive CLI utility using `getpass.getpass()` for initial Director account creation (never executed automatically).
- **Automated Unit Test Suite:** 89 passing unit tests covering all cryptographic, validation, lockout, rotation, and API operations.

> **Note on Stage 7B Boundaries:**
> - **Zero Default / Seed Admin Records:** `user_master` remains completely empty (0 records) until authorized users create real accounts via the bootstrap script or future UI.
> - **No Roles / Permissions Yet:** RBAC, permissions, and access control matrices will be established in Stage 7C.
> - **No Employee CRUD Endpoints / Frontend Yet:** Admin UI and employee management routes will be added in Stage 7D.

---

## Authentication Flow & Security Architecture

### 1. Dual Identifier Login
Users may log in with either:
- **Official Corporate Email:** (e.g. `director@gocompliances.in`) - automatically lowercased.
- **Employee Code:** (e.g. `CG0001`, `EP0001`, `BM0001`) - automatically uppercased.

```http
POST /api/auth/login
Content-Type: application/json

{
  "identifier": "director@gocompliances.in",
  "password": "ValidComplexPassword123!@"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOi...",
  "refresh_token": "eyJhbGciOi...",
  "token_type": "bearer",
  "expires_in": 900,
  "must_change_password": true
}
```

### 2. Token Lifetimes & Rotation Policy
- **Access Token:** 15 minutes default lifetime (`ACCESS_TOKEN_EXPIRE_MINUTES=15`).
- **Refresh Token:** 7 days default lifetime (`REFRESH_TOKEN_EXPIRE_DAYS=7`).
- **Token Rotation:** Every call to `POST /api/auth/refresh` revokes the old refresh token and issues a brand-new token pair.
- **Replay Attack Detection:** If a previously revoked refresh token is presented again, the system detects a token reuse attack, increments the user's `token_version`, and immediately invalidates all active sessions.

### 3. Password Complexity Policy
All user passwords must satisfy:
- Minimum 10 characters, maximum 128 characters
- At least one uppercase letter (`A-Z`)
- At least one lowercase letter (`a-z`)
- At least one digit (`0-9`)
- At least one special symbol (`!@#$%^&*()_+-=[]{};':"|,.<>/?~`)
- No leading or trailing whitespace

### 4. Account Lockout Rules
- 5 consecutive failed login attempts lock the account for 15 minutes.
- Successful login clears failed attempt counters and removes any lockout.

---

## Required Environment Variables

Configure these variables in your local `backend/.env`:

```bash
# Security & JWT Configuration
JWT_SECRET_KEY="YOUR_CRYPTO_SECURE_SECRET_MINIMUM_32_CHARACTERS"
JWT_ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
MAX_FAILED_LOGIN_ATTEMPTS=5
LOGIN_LOCK_MINUTES=15
```

### Generating a Secure JWT Secret
```bash
# Using OpenSSL:
openssl rand -base64 48

# Using Python secrets:
python3 -c "import secrets; print(secrets.token_urlsafe(48))"
```

---

## Database Migration & Verification Commands

All commands are run from the `backend/` directory with `.venv` activated:

```bash
cd backend
source .venv/bin/activate
```

### 1. Apply Database Migration
```bash
alembic upgrade head
```

### 2. Verify Database Tables & Row Counts
```bash
psql -d is_gocompliance_db -c "
SELECT count(*) AS companies FROM company_master;
SELECT count(*) AS departments FROM department_master;
SELECT count(*) AS designations FROM designation_master;
SELECT count(*) AS users FROM user_master;
SELECT count(*) AS refresh_tokens FROM auth_refresh_token;
"
```
**Expected Counts:**
- `company_master` = 3
- `department_master` = 12
- `designation_master` = 18
- `user_master` = 0
- `auth_refresh_token` = 0

---

## First Director Account Bootstrap (Manual Execution)

When approved real Director details are ready, run the interactive utility:

```bash
python3 -m app.scripts.bootstrap_admin
```

This utility will prompt interactively for Company Code, Department Code, Designation Code, Name, Official Email, Mobile, Joining Date, and Password (masked input).

---

## Running Automated Tests

Execute the full test suite using `pytest`:

```bash
pytest -v
```

All 89 unit tests run in isolation using mocking (no destructive database mutations).

---

## Roadmap / Upcoming Stages
- **Stage 7C:** Role-Based Access Control (RBAC), Permissions Framework, and Security Dependencies.
- **Stage 7D:** Employee Management HTTP CRUD APIs, Admin UI, and Profile Management.
