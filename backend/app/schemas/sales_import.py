"""Pydantic schemas for Sales Bulk Import, Validation, and Bulk Assignment."""
import uuid
from decimal import Decimal
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class SalesImportRowValidation(BaseModel):
    """Validation outcome for a single imported row."""

    model_config = ConfigDict(from_attributes=True)

    row_number: int = Field(..., description="1-based data row number in the file")
    sl_no: Optional[str] = Field(None, description="Original serial number identifier from template")
    location: Optional[str] = Field(None, description="Location / Branch / City")
    client_name: Optional[str] = Field(None, description="Client or company name")
    contact: Optional[str] = Field(None, description="Client phone / contact number (text preserved)")
    source: Optional[str] = Field(None, description="Normalized lead source")
    work: Optional[str] = Field(None, description="Service / Work name from template")
    base_amount: Optional[Decimal] = Field(None, description="Base order amount before GST in INR")
    gst_amount: Optional[Decimal] = Field(Decimal("0.00"), description="Calculated 18% GST amount in INR")
    gst_rate: Optional[Decimal] = Field(Decimal("0.00"), description="GST rate percentage applied (0 or 18)")
    gst_invoice_required: Optional[bool] = Field(False, description="Whether 18% GST was calculated and GST invoice required")
    total_amount: Optional[Decimal] = Field(None, description="Order total amount (Order Value) in INR")
    advance_amount: Optional[Decimal] = Field(Decimal("0.00"), description="Advance payment received in INR")
    incidental_cost: Optional[Decimal] = Field(Decimal("0.00"), description="Incidental expenses in INR")
    service_id: Optional[uuid.UUID] = Field(None, description="Resolved ServiceMaster UUID")
    service_name: Optional[str] = Field(None, description="Resolved official service name")
    is_valid: bool = Field(..., description="Whether this row passes all strict validation rules")
    is_duplicate_in_file: bool = Field(False, description="Whether this row duplicates another row in the same file")
    is_duplicate_in_db: bool = Field(False, description="Whether this matches an active order in the database")
    errors: List[str] = Field(default_factory=list, description="List of blocking validation error messages")
    warnings: List[str] = Field(default_factory=list, description="List of non-blocking warning messages (e.g. duplicates)")


class SalesImportPreviewResponse(BaseModel):
    """Summary and row-by-row preview for uploaded Excel/CSV file."""

    model_config = ConfigDict(from_attributes=True)

    filename: str = Field(..., description="Original uploaded filename")
    total_rows: int = Field(..., description="Total rows parsed (excluding headers and example rows)")
    valid_rows_count: int = Field(..., description="Count of fully valid rows ready for import")
    error_rows_count: int = Field(..., description="Count of rows with blocking validation errors")
    duplicate_warnings_count: int = Field(..., description="Count of rows with potential duplicate warnings")
    can_import: bool = Field(..., description="True if batch is valid and ready for confirmation")
    apply_gst: bool = Field(False, description="Whether 18% GST calculation was applied to preview")
    total_base_amount: Optional[Decimal] = Field(None, description="Sum of base amounts across all valid rows")
    total_gst_amount: Optional[Decimal] = Field(None, description="Sum of GST amounts across all valid rows")
    rows: List[SalesImportRowValidation] = Field(..., description="Row-by-row validation details and preview data")


class SalesImportExecuteRequest(BaseModel):
    """Payload to commit validated sales records and assign them to an Operations assignee."""

    model_config = ConfigDict(from_attributes=True)

    rows: List[SalesImportRowValidation] = Field(..., description="Validated rows to be imported")
    assignee_user_id: uuid.UUID = Field(..., description="Selected eligible Operations employee UUID")
    idempotency_key: Optional[str] = Field(None, description="Unique client key to prevent double submissions")
    allow_duplicates: bool = Field(
        default=False,
        description="Whether user explicitly confirmed import despite non-blocking duplicate warnings",
    )
    apply_gst: bool = Field(
        default=False,
        description="Whether to apply 18% GST calculation to base amounts and set gst_invoice_required=True",
    )


class SalesImportExecuteResponse(BaseModel):
    """Response returned upon successful atomic bulk sales import."""

    model_config = ConfigDict(from_attributes=True)

    success: bool = Field(..., description="True if entire batch was committed cleanly")
    imported_count: int = Field(..., description="Number of sales orders created")
    assignments_count: int = Field(..., description="Number of Operations assignments created")
    order_numbers: List[str] = Field(default_factory=list, description="Generated order numbers for created entries")
    message: str = Field(..., description="Human-readable success message")
