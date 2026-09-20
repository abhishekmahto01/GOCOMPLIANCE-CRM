"""Idempotent seed script for initial company-specific department master records."""
import logging
import sys
import uuid
from typing import Dict, List, Tuple

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.session import SessionLocal
from app.models.company import Company
from app.models.department import Department

logger = logging.getLogger("seed_departments")

# Stable namespace for deterministic Department UUID generation
NAMESPACE_DEPARTMENT = uuid.UUID("1b2c3d4e-5f6a-7b8c-9d0e-1f2a3b4c5d6e")

REQUIRED_COMPANY_CODES: List[str] = [
    "GOCOMPLIANCES",
    "ENTERPERNERSHIP",
    "BRANDMINGO",
]

DEFAULT_DEPARTMENTS: List[Dict[str, str]] = [
    {
        "department_code": "ADMINISTRATION",
        "department_name": "Administration",
        "description": "Executive leadership, administration, and corporate compliance operations",
        "status": "ACTIVE",
    },
    {
        "department_code": "SALES",
        "department_name": "Sales",
        "description": "Business development, client acquisition, and sales operations",
        "status": "ACTIVE",
    },
    {
        "department_code": "OPERATIONS",
        "department_name": "Operations",
        "description": "Client fulfillment, compliance services delivery, and casework",
        "status": "ACTIVE",
    },
    {
        "department_code": "RND",
        "department_name": "R&D",
        "description": "Research and development, technology solutions, and regulatory analysis",
        "status": "ACTIVE",
    },
]


def generate_department_uuid(company_code: str, department_code: str) -> uuid.UUID:
    """Generate a deterministic UUIDv5 for a (company_code, department_code) pair."""
    key = f"{company_code.upper()}:{department_code.upper()}"
    return uuid.uuid5(NAMESPACE_DEPARTMENT, key)


def seed_departments(db: Session) -> Tuple[int, int]:
    """Idempotently seed the default 4 departments for all 3 required companies.

    Returns:
        Tuple[int, int]: (inserted_count, skipped_count)

    Raises:
        ValueError: If any of the required companies are missing in company_master.
    """
    # 1. Resolve and validate all required companies
    companies_by_code: Dict[str, Company] = {}
    for code in REQUIRED_COMPANY_CODES:
        comp = db.execute(
            select(Company).where(Company.company_code == code)
        ).scalar_one_or_none()

        if comp is None:
            raise ValueError(
                f"Required company '{code}' not found in company_master. "
                "Please run seed_companies first before seeding departments."
            )
        companies_by_code[code] = comp

    inserted = 0
    skipped = 0

    # 2. Seed departments for each company
    for comp_code, company in companies_by_code.items():
        for dept_def in DEFAULT_DEPARTMENTS:
            dept_code = dept_def["department_code"]

            # Check if department already exists under this specific company
            existing = db.execute(
                select(Department).where(
                    Department.company_id == company.company_id,
                    Department.department_code == dept_code,
                )
            ).scalar_one_or_none()

            if existing is not None:
                skipped += 1
                logger.info(
                    "Department '%s' already exists for company '%s'. Skipping.",
                    dept_code,
                    comp_code,
                )
                continue

            dept_id = generate_department_uuid(comp_code, dept_code)
            new_dept = Department(
                department_id=dept_id,
                company_id=company.company_id,
                department_code=dept_code,
                department_name=dept_def["department_name"],
                description=dept_def["description"],
                status=dept_def["status"],
            )
            db.add(new_dept)
            inserted += 1
            logger.info(
                "Inserting department '%s' for company '%s' (ID: %s)",
                dept_code,
                comp_code,
                dept_id,
            )

    db.commit()
    return inserted, skipped


def run() -> None:
    """Run department seeding with SessionLocal within an explicit transaction."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    db: Session = SessionLocal()
    try:
        inserted, skipped = seed_departments(db)
        print(
            f"Department Seed Completed: {inserted} inserted, {skipped} skipped (already present)."
        )
    except Exception as exc:
        db.rollback()
        print(f"Error during department seeding: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run()
