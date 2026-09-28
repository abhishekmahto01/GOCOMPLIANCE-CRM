"""Service and Licence domain service and repository logic."""
import uuid
from typing import List, Optional
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.operation_application import OperationApplication
from app.models.sales_order import SalesOrder
from app.models.service import ServiceMaster, ServiceRequiredDocument
from app.schemas.service import ServiceCreate, ServiceUpdate


def list_services(
    session: Session,
    search: Optional[str] = None,
    category: Optional[str] = None,
    status_filter: Optional[str] = None,
) -> List[ServiceMaster]:
    """Retrieve all services/licenses with optional search, category, and status filtering.

    Args:
        session: Active SQLAlchemy session.
        search: Optional search term for code, name, or description.
        category: Optional category filter.
        status_filter: Optional status ('ACTIVE' or 'INACTIVE').

    Returns:
        List of ServiceMaster instances ordered by service_name ASC.
    """
    stmt = select(ServiceMaster)

    if status_filter and status_filter.strip().upper() in {"ACTIVE", "INACTIVE"}:
        stmt = stmt.where(ServiceMaster.status == status_filter.strip().upper())

    if category and category.strip():
        stmt = stmt.where(func.upper(ServiceMaster.category) == category.strip().upper())

    if search and search.strip():
        term = f"%{search.strip()}%"
        stmt = stmt.where(
            or_(
                ServiceMaster.service_code.ilike(term),
                ServiceMaster.service_name.ilike(term),
                ServiceMaster.category.ilike(term),
                ServiceMaster.description.ilike(term),
            )
        )

    stmt = stmt.order_by(ServiceMaster.service_name.asc())
    return list(session.execute(stmt).scalars().all())


def get_service_by_id(session: Session, service_id: uuid.UUID) -> Optional[ServiceMaster]:
    """Retrieve a single service by UUID primary key."""
    stmt = select(ServiceMaster).where(ServiceMaster.service_id == service_id)
    return session.execute(stmt).scalar_one_or_none()


def create_service(session: Session, service_in: ServiceCreate) -> ServiceMaster:
    """Create a new service/licence record ensuring uniqueness of service_code.

    Args:
        session: Active SQLAlchemy session.
        service_in: Validated ServiceCreate schema payload.

    Returns:
        The newly created ServiceMaster instance.

    Raises:
        ValueError: If service code or name already exists.
    """
    norm_code = service_in.service_code.strip().upper()
    norm_name = service_in.service_name.strip()

    # 1. Uniqueness check for service_code
    existing_code = session.execute(
        select(ServiceMaster.service_id).where(func.upper(ServiceMaster.service_code) == norm_code)
    ).scalar_one_or_none()
    if existing_code:
        raise ValueError(f"License/Service code '{norm_code}' is already registered.")

    # 2. Uniqueness check for service_name
    existing_name = session.execute(
        select(ServiceMaster.service_id).where(func.lower(ServiceMaster.service_name) == norm_name.lower())
    ).scalar_one_or_none()
    if existing_name:
        raise ValueError(f"License/Service name '{norm_name}' is already registered.")

    new_service = ServiceMaster(
        service_id=uuid.uuid4(),
        service_code=norm_code,
        service_name=norm_name,
        category=service_in.category.strip().upper(),
        description=service_in.description.strip() if service_in.description else None,
        base_price=service_in.base_price,
        govt_fee=service_in.govt_fee,
        standard_turnaround_days=service_in.standard_turnaround_days or 15,
        status=service_in.status.strip().upper() if service_in.status else "ACTIVE",
    )

    try:
        session.add(new_service)
        session.flush()

        # Add optional required documents if provided
        if service_in.required_documents:
            for doc in service_in.required_documents:
                doc_entity = ServiceRequiredDocument(
                    doc_config_id=uuid.uuid4(),
                    service_id=new_service.service_id,
                    document_code=doc.document_code.strip().upper(),
                    document_name=doc.document_name.strip(),
                    is_mandatory=doc.is_mandatory,
                    display_order=doc.display_order,
                )
                session.add(doc_entity)
            session.flush()

        session.commit()
        session.refresh(new_service)
        return new_service
    except Exception:
        session.rollback()
        raise


def update_service(
    session: Session,
    target_service: ServiceMaster,
    update_data: ServiceUpdate,
) -> ServiceMaster:
    """Update an existing service/licence record.

    Args:
        session: Active SQLAlchemy session.
        target_service: ServiceMaster model instance to update.
        update_data: ServiceUpdate schema payload.

    Returns:
        The refreshed ServiceMaster instance.

    Raises:
        ValueError: If service name conflicts with another service.
    """
    try:
        if update_data.service_name is not None:
            norm_name = update_data.service_name.strip()
            if norm_name.lower() != target_service.service_name.lower():
                existing = session.execute(
                    select(ServiceMaster.service_id).where(
                        func.lower(ServiceMaster.service_name) == norm_name.lower(),
                        ServiceMaster.service_id != target_service.service_id,
                    )
                ).scalar_one_or_none()
                if existing:
                    raise ValueError(f"License/Service name '{norm_name}' is already taken.")
                target_service.service_name = norm_name

        if update_data.category is not None:
            target_service.category = update_data.category.strip().upper()

        if "description" in update_data.model_fields_set:
            target_service.description = (
                update_data.description.strip() if update_data.description else None
            )

        if update_data.base_price is not None:
            target_service.base_price = update_data.base_price

        if update_data.govt_fee is not None:
            target_service.govt_fee = update_data.govt_fee

        if update_data.standard_turnaround_days is not None:
            target_service.standard_turnaround_days = update_data.standard_turnaround_days

        if update_data.status is not None:
            norm_status = update_data.status.strip().upper()
            if norm_status not in {"ACTIVE", "INACTIVE"}:
                raise ValueError("Status must be either 'ACTIVE' or 'INACTIVE'.")
            target_service.status = norm_status

        session.flush()
        session.commit()
        session.refresh(target_service)
        return target_service
    except Exception:
        session.rollback()
        raise


def delete_service(session: Session, target_service: ServiceMaster) -> None:
    """Delete a service/licence record ensuring no dependent sales orders or applications exist.

    Args:
        session: Active SQLAlchemy session.
        target_service: ServiceMaster model instance to delete.

    Raises:
        ValueError: If service is linked to sales orders or applications.
    """
    # 1. Check for sales orders linked to this service
    order_count = session.execute(
        select(func.count(SalesOrder.order_id)).where(SalesOrder.service_id == target_service.service_id)
    ).scalar() or 0
    if order_count > 0:
        raise ValueError(
            f"Cannot delete license '{target_service.service_name}' because {order_count} sales order(s) are linked to it. Please mark the license as INACTIVE instead."
        )

    # 2. Check for operations applications linked to this service
    op_count = session.execute(
        select(func.count(OperationApplication.application_id)).where(OperationApplication.service_id == target_service.service_id)
    ).scalar() or 0
    if op_count > 0:
        raise ValueError(
            f"Cannot delete license '{target_service.service_name}' because {op_count} operations application(s) are linked to it. Please mark the license as INACTIVE instead."
        )

    try:
        session.delete(target_service)
        session.flush()
        session.commit()
    except Exception:
        session.rollback()
        raise
