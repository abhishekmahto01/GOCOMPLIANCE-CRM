"""Database health verification service."""
import logging
from typing import Any, Dict, Tuple

from sqlalchemy import text

from app.database.session import engine

logger = logging.getLogger(__name__)


def check_database_health() -> Tuple[bool, Dict[str, Any]]:
    """Verify connectivity to the PostgreSQL database.

    Executes a safe read-only query (SELECT 1, current_database())
    and returns a tuple of (is_healthy, payload).

    Never exposes credentials or raw connection URLs in the returned payload.
    """
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1, current_database()"))
            row = result.fetchone()
            db_name = row[1] if row and len(row) > 1 else "unknown"

            return True, {
                "status": "healthy",
                "service": "postgresql",
                "database": db_name,
            }
    except Exception as exc:
        logger.error("Database health check failed: %s", type(exc).__name__)
        return False, {
            "status": "unhealthy",
            "service": "postgresql",
            "detail": "Database connection unavailable",
        }
