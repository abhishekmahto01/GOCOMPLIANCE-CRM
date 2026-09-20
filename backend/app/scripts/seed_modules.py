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
