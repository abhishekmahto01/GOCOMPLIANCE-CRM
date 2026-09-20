"""Idempotent seed script for initial company master records."""
import logging
import sys
import uuid
from typing import Dict, List, Tuple

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.session import SessionLocal
from app.models.company import Company

logger = logging.getLogger("seed_companies")

# Stable namespace for deterministic Company UUID generation
NAMESPACE_COMPANY = uuid.UUID("0a1b2c3d-4e5f-6a7b-8c9d-0e1f2a3b4c5d")

INITIAL_COMPANIES: List[Dict[str, str]] = [
    {
        "company_code": "GOCOMPLIANCES",
        "company_name": "Gocompliances",
        "employee_code_prefix": "CG",
        "next_employee_number": 1,
        "status": "ACTIVE",
        "legal_name": None,
    },
    {
        "company_code": "ENTERPERNERSHIP",
        "company_name": "Enterpernership",
        "employee_code_prefix": "EP",
        "next_employee_number": 1,
        "status": "ACTIVE",
        "legal_name": None,
    },
    {
        "company_code": "BRANDMINGO",
        "company_name": "Brandmingo",
        "employee_code_prefix": "BM",
        "next_employee_number": 1,
        "status": "ACTIVE",
        "legal_name": None,
    },
]


def generate_company_uuid(company_code: str) -> uuid.UUID:
    """Generate a deterministic UUIDv5 for a company code."""
    return uuid.uuid5(NAMESPACE_COMPANY, company_code.upper())


def seed_companies(db: Session) -> Tuple[int, int]:
    """Idempotently seed the initial 3 company master records.

    Returns:
        Tuple[int, int]: (inserted_count, skipped_count)
    """
    inserted = 0
    skipped = 0

    for item in INITIAL_COMPANIES:
        code = item["company_code"]
        # Check if company already exists by unique code
        existing = db.execute(
            select(Company).where(Company.company_code == code)
        ).scalar_one_or_none()

        if existing is not None:
            skipped += 1
            logger.info("Company '%s' already exists. Skipping insertion.", code)
            continue

        company_id = generate_company_uuid(code)
        new_company = Company(
            company_id=company_id,
            company_code=code,
            company_name=item["company_name"],
            legal_name=item["legal_name"],
            employee_code_prefix=item["employee_code_prefix"],
            next_employee_number=item["next_employee_number"],
            status=item["status"],
        )
        db.add(new_company)
        inserted += 1
        logger.info(
            "Inserting company '%s' (ID: %s, Prefix: %s)",
            code,
            company_id,
            item["employee_code_prefix"],
        )

    db.commit()
    return inserted, skipped


def run() -> None:
    """Run seeding using SessionLocal within an explicit transaction."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    db: Session = SessionLocal()
    try:
        inserted, skipped = seed_companies(db)
        print(
            f"Company Seed Completed: {inserted} inserted, {skipped} skipped (already present)."
        )
    except Exception as exc:
        db.rollback()
        print(f"Error during company seeding: {type(exc).__name__}", file=sys.stderr)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run()
