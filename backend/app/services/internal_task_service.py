"""Business logic for R&D / Internal Tasks (tasks not linked to Sales orders).

Access model (enforced on every read and write, per record):
- Manager: Super Admin, or a user with an ACTIVE permission row on page OPERATION_INTERNAL_TASKS
  that has can_view and (can_create or can_assign). A manager sees tasks within their data scope:
    ALL -> every company; COMPANY / DEPARTMENT -> own company; TEAM -> own team; SELF -> own tasks.
- Everyone (any department) always sees tasks assigned to them or created by them.
- Create: Super Admin or can_create.  Reassign: Super Admin, can_assign or can_create (within scope).
- Edit details: task creator or a manager in scope with can_create / can_edit.
- Status: assignee may move PENDING / IN_PROGRESS / COMPLETED; creator or manager in scope may
  additionally cancel or reopen (COMPLETED / CANCELLED -> PENDING / IN_PROGRESS).
- Chat: anyone who can see the task can read and post.

The broad "Operations department / manager" fallbacks in permissions.has_permission are deliberately
NOT used here, so only explicit grants on this page make someone a manager.
"""
import uuid
from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Dict, List, Optional

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.company import Company
from app.models.internal_task import InternalTask, InternalTaskMessage, internal_task_number_seq
from app.models.module import Module
from app.models.user import User
from app.models.user_module_permission import UserModulePermission
from app.schemas.internal_task import (
    InternalTaskCapabilities,
    InternalTaskCreate,
    InternalTaskListResponse,
    InternalTaskMessageRead,
    InternalTaskRead,
    InternalTaskSummary,
    InternalTaskThreadResponse,
    InternalTaskUpdate,
    InternalTaskUserRef,
)
from app.services import permissions

PAGE_CODE = "OPERATION_INTERNAL_TASKS"
TASK_NUMBER_PREFIX = "RND"
ASSIGNEE_ALLOWED_STATUSES = {"PENDING", "IN_PROGRESS", "COMPLETED"}


class InternalTaskNotFoundError(Exception):
    """Task does not exist or is not visible to the current user."""


class InternalTaskPermissionError(Exception):
    """User is not allowed to perform this action."""


@dataclass
class _Access:
    user: User
    is_super: bool
    scope: Optional[str]  # manager scope, None when not a manager
    can_create: bool
    can_assign: bool
    can_edit: bool
    team_ids: List[uuid.UUID]

    @property
    def is_manager(self) -> bool:
        return self.scope is not None


# -----------------------------------------------------------------------------
# Access resolution
# -----------------------------------------------------------------------------
def _page_permission(session: Session, user: User) -> Optional[UserModulePermission]:
    perm = session.execute(
        select(UserModulePermission)
        .join(Module, UserModulePermission.module_id == Module.module_id)
        .where(
            UserModulePermission.user_id == user.user_id,
            Module.module_code == PAGE_CODE,
        )
    ).scalar_one_or_none()
    if perm and permissions.is_permission_active_and_valid(perm) and perm.can_view:
        return perm
    return None


def resolve_access(session: Session, user: User) -> _Access:
    if permissions.is_super_admin_user(session, user):
        return _Access(user, True, "ALL", True, True, True, [])

    perm = _page_permission(session, user)
    if perm and (perm.can_create or perm.can_assign):
        scope = (perm.data_scope or "SELF").strip().upper()
        team_ids = permissions.get_team_user_ids(session, user.user_id) if scope == "TEAM" else []
        return _Access(
            user,
            False,
            scope,
            bool(perm.can_create),
            bool(perm.can_assign or perm.can_create),
            bool(perm.can_edit or perm.can_create),
            team_ids,
        )
    return _Access(user, False, None, False, False, False, [])


def _visibility_filter(access: _Access):
    """SQL condition selecting tasks visible to the user."""
    uid = access.user.user_id
    own = or_(InternalTask.assigned_to_user_id == uid, InternalTask.created_by_user_id == uid)
    if access.scope == "ALL":
        return None
    if access.scope in ("COMPANY", "DEPARTMENT"):
        return or_(own, InternalTask.company_id == access.user.company_id)
    if access.scope == "TEAM":
        return or_(
            own,
            InternalTask.assigned_to_user_id.in_(access.team_ids),
            InternalTask.created_by_user_id.in_(access.team_ids),
        )
    return own


def _manager_covers(access: _Access, task: InternalTask) -> bool:
    """Whether the user's manager scope covers this task."""
    if not access.is_manager:
        return False
    if access.scope == "ALL":
        return True
    if access.scope in ("COMPANY", "DEPARTMENT"):
        return task.company_id == access.user.company_id
    if access.scope == "TEAM":
        return task.assigned_to_user_id in access.team_ids or task.created_by_user_id in access.team_ids
    uid = access.user.user_id
    return task.assigned_to_user_id == uid or task.created_by_user_id == uid


def _can_view(access: _Access, task: InternalTask) -> bool:
    uid = access.user.user_id
    return task.assigned_to_user_id == uid or task.created_by_user_id == uid or _manager_covers(access, task)


def _is_owner_or_manager(access: _Access, task: InternalTask) -> bool:
    return task.created_by_user_id == access.user.user_id or _manager_covers(access, task)


def _can_edit(access: _Access, task: InternalTask) -> bool:
    if task.created_by_user_id == access.user.user_id:
        return True
    return _manager_covers(access, task) and access.can_edit


def _can_reassign(access: _Access, task: InternalTask) -> bool:
    return access.can_assign and _manager_covers(access, task)


def _can_update_status(access: _Access, task: InternalTask) -> bool:
    return task.assigned_to_user_id == access.user.user_id or _is_owner_or_manager(access, task)


def _assignee_in_scope(access: _Access, assignee: User) -> bool:
    if access.scope == "ALL":
        return True
    if access.scope == "TEAM":
        return assignee.user_id in access.team_ids
    if access.scope == "SELF":
        return assignee.user_id == access.user.user_id
    return assignee.company_id == access.user.company_id


# -----------------------------------------------------------------------------
# Serialization helpers
# -----------------------------------------------------------------------------
def _full_name(u: Optional[User]) -> str:
    if not u:
        return ""
    return " ".join(p for p in [u.first_name, u.last_name] if p).strip() or (u.employee_code or "")


def _user_ref(u: Optional[User]) -> Optional[InternalTaskUserRef]:
    if not u:
        return None
    return InternalTaskUserRef(
        user_id=u.user_id,
        name=_full_name(u),
        employee_code=u.employee_code,
        department_name=u.department.department_name if getattr(u, "department", None) else None,
        company_name=u.company.company_name if getattr(u, "company", None) else None,
    )


def _to_read(access: _Access, task: InternalTask, message_count: int = 0) -> InternalTaskRead:
    today = date.today()
    return InternalTaskRead(
        task_id=task.task_id,
        task_number=task.task_number,
        company_id=task.company_id,
        company_name=task.company.company_name if task.company else None,
        title=task.title,
        description=task.description,
        task_type=task.task_type,
        priority=task.priority,
        status=task.status,
        assigned_to=_user_ref(task.assigned_to),
        created_by=_user_ref(task.created_by),
        due_date=task.due_date,
        is_overdue=bool(task.due_date and task.due_date < today and task.status in ("PENDING", "IN_PROGRESS")),
        completed_at=task.completed_at,
        created_at=task.created_at,
        updated_at=task.updated_at,
        message_count=message_count,
        can_update_status=_can_update_status(access, task),
        can_edit=_can_edit(access, task),
        can_reassign=_can_reassign(access, task),
    )


def _to_message_read(user: User, m: InternalTaskMessage) -> InternalTaskMessageRead:
    return InternalTaskMessageRead(
        message_id=m.message_id,
        task_id=m.task_id,
        author_user_id=m.author_user_id,
        author_name=m.author_name,
        author_employee_code=m.author_employee_code,
        author_department_name=m.author_department_name,
        message_type=m.message_type,
        message_text=m.message_text,
        is_own=m.author_user_id == user.user_id,
        created_at=m.created_at,
    )


def _add_message(session: Session, task: InternalTask, actor: User, text: str, message_type: str) -> InternalTaskMessage:
    msg = InternalTaskMessage(
        message_id=uuid.uuid4(),
        task_id=task.task_id,
        author_user_id=actor.user_id,
        message_type=message_type,
        message_text=text,
        author_name=_full_name(actor),
        author_employee_code=actor.employee_code,
        author_department_name=actor.department.department_name if getattr(actor, "department", None) else None,
        created_at=datetime.now(timezone.utc),
    )
    session.add(msg)
    return msg


def _message_counts(session: Session, task_ids: List[uuid.UUID]) -> Dict[uuid.UUID, int]:
    if not task_ids:
        return {}
    rows = session.execute(
        select(InternalTaskMessage.task_id, func.count(InternalTaskMessage.message_id))
        .where(
            InternalTaskMessage.task_id.in_(task_ids),
            InternalTaskMessage.message_type == "COMMENT",
        )
        .group_by(InternalTaskMessage.task_id)
    ).all()
    return {r[0]: int(r[1]) for r in rows}


def _get_visible_task(session: Session, access: _Access, task_id: uuid.UUID) -> InternalTask:
    task = session.get(InternalTask, task_id)
    # Same error for "missing" and "not visible" so task IDs cannot be probed.
    if not task or not _can_view(access, task):
        raise InternalTaskNotFoundError("Task not found.")
    return task


def _load_active_user(session: Session, user_id: uuid.UUID) -> User:
    u = session.get(User, user_id)
    if not u or u.account_status != "ACTIVE":
        raise ValueError("Selected employee is not an active employee.")
    return u


# -----------------------------------------------------------------------------
# Public operations
# -----------------------------------------------------------------------------
def list_tasks(
    session: Session,
    user: User,
    status: Optional[str] = None,
    task_type: Optional[str] = None,
    assigned_to_user_id: Optional[uuid.UUID] = None,
    search: Optional[str] = None,
    mine_only: bool = False,
    skip: int = 0,
    limit: int = 50,
) -> InternalTaskListResponse:
    access = resolve_access(session, user)

    base = select(InternalTask)
    vis = _visibility_filter(access)
    if vis is not None:
        base = base.where(vis)
    if mine_only:
        base = base.where(InternalTask.assigned_to_user_id == user.user_id)
    if task_type:
        base = base.where(InternalTask.task_type == task_type.strip().upper())
    if assigned_to_user_id:
        base = base.where(InternalTask.assigned_to_user_id == assigned_to_user_id)
    if search and search.strip():
        term = f"%{search.strip()}%"
        base = base.where(or_(InternalTask.title.ilike(term), InternalTask.task_number.ilike(term)))

    # Summary cards reflect all filters except status.
    counts: Dict[str, int] = {}
    sub = base.subquery()
    for st, cnt in session.execute(select(sub.c.status, func.count()).group_by(sub.c.status)).all():
        counts[st] = int(cnt)
    summary = InternalTaskSummary(
        pending=counts.get("PENDING", 0),
        in_progress=counts.get("IN_PROGRESS", 0),
        completed=counts.get("COMPLETED", 0),
        cancelled=counts.get("CANCELLED", 0),
    )
    summary.total = summary.pending + summary.in_progress + summary.completed

    query = base
    if status:
        query = query.where(InternalTask.status == status.strip().upper())

    total = session.execute(select(func.count()).select_from(query.subquery())).scalar() or 0
    tasks = session.execute(
        query.order_by(InternalTask.created_at.desc()).offset(skip).limit(limit)
    ).unique().scalars().all()
    msg_counts = _message_counts(session, [t.task_id for t in tasks])

    return InternalTaskListResponse(
        items=[_to_read(access, t, msg_counts.get(t.task_id, 0)) for t in tasks],
        total=int(total),
        summary=summary,
        capabilities=InternalTaskCapabilities(
            can_create=access.can_create,
            can_assign=access.can_assign,
            is_manager=access.is_manager,
            scope=access.scope,
        ),
    )


def get_assignable_users(session: Session, user: User) -> List[InternalTaskUserRef]:
    """Active employees (any department) the current manager may assign tasks to."""
    access = resolve_access(session, user)
    if not (access.can_create or access.can_assign):
        raise InternalTaskPermissionError("You are not allowed to assign internal tasks.")
    stmt = select(User).where(User.account_status == "ACTIVE")
    if access.scope == "TEAM":
        stmt = stmt.where(User.user_id.in_(access.team_ids))
    elif access.scope == "SELF":
        stmt = stmt.where(User.user_id == user.user_id)
    elif access.scope != "ALL":
        stmt = stmt.where(User.company_id == user.company_id)
    users = session.execute(stmt.order_by(User.first_name, User.last_name)).unique().scalars().all()
    return [r for r in (_user_ref(u) for u in users) if r]


def create_task(session: Session, user: User, data: InternalTaskCreate) -> InternalTaskRead:
    access = resolve_access(session, user)
    if not access.can_create:
        raise InternalTaskPermissionError("You are not allowed to create internal tasks.")

    assignee = _load_active_user(session, data.assigned_to_user_id)
    if not _assignee_in_scope(access, assignee):
        raise InternalTaskPermissionError("You can only assign tasks to employees within your authorized scope.")
    company_id = assignee.company_id or user.company_id
    if not company_id or not session.get(Company, company_id):
        raise ValueError("Assigned employee does not belong to a valid company.")

    seq_val = session.execute(select(internal_task_number_seq.next_value())).scalar_one()
    task = InternalTask(
        task_id=uuid.uuid4(),
        task_number=f"{TASK_NUMBER_PREFIX}-{int(seq_val):04d}",
        company_id=company_id,
        title=data.title,
        description=data.description,
        task_type=data.task_type,
        priority=data.priority,
        status="PENDING",
        assigned_to_user_id=assignee.user_id,
        created_by_user_id=user.user_id,
        due_date=data.due_date,
    )
    session.add(task)
    session.flush()
    _add_message(
        session,
        task,
        user,
        f"Task created and assigned to {_full_name(assignee)} ({assignee.employee_code}) by {_full_name(user)}.",
        "SYSTEM_EVENT",
    )
    if data.description:
        _add_message(session, task, user, data.description, "COMMENT")
    session.flush()
    session.refresh(task)
    return _to_read(access, task, 1 if data.description else 0)


def get_task(session: Session, user: User, task_id: uuid.UUID) -> InternalTaskRead:
    access = resolve_access(session, user)
    task = _get_visible_task(session, access, task_id)
    return _to_read(access, task, _message_counts(session, [task.task_id]).get(task.task_id, 0))


def update_task(session: Session, user: User, task_id: uuid.UUID, data: InternalTaskUpdate) -> InternalTaskRead:
    access = resolve_access(session, user)
    task = _get_visible_task(session, access, task_id)
    if not _can_edit(access, task):
        raise InternalTaskPermissionError("Only the task creator or an authorized manager can edit this task.")

    changes = []
    fields = data.model_fields_set
    if "title" in fields and data.title and data.title != task.title:
        changes.append(f"Title: {task.title} -> {data.title}")
        task.title = data.title
    if "description" in fields and data.description != task.description:
        changes.append("Description updated")
        task.description = data.description
    if "task_type" in fields and data.task_type and data.task_type != task.task_type:
        changes.append(f"Type: {task.task_type} -> {data.task_type}")
        task.task_type = data.task_type
    if "priority" in fields and data.priority and data.priority != task.priority:
        changes.append(f"Priority: {task.priority} -> {data.priority}")
        task.priority = data.priority
    if "due_date" in fields and data.due_date != task.due_date:
        changes.append(f"Due date: {task.due_date or 'None'} -> {data.due_date or 'None'}")
        task.due_date = data.due_date

    if changes:
        _add_message(session, task, user, f"Task updated by {_full_name(user)}: " + "; ".join(changes), "SYSTEM_EVENT")
    session.flush()
    return get_task(session, user, task_id)


def update_status(
    session: Session, user: User, task_id: uuid.UUID, new_status: str, comment: Optional[str] = None
) -> InternalTaskRead:
    access = resolve_access(session, user)
    task = _get_visible_task(session, access, task_id)
    if not _can_update_status(access, task):
        raise InternalTaskPermissionError("You are not allowed to change the status of this task.")

    old_status = task.status
    if new_status == old_status:
        return get_task(session, user, task_id)

    privileged = _is_owner_or_manager(access, task)
    if not privileged:
        if old_status in ("COMPLETED", "CANCELLED"):
            raise InternalTaskPermissionError("Only the task creator or a manager can reopen this task.")
        if new_status not in ASSIGNEE_ALLOWED_STATUSES:
            raise InternalTaskPermissionError("Only the task creator or a manager can cancel this task.")

    task.status = new_status
    if new_status == "COMPLETED":
        task.completed_at = datetime.now(timezone.utc)
    elif old_status == "COMPLETED":
        task.completed_at = None

    label = {"PENDING": "Pending", "IN_PROGRESS": "In Progress", "COMPLETED": "Completed", "CANCELLED": "Cancelled"}
    text = f"Status changed from {label[old_status]} to {label[new_status]} by {_full_name(user)}."
    if comment and comment.strip():
        text += f" Note: {comment.strip()}"
    _add_message(session, task, user, text, "SYSTEM_EVENT")
    session.flush()
    return get_task(session, user, task_id)


def reassign_task(
    session: Session, user: User, task_id: uuid.UUID, new_assignee_id: uuid.UUID, reason: Optional[str] = None
) -> InternalTaskRead:
    access = resolve_access(session, user)
    task = _get_visible_task(session, access, task_id)
    if not _can_reassign(access, task):
        raise InternalTaskPermissionError("You are not allowed to reassign this task.")

    assignee = _load_active_user(session, new_assignee_id)
    if not _assignee_in_scope(access, assignee):
        raise InternalTaskPermissionError("You can only assign tasks to employees within your authorized scope.")
    if task.assigned_to_user_id == assignee.user_id:
        raise ValueError("Task is already assigned to this employee.")

    prev = task.assigned_to
    task.assigned_to_user_id = assignee.user_id
    task.assigned_to = assignee
    if assignee.company_id:
        task.company_id = assignee.company_id
    text = (
        f"Task reassigned from {_full_name(prev) or 'Unassigned'} to {_full_name(assignee)} "
        f"({assignee.employee_code}) by {_full_name(user)}."
    )
    if reason and reason.strip():
        text += f" Reason: {reason.strip()}"
    _add_message(session, task, user, text, "SYSTEM_EVENT")
    session.flush()
    return get_task(session, user, task_id)


def get_thread(session: Session, user: User, task_id: uuid.UUID) -> InternalTaskThreadResponse:
    access = resolve_access(session, user)
    task = _get_visible_task(session, access, task_id)
    msgs = session.execute(
        select(InternalTaskMessage)
        .where(InternalTaskMessage.task_id == task.task_id)
        .order_by(InternalTaskMessage.created_at.asc(), InternalTaskMessage.message_id.asc())
    ).scalars().all()
    comment_count = sum(1 for m in msgs if m.message_type == "COMMENT")
    return InternalTaskThreadResponse(
        task=_to_read(access, task, comment_count),
        messages=[_to_message_read(user, m) for m in msgs],
        can_post=True,
    )


def post_message(session: Session, user: User, task_id: uuid.UUID, text: str) -> InternalTaskMessageRead:
    access = resolve_access(session, user)
    task = _get_visible_task(session, access, task_id)
    msg = _add_message(session, task, user, text, "COMMENT")
    session.flush()
    return _to_message_read(user, msg)
