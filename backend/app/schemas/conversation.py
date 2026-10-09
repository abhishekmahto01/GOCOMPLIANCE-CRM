"""Pydantic schemas for Shared Task Conversation, Remarks, and Per-User Read Receipts."""
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict, Field, field_validator


IST_ZONE = ZoneInfo("Asia/Kolkata")


def format_ist_datetime(dt: Optional[datetime]) -> str:
    """Format UTC datetime into human-readable Asia/Kolkata time string."""
    if not dt:
        return "Date unavailable"
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    ist_dt = dt.astimezone(IST_ZONE)
    return ist_dt.strftime("%d %b %Y, %I:%M %p")


class ConversationMessageCreate(BaseModel):
    """Payload for creating a new comment/remark in the shared conversation."""

    message_text: str = Field(
        ...,
        min_length=1,
        max_length=3000,
        description="Remark / update text content",
    )
    originating_module: Optional[str] = Field(
        None,
        max_length=30,
        description="Optional module hint: SALES, OPERATIONS, ACCOUNTS",
    )
    idempotency_key: Optional[str] = Field(
        None,
        max_length=100,
        description="Client-supplied idempotency key preventing duplicate posts on retry",
    )

    @field_validator("message_text")
    @classmethod
    def validate_message_text(cls, v: str) -> str:
        stripped = (v or "").strip()
        if not stripped:
            raise ValueError("Message text cannot be empty or whitespace only.")
        return stripped


class ConversationMessageRead(BaseModel):
    """Response schema for a single conversation message or system event."""

    message_id: uuid.UUID
    sales_order_id: uuid.UUID
    author_user_id: Optional[uuid.UUID] = None
    message_type: str = Field(..., description="COMMENT or SYSTEM_EVENT")
    message_text: str
    originating_module: Optional[str] = None
    author_name: str
    author_employee_code: Optional[str] = None
    author_department_name: Optional[str] = None
    author_role_name: Optional[str] = None
    event_type: Optional[str] = None
    event_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    formatted_created_at: str
    is_mine: bool = False
    is_read: bool = True

    model_config = ConfigDict(from_attributes=True)


class LatestRemarkSummary(BaseModel):
    """Summary of the latest human remark on a sales order / compliance task."""

    message_id: Optional[uuid.UUID] = None
    remark_text: str
    author_name: str
    author_employee_code: Optional[str] = None
    author_department: Optional[str] = None
    created_at: Optional[datetime] = None
    formatted_created_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ConversationThreadResponse(BaseModel):
    """Complete thread view and metadata for task conversation modal."""

    order_id: uuid.UUID
    order_number: str
    client_name: str
    service_name: str
    location: Optional[str] = None
    salesperson_name: str
    salesperson_code: Optional[str] = None
    current_assignee_id: Optional[uuid.UUID] = None
    current_assignee_name: Optional[str] = None
    current_assignee_code: Optional[str] = None
    application_id: Optional[uuid.UUID] = None
    application_number: Optional[str] = None
    work_status: str
    payment_status: str
    gst_invoice_required: bool
    company_id: uuid.UUID
    company_name: str
    company_code: Optional[str] = None
    can_post: bool
    items: List[ConversationMessageRead]
    total_count: int
    has_more_older: bool = False

    model_config = ConfigDict(from_attributes=True)


class MarkReadRequest(BaseModel):
    """Payload for explicitly marking rendered message IDs as read for current user."""

    message_ids: List[uuid.UUID] = Field(
        ...,
        min_length=1,
        max_length=200,
        description="List of explicitly displayed message IDs to mark read",
    )


class MarkReadResponse(BaseModel):
    """Response returned after marking messages as read."""

    sales_order_id: uuid.UUID
    marked_read_count: int
    read_message_ids: List[uuid.UUID]

    model_config = ConfigDict(from_attributes=True)


class UnreadOrderSummaryItem(BaseModel):
    """Unread remarks metadata for a single sales order / compliance task."""

    order_id: uuid.UUID
    unread_count: int
    latest_unread_id: Optional[uuid.UUID] = None
    latest_remark_text: Optional[str] = None
    latest_author_name: Optional[str] = None
    latest_author_department: Optional[str] = None
    latest_created_at: Optional[datetime] = None
    formatted_latest_created_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class UnreadSummaryResponse(BaseModel):
    """Batch unread summary for authenticated user across all authorized tasks."""

    total_unread_count: int
    unread_orders: Dict[str, UnreadOrderSummaryItem] = Field(
        default_factory=dict,
        description="Map of sales_order_id (str) to UnreadOrderSummaryItem",
    )

    model_config = ConfigDict(from_attributes=True)


class RemarkNotificationItem(BaseModel):
    """Single notification item for common notification bell dropdown."""

    message_id: uuid.UUID
    sales_order_id: uuid.UUID
    order_number: str
    client_name: str
    service_name: str
    location: Optional[str] = None
    originating_module: Optional[str] = None
    message_text: str
    author_name: str
    author_employee_code: Optional[str] = None
    author_department_name: Optional[str] = None
    author_role_name: Optional[str] = None
    created_at: datetime
    formatted_created_at: str
    is_read: bool = False
    target_route: str = Field(
        ...,
        description="Smart authorized deep-link URL for navigating directly to the entry & opening conversation",
    )

    model_config = ConfigDict(from_attributes=True)


class RemarkNotificationListResponse(BaseModel):
    """Paginated list of remark notifications for notification bell."""

    items: List[RemarkNotificationItem]
    total_count: int
    unread_count: int
    page: int
    limit: int
    total_pages: int

    model_config = ConfigDict(from_attributes=True)
