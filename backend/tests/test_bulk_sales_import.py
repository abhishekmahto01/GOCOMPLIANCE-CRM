"""Automated test suite for Stage 2: Bulk Sales Import (Excel/CSV) with Bulk Operations Assignment.

Covers all 40 mandatory test cases across Categories A, B, C, D, and E:
- A. Template and file handling (1-8)
- B. Sales record validation (9-19)
- C. Bulk Operations assignment (20-27)
- D. Database integrity and financial calculations (28-35)
- E. Regression and permissions (36-40)
"""
import csv
import io
import os
import uuid
from decimal import Decimal
from typing import List

os.environ.setdefault("PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION", "python")

import openpyxl
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.client import ClientMaster
from app.models.operation_application import (
    ApplicationAssignmentHistory,
    OperationApplication,
)
from app.models.sales_order import SalesOrder
from app.models.user import User
from app.schemas.sales_import import (
    SalesImportExecuteRequest,
    SalesImportRowValidation,
)
from app.services import sales_import_service
from tests.test_gst_invoice_routing import auth_header, routing_fixture


def make_xlsx_bytes(headers: List[str], rows: List[List]) -> bytes:
    """Helper to construct XLSX file in memory."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Sales_Import_Template"
    ws.append(headers)
    for r in rows:
        ws.append(r)
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def make_csv_bytes(headers: List[str], rows: List[List]) -> bytes:
    """Helper to construct CSV file in memory."""
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerow(headers)
    for r in rows:
        writer.writerow(r)
    return buf.getvalue().encode("utf-8")


class TestBulkSalesImport:
    """Test suite covering 40 test cases for Bulk Sales Import & Assignment."""

    # -------------------------------------------------------------
    # SECTION A: Template and File Handling (Test Cases 1 - 8)
    # -------------------------------------------------------------

    def test_case_1_xlsx_template_download_success(self, client: TestClient, routing_fixture: dict):
        """Case 1: XLSX master template downloads successfully."""
        sales_user = routing_fixture["sales_user"]
        resp = client.get("/api/sales/import/template/xlsx", headers=auth_header(sales_user))
        assert resp.status_code == 200
        assert "spreadsheetml" in resp.headers["content-type"]
        assert len(resp.content) > 0
        wb = openpyxl.load_workbook(io.BytesIO(resp.content))
        assert "Sales_Import_Template" in wb.sheetnames
        assert "Instructions" in wb.sheetnames

    def test_case_2_csv_template_download_success(self, client: TestClient, routing_fixture: dict):
        """Case 2: CSV master template downloads successfully."""
        sales_user = routing_fixture["sales_user"]
        resp = client.get("/api/sales/import/template/csv", headers=auth_header(sales_user))
        assert resp.status_code == 200
        assert "text/csv" in resp.headers["content-type"]
        assert len(resp.content) > 0

    def test_case_3_both_templates_contain_exact_headers_in_order(self, client: TestClient, routing_fixture: dict):
        """Case 3: Both templates contain correct column headers in specified business order."""
        expected_headers = [
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
        sales_user = routing_fixture["sales_user"]

        # 1. XLSX
        resp_xlsx = client.get("/api/sales/import/template/xlsx", headers=auth_header(sales_user))
        wb = openpyxl.load_workbook(io.BytesIO(resp_xlsx.content))
        ws = wb["Sales_Import_Template"]
        xlsx_headers = [cell.value for cell in ws[1]]
        assert xlsx_headers == expected_headers

        # 2. CSV
        resp_csv = client.get("/api/sales/import/template/csv", headers=auth_header(sales_user))
        reader = csv.reader(io.StringIO(resp_csv.content.decode("utf-8")))
        csv_headers = next(reader)
        assert csv_headers == expected_headers

    def test_case_4_valid_xlsx_parsed_correctly(self, client: TestClient, routing_fixture: dict):
        """Case 4: Valid XLSX upload is parsed correctly."""
        sales_user = routing_fixture["sales_user"]
        service = routing_fixture["service"]
        headers = sales_import_service.TEMPLATE_COLUMNS
        rows = [
            ["1", "Indiranagar, Bangalore", "Zenith Retail Corp", "09876543210", "WEBSITE", service.service_name, 12000.00, 3000.00, 200.00],
        ]
        file_bytes = make_xlsx_bytes(headers, rows)
        resp = client.post(
            "/api/sales/import/preview",
            files={"file": ("orders.xlsx", file_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            headers=auth_header(sales_user),
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["total_rows"] == 1
        assert data["valid_rows_count"] == 1
        assert data["error_rows_count"] == 0
        assert data["can_import"] is True
        assert data["rows"][0]["client_name"] == "Zenith Retail Corp"
        assert data["rows"][0]["contact"] == "09876543210"
        assert float(data["rows"][0]["advance_amount"]) == 3000.00

    def test_case_5_valid_csv_parsed_correctly(self, client: TestClient, routing_fixture: dict):
        """Case 5: Valid CSV upload is parsed correctly."""
        sales_user = routing_fixture["sales_user"]
        service = routing_fixture["service"]
        headers = sales_import_service.TEMPLATE_COLUMNS
        rows = [
            ["1", "Connaught Place, Delhi", "Apex Logistics Ltd", "08888777766", "DIRECT", service.service_name, "18500.00", "5000.00", "500.00"],
        ]
        file_bytes = make_csv_bytes(headers, rows)
        resp = client.post(
            "/api/sales/import/preview",
            files={"file": ("orders.csv", file_bytes, "text/csv")},
            headers=auth_header(sales_user),
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["total_rows"] == 1
        assert data["valid_rows_count"] == 1
        assert data["error_rows_count"] == 0

        # Also verify Mac CR (\r) newline support (Apple Numbers export)
        mac_csv_content = f"{','.join(headers)}\r1,Mumbai,Mac User Corp,9876543210,DIRECT,{service.service_name},10000.00,2000.00,0.00\r"
        resp_mac = client.post(
            "/api/sales/import/preview",
            files={"file": ("mac_orders.csv", mac_csv_content.encode("utf-8"), "text/csv")},
            headers=auth_header(sales_user),
        )
        assert resp_mac.status_code == 200, resp_mac.text
        assert resp_mac.json()["valid_rows_count"] == 1

    def test_case_6_missing_required_columns_produce_clear_validation_error(self, client: TestClient, routing_fixture: dict):
        """Case 6: Missing required columns produce a clear validation error."""
        sales_user = routing_fixture["sales_user"]
        # Missing 'Total Amount' and 'Work'
        bad_headers = ["Sl No", "Location", "Client Name", "Contact", "Source", "Incidental Cost"]
        rows = [["1", "Delhi", "Acme", "9999900001", "DIRECT", "0.00"]]
        file_bytes = make_csv_bytes(bad_headers, rows)
        resp = client.post(
            "/api/sales/import/preview",
            files={"file": ("missing_cols.csv", file_bytes, "text/csv")},
            headers=auth_header(sales_user),
        )
        assert resp.status_code == 400
        assert "Missing required columns" in resp.json()["detail"]

    def test_case_7_malformed_empty_oversized_unsupported_files_rejected(self, client: TestClient, routing_fixture: dict):
        """Case 7: Malformed, empty, oversized, or unsupported files are rejected safely."""
        sales_user = routing_fixture["sales_user"]

        # Empty file
        resp = client.post(
            "/api/sales/import/preview",
            files={"file": ("empty.csv", b"", "text/csv")},
            headers=auth_header(sales_user),
        )
        assert resp.status_code == 400
        assert "empty" in resp.json()["detail"].lower()

        # Unsupported format (PDF)
        resp = client.post(
            "/api/sales/import/preview",
            files={"file": ("doc.pdf", b"%PDF-1.4 ...", "application/pdf")},
            headers=auth_header(sales_user),
        )
        assert resp.status_code == 400
        assert "unsupported" in resp.json()["detail"].lower()

        # Malformed Excel bytes
        resp = client.post(
            "/api/sales/import/preview",
            files={"file": ("corrupt.xlsx", b"not an excel file", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            headers=auth_header(sales_user),
        )
        assert resp.status_code == 400

    def test_case_8_example_rows_cannot_accidentally_become_real_sales(self, client: TestClient, routing_fixture: dict):
        """Case 8: Example rows in XLSX template cannot accidentally become real sales entries."""
        sales_user = routing_fixture["sales_user"]
        service = routing_fixture["service"]
        headers = sales_import_service.TEMPLATE_COLUMNS
        rows = [
            ["[EXAMPLE] 1", "Delhi", "Example Client A", "9999900001", "DIRECT", service.service_name, 10000.00, 0.00, 0.00],
            ["[EXAMPLE] 2", "Mumbai", "Sample Client B", "9999900002", "WEBSITE", service.service_name, 15000.00, 1000.00, 500.00],
            ["1", "Chennai", "Real Client", "09876543210", "DIRECT", service.service_name, 20000.00, 5000.00, 100.00],
        ]
        file_bytes = make_xlsx_bytes(headers, rows)
        resp = client.post(
            "/api/sales/import/preview",
            files={"file": ("template_with_examples.xlsx", file_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            headers=auth_header(sales_user),
        )
        assert resp.status_code == 200
        data = resp.json()
        # The 2 example rows must be completely filtered out; only Real Client should be parsed!
        assert data["total_rows"] == 1
        assert data["rows"][0]["client_name"] == "Real Client"

    # -------------------------------------------------------------
    # SECTION B: Sales Record Validation (Test Cases 9 - 19)
    # -------------------------------------------------------------

    def test_case_9_multiple_locations_preview_correct(self, client: TestClient, routing_fixture: dict):
        """Case 9: A valid file containing multiple locations produces the correct preview."""
        sales_user = routing_fixture["sales_user"]
        service = routing_fixture["service"]
        headers = sales_import_service.TEMPLATE_COLUMNS
        rows = [
            ["1", "Delhi - Karol Bagh", "FabIndia Ltd", "9811122233", "WEBSITE", service.service_name, 10000.00, 0.00, 0.00],
            ["2", "Mumbai - Bandra", "FabIndia Ltd", "9811122233", "WEBSITE", service.service_name, 10000.00, 0.00, 0.00],
            ["3", "Bangalore - Koramangala", "FabIndia Ltd", "9811122233", "WEBSITE", service.service_name, 10000.00, 0.00, 0.00],
        ]
        file_bytes = make_csv_bytes(headers, rows)
        resp = client.post(
            "/api/sales/import/preview",
            files={"file": ("multi_locations.csv", file_bytes, "text/csv")},
            headers=auth_header(sales_user),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_rows"] == 3
        assert data["valid_rows_count"] == 3
        assert data["duplicate_warnings_count"] == 0
        locs = [r["location"] for r in data["rows"]]
        assert locs == ["Delhi - Karol Bagh", "Mumbai - Bandra", "Bangalore - Koramangala"]

    def test_case_10_fifty_valid_location_rows_imported_and_verified(
        self, client: TestClient, db_session: Session, routing_fixture: dict
    ):
        """Case 10: Fifty valid location rows can be imported and verified."""
        sales_user = routing_fixture["sales_user"]
        ops_user = routing_fixture["ops_user"]
        service = routing_fixture["service"]

        rows_data = []
        for i in range(1, 51):
            rows_data.append(
                SalesImportRowValidation(
                    row_number=i,
                    sl_no=str(i),
                    location=f"Location Branch {i}",
                    client_name=f"Chain Store {i}",
                    contact=f"98000{i:05d}",
                    source="DIRECT",
                    work=service.service_name,
                    total_amount=Decimal("5000.00"),
                    incidental_cost=Decimal("100.00"),
                    service_id=service.service_id,
                    service_name=service.service_name,
                    is_valid=True,
                )
            )

        payload = SalesImportExecuteRequest(
            rows=rows_data,
            assignee_user_id=ops_user.user_id,
            idempotency_key=str(uuid.uuid4()),
        )
        resp = client.post("/api/sales/import/execute", json=payload.model_dump(mode="json"), headers=auth_header(sales_user))
        assert resp.status_code == 201, resp.text
        res = resp.json()
        assert res["imported_count"] == 50
        assert res["assignments_count"] == 50

        # Verify in DB
        orders = db_session.query(SalesOrder).filter(SalesOrder.salesperson_user_id == sales_user.user_id).all()
        assert len(orders) >= 50

    def test_case_11_same_client_and_contact_different_locations_accepted(
        self, client: TestClient, routing_fixture: dict
    ):
        """Case 11: Same client name and contact with different locations are handled correctly (no false duplicates)."""
        sales_user = routing_fixture["sales_user"]
        service = routing_fixture["service"]
        headers = sales_import_service.TEMPLATE_COLUMNS
        rows = [
            ["1", "Branch A - Hyderabad", "TechCorp MultiLoc", "9876500000", "DIRECT", service.service_name, 8000.00, 0.00, 0.00],
            ["2", "Branch B - Pune", "TechCorp MultiLoc", "9876500000", "DIRECT", service.service_name, 8000.00, 0.00, 0.00],
        ]
        file_bytes = make_csv_bytes(headers, rows)
        resp = client.post(
            "/api/sales/import/preview",
            files={"file": ("same_client_diff_loc.csv", file_bytes, "text/csv")},
            headers=auth_header(sales_user),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_rows"] == 2
        assert data["valid_rows_count"] == 2
        assert data["duplicate_warnings_count"] == 0
        assert data["can_import"] is True

    def test_case_12_duplicate_rows_within_file_detected(self, client: TestClient, routing_fixture: dict):
        """Case 12: Duplicate rows within the file are detected."""
        sales_user = routing_fixture["sales_user"]
        service = routing_fixture["service"]
        headers = sales_import_service.TEMPLATE_COLUMNS
        rows = [
            ["1", "Noida", "Identical Client", "9876511111", "WEBSITE", service.service_name, 5000.00, 0.00, 0.00],
            ["2", "Noida", "Identical Client", "9876511111", "WEBSITE", service.service_name, 5000.00, 0.00, 0.00],
        ]
        file_bytes = make_csv_bytes(headers, rows)
        resp = client.post(
            "/api/sales/import/preview",
            files={"file": ("dup_file.csv", file_bytes, "text/csv")},
            headers=auth_header(sales_user),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["duplicate_warnings_count"] >= 1
        assert data["rows"][1]["is_duplicate_in_file"] is True
        assert "Duplicate row in file" in data["rows"][1]["warnings"][0]

    def test_case_13_existing_record_duplicates_flagged(
        self, client: TestClient, db_session: Session, routing_fixture: dict
    ):
        """Case 13: Existing-record duplicates are detected and flagged with warnings."""
        sales_user = routing_fixture["sales_user"]
        ops_user = routing_fixture["ops_user"]
        service = routing_fixture["service"]

        # First import one order
        row1 = SalesImportRowValidation(
            row_number=1,
            sl_no="1",
            location="Chandigarh",
            client_name="PreExisting Client",
            contact="9812345678",
            source="DIRECT",
            work=service.service_name,
            total_amount=Decimal("15000.00"),
            incidental_cost=Decimal("0.00"),
            service_id=service.service_id,
            service_name=service.service_name,
            is_valid=True,
        )
        payload = SalesImportExecuteRequest(
            rows=[row1],
            assignee_user_id=ops_user.user_id,
            idempotency_key=str(uuid.uuid4()),
        )
        exec_resp = client.post("/api/sales/import/execute", json=payload.model_dump(mode="json"), headers=auth_header(sales_user))
        assert exec_resp.status_code == 201

        # Now preview a file containing the exact same record
        headers = sales_import_service.TEMPLATE_COLUMNS
        rows = [["1", "Chandigarh", "PreExisting Client", "9812345678", "DIRECT", service.service_name, 15000.00, 0.00, 0.00]]
        file_bytes = make_csv_bytes(headers, rows)
        preview_resp = client.post(
            "/api/sales/import/preview",
            files={"file": ("check_dup.csv", file_bytes, "text/csv")},
            headers=auth_header(sales_user),
        )
        assert preview_resp.status_code == 200
        data = preview_resp.json()
        assert data["rows"][0]["is_duplicate_in_db"] is True
        assert "already exists in CRM" in data["rows"][0]["warnings"][0]

    def test_case_14_missing_required_fields_identify_correct_row(self, client: TestClient, routing_fixture: dict):
        """Case 14: Missing required fields identify the correct row."""
        sales_user = routing_fixture["sales_user"]
        service = routing_fixture["service"]
        headers = sales_import_service.TEMPLATE_COLUMNS
        rows = [
            ["1", "Delhi", "Valid Client", "9876543210", "DIRECT", service.service_name, 5000.00, 0.00, 0.00],
            ["2", "Mumbai", "", "9876543211", "DIRECT", service.service_name, 5000.00, 0.00, 0.00],  # Missing Client Name
            ["3", "Chennai", "No Phone", "", "DIRECT", service.service_name, 5000.00, 0.00, 0.00],  # Missing Contact
            ["4", "Kolkata", "No Amount", "9876543212", "DIRECT", service.service_name, "", 0.00, 0.00],  # Missing Amount
        ]
        file_bytes = make_csv_bytes(headers, rows)
        resp = client.post(
            "/api/sales/import/preview",
            files={"file": ("missing_fields.csv", file_bytes, "text/csv")},
            headers=auth_header(sales_user),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_rows"] == 4
        assert data["error_rows_count"] == 3
        # Row 2 error
        assert "Client Name is required" in data["rows"][1]["errors"][0]
        # Row 3 error
        assert "Contact number is required" in data["rows"][2]["errors"][0]
        # Row 4 error
        assert "Total Amount is required" in data["rows"][3]["errors"][0]

    def test_case_15_invalid_source_and_work_values_rejected(self, client: TestClient, routing_fixture: dict):
        """Case 15: Invalid Source and Work values are rejected."""
        sales_user = routing_fixture["sales_user"]
        headers = sales_import_service.TEMPLATE_COLUMNS
        rows = [
            ["1", "Goa", "Client 1", "9876543210", "INVALID_SOURCE_ABC", "NonExistentService123", 5000.00, 0.00, 0.00],
        ]
        file_bytes = make_csv_bytes(headers, rows)
        resp = client.post(
            "/api/sales/import/preview",
            files={"file": ("bad_values.csv", file_bytes, "text/csv")},
            headers=auth_header(sales_user),
        )
        assert resp.status_code == 200
        row = resp.json()["rows"][0]
        errors = " ".join(row["errors"])
        assert "Invalid Source" in errors
        assert "does not match any active service" in errors

    def test_case_16_invalid_or_prohibited_financial_amounts_rejected(self, client: TestClient, routing_fixture: dict):
        """Case 16: Invalid or prohibited financial amounts are rejected."""
        sales_user = routing_fixture["sales_user"]
        service = routing_fixture["service"]
        headers = sales_import_service.TEMPLATE_COLUMNS
        rows = [
            ["1", "Delhi", "Client A", "9876543210", "DIRECT", service.service_name, -500.00, 0.00, 0.00],  # Negative Total
            ["2", "Delhi", "Client B", "9876543211", "DIRECT", service.service_name, 500.00, 0.00, -50.00],  # Negative Incidental
            ["3", "Delhi", "Client C", "9876543212", "DIRECT", service.service_name, 500.00, 0.00, 600.00],  # Incidental > Total
            ["4", "Delhi", "Client D", "9876543213", "DIRECT", service.service_name, 500.00, -100.00, 0.00],  # Negative Advance
            ["5", "Delhi", "Client E", "9876543214", "DIRECT", service.service_name, 500.00, 700.00, 0.00],  # Advance > Total
        ]
        file_bytes = make_csv_bytes(headers, rows)
        resp = client.post(
            "/api/sales/import/preview",
            files={"file": ("bad_finances.csv", file_bytes, "text/csv")},
            headers=auth_header(sales_user),
        )
        assert resp.status_code == 200
        rows_res = resp.json()["rows"]
        assert "Total Amount cannot be negative" in rows_res[0]["errors"][0]
        assert "Incidental Cost cannot be negative" in rows_res[1]["errors"][0]
        assert "Incidental Cost cannot exceed Total Amount" in rows_res[2]["errors"][0]
        assert "Advance Amount cannot be negative" in rows_res[3]["errors"][0]
        assert "Advance Amount cannot exceed Total Amount" in rows_res[4]["errors"][0]

    def test_case_17_contact_numbers_and_leading_zeros_preserved(
        self, client: TestClient, db_session: Session, routing_fixture: dict
    ):
        """Case 17: Contact numbers and leading zeros are preserved correctly."""
        sales_user = routing_fixture["sales_user"]
        ops_user = routing_fixture["ops_user"]
        service = routing_fixture["service"]

        row = SalesImportRowValidation(
            row_number=1,
            sl_no="1",
            location="Delhi",
            client_name="Zero Phone Client",
            contact="09876543210",
            source="DIRECT",
            work=service.service_name,
            total_amount=Decimal("10000.00"),
            incidental_cost=Decimal("0.00"),
            service_id=service.service_id,
            service_name=service.service_name,
            is_valid=True,
        )
        payload = SalesImportExecuteRequest(
            rows=[row],
            assignee_user_id=ops_user.user_id,
            idempotency_key=str(uuid.uuid4()),
        )
        resp = client.post("/api/sales/import/execute", json=payload.model_dump(mode="json"), headers=auth_header(sales_user))
        assert resp.status_code == 201

        # Check client in DB
        cl = db_session.query(ClientMaster).filter(ClientMaster.client_name == "Zero Phone Client").first()
        assert cl is not None
        assert cl.contact_phone == "09876543210"

    def test_case_18_invalid_files_create_zero_sales_records(
        self, client: TestClient, db_session: Session, routing_fixture: dict
    ):
        """Case 18: Invalid files create zero sales records."""
        sales_user = routing_fixture["sales_user"]
        ops_user = routing_fixture["ops_user"]

        init_count = db_session.query(SalesOrder).count()

        # Attempt to execute import with an invalid row
        row = SalesImportRowValidation(
            row_number=1,
            sl_no="1",
            location="Delhi",
            client_name="Invalid Test",
            contact="123",  # Malformed
            source="INVALID",
            work="NonExistent",
            total_amount=Decimal("-10.00"),
            incidental_cost=Decimal("0.00"),
            is_valid=False,
            errors=["Invalid contact"],
        )
        payload = SalesImportExecuteRequest(
            rows=[row],
            assignee_user_id=ops_user.user_id,
        )
        resp = client.post("/api/sales/import/execute", json=payload.model_dump(mode="json"), headers=auth_header(sales_user))
        assert resp.status_code == 400

        final_count = db_session.query(SalesOrder).count()
        assert final_count == init_count

    def test_case_19_preview_or_validation_does_not_create_sales_entries(
        self, client: TestClient, db_session: Session, routing_fixture: dict
    ):
        """Case 19: Previewing or validating a file does not create sales entries."""
        sales_user = routing_fixture["sales_user"]
        service = routing_fixture["service"]
        init_count = db_session.query(SalesOrder).count()

        headers = sales_import_service.TEMPLATE_COLUMNS
        rows = [["1", "Delhi", "Preview Only Corp", "9876500999", "DIRECT", service.service_name, 10000.00, 0.00, 0.00]]
        file_bytes = make_csv_bytes(headers, rows)
        resp = client.post(
            "/api/sales/import/preview",
            files={"file": ("preview_test.csv", file_bytes, "text/csv")},
            headers=auth_header(sales_user),
        )
        assert resp.status_code == 200

        final_count = db_session.query(SalesOrder).count()
        assert final_count == init_count

    # -------------------------------------------------------------
    # SECTION C: Bulk Operations Assignment (Test Cases 20 - 27)
    # -------------------------------------------------------------

    def test_case_20_valid_operations_employee_can_be_selected(self, client: TestClient, routing_fixture: dict):
        """Case 20: A valid Operations employee can be selected for the batch."""
        sales_user = routing_fixture["sales_user"]
        resp = client.get("/api/sales/operations-assignees", headers=auth_header(sales_user))
        assert resp.status_code == 200
        assignees = resp.json()
        assert len(assignees) > 0
        ops_user_id = str(routing_fixture["ops_user"].user_id)
        assert any(a["user_id"] == ops_user_id for a in assignees)

    def test_case_21_every_imported_sales_entry_assigned_to_selected_employee(
        self, client: TestClient, db_session: Session, routing_fixture: dict
    ):
        """Case 21: Every imported sales entry is assigned to the selected employee."""
        sales_user = routing_fixture["sales_user"]
        ops_user = routing_fixture["ops_user"]
        service = routing_fixture["service"]

        rows = [
            SalesImportRowValidation(
                row_number=1,
                sl_no="1",
                location="Kolkata",
                client_name="Assigned Test 1",
                contact="9800011111",
                source="DIRECT",
                work=service.service_name,
                total_amount=Decimal("12000.00"),
                service_id=service.service_id,
                service_name=service.service_name,
                is_valid=True,
            ),
            SalesImportRowValidation(
                row_number=2,
                sl_no="2",
                location="Patna",
                client_name="Assigned Test 2",
                contact="9800022222",
                source="DIRECT",
                work=service.service_name,
                total_amount=Decimal("15000.00"),
                service_id=service.service_id,
                service_name=service.service_name,
                is_valid=True,
            ),
        ]
        payload = SalesImportExecuteRequest(
            rows=rows,
            assignee_user_id=ops_user.user_id,
            idempotency_key=str(uuid.uuid4()),
        )
        resp = client.post("/api/sales/import/execute", json=payload.model_dump(mode="json"), headers=auth_header(sales_user))
        assert resp.status_code == 201
        data = resp.json()

        for order_no in data["order_numbers"]:
            order = db_session.query(SalesOrder).filter(SalesOrder.order_number == order_no).first()
            assert order is not None
            assert order.confirmation_status == "CONFIRMED"
            app = db_session.query(OperationApplication).filter(OperationApplication.sales_order_id == order.order_id).first()
            assert app is not None
            assert app.assigned_to_user_id == ops_user.user_id
            assert app.application_status == "ASSIGNED"

    def test_case_22_assignment_history_created_for_each_entry(
        self, client: TestClient, db_session: Session, routing_fixture: dict
    ):
        """Case 22: Assignment history is created for each imported entry."""
        sales_user = routing_fixture["sales_user"]
        ops_user = routing_fixture["ops_user"]
        service = routing_fixture["service"]

        row = SalesImportRowValidation(
            row_number=1,
            sl_no="1",
            location="Jaipur",
            client_name="History Test Corp",
            contact="9876599999",
            source="DIRECT",
            work=service.service_name,
            total_amount=Decimal("9000.00"),
            service_id=service.service_id,
            service_name=service.service_name,
            is_valid=True,
        )
        payload = SalesImportExecuteRequest(
            rows=[row],
            assignee_user_id=ops_user.user_id,
            idempotency_key=str(uuid.uuid4()),
        )
        resp = client.post("/api/sales/import/execute", json=payload.model_dump(mode="json"), headers=auth_header(sales_user))
        assert resp.status_code == 201

        order_no = resp.json()["order_numbers"][0]
        order = db_session.query(SalesOrder).filter(SalesOrder.order_number == order_no).first()
        app = db_session.query(OperationApplication).filter(OperationApplication.sales_order_id == order.order_id).first()
        histories = db_session.query(ApplicationAssignmentHistory).filter(ApplicationAssignmentHistory.application_id == app.application_id).all()
        assert len(histories) >= 1
        assert histories[0].new_assignee_user_id == ops_user.user_id
        assert histories[0].assigned_by_user_id == sales_user.user_id

    def test_case_23_assigned_employee_sees_tasks_in_operations_dashboard(
        self, client: TestClient, routing_fixture: dict
    ):
        """Case 23: The assigned employee can see the new tasks in Operations dashboard."""
        sales_user = routing_fixture["sales_user"]
        ops_user = routing_fixture["ops_user"]
        service = routing_fixture["service"]

        row = SalesImportRowValidation(
            row_number=1,
            sl_no="1",
            location="Nagpur",
            client_name="Ops Visible Corp",
            contact="9876588888",
            source="DIRECT",
            work=service.service_name,
            total_amount=Decimal("11000.00"),
            service_id=service.service_id,
            service_name=service.service_name,
            is_valid=True,
        )
        payload = SalesImportExecuteRequest(
            rows=[row],
            assignee_user_id=ops_user.user_id,
            idempotency_key=str(uuid.uuid4()),
        )
        resp = client.post("/api/sales/import/execute", json=payload.model_dump(mode="json"), headers=auth_header(sales_user))
        assert resp.status_code == 201

        # Ops user queries operations tasks
        ops_resp = client.get("/api/operations/tasks", headers=auth_header(ops_user))
        assert ops_resp.status_code == 200
        items = ops_resp.json().get("items", [])
        assert any(item.get("client_name") == "Ops Visible Corp" for item in items)

    def test_case_24_unauthorized_inactive_or_ineligible_employee_rejected(
        self, client: TestClient, db_session: Session, routing_fixture: dict
    ):
        """Case 24: An unauthorized, inactive, or ineligible employee cannot be assigned."""
        from app.models.module import Module
        # Ensure OPERATIONS module is not parented under SALES in test fixture
        ops_mod = db_session.query(Module).filter(Module.module_code == "OPERATIONS").first()
        if ops_mod:
            ops_mod.parent_module_id = None
            db_session.flush()

        sales_user = routing_fixture["sales_user"]
        ops_user = routing_fixture["ops_user"]
        service = routing_fixture["service"]

        row = SalesImportRowValidation(
            row_number=1,
            sl_no="1",
            location="Delhi",
            client_name="Test Bad Assignee",
            contact="9876543210",
            source="DIRECT",
            work=service.service_name,
            total_amount=Decimal("5000.00"),
            service_id=service.service_id,
            is_valid=True,
        )

        # 1. Non-existent UUID
        fake_id = uuid.uuid4()
        payload = SalesImportExecuteRequest(rows=[row], assignee_user_id=fake_id)
        resp1 = client.post("/api/sales/import/execute", json=payload.model_dump(mode="json"), headers=auth_header(sales_user))
        assert resp1.status_code == 400
        assert "not found" in resp1.json()["detail"].lower()

        # 2. Inactive Employee
        ops_user.account_status = "INACTIVE"
        db_session.flush()
        payload.assignee_user_id = ops_user.user_id
        resp2 = client.post("/api/sales/import/execute", json=payload.model_dump(mode="json"), headers=auth_header(sales_user))
        assert resp2.status_code == 400
        assert "inactive" in resp2.json()["detail"].lower()
        ops_user.account_status = "ACTIVE"
        db_session.flush()

        # 3. Pure Sales employee without Ops permission
        payload.assignee_user_id = sales_user.user_id
        resp3 = client.post("/api/sales/import/execute", json=payload.model_dump(mode="json"), headers=auth_header(sales_user))
        assert resp3.status_code == 400
        assert "not eligible" in resp3.json()["detail"].lower()

    def test_case_25_users_cannot_bypass_company_scope(
        self, client: TestClient, routing_fixture: dict
    ):
        """Case 25: Users cannot bypass existing company scope or access permissions."""
        sales_user = routing_fixture["sales_user"]
        company_b_user = routing_fixture["company_b_user"]
        service = routing_fixture["service"]

        row = SalesImportRowValidation(
            row_number=1,
            sl_no="1",
            location="Delhi",
            client_name="Cross Company Client",
            contact="9876543210",
            source="DIRECT",
            work=service.service_name,
            total_amount=Decimal("5000.00"),
            service_id=service.service_id,
            is_valid=True,
        )
        payload = SalesImportExecuteRequest(rows=[row], assignee_user_id=company_b_user.user_id)
        resp = client.post("/api/sales/import/execute", json=payload.model_dump(mode="json"), headers=auth_header(sales_user))
        assert resp.status_code == 400
        assert "authorized company" in resp.json()["detail"].lower() or "not eligible" in resp.json()["detail"].lower()

    def test_case_26_failed_assignment_leaves_no_partially_committed_sales_records(
        self, client: TestClient, db_session: Session, routing_fixture: dict
    ):
        """Case 26: A failed assignment does not leave partially committed sales records."""
        sales_user = routing_fixture["sales_user"]
        ops_user = routing_fixture["ops_user"]
        service = routing_fixture["service"]

        init_orders = db_session.query(SalesOrder).count()

        # Create batch with 2 rows: first is valid, second has non-existent service_id which fails during processing
        rows = [
            SalesImportRowValidation(
                row_number=1,
                sl_no="1",
                location="Delhi",
                client_name="Rollback Test 1",
                contact="9876543210",
                source="DIRECT",
                work=service.service_name,
                total_amount=Decimal("5000.00"),
                service_id=service.service_id,
                is_valid=True,
            ),
            SalesImportRowValidation(
                row_number=2,
                sl_no="2",
                location="Delhi",
                client_name="Rollback Test 2",
                contact="9876543211",
                source="DIRECT",
                work="Bad Service",
                total_amount=Decimal("5000.00"),
                service_id=uuid.uuid4(),  # Does not exist in FK
                is_valid=True,
            ),
        ]
        payload = SalesImportExecuteRequest(rows=rows, assignee_user_id=ops_user.user_id)
        resp = client.post("/api/sales/import/execute", json=payload.model_dump(mode="json"), headers=auth_header(sales_user))
        assert resp.status_code in (400, 500)

        # Entire batch rolled back: no new orders in DB
        final_orders = db_session.query(SalesOrder).count()
        assert final_orders == init_orders

    def test_case_27_imported_assignments_visible_to_authorized_administrators(
        self, client: TestClient, routing_fixture: dict
    ):
        """Case 27: Imported assignments are visible to authorized administrators."""
        super_admin = routing_fixture["super_admin"]
        sales_user = routing_fixture["sales_user"]
        ops_user = routing_fixture["ops_user"]
        service = routing_fixture["service"]

        row = SalesImportRowValidation(
            row_number=1,
            sl_no="1",
            location="Surat",
            client_name="Admin Audit Corp",
            contact="9876533333",
            source="DIRECT",
            work=service.service_name,
            total_amount=Decimal("25000.00"),
            service_id=service.service_id,
            service_name=service.service_name,
            is_valid=True,
        )
        payload = SalesImportExecuteRequest(
            rows=[row],
            assignee_user_id=ops_user.user_id,
            idempotency_key=str(uuid.uuid4()),
        )
        resp = client.post("/api/sales/import/execute", json=payload.model_dump(mode="json"), headers=auth_header(sales_user))
        assert resp.status_code == 201

        # Super admin queries operations
        admin_resp = client.get("/api/operations/tasks", headers=auth_header(super_admin))
        assert admin_resp.status_code == 200
        items = admin_resp.json().get("items", [])
        assert any(item.get("client_name") == "Admin Audit Corp" for item in items)

    # -------------------------------------------------------------
    # SECTION D: Database Integrity and Financial Calculations (Test Cases 28 - 35)
    # -------------------------------------------------------------

    def test_case_28_successful_import_creates_correct_number_of_sales_entries(
        self, client: TestClient, db_session: Session, routing_fixture: dict
    ):
        """Case 28: Successful import creates the correct number of sales entries."""
        sales_user = routing_fixture["sales_user"]
        ops_user = routing_fixture["ops_user"]
        service = routing_fixture["service"]

        init_orders = db_session.query(SalesOrder).count()
        rows = [
            SalesImportRowValidation(
                row_number=1,
                sl_no="1",
                location="Lucknow",
                client_name="Batch Entry 1",
                contact="9876500001",
                source="DIRECT",
                work=service.service_name,
                total_amount=Decimal("10000.00"),
                service_id=service.service_id,
                is_valid=True,
            ),
            SalesImportRowValidation(
                row_number=2,
                sl_no="2",
                location="Kanpur",
                client_name="Batch Entry 2",
                contact="9876500002",
                source="DIRECT",
                work=service.service_name,
                total_amount=Decimal("12000.00"),
                service_id=service.service_id,
                is_valid=True,
            ),
        ]
        payload = SalesImportExecuteRequest(
            rows=rows,
            assignee_user_id=ops_user.user_id,
            idempotency_key=str(uuid.uuid4()),
        )
        resp = client.post("/api/sales/import/execute", json=payload.model_dump(mode="json"), headers=auth_header(sales_user))
        assert resp.status_code == 201

        final_orders = db_session.query(SalesOrder).count()
        assert final_orders == init_orders + 2

    def test_case_29_gst_calculation_logic_reused_without_double_tax(
        self, client: TestClient, db_session: Session, routing_fixture: dict
    ):
        """Case 29: Existing GST calculation logic is reused without double taxation."""
        sales_user = routing_fixture["sales_user"]
        ops_user = routing_fixture["ops_user"]
        service = routing_fixture["service"]

        row = SalesImportRowValidation(
            row_number=1,
            sl_no="1",
            location="Delhi",
            client_name="GST Reuse Corp",
            contact="9876543299",
            source="DIRECT",
            work=service.service_name,
            total_amount=Decimal("10000.00"),
            incidental_cost=Decimal("500.00"),
            service_id=service.service_id,
            is_valid=True,
        )
        payload = SalesImportExecuteRequest(
            rows=[row],
            assignee_user_id=ops_user.user_id,
            idempotency_key=str(uuid.uuid4()),
        )
        resp = client.post("/api/sales/import/execute", json=payload.model_dump(mode="json"), headers=auth_header(sales_user))
        assert resp.status_code == 201
        order_no = resp.json()["order_numbers"][0]

        order = db_session.query(SalesOrder).filter(SalesOrder.order_number == order_no).first()
        assert order.order_value == Decimal("10000.00")  # Exactly equal to Total Amount
        assert order.gst_invoice_required is False
        assert order.profit_amount == Decimal("9500.00")  # Total Amount - Incidental Cost

    def test_case_30_payment_and_financial_workflows_preserved(
        self, client: TestClient, db_session: Session, routing_fixture: dict
    ):
        """Case 30: Existing payment, invoice, and other financial workflows are not unintentionally changed."""
        sales_user = routing_fixture["sales_user"]
        ops_user = routing_fixture["ops_user"]
        service = routing_fixture["service"]

        row = SalesImportRowValidation(
            row_number=1,
            sl_no="1",
            location="Delhi",
            client_name="Finance Flow Corp",
            contact="9876543288",
            source="DIRECT",
            work=service.service_name,
            total_amount=Decimal("20000.00"),
            service_id=service.service_id,
            is_valid=True,
        )
        payload = SalesImportExecuteRequest(
            rows=[row],
            assignee_user_id=ops_user.user_id,
            idempotency_key=str(uuid.uuid4()),
        )
        resp = client.post("/api/sales/import/execute", json=payload.model_dump(mode="json"), headers=auth_header(sales_user))
        assert resp.status_code == 201
        order_no = resp.json()["order_numbers"][0]

        order = db_session.query(SalesOrder).filter(SalesOrder.order_number == order_no).first()
        assert order.amount_received == Decimal("0.00")
        assert order.balance_amount == Decimal("20000.00")
        assert order.payment_status == "PENDING"
        assert order.govt_fees == Decimal("0.00")

    def test_case_31_database_failure_rolls_back_transaction(
        self, client: TestClient, db_session: Session, routing_fixture: dict
    ):
        """Case 31: A database failure during import rolls back the transaction correctly."""
        sales_user = routing_fixture["sales_user"]
        ops_user = routing_fixture["ops_user"]
        service = routing_fixture["service"]

        init_orders = db_session.query(SalesOrder).count()

        # Send row with duplicate order_number collision or forced error
        row = SalesImportRowValidation(
            row_number=1,
            sl_no="1",
            location="Delhi",
            client_name="DB Fail Corp",
            contact="9876543277",
            source="DIRECT",
            work=service.service_name,
            total_amount=Decimal("15000.00"),
            service_id=uuid.uuid4(),  # Invalid FK
            is_valid=True,
        )
        payload = SalesImportExecuteRequest(rows=[row], assignee_user_id=ops_user.user_id)
        resp = client.post("/api/sales/import/execute", json=payload.model_dump(mode="json"), headers=auth_header(sales_user))
        assert resp.status_code in (400, 500)

        final_orders = db_session.query(SalesOrder).count()
        assert final_orders == init_orders

    def test_case_32_repeated_submission_does_not_create_duplicates_idempotency(
        self, client: TestClient, db_session: Session, routing_fixture: dict
    ):
        """Case 32: Repeated submission of the same batch with idempotency key does not create duplicate entries."""
        sales_user = routing_fixture["sales_user"]
        ops_user = routing_fixture["ops_user"]
        service = routing_fixture["service"]

        idem_key = f"idem-key-{uuid.uuid4()}"
        row = SalesImportRowValidation(
            row_number=1,
            sl_no="1",
            location="Delhi",
            client_name="Idempotent Client",
            contact="9876543266",
            source="DIRECT",
            work=service.service_name,
            total_amount=Decimal("15000.00"),
            service_id=service.service_id,
            is_valid=True,
        )
        payload = SalesImportExecuteRequest(
            rows=[row],
            assignee_user_id=ops_user.user_id,
            idempotency_key=idem_key,
        )

        # First request
        resp1 = client.post("/api/sales/import/execute", json=payload.model_dump(mode="json"), headers=auth_header(sales_user))
        assert resp1.status_code == 201
        data1 = resp1.json()

        orders_after_first = db_session.query(SalesOrder).filter(SalesOrder.order_number.in_(data1["order_numbers"])).count()
        assert orders_after_first == 1

        # Second identical request (retry / double submission)
        resp2 = client.post("/api/sales/import/execute", json=payload.model_dump(mode="json"), headers=auth_header(sales_user))
        assert resp2.status_code == 201
        data2 = resp2.json()

        # Returns identical response without creating extra records
        assert data2["order_numbers"] == data1["order_numbers"]
        orders_after_second = db_session.query(SalesOrder).filter(SalesOrder.order_number.in_(data1["order_numbers"])).count()
        assert orders_after_second == 1

    def test_case_33_duplicate_records_require_explicit_confirmation(
        self, client: TestClient, routing_fixture: dict
    ):
        """Case 33: Concurrent or duplicate requests do not bypass duplicate protections without explicit flag."""
        sales_user = routing_fixture["sales_user"]
        ops_user = routing_fixture["ops_user"]
        service = routing_fixture["service"]

        row = SalesImportRowValidation(
            row_number=1,
            sl_no="1",
            location="Delhi",
            client_name="Warning Client",
            contact="9876543255",
            source="DIRECT",
            work=service.service_name,
            total_amount=Decimal("15000.00"),
            service_id=service.service_id,
            is_valid=True,
            is_duplicate_in_file=True,
            warnings=["Duplicate row in file"],
        )
        # Attempt without allow_duplicates=True
        payload = SalesImportExecuteRequest(
            rows=[row],
            assignee_user_id=ops_user.user_id,
            allow_duplicates=False,
        )
        resp = client.post("/api/sales/import/execute", json=payload.model_dump(mode="json"), headers=auth_header(sales_user))
        assert resp.status_code == 400
        assert "duplicate" in resp.json()["detail"].lower()

        # Now attempt with allow_duplicates=True
        payload.allow_duplicates = True
        payload.idempotency_key = str(uuid.uuid4())
        resp2 = client.post("/api/sales/import/execute", json=payload.model_dump(mode="json"), headers=auth_header(sales_user))
        assert resp2.status_code == 201

    def test_case_34_no_orphaned_assignments_or_incomplete_records(
        self, client: TestClient, db_session: Session, routing_fixture: dict
    ):
        """Case 34: A failed import does not create orphaned assignments or incomplete records."""
        sales_user = routing_fixture["sales_user"]
        ops_user = routing_fixture["ops_user"]

        init_apps = db_session.query(OperationApplication).count()
        init_orders = db_session.query(SalesOrder).count()

        # Intentional failure payload
        row = SalesImportRowValidation(
            row_number=1,
            sl_no="1",
            location="Delhi",
            client_name="Orphan Check",
            contact="9876543244",
            source="DIRECT",
            work="FailWork",
            total_amount=Decimal("15000.00"),
            service_id=uuid.uuid4(),
            is_valid=True,
        )
        payload = SalesImportExecuteRequest(rows=[row], assignee_user_id=ops_user.user_id)
        resp = client.post("/api/sales/import/execute", json=payload.model_dump(mode="json"), headers=auth_header(sales_user))
        assert resp.status_code in (400, 500)

        assert db_session.query(OperationApplication).count() == init_apps
        assert db_session.query(SalesOrder).count() == init_orders

    def test_case_35_existing_records_remain_unchanged_after_import_tests(
        self, client: TestClient, db_session: Session, routing_fixture: dict
    ):
        """Case 35: Existing records remain unchanged after the import tests."""
        sales_user = routing_fixture["sales_user"]
        ops_user = routing_fixture["ops_user"]
        service = routing_fixture["service"]

        # Create one pre-existing record manually
        order_pre = SalesOrder(
            order_number=f"SO-PRE-{uuid.uuid4().hex[:6]}",
            company_id=routing_fixture["company_a"].company_id,
            client_id=routing_fixture["client"].client_id,
            service_id=service.service_id,
            salesperson_user_id=sales_user.user_id,
            lead_source="DIRECT",
            order_date=routing_fixture["client"].created_at.date() if routing_fixture["client"].created_at else sales_user.date_of_joining,
            order_value=Decimal("50000.00"),
            amount_received=Decimal("50000.00"),
            balance_amount=Decimal("0.00"),
            govt_fees=Decimal("0.00"),
            incidental_cost=Decimal("0.00"),
            profit_amount=Decimal("50000.00"),
            payment_status="FULLY_PAID",
            confirmation_status="CONFIRMED",
        )
        db_session.add(order_pre)
        db_session.commit()
        pre_id = order_pre.order_id

        # Execute bulk import
        row = SalesImportRowValidation(
            row_number=1,
            sl_no="1",
            location="Delhi",
            client_name="Other Client",
            contact="9876543233",
            source="DIRECT",
            work=service.service_name,
            total_amount=Decimal("15000.00"),
            service_id=service.service_id,
            is_valid=True,
        )
        payload = SalesImportExecuteRequest(
            rows=[row],
            assignee_user_id=ops_user.user_id,
            idempotency_key=str(uuid.uuid4()),
        )
        resp = client.post("/api/sales/import/execute", json=payload.model_dump(mode="json"), headers=auth_header(sales_user))
        assert resp.status_code == 201

        # Verify pre-existing order is completely intact
        refreshed = db_session.get(SalesOrder, pre_id)
        assert refreshed is not None
        assert refreshed.order_value == Decimal("50000.00")
        assert refreshed.payment_status == "FULLY_PAID"

    # -------------------------------------------------------------
    # SECTION E: Regression and Permissions (Test Cases 36 - 40)
    # -------------------------------------------------------------

    def test_case_36_existing_manual_sales_entry_still_works(
        self, client: TestClient, routing_fixture: dict
    ):
        """Case 36: Existing manual Sales Entry still works."""
        sales_user = routing_fixture["sales_user"]
        service = routing_fixture["service"]
        cl = routing_fixture["client"]

        payload = {
            "order_date": "2026-10-25",
            "client_name": cl.client_name,
            "client_id": str(cl.client_id),
            "contact_no": "9876543210",
            "lead_source": "DIRECT",
            "service_id": str(service.service_id),
            "salesperson_user_id": str(sales_user.user_id),
            "order_value": 15000.00,
            "amount_received": 0.00,
            "govt_fees": 0.00,
            "incidental_cost": 0.00,
            "gst_invoice_required": False,
            "auto_confirm": True,
        }
        resp = client.post("/api/sales/orders", json=payload, headers=auth_header(sales_user))
        assert resp.status_code == 201
        assert resp.json()["confirmation_status"] == "CONFIRMED"

    def test_case_37_existing_sales_register_still_loads_and_displays_records(
        self, client: TestClient, routing_fixture: dict
    ):
        """Case 37: Existing Sales Register still loads and displays records."""
        sales_user = routing_fixture["sales_user"]
        resp = client.get("/api/sales/register", headers=auth_header(sales_user))
        assert resp.status_code == 200
        assert "items" in resp.json()

    def test_case_38_existing_sales_and_operations_apis_continue_working(
        self, client: TestClient, routing_fixture: dict
    ):
        """Case 38: Existing Sales and Operations APIs continue working."""
        sales_user = routing_fixture["sales_user"]
        ops_user = routing_fixture["ops_user"]

        # Sales dashboard
        resp1 = client.get("/api/sales/dashboard", headers=auth_header(sales_user))
        assert resp1.status_code == 200

        # Operations tasks
        resp2 = client.get("/api/operations/tasks", headers=auth_header(ops_user))
        assert resp2.status_code == 200

    def test_case_39_existing_authentication_and_permissions_remain_intact(
        self, client: TestClient
    ):
        """Case 39: Existing authentication and role-based permissions remain intact."""
        # Unauthenticated request rejected
        resp = client.get("/api/sales/import/template/xlsx")
        assert resp.status_code == 401

    def test_case_40_downloadable_error_report_generated(
        self, client: TestClient, routing_fixture: dict
    ):
        """Case 40: Downloadable error report is generated correctly."""
        sales_user = routing_fixture["sales_user"]
        rows = [
            SalesImportRowValidation(
                row_number=2,
                sl_no="1",
                location="Delhi",
                client_name="Error Corp",
                contact="123",
                source="INVALID_SRC",
                work="Bad Work",
                total_amount=Decimal("5000.00"),
                is_valid=False,
                errors=["Invalid contact", "Invalid source", "Invalid work"],
                warnings=["Duplicate warning"],
            )
        ]
        resp = client.post(
            "/api/sales/import/error-report",
            json=[r.model_dump(mode="json") for r in rows],
            headers=auth_header(sales_user),
        )
        assert resp.status_code == 200
        assert "text/csv" in resp.headers["content-type"]
        assert "attachment" in resp.headers["content-disposition"]
        csv_text = resp.content.decode("utf-8")
        assert "Error Corp" in csv_text
        assert "Invalid contact" in csv_text

    def test_case_41_apple_numbers_format_parsed_correctly(self, client: TestClient, routing_fixture: dict):
        """Case 41: Apple Numbers (.numbers) native Mac spreadsheet is parsed correctly."""
        import os
        import tempfile
        from numbers_parser import Document

        sales_user = routing_fixture["sales_user"]
        service = routing_fixture["service"]
        headers = sales_import_service.TEMPLATE_COLUMNS

        doc = Document()
        table = doc.sheets[0].tables[0]
        for c_idx, h in enumerate(headers):
            table.write(0, c_idx, h)
        data = ["1", "Indiranagar, Bangalore", "Mac Numbers Client", "09876543210", "WEBSITE", service.service_name, 15000.00, 3000.00, 500.00]
        for c_idx, v in enumerate(data):
            table.write(1, c_idx, v)

        with tempfile.NamedTemporaryFile(suffix=".numbers", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            doc.save(tmp_path)
            with open(tmp_path, "rb") as f:
                numbers_bytes = f.read()

            resp = client.post(
                "/api/sales/import/preview",
                files={"file": ("orders.numbers", numbers_bytes, "application/vnd.apple.numbers")},
                headers=auth_header(sales_user),
            )
            assert resp.status_code == 200, resp.text
            res_data = resp.json()
            assert res_data["total_rows"] == 1
            assert res_data["valid_rows_count"] == 1
            assert res_data["rows"][0]["client_name"] == "Mac Numbers Client"
            assert res_data["rows"][0]["contact"] == "09876543210"
            assert float(res_data["rows"][0]["advance_amount"]) == 3000.00
        finally:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass

    def test_case_42_advance_amount_handling_and_payment_status_derivation(
        self, client: TestClient, db_session: Session, routing_fixture: dict
    ):
        """Case 42: Advance Amount correctly sets amount_received, balance_amount, and payment_status."""
        sales_user = routing_fixture["sales_user"]
        ops_user = routing_fixture["ops_user"]
        service = routing_fixture["service"]
        headers = sales_import_service.TEMPLATE_COLUMNS

        rows = [
            ["1", "Bangalore", "Advance Partial Client", "9876599001", "DIRECT", service.service_name, 10000.00, 4000.00, 200.00],
            ["2", "Bangalore", "Advance Full Client", "9876599002", "DIRECT", service.service_name, 15000.00, 15000.00, 0.00],
            ["3", "Bangalore", "Advance Zero Client", "9876599003", "DIRECT", service.service_name, 8000.00, 0.00, 100.00],
        ]
        file_bytes = make_csv_bytes(headers, rows)

        # 1. Preview
        resp_preview = client.post(
            "/api/sales/import/preview",
            files={"file": ("adv_test.csv", file_bytes, "text/csv")},
            headers=auth_header(sales_user),
        )
        assert resp_preview.status_code == 200, resp_preview.text
        pdata = resp_preview.json()
        assert pdata["valid_rows_count"] == 3
        assert float(pdata["rows"][0]["advance_amount"]) == 4000.00
        assert float(pdata["rows"][1]["advance_amount"]) == 15000.00
        assert float(pdata["rows"][2]["advance_amount"]) == 0.00

        # 2. Execute
        valid_rows = [SalesImportRowValidation(**r) for r in pdata["rows"]]
        exec_payload = SalesImportExecuteRequest(
            rows=valid_rows,
            assignee_user_id=ops_user.user_id,
            idempotency_key=str(uuid.uuid4()),
        )
        resp_exec = client.post(
            "/api/sales/import/execute",
            json=exec_payload.model_dump(mode="json"),
            headers=auth_header(sales_user),
        )
        assert resp_exec.status_code == 201, resp_exec.text
        order_numbers = resp_exec.json()["order_numbers"]
        assert len(order_numbers) == 3

        # 3. Verify in DB
        # Order 1: Partial payment
        ord1 = db_session.query(SalesOrder).filter(SalesOrder.order_number == order_numbers[0]).first()
        assert ord1.order_value == Decimal("10000.00")
        assert ord1.amount_received == Decimal("4000.00")
        assert ord1.balance_amount == Decimal("6000.00")
        assert ord1.payment_status == "PARTIALLY_PAID"

        # Order 2: Full payment
        ord2 = db_session.query(SalesOrder).filter(SalesOrder.order_number == order_numbers[1]).first()
        assert ord2.order_value == Decimal("15000.00")
        assert ord2.amount_received == Decimal("15000.00")
        assert ord2.balance_amount == Decimal("0.00")
        assert ord2.payment_status == "FULLY_PAID"

        # Order 3: Zero advance / Pending
        ord3 = db_session.query(SalesOrder).filter(SalesOrder.order_number == order_numbers[2]).first()
        assert ord3.order_value == Decimal("8000.00")
        assert ord3.amount_received == Decimal("0.00")
        assert ord3.balance_amount == Decimal("8000.00")
        assert ord3.payment_status == "PENDING"

    def test_case_43_legacy_8_column_file_backward_compatibility(
        self, client: TestClient, db_session: Session, routing_fixture: dict
    ):
        """Case 43: Legacy 8-column files without Advance Amount header remain fully backwards compatible."""
        sales_user = routing_fixture["sales_user"]
        ops_user = routing_fixture["ops_user"]
        service = routing_fixture["service"]

        legacy_headers = [
            "Sl No",
            "Location",
            "Client Name",
            "Contact",
            "Source",
            "Work",
            "Total Amount",
            "Incidental Cost",
        ]
        rows = [
            ["1", "Indore", "Legacy 8Col Client", "9876599099", "DIRECT", service.service_name, 12000.00, 300.00]
        ]
        file_bytes = make_csv_bytes(legacy_headers, rows)

        # 1. Preview
        resp_preview = client.post(
            "/api/sales/import/preview",
            files={"file": ("legacy_8col.csv", file_bytes, "text/csv")},
            headers=auth_header(sales_user),
        )
        assert resp_preview.status_code == 200, resp_preview.text
        pdata = resp_preview.json()
        assert pdata["valid_rows_count"] == 1
        assert float(pdata["rows"][0]["advance_amount"]) == 0.00

        # 2. Execute
        valid_rows = [SalesImportRowValidation(**r) for r in pdata["rows"]]
        exec_payload = SalesImportExecuteRequest(
            rows=valid_rows,
            assignee_user_id=ops_user.user_id,
            idempotency_key=str(uuid.uuid4()),
        )
        resp_exec = client.post(
            "/api/sales/import/execute",
            json=exec_payload.model_dump(mode="json"),
            headers=auth_header(sales_user),
        )
        assert resp_exec.status_code == 201, resp_exec.text
        order_no = resp_exec.json()["order_numbers"][0]

        # 3. Verify in DB
        ord_db = db_session.query(SalesOrder).filter(SalesOrder.order_number == order_no).first()
        assert ord_db.order_value == Decimal("12000.00")
        assert ord_db.amount_received == Decimal("0.00")
        assert ord_db.balance_amount == Decimal("12000.00")
        assert ord_db.payment_status == "PENDING"

    def test_case_44_bulk_import_with_18_percent_gst_calculation(
        self, client: TestClient, db_session: Session, routing_fixture: dict
    ):
        """Case 44: When apply_gst=True, 18% GST is added to base amounts and gst_invoice_required is set to True."""
        sales_user = routing_fixture["sales_user"]
        ops_user = routing_fixture["ops_user"]
        service = routing_fixture["service"]
        headers = sales_import_service.TEMPLATE_COLUMNS

        # Row 1: Base 10,000, Advance 2,000, Incidental 200 -> GST 1,800, Total 11,800, Balance 9,800
        # Row 2: Base 20,000, Advance 23,600, Incidental 0 -> GST 3,600, Total 23,600, FULLY_PAID
        # Row 3: Base 10,000, Advance 11,000 (Advance > Base 10,000, but <= Final Total 11,800)
        rows = [
            ["1", "Delhi", "GST Client One", "9876599101", "DIRECT", service.service_name, 10000.00, 2000.00, 200.00],
            ["2", "Delhi", "GST Client Two", "9876599102", "DIRECT", service.service_name, 20000.00, 23600.00, 0.00],
            ["3", "Delhi", "GST Client Three", "9876599103", "DIRECT", service.service_name, 10000.00, 11000.00, 0.00],
        ]
        file_bytes = make_csv_bytes(headers, rows)

        # 1. Preview with apply_gst=true
        resp_preview = client.post(
            "/api/sales/import/preview?apply_gst=true",
            files={"file": ("gst_bulk.csv", file_bytes, "text/csv")},
            headers=auth_header(sales_user),
        )
        assert resp_preview.status_code == 200, resp_preview.text
        pdata = resp_preview.json()
        assert pdata["apply_gst"] is True
        assert pdata["valid_rows_count"] == 3
        assert pdata["can_import"] is True

        # Check Row 1 preview
        r1 = pdata["rows"][0]
        assert float(r1["base_amount"]) == 10000.00
        assert float(r1["gst_amount"]) == 1800.00
        assert float(r1["total_amount"]) == 11800.00
        assert r1["gst_invoice_required"] is True

        # Check Row 3 preview (Advance 11,000 is valid because 11,000 <= 11,800)
        r3 = pdata["rows"][2]
        assert r3["is_valid"] is True
        assert float(r3["total_amount"]) == 11800.00

        # 2. Execute with apply_gst=True
        valid_rows = [SalesImportRowValidation(**r) for r in pdata["rows"]]
        exec_payload = SalesImportExecuteRequest(
            rows=valid_rows,
            assignee_user_id=ops_user.user_id,
            idempotency_key=str(uuid.uuid4()),
            apply_gst=True,
        )
        resp_exec = client.post(
            "/api/sales/import/execute",
            json=exec_payload.model_dump(mode="json"),
            headers=auth_header(sales_user),
        )
        assert resp_exec.status_code == 201, resp_exec.text
        order_numbers = resp_exec.json()["order_numbers"]
        assert len(order_numbers) == 3

        # 3. Check Order 1 in DB
        ord1 = db_session.query(SalesOrder).filter(SalesOrder.order_number == order_numbers[0]).first()
        assert ord1.order_value == Decimal("11800.00")  # Base 10,000 + 18% GST (1,800)
        assert ord1.amount_received == Decimal("2000.00")
        assert ord1.balance_amount == Decimal("9800.00")  # 11,800 - 2,000
        assert ord1.profit_amount == Decimal("11600.00")  # 11,800 - 200
        assert ord1.gst_invoice_required is True
        assert ord1.payment_status == "PARTIALLY_PAID"

        # Check Order 2 in DB (Fully Paid)
        ord2 = db_session.query(SalesOrder).filter(SalesOrder.order_number == order_numbers[1]).first()
        assert ord2.order_value == Decimal("23600.00")  # Base 20,000 + 18% GST (3,600)
        assert ord2.amount_received == Decimal("23600.00")
        assert ord2.balance_amount == Decimal("0.00")
        assert ord2.gst_invoice_required is True
        assert ord2.payment_status == "FULLY_PAID"

        # Check Order 3 in DB
        ord3 = db_session.query(SalesOrder).filter(SalesOrder.order_number == order_numbers[2]).first()
        assert ord3.order_value == Decimal("11800.00")
        assert ord3.amount_received == Decimal("11000.00")
        assert ord3.balance_amount == Decimal("800.00")
        assert ord3.gst_invoice_required is True
        assert ord3.payment_status == "PARTIALLY_PAID"


