"""Seed script for Source Master to populate default lead sources."""
import logging
import uuid
from sqlalchemy import select
from app.database.session import SessionLocal
from app.models.source import SourceMaster

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

INITIAL_SOURCES = [
    {
        "source_code": "WEBSITE",
        "source_name": "Website",
        "description": "Direct enquiries from company website",
        "status": "ACTIVE",
        "is_system": True,
    },
    {
        "source_code": "REFERRAL",
        "source_name": "Referral",
        "description": "Client referrals and partner recommendations",
        "status": "ACTIVE",
        "is_system": True,
    },
    {
        "source_code": "DIRECT",
        "source_name": "Direct",
        "description": "Direct walk-in or outbound sales contact",
        "status": "ACTIVE",
        "is_system": True,
    },
    {
        "source_code": "JUSTDIAL",
        "source_name": "Justdial",
        "description": "Lead acquisition via Justdial platform",
        "status": "ACTIVE",
        "is_system": True,
    },
    {
        "source_code": "INDIAMART",
        "source_name": "IndiaMART",
        "description": "Lead acquisition via IndiaMART marketplace",
        "status": "ACTIVE",
        "is_system": True,
    },
    {
        "source_code": "OTHERS",
        "source_name": "Others",
        "description": "Other miscellaneous acquisition channels",
        "status": "ACTIVE",
        "is_system": True,
    },
]


def seed_sources() -> None:
    session = SessionLocal()
    try:
        created_count = 0
        for item in INITIAL_SOURCES:
            existing = session.execute(
                select(SourceMaster).where(SourceMaster.source_code == item["source_code"])
            ).scalar_one_or_none()
            if not existing:
                src = SourceMaster(
                    source_id=uuid.uuid4(),
                    source_code=item["source_code"],
                    source_name=item["source_name"],
                    description=item["description"],
                    status=item["status"],
                    is_system=item["is_system"],
                )
                session.add(src)
                created_count += 1
        session.commit()
        logger.info(f"Seed sources completed. Added {created_count} sources.")
    except Exception as e:
        session.rollback()
        logger.error(f"Error seeding sources: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed_sources()

