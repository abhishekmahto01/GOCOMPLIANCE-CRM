"""Seed initial Module Master records for Gocompliances CRM navigation and permissions."""
import uuid
from typing import Dict, List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.session import SessionLocal
from app.models.module import Module

MODULE_NAMESPACE = uuid.uuid5(uuid.NAMESPACE_DNS, "gocompliance.crm.modules")


def get_deterministic_module_uuid(module_code: str) -> uuid.UUID:
    """Generate a deterministic UUIDv5 for a module code to ensure idempotent seeding."""
    return uuid.uuid5(MODULE_NAMESPACE, module_code.upper())


# Initial 8 system modules definition
INITIAL_MODULES: List[Dict[str, Optional[object]]] = [
    # Top-Level Root Modules
    {
        "module_code": "ADMIN",
        "module_name": "Admin",
        "parent_code": None,
        "route": "/admin",
        "description": "Administrative settings, company management, and access controls",
        "display_order": 10,
        "is_navigation": True,
        "status": "ACTIVE",
    },
    {
        "module_code": "SALES",
        "module_name": "Sales",
        "parent_code": None,
        "route": "/sales",
        "description": "Sales pipeline, lead management, and customer conversions",
        "display_order": 20,
        "is_navigation": True,
        "status": "ACTIVE",
    },
    {
        "module_code": "OPERATIONS",
        "module_name": "Operations",
        "parent_code": None,
        "route": "/operations",
        "description": "Client compliance workflows, task execution, and delivery",
        "display_order": 30,
        "is_navigation": True,
        "status": "ACTIVE",
    },
    # Sub-Modules under ADMIN
    {
        "module_code": "ADMIN_COMPANIES",
        "module_name": "Companies",
        "parent_code": "ADMIN",
        "route": "/admin/companies",
        "description": "Corporate entities and company code prefixes",
        "display_order": 10,
        "is_navigation": True,
        "status": "ACTIVE",
    },
    {
        "module_code": "ADMIN_DEPARTMENTS",
        "module_name": "Departments",
        "parent_code": "ADMIN",
        "route": "/admin/departments",
        "description": "Company-specific department configuration",
        "display_order": 20,
        "is_navigation": True,
        "status": "ACTIVE",
    },
    {
        "module_code": "ADMIN_DESIGNATIONS",
        "module_name": "Designations",
        "parent_code": "ADMIN",
        "route": "/admin/designations",
        "description": "Company-specific employee designations and seniority ranks",
        "display_order": 30,
        "is_navigation": True,
        "status": "ACTIVE",
    },
    {
        "module_code": "ADMIN_EMPLOYEES",
        "module_name": "Employees",
        "parent_code": "ADMIN",
        "route": "/admin/employees",
        "description": "Employee master records and organizational hierarchy",
        "display_order": 40,
        "is_navigation": True,
        "status": "ACTIVE",
    },
    {
        "module_code": "ADMIN_ACCESS",
        "module_name": "Access Control",
        "parent_code": "ADMIN",
        "route": "/admin/access",
        "description": "User module permissions and role authorization",
        "display_order": 50,
        "is_navigation": True,
        "status": "ACTIVE",
    },
    # Sub-Modules (Pages) under SALES
    {
        "module_code": "SALES_DASHBOARD",
        "module_name": "Sales Dashboard",
        "parent_code": "SALES",
        "route": "/sales/dashboard",
        "description": "Sales overview and performance metrics",
        "display_order": 10,
        "is_navigation": True,
        "status": "ACTIVE",
    },
    {
        "module_code": "SALES_CONFIRMED_ORDER",
        "module_name": "Create Confirmed Order",
        "parent_code": "SALES",
        "route": "/sales/confirmed-order",
        "description": "Create new confirmed sales orders",
        "display_order": 20,
        "is_navigation": True,
        "status": "ACTIVE",
    },
    {
        "module_code": "SALES_MY_ORDERS",
        "module_name": "My Sales Orders",
        "parent_code": "SALES",
        "route": "/sales/my-orders",
        "description": "View and manage sales orders created by current employee",
        "display_order": 30,
        "is_navigation": True,
        "status": "ACTIVE",
    },
    {
        "module_code": "SALES_ALL_ORDERS",
        "module_name": "All Sales Orders",
        "parent_code": "SALES",
        "route": "/sales/all-orders",
        "description": "View and manage all sales orders within data scope",
        "display_order": 40,
        "is_navigation": True,
        "status": "ACTIVE",
    },
    {
        "module_code": "SALES_CLIENT_MASTER",
        "module_name": "Client Master",
        "parent_code": "SALES",
        "route": "/sales/clients",
        "description": "Manage corporate clients and accounts",
        "display_order": 50,
        "is_navigation": True,
        "status": "ACTIVE",
    },
    {
        "module_code": "SALES_REPORTS",
        "module_name": "Sales Reports",
        "parent_code": "SALES",
        "route": "/sales/reports",
        "description": "Sales performance and conversion reports",
        "display_order": 60,
        "is_navigation": True,
        "status": "ACTIVE",
    },
    # Sub-Modules (Pages) under OPERATIONS
    {
        "module_code": "OPERATION_DASHBOARD",
        "module_name": "Operation Dashboard",
        "parent_code": "OPERATIONS",
        "route": "/operations/dashboard",
        "description": "Operations workflow status and metrics",
        "display_order": 10,
        "is_navigation": True,
        "status": "ACTIVE",
    },
    {
        "module_code": "OPERATION_UNASSIGNED_ORDERS",
        "module_name": "Unassigned Orders",
        "parent_code": "OPERATIONS",
        "route": "/operations/unassigned-orders",
        "description": "View and assign unassigned compliance orders",
        "display_order": 20,
        "is_navigation": True,
        "status": "ACTIVE",
    },
    {
        "module_code": "OPERATION_TASK_ASSIGNMENT",
        "module_name": "Task Assignment",
        "parent_code": "OPERATIONS",
        "route": "/operations/task-assignment",
        "description": "Assign and reassign compliance tasks across team",
        "display_order": 30,
        "is_navigation": True,
        "status": "ACTIVE",
    },
    {
        "module_code": "OPERATION_MY_TASKS",
        "module_name": "My Assigned Tasks",
        "parent_code": "OPERATIONS",
        "route": "/operations/my-tasks",
        "description": "Compliance tasks assigned to current employee",
        "display_order": 40,
        "is_navigation": True,
        "status": "ACTIVE",
    },
    {
        "module_code": "OPERATION_ALL_TASKS",
        "module_name": "All Operation Tasks",
        "parent_code": "OPERATIONS",
        "route": "/operations/all-tasks",
        "description": "All compliance tasks within data scope",
        "display_order": 50,
        "is_navigation": True,
        "status": "ACTIVE",
    },
    {
        "module_code": "OPERATION_DOCUMENTS",
        "module_name": "Required Documents",
        "parent_code": "OPERATIONS",
        "route": "/operations/documents",
        "description": "Manage statutory compliance documents and checklists",
        "display_order": 60,
        "is_navigation": True,
        "status": "ACTIVE",
    },
    {
        "module_code": "OPERATION_APPLICATION_STATUS",
        "module_name": "Application Status",
        "parent_code": "OPERATIONS",
        "route": "/operations/application-status",
        "description": "Track statutory filing and application statuses",
        "display_order": 70,
        "is_navigation": True,
        "status": "ACTIVE",
    },
    {
        "module_code": "OPERATION_REPORTS",
        "module_name": "Operation Reports",
        "parent_code": "OPERATIONS",
        "route": "/operations/reports",
        "description": "Operations turnaround time and completion reports",
        "display_order": 80,
        "is_navigation": True,
        "status": "ACTIVE",
    },
]


def seed_modules(session: Session) -> Tuple[int, int]:
    """Idempotently seed the initial 8 system modules into module_master.

    Args:
        session: Active SQLAlchemy database session.

    Returns:
        Tuple of (inserted_count, skipped_count).
    """
    inserted = 0
    skipped = 0

    # Fetch existing module codes
    existing_codes = set(session.scalars(select(Module.module_code)).all())

    # Pass 1: Insert root modules (parent_code is None)
    for mod_data in INITIAL_MODULES:
        code = str(mod_data["module_code"])
        if mod_data["parent_code"] is None:
            if code in existing_codes:
                skipped += 1
                continue

            module_id = get_deterministic_module_uuid(code)
            new_module = Module(
                module_id=module_id,
                module_code=code,
                module_name=str(mod_data["module_name"]),
                parent_module_id=None,
                route=str(mod_data["route"]) if mod_data["route"] else None,
                description=str(mod_data["description"]) if mod_data["description"] else None,
                display_order=int(mod_data["display_order"] or 0),
                is_navigation=bool(mod_data["is_navigation"]),
                status=str(mod_data["status"]),
            )
            session.add(new_module)
            existing_codes.add(code)
            inserted += 1

    session.flush()

    # Pass 2: Insert sub-modules (parent_code is not None)
    for mod_data in INITIAL_MODULES:
        code = str(mod_data["module_code"])
        parent_code = mod_data["parent_code"]
        if parent_code is not None:
            if code in existing_codes:
                skipped += 1
                continue

            # Resolve parent module ID
            parent_id = session.scalar(
                select(Module.module_id).where(Module.module_code == str(parent_code))
            )
            if not parent_id:
                raise ValueError(
                    f"Parent module '{parent_code}' could not be resolved for child module '{code}'"
                )

            module_id = get_deterministic_module_uuid(code)
            new_module = Module(
                module_id=module_id,
                module_code=code,
                module_name=str(mod_data["module_name"]),
                parent_module_id=parent_id,
                route=str(mod_data["route"]) if mod_data["route"] else None,
                description=str(mod_data["description"]) if mod_data["description"] else None,
                display_order=int(mod_data["display_order"] or 0),
                is_navigation=bool(mod_data["is_navigation"]),
                status=str(mod_data["status"]),
            )
            session.add(new_module)
            existing_codes.add(code)
            inserted += 1

    session.commit()
    return inserted, skipped


def main() -> None:
    """Run seed script directly from CLI."""
    session = SessionLocal()
    try:
        print("Starting Module Master seeding...")
        inserted, skipped = seed_modules(session)
        print(f"Module seeding complete: {inserted} inserted, {skipped} skipped.")
    except Exception as exc:
        session.rollback()
        print(f"Error seeding modules: {exc}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
