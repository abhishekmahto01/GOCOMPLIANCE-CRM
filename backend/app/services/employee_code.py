"""Employee code generation service with concurrency row-locking."""
import uuid
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.company import Company


def generate_employee_code(session: Session, company_id: uuid.UUID) -> str:
    """Generate the next sequential employee code for a company.

    Uses PostgreSQL row-level locking (SELECT ... FOR UPDATE) on company_master
    to prevent race conditions, guarantee strictly sequential employee codes,
    and increment next_employee_number atomically.

    Args:
        session: Active SQLAlchemy database session.
        company_id: UUID of the target company.

    Returns:
        Generated uppercase employee code string (e.g., 'CG0001', 'EP0001', 'BM0001').

    Raises:
        ValueError: If company is not found or is inactive.
    """
    stmt = (
        select(Company)
        .where(Company.company_id == company_id)
        .with_for_update()
    )
    company = session.execute(stmt).scalar_one_or_none()

    if not company:
        raise ValueError(f"Company with ID '{company_id}' not found")

    if company.status != "ACTIVE":
        raise ValueError(
            f"Cannot generate employee code for inactive company '{company.company_name}'"
        )

    current_number = company.next_employee_number
    prefix = company.employee_code_prefix.upper()

    # Format code with minimum 4 digits padding (e.g. CG0001; 10000 -> CG10000)
    employee_code = f"{prefix}{current_number:04d}"

    # Increment counter atomically within the active transaction
    company.next_employee_number = current_number + 1

    return employee_code
