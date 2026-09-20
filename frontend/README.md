# GOCOMPLIANCE CRM — Main Frontend Application

The primary web client for the **GOCOMPLIANCE CRM** platform, built with **React**, **TypeScript**, **Vite**, and **Tailwind CSS**.

## Architecture & Ports

```text
Main CRM Frontend: http://localhost:5173  (Active Canonical Client)
FastAPI Backend:   http://localhost:8000  (Core REST & JWT API)
System Admin:      http://localhost:8001  (Standalone bootstrap reference - Stage 10A)
PostgreSQL:        localhost:5432         (Database: is_gocompliance_db)
```

> **Note on `admin-frontend/`**: The separate `admin-frontend/` codebase is temporarily retained as a bootstrap/verification reference. The canonical Employee Management and Administration experience is hosted inside this `frontend/` application under `/admin`.

---

## Key Features & Modules

### 1. Real JWT Authentication & Session Lifecycle
- Secure login against FastAPI `/api/auth/login` (supports official email or auto-generated employee code).
- Rotating access tokens and refresh tokens in `localStorage`.
- Current user profile (`/api/auth/me`) and permission scopes (`/api/auth/me/modules`) loaded upon login.
- Preserved signature login page design with interactive floating inputs, show/hide password toggle, and successful login paper airplane animation transition.

### 2. Main Dashboard & Module Cards
- Visual dashboard with module cards for **Admin**, **Sales**, and **Operations**.
- **Admin card visibility & access gate**: Connected to `/admin` and visible/accessible only when the user possesses `can_view` permission on the `ADMIN` module.

### 3. Integrated Administration Module (`/admin`)
- **Admin Hub Landing Page** (`/admin`):
  - **Employee Management** (`/admin/employees`): Active canonical directory for CRM workforce.
  - **User Module Access** (`/admin/access`): Placeholder route (Scheduled for Stage 10B).
  - **Account Activation** (`/admin/account-activation`): Placeholder route (Scheduled for Stage 10C).

### 4. Canonical Employee Management (`/admin/employees`)
- **Employee Directory** (`/admin/employees`):
  - Server-side search across Employee Code, First Name, Last Name, and Official Email.
  - Dependent filters for Company, Department, Designation, Manager, and Operational Status (`ACTIVE`, `PENDING`, `INACTIVE`, `SUSPENDED`).
  - Pagination controls (page size and page index).
- **Add Employee** (`/admin/employees/new`):
  - Strict profile creation (auto-generated employee codes `CGxxxx`, `EPxxxx`, `BMxxxx`).
  - Dynamic company-dependent department and designation dropdowns.
  - Explicit security notice: passwords are NOT accepted during creation (login access is granted via Stage 10C activation).
  - Permission-gated (`ADMIN_EMPLOYEES` -> `create`).
- **Employee Detail Profile** (`/admin/employees/:userId`):
  - Full breakdown of Organizational Structure, Contact & Communication, Employment Terms, and System Metadata.
  - Out-of-scope access guard (respects `SELF`, `TEAM`, `DEPARTMENT`, `COMPANY`, `ALL` data scopes).
  - Operational status management modal (requires `approve` permission).
- **Edit Employee Profile** (`/admin/employees/:userId/edit`):
  - Safe partial updates to name, personal email, mobile number, department, designation, manager, and employment type.
  - Immutability guarantees (Company and Employee Code cannot be altered).
  - Permission-gated (`ADMIN_EMPLOYEES` -> `edit`).

---

## Development & Verification

### Running the Dev Server
```bash
npm run dev
```
Accessible at `http://localhost:5173`.

### Running Automated Vitest Suite
```bash
npm test -- --run
```
Covers:
- `src/__tests__/auth_flow.test.tsx` (Login, session state, permission resolution, logout)
- `src/__tests__/admin_routes.test.tsx` (Dashboard card gating, route protection, placeholders)
- `src/__tests__/employee_management.test.tsx` (Directory rendering, add employee form, profile detail view)

### Production Build Validation
```bash
npm run build
```
Validates full TypeScript type-checking and produces optimized production assets with Vite.

