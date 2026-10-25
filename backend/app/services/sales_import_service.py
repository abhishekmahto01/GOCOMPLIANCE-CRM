"""Sales Bulk Import Service.

Handles:
1. Master Template Generation (XLSX and CSV) with exact column order and instructions.
2. Excel / CSV File Parsing and Multi-Rule Validation.
3. In-File and Database Duplicate Detection with Multi-Location Support.
4. Validation Error Report Generation (CSV).
5. Atomic Bulk Import & Bulk Assignment to Operations with Rollback & Idempotency.
"""
import csv
import io
import re
import sys
import time
import uuid
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any, Dict, List, Optional, Set, Tuple

# Enable large CSV field handling across Windows and Mac exports
try:
    csv.field_size_limit(10 * 1024 * 1024)
except Exception:
    pass

import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models.client import ClientMaster
from app.models.company import Company
from app.models.sales_order import SalesOrder
from app.models.service import ServiceMaster
from app.models.user import User
from app.schemas.sales_import import (
    SalesImportExecuteRequest,
    SalesImportExecuteResponse,
    SalesImportPreviewResponse,
    SalesImportRowValidation,
)
from app.schemas.sales_order import SalesOrderCreate
from app.services import operation_service, permissions, sales_service

# Exact required business columns in required order
TEMPLATE_COLUMNS: List[str] = [
    "Sl No",
    "Location",
    "Client Name",
    "Contact",
    "Source",
    "Work",
    "Total Amount",
    "Advance Amount",
    "Incidental Cost",
]

ALLOWED_LEAD_SOURCES: Set[str] = {
    "WEBSITE",
    "REFERRAL",
    "DIRECT",
    "JUSTDIAL",
    "INDIAMART",
    "OTHERS",
}

MAX_FILE_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB limit
MAX_ROW_LIMIT: int = 500  # Sensible batch limit for fast atomic execution

# In-memory idempotency cache: { idempotency_key: (timestamp, SalesImportExecuteResponse) }
_IDEMPOTENCY_CACHE: Dict[str, Tuple[float, SalesImportExecuteResponse]] = {}
IDEMPOTENCY_EXPIRY_SECONDS: float = 600.0  # 10 minutes cache window


def _clean_idempotency_cache() -> None:
    """Evict expired idempotency keys."""
    now = time.time()
    expired = [k for k, (ts, _) in _IDEMPOTENCY_CACHE.items() if now - ts > IDEMPOTENCY_EXPIRY_SECONDS]
    for k in expired:
        _IDEMPOTENCY_CACHE.pop(k, None)


def _normalize_header(name: str) -> str:
    """Normalize column header for robust case-insensitive comparison."""
    return re.sub(r"[^a-z0-9]", "", str(name).strip().lower())


def _normalize_phone(val: Any) -> str:
    """Clean phone value while strictly preserving text digits and leading zeros."""
    if val is None:
        return ""
    s = str(val).strip()
    # If float string like '9876543210.0', strip trailing .0
    if s.endswith(".0") and s[:-2].isdigit():
        s = s[:-2]
    # Remove spacing, dashes, and parentheses for length validation
    return s


def is_example_row(sl_no: Any, client_name: Any) -> bool:
    """Determine if a row is a template example / instruction row that should not be imported."""
    sl_str = str(sl_no or "").strip().upper()
    client_str = str(client_name or "").strip().upper()
    if sl_str.startswith("[EXAMPLE]") or "EXAMPLE" in sl_str or sl_str.startswith("EX-"):
        return True
    if client_str.startswith("[EXAMPLE]") or "EXAMPLE" in client_str or "SAMPLE" in client_str:
        return True
    return False


def generate_master_template_xlsx(session: Optional[Session] = None) -> bytes:
    """Generate professional Excel (.xlsx) master import template with instructions & styled example rows."""
    wb = openpyxl.Workbook()

    # Sheet 1: Main Template
    ws = wb.active
    ws.title = "Sales_Import_Template"

    # Header styling
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="1E40AF", end_color="1E40AF", fill_type="solid")  # Indigo/Navy
    center_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
    left_align = Alignment(horizontal="left", vertical="center")
    right_align = Alignment(horizontal="right", vertical="center")
    thin_border = Border(
        left=Side(style="thin", color="CBD5E1"),
        right=Side(style="thin", color="CBD5E1"),
        top=Side(style="thin", color="CBD5E1"),
        bottom=Side(style="thin", color="CBD5E1"),
    )

    # Write Headers
    ws.row_dimensions[1].height = 28
    for col_idx, col_name in enumerate(TEMPLATE_COLUMNS, start=1):
        cell = ws.cell(row=1, column=col_idx, value=col_name)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = center_align
        cell.border = thin_border

    # Pre-create 50 formatted empty data rows with thin borders so Apple Numbers,
    # Excel, and Sheets display a visible, ready-to-type table grid below the header.
    data_font = Font(name="Calibri", size=11, color="1E293B")
    left_align = Alignment(horizontal="left", vertical="center")
    right_align = Alignment(horizontal="right", vertical="center")

    for r in range(2, 52):
        ws.row_dimensions[r].height = 22
        for col_idx in range(1, len(TEMPLATE_COLUMNS) + 1):
            cell = ws.cell(row=r, column=col_idx)
            cell.font = data_font
            cell.border = thin_border
            if col_idx == 4:  # Contact: Text format to preserve leading zeros
                cell.number_format = "@"
                cell.alignment = left_align
            elif col_idx in (7, 8, 9):  # Amounts (Total Amount, Advance Amount, Incidental Cost)
                cell.number_format = "#,##0.00"
                cell.alignment = right_align
            elif col_idx == 1:
                cell.alignment = center_align
            else:
                cell.alignment = left_align

    # Extend text formatting for Contact column up to row 500
    for r in range(52, 501):
        ws.cell(row=r, column=4).number_format = "@"

    # Auto-fit column widths
    column_widths = {
        "A": 16,  # Sl No
        "B": 28,  # Location
        "C": 35,  # Client Name
        "D": 20,  # Contact
        "E": 16,  # Source
        "F": 38,  # Work
        "G": 18,  # Total Amount
        "H": 18,  # Advance Amount
        "I": 18,  # Incidental Cost
    }
    for col_letter, width in column_widths.items():
        ws.column_dimensions[col_letter].width = width

    # Sheet 2: Instructions & Masters Lookup
    ws_inst = wb.create_sheet(title="Instructions")
    ws_inst.row_dimensions[1].height = 26
    inst_header = ws_inst.cell(row=1, column=1, value="GoCompliance Bulk Sales Import — Guide & Rules")
    inst_header.font = Font(name="Calibri", size=14, bold=True, color="1E3A8A")

    instructions_text = [
        ("1. Exact Columns", "Do not add, remove, or reorder column headers in 'Sales_Import_Template'."),
        ("2. Sl No", "A sequential tracking reference (e.g. 1, 2, 3). Used for validation and error reporting."),
        ("3. Location", "City / branch / outlet (e.g. 'Delhi South Ext', 'Whitefield Bangalore'). Supports multi-location orders for the same client."),
        ("4. Client Name", "Required client or corporate entity name (up to 200 characters)."),
        ("5. Contact", "Client phone number. Stored as text to ensure leading zeros (e.g. '09876543210') are never truncated."),
        ("6. Source", "Allowed values: WEBSITE, REFERRAL, DIRECT, JUSTDIAL, INDIAMART, OTHERS (case-insensitive)."),
        ("7. Work", "Exact Service / License Name matching the CRM Service Master."),
        ("8. Total Amount", "Total order contract amount in INR. Must be a valid positive number (e.g. 15000.00)."),
        ("9. Advance Amount", "Upfront payment received from client (e.g. 5000.00). Cannot exceed Total Amount. Leave blank or 0 if no advance received."),
        ("10. Incidental Cost", "Incidental / expense cost in INR. Must be non-negative and less than or equal to Total Amount."),
        ("11. Example Rows", "Rows starting with '[EXAMPLE]' are sample rows and will automatically be ignored during import."),
    ]

    for idx, (title, desc) in enumerate(instructions_text, start=3):
        t_cell = ws_inst.cell(row=idx, column=1, value=title)
        t_cell.font = Font(name="Calibri", size=11, bold=True, color="0F172A")
        d_cell = ws_inst.cell(row=idx, column=2, value=desc)
        d_cell.font = Font(name="Calibri", size=11, color="334155")

    ws_inst.column_dimensions["A"].width = 24
    ws_inst.column_dimensions["B"].width = 90

    # If session provided, add active services reference list to Instructions sheet
    if session:
        active_services = (
            session.execute(
                select(ServiceMaster.service_name, ServiceMaster.service_code)
                .where(ServiceMaster.status == "ACTIVE")
                .order_by(ServiceMaster.service_name.asc())
            )
            .all()
        )
        if active_services:
            srv_start = len(instructions_text) + 5
            srv_title = ws_inst.cell(row=srv_start, column=1, value="Active Services / Work Master (Reference)")
            srv_title.font = Font(name="Calibri", size=12, bold=True, color="1E3A8A")

            ws_inst.cell(row=srv_start + 1, column=1, value="Service Name").font = Font(bold=True)
            ws_inst.cell(row=srv_start + 1, column=2, value="Service Code").font = Font(bold=True)

            for s_idx, (s_name, s_code) in enumerate(active_services, start=srv_start + 2):
                ws_inst.cell(row=s_idx, column=1, value=s_name)
                ws_inst.cell(row=s_idx, column=2, value=s_code or "—")

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output.getvalue()


def generate_master_template_csv() -> bytes:
    """Generate standard CSV master import template with headers only."""
    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")

    # Header Row
    writer.writerow(TEMPLATE_COLUMNS)

    return output.getvalue().encode("utf-8")


def parse_and_validate_sales_file(
    file_bytes: bytes,
    filename: str,
    current_user: User,
    session: Session,
    apply_gst: bool = False,
) -> SalesImportPreviewResponse:
    """Parse Excel or CSV sales file and execute comprehensive validation checks.

    Validates:
    - File size and format (.xlsx, .csv).
    - Header columns and order.
    - Required fields, character lengths, numeric constraints.
    - Source against allowed values.
    - Work against active ServiceMaster (case-insensitive name or code).
    - Preserves contact phone text and leading zeros.
    - Identifies duplicates in file and against active database sales orders.
    - Supports legitimate multi-location orders for same client & contact.
    """
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise ValueError(
            f"File size ({len(file_bytes) / (1024 * 1024):.1f} MB) exceeds maximum allowed limit of {MAX_FILE_SIZE_BYTES // (1024 * 1024)} MB."
        )

    lower_filename = filename.lower()
    raw_rows: List[List[Any]] = []

    if lower_filename.endswith(".xlsx"):
        try:
            wb = openpyxl.load_workbook(io.BytesIO(file_bytes), data_only=True)
        except Exception as exc:
            raise ValueError(f"Failed to read Excel file: {str(exc)}") from exc

        # Search all sheets to find the one containing matching sales template headers
        sheet_names = wb.sheetnames
        target_ws = None
        for sname in sheet_names:
            candidate_ws = wb[sname]
            first_rows = [list(r) for r in candidate_ws.iter_rows(max_row=5, values_only=True)]
            found_header = False
            for r in first_rows:
                r_norms = [_normalize_header(c) for c in r if c]
                if any(v in r_norms for v in ["clientname", "client"]) and any(v in r_norms for v in ["contact", "contactno", "phone"]):
                    found_header = True
                    break
            if found_header:
                target_ws = candidate_ws
                break

        if target_ws is None:
            target_sheet_name = "Sales_Import_Template" if "Sales_Import_Template" in sheet_names else sheet_names[0]
            target_ws = wb[target_sheet_name]

        for row in target_ws.iter_rows(values_only=True):
            raw_rows.append(list(row))
    elif lower_filename.endswith(".csv"):
        try:
            # Multi-encoding decode with fallback for Windows (cp1252), Mac, and UTF-8
            decoded_text = None
            for enc in ["utf-8-sig", "utf-8", "cp1252", "latin-1"]:
                try:
                    decoded_text = file_bytes.decode(enc)
                    break
                except (UnicodeDecodeError, LookupError):
                    continue
            if decoded_text is None:
                decoded_text = file_bytes.decode("latin-1", errors="replace")

            # Universal newline normalization:
            # Replaces Mac carriage returns (\r) and Windows returns (\r\n) with standard \n.
            # Strips null bytes if any. Completely resolves 'new-line character seen in unquoted field'.
            normalized_text = decoded_text.replace("\x00", "").replace("\r\n", "\n").replace("\r", "\n")

            # Auto-detect delimiter: comma, semicolon, or tab
            delimiter = ","
            first_line = normalized_text.split("\n", 1)[0]
            if ";" in first_line and first_line.count(";") >= 4:
                delimiter = ";"
            elif "\t" in first_line and first_line.count("\t") >= 4:
                delimiter = "\t"

            reader = csv.reader(io.StringIO(normalized_text, newline=""), delimiter=delimiter)
            for row in reader:
                raw_rows.append(row)
        except Exception as exc:
            raise ValueError(f"Failed to parse CSV file: {str(exc)}") from exc
    elif lower_filename.endswith(".numbers"):
        import os
        import tempfile
        try:
            from numbers_parser import Document
        except ImportError:
            raise ValueError("Apple Numbers (.numbers) support library is not available.")

        with tempfile.NamedTemporaryFile(suffix=".numbers", delete=False) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name

        try:
            doc = Document(tmp_path)
            found_rows: List[List[Any]] = []
            for sheet in doc.sheets:
                for table in sheet.tables:
                    t_rows = [[c.value for c in row] for row in table.rows()]
                    for r in t_rows[:5]:
                        r_norms = [_normalize_header(c) for c in r if c is not None]
                        if any(v in r_norms for v in ["clientname", "client"]) and any(v in r_norms for v in ["contact", "contactno", "phone"]):
                            found_rows = t_rows
                            break
                    if found_rows:
                        break
                if found_rows:
                    break

            if not found_rows and doc.sheets and doc.sheets[0].tables:
                found_rows = [[c.value for c in row] for row in doc.sheets[0].tables[0].rows()]

            raw_rows = found_rows
        except Exception as exc:
            raise ValueError(f"Failed to parse Apple Numbers (.numbers) file: {str(exc)}") from exc
        finally:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass
    else:
        raise ValueError(f"Unsupported file format '{filename}'. Only .xlsx, .csv, and .numbers files are supported.")

    if not raw_rows:
        raise ValueError("The uploaded file is empty.")

    # 1. Header Row Extraction and Validation
    expected_norm_map = {
        "slno": ["slno", "sl", "serialno", "sno"],
        "location": ["location", "branch", "city"],
        "clientname": ["clientname", "client", "customername", "customer"],
        "contact": ["contact", "contactno", "phone", "phoneno", "mobile"],
        "source": ["source", "leadsource"],
        "work": ["work", "service", "servicename"],
        "totalamount": ["totalamount", "amount", "ordervalue", "value"],
        "incidentalcost": ["incidentalcost", "incidental", "incidentals"],
    }
    optional_norm_map = {
        "advanceamount": ["advanceamount", "advance", "advancereceived", "amountreceived", "advancepaid", "advamt", "advancepayment"],
    }

    # Search first 10 rows to locate the header row (handles table titles or blank lines added by Numbers/Excel)
    header_row_idx = None
    col_indices: Dict[str, int] = {}
    missing_columns: List[str] = []

    for r_idx in range(min(10, len(raw_rows))):
        candidate_row = [str(c or "").strip() for c in raw_rows[r_idx]]
        norm_to_idx: Dict[str, int] = {}
        for idx, col in enumerate(candidate_row):
            norm = _normalize_header(col)
            if norm and norm not in norm_to_idx:
                norm_to_idx[norm] = idx

        temp_indices: Dict[str, int] = {}
        temp_missing: List[str] = []
        for standard_col, variants in expected_norm_map.items():
            found_idx = None
            for v in variants:
                if v in norm_to_idx:
                    found_idx = norm_to_idx[v]
                    break
            if found_idx is not None:
                temp_indices[standard_col] = found_idx
            else:
                temp_missing.append(standard_col)

        # Check optional columns like advance amount
        for opt_col, variants in optional_norm_map.items():
            for v in variants:
                if v in norm_to_idx:
                    temp_indices[opt_col] = norm_to_idx[v]
                    break

        if len(temp_missing) == 0:
            header_row_idx = r_idx
            col_indices = temp_indices
            missing_columns = []
            break
        elif len(temp_indices) >= 5 and (header_row_idx is None or len(temp_indices) > len(col_indices)):
            header_row_idx = r_idx
            col_indices = temp_indices
            missing_columns = temp_missing

    if header_row_idx is None:
        header_row_idx = 0
        missing_columns = list(expected_norm_map.keys())

    if missing_columns:
        raise ValueError(
            f"Missing required columns in template: {', '.join(missing_columns)}. "
            f"Expected template headers in order: {', '.join(TEMPLATE_COLUMNS)}"
        )

    # 2. Pre-fetch Active Services and Allowed Sources for Fast Lookup
    active_services = (
        session.execute(
            select(ServiceMaster).where(ServiceMaster.status == "ACTIVE")
        )
        .scalars()
        .all()
    )
    service_by_name = {s.service_name.strip().lower(): s for s in active_services}
    service_by_code = {s.service_code.strip().lower(): s for s in active_services if s.service_code}

    # Tracking sets for duplicate detection
    seen_in_file: Dict[Tuple[str, str, str, str], int] = {}
    parsed_rows: List[SalesImportRowValidation] = []
    data_row_counter = 0

    # 3. Parse Data Rows
    for row_num, row_cells in enumerate(raw_rows[header_row_idx + 1:], start=header_row_idx + 2):
        # Extract row values
        def get_val(key: str) -> str:
            idx = col_indices.get(key)
            if idx is not None and idx < len(row_cells):
                val = row_cells[idx]
                return "" if val is None else str(val).strip()
            return ""

        sl_no_raw = get_val("slno")
        loc_raw = get_val("location")
        client_raw = get_val("clientname")
        contact_raw = get_val("contact")
        source_raw = get_val("source")
        work_raw = get_val("work")
        amt_raw = get_val("totalamount")
        adv_raw = get_val("advanceamount")
        inc_raw = get_val("incidentalcost")

        # Skip blank lines (if there is no client or order data)
        if not any([client_raw, contact_raw, source_raw, work_raw, amt_raw, adv_raw, inc_raw]):
            continue

        # Skip clearly marked example rows
        if is_example_row(sl_no_raw, client_raw):
            continue

        data_row_counter += 1
        if data_row_counter > MAX_ROW_LIMIT:
            raise ValueError(
                f"File contains more than {MAX_ROW_LIMIT} data rows. Please divide your file into batches of {MAX_ROW_LIMIT} rows or fewer."
            )

        row_errors: List[str] = []
        row_warnings: List[str] = []

        # Validate Sl No
        sl_no_val = sl_no_raw or str(data_row_counter)

        # Validate Location (optional, up to 200 chars)
        location_val = loc_raw.strip() if loc_raw else None
        if location_val and len(location_val) > 200:
            row_errors.append("Location exceeds maximum length of 200 characters.")

        # Validate Client Name (mandatory, up to 200 chars)
        client_name_val = client_raw.strip()
        if not client_name_val:
            row_errors.append("Client Name is required.")
        elif len(client_name_val) > 200:
            row_errors.append("Client Name exceeds maximum length of 200 characters.")

        # Validate Contact (mandatory, preserve text & leading zeros, min 7 digits, max 20)
        contact_val = _normalize_phone(contact_raw)
        if not contact_val:
            row_errors.append("Contact number is required.")
        else:
            clean_digits = re.sub(r"[\s\-\+\(\)]", "", contact_val)
            if not clean_digits.isdigit() or len(clean_digits) < 7 or len(clean_digits) > 20:
                row_errors.append(f"Invalid Contact number '{contact_val}'. Must contain between 7 and 20 digits.")

        # Validate Lead Source
        source_val = source_raw.strip().upper() if source_raw else ""
        if not source_val:
            row_errors.append("Source is required.")
        elif source_val not in ALLOWED_LEAD_SOURCES:
            row_errors.append(
                f"Invalid Source '{source_raw}'. Allowed sources: {', '.join(sorted(ALLOWED_LEAD_SOURCES))}."
            )

        # Validate Work / Service
        resolved_service: Optional[ServiceMaster] = None
        work_val = work_raw.strip()
        if not work_val:
            row_errors.append("Work (Service) is required.")
        else:
            work_lower = work_val.lower()
            resolved_service = service_by_name.get(work_lower) or service_by_code.get(work_lower)
            if not resolved_service:
                row_errors.append(
                    f"Work '{work_raw}' does not match any active service in the system. Check the Instructions tab for valid services."
                )

        # Validate Base Amount / Total Amount
        base_amount_val: Optional[Decimal] = None
        gst_amount_val: Decimal = Decimal("0.00")
        gst_rate_val: Decimal = Decimal("18.00") if apply_gst else Decimal("0.00")
        gst_invoice_req: bool = bool(apply_gst)
        total_amount_val: Optional[Decimal] = None

        if not amt_raw:
            row_errors.append("Total Amount is required.")
        else:
            try:
                # Strip currency symbols and commas if present
                clean_amt = re.sub(r"[₹,\s]", "", amt_raw)
                parsed_amt = Decimal(clean_amt)
                if parsed_amt < Decimal("0.00"):
                    row_errors.append("Total Amount cannot be negative.")
                else:
                    base_amount_val = parsed_amt
                    if apply_gst:
                        gst_amount_val = (base_amount_val * Decimal("0.18")).quantize(
                            Decimal("0.01"), rounding=ROUND_HALF_UP
                        )
                        total_amount_val = (base_amount_val + gst_amount_val).quantize(
                            Decimal("0.01"), rounding=ROUND_HALF_UP
                        )
                    else:
                        gst_amount_val = Decimal("0.00")
                        total_amount_val = base_amount_val
            except (InvalidOperation, ValueError):
                row_errors.append(f"Invalid Total Amount '{amt_raw}'. Must be a valid positive number.")

        # Validate Advance Amount (optional, defaults to 0.00, cannot be negative or exceed Total Amount)
        advance_amount_val: Decimal = Decimal("0.00")
        if adv_raw:
            try:
                clean_adv = re.sub(r"[₹,\s]", "", adv_raw)
                advance_amount_val = Decimal(clean_adv)
                if advance_amount_val < Decimal("0.00"):
                    row_errors.append("Advance Amount cannot be negative.")
                elif total_amount_val is not None and advance_amount_val > total_amount_val:
                    row_errors.append("Advance Amount cannot exceed Total Amount.")
            except (InvalidOperation, ValueError):
                row_errors.append(f"Invalid Advance Amount '{adv_raw}'. Must be a valid non-negative number.")

        # Validate Incidental Cost
        incidental_cost_val: Optional[Decimal] = Decimal("0.00")
        if inc_raw:
            try:
                clean_inc = re.sub(r"[₹,\s]", "", inc_raw)
                incidental_cost_val = Decimal(clean_inc)
                if incidental_cost_val < Decimal("0.00"):
                    row_errors.append("Incidental Cost cannot be negative.")
                elif total_amount_val is not None and incidental_cost_val > total_amount_val:
                    row_errors.append("Incidental Cost cannot exceed Total Amount.")
            except (InvalidOperation, ValueError):
                row_errors.append(f"Invalid Incidental Cost '{inc_raw}'. Must be a valid non-negative number.")

        # Duplicate detection within file
        is_dup_in_file = False
        is_dup_in_db = False

        if client_name_val and contact_val and work_val:
            # Key distinguishes Location so multi-location client orders are NOT false-flagged!
            file_dup_key = (
                client_name_val.lower(),
                re.sub(r"[\s\-\+\(\)]", "", contact_val),
                (location_val or "").lower(),
                work_val.lower(),
            )
            if file_dup_key in seen_in_file:
                is_dup_in_file = True
                first_seen_row = seen_in_file[file_dup_key]
                row_warnings.append(
                    f"Duplicate row in file: identical to Row {first_seen_row} (Client, Contact, Location, and Work)."
                )
            else:
                seen_in_file[file_dup_key] = row_num

            # Duplicate check against existing active database records
            if resolved_service and not row_errors:
                company_filter = current_user.company_id
                query = (
                    select(SalesOrder.order_number)
                    .join(ClientMaster, SalesOrder.client_id == ClientMaster.client_id)
                    .where(
                        func.lower(ClientMaster.client_name) == client_name_val.lower(),
                        ClientMaster.contact_phone == re.sub(r"[\s\-\+\(\)]", "", contact_val),
                        SalesOrder.service_id == resolved_service.service_id,
                        func.lower(func.coalesce(SalesOrder.location, "")) == (location_val or "").lower(),
                        SalesOrder.confirmation_status != "CANCELLED",
                        SalesOrder.deleted_at.is_(None),
                    )
                )
                if company_filter and not permissions.is_super_admin_user(session, current_user):
                    query = query.where(SalesOrder.company_id == company_filter)

                existing_order_num = session.execute(query).scalars().first()
                if existing_order_num:
                    is_dup_in_db = True
                    row_warnings.append(
                        f"Potential duplicate: Order '{existing_order_num}' already exists in CRM for this Client, Contact, Location, and Work."
                    )

        parsed_rows.append(
            SalesImportRowValidation(
                row_number=row_num,
                sl_no=sl_no_val,
                location=location_val,
                client_name=client_name_val or None,
                contact=contact_val or None,
                source=source_val or None,
                work=work_val or None,
                base_amount=base_amount_val,
                gst_amount=gst_amount_val,
                gst_rate=gst_rate_val,
                gst_invoice_required=gst_invoice_req,
                total_amount=total_amount_val,
                advance_amount=advance_amount_val,
                incidental_cost=incidental_cost_val,
                service_id=resolved_service.service_id if resolved_service else None,
                service_name=resolved_service.service_name if resolved_service else None,
                is_valid=(len(row_errors) == 0),
                is_duplicate_in_file=is_dup_in_file,
                is_duplicate_in_db=is_dup_in_db,
                errors=row_errors,
                warnings=row_warnings,
            )
        )

    if not parsed_rows:
        raise ValueError(
            "The uploaded file contains no customer entries. "
            "Please open the template, enter at least 1 sales record (Client Name, Contact, Work, Total Amount), and upload again."
        )

    valid_count = sum(1 for r in parsed_rows if r.is_valid)
    error_count = sum(1 for r in parsed_rows if not r.is_valid)
    dup_count = sum(1 for r in parsed_rows if (r.is_duplicate_in_file or r.is_duplicate_in_db))
    can_import = len(parsed_rows) > 0 and error_count == 0
    valid_base_total = sum((r.base_amount for r in parsed_rows if r.is_valid and r.base_amount is not None), Decimal("0.00"))
    valid_gst_total = sum((r.gst_amount for r in parsed_rows if r.is_valid and r.gst_amount is not None), Decimal("0.00"))

    return SalesImportPreviewResponse(
        filename=filename,
        total_rows=len(parsed_rows),
        valid_rows_count=valid_count,
        error_rows_count=error_count,
        duplicate_warnings_count=dup_count,
        can_import=can_import,
        apply_gst=apply_gst,
        total_base_amount=valid_base_total,
        total_gst_amount=valid_gst_total,
        rows=parsed_rows,
    )


def generate_validation_error_csv(rows: List[SalesImportRowValidation]) -> bytes:
    """Generate a downloadable CSV containing detailed row-specific error and warning reports."""
    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")

    writer.writerow([
        "Row Number",
        "Sl No",
        "Location",
        "Client Name",
        "Contact",
        "Source",
        "Work",
        "Total Amount",
        "Advance Amount",
        "Incidental Cost",
        "Status",
        "Errors",
        "Warnings",
    ])

    for r in rows:
        status_text = "VALID" if r.is_valid else "ERROR"
        err_text = " | ".join(r.errors) if r.errors else "None"
        warn_text = " | ".join(r.warnings) if r.warnings else "None"
        writer.writerow([
            r.row_number,
            r.sl_no or "",
            r.location or "",
            r.client_name or "",
            r.contact or "",
            r.source or "",
            r.work or "",
            f"{r.total_amount:.2f}" if r.total_amount is not None else "",
            f"{r.advance_amount:.2f}" if getattr(r, "advance_amount", None) is not None else "0.00",
            f"{r.incidental_cost:.2f}" if r.incidental_cost is not None else "",
            status_text,
            err_text,
            warn_text,
        ])

    return output.getvalue().encode("utf-8")


def execute_bulk_sales_import(
    session: Session,
    current_user: User,
    data: SalesImportExecuteRequest,
) -> SalesImportExecuteResponse:
    """Atomically import validated sales records and assign each to the chosen Operations assignee.

    Features:
    - Server-side Idempotency check to prevent duplicate batches.
    - Strict assignee verification against existing eligibility and RBAC rules.
    - All-or-nothing database transaction rollback on any failure.
    - Native integration with existing confirm_sales_order & Operations assignment workflow.
    - Preserves contact phone text, leading zeros, and multi-location integrity.
    """
    _clean_idempotency_cache()

    # 1. Idempotency Check
    if data.idempotency_key:
        cached_entry = _IDEMPOTENCY_CACHE.get(data.idempotency_key)
        if cached_entry:
            _, cached_response = cached_entry
            return cached_response

    # 2. Assignee Verification
    stmt = (
        select(User)
        .options(
            joinedload(User.company),
            joinedload(User.department),
            joinedload(User.designation),
        )
        .where(User.user_id == data.assignee_user_id)
    )
    assignee = session.execute(stmt).scalars().first()
    if not assignee:
        raise ValueError("Selected Operations assignee was not found in the employee master.")

    if assignee.account_status != "ACTIVE":
        raise ValueError(
            f"Selected Operations assignee '{assignee.first_name} {assignee.last_name}' is inactive."
        )

    # Check company scope if actor is not super admin
    is_super = permissions.is_super_admin_user(session, current_user)
    if not is_super and current_user.company_id and assignee.company_id != current_user.company_id:
        raise ValueError("Selected Operations assignee does not belong to your authorized company.")

    # Strict check against disallowed roles (Sales, Admin, Director without Ops permissions)
    if operation_service.is_disallowed_ops_assignee(assignee, session):
        raise ValueError(
            f"Selected employee '{assignee.first_name} {assignee.last_name}' ({assignee.employee_code}) is not eligible for Operations task assignment."
        )

    dept_name = (assignee.department.department_name.lower() if assignee.department and assignee.department.department_name else "")
    dept_code = (assignee.department.department_code.upper() if assignee.department and assignee.department.department_code else "")
    is_ops_dept = "operat" in dept_name or "operat" in dept_code or dept_code in ("OP", "OPS", "OPERATIONS")
    has_ops_perm = permissions.has_permission(session, assignee, "OPERATIONS", "view")
    is_assignee_super = permissions.is_super_admin_user(session, assignee)

    if not (is_ops_dept or has_ops_perm or is_assignee_super):
        raise ValueError(
            f"Selected employee '{assignee.first_name} {assignee.last_name}' ({assignee.employee_code}) is not eligible for Operations task assignment."
        )

    # 3. Payload Pre-Validation
    if not data.rows:
        raise ValueError("No sales rows provided for bulk import.")

    invalid_rows = [r.row_number for r in data.rows if not r.is_valid]
    if invalid_rows:
        raise ValueError(
            f"Cannot import batch with validation errors on row(s): {invalid_rows}. Please correct and re-upload."
        )

    if not data.allow_duplicates:
        duplicate_rows = [r.row_number for r in data.rows if r.is_duplicate_in_file or r.is_duplicate_in_db]
        if duplicate_rows:
            raise ValueError(
                f"Batch contains duplicate warnings on row(s): {duplicate_rows}. Please confirm 'Allow Duplicates' if these are legitimate multi-order entries."
            )

    # 4. Atomic Database Transaction
    created_orders: List[SalesOrder] = []
    order_numbers: List[str] = []

    # Use a savepoint / nested transaction or rely on caller commit/rollback
    try:
        authoritative_company_id = current_user.company_id or assignee.company_id
        if not authoritative_company_id:
            # Fallback to active company in DB
            authoritative_company_id = session.execute(
                select(Company.company_id).where(Company.status == "ACTIVE")
            ).scalar()

        today = date.today()

        active_services = (
            session.execute(
                select(ServiceMaster).where(ServiceMaster.status == "ACTIVE")
            )
            .scalars()
            .all()
        )
        service_by_id = {s.service_id: s for s in active_services}
        service_by_name = {s.service_name.strip().lower(): s for s in active_services}
        service_by_code = {s.service_code.strip().lower(): s for s in active_services if s.service_code}

        for row in data.rows:
            target_service_id = row.service_id
            if not target_service_id and row.work:
                w_lower = row.work.strip().lower()
                matched_svc = service_by_name.get(w_lower) or service_by_code.get(w_lower)
                if matched_svc:
                    target_service_id = matched_svc.service_id

            if not target_service_id:
                raise ValueError(
                    f"Row {row.row_number}: Service '{row.work or 'Unknown'}' is not recognized as an active service."
                )

            c_name = row.client_name.strip()
            raw_phone = row.contact.strip() if row.contact else ""
            clean_phone = re.sub(r"[\s\-\+\(\)]", "", raw_phone)

            # Deduplicate or create ClientMaster
            matched_client = None
            if clean_phone:
                matched_client = session.execute(
                    select(ClientMaster).where(
                        ClientMaster.company_id == authoritative_company_id,
                        func.lower(ClientMaster.client_name) == func.lower(c_name),
                        ClientMaster.contact_phone == clean_phone,
                    )
                ).scalars().first()

            if not matched_client:
                matched_client = session.execute(
                    select(ClientMaster).where(
                        ClientMaster.company_id == authoritative_company_id,
                        func.lower(ClientMaster.client_name) == func.lower(c_name),
                    )
                ).scalars().first()

            if matched_client:
                client = matched_client
                if clean_phone and not matched_client.contact_phone:
                    matched_client.contact_phone = clean_phone
            else:
                client = ClientMaster(
                    client_id=uuid.uuid4(),
                    company_id=authoritative_company_id,
                    client_name=c_name,
                    contact_person=c_name,
                    contact_email=f"{clean_phone}@client.crm" if clean_phone else "",
                    contact_phone=clean_phone or "0000000000",
                    entity_type="INDIVIDUAL",
                    created_by_user_id=current_user.user_id,
                    status="ACTIVE",
                )
                session.add(client)
                session.flush()

            # Generate SalesOrder
            order_num = sales_service.generate_sales_order_number(session, today)

            # Determine if 18% GST calculation applies
            is_gst = bool(data.apply_gst or getattr(row, "gst_invoice_required", False))
            base_val = Decimal(str(row.base_amount or row.total_amount or "0.00"))

            if is_gst:
                gst_rate = Decimal("18.00")
                gst_amt = (base_val * Decimal("0.18")).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
                tot_amt = (base_val + gst_amt).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
                gst_req = True
            else:
                tot_amt = Decimal(str(row.total_amount or base_val or "0.00"))
                gst_req = False

            adv_amt = Decimal(str(getattr(row, "advance_amount", 0) or "0.00"))
            inc_cost = Decimal(str(row.incidental_cost or "0.00"))
            bal_amt = max(Decimal("0.00"), tot_amt - adv_amt)
            profit = tot_amt - inc_cost

            if adv_amt >= tot_amt and tot_amt > Decimal("0.00"):
                pmt_status = "FULLY_PAID"
            elif adv_amt > Decimal("0.00"):
                pmt_status = "PARTIALLY_PAID"
            else:
                pmt_status = "PENDING"

            order = SalesOrder(
                order_number=order_num,
                company_id=authoritative_company_id,
                client_id=client.client_id,
                service_id=target_service_id,
                salesperson_user_id=current_user.user_id,
                lead_source=row.source.upper() if row.source else "DIRECT",
                location=row.location.strip() if row.location else None,
                order_date=today,
                order_value=tot_amt,
                amount_received=adv_amt,
                balance_amount=bal_amt,
                govt_fees=Decimal("0.00"),
                incidental_cost=inc_cost,
                profit_amount=profit,
                payment_status=pmt_status,
                confirmation_status="DRAFT",
                gst_invoice_required=gst_req,
                notes=f"Bulk imported on {today.isoformat()} (Ref: Sl No {row.sl_no or row.row_number})",
            )
            session.add(order)
            session.flush()

            # Confirm and Assign to Operations assignee
            sales_service.confirm_sales_order(
                session=session,
                order_id=order.order_id,
                current_user=current_user,
                assignee_user_id=assignee.user_id,
            )

            created_orders.append(order)
            order_numbers.append(order.order_number)

        # Commit entire atomic batch
        session.commit()

    except Exception as exc:
        session.rollback()
        raise exc

    response = SalesImportExecuteResponse(
        success=True,
        imported_count=len(created_orders),
        assignments_count=len(created_orders),
        order_numbers=order_numbers,
        message=f"Successfully imported and assigned {len(created_orders)} sales orders to {assignee.first_name} {assignee.last_name} ({assignee.employee_code}).",
    )

    if data.idempotency_key:
        _IDEMPOTENCY_CACHE[data.idempotency_key] = (time.time(), response)

    return response
