"""Pydantic schemas for Shared Task Conversation and Remarks."""
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
    author_name: str
    author_employee_code: Optional[str] = None
    author_department_name: Optional[str] = None
    author_role_name: Optional[str] = None
    event_type: Optional[str] = None
    event_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    formatted_created_at: str
    is_mine: bool = False

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
