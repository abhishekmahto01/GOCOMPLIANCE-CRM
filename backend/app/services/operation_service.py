"""Operations service layer handling task assignment, reassignment, status transitions, scoping, and dashboard analytics."""
import uuid
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import desc, func, or_, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.client import ClientMaster
from app.models.company import Company
from app.models.department import Department
from app.models.designation import Designation
from app.models.module import Module
from app.models.operation_application import (
    ApplicationActivityLog,
    ApplicationAssignmentHistory,
    ApplicationDocument,
    OperationApplication,
)
from app.models.sales_order import SalesOrder
from app.models.user import User
from app.models.user_module_permission import UserModulePermission
from app.schemas.operation_application import (
    ActivityLogRead,
    ApplicationDocRead,
    AssignmentHistoryRead,
    ExecutiveWorkloadItem,
    OperationApplicationDetailRead,
    OperationApplicationRead,
    OperationsDashboardResponse,
    OperationsKpiSummary,
    OperationsStatusBreakdownItem,
    OperationsTaskListResponse,
    OperationsTaskSummary,
)
from app.services import permissions

# Allowed forward status transitions map
VALID_STATUS_TRANSITIONS: Dict[str, List[str]] = {
    "UNASSIGNED": ["ASSIGNED", "CANCELLED"],
    "ASSIGNED": ["IN_PROGRESS", "UNASSIGNED", "CANCELLED"],
    "IN_PROGRESS": ["PENDING_DOCUMENTS", "READY_FOR_SUBMISSION", "SUBMITTED", "CANCELLED"],
    "PENDING_DOCUMENTS": ["IN_PROGRESS", "READY_FOR_SUBMISSION", "CANCELLED"],
    "READY_FOR_SUBMISSION": ["SUBMITTED", "IN_PROGRESS", "CANCELLED"],
    "SUBMITTED": ["AUTHORITY_QUERY", "APPROVED", "CANCELLED"],
    "AUTHORITY_QUERY": ["SUBMITTED", "IN_PROGRESS", "CANCELLED"],
    "APPROVED": [],
    "CANCELLED": [],
}

STATUS_COLOR_MAP = {
    "UNASSIGNED": "#64748B",
    "ASSIGNED": "#3B82F6",
    "IN_PROGRESS": "#6366F1",
    "PENDING_DOCUMENTS": "#F59E0B",
    "READY_FOR_SUBMISSION": "#06B6D4",
    "SUBMITTED": "#8B5CF6",
    "AUTHORITY_QUERY": "#F43F5E",
    "APPROVED": "#10B981",
    "CANCELLED": "#9CA3AF",
}

STATUS_LABEL_MAP = {
    "UNASSIGNED": "Unassigned",
    "ASSIGNED": "Assigned",
    "IN_PROGRESS": "In Progress",
    "PENDING_DOCUMENTS": "Pending Documents",
    "READY_FOR_SUBMISSION": "Ready for Submission",
    "SUBMITTED": "Submitted",
    "AUTHORITY_QUERY": "Authority Query",
    "APPROVED": "Approved",
    "CANCELLED": "Cancelled",
}


class ApplicationNotFoundError(Exception):
    """Raised when application is not found."""
    pass


class InvalidStatusTransitionError(Exception):
    """Raised when an invalid state transition is requested."""
    pass


class AssignmentAuthorizationError(Exception):
    """Raised when a user is not authorized to assign or reassign tasks."""
    pass


def _to_application_read(app: OperationApplication) -> OperationApplicationRead:
    """Convert an OperationApplication ORM instance into OperationApplicationRead schema."""
    today = date.today()
    is_overdue = bool(
        app.target_due_date
        and app.target_due_date < today
        and app.application_status not in ("APPROVED", "CANCELLED")
    )
    is_due_soon = bool(
        app.target_due_date
        and 0 <= (app.target_due_date - today).days <= 3
        and app.application_status not in ("APPROVED", "CANCELLED")
    )

    doc_list = app.documents if hasattr(app, "documents") and app.documents is not None else []
    docs_total = len(doc_list)
    docs_completed = sum(1 for d in doc_list if d.status == "VERIFIED")

    client_name = app.client.client_name if app.client else None
    client_phone = None
    client_email = None
    if app.client:
        client_phone = app.client.contact_phone
        client_email = app.client.contact_email
    elif app.sales_order and app.sales_order.client:
        client_name = app.sales_order.client.client_name
        client_phone = app.sales_order.client.contact_phone
        client_email = app.sales_order.client.contact_email

    service_name = app.service.service_name if app.service else (app.sales_order.service.service_name if app.sales_order and app.sales_order.service else None)
    service_code = app.service.service_code if app.service else (app.sales_order.service.service_code if app.sales_order and app.sales_order.service else None)

    salesperson_name = None
    salesperson_code = None
    order_date = None
    if app.sales_order:
        order_date = app.sales_order.order_date
        if app.sales_order.salesperson:
            salesperson_name = f"{app.sales_order.salesperson.first_name} {app.sales_order.salesperson.last_name}".strip()
            salesperson_code = app.sales_order.salesperson.employee_code

    assigned_to_name = None
    assigned_to_code = None
    if app.assigned_to:
        assigned_to_name = f"{app.assigned_to.first_name} {app.assigned_to.last_name}".strip()
        assigned_to_code = app.assigned_to.employee_code

    assigned_by_name = None
    if app.assigned_by:
        assigned_by_name = f"{app.assigned_by.first_name} {app.assigned_by.last_name}".strip()

    formatted_assigned_at = app.assigned_at.strftime("%d %b %Y, %I:%M %p") if app.assigned_at else None
    formatted_due_date = app.target_due_date.strftime("%d %b %Y") if app.target_due_date else None
    formatted_order_date = order_date.strftime("%d %b %Y") if order_date else None

    return OperationApplicationRead(
        application_id=app.application_id,
        application_number=app.application_number,
        sales_order_id=app.sales_order_id,
        sales_order_number=app.sales_order.order_number if app.sales_order else None,
        company_id=app.company_id,
        client_id=app.client_id,
        client_name=client_name,
        client_phone=client_phone,
        client_email=client_email,
        service_id=app.service_id,
        service_name=service_name,
        service_code=service_code,
        salesperson_name=salesperson_name,
        salesperson_code=salesperson_code,
        assigned_to_user_id=app.assigned_to_user_id,
        assigned_to_name=assigned_to_name,
        assigned_to_code=assigned_to_code,
        assigned_by_user_id=app.assigned_by_user_id,
        assigned_by_name=assigned_by_name,
        assigned_at=app.assigned_at,
        formatted_assigned_at=formatted_assigned_at,
        priority=app.priority,
        application_status=app.application_status,
        target_due_date=app.target_due_date,
        formatted_due_date=formatted_due_date,
        completion_date=app.completion_date,
        assignment_notes=app.assignment_notes,
        documents_completed=docs_completed,
        documents_total=docs_total,
        is_overdue=is_overdue,
        is_due_soon=is_due_soon,
        order_date=order_date,
        formatted_order_date=formatted_order_date,
        created_at=app.created_at,
        updated_at=app.updated_at,
    )


def _to_application_detail_read(app: OperationApplication) -> OperationApplicationDetailRead:
    """Convert an OperationApplication ORM instance into full detail schema with documents and logs."""
    base = _to_application_read(app)
    
    docs_read: List[ApplicationDocRead] = []
    if hasattr(app, "documents") and app.documents:
        for d in app.documents:
            v_name = f"{d.verified_by.first_name} {d.verified_by.last_name}".strip() if d.verified_by else None
            docs_read.append(
                ApplicationDocRead(
                    app_doc_id=d.app_doc_id,
                    application_id=d.application_id,
                    document_code=d.document_code,
                    document_name=d.document_name,
                    is_mandatory=d.is_mandatory,
                    status=d.status,
                    rejection_reason=d.rejection_reason,
                    verified_by_user_id=d.verified_by_user_id,
                    verified_by_name=v_name,
                    verified_at=d.verified_at,
                    created_at=d.created_at,
                    updated_at=d.updated_at,
                )
            )

    history_read: List[AssignmentHistoryRead] = []
    if hasattr(app, "assignment_history") and app.assignment_history:
        for h in app.assignment_history:
            by_name = f"{h.assigned_by.first_name} {h.assigned_by.last_name}".strip() if h.assigned_by else None
            prev_name = f"{h.previous_assignee.first_name} {h.previous_assignee.last_name}".strip() if h.previous_assignee else None
            new_name = f"{h.new_assignee.first_name} {h.new_assignee.last_name}".strip() if h.new_assignee else None
            history_read.append(
                AssignmentHistoryRead(
                    history_id=h.history_id,
                    application_id=h.application_id,
                    assigned_by_user_id=h.assigned_by_user_id,
                    assigned_by_name=by_name,
                    previous_assignee_user_id=h.previous_assignee_user_id,
                    previous_assignee_name=prev_name,
                    new_assignee_user_id=h.new_assignee_user_id,
                    new_assignee_name=new_name,
                    reason=h.reason,
                    assigned_at=h.assigned_at,
                )
            )

    logs_read: List[ActivityLogRead] = []
    if hasattr(app, "activity_logs") and app.activity_logs:
        for log in app.activity_logs:
            actor_name = f"{log.actor.first_name} {log.actor.last_name}".strip() if log.actor else None
            logs_read.append(
                ActivityLogRead(
                    activity_id=log.activity_id,
                    application_id=log.application_id,
                    actor_user_id=log.actor_user_id,
                    actor_name=actor_name,
                    action_type=log.action_type,
                    old_value=log.old_value,
                    new_value=log.new_value,
                    comment=log.comment,
                    created_at=log.created_at,
                )
            )

    return OperationApplicationDetailRead(
        **base.model_dump(),
        documents=docs_read,
        assignment_history=history_read,
        activity_logs=logs_read,
    )


def _apply_operations_scope(
    stmt: Any,
    user: User,
    context: permissions.DataScopeContext,
) -> Any:
    """Apply RBAC data scope filters to OperationApplication queries."""
    if context.scope == "ALL":
        return stmt
    if context.scope == "COMPANY":
        return stmt.where(OperationApplication.company_id == context.company_id)
    if context.scope == "DEPARTMENT":
        # Scoped to company
        return stmt.where(OperationApplication.company_id == context.company_id)
    if context.scope == "TEAM":
        return stmt.where(
            or_(
                OperationApplication.assigned_to_user_id.in_(context.team_user_ids),
                OperationApplication.assigned_by_user_id == user.user_id,
            )
        )
    if context.scope == "SELF":
        return stmt.where(OperationApplication.assigned_to_user_id == user.user_id)
    return stmt.where(OperationApplication.assigned_to_user_id == user.user_id)


def get_operations_dashboard_data(
    session: Session,
    user: User,
) -> OperationsDashboardResponse:
    """Generate live Operations Dashboard analytics for the current user's permitted data scope."""
    context = permissions.resolve_data_scope_context(session, user, "OPERATIONS")
    today = date.today()

    base_query = (
        select(OperationApplication)
        .options(
            joinedload(OperationApplication.client),
            joinedload(OperationApplication.service),
            joinedload(OperationApplication.sales_order).joinedload(SalesOrder.salesperson),
            joinedload(OperationApplication.assigned_to),
            selectinload(OperationApplication.documents),
        )
    )
    base_query = _apply_operations_scope(base_query, user, context)
    all_apps = session.execute(base_query).scalars().all()

    total_applications = len(all_apps)
    assigned_count = sum(1 for a in all_apps if a.application_status == "ASSIGNED")
    in_progress_count = sum(1 for a in all_apps if a.application_status == "IN_PROGRESS")
    pending_documents_count = sum(1 for a in all_apps if a.application_status == "PENDING_DOCUMENTS")
    ready_submitted_count = sum(1 for a in all_apps if a.application_status in ("READY_FOR_SUBMISSION", "SUBMITTED"))
    authority_query_count = sum(1 for a in all_apps if a.application_status == "AUTHORITY_QUERY")
    approved_count = sum(1 for a in all_apps if a.application_status == "APPROVED")
    unassigned_count = sum(1 for a in all_apps if a.application_status == "UNASSIGNED" or a.assigned_to_user_id is None)
    
    overdue_count = sum(
        1 for a in all_apps
        if a.target_due_date and a.target_due_date < today and a.application_status not in ("APPROVED", "CANCELLED")
    )
    
    active_or_completed = sum(1 for a in all_apps if a.application_status != "CANCELLED")
    sla_adherence_percent = 100.0
    if active_or_completed > 0:
        sla_adherence_percent = round(((active_or_completed - overdue_count) / active_or_completed) * 100.0, 1)

    kpis = OperationsKpiSummary(
        total_applications=total_applications,
        assigned_count=assigned_count,
        in_progress_count=in_progress_count,
        pending_documents_count=pending_documents_count,
        ready_submitted_count=ready_submitted_count,
        authority_query_count=authority_query_count,
        approved_count=approved_count,
        overdue_count=overdue_count,
        unassigned_count=unassigned_count,
        sla_adherence_percent=sla_adherence_percent,
    )

    # Status breakdown distribution
    status_counts: Dict[str, int] = {}
    for a in all_apps:
        status_counts[a.application_status] = status_counts.get(a.application_status, 0) + 1

    status_breakdown: List[OperationsStatusBreakdownItem] = []
    display_statuses = [
        "UNASSIGNED",
        "ASSIGNED",
        "IN_PROGRESS",
        "PENDING_DOCUMENTS",
        "READY_FOR_SUBMISSION",
        "SUBMITTED",
        "AUTHORITY_QUERY",
        "APPROVED",
        "CANCELLED",
    ]
    for st in display_statuses:
        cnt = status_counts.get(st, 0)
        pct = round((cnt / total_applications * 100.0), 1) if total_applications > 0 else 0.0
        status_breakdown.append(
            OperationsStatusBreakdownItem(
                status=st,
                label=STATUS_LABEL_MAP.get(st, st),
                count=cnt,
                percentage=pct,
                color=STATUS_COLOR_MAP.get(st, "#64748B"),
            )
        )

    # Executive Workload calculation
    eligible_assignees = get_eligible_operations_assignees(session, user)
    workload_by_executive: List[ExecutiveWorkloadItem] = []
    for exec_user in eligible_assignees:
        user_apps = [a for a in all_apps if a.assigned_to_user_id == exec_user.user_id]
        active = sum(1 for a in user_apps if a.application_status not in ("APPROVED", "CANCELLED", "UNASSIGNED"))
        inp = sum(1 for a in user_apps if a.application_status in ("IN_PROGRESS", "PENDING_DOCUMENTS", "READY_FOR_SUBMISSION", "SUBMITTED", "AUTHORITY_QUERY"))
        comp = sum(1 for a in user_apps if a.application_status == "APPROVED")
        over = sum(1 for a in user_apps if a.target_due_date and a.target_due_date < today and a.application_status not in ("APPROVED", "CANCELLED"))
        
        tot_tracked = active + comp
        sla_r = round(((tot_tracked - over) / tot_tracked * 100.0), 1) if tot_tracked > 0 else 100.0

        workload_by_executive.append(
            ExecutiveWorkloadItem(
                user_id=exec_user.user_id,
                employee_code=exec_user.employee_code,
                full_name=f"{exec_user.first_name} {exec_user.last_name}".strip(),
                designation_name=exec_user.designation.designation_name if exec_user.designation else None,
                active_tasks=active,
                in_progress_tasks=inp,
                completed_tasks=comp,
                overdue_tasks=over,
                sla_rating=sla_r,
            )
        )

    # Sort workload by active tasks descending
    workload_by_executive.sort(key=lambda x: x.active_tasks, reverse=True)

    # Recent applications (latest 10)
    sorted_recent = sorted(all_apps, key=lambda a: a.created_at, reverse=True)[:10]
    recent_applications = [_to_application_read(a) for a in sorted_recent]

    # Priority queue (URGENT/HIGH priority or overdue, not completed)
    priority_apps = [
        a for a in all_apps
        if a.application_status not in ("APPROVED", "CANCELLED")
        and (
            a.priority in ("HIGH", "URGENT")
            or (a.target_due_date and a.target_due_date < today)
        )
    ]
    priority_apps.sort(
        key=lambda a: (
            0 if a.priority == "URGENT" else (1 if a.priority == "HIGH" else 2),
            a.target_due_date or date.max,
        )
    )
    priority_queue = [_to_application_read(a) for a in priority_apps[:10]]

    company_name = user.company.company_name if user.company else "Company"

    return OperationsDashboardResponse(
        kpis=kpis,
        status_breakdown=status_breakdown,
        workload_by_executive=workload_by_executive,
        recent_applications=recent_applications,
        priority_queue=priority_queue,
        scope=context.scope,
        company_id=user.company_id,
        company_name=company_name,
    )


def get_operations_tasks(
    session: Session,
    user: User,
    page: int = 1,
    limit: int = 20,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    search: Optional[str] = None,
    assigned_to_user_id: Optional[uuid.UUID] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    my_tasks_only: bool = False,
    unassigned_only: bool = False,
) -> OperationsTaskListResponse:
    """Retrieve filtered, paginated operations tasks with scoping and summary metrics."""
    context = permissions.resolve_data_scope_context(session, user, "OPERATIONS")
    today = date.today()

    stmt = (
        select(OperationApplication)
        .join(OperationApplication.sales_order)
        .join(OperationApplication.client)
        .join(OperationApplication.service)
        .options(
            joinedload(OperationApplication.client),
            joinedload(OperationApplication.service),
            joinedload(OperationApplication.sales_order).joinedload(SalesOrder.salesperson),
            joinedload(OperationApplication.assigned_to),
            joinedload(OperationApplication.assigned_by),
            selectinload(OperationApplication.documents),
        )
    )

    if my_tasks_only:
        stmt = stmt.where(OperationApplication.assigned_to_user_id == user.user_id)
    elif unassigned_only:
        stmt = stmt.where(
            or_(
                OperationApplication.application_status == "UNASSIGNED",
                OperationApplication.assigned_to_user_id.is_(None),
            )
        )
        stmt = _apply_operations_scope(stmt, user, context)
    else:
        stmt = _apply_operations_scope(stmt, user, context)

    # Dynamic filters
    if status:
        stat_upper = status.strip().upper()
        if stat_upper == "OVERDUE":
            stmt = stmt.where(
                OperationApplication.target_due_date < today,
                OperationApplication.application_status.notin_(["APPROVED", "CANCELLED"]),
            )
        elif stat_upper != "ALL":
            stmt = stmt.where(OperationApplication.application_status == stat_upper)

    if priority and priority.strip().upper() != "ALL":
        stmt = stmt.where(OperationApplication.priority == priority.strip().upper())

    if assigned_to_user_id and not unassigned_only:
        stmt = stmt.where(OperationApplication.assigned_to_user_id == assigned_to_user_id)

    if start_date:
        stmt = stmt.where(func.date(OperationApplication.created_at) >= start_date)
    if end_date:
        stmt = stmt.where(func.date(OperationApplication.created_at) <= end_date)

    if search:
        s_term = f"%{search.strip().lower()}%"
        stmt = stmt.where(
            or_(
                func.lower(OperationApplication.application_number).like(s_term),
                func.lower(SalesOrder.order_number).like(s_term),
                func.lower(ClientMaster.client_name).like(s_term),
                func.lower(ClientMaster.contact_phone).like(s_term),
                func.lower(ServiceMaster.service_name).like(s_term),
                func.lower(ServiceMaster.service_code).like(s_term),
            )
        )

    # Calculate summary counts on the filtered population (or full scoped set)
    all_matched = session.execute(stmt).scalars().all()
    total_count = len(all_matched)

    assigned_cnt = sum(1 for a in all_matched if a.application_status == "ASSIGNED")
    in_prog_cnt = sum(1 for a in all_matched if a.application_status == "IN_PROGRESS")
    pending_docs_cnt = sum(1 for a in all_matched if a.application_status == "PENDING_DOCUMENTS")
    under_review_cnt = sum(1 for a in all_matched if a.application_status in ("READY_FOR_SUBMISSION", "SUBMITTED", "AUTHORITY_QUERY"))
    completed_cnt = sum(1 for a in all_matched if a.application_status == "APPROVED")
    overdue_cnt = sum(1 for a in all_matched if a.target_due_date and a.target_due_date < today and a.application_status not in ("APPROVED", "CANCELLED"))

    summary = OperationsTaskSummary(
        total_tasks=total_count,
        assigned=assigned_cnt,
        in_progress=in_prog_cnt,
        pending_docs=pending_docs_cnt,
        under_review=under_review_cnt,
        completed=completed_cnt,
        overdue=overdue_cnt,
    )

    # Sorting
    sort_column_map = {
        "created_at": OperationApplication.created_at,
        "application_number": OperationApplication.application_number,
        "target_due_date": OperationApplication.target_due_date,
        "priority": OperationApplication.priority,
        "application_status": OperationApplication.application_status,
    }
    sort_col = sort_column_map.get(sort_by, OperationApplication.created_at)
    if sort_order.lower() == "asc":
        stmt = stmt.order_by(sort_col.asc().nulls_last())
    else:
        stmt = stmt.order_by(sort_col.desc().nulls_last())

    # Pagination
    offset = max(0, (page - 1) * limit)
    paginated_stmt = stmt.offset(offset).limit(limit)
    items_raw = session.execute(paginated_stmt).scalars().all()

    items = [_to_application_read(app) for app in items_raw]
    total_pages = max(1, (total_count + limit - 1) // limit)

    return OperationsTaskListResponse(
        items=items,
        total_count=total_count,
        page=page,
        limit=limit,
        total_pages=total_pages,
        summary=summary,
    )


def get_my_tasks(
    session: Session,
    user: User,
    page: int = 1,
    limit: int = 20,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    search: Optional[str] = None,
    assigned_to_user_id: Optional[uuid.UUID] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
) -> OperationsTaskListResponse:
    """Retrieve tasks assigned to or delegated/reassigned by the currently logged in operations employee."""
    return get_operations_tasks(
        session=session,
        user=user,
        page=page,
        limit=limit,
        status=status,
        priority=priority,
        search=search,
        assigned_to_user_id=assigned_to_user_id,
        start_date=start_date,
        end_date=end_date,
        sort_by=sort_by,
        sort_order=sort_order,
        my_tasks_only=True,
    )


def get_unassigned_operations_orders(
    session: Session,
    user: User,
    page: int = 1,
    limit: int = 20,
    search: Optional[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
) -> OperationsTaskListResponse:
    """Retrieve unassigned applications awaiting assignment to an operations employee."""
    return get_operations_tasks(
        session=session,
        user=user,
        page=page,
        limit=limit,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        unassigned_only=True,
    )


def get_operation_application_detail(
    session: Session,
    application_id: uuid.UUID,
    user: User,
) -> OperationApplicationDetailRead:
    """Retrieve full application details, checklist documents, and audit logs with RBAC check."""
    context = permissions.resolve_data_scope_context(session, user, "OPERATIONS")

    stmt = (
        select(OperationApplication)
        .options(
            joinedload(OperationApplication.client),
            joinedload(OperationApplication.service),
            joinedload(OperationApplication.sales_order).joinedload(SalesOrder.salesperson),
            joinedload(OperationApplication.assigned_to),
            joinedload(OperationApplication.assigned_by),
            selectinload(OperationApplication.documents).joinedload(ApplicationDocument.verified_by),
            selectinload(OperationApplication.assignment_history).joinedload(ApplicationAssignmentHistory.assigned_by),
            selectinload(OperationApplication.assignment_history).joinedload(ApplicationAssignmentHistory.previous_assignee),
            selectinload(OperationApplication.assignment_history).joinedload(ApplicationAssignmentHistory.new_assignee),
            selectinload(OperationApplication.activity_logs).joinedload(ApplicationActivityLog.actor),
        )
        .where(OperationApplication.application_id == application_id)
    )

    app = session.execute(stmt).scalar_one_or_none()
    if not app:
        raise ApplicationNotFoundError(f"Operation application with ID '{application_id}' not found.")

    # Scoping check
    if not context.is_user_permitted(
        target_user_id=app.assigned_to_user_id or user.user_id,
        target_company_id=app.company_id,
    ):
        # Permit if user is the assigned employee, the assigner, or super admin
        is_participant = (
            app.assigned_to_user_id == user.user_id
            or app.assigned_by_user_id == user.user_id
            or getattr(user, "is_super_admin", False)
        )
        if not is_participant:
            raise permissions.PermissionDeniedError(
                f"User '{user.employee_code}' does not have permission to view application '{app.application_number}'."
            )

    return _to_application_detail_read(app)


def is_disallowed_ops_assignee(u: User) -> bool:
    """Check if user belongs to Sales, Admin, or Director roles, who are forbidden from being assigned operations tasks."""
    if not u or u.account_status != "ACTIVE":
        return True

    dept_name = (u.department.department_name.lower() if u.department and u.department.department_name else "")
    dept_code = (u.department.department_code.upper() if u.department and u.department.department_code else "")
    desig_name = (u.designation.designation_name.lower() if u.designation and u.designation.designation_name else "")
    desig_code = (u.designation.designation_code.upper() if u.designation and u.designation.designation_code else "")

    # Disallow Sales
    if "sale" in dept_name or "sale" in dept_code or dept_code in ("SL", "SALES", "SALE"):
        return True
    if "sale" in desig_name or "sale" in desig_code:
        return True

    # Disallow Admin / Administration
    if "admin" in dept_name or "admin" in dept_code or dept_code in ("AD", "ADM", "ADMIN", "ADMINISTRATION"):
        return True
    if "admin" in desig_name or "admin" in desig_code:
        return True

    # Disallow Directors / Executive / CEO
    if "director" in desig_name or "director" in desig_code or desig_code in ("DIR", "MD", "CEO"):
        return True
    if "managing director" in desig_name or "ceo" in desig_name or "chief" in desig_name:
        return True

    # Disallow Super Admin
    if getattr(u, "is_super_admin", False) or getattr(u, "role_type", "") == "SUPER_ADMIN" or getattr(u, "employee_code", "") == "CG0001":
        return True

    return False


def get_eligible_operations_assignees(
    session: Session,
    user: User,
) -> List[User]:
    """Retrieve active employees in the company who are eligible to be assigned operations tasks (strictly excluding Sales, Admin, and Directors)."""
    stmt = (
        select(User)
        .options(
            joinedload(User.department),
            joinedload(User.designation),
        )
        .where(
            User.company_id == user.company_id,
            User.account_status == "ACTIVE",
        )
    )

    users = session.execute(stmt).scalars().all()
    eligible: List[User] = []
    for u in users:
        if is_disallowed_ops_assignee(u):
            continue
        dept_name = u.department.department_name.lower() if u.department else ""
        dept_code = u.department.department_code.upper() if u.department else ""
        if "operat" in dept_name or "operat" in dept_code or dept_code in ("OP", "OPS", "OPERATIONS"):
            eligible.append(u)
        elif permissions.has_permission(session, u, "OPERATIONS", "view"):
            eligible.append(u)

    # Sort by first_name, last_name
    eligible.sort(key=lambda u: (u.first_name, u.last_name))
    return eligible


def assign_task(
    session: Session,
    application_id: uuid.UUID,
    assignee_user_id: uuid.UUID,
    assigned_by: User,
    priority: str = "MEDIUM",
    target_due_date: Optional[date] = None,
    notes: Optional[str] = None,
) -> OperationApplication:
    """Assign an unassigned or existing application to an operations employee."""
    app = session.get(OperationApplication, application_id)
    if not app:
        raise ApplicationNotFoundError(f"Operation application with ID '{application_id}' not found.")

    assignee = session.get(User, assignee_user_id)
    if not assignee or assignee.account_status != "ACTIVE":
        raise ValueError(f"Target assignee with ID '{assignee_user_id}' is not an active employee.")

    # Validate assignee belongs to the same company
    if assignee.company_id != app.company_id:
        raise ValueError("Assignee does not belong to the application's company.")

    # Validation: target assignee cannot be from Sales, Admin, or Director roles
    if is_disallowed_ops_assignee(assignee):
        raise ValueError(
            "Task cannot be assigned to Sales, Administration, or Director personnel. "
            "Please select an eligible Operations team member."
        )

    prev_assignee_id = app.assigned_to_user_id
    now_utc = datetime.now(timezone.utc)

    # Update application
    app.assigned_to_user_id = assignee_user_id
    app.assigned_by_user_id = assigned_by.user_id
    app.assigned_at = now_utc
    app.priority = priority
    if target_due_date:
        app.target_due_date = target_due_date
    if notes:
        app.assignment_notes = notes

    if app.application_status == "UNASSIGNED":
        app.application_status = "ASSIGNED"

    # Log assignment history
    history = ApplicationAssignmentHistory(
        application_id=app.application_id,
        assigned_by_user_id=assigned_by.user_id,
        previous_assignee_user_id=prev_assignee_id,
        new_assignee_user_id=assignee_user_id,
        reason=notes or "Initial task assignment",
        assigned_at=now_utc,
    )
    session.add(history)

    # Log activity
    activity = ApplicationActivityLog(
        application_id=app.application_id,
        actor_user_id=assigned_by.user_id,
        action_type="ASSIGNMENT_CHANGE",
        old_value=str(prev_assignee_id) if prev_assignee_id else "UNASSIGNED",
        new_value=f"{assignee.first_name} {assignee.last_name} ({assignee.employee_code})",
        comment=f"Assigned to {assignee.first_name} {assignee.last_name}. Priority: {priority}",
        created_at=now_utc,
    )
    session.add(activity)
    session.flush()

    return app


def reassign_task(
    session: Session,
    application_id: uuid.UUID,
    new_assignee_user_id: uuid.UUID,
    reason: str,
    reassigned_by: User,
    priority: Optional[str] = None,
    target_due_date: Optional[date] = None,
) -> OperationApplication:
    """Reassign an existing assigned application to a different operations employee."""
    app = session.get(OperationApplication, application_id)
    if not app:
        raise ApplicationNotFoundError(f"Operation application with ID '{application_id}' not found.")

    new_assignee = session.get(User, new_assignee_user_id)
    if not new_assignee or new_assignee.account_status != "ACTIVE":
        raise ValueError(f"Target assignee with ID '{new_assignee_user_id}' is not an active employee.")

    if new_assignee.company_id != app.company_id:
        raise ValueError("Assignee does not belong to the application's company.")

    # Validation: target assignee cannot be from Sales, Admin, or Director roles
    if is_disallowed_ops_assignee(new_assignee):
        raise ValueError(
            "Task cannot be assigned to Sales, Administration, or Director personnel. "
            "Please select an eligible Operations team member."
        )

    # Validation: cannot reassign to current assignee or self
    if app.assigned_to_user_id and str(app.assigned_to_user_id) == str(new_assignee_user_id):
        raise ValueError("Task is already assigned to this employee. Cannot reassign to the current assignee.")

    if reassigned_by and str(reassigned_by.user_id) == str(new_assignee_user_id):
        raise ValueError("Cannot reassign task to yourself.")

    prev_assignee_id = app.assigned_to_user_id
    now_utc = datetime.now(timezone.utc)

    app.assigned_to_user_id = new_assignee_user_id
    app.assigned_by_user_id = reassigned_by.user_id
    app.assigned_at = now_utc
    if priority:
        app.priority = priority
    if target_due_date:
        app.target_due_date = target_due_date

    # Log assignment history
    history = ApplicationAssignmentHistory(
        application_id=app.application_id,
        assigned_by_user_id=reassigned_by.user_id,
        previous_assignee_user_id=prev_assignee_id,
        new_assignee_user_id=new_assignee_user_id,
        reason=reason,
        assigned_at=now_utc,
    )
    session.add(history)

    # Log activity
    activity = ApplicationActivityLog(
        application_id=app.application_id,
        actor_user_id=reassigned_by.user_id,
        action_type="ASSIGNMENT_CHANGE",
        old_value=str(prev_assignee_id) if prev_assignee_id else "UNASSIGNED",
        new_value=f"{new_assignee.first_name} {new_assignee.last_name} ({new_assignee.employee_code})",
        comment=f"Reassigned to {new_assignee.first_name} {new_assignee.last_name}. Reason: {reason}",
        created_at=now_utc,
    )
    session.add(activity)
    session.flush()

    return app


def update_application_status(
    session: Session,
    application_id: uuid.UUID,
    new_status: str,
    actor: User,
    comment: Optional[str] = None,
) -> OperationApplication:
    """Transition application status validating state machine rules."""
    app = session.get(OperationApplication, application_id)
    if not app:
        raise ApplicationNotFoundError(f"Operation application with ID '{application_id}' not found.")

    old_status = app.application_status
    if old_status == new_status:
        return app

    # Validate transition
    allowed = VALID_STATUS_TRANSITIONS.get(old_status, [])
    if new_status not in allowed:
        raise InvalidStatusTransitionError(
            f"Cannot transition application from '{old_status}' to '{new_status}'. Allowed transitions: {allowed}"
        )

    now_utc = datetime.now(timezone.utc)
    app.application_status = new_status
    if new_status == "APPROVED":
        app.completion_date = date.today()

    activity = ApplicationActivityLog(
        application_id=app.application_id,
        actor_user_id=actor.user_id,
        action_type="STATUS_CHANGE",
        old_value=old_status,
        new_value=new_status,
        comment=comment or f"Status changed from {old_status} to {new_status}",
        created_at=now_utc,
    )
    session.add(activity)
    session.flush()

    return app


def update_document_status(
    session: Session,
    app_doc_id: uuid.UUID,
    new_status: str,
    actor: User,
    rejection_reason: Optional[str] = None,
) -> ApplicationDocument:
    """Update document checklist item verification status."""
    doc = session.get(ApplicationDocument, app_doc_id)
    if not doc:
        raise ValueError(f"Application document with ID '{app_doc_id}' not found.")

    old_status = doc.status
    doc.status = new_status
    if new_status == "VERIFIED":
        doc.verified_by_user_id = actor.user_id
        doc.verified_at = datetime.now(timezone.utc)
        doc.rejection_reason = None
    elif new_status == "REJECTED":
        doc.rejection_reason = rejection_reason
        doc.verified_by_user_id = actor.user_id
        doc.verified_at = datetime.now(timezone.utc)
    else:
        doc.verified_by_user_id = None
        doc.verified_at = None

    activity = ApplicationActivityLog(
        application_id=doc.application_id,
        actor_user_id=actor.user_id,
        action_type="DOCUMENT_STATUS_CHANGE",
        old_value=f"{doc.document_code}: {old_status}",
        new_value=f"{doc.document_code}: {new_status}",
        comment=rejection_reason if new_status == "REJECTED" else f"Document '{doc.document_name}' marked as {new_status}",
        created_at=datetime.now(timezone.utc),
    )
    session.add(activity)
    session.flush()

    return doc
