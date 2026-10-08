"""Service for managing Operations Coordinator Configuration per company."""
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.company import Company
from app.models.operations_coordinator_config import OperationsCoordinatorConfig
from app.models.user import User
from app.schemas.coordinator_config import (
    EligibleCoordinatorOption,
    OperationsCoordinatorConfigRead,
)
from app.services import permissions
from app.services.operation_service import is_disallowed_ops_assignee


def list_coordinator_configs(session: Session) -> List[OperationsCoordinatorConfigRead]:
    """Retrieve all company coordinator configurations, creating default records for active companies if needed."""
    companies = (
        session.execute(
            select(Company)
            .where(Company.status == "ACTIVE")
            .order_by(Company.company_name)
        )
        .scalars()
        .all()
    )

    results: List[OperationsCoordinatorConfigRead] = []

    for comp in companies:
        config = (
            session.execute(
                select(OperationsCoordinatorConfig)
                .options(
                    joinedload(OperationsCoordinatorConfig.coordinator)
                    .joinedload(User.department),
                    joinedload(OperationsCoordinatorConfig.updated_by),
                )
                .where(OperationsCoordinatorConfig.company_id == comp.company_id)
            )
            .scalars()
            .first()
        )

        if config:
            coord = config.coordinator
            upd = config.updated_by
            results.append(
                OperationsCoordinatorConfigRead(
                    config_id=config.config_id,
                    company_id=comp.company_id,
                    company_name=comp.company_name,
                    company_code=comp.company_code,
                    coordinator_user_id=config.coordinator_user_id,
                    coordinator_name=f"{coord.first_name} {coord.last_name}".strip() if coord else None,
                    coordinator_employee_code=coord.employee_code if coord else None,
                    coordinator_email=coord.official_email if coord else None,
                    coordinator_department_name=coord.department.department_name if coord and coord.department else None,
                    updated_by_user_id=config.updated_by_user_id,
                    updated_by_name=f"{upd.first_name} {upd.last_name}".strip() if upd else None,
                    updated_at=config.updated_at,
                )
            )
        else:
            # Unconfigured company row
            now_utc = datetime.now(timezone.utc)
            results.append(
                OperationsCoordinatorConfigRead(
                    config_id=uuid.uuid4(),
                    company_id=comp.company_id,
                    company_name=comp.company_name,
                    company_code=comp.company_code,
                    coordinator_user_id=None,
                    coordinator_name=None,
                    coordinator_employee_code=None,
                    coordinator_email=None,
                    coordinator_department_name=None,
                    updated_by_user_id=None,
                    updated_by_name=None,
                    updated_at=now_utc,
                )
            )

    return results


def get_coordinator_for_company(session: Session, company_id: uuid.UUID) -> Optional[User]:
    """Retrieve the configured active Operations coordinator for a company.
    
    Returns None if no coordinator is configured, or if the configured coordinator is inactive.
    """
    config = (
        session.execute(
            select(OperationsCoordinatorConfig)
            .options(
                joinedload(OperationsCoordinatorConfig.coordinator)
                .joinedload(User.department)
            )
            .where(OperationsCoordinatorConfig.company_id == company_id)
        )
        .scalars()
        .first()
    )

    if not config or not config.coordinator_user_id:
        return None

    coordinator = config.coordinator
    if not coordinator:
        coordinator = session.get(User, config.coordinator_user_id)

    if coordinator and coordinator.account_status == "ACTIVE":
        return coordinator

    return None


def update_coordinator_config(
    session: Session,
    company_id: uuid.UUID,
    coordinator_user_id: Optional[uuid.UUID],
    updated_by: User,
) -> OperationsCoordinatorConfigRead:
    """Update or create the default Operations coordinator for a company."""
    company = session.get(Company, company_id)
    if not company:
        raise ValueError(f"Company with ID '{company_id}' not found.")

    coordinator: Optional[User] = None
    if coordinator_user_id:
        coordinator = session.get(User, coordinator_user_id)
        if not coordinator:
            raise ValueError(f"Target coordinator user '{coordinator_user_id}' not found.")
        if coordinator.account_status != "ACTIVE":
            raise ValueError("Configured coordinator must be an active employee.")
        if is_disallowed_ops_assignee(coordinator):
            raise ValueError(
                "Selected user cannot be an Operations coordinator (disallowed role / department)."
            )

    config = (
        session.execute(
            select(OperationsCoordinatorConfig).where(
                OperationsCoordinatorConfig.company_id == company_id
            )
        )
        .scalars()
        .first()
    )

    now_utc = datetime.now(timezone.utc)
    if not config:
        config = OperationsCoordinatorConfig(
            company_id=company_id,
            coordinator_user_id=coordinator_user_id,
            updated_by_user_id=updated_by.user_id,
            created_at=now_utc,
            updated_at=now_utc,
        )
        session.add(config)
    else:
        config.coordinator_user_id = coordinator_user_id
        config.updated_by_user_id = updated_by.user_id
        config.updated_at = now_utc

    session.commit()
    session.refresh(config)

    coord = session.get(User, config.coordinator_user_id) if config.coordinator_user_id else None

    return OperationsCoordinatorConfigRead(
        config_id=config.config_id,
        company_id=company.company_id,
        company_name=company.company_name,
        company_code=company.company_code,
        coordinator_user_id=config.coordinator_user_id,
        coordinator_name=f"{coord.first_name} {coord.last_name}".strip() if coord else None,
        coordinator_employee_code=coord.employee_code if coord else None,
        coordinator_email=coord.official_email if coord else None,
        coordinator_department_name=coord.department.department_name if coord and coord.department else None,
        updated_by_user_id=updated_by.user_id,
        updated_by_name=f"{updated_by.first_name} {updated_by.last_name}".strip(),
        updated_at=config.updated_at,
    )


def get_eligible_coordinators(session: Session) -> List[EligibleCoordinatorOption]:
    """Retrieve all active Operations team members across companies eligible to be Operations coordinators."""
    stmt = (
        select(User)
        .options(
            joinedload(User.company),
            joinedload(User.department),
            joinedload(User.designation),
        )
        .where(User.account_status == "ACTIVE")
    )

    users = session.execute(stmt).scalars().all()
    eligible: List[EligibleCoordinatorOption] = []

    for u in users:
        if is_disallowed_ops_assignee(u):
            continue

        dept_name = u.department.department_name.lower() if u.department else ""
        dept_code = u.department.department_code.upper() if u.department else ""
        has_ops_dept = (
            "operat" in dept_name
            or "operat" in dept_code
            or dept_code in ("OP", "OPS", "OPERATIONS")
        )
        has_ops_perm = permissions.has_permission(session, u, "OPERATIONS", "view")

        if has_ops_dept or has_ops_perm:
            comp_name = u.company.company_name if u.company else "Unknown"
            comp_code = u.company.company_code if u.company else "UNK"
            dept_display = u.department.department_name if u.department else None
            desig_display = u.designation.designation_name if u.designation else None

            eligible.append(
                EligibleCoordinatorOption(
                    user_id=u.user_id,
                    employee_code=u.employee_code,
                    full_name=f"{u.first_name} {u.last_name}".strip(),
                    email=u.official_email,
                    company_id=u.company_id,
                    company_name=comp_name,
                    company_code=comp_code,
                    department_name=dept_display,
                    designation_name=desig_display,
                )
            )

    eligible.sort(key=lambda o: (o.full_name, o.employee_code))
    return eligible
