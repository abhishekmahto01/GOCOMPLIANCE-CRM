"""Pydantic schemas for Sales Orders and Confirmation."""
import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SalesOrderBase(BaseModel):
    """Base schema for Sales Order."""

    company_id: uuid.UUID
    client_id: uuid.UUID
    service_id: uuid.UUID
    salesperson_user_id: uuid.UUID
    lead_source: str = Field(default="DIRECT", description="WEBSITE, REFERRAL, DIRECT, OTHERS")
    order_date: date
    order_value: Decimal = Field(..., ge=0, description="Total order amount in INR")
    amount_received: Decimal = Field(default=Decimal("0.00"), ge=0, description="Amount collected in INR")
    payment_status: str = Field(default="PENDING", description="FULLY_PAID, PARTIALLY_PAID, PENDING, OVERDUE")
    notes: Optional[str] = Field(None, max_length=1000)

    @field_validator("lead_source", mode="before")
    @classmethod
    def normalize_lead_source(cls, v: str) -> str:
        if isinstance(v, str):
            v = v.strip().upper()
        return v

    @field_validator("payment_status", mode="before")
    @classmethod
    def normalize_payment_status(cls, v: str) -> str:
        if isinstance(v, str):
            v = v.strip().upper()
            if v not in ("FULLY_PAID", "PARTIALLY_PAID", "PENDING", "OVERDUE"):
                raise ValueError(f"Invalid payment status '{v}'")
        return v


class SalesOrderCreate(SalesOrderBase):
    """Schema for creating a sales order."""
    auto_confirm: bool = Field(default=False, description="Automatically confirm order upon creation")


class SalesOrderUpdate(BaseModel):
    """Schema for updating a sales order."""

    order_value: Optional[Decimal] = Field(None, ge=0)
    amount_received: Optional[Decimal] = Field(None, ge=0)
    payment_status: Optional[str] = None
    lead_source: Optional[str] = None
    order_date: Optional[date] = None
    notes: Optional[str] = Field(None, max_length=1000)


class SalesOrderRead(BaseModel):
    """Lightweight read schema for Sales Order."""

    order_id: uuid.UUID
    order_number: str
    company_id: uuid.UUID
    client_id: uuid.UUID
    service_id: uuid.UUID
    salesperson_user_id: uuid.UUID
    lead_source: str
    order_date: date
    order_value: Decimal
    amount_received: Decimal
    balance_amount: Decimal
    payment_status: str
    confirmation_status: str
    confirmed_at: Optional[datetime]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SalesOrderDetailRead(SalesOrderRead):
    """Enriched Sales Order read schema with joined metadata for UI tables."""

    client_name: Optional[str] = None
    service_name: Optional[str] = None
    salesperson_name: Optional[str] = None
    application_id: Optional[uuid.UUID] = None
    application_number: Optional[str] = None
    operation_status: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class SalesOrderConfirmResponse(BaseModel):
    """Response returned when an order is confirmed and handed over to operations."""

    order_id: uuid.UUID
    order_number: str
    confirmation_status: str
    confirmed_at: datetime
    application_id: uuid.UUID
    application_number: str
    application_status: str
    assigned_to_user_id: Optional[uuid.UUID] = None
    documents_count: int

    model_config = ConfigDict(from_attributes=True)
