"""Comprehensive integration tests for Sales Register, Entry Form, Calculations, and RBAC scoping."""
import uuid
from datetime import date, timedelta
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.models.client import ClientMaster
from app.models.company import Company
from app.models.department import Department
from app.models.designation import Designation
from app.models.module import Module
from app.models.operation_application import OperationApplication
from app.models.sales_order import SalesOrder
from app.models.service import ServiceMaster, ServiceRequiredDocument
from app.models.user import User
from app.models.user_module_permission import UserModulePermission
from app.schemas.sales_order import SalesOrderCreate
from app.services.sales_service import create_sales_order, get_sales_register_data


@pytest.fixture
def sales_fixture(db_session: Session):
    """Seed test company, hierarchy, services, and permissions."""
    company = Company(
        company_code="GC_TEST",
        company_name="GoCompliance Test Corp",
        employee_code_prefix="GCT",
        status="ACTIVE",
    )
    db_session.add(company)
    db_session.flush()

    dept = Department(
        company_id=company.company_id,
        department_code="SALES",
        department_name="Sales Department",
        status="ACTIVE",
    )
    db_session.add(dept)
    db_session.flush()

    desig_mgr = Designation(
        company_id=company.company_id,
        designation_code="SALES_MGR",
        designation_name="Sales Manager",
        level_rank=10,
        status="ACTIVE",
    )
    desig_rep = Designation(
        company_id=company.company_id,
        designation_code="SALES_REP",
        designation_name="Sales Representative",
        level_rank=5,
        status="ACTIVE",
    )
    db_session.add_all([desig_mgr, desig_rep])
    db_session.flush()

    # Manager User
    manager = User(
        employee_code="GCT001",
        company_id=company.company_id,
        department_id=dept.department_id,
        designation_id=desig_mgr.designation_id,
        first_name="Meera",
        last_name="Kapoor",
        official_email="meera.k@gocompliance.test",
        mobile_number="+919888800001",
        date_of_joining=date(2023, 1, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        is_reporting_manager=True,
        must_change_password=False,
    )
    db_session.add(manager)
    db_session.flush()

    # Sales Rep 1 (Reports to Meera)
    rep1 = User(
        employee_code="GCT002",
        company_id=company.company_id,
        department_id=dept.department_id,
        designation_id=desig_rep.designation_id,
        manager_user_id=manager.user_id,
        first_name="Rohan",
        last_name="Gupta",
        official_email="rohan.g@gocompliance.test",
        mobile_number="+919888800002",
        date_of_joining=date(2023, 6, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        must_change_password=False,
    )
    # Sales Rep 2 (Reports to Meera)
    rep2 = User(
        employee_code="GCT003",
        company_id=company.company_id,
        department_id=dept.department_id,
        designation_id=desig_rep.designation_id,
        manager_user_id=manager.user_id,
        first_name="Simran",
        last_name="Kaur",
        official_email="simran.k@gocompliance.test",
        mobile_number="+919888800003",
        date_of_joining=date(2023, 6, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        must_change_password=False,
    )
    # Other Rep (Independent, not in Meera's team)
    other_rep = User(
        employee_code="GCT004",
        company_id=company.company_id,
        department_id=dept.department_id,
        designation_id=desig_rep.designation_id,
        first_name="Vikram",
        last_name="Singh",
        official_email="vikram.s@gocompliance.test",
        mobile_number="+919888800004",
        date_of_joining=date(2023, 6, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        must_change_password=False,
    )
    db_session.add_all([rep1, rep2, other_rep])
    db_session.flush()

    # Services
    srv1 = ServiceMaster(
        service_code="PVT_LTD_INC",
        service_name="Private Limited Company Incorporation",
        category="INCORPORATION",
        base_price=Decimal("15000.00"),
        govt_fee=Decimal("4000.00"),
        status="ACTIVE",
    )
    srv2 = ServiceMaster(
        service_code="GST_REG",
        service_name="GST Registration",
        category="REGISTRATION",
        base_price=Decimal("5000.00"),
        govt_fee=Decimal("1000.00"),
        status="ACTIVE",
    )
    db_session.add_all([srv1, srv2])
    db_session.flush()

    # Add required doc for srv1
    doc_req = ServiceRequiredDocument(
        service_id=srv1.service_id,
        document_code="PAN_CARD",
        document_name="PAN Card of Applicant",
        is_mandatory=True,
        display_order=1,
    )
    db_session.add(doc_req)
    db_session.flush()

    # Pre-existing client
    existing_client = ClientMaster(
        company_id=company.company_id,
        client_name="Apex Logistics Ltd",
        entity_type="Private Limited",
        contact_person="Rajesh Apex",
        contact_email="rajesh@apexlogistics.in",
        contact_phone="9876500001",
        created_by_user_id=rep1.user_id,
        status="ACTIVE",
    )
    db_session.add(existing_client)
    db_session.flush()

    # Operations Department and Designations
    dept_ops = Department(
        company_id=company.company_id,
        department_code="OPERATIONS",
        department_name="Operations Department",
        status="ACTIVE",
    )
    db_session.add(dept_ops)
    db_session.flush()

    desig_ops_head = Designation(
        company_id=company.company_id,
        designation_code="OPS_HEAD",
        designation_name="Operations Head",
        level_rank=10,
        status="ACTIVE",
    )
    desig_ops_exec = Designation(
        company_id=company.company_id,
        designation_code="OPS_EXEC",
        designation_name="Operations Executive",
        level_rank=4,
        status="ACTIVE",
    )
    db_session.add_all([desig_ops_head, desig_ops_exec])
    db_session.flush()

    # Karishma (Operations Manager / Head)
    karishma = User(
        employee_code="GCT005",
        company_id=company.company_id,
        department_id=dept_ops.department_id,
        designation_id=desig_ops_head.designation_id,
        first_name="Karishma",
        last_name="Upadhyay",
        official_email="karishma.u@gocompliance.test",
        mobile_number="+919888800005",
        date_of_joining=date(2023, 1, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        is_reporting_manager=True,
        must_change_password=False,
    )
    # Mansi (Operations Executive reporting to Karishma)
    mansi = User(
        employee_code="GCT006",
        company_id=company.company_id,
        department_id=dept_ops.department_id,
        designation_id=desig_ops_exec.designation_id,
        manager_user_id=None,
        first_name="Mansi",
        last_name="Sharma",
        official_email="mansi.s@gocompliance.test",
        mobile_number="+919888800006",
        date_of_joining=date(2023, 3, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        must_change_password=False,
    )
    db_session.add_all([karishma, mansi])
    db_session.flush()
    mansi.manager_user_id = karishma.user_id

    # Modules
    sales_root = Module(module_code="SALES", module_name="Sales", status="ACTIVE", display_order=10)
    sales_dash = Module(module_code="SALES_DASHBOARD", module_name="Sales Dashboard", status="ACTIVE", parent_module_id=sales_root.module_id, display_order=10)
    sales_my_orders = Module(module_code="SALES_MY_ORDERS", module_name="My Sales Orders", status="ACTIVE", parent_module_id=sales_root.module_id, display_order=20)
    sales_confirmed = Module(module_code="SALES_CONFIRMED_ORDER", module_name="Create Confirmed Order", status="ACTIVE", parent_module_id=sales_root.module_id, display_order=30)
    ops_root = Module(module_code="OPERATIONS", module_name="Operations", status="ACTIVE", display_order=20)
    db_session.add_all([sales_root, sales_dash, sales_my_orders, sales_confirmed, ops_root])
    db_session.flush()

    # Grant permissions:
    # Manager: TEAM scope on Sales
    for mod in [sales_root, sales_dash, sales_my_orders, sales_confirmed]:
        db_session.add(
            UserModulePermission(
                user_id=manager.user_id,
                module_id=mod.module_id,
                can_view=True,
                can_create=True,
                can_edit=True,
                can_delete=True,
                can_export=True,
                data_scope="TEAM",
                status="ACTIVE",
            )
        )

    # Rep 1: SELF scope on Sales
    for mod in [sales_root, sales_dash, sales_my_orders, sales_confirmed]:
        db_session.add(
            UserModulePermission(
                user_id=rep1.user_id,
                module_id=mod.module_id,
                can_view=True,
                can_create=True,
                can_edit=True,
                can_delete=False,
                can_export=True,
                data_scope="SELF",
                status="ACTIVE",
            )
        )

    # Other Rep: SELF scope on Sales
    for mod in [sales_root, sales_dash, sales_my_orders, sales_confirmed]:
        db_session.add(
            UserModulePermission(
                user_id=other_rep.user_id,
                module_id=mod.module_id,
                can_view=True,
                can_create=True,
                can_edit=True,
                can_delete=False,
                can_export=True,
                data_scope="SELF",
                status="ACTIVE",
            )
        )

    # Karishma: COMPANY/DEPARTMENT scope on Operations and SALES
    for mod in [ops_root, sales_root, sales_dash, sales_my_orders, sales_confirmed]:
        db_session.add(
            UserModulePermission(
                user_id=karishma.user_id,
                module_id=mod.module_id,
                can_view=True,
                can_create=True,
                can_edit=True,
                can_delete=True,
                can_export=True,
                data_scope="COMPANY",
                status="ACTIVE",
            )
        )

    # Mansi: SELF scope on Operations
    db_session.add(
        UserModulePermission(
            user_id=mansi.user_id,
            module_id=ops_root.module_id,
            can_view=True,
            can_create=True,
            can_edit=True,
            can_delete=False,
            can_export=False,
            data_scope="SELF",
            status="ACTIVE",
        )
    )

    db_session.flush()

    return {
        "company": company,
        "manager": manager,
        "rep1": rep1,
        "rep2": rep2,
        "other_rep": other_rep,
        "karishma": karishma,
        "mansi": mansi,
        "dept_ops": dept_ops,
        "srv1": srv1,
        "srv2": srv2,
        "existing_client": existing_client,
    }


def auth_headers(user: User) -> dict:
    """Generate Authorization headers with a valid JWT token."""
    token = create_access_token(
        user_id=user.user_id,
        token_version=user.token_version,
    )
    return {"Authorization": f"Bearer {token}"}


# =============================================================================
# 1. Calculation & Business Rule Tests
# =============================================================================

def test_sales_calculations_and_profit(client: TestClient, db_session: Session, sales_fixture: dict):
    """Verify Pending Amount, Payment Status, and Profits (Total - Govt - Incidental) calculation."""
    f = sales_fixture
    headers = auth_headers(f["rep1"])

    # Total = 50,000, Advance = 20,000, Govt = 5,000, Incidental = 2,000
    # Expected: Pending = 30,000, Payment Status = PARTIALLY_PAID, Profit = 43,000
    payload = {
        "client_name": "Calculated Enterprises",
        "contact_no": "9811122233",
        "service_id": str(f["srv1"].service_id),
        "lead_source": "WEBSITE",
        "order_date": date.today().isoformat(),
        "order_value": "50000.00",
        "amount_received": "20000.00",
        "govt_fees": "5000.00",
        "incidental_cost": "2000.00",
        "proforma_invoice_no": "PI-2026-001",
        "tax_invoice_no": "TI-2026-001",
        "reimbursement_note": "Client will reimburse stamp duty",
        "notes": "Verified calculation test",
    }

    resp = client.post("/api/sales/orders", json=payload, headers=headers)
    assert resp.status_code == 201, resp.text
    data = resp.json()

    assert Decimal(data["order_value"]) == Decimal("50000.00")
    assert Decimal(data["amount_received"]) == Decimal("20000.00")
    assert Decimal(data["balance_amount"]) == Decimal("30000.00")  # Pending Amount
    assert Decimal(data["govt_fees"]) == Decimal("5000.00")
    assert Decimal(data["incidental_cost"]) == Decimal("2000.00")
    assert Decimal(data["profit_amount"]) == Decimal("43000.00")  # Profits = 50000 - 5000 - 2000
    assert data["payment_status"] == "PARTIALLY_PAID"
    assert data["proforma_invoice_no"] == "PI-2026-001"
    assert data["tax_invoice_no"] == "TI-2026-001"
    assert data["reimbursement_note"] == "Client will reimburse stamp duty"


def test_payment_status_fully_paid_and_pending(client: TestClient, db_session: Session, sales_fixture: dict):
    """Verify payment status auto-computation for FULLY_PAID and PENDING."""
    f = sales_fixture
    headers = auth_headers(f["rep1"])

    # 1. Advance == Total -> FULLY_PAID
    payload_full = {
        "client_name": "Full Pay Co",
        "contact_no": "9811100011",
        "service_id": str(f["srv1"].service_id),
        "order_date": date.today().isoformat(),
        "order_value": "30000.00",
        "amount_received": "30000.00",
        "govt_fees": "3000.00",
        "incidental_cost": "1000.00",
    }
    resp1 = client.post("/api/sales/orders", json=payload_full, headers=headers)
    assert resp1.status_code == 201
    assert resp1.json()["payment_status"] == "FULLY_PAID"
    assert Decimal(resp1.json()["balance_amount"]) == Decimal("0.00")
    assert Decimal(resp1.json()["profit_amount"]) == Decimal("26000.00")

    # 2. Advance == 0 -> PENDING
    payload_pending = {
        "client_name": "Zero Pay Co",
        "contact_no": "9811100022",
        "service_id": str(f["srv1"].service_id),
        "order_date": date.today().isoformat(),
        "order_value": "25000.00",
        "amount_received": "0.00",
        "govt_fees": "2000.00",
        "incidental_cost": "0.00",
    }
    resp2 = client.post("/api/sales/orders", json=payload_pending, headers=headers)
    assert resp2.status_code == 201
    assert resp2.json()["payment_status"] == "PENDING"
    assert Decimal(resp2.json()["balance_amount"]) == Decimal("25000.00")
    assert Decimal(resp2.json()["profit_amount"]) == Decimal("23000.00")


def test_validation_rejects_advance_greater_than_total(client: TestClient, db_session: Session, sales_fixture: dict):
    """Verify that entering Advance Amount > Total Amount is rejected with 400 Bad Request."""
    f = sales_fixture
    headers = auth_headers(f["rep1"])

    payload = {
        "client_name": "Invalid Advance Co",
        "contact_no": "9811199999",
        "service_id": str(f["srv1"].service_id),
        "order_date": date.today().isoformat(),
        "order_value": "10000.00",
        "amount_received": "15000.00",  # Advance > Total
    }
    resp = client.post("/api/sales/orders", json=payload, headers=headers)
    assert resp.status_code in (400, 422)
    assert "Advance Amount cannot be greater than Total Amount" in resp.text


# =============================================================================
# 2. Client Matching & Deduplication Tests
# =============================================================================

def test_client_deduplication_reuses_existing_client(client: TestClient, db_session: Session, sales_fixture: dict):
    """Verify that entering an existing client's name or phone reuses the existing client record."""
    f = sales_fixture
    headers = auth_headers(f["rep1"])
    initial_client_count = db_session.query(ClientMaster).count()

    # Use matching existing client name
    payload = {
        "client_name": "Apex Logistics Ltd",  # Exact match to existing client
        "contact_no": "9876500001",
        "service_id": str(f["srv1"].service_id),
        "order_date": date.today().isoformat(),
        "order_value": "12000.00",
        "amount_received": "6000.00",
    }
    resp = client.post("/api/sales/orders", json=payload, headers=headers)
    assert resp.status_code == 201
    order_data = resp.json()

    # Must reuse existing client ID
    assert order_data["client_id"] == str(f["existing_client"].client_id)
    # Total clients in DB should not have increased
    assert db_session.query(ClientMaster).count() == initial_client_count


def test_new_client_created_when_no_match(client: TestClient, db_session: Session, sales_fixture: dict):
    """Verify that a new client record is created when client details do not match any existing client."""
    f = sales_fixture
    headers = auth_headers(f["rep1"])
    initial_client_count = db_session.query(ClientMaster).count()

    payload = {
        "client_name": "Brand New Enterprise",
        "contact_no": "9900011223",
        "service_id": str(f["srv1"].service_id),
        "order_date": date.today().isoformat(),
        "order_value": "18000.00",
        "amount_received": "9000.00",
    }
    resp = client.post("/api/sales/orders", json=payload, headers=headers)
    assert resp.status_code == 201

    assert db_session.query(ClientMaster).count() == initial_client_count + 1
    new_client = db_session.query(ClientMaster).filter(ClientMaster.client_name == "Brand New Enterprise").first()
    assert new_client is not None
    assert new_client.contact_phone == "9900011223"


# =============================================================================
# 3. RBAC & Data Scoping Tests
# =============================================================================

def test_salesperson_self_scope_isolation(client: TestClient, db_session: Session, sales_fixture: dict):
    """Verify Salesperson with SELF scope only sees their own orders in register."""
    f = sales_fixture
    rep1_headers = auth_headers(f["rep1"])
    other_headers = auth_headers(f["other_rep"])

    # Create order by rep1
    client.post(
        "/api/sales/orders",
        json={
            "client_name": "Rep1 Client",
            "contact_no": "9111100001",
            "service_id": str(f["srv1"].service_id),
            "order_date": date.today().isoformat(),
            "order_value": "20000.00",
            "amount_received": "10000.00",
        },
        headers=rep1_headers,
    )

    # Create order by other_rep
    client.post(
        "/api/sales/orders",
        json={
            "client_name": "Other Rep Client",
            "contact_no": "9111100002",
            "service_id": str(f["srv1"].service_id),
            "order_date": date.today().isoformat(),
            "order_value": "35000.00",
            "amount_received": "15000.00",
        },
        headers=other_headers,
    )

    # Rep1 queries register
    resp1 = client.get("/api/sales/register", headers=rep1_headers)
    assert resp1.status_code == 200
    data1 = resp1.json()
    assert len(data1["items"]) == 1
    assert data1["items"][0]["client_name"] == "Rep1 Client"

    # Other Rep queries register
    resp2 = client.get("/api/sales/register", headers=other_headers)
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert len(data2["items"]) == 1
    assert data2["items"][0]["client_name"] == "Other Rep Client"


def test_manager_team_scope_sees_team_records(client: TestClient, db_session: Session, sales_fixture: dict):
    """Verify Manager with TEAM scope sees orders of all subordinate team members."""
    f = sales_fixture
    mgr_headers = auth_headers(f["manager"])
    rep1_headers = auth_headers(f["rep1"])
    other_headers = auth_headers(f["other_rep"])

    # Order from Rep1 (in Manager's team)
    client.post(
        "/api/sales/orders",
        json={
            "client_name": "Team Rep1 Order",
            "contact_no": "9222200001",
            "service_id": str(f["srv1"].service_id),
            "order_date": date.today().isoformat(),
            "order_value": "40000.00",
            "amount_received": "20000.00",
        },
        headers=rep1_headers,
    )

    # Order from Other Rep (outside Manager's team)
    client.post(
        "/api/sales/orders",
        json={
            "client_name": "Outside Team Order",
            "contact_no": "9222200002",
            "service_id": str(f["srv1"].service_id),
            "order_date": date.today().isoformat(),
            "order_value": "60000.00",
            "amount_received": "30000.00",
        },
        headers=other_headers,
    )

    # Manager queries register -> should see team orders, but NOT outside team
    resp = client.get("/api/sales/register", headers=mgr_headers)
    assert resp.status_code == 200
    mgr_data = resp.json()
    client_names = [item["client_name"] for item in mgr_data["items"]]

    assert "Team Rep1 Order" in client_names
    assert "Outside Team Order" not in client_names


# =============================================================================
# 4. Operations Handoff (Draft vs Confirmed)
# =============================================================================

def test_save_as_draft_does_not_create_operation_task(client: TestClient, db_session: Session, sales_fixture: dict):
    """Verify saving a sales entry in draft mode does not trigger operations handoff."""
    f = sales_fixture
    headers = auth_headers(f["rep1"])
    initial_app_count = db_session.query(OperationApplication).count()

    payload = {
        "client_name": "Draft Client",
        "contact_no": "9333300001",
        "service_id": str(f["srv1"].service_id),
        "order_date": date.today().isoformat(),
        "order_value": "15000.00",
        "amount_received": "5000.00",
        "auto_confirm": False,  # Save as draft
    }
    resp = client.post("/api/sales/orders", json=payload, headers=headers)
    assert resp.status_code == 201
    assert resp.json()["confirmation_status"] == "DRAFT"
    assert resp.json()["application_id"] is None

    # No new Operations application created
    assert db_session.query(OperationApplication).count() == initial_app_count


def test_save_and_confirm_creates_operations_application(client: TestClient, db_session: Session, sales_fixture: dict):
    """Verify saving with auto_confirm=True immediately triggers operations application handoff."""
    f = sales_fixture
    headers = auth_headers(f["rep1"])
    initial_app_count = db_session.query(OperationApplication).count()

    payload = {
        "client_name": "Confirmed Client",
        "contact_no": "9333300002",
        "service_id": str(f["srv1"].service_id),
        "order_date": date.today().isoformat(),
        "order_value": "25000.00",
        "amount_received": "25000.00",
        "auto_confirm": True,  # Save and confirm
    }
    resp = client.post("/api/sales/orders", json=payload, headers=headers)
    assert resp.status_code == 201
    data = resp.json()

    assert data["confirmation_status"] == "CONFIRMED"
    assert data["application_id"] is not None
    assert data["application_number"].startswith("AP-")
    assert data["operation_status"] == "ASSIGNED"
    assert data["assigned_to_user_id"] == str(f["mansi"].user_id)
    assert db_session.query(OperationApplication).count() == initial_app_count + 1


# =============================================================================
# 5. Form Options & Register CSV Export Endpoints
# =============================================================================

def test_form_options_endpoint(client: TestClient, db_session: Session, sales_fixture: dict):
    """Verify /api/sales/form-options returns services, permitted salespersons, and clients."""
    f = sales_fixture
    rep1_headers = auth_headers(f["rep1"])
    mgr_headers = auth_headers(f["manager"])

    # Rep1 (SELF): can_select_salesperson = False, default = Rep1
    resp1 = client.get("/api/sales/form-options", headers=rep1_headers)
    assert resp1.status_code == 200
    data1 = resp1.json()
    assert len(data1["services"]) >= 2
    assert data1["can_select_salesperson"] is False
    assert data1["default_salesperson_id"] == str(f["rep1"].user_id)

    # Manager (TEAM): can_select_salesperson = True, includes team reps
    resp2 = client.get("/api/sales/form-options", headers=mgr_headers)
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert data2["can_select_salesperson"] is True
    emp_ids = [e["user_id"] for e in data2["salespersons"]]
    assert str(f["rep1"].user_id) in emp_ids
    assert str(f["rep2"].user_id) in emp_ids


def test_sales_register_csv_export(client: TestClient, db_session: Session, sales_fixture: dict):
    """Verify /api/sales/register/export returns 20-column CSV with proper headers."""
    f = sales_fixture
    headers = auth_headers(f["rep1"])

    # Seed one order
    client.post(
        "/api/sales/orders",
        json={
            "client_name": "Export Test Client",
            "contact_no": "9444400001",
            "service_id": str(f["srv1"].service_id),
            "order_date": date.today().isoformat(),
            "order_value": "45000.00",
            "amount_received": "15000.00",
            "govt_fees": "4000.00",
            "incidental_cost": "1000.00",
            "proforma_invoice_no": "PI-EXPORT-01",
            "tax_invoice_no": "TI-EXPORT-01",
            "reimbursement_note": "Reimburse filing",
            "notes": "CSV export check",
        },
        headers=headers,
    )

    resp = client.get("/api/sales/register/export", headers=headers)
    assert resp.status_code == 200
    assert "text/csv" in resp.headers["Content-Type"]
    csv_text = resp.text

    # Check 20 headers in exact order
    first_line = csv_text.strip().splitlines()[0]
    expected_headers = [
        "S.No",
        "Date",
        "Client Name",
        "Contact No",
        "Source",
        "Work",
        "Converted By",
        "Assigned To",
        "Work Status",
        "Total Amount",
        "Advance Amount",
        "Pending Amount",
        "Payment Status",
        "Proforma Invoice No.",
        "Tax Invoice No.",
        "Reimbursement Note",
        "Govt Fees",
        "Incidental Cost",
        "Profits",
        "Remarks",
    ]
    assert first_line == ",".join(expected_headers)
    assert "Export Test Client" in csv_text
    assert "40000.00" in csv_text  # Profits: 45000 - 4000 - 1000 = 40000


# =============================================================================
# 6. Operations Assignment Flow & Clean Initial State
# =============================================================================

def test_sales_entry_initial_unassigned_and_empty_invoicing_notes(
    client: TestClient, db_session: Session, sales_fixture: dict
):
    """Verify initial sales entry auto-assigns to Operations Lead (Mansi) by default and unpopulated invoice/remarks fields remain empty."""
    f = sales_fixture
    headers = auth_headers(f["rep1"])

    # Sales rep enters core details without any invoicing or notes
    payload = {
        "client_name": "Clean Entry Technologies Pvt Ltd",
        "contact_no": "9876500111",
        "service_id": str(f["srv1"].service_id),
        "lead_source": "DIRECT",
        "order_date": date.today().isoformat(),
        "order_value": "30000.00",
        "amount_received": "10000.00",
        "govt_fees": "3000.00",
        "incidental_cost": "500.00",
        "auto_confirm": True,
    }

    resp = client.post("/api/sales/orders", json=payload, headers=headers)
    assert resp.status_code == 201
    created_order = resp.json()

    # Initial state auto-assigns to Mansi by default
    assert created_order["assigned_to_user_id"] == str(f["mansi"].user_id)
    assert created_order["assigned_to_name"] == "Mansi Sharma"
    assert created_order["operation_status"] == "ASSIGNED"
    assert created_order["proforma_invoice_no"] is None
    assert created_order["tax_invoice_no"] is None
    assert created_order["reimbursement_note"] is None
    assert created_order["notes"] is None

    # Fetch Sales Register
    reg_resp = client.get("/api/sales/register", headers=headers)
    assert reg_resp.status_code == 200
    items = reg_resp.json()["items"]
    clean_item = next(i for i in items if i["client_name"] == "Clean Entry Technologies Pvt Ltd")

    assert clean_item["assigned_to_name"] == "Mansi Sharma"
    assert clean_item["assigned_to_user_id"] == str(f["mansi"].user_id)
    assert clean_item["work_status"] == "ASSIGNED"
    assert clean_item["salesperson_name"] == "Rohan Gupta"  # Converted By
    assert clean_item["proforma_invoice_no"] is None
    assert clean_item["tax_invoice_no"] is None
    assert clean_item["reimbursement_note"] is None
    assert clean_item["remarks"] is None


def test_operations_assignees_endpoint(client: TestClient, db_session: Session, sales_fixture: dict):
    """Verify /api/sales/operations-assignees returns eligible Operations employees only."""
    f = sales_fixture
    karishma_headers = auth_headers(f["karishma"])

    resp = client.get("/api/sales/operations-assignees", headers=karishma_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1

    ops_names = [emp["full_name"] for emp in data]
    assert "Mansi Sharma" in ops_names
    assert "Karishma Upadhyay" in ops_names


def test_operations_manager_assigns_order_to_ops_member(
    client: TestClient, db_session: Session, sales_fixture: dict
):
    """Verify Karishma (Operations Head) can assign a confirmed sales order to Mansi (Operations Exec)."""
    f = sales_fixture
    rep1_headers = auth_headers(f["rep1"])
    karishma_headers = auth_headers(f["karishma"])

    # 1. Rep1 creates a confirmed order
    create_payload = {
        "client_name": "Zenith Cloud Solutions",
        "contact_no": "9812345678",
        "service_id": str(f["srv1"].service_id),
        "order_date": date.today().isoformat(),
        "order_value": "40000.00",
        "amount_received": "20000.00",
        "auto_confirm": True,
    }
    create_resp = client.post("/api/sales/orders", json=create_payload, headers=rep1_headers)
    assert create_resp.status_code == 201
    order_id = create_resp.json()["order_id"]

    # 2. Karishma assigns the order to Mansi
    target_date = (date.today() + timedelta(days=5)).isoformat()
    assign_payload = {
        "assigned_to_user_id": str(f["mansi"].user_id),
        "target_completion_date": target_date,
        "priority": "HIGH",
        "handover_notes": "Expedite filing for Zenith Cloud Solutions",
    }
    assign_resp = client.post(f"/api/sales/orders/{order_id}/assign", json=assign_payload, headers=karishma_headers)
    assert assign_resp.status_code == 200, assign_resp.text
    assigned_data = assign_resp.json()

    assert assigned_data["assigned_to_user_id"] == str(f["mansi"].user_id)
    assert assigned_data["assigned_to_name"] == "Mansi Sharma"
    assert assigned_data["operation_status"] == "ASSIGNED"

    # 3. Check Register: Converted By is Rohan Gupta, Assigned To is Mansi Sharma
    reg_resp = client.get("/api/sales/register", headers=karishma_headers)
    assert reg_resp.status_code == 200
    zenith_item = next(i for i in reg_resp.json()["items"] if i["order_id"] == order_id)
    assert zenith_item["salesperson_name"] == "Rohan Gupta"  # Converted By
    assert zenith_item["assigned_to_name"] == "Mansi Sharma"  # Assigned To
    assert zenith_item["work_status"] == "ASSIGNED"


def test_unauthorized_user_cannot_assign_sales_order(
    client: TestClient, db_session: Session, sales_fixture: dict
):
    """Verify order creator can assign to operations employee, while unrelated salespeople cannot."""
    f = sales_fixture
    rep1_headers = auth_headers(f["rep1"])
    rep2_headers = auth_headers(f["rep2"])

    # Create order by rep1
    create_resp = client.post(
        "/api/sales/orders",
        json={
            "client_name": "Permission Test Corp",
            "contact_no": "9988776655",
            "service_id": str(f["srv1"].service_id),
            "order_date": date.today().isoformat(),
            "order_value": "20000.00",
            "amount_received": "20000.00",
            "auto_confirm": True,
        },
        headers=rep1_headers,
    )
    assert create_resp.status_code == 201
    order_id = create_resp.json()["order_id"]

    # Rep2 (unrelated sales rep who did not create the order) tries to assign -> 403
    unauth_assign_resp = client.post(
        f"/api/sales/orders/{order_id}/assign",
        json={"assigned_to_user_id": str(f["mansi"].user_id), "priority": "HIGH"},
        headers=rep2_headers,
    )
    assert unauth_assign_resp.status_code == 403

    # Creator rep1 assigns to operations employee Mansi -> 200 OK
    rep1_assign_resp = client.post(
        f"/api/sales/orders/{order_id}/assign",
        json={"assigned_to_user_id": str(f["mansi"].user_id), "priority": "HIGH"},
        headers=rep1_headers,
    )
    assert rep1_assign_resp.status_code == 200
    assert rep1_assign_resp.json()["assigned_to_user_id"] == str(f["mansi"].user_id)
    assert rep1_assign_resp.json()["assigned_to_name"] == "Mansi Sharma"


def test_lead_sources_justdial_and_indiamart(
    client: TestClient, db_session: Session, sales_fixture: dict
):
    """Verify JUSTDIAL and INDIAMART lead sources in form options, order creation, register, and filters."""
    f = sales_fixture
    rep1_headers = auth_headers(f["rep1"])

    # 1. Check form options includes JUSTDIAL and INDIAMART
    opts_resp = client.get("/api/sales/form-options", headers=rep1_headers)
    assert opts_resp.status_code == 200
    sources = opts_resp.json()["lead_sources"]
    assert "JUSTDIAL" in sources
    assert "INDIAMART" in sources

    # 2. Create order with JUSTDIAL
    jd_resp = client.post(
        "/api/sales/orders",
        json={
            "client_name": "Justdial Client Ltd",
            "contact_no": "9123456780",
            "service_id": str(f["srv1"].service_id),
            "lead_source": "JUSTDIAL",
            "order_date": date.today().isoformat(),
            "order_value": "35000.00",
            "amount_received": "15000.00",
            "govt_fees": "4000.00",
            "incidental_cost": "1000.00",
            "auto_confirm": True,
        },
        headers=rep1_headers,
    )
    assert jd_resp.status_code == 201
    jd_order = jd_resp.json()
    assert jd_order["lead_source"] == "JUSTDIAL"
    assert Decimal(str(jd_order["profit_amount"])) == Decimal("30000.00")
    assert Decimal(str(jd_order["balance_amount"])) == Decimal("20000.00")

    # 3. Create order with INDIAMART
    im_resp = client.post(
        "/api/sales/orders",
        json={
            "client_name": "IndiaMART Supplier Pvt Ltd",
            "contact_no": "9123456781",
            "service_id": str(f["srv2"].service_id),
            "lead_source": "INDIAMART",
            "order_date": date.today().isoformat(),
            "order_value": "18000.00",
            "amount_received": "18000.00",
            "govt_fees": "2000.00",
            "incidental_cost": "500.00",
            "auto_confirm": True,
        },
        headers=rep1_headers,
    )
    assert im_resp.status_code == 201
    im_order = im_resp.json()
    assert im_order["lead_source"] == "INDIAMART"
    assert Decimal(str(im_order["profit_amount"])) == Decimal("15500.00")
    assert Decimal(str(im_order["balance_amount"])) == Decimal("0.00")

    # 4. Filter register by JUSTDIAL
    jd_filter_resp = client.get("/api/sales/register?lead_source=JUSTDIAL", headers=rep1_headers)
    assert jd_filter_resp.status_code == 200
    jd_items = jd_filter_resp.json()["items"]
    assert any(item["order_id"] == jd_order["order_id"] for item in jd_items)
    assert all(item["lead_source"] == "JUSTDIAL" for item in jd_items)

    # 5. Filter register by INDIAMART
    im_filter_resp = client.get("/api/sales/register?lead_source=INDIAMART", headers=rep1_headers)
    assert im_filter_resp.status_code == 200
    im_items = im_filter_resp.json()["items"]
    assert any(item["order_id"] == im_order["order_id"] for item in im_items)
    assert all(item["lead_source"] == "INDIAMART" for item in im_items)


def test_custom_service_pricing_and_calculated_financials(
    client: TestClient, db_session: Session, sales_fixture: dict
):
    """Verify salesperson can quote different prices for the same service and verify pending/profit calculations."""
    f = sales_fixture
    rep1_headers = auth_headers(f["rep1"])
    srv_id = str(f["srv1"].service_id)

    # Client A: Quoted 50,000 (Govt fees 5,000, Incidental 1,500, Advance 20,000)
    order_a_resp = client.post(
        "/api/sales/orders",
        json={
            "client_name": "Premium Client A",
            "contact_no": "9811111111",
            "service_id": srv_id,
            "order_date": date.today().isoformat(),
            "order_value": "50000.00",
            "amount_received": "20000.00",
            "govt_fees": "5000.00",
            "incidental_cost": "1500.00",
            "auto_confirm": True,
        },
        headers=rep1_headers,
    )
    assert order_a_resp.status_code == 201
    order_a = order_a_resp.json()
    assert Decimal(str(order_a["order_value"])) == Decimal("50000.00")
    assert Decimal(str(order_a["amount_received"])) == Decimal("20000.00")
    assert Decimal(str(order_a["balance_amount"])) == Decimal("30000.00")  # 50000 - 20000
    assert Decimal(str(order_a["profit_amount"])) == Decimal("43500.00")  # 50000 - 5000 - 1500

    # Client B: Quoted 25,000 (Govt fees 3,000, Incidental 500, Advance 10,000) for same service
    order_b_resp = client.post(
        "/api/sales/orders",
        json={
            "client_name": "Discounted Client B",
            "contact_no": "9822222222",
            "service_id": srv_id,
            "order_date": date.today().isoformat(),
            "order_value": "25000.00",
            "amount_received": "10000.00",
            "govt_fees": "3000.00",
            "incidental_cost": "500.00",
            "auto_confirm": True,
        },
        headers=rep1_headers,
    )
    assert order_b_resp.status_code == 201
    order_b = order_b_resp.json()
    assert Decimal(str(order_b["order_value"])) == Decimal("25000.00")
    assert Decimal(str(order_b["amount_received"])) == Decimal("10000.00")
    assert Decimal(str(order_b["balance_amount"])) == Decimal("15000.00")  # 25000 - 10000
    assert Decimal(str(order_b["profit_amount"])) == Decimal("21500.00")  # 25000 - 3000 - 500


def test_order_creator_can_assign_to_operations_manager_and_shows_in_ops_list(
    client: TestClient, db_session: Session, sales_fixture: dict
):
    """Verify order creator assigning order to Mansi appears in Mansi's Operations tasks list."""
    f = sales_fixture
    rep1_headers = auth_headers(f["rep1"])
    mansi_headers = auth_headers(f["mansi"])

    # Create order
    create_resp = client.post(
        "/api/sales/orders",
        json={
            "client_name": "Apex Work Flow Corp",
            "contact_no": "9876543210",
            "service_id": str(f["srv1"].service_id),
            "order_date": date.today().isoformat(),
            "order_value": "45000.00",
            "amount_received": "45000.00",
            "auto_confirm": True,
        },
        headers=rep1_headers,
    )
    assert create_resp.status_code == 201
    order_id = create_resp.json()["order_id"]

    # Rep1 assigns order to Mansi
    assign_resp = client.post(
        f"/api/sales/orders/{order_id}/assign",
        json={
            "assignee_user_id": str(f["mansi"].user_id),
            "priority": "HIGH",
            "notes": "Urgent incorporation client from Justdial",
        },
        headers=rep1_headers,
    )
    assert assign_resp.status_code == 200
    assigned_data = assign_resp.json()
    assert assigned_data["assigned_to_user_id"] == str(f["mansi"].user_id)
    assert assigned_data["assigned_to_name"] == "Mansi Sharma"

    # Query Operations tasks as Mansi
    ops_resp = client.get("/api/operations/tasks", headers=mansi_headers)
    assert ops_resp.status_code == 200
    ops_items = ops_resp.json()["items"]
    matched = [item for item in ops_items if item["client_name"] == "Apex Work Flow Corp"]
    assert len(matched) == 1
    assert matched[0]["assigned_to_user_id"] == str(f["mansi"].user_id)
    assert matched[0]["priority"] == "HIGH"

    # Query My Tasks as Mansi
    my_tasks_resp = client.get("/api/operations/tasks/my-tasks", headers=mansi_headers)
    assert my_tasks_resp.status_code == 200
    my_items = my_tasks_resp.json()["items"]
    matched_my = [item for item in my_items if item["client_name"] == "Apex Work Flow Corp"]
    assert len(matched_my) == 1


def test_owner_salesperson_can_edit_sales_order(
    client: TestClient, db_session: Session, sales_fixture: dict
):
    """Test authorized salesperson owner can edit financial and sales fields."""
    f = sales_fixture
    rep1_headers = auth_headers(f["rep1"])

    create_resp = client.post(
        "/api/sales/orders",
        json={
            "client_name": "Editable Client Alpha",
            "contact_no": "9811111111",
            "service_id": str(f["srv1"].service_id),
            "order_date": date.today().isoformat(),
            "order_value": "40000.00",
            "amount_received": "15000.00",
            "govt_fees": "3000.00",
            "incidental_cost": "1000.00",
            "auto_confirm": True,
        },
        headers=rep1_headers,
    )
    assert create_resp.status_code == 201
    order_id = create_resp.json()["order_id"]

    # Rep1 updates financial fields, invoice details, remarks
    edit_resp = client.put(
        f"/api/sales/orders/{order_id}",
        json={
            "order_value": "50000.00",
            "amount_received": "50000.00",
            "govt_fees": "4000.00",
            "incidental_cost": "1500.00",
            "proforma_invoice_no": "PI-2026-0099",
            "tax_invoice_no": "INV-2026-0099",
            "reimbursement_note": "Courier & Stamp Duty reimbursed",
            "notes": "Payment received in full via NEFT",
            "lead_source": "INDIAMART",
        },
        headers=rep1_headers,
    )
    assert edit_resp.status_code == 200
    updated = edit_resp.json()
    assert Decimal(str(updated["order_value"])) == Decimal("50000.00")
    assert Decimal(str(updated["amount_received"])) == Decimal("50000.00")
    assert Decimal(str(updated["balance_amount"])) == Decimal("0.00")
    assert Decimal(str(updated["govt_fees"])) == Decimal("4000.00")
    assert Decimal(str(updated["incidental_cost"])) == Decimal("1500.00")
    assert Decimal(str(updated["profit_amount"])) == Decimal("44500.00")  # 50000 - 4000 - 1500
    assert updated["payment_status"] == "FULLY_PAID"
    assert updated["proforma_invoice_no"] == "PI-2026-0099"
    assert updated["tax_invoice_no"] == "INV-2026-0099"
    assert updated["reimbursement_note"] == "Courier & Stamp Duty reimbursed"
    assert updated["notes"] == "Payment received in full via NEFT"
    assert updated["lead_source"] == "INDIAMART"


def test_non_owner_forbidden_from_editing_sales_order(
    client: TestClient, db_session: Session, sales_fixture: dict
):
    """Test non-owner salesperson with SELF scope cannot edit someone else's order."""
    f = sales_fixture
    rep1_headers = auth_headers(f["rep1"])
    other_rep_headers = auth_headers(f["other_rep"])

    create_resp = client.post(
        "/api/sales/orders",
        json={
            "client_name": "Rep1 Private Client",
            "contact_no": "9812345678",
            "service_id": str(f["srv1"].service_id),
            "order_date": date.today().isoformat(),
            "order_value": "30000.00",
            "amount_received": "10000.00",
            "auto_confirm": True,
        },
        headers=rep1_headers,
    )
    assert create_resp.status_code == 201
    order_id = create_resp.json()["order_id"]

    # other_rep attempts to update Rep1's order
    edit_resp = client.put(
        f"/api/sales/orders/{order_id}",
        json={
            "order_value": "35000.00",
            "amount_received": "20000.00",
        },
        headers=other_rep_headers,
    )
    assert edit_resp.status_code == 403
    assert "not authorized" in edit_resp.json()["detail"].lower()


def test_manager_and_admin_can_edit_sales_orders(
    client: TestClient, db_session: Session, sales_fixture: dict
):
    """Test Manager (TEAM scope) and Director/Admin can edit subordinate sales orders."""
    f = sales_fixture
    rep1_headers = auth_headers(f["rep1"])
    mgr_headers = auth_headers(f["manager"])
    karishma_headers = auth_headers(f["karishma"])

    create_resp = client.post(
        "/api/sales/orders",
        json={
            "client_name": "Team Scope Client",
            "contact_no": "9833333333",
            "service_id": str(f["srv1"].service_id),
            "order_date": date.today().isoformat(),
            "order_value": "60000.00",
            "amount_received": "20000.00",
            "auto_confirm": True,
        },
        headers=rep1_headers,
    )
    assert create_resp.status_code == 201
    order_id = create_resp.json()["order_id"]

    # Manager edits order
    mgr_edit_resp = client.put(
        f"/api/sales/orders/{order_id}",
        json={
            "order_value": "65000.00",
            "amount_received": "30000.00",
            "notes": "Manager approved discount adjustment",
        },
        headers=mgr_headers,
    )
    assert mgr_edit_resp.status_code == 200
    assert Decimal(str(mgr_edit_resp.json()["order_value"])) == Decimal("65000.00")
    assert Decimal(str(mgr_edit_resp.json()["balance_amount"])) == Decimal("35000.00")

    # Karishma (Company scope) edits order
    admin_edit_resp = client.put(
        f"/api/sales/orders/{order_id}",
        json={
            "order_value": "70000.00",
            "amount_received": "70000.00",
            "tax_invoice_no": "INV-ADMIN-01",
        },
        headers=karishma_headers,
    )
    assert admin_edit_resp.status_code == 200
    assert Decimal(str(admin_edit_resp.json()["order_value"])) == Decimal("70000.00")
    assert admin_edit_resp.json()["payment_status"] == "FULLY_PAID"


def test_sales_edit_allowed_when_operations_task_is_completed(
    client: TestClient, db_session: Session, sales_fixture: dict
):
    """Test editing sales fields is not locked when Operations task is APPROVED/COMPLETED."""
    f = sales_fixture
    rep1_headers = auth_headers(f["rep1"])

    create_resp = client.post(
        "/api/sales/orders",
        json={
            "client_name": "Completed Ops Client",
            "contact_no": "9844444444",
            "service_id": str(f["srv1"].service_id),
            "order_date": date.today().isoformat(),
            "order_value": "80000.00",
            "amount_received": "40000.00",
            "auto_confirm": True,
        },
        headers=rep1_headers,
    )
    assert create_resp.status_code == 201
    order_id = uuid.UUID(create_resp.json()["order_id"])

    # Simulate Operations completion (task marked APPROVED / COMPLETED)
    order = db_session.get(SalesOrder, order_id)
    assert order.application is not None
    order.application.application_status = "APPROVED"
    db_session.commit()

    # Sales rep updates final payment after license issuance
    edit_resp = client.put(
        f"/api/sales/orders/{order_id}",
        json={
            "amount_received": "80000.00",
            "tax_invoice_no": "TAX-FINAL-888",
            "notes": "Client cleared remaining 50% upon license delivery",
        },
        headers=rep1_headers,
    )
    assert edit_resp.status_code == 200
    updated = edit_resp.json()
    assert Decimal(str(updated["amount_received"])) == Decimal("80000.00")
    assert Decimal(str(updated["balance_amount"])) == Decimal("0.00")
    assert updated["payment_status"] == "FULLY_PAID"
    # Verify Operations status was NOT changed or reverted
    assert updated["work_status"] == "APPROVED"
    assert updated["operation_status"] == "APPROVED"


def test_sales_edit_validation_rejects_negative_and_excessive_advance(
    client: TestClient, db_session: Session, sales_fixture: dict
):
    """Test validation errors for invalid amounts."""
    f = sales_fixture
    rep1_headers = auth_headers(f["rep1"])

    create_resp = client.post(
        "/api/sales/orders",
        json={
            "client_name": "Validation Test Client",
            "contact_no": "9855555555",
            "service_id": str(f["srv1"].service_id),
            "order_date": date.today().isoformat(),
            "order_value": "50000.00",
            "amount_received": "20000.00",
            "auto_confirm": True,
        },
        headers=rep1_headers,
    )
    assert create_resp.status_code == 201
    order_id = create_resp.json()["order_id"]

    # Reject Advance > Total
    bad_advance_resp = client.put(
        f"/api/sales/orders/{order_id}",
        json={
            "order_value": "50000.00",
            "amount_received": "60000.00",
        },
        headers=rep1_headers,
    )
    assert bad_advance_resp.status_code in (400, 422)

    # Reject Negative Total Amount
    neg_total_resp = client.put(
        f"/api/sales/orders/{order_id}",
        json={
            "order_value": "-1000.00",
        },
        headers=rep1_headers,
    )
    assert neg_total_resp.status_code in (400, 422)


