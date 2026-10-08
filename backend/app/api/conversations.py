"""Shared Task Conversation HTTP APIs."""
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_fully_activated_user, require_super_admin
from app.database.session import get_db
from app.models.user import User
from app.schemas.conversation import (
    ConversationMessageCreate,
    ConversationMessageRead,
    ConversationThreadResponse,
)
from app.services import conversation_service, permissions

router = APIRouter(prefix="/api/conversations", tags=["Shared Task Conversations"])


@router.get(
    "/{order_id}",
    response_model=ConversationThreadResponse,
    summary="Get Task Conversation Thread",
    description="Retrieve the shared chronological conversation thread for a Sales Order / Compliance Task.",
)
def get_conversation_thread(
    order_id: uuid.UUID,
    limit: int = Query(50, ge=1, le=100, description="Number of messages to retrieve"),
    before_id: Optional[uuid.UUID] = Query(None, description="Cursor for loading older messages"),
    offset: int = Query(0, ge=0, description="Offset pagination"),
    current_user: User = Depends(require_fully_activated_user),
    session: Session = Depends(get_db),
):
    """Retrieve complete shared conversation thread with role-based access scoping."""
    try:
        thread = conversation_service.get_task_conversation(
            session=session,
            user=current_user,
            order_id=order_id,
            limit=limit,
            before_id=before_id,
            offset=offset,
        )
        return thread
    except conversation_service.ConversationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except permissions.PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post(
    "/{order_id}/messages",
    response_model=ConversationMessageRead,
    status_code=status.HTTP_201_CREATED,
    summary="Post Message / Remark to Conversation",
    description="Post a new append-only human remark to the shared task conversation.",
)
def post_conversation_message(
    order_id: uuid.UUID,
    payload: ConversationMessageCreate,
    current_user: User = Depends(require_fully_activated_user),
    session: Session = Depends(get_db),
):
    """Post an append-only remark derived strictly from the authenticated backend session."""
    try:
        msg = conversation_service.post_conversation_message(
            session=session,
            user=current_user,
            order_id=order_id,
            message_text=payload.message_text,
            idempotency_key=payload.idempotency_key,
        )
        session.commit()
        return msg
    except conversation_service.ConversationNotFoundError as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except permissions.PermissionDeniedError as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception:
        session.rollback()
        raise


@router.post(
    "/backfill/legacy-remarks",
    summary="Backfill Legacy Remarks",
    description="Safely migrate existing remarks into the unified conversation timeline (Idempotent).",
)
def trigger_legacy_backfill(
    current_user: User = Depends(require_super_admin),
    session: Session = Depends(get_db),
):
    """Execute repeat-safe migration of existing sales, operations, and accounts remarks."""
    stats = conversation_service.backfill_legacy_remarks(session)
    session.commit()
    return {"status": "success", "imported": stats}
