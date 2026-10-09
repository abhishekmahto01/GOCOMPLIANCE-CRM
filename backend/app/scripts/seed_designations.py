"""Idempotent seed script for global reusable designation master records."""
import logging
import sys
import uuid
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database.session import SessionLocal
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


def generate_designation_uuid(param1: str, param2: Optional[str] = None) -> uuid.UUID:
    """Generate a deterministic UUIDv5 for a designation_code globally (or company_code:designation_code for legacy callers)."""
    if param2 is not None:
        key = param2.upper()
    else:
        key = param1.upper()
    return uuid.uuid5(NAMESPACE_DESIGNATION, key)


def seed_designations(db: Session) -> Tuple[int, int]:
    """Idempotently seed the default global reusable designations across all companies.

    Returns:
        Tuple[int, int]: (inserted_count, skipped_count)
    """
    inserted = 0
    skipped = 0

    for desig_def in DEFAULT_DESIGNATIONS:
        desig_code = desig_def["designation_code"]

        # Check if designation already exists globally
        existing = db.execute(
            select(Designation).where(
                func.upper(Designation.designation_code) == desig_code.upper(),
            )
        ).scalar_one_or_none()

        if existing is not None:
            skipped += 1
            logger.info(
                "Designation '%s' already exists globally. Skipping.",
                desig_code,
            )
            continue

        desig_id = generate_designation_uuid(desig_code)
        new_desig = Designation(
            designation_id=desig_id,
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
            "Inserting global designation '%s' (ID: %s, Rank: %d, Managerial: %s)",
            desig_code,
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
