"""Shared Task Conversation service managing unified timeline across Sales, Operations, and Accounts."""
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

from sqlalchemy import and_, case, exists, func, not_, or_, select, text
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
from app.models.task_conversation_read import TaskConversationReadState
from app.models.user import User
from app.schemas.conversation import (
    ConversationMessageRead,
    ConversationThreadResponse,
    LatestRemarkSummary,
    RemarkNotificationItem,
    RemarkNotificationListResponse,
    UnreadOrderSummaryItem,
    UnreadSummaryResponse,
    format_ist_datetime,
)
from app.services import permissions

# Cutoff date for tracking unread remark notifications (prevents historical backlogs)
FEATURE_CUTOFF_DATE = datetime(2026, 10, 1, 0, 0, 0, tzinfo=timezone.utc)


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


def get_user_authorized_orders_subquery(session: Session, user: User):
    """Generate an authorized SalesOrder query matching the authenticated user's current RBAC scopes."""
    is_super = (
        getattr(user, "is_super_admin", False)
        or getattr(user, "role_type", "") == "SUPER_ADMIN"
        or getattr(user, "employee_code", "") == "CG0001"
        or permissions.is_super_admin_user(session, user)
    )
    if is_super:
        return select(SalesOrder.order_id).where(SalesOrder.confirmation_status != "CANCELLED")

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
        return select(SalesOrder.order_id).where(
            SalesOrder.company_id == user.company_id,
            SalesOrder.confirmation_status != "CANCELLED",
        )

    module_conditions = []

    # Sales Conditions
    has_sales_perm = (
        permissions.has_permission(session, user, "SALES_MY_ORDERS", "view")
        or permissions.has_permission(session, user, "SALES_ALL_ORDERS", "view")
        or permissions.has_permission(session, user, "SALES_REGISTER", "view")
        or permissions.has_permission(session, user, "SALES_CONFIRMED_ORDER", "view")
        or permissions.has_permission(session, user, "SALES", "view")
        or ("sale" in dept_name or "sale" in dept_code)
    )
    if has_sales_perm:
        sales_conds = [SalesOrder.salesperson_user_id == user.user_id]
        scope_ctx = None
        for mod_code in ("SALES_CONFIRMED_ORDER", "SALES_ALL_ORDERS", "SALES_REGISTER", "SALES_MY_ORDERS"):
            try:
                sc = permissions.resolve_data_scope_context(session, user, mod_code)
                if sc and sc.scope in ("ALL", "COMPANY"):
                    scope_ctx = sc
                    break
                elif sc and scope_ctx is None:
                    scope_ctx = sc
            except permissions.PermissionDeniedError:
                continue

        if scope_ctx:
            if scope_ctx.scope in ("ALL", "COMPANY"):
                sales_conds.append(SalesOrder.company_id == user.company_id)
            elif scope_ctx.scope == "DEPARTMENT" and user.department_id:
                # Salespersons in same department
                dept_sp_subquery = select(User.user_id).where(User.department_id == user.department_id)
                sales_conds.append(SalesOrder.salesperson_user_id.in_(dept_sp_subquery))
            elif scope_ctx.scope == "TEAM" and scope_ctx.team_user_ids:
                sales_conds.append(SalesOrder.salesperson_user_id.in_(scope_ctx.team_user_ids))
        module_conditions.append(or_(*sales_conds))

    # Operations Conditions
    has_ops_perm = (
        permissions.has_permission(session, user, "OPERATIONS", "view")
        or permissions.has_permission(session, user, "OPERATION_MY_TASKS", "view")
        or permissions.has_permission(session, user, "OPERATION_ALL_TASKS", "view")
        or permissions.has_permission(session, user, "OPERATION_TASK_ASSIGNMENT", "view")
        or permissions.has_permission(session, user, "OPERATION_DASHBOARD", "view")
        or ("operat" in dept_name or "operat" in dept_code or dept_code in ("OP", "OPS", "OPERATIONS"))
    )
    if has_ops_perm:
        ops_conds = []
        # Direct assignment
        ops_conds.append(
            SalesOrder.order_id.in_(
                select(OperationApplication.sales_order_id).where(
                    OperationApplication.assigned_to_user_id == user.user_id
                )
            )
        )
        ops_ctx = None
        for op_mod in ("OPERATIONS", "OPERATION_ALL_TASKS", "OPERATION_TASK_ASSIGNMENT", "OPERATION_DASHBOARD"):
            try:
                sc = permissions.resolve_data_scope_context(session, user, op_mod)
                if sc and sc.scope in ("ALL", "COMPANY", "DEPARTMENT"):
                    ops_ctx = sc
                    break
                elif sc and ops_ctx is None:
                    ops_ctx = sc
            except permissions.PermissionDeniedError:
                continue

        if ops_ctx:
            if ops_ctx.scope in ("ALL", "COMPANY", "DEPARTMENT"):
                ops_conds.append(SalesOrder.company_id == user.company_id)
            elif ops_ctx.scope == "TEAM" and ops_ctx.team_user_ids:
                ops_conds.append(
                    SalesOrder.order_id.in_(
                        select(OperationApplication.sales_order_id).where(
                            OperationApplication.assigned_to_user_id.in_(ops_ctx.team_user_ids)
                        )
                    )
                )
        module_conditions.append(or_(*ops_conds))

    # Accounts Conditions
    has_acc_perm = (
        permissions.has_permission(session, user, "ACCOUNTS_ENTRIES", "view")
        or permissions.has_permission(session, user, "ACCOUNTS_DASHBOARD", "view")
        or permissions.has_permission(session, user, "ACCOUNTS", "view")
        or permissions.has_permission(session, user, "ACCOUNTS_ENTRIES", "read")
        or permissions.has_permission(session, user, "ACCOUNTS", "read")
    )
    if has_acc_perm:
        acc_conds = [SalesOrder.gst_invoice_required.is_(True)]
        acc_ctx = None
        for acc_mod in ("ACCOUNTS_ENTRIES", "ACCOUNTS_DASHBOARD", "ACCOUNTS"):
            try:
                sc = permissions.resolve_data_scope_context(session, user, acc_mod)
                if sc and sc.scope in ("ALL", "COMPANY"):
                    acc_ctx = sc
                    break
                elif sc and acc_ctx is None:
                    acc_ctx = sc
            except permissions.PermissionDeniedError:
                continue

        if acc_ctx:
            if acc_ctx.scope in ("ALL", "COMPANY"):
                acc_conds.append(SalesOrder.company_id == user.company_id)
            elif acc_ctx.scope == "DEPARTMENT" and user.department_id:
                dept_sp_subquery = select(User.user_id).where(User.department_id == user.department_id)
                acc_conds.append(SalesOrder.salesperson_user_id.in_(dept_sp_subquery))
            elif acc_ctx.scope == "TEAM" and acc_ctx.team_user_ids:
                acc_conds.append(SalesOrder.salesperson_user_id.in_(acc_ctx.team_user_ids))
        module_conditions.append(and_(*acc_conds))

    if not module_conditions:
        # User has no accessible modules
        return select(SalesOrder.order_id).where(text("1 = 0"))

    return select(SalesOrder.order_id).where(
        SalesOrder.company_id == user.company_id,
        SalesOrder.confirmation_status != "CANCELLED",
        or_(*module_conditions),
    )


def resolve_target_route_for_user(
    session: Session,
    user: User,
    order: SalesOrder,
    originating_module: Optional[str] = None,
) -> str:
    """Determine the optimal accessible route for deep-linking into the remark panel."""
    # Check if user has Operations access and order has application
    has_ops = (
        permissions.has_permission(session, user, "OPERATION_MY_TASKS", "view")
        or permissions.has_permission(session, user, "OPERATIONS", "view")
        or permissions.has_permission(session, user, "OPERATION_TASK_ASSIGNMENT", "view")
    )
    app = getattr(order, "application", None)
    is_ops_assignee = app and app.assigned_to_user_id == user.user_id

    if is_ops_assignee:
        return f"/operations/my-tasks?open_conversation_order_id={order.order_id}"

    # If originating module was Operations and user has ops assignment access
    if originating_module == "OPERATIONS" and has_ops:
        return f"/operations/task-assignment?open_conversation_order_id={order.order_id}"

    # If originating module was Accounts or user is in Accounts and order has GST
    has_acc = (
        permissions.has_permission(session, user, "ACCOUNTS_ENTRIES", "view")
        or permissions.has_permission(session, user, "ACCOUNTS", "view")
    )
    if (originating_module == "ACCOUNTS" or has_acc) and getattr(order, "gst_invoice_required", False) and has_acc:
        return f"/accounts/entries?open_conversation_order_id={order.order_id}"

    # Default to Sales Register for Sales / Admin / General access
    has_sales = (
        permissions.has_permission(session, user, "SALES_REGISTER", "view")
        or permissions.has_permission(session, user, "SALES_MY_ORDERS", "view")
        or permissions.has_permission(session, user, "SALES", "view")
    )
    if has_sales or getattr(user, "is_super_admin", False):
        return f"/sales/register?open_conversation_order_id={order.order_id}"

    if has_ops:
        return f"/operations/my-tasks?open_conversation_order_id={order.order_id}"

    if has_acc and getattr(order, "gst_invoice_required", False):
        return f"/accounts/entries?open_conversation_order_id={order.order_id}"

    return f"/sales/register?open_conversation_order_id={order.order_id}"


def _to_message_read(
    msg: TaskConversationMessage,
    current_user_id: Optional[uuid.UUID] = None,
    is_read: bool = True,
) -> ConversationMessageRead:
    """Transform TaskConversationMessage model into ConversationMessageRead schema."""
    parsed_metadata = None
    if msg.event_metadata:
        try:
            parsed_metadata = json.loads(msg.event_metadata)
        except Exception:
            parsed_metadata = {"raw": msg.event_metadata}

    is_mine = bool(current_user_id and msg.author_user_id and str(msg.author_user_id) == str(current_user_id))

    return ConversationMessageRead(
        message_id=msg.message_id,
        sales_order_id=msg.sales_order_id,
        author_user_id=msg.author_user_id,
        message_type=msg.message_type,
        message_text=msg.message_text,
        originating_module=getattr(msg, "originating_module", None),
        author_name=msg.author_name or "System",
        author_employee_code=msg.author_employee_code,
        author_department_name=msg.author_department_name,
        author_role_name=msg.author_role_name,
        event_type=msg.event_type,
        event_metadata=parsed_metadata,
        created_at=msg.created_at,
        formatted_created_at=format_ist_datetime(msg.created_at),
        is_mine=is_mine,
        is_read=is_read or is_mine,
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
            joinedload(SalesOrder.company),
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

    # Determine read state for displayed messages for the current user
    msg_ids = [m.message_id for m in messages]
    read_msg_ids: Set[uuid.UUID] = set()
    if msg_ids:
        read_stmt = select(TaskConversationReadState.message_id).where(
            TaskConversationReadState.user_id == user.user_id,
            TaskConversationReadState.message_id.in_(msg_ids),
        )
        read_msg_ids = set(session.execute(read_stmt).scalars().all())

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
    comp_name = order.company.company_name if order.company else "Company"
    comp_code = order.company.company_code if order.company else None

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
        company_id=order.company_id,
        company_name=comp_name,
        company_code=comp_code,
        can_post=can_post,
        items=[
            _to_message_read(
                m,
                user.user_id,
                is_read=(
                    m.message_id in read_msg_ids
                    or (m.author_user_id and m.author_user_id == user.user_id)
                    or m.created_at < FEATURE_CUTOFF_DATE
                ),
            )
            for m in messages
        ],
        total_count=total_count,
        has_more_older=has_more_older,
    )


def post_conversation_message(
    session: Session,
    user: User,
    order_id: uuid.UUID,
    message_text: str,
    originating_module: Optional[str] = None,
    idempotency_key: Optional[str] = None,
) -> ConversationMessageRead:
    """Post an append-only human remark to the shared task conversation and mark as read for author."""
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
            # Ensure author read state exists
            existing_read = session.execute(
                select(TaskConversationReadState).where(
                    TaskConversationReadState.user_id == user.user_id,
                    TaskConversationReadState.message_id == existing_msg.message_id,
                )
            ).scalar_one_or_none()
            if not existing_read:
                read_receipt = TaskConversationReadState(
                    read_id=uuid.uuid4(),
                    message_id=existing_msg.message_id,
                    user_id=user.user_id,
                    sales_order_id=order_id,
                    read_at=datetime.now(timezone.utc),
                )
                session.add(read_receipt)
                session.flush()
            return _to_message_read(existing_msg, user.user_id, is_read=True)

    now_utc = datetime.now(timezone.utc)
    author_name = f"{user.first_name} {user.last_name}".strip() or "Employee"
    author_code = user.employee_code
    dept_name = user.department.department_name if user.department else None
    role_name = user.designation.designation_name if user.designation else None

    # Determine originating module if not explicitly supplied
    resolved_module = originating_module
    if not resolved_module:
        d_lower = (dept_name or "").lower()
        if "sale" in d_lower:
            resolved_module = "SALES"
        elif "operat" in d_lower:
            resolved_module = "OPERATIONS"
        elif "account" in d_lower:
            resolved_module = "ACCOUNTS"
        elif "admin" in d_lower:
            resolved_module = "ADMIN"
        else:
            resolved_module = "SALES"

    msg = TaskConversationMessage(
        message_id=uuid.uuid4(),
        sales_order_id=order_id,
        author_user_id=user.user_id,
        message_type="COMMENT",
        message_text=clean_text,
        originating_module=resolved_module,
        author_name=author_name,
        author_employee_code=author_code,
        author_department_name=dept_name,
        author_role_name=role_name,
        idempotency_key=idempotency_key.strip() if idempotency_key else None,
        created_at=now_utc,
    )
    session.add(msg)

    # Automatically and atomically create read state for the author
    author_read_receipt = TaskConversationReadState(
        read_id=uuid.uuid4(),
        message_id=msg.message_id,
        user_id=user.user_id,
        sales_order_id=order_id,
        read_at=now_utc,
    )
    session.add(author_read_receipt)

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
    return _to_message_read(msg, user.user_id, is_read=True)


def record_system_event(
    session: Session,
    order_id: uuid.UUID,
    event_type: str,
    message_text: str,
    actor: Optional[User] = None,
    originating_module: Optional[str] = None,
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
        message_id=uuid.uuid4(),
        sales_order_id=order_id,
        author_user_id=actor.user_id if actor else None,
        message_type="SYSTEM_EVENT",
        message_text=message_text,
        originating_module=originating_module,
        author_name=actor_name,
        author_employee_code=actor_code,
        author_department_name=dept_name,
        author_role_name=role_name,
        event_type=event_type,
        event_metadata=meta_str,
        created_at=now_utc,
    )
    session.add(msg)

    if actor:
        actor_read_receipt = TaskConversationReadState(
            read_id=uuid.uuid4(),
            message_id=msg.message_id,
            user_id=actor.user_id,
            sales_order_id=order_id,
            read_at=now_utc,
        )
        session.add(actor_read_receipt)

    session.flush()
    return msg


def mark_conversation_messages_as_read(
    session: Session,
    user: User,
    order_id: uuid.UUID,
    message_ids: List[uuid.UUID],
) -> Tuple[int, List[uuid.UUID]]:
    """Mark explicitly displayed message IDs as read for current authenticated user.

    Validates that:
    1. The user has authorized read access to the specified sales order.
    2. All message IDs actually belong to the sales order.
    3. Read receipts are recorded idempotently without duplicates.
    """
    if not message_ids:
        return 0, []

    order = session.get(SalesOrder, order_id)
    if not order or order.confirmation_status == "CANCELLED":
        raise ConversationNotFoundError(f"Sales order with ID '{order_id}' not found.")

    can_read, _, reason = check_conversation_access(session, user, order)
    if not can_read:
        raise permissions.PermissionDeniedError(reason)

    # Validate that the supplied message IDs belong to this sales order
    valid_messages = session.execute(
        select(TaskConversationMessage.message_id).where(
            TaskConversationMessage.sales_order_id == order_id,
            TaskConversationMessage.message_id.in_(message_ids),
        )
    ).scalars().all()

    if not valid_messages:
        return 0, []

    # Find which ones are already marked read for this user
    already_read = set(
        session.execute(
            select(TaskConversationReadState.message_id).where(
                TaskConversationReadState.user_id == user.user_id,
                TaskConversationReadState.message_id.in_(valid_messages),
            )
        ).scalars().all()
    )

    now_utc = datetime.now(timezone.utc)
    to_insert = [m_id for m_id in valid_messages if m_id not in already_read]

    for m_id in to_insert:
        read_receipt = TaskConversationReadState(
            read_id=uuid.uuid4(),
            message_id=m_id,
            user_id=user.user_id,
            sales_order_id=order_id,
            read_at=now_utc,
        )
        session.add(read_receipt)

    session.flush()
    return len(to_insert), list(valid_messages)


def get_user_unread_summary(
    session: Session,
    user: User,
) -> UnreadSummaryResponse:
    """Retrieve unread remark counts and metadata aggregated per sales order for the authenticated user."""
    auth_orders_subquery = get_user_authorized_orders_subquery(session, user)

    # Query all unread COMMENT messages for authorized orders created after feature cutoff
    read_exists = exists(
        select(1).where(
            TaskConversationReadState.message_id == TaskConversationMessage.message_id,
            TaskConversationReadState.user_id == user.user_id,
        )
    )

    unread_query = (
        select(
            TaskConversationMessage.sales_order_id,
            TaskConversationMessage.message_id,
            TaskConversationMessage.message_text,
            TaskConversationMessage.author_name,
            TaskConversationMessage.author_department_name,
            TaskConversationMessage.created_at,
        )
        .where(
            TaskConversationMessage.sales_order_id.in_(auth_orders_subquery),
            TaskConversationMessage.message_type == "COMMENT",
            TaskConversationMessage.created_at >= FEATURE_CUTOFF_DATE,
            not_(read_exists),
        )
        .order_by(
            TaskConversationMessage.sales_order_id,
            TaskConversationMessage.created_at.desc(),
        )
    )

    rows = session.execute(unread_query).all()

    unread_orders_map: Dict[str, UnreadOrderSummaryItem] = {}
    total_unread = len(rows)

    for row in rows:
        order_id_str = str(row.sales_order_id)
        if order_id_str not in unread_orders_map:
            unread_orders_map[order_id_str] = UnreadOrderSummaryItem(
                order_id=row.sales_order_id,
                unread_count=1,
                latest_unread_id=row.message_id,
                latest_remark_text=row.message_text,
                latest_author_name=row.author_name,
                latest_author_department=row.author_department_name,
                latest_created_at=row.created_at,
                formatted_latest_created_at=format_ist_datetime(row.created_at),
            )
        else:
            unread_orders_map[order_id_str].unread_count += 1

    return UnreadSummaryResponse(
        total_unread_count=total_unread,
        unread_orders=unread_orders_map,
    )


def get_user_notifications_list(
    session: Session,
    user: User,
    page: int = 1,
    limit: int = 20,
    unread_only: bool = False,
) -> RemarkNotificationListResponse:
    """Retrieve paginated remark notifications for the notification bell dropdown with smart routing."""
    auth_orders_subquery = get_user_authorized_orders_subquery(session, user)

    # Base query for messages joined with order and read state
    read_state_alias = (
        select(TaskConversationReadState.message_id)
        .where(TaskConversationReadState.user_id == user.user_id)
        .subquery()
    )

    base_query = (
        select(
            TaskConversationMessage,
            SalesOrder,
            case((read_state_alias.c.message_id.isnot(None), True), else_=False).label("is_read"),
        )
        .join(SalesOrder, SalesOrder.order_id == TaskConversationMessage.sales_order_id)
        .options(
            joinedload(SalesOrder.client),
            joinedload(SalesOrder.service),
            joinedload(SalesOrder.salesperson),
            joinedload(SalesOrder.application),
        )
        .outerjoin(read_state_alias, read_state_alias.c.message_id == TaskConversationMessage.message_id)
        .where(
            TaskConversationMessage.sales_order_id.in_(auth_orders_subquery),
            TaskConversationMessage.message_type == "COMMENT",
            TaskConversationMessage.created_at >= FEATURE_CUTOFF_DATE,
        )
    )

    if unread_only:
        base_query = base_query.where(read_state_alias.c.message_id.is_(None))

    # Total unread count
    unread_count_query = (
        select(func.count(TaskConversationMessage.message_id))
        .outerjoin(read_state_alias, read_state_alias.c.message_id == TaskConversationMessage.message_id)
        .where(
            TaskConversationMessage.sales_order_id.in_(auth_orders_subquery),
            TaskConversationMessage.message_type == "COMMENT",
            TaskConversationMessage.created_at >= FEATURE_CUTOFF_DATE,
            read_state_alias.c.message_id.is_(None),
        )
    )
    total_unread = session.execute(unread_count_query).scalar_one()

    # Total items in current filter
    count_query = select(func.count()).select_from(base_query.subquery())
    total_count = session.execute(count_query).scalar_one()

    # Pagination
    safe_page = max(1, page)
    safe_limit = min(100, max(1, limit))
    offset = (safe_page - 1) * safe_limit

    ordered_query = (
        base_query
        .order_by(TaskConversationMessage.created_at.desc(), TaskConversationMessage.message_id.desc())
        .offset(offset)
        .limit(safe_limit)
    )

    results = session.execute(ordered_query).all()

    items: List[RemarkNotificationItem] = []
    for msg, order, is_read in results:
        target_route = resolve_target_route_for_user(
            session=session,
            user=user,
            order=order,
            originating_module=getattr(msg, "originating_module", None),
        )
        items.append(
            RemarkNotificationItem(
                message_id=msg.message_id,
                sales_order_id=msg.sales_order_id,
                order_number=order.order_number,
                client_name=order.client.client_name if order.client else "Client",
                service_name=order.service.service_name if order.service else "Service",
                location=order.location,
                originating_module=getattr(msg, "originating_module", None),
                message_text=msg.message_text,
                author_name=msg.author_name or "Staff",
                author_employee_code=msg.author_employee_code,
                author_department_name=msg.author_department_name,
                author_role_name=msg.author_role_name,
                created_at=msg.created_at,
                formatted_created_at=format_ist_datetime(msg.created_at),
                is_read=bool(is_read or (msg.author_user_id and msg.author_user_id == user.user_id)),
                target_route=target_route,
            )
        )

    total_pages = (total_count + safe_limit - 1) // safe_limit if total_count > 0 else 1

    return RemarkNotificationListResponse(
        items=items,
        total_count=total_count,
        unread_count=total_unread,
        page=safe_page,
        limit=safe_limit,
        total_pages=total_pages,
    )


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
                message_id=uuid.uuid4(),
                sales_order_id=o.order_id,
                author_user_id=sp.user_id if sp else None,
                message_type="COMMENT",
                message_text=text_val,
                originating_module="SALES",
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
                message_id=uuid.uuid4(),
                sales_order_id=so_id,
                author_user_id=author.user_id if author else None,
                message_type="COMMENT",
                message_text=text_val,
                originating_module="OPERATIONS",
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
