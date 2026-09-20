"""Idempotent seed script for initial company-specific designation master records."""
import logging
import sys
import uuid
from typing import Any, Dict, List, Tuple

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.session import SessionLocal
from app.models.company import Company
from app.models.designation import Designation

logger = logging.getLogger("seed_designations")

# Stable namespace for deterministic Designation UUID generation
NAMESPACE_DESIGNATION = uuid.UUID("2c3d4e5f-6a7b-8c9d-0e1f-2a3b4c5d6e7f")

REQUIRED_COMPANY_CODES: List[str] = [
    "GOCOMPLIANCES",
    "ENTERPERNERSHIP",
    "BRANDMINGO",
]

DEFAULT_DESIGNATIONS: List[Dict[str, Any]] = [
    {
        "designation_code": "EXECUTIVE",
        "designation_name": "Executive",
        "level_rank": 10,
        "is_managerial": False,
        "description": "Entry-level operational and executive position",
        "status": "ACTIVE",
    },
    {
        "designation_code": "SENIOR_EXECUTIVE",
        "designation_name": "Senior Executive",
        "level_rank": 20,
        "is_managerial": False,
        "description": "Experienced operational professional handling complex workflows",
        "status": "ACTIVE",
    },
    {
        "designation_code": "ASSISTANT_MANAGER",
        "designation_name": "Assistant Manager",
        "level_rank": 30,
        "is_managerial": True,
        "description": "First-line supervisory and managerial position",
        "status": "ACTIVE",
    },
    {
        "designation_code": "MANAGER",
        "designation_name": "Manager",
        "level_rank": 40,
        "is_managerial": True,
        "description": "Functional team manager responsible for operational delivery",
        "status": "ACTIVE",
    },
    {
        "designation_code": "HEAD",
        "designation_name": "Head",
        "level_rank": 50,
        "is_managerial": True,
        "description": "Departmental head leading strategy and departmental performance",
        "status": "ACTIVE",
    },
    {
        "designation_code": "DIRECTOR",
        "designation_name": "Director",
        "level_rank": 60,
        "is_managerial": True,
        "description": "Executive director overseeing company-wide business verticals",
        "status": "ACTIVE",
    },
]


def generate_designation_uuid(company_code: str, designation_code: str) -> uuid.UUID:
    """Generate a deterministic UUIDv5 for a (company_code, designation_code) pair."""
    key = f"{company_code.upper()}:{designation_code.upper()}"
    return uuid.uuid5(NAMESPACE_DESIGNATION, key)


def seed_designations(db: Session) -> Tuple[int, int]:
    """Idempotently seed the 6 default designations for all 3 required companies.

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
                "Please run seed_companies first before seeding designations."
            )
        companies_by_code[code] = comp

    inserted = 0
    skipped = 0

    # 2. Seed designations for each company
    for comp_code, company in companies_by_code.items():
        for desig_def in DEFAULT_DESIGNATIONS:
            desig_code = desig_def["designation_code"]

            # Check if designation already exists under this specific company
            existing = db.execute(
                select(Designation).where(
                    Designation.company_id == company.company_id,
                    Designation.designation_code == desig_code,
                )
            ).scalar_one_or_none()

            if existing is not None:
                skipped += 1
                logger.info(
                    "Designation '%s' already exists for company '%s'. Skipping.",
                    desig_code,
                    comp_code,
                )
                continue

            desig_id = generate_designation_uuid(comp_code, desig_code)
            new_desig = Designation(
                designation_id=desig_id,
                company_id=company.company_id,
                designation_code=desig_code,
                designation_name=desig_def["designation_name"],
                level_rank=desig_def["level_rank"],
                is_managerial=desig_def["is_managerial"],
                description=desig_def["description"],
                status=desig_def["status"],
            )
            db.add(new_desig)
            inserted += 1
            logger.info(
                "Inserting designation '%s' for company '%s' (ID: %s, Rank: %d, Managerial: %s)",
                desig_code,
                comp_code,
                desig_id,
                desig_def["level_rank"],
                desig_def["is_managerial"],
            )

    db.commit()
    return inserted, skipped


def run() -> None:
    """Run designation seeding with SessionLocal within an explicit transaction."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    db: Session = SessionLocal()
    try:
        inserted, skipped = seed_designations(db)
        print(
            f"Designation Seed Completed: {inserted} inserted, {skipped} skipped (already present)."
        )
    except Exception as exc:
        db.rollback()
        print(f"Error during designation seeding: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run()
