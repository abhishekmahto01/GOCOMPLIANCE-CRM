# Gocompliances CRM - Backend

Production-ready FastAPI backend foundation for Gocompliances CRM.

## Current Stage Scope: Stage 7A (User Master Database Foundation & Employee-Code Generation)

Stage 7A establishes the fundamental user and employee registry (`user_master`) along with concurrency-safe employee-code generation and cross-company integrity validation:
- **SQLAlchemy 2 Typed Model `User`** mapped to `user_master` with foreign keys to `company_master`, `department_master`, `designation_master`, and a nullable self-referencing reporting manager foreign key (`user_master.user_id`).
- **Pydantic v2 Schemas** (`UserBase`, `UserCreate`, `UserUpdate`, `UserRead`) with strict validation for names, normalized lowercased emails, Indian `+91` mobile formats, employment types, and account statuses.
- **Alembic Schema Migration** `574d1e27cc56_create_user_master.py` with foreign key constraints, check constraints, indexes, and functional unique lower-cased index on `official_email`.
- **Employee-Code Generation Service** (`app/services/employee_code.py`) using PostgreSQL row-level locking (`SELECT ... FOR UPDATE`) on `company_master` to assign strictly sequential, atomic employee codes (e.g. `CG0001`, `EP0001`, `BM0001`).
- **User Creation Service & Integrity Validation** (`app/services/user_service.py`) enforcing cross-company consistency (Department, Designation, and Reporting Manager must all belong to the employee's assigned Company).
- **Automated Unit Test Suite** with 67 tests covering models, constraints, relationships, schema normalization, employee code generation, concurrency locking, cross-company validation, and rollback safety.

> **Note on Stage 7A Boundaries:**
> - **Zero Seed Employee Records:** `user_master` remains completely empty (0 records) until authorized users create real accounts via the future Admin UI.
> - **No Passwords / JWT / Authentication Yet:** Authentication, password hashing, and JWT tokens will be introduced in subsequent sub-stages (7B/7C).
> - **No Public CRUD Endpoints Yet:** HTTP API routes and UI components will be built in sub-stages after authentication and authorization frameworks are complete.

---

## Employee Profile Scope & Boundaries

### Included Fields (Basic CRM Employee Data)
- **Auto-generated Employee Code:** Company prefix + 4-digit zero-padded number (e.g., `CG0001`, `EP0001`, `BM0001`, scaling beyond 9999 as `CG10000`).
- **Employee Name:** `first_name`, `middle_name` (optional), `last_name`.
- **Official Email:** Corporate email address (case-insensitively unique via PostgreSQL functional index `lower(official_email)`).
- **Personal Email:** Optional personal email address (lowercased).
- **Mobile Number:** Primary contact number supporting Indian `+91` format.
- **Organizational Alignment:** `company_id`, `department_id`, `designation_id`.
- **Reporting Manager:** `manager_user_id` (nullable self-referencing foreign key).
- **Joining Date:** `date_of_joining` (`DATE`).
- **Employment Type:** `FULL_TIME`, `PART_TIME`, `CONTRACT`, `INTERN`, `CONSULTANT`.
- **Account Status:** `PENDING` (default), `ACTIVE`, `INACTIVE`, `SUSPENDED`.

### Excluded HRMS Fields (Out of Scope for CRM)
The following sensitive HR fields are intentionally excluded from `user_master` and belong strictly to future HRMS services:
- Aadhaar number
- PAN number
- Salary / compensation structures
- Bank account details
- Attendance logs
- Detailed residential addresses
- Medical / health information

---

## Organizational Hierarchy & Relationships

In Gocompliances CRM, employees are strictly organized across corporate entities:

```text
Company (e.g. Gocompliances / CG)
├── Department (e.g. Sales)
└── Designation (e.g. Executive, Manager, Director)
      └── User / Employee (e.g. CG0001 - Amit Sharma)
            └── Reports to Manager (e.g. CG0002 - Priya Patel)
```

### Business Rules Enforced by the Service Layer:
1. **Department Belongs to Company:** An employee's Department must belong to the selected Company and be in `ACTIVE` status.
2. **Designation Belongs to Company:** An employee's Designation must belong to the selected Company and be in `ACTIVE` status.
3. **Manager Belongs to Same Company:** A reporting manager must belong to the same Company as the employee.
4. **Self-Manager Prohibition:** An employee cannot report to themselves (enforced both at the database level via `chk_user_self_manager` check constraint and at the service validation layer).

---

## Employee-Code Generation & Concurrency Locking

To ensure collision-free, sequential employee IDs in high-concurrency environments:
1. A transaction acquires an exclusive row lock on the parent company using `SELECT ... FOR UPDATE` on `company_master`.
2. The current `next_employee_number` is read and formatted with the company's `employee_code_prefix` and 4-digit zero padding:
   - `CG` + `1` $\rightarrow$ `CG0001`
   - `EP` + `1` $\rightarrow$ `EP0001`
   - `BM` + `1` $\rightarrow$ `BM0001`
   - Counters exceeding 9999 expand dynamically (e.g. `CG10000`).
3. The counter `company.next_employee_number` is incremented by 1.
4. The user record is inserted and committed in the **same transaction**.
5. If any validation or database error occurs during creation, the transaction is completely rolled back, ensuring sequence numbers are never wasted or skipped.

---

## `user_master` Column Specifications

| Column | Type | Constraints / Defaults | Description |
| :--- | :--- | :--- | :--- |
| `user_id` | `UUID` | Primary Key, `NOT NULL` | Unique user identifier (UUIDv4) |
| `employee_code` | `VARCHAR(20)` | `NOT NULL`, Unique Index | Uppercase unique code (e.g. `CG0001`) |
| `company_id` | `UUID` | Foreign Key (`company_master.company_id`), `ON DELETE RESTRICT`, `NOT NULL`, Index | Company reference |
| `department_id` | `UUID` | Foreign Key (`department_master.department_id`), `ON DELETE RESTRICT`, `NOT NULL`, Index | Department reference |
| `designation_id` | `UUID` | Foreign Key (`designation_master.designation_id`), `ON DELETE RESTRICT`, `NOT NULL`, Index | Designation reference |
| `manager_user_id` | `UUID` | Foreign Key (`user_master.user_id`), `ON DELETE SET NULL`, `NULLABLE`, Index | Reporting manager reference |
| `first_name` | `VARCHAR(100)` | `NOT NULL` | Employee first name |
| `middle_name` | `VARCHAR(100)` | `NULLABLE` | Employee middle name (optional) |
| `last_name` | `VARCHAR(100)` | `NOT NULL` | Employee last name |
| `official_email` | `VARCHAR(255)` | `NOT NULL`, Unique Index on `lower(official_email)` | Corporate email address |
| `personal_email` | `VARCHAR(255)` | `NULLABLE` | Personal contact email |
| `mobile_number` | `VARCHAR(20)` | `NOT NULL` | Contact number (+91 format) |
| `date_of_joining` | `DATE` | `NOT NULL` | Official joining date |
| `employment_type` | `VARCHAR(20)` | `NOT NULL`, Check Constraint | `FULL_TIME`, `PART_TIME`, `CONTRACT`, `INTERN`, `CONSULTANT` |
| `account_status` | `VARCHAR(20)` | `NOT NULL`, Default: `'PENDING'`, Index, Check Constraint | `PENDING`, `ACTIVE`, `INACTIVE`, `SUSPENDED` |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL`, Default: `now()` | Record creation timestamp (UTC) |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL`, Default: `now()` | Record update timestamp (UTC) |

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
"
```
**Expected Counts:**
- `company_master` = 3
- `department_master` = 12
- `designation_master` = 18
- `user_master` = 0 (empty table)

---

## Running Automated Tests

Execute the full test suite using `pytest`:

```bash
pytest -v
```

All 67 unit tests run in isolation using mocking (no destructive database mutations).

---

## Roadmap / Upcoming Stages
- **Stage 7B:** User Authentication, Password Hashing (Argon2id/Bcrypt), and JWT Token Architecture.
- **Stage 7C:** Role-Based Access Control (RBAC), Permissions Framework, and Security Dependencies.
- **Stage 7D:** Employee Management HTTP CRUD APIs, Admin UI, and Profile Management.
