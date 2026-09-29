"""Employee code generation service with concurrency row-locking."""
import re
import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.company import Company
from app.models.user import User


def extract_code_number(code: str, prefix: str) -> Optional[int]:
    """Extract integer sequence number from an employee code given its prefix."""
    if not code or not prefix:
        return None
    pattern = rf"^{re.escape(prefix)}(\d+)$"
    match = re.match(pattern, code, re.IGNORECASE)
    if match:
        try:
            return int(match.group(1))
        except ValueError:
            return None
    return None


def generate_employee_code(session: Session, company_id: uuid.UUID) -> str:
    """Generate the next sequential employee code for a company.

    Uses PostgreSQL row-level locking (SELECT ... FOR UPDATE) on company_master
    to prevent race conditions, guarantee strictly sequential employee codes,
    re-use sequence gaps if employees were deleted, and update next_employee_number atomically.

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

    prefix = company.employee_code_prefix.upper()

    # Query all existing employee codes for this company
    existing_codes = session.execute(
        select(User.employee_code).where(User.company_id == company_id)
    ).scalars().all()

    used_numbers = set()
    for code in existing_codes:
        num = extract_code_number(code, prefix)
        if num is not None:
            used_numbers.add(num)

    if not used_numbers:
        assigned_number = max(company.next_employee_number or 1, 1)
    else:
        candidate = 1
        while candidate in used_numbers:
            candidate += 1
        assigned_number = candidate

    # Format code with minimum 4 digits padding (e.g. CG0001; 10000 -> CG10000)
    employee_code = f"{prefix}{assigned_number:04d}"

    # Update next_employee_number to next available integer
    max_used = max(used_numbers, default=0)
    company.next_employee_number = max(max_used, assigned_number) + 1

    return employee_code

