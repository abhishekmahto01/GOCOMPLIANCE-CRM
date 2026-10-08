"""Shared Task Conversation service managing unified timeline across Sales, Operations, and Accounts."""
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import func, or_, select, text
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.accounts_follow_up import AccountsFollowUp
from app.models.department import Department
from app.models.designation import Designation
from app.models.operation_application import (
    ApplicationActivityLog,
    ApplicationAssignmentHistory,
    OperationApplication,
    OperationRemark,
)
from app.models.sales_order import SalesOrder
from app.models.task_conversation import TaskConversationMessage
from app.models.user import User
from app.schemas.conversation import (
    ConversationMessageRead,
    ConversationThreadResponse,
    LatestRemarkSummary,
    format_ist_datetime,
)
from app.services import permissions


class ConversationNotFoundError(Exception):
    """Raised when the specified sales order / conversation thread is not found."""
    pass


def check_conversation_access(
    session: Session,
    user: User,
    order: SalesOrder,
) -> Tuple[bool, bool, str]:
    """Check read and post access to a shared task conversation.

    Returns:
        Tuple of (can_read: bool, can_post: bool, reason: str)
    """
    # 1. Super Admin has unrestricted read/post access
    if (
        getattr(user, "is_super_admin", False)
        or getattr(user, "role_type", "") == "SUPER_ADMIN"
        or getattr(user, "employee_code", "") == "CG0001"
        or permissions.is_super_admin_user(session, user)
    ):
        return True, True, "Super Admin access"

    # 2. Strict Company Boundary for non-super-admins
    if user.company_id != order.company_id:
        return False, False, "Access denied: Record belongs to a different company."

    can_read = False
    can_post = False
    reasons = []

    # 3. Director / Company Admin Check
    desig_name = (user.designation.designation_name.lower() if user.designation and user.designation.designation_name else "")
    desig_code = (user.designation.designation_code.upper() if user.designation and user.designation.designation_code else "")
    dept_name = (user.department.department_name.lower() if user.department and user.department.department_name else "")
    dept_code = (user.department.department_code.upper() if user.department and user.department.department_code else "")

    is_admin_or_director = (
        "director" in desig_name
        or "director" in desig_code
        or desig_code in ("DIR", "MD", "CEO")
        or "admin" in dept_name
        or "admin" in dept_code
        or getattr(user, "role_type", "") in ("ADMIN", "DIRECTOR")
    )

    if is_admin_or_director:
        return True, True, "Company Director / Admin access"

    # 4. Sales Module Access
    is_sales_owner = (order.salesperson_user_id == user.user_id)
    has_sales_perm = (
        permissions.has_permission(session, user, "SALES_MY_ORDERS", "view")
        or permissions.has_permission(session, user, "SALES_ALL_ORDERS", "view")
        or permissions.has_permission(session, user, "SALES_REGISTER", "view")
        or permissions.has_permission(session, user, "SALES_CONFIRMED_ORDER", "view")
        or permissions.has_permission(session, user, "SALES", "view")
        or ("sale" in dept_name or "sale" in dept_code)
    )
    if is_sales_owner:
        can_read = True
        can_post = True
        reasons.append("Sales order salesperson")
    elif has_sales_perm:
        try:
            scope_ctx = permissions.resolve_data_scope_context(session, user, "SALES_MY_ORDERS")
        except permissions.PermissionDeniedError:
            try:
                scope_ctx = permissions.resolve_data_scope_context(session, user, "SALES_ALL_ORDERS")
            except permissions.PermissionDeniedError:
                try:
                    scope_ctx = permissions.resolve_data_scope_context(session, user, "SALES_CONFIRMED_ORDER")
                except permissions.PermissionDeniedError:
                    scope_ctx = None

        if scope_ctx and scope_ctx.is_user_permitted(order.salesperson_user_id, order.company_id):
            can_read = True
            can_post = True
            reasons.append("Sales authorized scope")
        elif "sale" in dept_name or "sale" in dept_code:
            can_read = True
            can_post = True
            reasons.append("Sales department employee")

    # 5. Operations Module Access
    app = order.application
    if not app:
        app = session.execute(
            select(OperationApplication).where(OperationApplication.sales_order_id == order.order_id)
        ).scalar_one_or_none()

    has_ops_perm = (
        permissions.has_permission(session, user, "OPERATIONS", "view")
        or permissions.has_permission(session, user, "OPERATION_MY_TASKS", "view")
        or permissions.has_permission(session, user, "OPERATION_ALL_TASKS", "view")
        or permissions.has_permission(session, user, "OPERATION_TASK_ASSIGNMENT", "view")
        or permissions.has_permission(session, user, "OPERATION_DASHBOARD", "view")
        or ("operat" in dept_name or "operat" in dept_code or dept_code in ("OP", "OPS", "OPERATIONS"))
    )

    if has_ops_perm and app:
        # Check if user is current assignee
        is_current_assignee = app.assigned_to_user_id is not None and app.assigned_to_user_id == user.user_id
        if is_current_assignee:
            can_read = True
            can_post = True
            reasons.append("Current Operations assignee")
        else:
            try:
                ops_ctx = permissions.resolve_data_scope_context(session, user, "OPERATIONS")
            except permissions.PermissionDeniedError:
                try:
                    ops_ctx = permissions.resolve_data_scope_context(session, user, "OPERATION_ALL_TASKS")
                except permissions.PermissionDeniedError:
                    ops_ctx = None

            if ops_ctx:
                if ops_ctx.scope in ("ALL", "COMPANY", "DEPARTMENT"):
                    can_read = True
                    can_post = True
                    reasons.append("Operations Manager / Team Lead scope")
                elif ops_ctx.scope == "TEAM" and app.assigned_to_user_id in ops_ctx.team_user_ids:
                    can_read = True
                    can_post = True
                    reasons.append("Operations Supervisor team scope")

    # 6. Accounts Module Access
    has_accounts_perm = (
        permissions.has_permission(session, user, "ACCOUNTS_ENTRIES", "view")
        or permissions.has_permission(session, user, "ACCOUNTS_DASHBOARD", "view")
        or permissions.has_permission(session, user, "ACCOUNTS", "view")
        or permissions.has_permission(session, user, "ACCOUNTS_ENTRIES", "read")
        or permissions.has_permission(session, user, "ACCOUNTS", "read")
    )

    if has_accounts_perm:
        # Accounts users may ONLY access when GST Invoice Required is True
        if getattr(order, "gst_invoice_required", False):
            try:
                acc_ctx = permissions.resolve_data_scope_context(session, user, "ACCOUNTS_ENTRIES")
            except permissions.PermissionDeniedError:
                try:
                    acc_ctx = permissions.resolve_data_scope_context(session, user, "ACCOUNTS")
                except permissions.PermissionDeniedError:
                    acc_ctx = None

            if acc_ctx and acc_ctx.is_user_permitted(order.salesperson_user_id, order.company_id):
                can_read = True
                can_post = True
                reasons.append("Accounts GST-eligible entry scope")

    if can_read or can_post:
        return can_read, can_post, "; ".join(reasons)

    return False, False, "Access denied: You do not have permission to access this task conversation."


def _to_message_read(msg: TaskConversationMessage, current_user_id: Optional[uuid.UUID] = None) -> ConversationMessageRead:
    """Transform TaskConversationMessage model into ConversationMessageRead schema."""
    parsed_metadata = None
    if msg.event_metadata:
        try:
            parsed_metadata = json.loads(msg.event_metadata)
        except Exception:
            parsed_metadata = {"raw": msg.event_metadata}

    return ConversationMessageRead(
        message_id=msg.message_id,
        sales_order_id=msg.sales_order_id,
        author_user_id=msg.author_user_id,
        message_type=msg.message_type,
        message_text=msg.message_text,
        author_name=msg.author_name or "System",
        author_employee_code=msg.author_employee_code,
        author_department_name=msg.author_department_name,
        author_role_name=msg.author_role_name,
        event_type=msg.event_type,
        event_metadata=parsed_metadata,
        created_at=msg.created_at,
        formatted_created_at=format_ist_datetime(msg.created_at),
        is_mine=bool(current_user_id and msg.author_user_id == current_user_id),
    )


def get_task_conversation(
    session: Session,
    user: User,
    order_id: uuid.UUID,
    limit: int = 50,
    before_id: Optional[uuid.UUID] = None,
    offset: int = 0,
) -> ConversationThreadResponse:
    """Retrieve full chronological conversation thread for a task with RBAC scoping."""
    order = (
        session.query(SalesOrder)
        .options(
            joinedload(SalesOrder.client),
            joinedload(SalesOrder.service),
            joinedload(SalesOrder.salesperson),
            joinedload(SalesOrder.application).joinedload(OperationApplication.assigned_to),
        )
        .filter(SalesOrder.order_id == order_id)
        .first()
    )

    if not order or order.confirmation_status == "CANCELLED":
        raise ConversationNotFoundError(f"Sales order with ID '{order_id}' not found.")

    can_read, can_post, reason = check_conversation_access(session, user, order)
    if not can_read:
        raise permissions.PermissionDeniedError(reason)

    # Base query for messages
    query = (
        select(TaskConversationMessage)
        .where(TaskConversationMessage.sales_order_id == order_id)
    )

    total_count = session.execute(
        select(func.count(TaskConversationMessage.message_id)).where(
            TaskConversationMessage.sales_order_id == order_id
        )
    ).scalar_one()

    # If before_id cursor is provided for loading older messages
    if before_id:
        target_msg = session.get(TaskConversationMessage, before_id)
        if target_msg:
            query = query.where(
                or_(
                    TaskConversationMessage.created_at < target_msg.created_at,
                    (TaskConversationMessage.created_at == target_msg.created_at) & (TaskConversationMessage.message_id < target_msg.message_id),
                )
            )

    # Order newest or chronological
    query = query.order_by(
        TaskConversationMessage.created_at.asc(),
        TaskConversationMessage.message_id.asc(),
    )

    if limit and limit > 0:
        query = query.limit(limit)
    if offset and offset > 0:
        query = query.offset(offset)

    messages = session.execute(query).scalars().all()

    # Determine if more older messages exist
    has_more_older = False
    if messages and total_count > len(messages):
        has_more_older = True

    # Resolve application details
    app = order.application
    assignee_name = None
    assignee_code = None
    assignee_id = None
    app_id = None
    app_num = None
    work_status = "UNASSIGNED"

    if app:
        app_id = app.application_id
        app_num = app.application_number
        work_status = app.application_status
        if app.assigned_to:
            assignee_id = app.assigned_to.user_id
            assignee_name = f"{app.assigned_to.first_name} {app.assigned_to.last_name}"
            assignee_code = app.assigned_to.employee_code
    elif order.confirmation_status == "DRAFT":
        work_status = "DRAFT"

    salesperson_name = f"{order.salesperson.first_name} {order.salesperson.last_name}" if order.salesperson else "Sales"
    salesperson_code = order.salesperson.employee_code if order.salesperson else None

    return ConversationThreadResponse(
        order_id=order.order_id,
        order_number=order.order_number,
        client_name=order.client.client_name if order.client else "Client",
        service_name=order.service.service_name if order.service else "Service",
        location=order.location,
        salesperson_name=salesperson_name,
        salesperson_code=salesperson_code,
        current_assignee_id=assignee_id,
        current_assignee_name=assignee_name,
        current_assignee_code=assignee_code,
        application_id=app_id,
        application_number=app_num,
        work_status=work_status,
        payment_status=order.payment_status,
        gst_invoice_required=getattr(order, "gst_invoice_required", False),
        can_post=can_post,
        items=[_to_message_read(m, user.user_id) for m in messages],
        total_count=total_count,
        has_more_older=has_more_older,
    )


def post_conversation_message(
    session: Session,
    user: User,
    order_id: uuid.UUID,
    message_text: str,
    idempotency_key: Optional[str] = None,
) -> ConversationMessageRead:
    """Post an append-only human remark to the shared task conversation."""
    clean_text = (message_text or "").strip()
    if not clean_text:
        raise ValueError("Message text cannot be empty or whitespace only.")

    order = session.get(SalesOrder, order_id)
    if not order or order.confirmation_status == "CANCELLED":
        raise ConversationNotFoundError(f"Sales order with ID '{order_id}' not found.")

    can_read, can_post, reason = check_conversation_access(session, user, order)
    if not can_post:
        raise permissions.PermissionDeniedError(reason)

    # Idempotency check: prevent duplicate insertion on network retry or double-click
    if idempotency_key and idempotency_key.strip():
        existing_msg = session.execute(
            select(TaskConversationMessage).where(
                TaskConversationMessage.sales_order_id == order_id,
                TaskConversationMessage.idempotency_key == idempotency_key.strip(),
            )
        ).scalar_one_or_none()
        if existing_msg:
            return _to_message_read(existing_msg, user.user_id)

    now_utc = datetime.now(timezone.utc)
    author_name = f"{user.first_name} {user.last_name}".strip() or "Employee"
    author_code = user.employee_code
    dept_name = user.department.department_name if user.department else None
    role_name = user.designation.designation_name if user.designation else None

    msg = TaskConversationMessage(
        sales_order_id=order_id,
        author_user_id=user.user_id,
        message_type="COMMENT",
        message_text=clean_text,
        author_name=author_name,
        author_employee_code=author_code,
        author_department_name=dept_name,
        author_role_name=role_name,
        idempotency_key=idempotency_key.strip() if idempotency_key else None,
        created_at=now_utc,
    )
    session.add(msg)

    # Keep sales_order.notes synchronized with latest human remark
    order.notes = clean_text
    order.updated_at = now_utc

    # If linked to an active operation application, also record backward-compatible OperationRemark
    app = session.execute(
        select(OperationApplication).where(OperationApplication.sales_order_id == order_id)
    ).scalar_one_or_none()

    if app:
        op_remark = OperationRemark(
            application_id=app.application_id,
            author_user_id=user.user_id,
            remark_text=clean_text,
            created_at=now_utc,
        )
        session.add(op_remark)

        activity = ApplicationActivityLog(
            application_id=app.application_id,
            actor_user_id=user.user_id,
            action_type="REMARK_ADDED",
            old_value=None,
            new_value=None,
            comment=f"Remark added by {author_name} ({dept_name or 'Staff'}): {clean_text[:120]}",
            created_at=now_utc,
        )
        session.add(activity)

    session.flush()
    return _to_message_read(msg, user.user_id)


def record_system_event(
    session: Session,
    order_id: uuid.UUID,
    event_type: str,
    message_text: str,
    actor: Optional[User] = None,
    event_metadata: Optional[Dict[str, Any]] = None,
    created_at: Optional[datetime] = None,
) -> TaskConversationMessage:
    """Record an immutable system lifecycle event in the shared conversation thread."""
    now_utc = created_at or datetime.now(timezone.utc)
    actor_name = f"{actor.first_name} {actor.last_name}".strip() if actor else "System"
    actor_code = actor.employee_code if actor else None
    dept_name = actor.department.department_name if actor and actor.department else None
    role_name = actor.designation.designation_name if actor and actor.designation else None

    meta_str = json.dumps(event_metadata, default=str) if event_metadata else None

    msg = TaskConversationMessage(
        sales_order_id=order_id,
        author_user_id=actor.user_id if actor else None,
        message_type="SYSTEM_EVENT",
        message_text=message_text,
        author_name=actor_name,
        author_employee_code=actor_code,
        author_department_name=dept_name,
        author_role_name=role_name,
        event_type=event_type,
        event_metadata=meta_str,
        created_at=now_utc,
    )
    session.add(msg)
    session.flush()
    return msg


def get_latest_human_remark(
    session: Session,
    order_id: uuid.UUID,
) -> Optional[LatestRemarkSummary]:
    """Retrieve summary of the latest human remark on a sales order / task."""
    msg = (
        session.query(TaskConversationMessage)
        .filter(
            TaskConversationMessage.sales_order_id == order_id,
            TaskConversationMessage.message_type == "COMMENT",
        )
        .order_by(
            TaskConversationMessage.created_at.desc(),
            TaskConversationMessage.message_id.desc(),
        )
        .first()
    )

    if msg:
        return LatestRemarkSummary(
            message_id=msg.message_id,
            remark_text=msg.message_text,
            author_name=msg.author_name or "Staff",
            author_employee_code=msg.author_employee_code,
            author_department=msg.author_department_name,
            created_at=msg.created_at,
            formatted_created_at=format_ist_datetime(msg.created_at),
        )

    # Fallback to SalesOrder.notes if present
    order = session.get(SalesOrder, order_id)
    if order and order.notes and order.notes.strip():
        author_name = f"{order.salesperson.first_name} {order.salesperson.last_name}" if order.salesperson else "Legacy remark"
        author_code = order.salesperson.employee_code if order.salesperson else None
        return LatestRemarkSummary(
            message_id=None,
            remark_text=order.notes.strip(),
            author_name=author_name,
            author_employee_code=author_code,
            author_department="Sales" if order.salesperson else None,
            created_at=order.created_at,
            formatted_created_at=format_ist_datetime(order.created_at),
        )

    return None


def backfill_legacy_remarks(session: Session) -> Dict[str, int]:
    """Repeat-safe migration & backfill of legacy remarks into task_conversation_message."""
    stats = {
        "sales_notes_imported": 0,
        "operation_remarks_imported": 0,
        "follow_ups_imported": 0,
    }

    # 1. Backfill initial notes on SalesOrder
    orders = (
        session.query(SalesOrder)
        .options(
            joinedload(SalesOrder.salesperson).joinedload(User.department),
            joinedload(SalesOrder.salesperson).joinedload(User.designation),
        )
        .filter(SalesOrder.notes.isnot(None))
        .all()
    )

    for o in orders:
        if not o.notes or not o.notes.strip():
            continue
        text_val = o.notes.strip()

        # Check if already imported
        existing = session.execute(
            select(TaskConversationMessage).where(
                TaskConversationMessage.sales_order_id == o.order_id,
                TaskConversationMessage.message_type == "COMMENT",
                TaskConversationMessage.message_text == text_val,
            )
        ).scalar_one_or_none()

        if not existing:
            sp = o.salesperson
            author_name = f"{sp.first_name} {sp.last_name}" if sp else "Legacy remark"
            author_code = sp.employee_code if sp else None
            dept_name = sp.department.department_name if sp and sp.department else None
            role_name = sp.designation.designation_name if sp and sp.designation else None

            msg = TaskConversationMessage(
                sales_order_id=o.order_id,
                author_user_id=sp.user_id if sp else None,
                message_type="COMMENT",
                message_text=text_val,
                author_name=author_name,
                author_employee_code=author_code,
                author_department_name=dept_name,
                author_role_name=role_name,
                created_at=o.created_at or datetime.now(timezone.utc),
            )
            session.add(msg)
            stats["sales_notes_imported"] += 1

    # 2. Backfill OperationRemark records
    op_remarks = (
        session.query(OperationRemark)
        .options(
            joinedload(OperationRemark.application),
            joinedload(OperationRemark.author).joinedload(User.department),
            joinedload(OperationRemark.author).joinedload(User.designation),
        )
        .all()
    )

    for op_rem in op_remarks:
        if not op_rem.application or not op_rem.application.sales_order_id:
            continue
        text_val = op_rem.remark_text.strip()
        so_id = op_rem.application.sales_order_id

        # Check if already imported
        existing = session.execute(
            select(TaskConversationMessage).where(
                TaskConversationMessage.sales_order_id == so_id,
                TaskConversationMessage.message_type == "COMMENT",
                TaskConversationMessage.message_text == text_val,
                TaskConversationMessage.created_at == op_rem.created_at,
            )
        ).scalar_one_or_none()

        if not existing:
            author = op_rem.author
            author_name = f"{author.first_name} {author.last_name}" if author else "Legacy remark"
            author_code = author.employee_code if author else None
            dept_name = author.department.department_name if author and author.department else "Operations"
            role_name = author.designation.designation_name if author and author.designation else None

            msg = TaskConversationMessage(
                sales_order_id=so_id,
                author_user_id=author.user_id if author else None,
                message_type="COMMENT",
                message_text=text_val,
                author_name=author_name,
                author_employee_code=author_code,
                author_department_name=dept_name,
                author_role_name=role_name,
                created_at=op_rem.created_at or datetime.now(timezone.utc),
            )
            session.add(msg)
            stats["operation_remarks_imported"] += 1

    session.flush()
    stats["total_imported"] = (
        stats["sales_notes_imported"]
        + stats["operation_remarks_imported"]
        + stats["follow_ups_imported"]
    )
    return stats
