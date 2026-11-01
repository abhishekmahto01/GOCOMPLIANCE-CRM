"""Source Master domain service and repository logic."""
import uuid
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.sales_order import SalesOrder
from app.models.source import SourceMaster
from app.schemas.source import SourceCreate, SourceUpdate

# Fallback default sources if source_master table is ever empty
DEFAULT_SOURCE_TUPLES = [
    ("WEBSITE", "Website", "Direct enquiries from company website"),
    ("REFERRAL", "Referral", "Client referrals and partner recommendations"),
    ("DIRECT", "Direct", "Direct walk-in or outbound sales contact"),
    ("JUSTDIAL", "Justdial", "Lead acquisition via Justdial platform"),
    ("INDIAMART", "IndiaMART", "Lead acquisition via IndiaMART marketplace"),
    ("OTHERS", "Others", "Other miscellaneous acquisition channels"),
]


def list_sources(
    session: Session,
    search: Optional[str] = None,
    status_filter: Optional[str] = None,
) -> List[SourceMaster]:
    """Retrieve all lead sources with optional search and status filtering."""
    stmt = select(SourceMaster)

    if status_filter and status_filter.strip().upper() in {"ACTIVE", "INACTIVE"}:
        stmt = stmt.where(SourceMaster.status == status_filter.strip().upper())

    if search and search.strip():
        term = f"%{search.strip()}%"
        stmt = stmt.where(
            or_(
                SourceMaster.source_code.ilike(term),
                SourceMaster.source_name.ilike(term),
                SourceMaster.description.ilike(term),
            )
        )

    stmt = stmt.order_by(SourceMaster.source_name.asc())
    return list(session.execute(stmt).scalars().all())


def get_source_by_id(session: Session, source_id: uuid.UUID) -> Optional[SourceMaster]:
    """Retrieve a single source by UUID primary key."""
    stmt = select(SourceMaster).where(SourceMaster.source_id == source_id)
    return session.execute(stmt).scalar_one_or_none()


def get_source_by_code(session: Session, source_code: str) -> Optional[SourceMaster]:
    """Retrieve a single source by uppercase code."""
    stmt = select(SourceMaster).where(func.upper(SourceMaster.source_code) == source_code.strip().upper())
    return session.execute(stmt).scalar_one_or_none()


def get_active_source_codes(session: Session) -> List[str]:
    """Retrieve list of active source codes, falling back to defaults if empty."""
    stmt = (
        select(SourceMaster.source_code)
        .where(SourceMaster.status == "ACTIVE")
        .order_by(SourceMaster.source_name.asc())
    )
    codes = list(session.execute(stmt).scalars().all())
    if not codes:
        return [code for code, _, _ in DEFAULT_SOURCE_TUPLES]
    return codes


def get_active_sources(session: Session) -> List[SourceMaster]:
    """Retrieve list of active SourceMaster instances."""
    stmt = (
        select(SourceMaster)
        .where(SourceMaster.status == "ACTIVE")
        .order_by(SourceMaster.source_name.asc())
    )
    sources = list(session.execute(stmt).scalars().all())
    return sources


def create_source(session: Session, source_in: SourceCreate) -> SourceMaster:
    """Create a new lead source in Source Master."""
    norm_code = source_in.source_code.strip().upper()
    norm_name = source_in.source_name.strip()

    # Check unique source_code
    existing_code = session.execute(
        select(SourceMaster).where(func.upper(SourceMaster.source_code) == norm_code)
    ).scalar_one_or_none()
    if existing_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Source with code '{norm_code}' already exists.",
        )

    # Check unique source_name
    existing_name = session.execute(
        select(SourceMaster).where(func.lower(SourceMaster.source_name) == norm_name.lower())
    ).scalar_one_or_none()
    if existing_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Source with name '{norm_name}' already exists.",
        )

    source = SourceMaster(
        source_code=norm_code,
        source_name=norm_name,
        description=source_in.description.strip() if source_in.description else None,
        status=source_in.status,
        is_system=False,
    )
    session.add(source)
    session.commit()
    session.refresh(source)
    return source


def update_source(session: Session, source_id: uuid.UUID, source_in: SourceUpdate) -> SourceMaster:
    """Update an existing source."""
    source = get_source_by_id(session, source_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source not found.",
        )

    if source_in.source_name is not None:
        norm_name = source_in.source_name.strip()
        existing_name = session.execute(
            select(SourceMaster).where(
                func.lower(SourceMaster.source_name) == norm_name.lower(),
                SourceMaster.source_id != source_id,
            )
        ).scalar_one_or_none()
        if existing_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Source with name '{norm_name}' already exists.",
            )
        source.source_name = norm_name

    if source_in.description is not None:
        source.description = source_in.description.strip() if source_in.description else None

    if source_in.status is not None:
        source.status = source_in.status

    session.commit()
    session.refresh(source)
    return source


def delete_source(session: Session, source_id: uuid.UUID) -> bool:
    """Delete a source, preventing deletion if system source or referenced by orders."""
    source = get_source_by_id(session, source_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source not found.",
        )

    if source.is_system:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete core system source. You may deactivate it by setting status to INACTIVE instead.",
        )

    # Check if any sales orders reference this source
    order_count = session.execute(
        select(func.count(SalesOrder.order_id)).where(
            func.upper(SalesOrder.lead_source) == source.source_code.upper()
        )
    ).scalar() or 0

    if order_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete source '{source.source_name}' because it is linked to {order_count} sales order(s). You can mark it as INACTIVE instead.",
        )

    session.delete(source)
    session.commit()
    return True
