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
    MarkAllReadResponse,
    MarkBatchReadRequest,
    MarkBatchReadResponse,
    MarkReadRequest,
    MarkReadResponse,
    RemarkNotificationListResponse,
    UnreadSummaryResponse,
)
from app.services import conversation_service, permissions

router = APIRouter(prefix="/api/conversations", tags=["Shared Task Conversations"])


@router.get(
    "/unread-summary",
    response_model=UnreadSummaryResponse,
    summary="Get Unread Remarks Summary",
    description="Retrieve unread remark counts and metadata aggregated across all authorized tasks for the authenticated user.",
)
def get_unread_summary(
    current_user: User = Depends(require_fully_activated_user),
    session: Session = Depends(get_db),
):
    """Return total unread count and map of order_id to unread summary."""
    try:
        return conversation_service.get_user_unread_summary(
            session=session,
            user=current_user,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch unread remarks summary: {str(e)}",
        )


@router.get(
    "/notifications",
    response_model=RemarkNotificationListResponse,
    summary="Get Remark Notifications",
    description="Retrieve paginated remark notifications for the notification bell dropdown with smart routing.",
)
def get_remark_notifications(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    unread_only: bool = Query(False, description="Filter only unread notifications"),
    current_user: User = Depends(require_fully_activated_user),
    session: Session = Depends(get_db),
):
    """Return paginated remark notifications for current user with authorization checks."""
    try:
        return conversation_service.get_user_notifications_list(
            session=session,
            user=current_user,
            page=page,
            limit=limit,
            unread_only=unread_only,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch notifications: {str(e)}",
        )


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
            originating_module=payload.originating_module,
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
    "/{order_id}/mark-read",
    response_model=MarkReadResponse,
    summary="Mark Rendered Messages as Read",
    description="Explicitly mark rendered message IDs as read for the authenticated user.",
)
def mark_messages_read(
    order_id: uuid.UUID,
    payload: MarkReadRequest,
    current_user: User = Depends(require_fully_activated_user),
    session: Session = Depends(get_db),
):
    """Idempotently mark displayed message IDs as read for current user."""
    try:
        marked_count, valid_ids = conversation_service.mark_conversation_messages_as_read(
            session=session,
            user=current_user,
            order_id=order_id,
            message_ids=payload.message_ids,
        )
        session.commit()
        return MarkReadResponse(
            sales_order_id=order_id,
            marked_read_count=marked_count,
            read_message_ids=valid_ids,
        )
    except conversation_service.ConversationNotFoundError as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except permissions.PermissionDeniedError as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark messages as read: {str(e)}",
        )


@router.post(
    "/mark-read",
    response_model=MarkBatchReadResponse,
    summary="Mark Displayed Notification Messages as Read",
    description="Idempotently mark displayed notification message IDs as read for current user.",
)
def mark_notification_messages_read(
    payload: MarkBatchReadRequest,
    current_user: User = Depends(require_fully_activated_user),
    session: Session = Depends(get_db),
):
    """Idempotently mark displayed notification message IDs as read for current user."""
    try:
        marked_count, valid_ids = conversation_service.mark_notifications_as_read(
            session=session,
            user=current_user,
            message_ids=payload.message_ids,
        )
        session.commit()
        unread_summary = conversation_service.get_user_unread_summary(session=session, user=current_user)
        return MarkBatchReadResponse(
            marked_read_count=marked_count,
            read_message_ids=valid_ids,
            total_unread_count=unread_summary.total_unread_count,
        )
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark notifications as read: {str(e)}",
        )


@router.post(
    "/mark-all-read",
    response_model=MarkAllReadResponse,
    summary="Mark All Authorized Notifications as Read",
    description="Mark all unread remark notifications across all authorized tasks as read for current user.",
)
def mark_all_notifications_read(
    current_user: User = Depends(require_fully_activated_user),
    session: Session = Depends(get_db),
):
    """Mark all unread notifications across all authorized tasks as read for the authenticated user."""
    try:
        marked_count = conversation_service.mark_all_user_notifications_as_read(
            session=session,
            user=current_user,
        )
        session.commit()
        return MarkAllReadResponse(
            marked_read_count=marked_count,
            total_unread_count=0,
        )
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark all notifications as read: {str(e)}",
        )


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
