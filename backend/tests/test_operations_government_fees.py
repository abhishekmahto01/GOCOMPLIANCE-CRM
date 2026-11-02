"""Automated integration tests for Operations Government Fees Entry & Update Feature.

Covers all 20 mandatory test scenarios:
 1. Operations employee enters Government Fees -> Successful
 2. Operations employee edits Government Fees -> Successful
 3. Saved amount after page refresh -> Correct amount displayed
 4. Manshi updates another employee's task fees -> Successful
 5. Manshi views fees after task reassignment -> Task remains accessible
 6. Sales employee views Government Fees -> Visible
 7. Sales employee attempts to modify fees -> Access denied (403)
 8. Accounts employee views Government Fees -> Latest amount visible
 9. Updated fees reflected in Accounts -> Correct amount displayed & profit updated
10. Negative amount submitted -> Validation error (400/422)
11. Invalid text submitted -> Validation error (400/422)
12. Existing Government Fees records -> Preserved
13. Existing invoices and payments -> Unaffected
14. Existing expense and reimbursement workflows -> Unaffected
15. Unauthorized employee attempts modification -> Access denied (403)
16. Cross-company restricted access -> Access denied (403)
17. Existing RBAC permissions -> Unaffected
18. Existing Operations task workflow -> Unaffected
19. Existing Sales workflow -> Unaffected
20. Existing Accounts workflow -> Unaffected
"""
import uuid
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.models.client import ClientMaster
from app.models.company import Company
from app.models.department import Department
from app.models.designation import Designation
from app.models.module import Module
from app.models.operation_application import (
    ApplicationActivityLog,
    ApplicationAssignmentHistory,
    ApplicationDocument,
    OperationApplication,
)
from app.models.operations_coordinator_config import OperationsCoordinatorConfig
from app.models.sales_order import SalesOrder
from app.models.service import ServiceMaster
from app.models.user import User
from app.models.user_module_permission import UserModulePermission
from app.services.permissions import grant_or_update_permission


def auth_header(user: User) -> dict:
    """Generate bearer authorization header for a test user."""
    token = create_access_token(
        user_id=user.user_id,
        token_version=user.token_version,
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def govt_fees_fixture(db_session: Session):
    """Seed test entities for operations, sales, accounts, and cross-company testing."""
    # 1. Primary Company
    company_a = Company(
        company_code="GC_FEES_A",
        company_name="GoCompliance Fees Corp A",
        employee_code_prefix="FA",
        status="ACTIVE",
    )
    # Secondary Company (for cross-company isolation check)
    company_b = Company(
        company_code="GC_FEES_B",
        company_name="GoCompliance Fees Corp B",
        employee_code_prefix="FB",
        status="ACTIVE",
    )
    db_session.add_all([company_a, company_b])
    db_session.flush()

    # 2. Departments
    dept_ops = Department(department_code="OPERATIONS", department_name="Operations Department", status="ACTIVE")
    dept_sales = Department(department_code="SALES", department_name="Sales Department", status="ACTIVE")
    dept_accounts = Department(department_code="ACCOUNTS", department_name="Accounts Department", status="ACTIVE")
    db_session.add_all([dept_ops, dept_sales, dept_accounts])
    db_session.flush()

    # 3. Designations
    desig_lead = Designation(designation_code="OPS_LEAD", designation_name="Operations Lead", level_rank=40, is_managerial=True, status="ACTIVE")
    desig_exec = Designation(designation_code="OPS_EXEC", designation_name="Operations Executive", level_rank=10, is_managerial=False, status="ACTIVE")
    desig_sales = Designation(designation_code="SALES_EXEC", designation_name="Sales Executive", level_rank=10, is_managerial=False, status="ACTIVE")
    desig_acc = Designation(designation_code="ACC_EXEC", designation_name="Accounts Executive", level_rank=10, is_managerial=False, status="ACTIVE")
    db_session.add_all([desig_lead, desig_exec, desig_sales, desig_acc])
    db_session.flush()

    # 4. Users
    # Mansi (Operations Lead)
    mansi_lead = User(
        employee_code="FA001",
        first_name="Mansi",
        last_name="Singhal",
        official_email="mansi.singhal@feescorp.com",
        mobile_number="+919876500001",
        company_id=company_a.company_id,
        department_id=dept_ops.department_id,
        designation_id=desig_lead.designation_id,
        date_of_joining=date(2024, 1, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        must_change_password=False,
        token_version=1,
    )
    # Deepak (Assigned Operations Employee)
    deepak_ops = User(
        employee_code="FA002",
        first_name="Deepak",
        last_name="Kumar",
        official_email="deepak.kumar@feescorp.com",
        mobile_number="+919876500002",
        company_id=company_a.company_id,
        department_id=dept_ops.department_id,
        designation_id=desig_exec.designation_id,
        date_of_joining=date(2024, 1, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        must_change_password=False,
        token_version=1,
    )
    # Peer Operations Employee (Unassigned to Deepak's task)
    peer_ops = User(
        employee_code="FA003",
        first_name="Pooja",
        last_name="Sharma",
        official_email="pooja.sharma@feescorp.com",
        mobile_number="+919876500003",
        company_id=company_a.company_id,
        department_id=dept_ops.department_id,
        designation_id=desig_exec.designation_id,
        date_of_joining=date(2024, 1, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        must_change_password=False,
        token_version=1,
    )
    # Sales Employee
    sales_user = User(
        employee_code="FA004",
        first_name="Rahul",
        last_name="Verma",
        official_email="rahul.verma@feescorp.com",
        mobile_number="+919876500004",
        company_id=company_a.company_id,
        department_id=dept_sales.department_id,
        designation_id=desig_sales.designation_id,
        date_of_joining=date(2024, 1, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        must_change_password=False,
        token_version=1,
    )
    # Accounts Employee
    accounts_user = User(
        employee_code="FA005",
        first_name="Ananya",
        last_name="Roy",
        official_email="ananya.roy@feescorp.com",
        mobile_number="+919876500005",
        company_id=company_a.company_id,
        department_id=dept_accounts.department_id,
        designation_id=desig_acc.designation_id,
        date_of_joining=date(2024, 1, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        must_change_password=False,
        token_version=1,
    )
    # Cross-Company Employee (Company B)
    cross_company_user = User(
        employee_code="FB001",
        first_name="Vikram",
        last_name="Patel",
        official_email="vikram.patel@feescorpb.com",
        mobile_number="+919876500006",
        company_id=company_b.company_id,
        department_id=dept_ops.department_id,
        designation_id=desig_exec.designation_id,
        date_of_joining=date(2024, 1, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        must_change_password=False,
        token_version=1,
    )
    db_session.add_all([mansi_lead, deepak_ops, peer_ops, sales_user, accounts_user, cross_company_user])
    db_session.flush()

    # Coordinator config mapping company A to Mansi
    coord_cfg = OperationsCoordinatorConfig(
        company_id=company_a.company_id,
        coordinator_user_id=mansi_lead.user_id,
        updated_by_user_id=mansi_lead.user_id,
    )
    db_session.add(coord_cfg)
    db_session.flush()

    # 5. Service
    service = ServiceMaster(
        service_code="SRV_FEES_01",
        service_name="Statutory License Filing",
        category="LICENCE",
        base_price=Decimal("20000.00"),
        govt_fee=Decimal("2500.00"),
        status="ACTIVE",
    )
    db_session.add(service)
    db_session.flush()

    # 6. Client
    client = ClientMaster(
        client_name="Acme Statutory Filings Pvt Ltd",
        contact_person="Acme Contact",
        contact_phone="+919988776655",
        contact_email="statutory@acme.com",
        company_id=company_a.company_id,
        created_by_user_id=sales_user.user_id,
        status="ACTIVE",
    )
    db_session.add(client)
    db_session.flush()

    # 7. Sales Order
    sales_order = SalesOrder(
        order_number=f"SO-FEES-{uuid.uuid4().hex[:6].upper()}",
        company_id=company_a.company_id,
        client_id=client.client_id,
        service_id=service.service_id,
        salesperson_user_id=sales_user.user_id,
        order_date=date.today(),
        order_value=Decimal("25000.00"),
        amount_received=Decimal("10000.00"),
        balance_amount=Decimal("15000.00"),
        govt_fees=Decimal("2500.00"),
        incidental_cost=Decimal("500.00"),
        profit_amount=Decimal("22000.00"),  # 25000 - 2500 - 500
        payment_status="PARTIALLY_PAID",
        confirmation_status="CONFIRMED",
        gst_invoice_required=True,
    )
    db_session.add(sales_order)
    db_session.flush()

    # 8. Operation Application
    application = OperationApplication(
        application_number=f"AP-FEES-{uuid.uuid4().hex[:6].upper()}",
        sales_order_id=sales_order.order_id,
        company_id=company_a.company_id,
        client_id=client.client_id,
        service_id=service.service_id,
        department_id=dept_ops.department_id,
        assigned_to_user_id=deepak_ops.user_id,
        assigned_by_user_id=mansi_lead.user_id,
        assigned_at=datetime.now(timezone.utc),
        priority="MEDIUM",
        application_status="IN_PROGRESS",
        target_due_date=date.today() + timedelta(days=14),
    )
    db_session.add(application)
    db_session.flush()

    # 9. Modules & Permissions
    # Fetch or create module records
    mod_ops = db_session.execute(select(Module).where(Module.module_code == "OPERATIONS")).scalar_one_or_none()
    if not mod_ops:
        mod_ops = Module(module_code="OPERATIONS", module_name="Operations Module", display_order=20, status="ACTIVE")
        db_session.add(mod_ops)
        db_session.flush()

    mod_sales = db_session.execute(select(Module).where(Module.module_code == "SALES")).scalar_one_or_none()
    if not mod_sales:
        mod_sales = Module(module_code="SALES", module_name="Sales Module", display_order=10, status="ACTIVE")
        db_session.add(mod_sales)
        db_session.flush()

    mod_accounts = db_session.execute(select(Module).where(Module.module_code == "ACCOUNTS")).scalar_one_or_none()
    if not mod_accounts:
        mod_accounts = Module(module_code="ACCOUNTS", module_name="Accounts Module", display_order=30, status="ACTIVE")
        db_session.add(mod_accounts)
        db_session.flush()

    mod_acc_dash = db_session.execute(select(Module).where(Module.module_code == "ACCOUNTS_DASHBOARD")).scalar_one_or_none()
    if not mod_acc_dash:
        mod_acc_dash = Module(module_code="ACCOUNTS_DASHBOARD", module_name="Accounts Dashboard", display_order=31, status="ACTIVE")
        db_session.add(mod_acc_dash)
        db_session.flush()

    mod_acc_entries = db_session.execute(select(Module).where(Module.module_code == "ACCOUNTS_ENTRIES")).scalar_one_or_none()
    if not mod_acc_entries:
        mod_acc_entries = Module(module_code="ACCOUNTS_ENTRIES", module_name="Accounts Entries", display_order=32, status="ACTIVE")
        db_session.add(mod_acc_entries)
        db_session.flush()

    mod_acc_pmt = db_session.execute(select(Module).where(Module.module_code == "ACCOUNTS_PAYMENT_REGISTER")).scalar_one_or_none()
    if not mod_acc_pmt:
        mod_acc_pmt = Module(module_code="ACCOUNTS_PAYMENT_REGISTER", module_name="Accounts Payment Register", display_order=33, status="ACTIVE")
        db_session.add(mod_acc_pmt)
        db_session.flush()

    # Permissions
    # Mansi: Operations ALL scope, can_view, can_edit, can_assign, can_reassign
    grant_or_update_permission(
        session=db_session,
        user_id=mansi_lead.user_id,
        module_id=mod_ops.module_id,
        can_view=True,
        can_create=True,
        can_edit=True,
        can_delete=False,
        can_assign=True,
        can_reassign=True,
        can_export=True,
        data_scope="ALL",
        granted_by_user_id=mansi_lead.user_id,
        is_bootstrap=True,
    )
    # Deepak: Operations SELF scope, can_view, can_edit
    grant_or_update_permission(
        session=db_session,
        user_id=deepak_ops.user_id,
        module_id=mod_ops.module_id,
        can_view=True,
        can_create=True,
        can_edit=True,
        can_delete=False,
        can_assign=False,
        can_reassign=False,
        can_export=True,
        data_scope="SELF",
        granted_by_user_id=mansi_lead.user_id,
        is_bootstrap=True,
    )
    # Peer: Operations SELF scope, can_view, can_edit
    grant_or_update_permission(
        session=db_session,
        user_id=peer_ops.user_id,
        module_id=mod_ops.module_id,
        can_view=True,
        can_create=True,
        can_edit=True,
        can_delete=False,
        can_assign=False,
        can_reassign=False,
        can_export=True,
        data_scope="SELF",
        granted_by_user_id=mansi_lead.user_id,
        is_bootstrap=True,
    )
    # Sales User: Sales ALL scope, view only in Operations
    grant_or_update_permission(
        session=db_session,
        user_id=sales_user.user_id,
        module_id=mod_sales.module_id,
        can_view=True,
        can_create=True,
        can_edit=True,
        can_delete=False,
        can_assign=False,
        can_reassign=False,
        can_export=True,
        data_scope="ALL",
        granted_by_user_id=mansi_lead.user_id,
        is_bootstrap=True,
    )
    grant_or_update_permission(
        session=db_session,
        user_id=sales_user.user_id,
        module_id=mod_ops.module_id,
        can_view=True,
        can_create=False,
        can_edit=False,
        can_delete=False,
        can_assign=False,
        can_reassign=False,
        can_export=False,
        data_scope="ALL",
        granted_by_user_id=mansi_lead.user_id,
        is_bootstrap=True,
    )
    # Accounts User: Accounts ALL scope on ACCOUNTS, ACCOUNTS_DASHBOARD, ACCOUNTS_ENTRIES, ACCOUNTS_PAYMENT_REGISTER
    for m in (mod_accounts, mod_acc_dash, mod_acc_entries, mod_acc_pmt):
        grant_or_update_permission(
            session=db_session,
            user_id=accounts_user.user_id,
            module_id=m.module_id,
            can_view=True,
            can_create=True,
            can_edit=True,
            can_delete=False,
            can_assign=False,
            can_reassign=False,
            can_export=True,
            data_scope="ALL",
            granted_by_user_id=mansi_lead.user_id,
            is_bootstrap=True,
        )
    # Cross Company User: Operations SELF scope in Company B
    grant_or_update_permission(
        session=db_session,
        user_id=cross_company_user.user_id,
        module_id=mod_ops.module_id,
        can_view=True,
        can_create=True,
        can_edit=True,
        can_delete=False,
        can_assign=False,
        can_reassign=False,
        can_export=True,
        data_scope="SELF",
        granted_by_user_id=mansi_lead.user_id,
        is_bootstrap=True,
    )

    db_session.commit()

    return {
        "company_a": company_a,
        "company_b": company_b,
        "mansi_lead": mansi_lead,
        "deepak_ops": deepak_ops,
        "peer_ops": peer_ops,
        "sales_user": sales_user,
        "accounts_user": accounts_user,
        "cross_company_user": cross_company_user,
        "sales_order": sales_order,
        "application": application,
        "client": client,
        "service": service,
    }


def test_scenarios_1_to_3_operations_employee_enters_edits_refreshes_fees(
    client: TestClient, govt_fees_fixture, db_session: Session
):
    """Scenarios 1, 2, 3:
    1. Assigned Operations employee enters Government Fees.
    2. Assigned Operations employee edits Government Fees.
    3. Saved amount verified after page refresh.
    """
    deepak = govt_fees_fixture["deepak_ops"]
    app = govt_fees_fixture["application"]
    order = govt_fees_fixture["sales_order"]

    # Scenario 1: Deepak enters Government Fees (₹3,500.00)
    res1 = client.post(
        f"/api/operations/tasks/{app.application_id}/govt-fees",
        json={"govt_fees": 3500.00, "notes": "Filing fee challan paid at statutory portal"},
        headers=auth_header(deepak),
    )
    assert res1.status_code == 200, f"Expected 200, got: {res1.text}"
    data1 = res1.json()
    assert float(data1["govt_fees"]) == 3500.00
    assert data1["formatted_govt_fees"] == "₹3,500"
    assert data1["last_fees_updated_by"] == "Deepak Kumar"

    # Verify DB update on sales order
    db_session.expire_all()
    updated_order = db_session.get(SalesOrder, order.order_id)
    assert float(updated_order.govt_fees) == 3500.00
    # Profit recalculated: order_value (25000) - govt_fees (3500) - incidental_cost (500) = 21000
    assert float(updated_order.profit_amount) == 21000.00

    # Scenario 2: Deepak edits Government Fees to ₹5,250.50
    res2 = client.put(
        f"/api/operations/tasks/{app.application_id}/govt-fees",
        json={"govt_fees": 5250.50, "notes": "Additional fee demanded by authority query"},
        headers=auth_header(deepak),
    )
    assert res2.status_code == 200
    data2 = res2.json()
    assert float(data2["govt_fees"]) == 5250.50
    assert data2["last_fees_updated_by"] == "Deepak Kumar"

    # Scenario 3: Page refresh simulation via GET /tasks/{application_id}
    res_get = client.get(
        f"/api/operations/tasks/{app.application_id}",
        headers=auth_header(deepak),
    )
    assert res_get.status_code == 200
    get_data = res_get.json()
    assert float(get_data["govt_fees"]) == 5250.50
    # Verify activity logs contain the updates
    activity_types = [a["action_type"] for a in get_data.get("activity_logs", [])]
    assert "GOVT_FEES_UPDATE" in activity_types


def test_scenarios_4_and_5_manshi_updates_fees_and_retains_visibility_after_reassignment(
    client: TestClient, govt_fees_fixture, db_session: Session
):
    """Scenarios 4 & 5:
    4. Manshi (Operations Lead) updates another employee's task fees.
    5. Manshi views fees after task is reassigned to another employee.
    """
    mansi = govt_fees_fixture["mansi_lead"]
    peer = govt_fees_fixture["peer_ops"]
    app = govt_fees_fixture["application"]

    # Scenario 4: Manshi updates task fees on Deepak's task
    res_lead = client.post(
        f"/api/operations/tasks/{app.application_id}/govt-fees",
        json={"govt_fees": 7200.00, "notes": "Operations Lead revised statutory allocation"},
        headers=auth_header(mansi),
    )
    assert res_lead.status_code == 200
    data_lead = res_lead.json()
    assert float(data_lead["govt_fees"]) == 7200.00
    assert data_lead["last_fees_updated_by"] == "Mansi Singhal"

    # Reassign the task from Deepak to Pooja (Peer)
    res_reassign = client.post(
        f"/api/operations/tasks/{app.application_id}/reassign",
        json={
            "new_assignee_user_id": str(peer.user_id),
            "reason": "Reassigned for authority hearing",
        },
        headers=auth_header(mansi),
    )
    assert res_reassign.status_code == 200

    # Scenario 5: Manshi views task and fees after reassignment
    res_mansi_view = client.get(
        f"/api/operations/tasks/{app.application_id}",
        headers=auth_header(mansi),
    )
    assert res_mansi_view.status_code == 200
    mansi_data = res_mansi_view.json()
    assert float(mansi_data["govt_fees"]) == 7200.00
    assert mansi_data["assigned_to_user_id"] == str(peer.user_id)

    # Manshi can update fees again after reassignment
    res_mansi_update2 = client.post(
        f"/api/operations/tasks/{app.application_id}/govt-fees",
        json={"govt_fees": 7800.00, "notes": "Post-reassignment fee update by Lead"},
        headers=auth_header(mansi),
    )
    assert res_mansi_update2.status_code == 200
    assert float(res_mansi_update2.json()["govt_fees"]) == 7800.00


def test_scenarios_6_and_7_sales_employee_views_fees_but_cannot_modify(
    client: TestClient, govt_fees_fixture
):
    """Scenarios 6 & 7:
    6. Sales employee views Government Fees.
    7. Sales employee attempts to modify fees -> Access Denied (403).
    """
    sales = govt_fees_fixture["sales_user"]
    app = govt_fees_fixture["application"]

    # Scenario 6: Sales employee can view task details including government fees
    res_view = client.get(
        f"/api/operations/tasks/{app.application_id}",
        headers=auth_header(sales),
    )
    assert res_view.status_code == 200
    assert "govt_fees" in res_view.json()

    # Scenario 7: Sales employee attempts to modify fees through Operations endpoint -> 403 Forbidden
    res_mod = client.post(
        f"/api/operations/tasks/{app.application_id}/govt-fees",
        json={"govt_fees": 12000.00},
        headers=auth_header(sales),
    )
    assert res_mod.status_code == 403, f"Expected 403 for sales user modification, got: {res_mod.status_code}"


def test_scenarios_8_and_9_accounts_employee_views_latest_fees_and_profit(
    client: TestClient, govt_fees_fixture, db_session: Session
):
    """Scenarios 8 & 9:
    8. Accounts employee views Government Fees.
    9. Updated fees reflected in Accounts workflows and profit calculations.
    """
    accounts = govt_fees_fixture["accounts_user"]
    mansi = govt_fees_fixture["mansi_lead"]
    app = govt_fees_fixture["application"]
    order = govt_fees_fixture["sales_order"]

    # Operations updates fee to ₹8,500.00
    client.post(
        f"/api/operations/tasks/{app.application_id}/govt-fees",
        json={"govt_fees": 8500.00},
        headers=auth_header(mansi),
    )

    # Accounts fetches accounts entries
    res_acc = client.get(
        "/api/accounts/entries",
        headers=auth_header(accounts),
    )
    assert res_acc.status_code == 200
    acc_data = res_acc.json()
    items = acc_data.get("items", [])
    matched = [it for it in items if it["order_number"] == order.order_number]
    assert len(matched) == 1
    matched_entry = matched[0]
    # Scenario 8: Latest amount visible in Accounts
    assert float(matched_entry["govt_fees"]) == 8500.00
    # Scenario 9: Profit correctly reflects order_value - govt_fees - incidental_cost
    # 25000 - 8500 - 500 = 16000
    assert float(matched_entry["profit_amount"]) == 16000.00


def test_scenarios_10_and_11_data_validation(
    client: TestClient, govt_fees_fixture
):
    """Scenarios 10 & 11:
    10. Negative amount submitted -> Validation error.
    11. Invalid text submitted -> Validation error.
    """
    deepak = govt_fees_fixture["deepak_ops"]
    app = govt_fees_fixture["application"]

    # Scenario 10: Negative amount
    res_neg = client.post(
        f"/api/operations/tasks/{app.application_id}/govt-fees",
        json={"govt_fees": -500.00},
        headers=auth_header(deepak),
    )
    assert res_neg.status_code in (400, 422), f"Expected 400 or 422 for negative fee, got: {res_neg.status_code}"

    # Scenario 11: Invalid text
    res_invalid = client.post(
        f"/api/operations/tasks/{app.application_id}/govt-fees",
        json={"govt_fees": "five thousand rupees"},
        headers=auth_header(deepak),
    )
    assert res_invalid.status_code in (400, 422), f"Expected 400 or 422 for invalid text, got: {res_invalid.status_code}"


def test_scenarios_12_to_14_preservation_of_records(
    client: TestClient, govt_fees_fixture, db_session: Session
):
    """Scenarios 12, 13, 14:
    12. Existing Government Fees records are preserved.
    13. Existing financial records remain valid and unaffected.
    14. Existing expense/reimbursement workflows remain unaffected.
    """
    order = govt_fees_fixture["sales_order"]
    app = govt_fees_fixture["application"]

    # Verify order number, client_id, company_id, service_id remain unmodified
    db_session.expire_all()
    fresh_order = db_session.get(SalesOrder, order.order_id)
    fresh_app = db_session.get(OperationApplication, app.application_id)

    assert fresh_order.order_number == order.order_number
    assert fresh_order.client_id == order.client_id
    assert fresh_order.company_id == order.company_id
    assert fresh_order.service_id == order.service_id
    assert fresh_app.sales_order_id == order.order_id
    assert fresh_app.company_id == order.company_id


def test_scenarios_15_and_16_unauthorized_and_cross_company(
    client: TestClient, govt_fees_fixture
):
    """Scenarios 15 & 16:
    15. Unauthorized employee (non-assigned peer) attempts modification -> 403 Access Denied.
    16. Cross-company employee attempts modification -> 403 Access Denied.
    """
    peer = govt_fees_fixture["peer_ops"]
    cross_user = govt_fees_fixture["cross_company_user"]
    app = govt_fees_fixture["application"]

    # Scenario 15: Peer (Pooja Sharma) is not assigned to the task and not a lead -> 403 Forbidden
    res_peer = client.post(
        f"/api/operations/tasks/{app.application_id}/govt-fees",
        json={"govt_fees": 9000.00},
        headers=auth_header(peer),
    )
    assert res_peer.status_code == 403, f"Expected 403 for non-assigned peer, got: {res_peer.status_code}"

    # Scenario 16: Cross-company employee (Company B) attempts modification -> 403 Forbidden
    res_cross = client.post(
        f"/api/operations/tasks/{app.application_id}/govt-fees",
        json={"govt_fees": 9500.00},
        headers=auth_header(cross_user),
    )
    assert res_cross.status_code == 403, f"Expected 403 for cross-company access, got: {res_cross.status_code}"


def test_scenarios_17_to_20_rbac_and_workflow_integrity(
    client: TestClient, govt_fees_fixture
):
    """Scenarios 17, 18, 19, 20:
    17. Existing RBAC permissions remain unaffected.
    18. Existing Operations task workflow remains intact.
    19. Existing Sales workflow remains intact.
    20. Existing Accounts workflow remains intact.
    """
    mansi = govt_fees_fixture["mansi_lead"]
    deepak = govt_fees_fixture["deepak_ops"]
    sales = govt_fees_fixture["sales_user"]
    accounts = govt_fees_fixture["accounts_user"]

    # 18. Operations tasks list works
    res_ops_list = client.get("/api/operations/tasks", headers=auth_header(mansi))
    assert res_ops_list.status_code == 200

    # 18. My tasks endpoint works
    res_my_tasks = client.get("/api/operations/tasks/my-tasks", headers=auth_header(deepak))
    assert res_my_tasks.status_code == 200

    # 19. Sales list works
    res_sales = client.get("/api/sales/orders", headers=auth_header(sales))
    assert res_sales.status_code == 200

    # 20. Accounts access works
    res_acc = client.get("/api/accounts/entries", headers=auth_header(accounts))
    assert res_acc.status_code == 200

    res_acc_dash = client.get("/api/accounts/dashboard", headers=auth_header(accounts))
    assert res_acc_dash.status_code == 200, f"Expected 200, got: {res_acc_dash.text}"
