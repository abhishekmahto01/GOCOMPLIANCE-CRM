# Gocompliances CRM - Backend

Production-ready FastAPI backend foundation for Gocompliances CRM.

## Current Stage Scope: Stage 7C (Authorized Employee CRUD API)

Stage 7C delivers authorized Employee Management HTTP APIs governed by granular `ADMIN_EMPLOYEES` module permissions and server-enforced data scoping:
- **FastAPI Router `/api/admin/employees`** with full CRUD and operational lifecycle control.
- **Granular Permission Checks:** All endpoints enforced with `require_module_permission("ADMIN_EMPLOYEES", action)`:
  - `POST /api/admin/employees` (`create` action)
  - `GET /api/admin/employees` (`view` action)
  - `GET /api/admin/employees/{user_id}` (`view` action)
  - `PATCH /api/admin/employees/{user_id}` (`edit` action)
  - `PATCH /api/admin/employees/{user_id}/status` (`approve` action)
- **Multi-Tier Data Scopes:** Server-side evaluation of `SELF`, `TEAM` (recursive hierarchy via cycle-safe PostgreSQL CTE), `DEPARTMENT`, `COMPANY`, and `ALL`.
- **Atomic Code Generation:** Automatic company-prefix based employee code assignment on creation (`CG0001`, `EP0001`, `BM0001`). Client-supplied codes are forbidden.
- **Strict Organizational Integrity:** Server validates that department, designation, and reporting manager exist, are `ACTIVE`, and belong to the employee's company.
- **Hierarchy Loop Prevention:** Ensures employees cannot report to themselves or to any subordinate in their reporting subtree.
- **Zero Secret/Password Exposure:** Response schemas strictly exclude `password_hash`, reset tokens, and sensitive authentication internals. Plaintext passwords are never accepted or stored.
- **Automated Unit & Integration Test Suite:** 140 passing tests.

---

## Employee Management Endpoints

All endpoints are mounted under `/api/admin/employees`:

| Method | Route | Required Module & Action | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/admin/employees` | `ADMIN_EMPLOYEES:create` | Create a new employee with an auto-generated employee code. |
| `GET` | `/api/admin/employees` | `ADMIN_EMPLOYEES:view` | List paginated employees within the user's data scope. |
| `GET` | `/api/admin/employees/{user_id}` | `ADMIN_EMPLOYEES:view` | Retrieve detailed employee profile. Returns `404` if not found, `403` if out-of-scope. |
| `PATCH` | `/api/admin/employees/{user_id}` | `ADMIN_EMPLOYEES:edit` | Partially update employee profile with integrity & cycle prevention. |
| `PATCH` | `/api/admin/employees/{user_id}/status` | `ADMIN_EMPLOYEES:approve` | Update employee operational status (`PENDING`, `ACTIVE`, `INACTIVE`, `SUSPENDED`). |

*Note: There is no `DELETE` endpoint. Employee accounts are deactivated or suspended via the status update endpoint.*

---

## Data Scope Visibility Matrix

| Data Scope | Meaning & Record Access Boundary | Resolution Strategy |
| :--- | :--- | :--- |
| `SELF` | Only the authenticated user's own employee record. | `user_id == current_user.user_id` |
| `TEAM` | Current user and all direct/indirect recursive subordinates. | PostgreSQL Recursive CTE on `user_master` (`manager_user_id`) with cycle tracking and depth limit. |
| `DEPARTMENT` | Employees belonging to the same company and department. | `company_id == user.company_id AND department_id == user.department_id` |
| `COMPANY` | Employees belonging to the same company. | `company_id == user.company_id` |
| `ALL` | All employees across all companies and departments. | Global administrative access. |

---

## Available Query Filters for Listing (`GET /api/admin/employees`)

- `page` (integer, default: 1): 1-indexed page number.
- `page_size` (integer, default: 20, max: 100): Items per page.
- `search` (string): Case-insensitive search on employee code, official email, first name, last name, or full name.
- `company_id` (UUID): Filter by company.
- `department_id` (UUID): Filter by department.
- `designation_id` (UUID): Filter by designation.
- `manager_user_id` (UUID): Filter by direct reporting manager.
- `account_status` (string): Filter by `PENDING`, `ACTIVE`, `INACTIVE`, `SUSPENDED`.

---

## Example Request & Response Payloads

### 1. Create Employee (`POST /api/admin/employees`)

**Request:**
```json
{
  "company_id": "07dc4671-4240-4add-bce6-67e3d2bd45c9",
  "department_id": "ff903dd1-eaf1-4da5-8f7b-83f3ca227195",
  "designation_id": "832bb14a-b45b-4833-8db9-d3b3937bb77e",
  "manager_user_id": "18f507b9-f7cf-4513-bfa1-d68a9b1c7dc4",
  "first_name": "Rohan",
  "middle_name": "Kumar",
  "last_name": "Verma",
  "official_email": "rohan.verma@gocompliances.in",
  "personal_email": "rohan.v@example.com",
  "mobile_number": "+919876543210",
  "date_of_joining": "2026-03-01",
  "employment_type": "FULL_TIME",
  "account_status": "ACTIVE"
}
```

**Response (HTTP 201 Created):**
```json
{
  "user_id": "9a7d341b-4f9e-4a6c-94fb-741982b6c12d",
  "employee_code": "CG0002",
  "company_id": "07dc4671-4240-4add-bce6-67e3d2bd45c9",
  "company_name": "Gocompliances",
  "company_code": "GOCOMPLIANCES",
  "department_id": "ff903dd1-eaf1-4da5-8f7b-83f3ca227195",
  "department_name": "Sales",
  "department_code": "SALES",
  "designation_id": "832bb14a-b45b-4833-8db9-d3b3937bb77e",
  "designation_name": "Executive",
  "designation_code": "EXECUTIVE",
  "manager_user_id": "18f507b9-f7cf-4513-bfa1-d68a9b1c7dc4",
  "manager_name": "Amit Sharma",
  "manager_employee_code": "CG0001",
  "first_name": "Rohan",
  "middle_name": "Kumar",
  "last_name": "Verma",
  "official_email": "rohan.verma@gocompliances.in",
  "personal_email": "rohan.v@example.com",
  "mobile_number": "+919876543210",
  "date_of_joining": "2026-03-01",
  "employment_type": "FULL_TIME",
  "account_status": "ACTIVE",
  "created_at": "2026-09-20T20:10:00Z",
  "updated_at": "2026-09-20T20:10:00Z"
}
```

### 2. Paginated List (`GET /api/admin/employees?page=1&page_size=20`)

**Response (HTTP 200 OK):**
```json
{
  "items": [
    {
      "user_id": "9a7d341b-4f9e-4a6c-94fb-741982b6c12d",
      "employee_code": "CG0002",
      "company_name": "Gocompliances",
      "department_name": "Sales",
      "designation_name": "Executive",
      "first_name": "Rohan",
      "last_name": "Verma",
      "official_email": "rohan.verma@gocompliances.in",
      "mobile_number": "+919876543210",
      "date_of_joining": "2026-03-01",
      "employment_type": "FULL_TIME",
      "account_status": "ACTIVE",
      "created_at": "2026-09-20T20:10:00Z",
      "updated_at": "2026-09-20T20:10:00Z"
    }
  ],
  "page": 1,
  "page_size": 20,
  "total": 1,
  "pages": 1
}
```

---

## Running Verification & Tests

Run all unit and integration tests:

```bash
cd backend
source .venv/bin/activate
pytest -v
alembic current
```

---

## Upcoming Stages
- **Stage 7D:** Manager & Employee Management React UI integration.
