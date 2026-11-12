"""R&D / Internal Tasks API routes (tasks not linked to Sales orders)."""
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import require_fully_activated_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.internal_task import (
    InternalTaskCreate,
    InternalTaskListResponse,
    InternalTaskMessageCreate,
    InternalTaskMessageRead,
    InternalTaskRead,
    InternalTaskReassign,
    InternalTaskStatusUpdate,
    InternalTaskThreadResponse,
    InternalTaskUpdate,
    InternalTaskUserRef,
)
from app.services import internal_task_service as svc

router = APIRouter(prefix="/internal-tasks", tags=["R&D / Internal Tasks"])


def _run(session: Session, fn, *args, commit: bool = False, **kwargs):
    """Execute a service call, committing on success and mapping domain errors to HTTP errors."""
    try:
        result = fn(session, *args, **kwargs)
        if commit:
            session.commit()
        return result
    except svc.InternalTaskNotFoundError as exc:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except svc.InternalTaskPermissionError as exc:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except ValueError as exc:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception:
        session.rollback()
        raise


@router.get("", response_model=InternalTaskListResponse, summary="List Internal Tasks")
def list_internal_tasks(
    task_status: Optional[str] = Query(None, alias="status"),
    task_type: Optional[str] = Query(None),
    assigned_to_user_id: Optional[uuid.UUID] = Query(None),
    search: Optional[str] = Query(None, max_length=100),
    mine: bool = Query(False, description="Only tasks assigned to me"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(require_fully_activated_user),
    session: Session = Depends(get_db),
) -> InternalTaskListResponse:
    return _run(
        session,
        svc.list_tasks,
        current_user,
        status=task_status,
        task_type=task_type,
        assigned_to_user_id=assigned_to_user_id,
        search=search,
        mine_only=mine,
        skip=skip,
        limit=limit,
    )


@router.get("/assignees", response_model=List[InternalTaskUserRef], summary="Employees Available For Assignment")
def list_assignees(
    current_user: User = Depends(require_fully_activated_user),
    session: Session = Depends(get_db),
) -> List[InternalTaskUserRef]:
    return _run(session, svc.get_assignable_users, current_user)


@router.post("", response_model=InternalTaskRead, status_code=status.HTTP_201_CREATED, summary="Create & Assign Task")
def create_internal_task(
    payload: InternalTaskCreate,
    current_user: User = Depends(require_fully_activated_user),
    session: Session = Depends(get_db),
) -> InternalTaskRead:
    return _run(session, svc.create_task, current_user, payload, commit=True)


@router.get("/{task_id}", response_model=InternalTaskRead, summary="Get Internal Task")
def get_internal_task(
    task_id: uuid.UUID,
    current_user: User = Depends(require_fully_activated_user),
    session: Session = Depends(get_db),
) -> InternalTaskRead:
    return _run(session, svc.get_task, current_user, task_id)


@router.patch("/{task_id}", response_model=InternalTaskRead, summary="Edit Internal Task Details")
def update_internal_task(
    task_id: uuid.UUID,
    payload: InternalTaskUpdate,
    current_user: User = Depends(require_fully_activated_user),
    session: Session = Depends(get_db),
) -> InternalTaskRead:
    return _run(session, svc.update_task, current_user, task_id, payload, commit=True)


@router.post("/{task_id}/status", response_model=InternalTaskRead, summary="Change Internal Task Status")
def update_internal_task_status(
    task_id: uuid.UUID,
    payload: InternalTaskStatusUpdate,
    current_user: User = Depends(require_fully_activated_user),
    session: Session = Depends(get_db),
) -> InternalTaskRead:
    return _run(session, svc.update_status, current_user, task_id, payload.status, payload.comment, commit=True)


@router.post("/{task_id}/reassign", response_model=InternalTaskRead, summary="Reassign Internal Task")
def reassign_internal_task(
    task_id: uuid.UUID,
    payload: InternalTaskReassign,
    current_user: User = Depends(require_fully_activated_user),
    session: Session = Depends(get_db),
) -> InternalTaskRead:
    return _run(
        session, svc.reassign_task, current_user, task_id, payload.assigned_to_user_id, payload.reason, commit=True
    )


@router.get("/{task_id}/messages", response_model=InternalTaskThreadResponse, summary="Get Task Chat")
def get_internal_task_messages(
    task_id: uuid.UUID,
    current_user: User = Depends(require_fully_activated_user),
    session: Session = Depends(get_db),
) -> InternalTaskThreadResponse:
    return _run(session, svc.get_thread, current_user, task_id)


@router.post(
    "/{task_id}/messages",
    response_model=InternalTaskMessageRead,
    status_code=status.HTTP_201_CREATED,
    summary="Post Message To Task Chat",
)
def post_internal_task_message(
    task_id: uuid.UUID,
    payload: InternalTaskMessageCreate,
    current_user: User = Depends(require_fully_activated_user),
    session: Session = Depends(get_db),
) -> InternalTaskMessageRead:
    return _run(session, svc.post_message, current_user, task_id, payload.message_text, commit=True)
