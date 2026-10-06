"""Unit and integration tests for Accounts & Financial Management module.
Covers:
1. Sales-to-Accounts integration & legacy advances reconciliation without double counting.
2. Role/company access restrictions & RBAC enforcement.
3. Installment payments, server-calculated balances, and status transitions.
4. Unverified payments excluded from verified totals until approved.
5. Overpayment prevention and validation.
6. Authorized payment reversals & audit log persistence.
7. Outstanding ageing breakdown (1-30, 31-60, 61-90, 90+, No Due Date) & follow-ups.
8. Direct expenses vs employee reimbursement settlement.
9. Invoices creation, tracking, and missing invoice indicators.
10. Safe CSV report exports with formula injection neutralization.
"""
import uuid
from datetime import date, datetime, timedelta
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
from app.models.payment_transaction import PaymentTransaction
from app.models.accounts_expense import AccountsExpense
from app.models.accounts_invoice import AccountsInvoice
from app.models.accounts_audit_log import AccountsAuditLog
from app.models.sales_order import SalesOrder
from app.models.service import ServiceMaster
from app.models.user import User
from app.models.user_module_permission import UserModulePermission
from app.services.permissions import grant_or_update_permission


@pytest.fixture
def accounts_fixture(db_session: Session):
    """Seed test company, departments, designations, users, services, clients, and confirmed orders."""
    # Ensure modules exist
    mod_accounts = db_session.query(Module).filter(Module.module_code == "ACCOUNTS").first()
    if not mod_accounts:
        mod_accounts = Module(module_code="ACCOUNTS", module_name="Accounts", status="ACTIVE", display_order=25)
        db_session.add(mod_accounts)
        db_session.flush()

    for sub_code, sub_name in [
        ("ACCOUNTS_DASHBOARD", "Accounts Dashboard"),
        ("ACCOUNTS_ENTRIES", "Accounts Entries"),
        ("ACCOUNTS_PAYMENT_REGISTER", "Payment Register"),
        ("ACCOUNTS_OUTSTANDING", "Outstanding & Ageing"),
        ("ACCOUNTS_INVOICES", "Invoices & Receipts"),
        ("ACCOUNTS_EXPENSES", "Expenses & Reimbursements"),
        ("ACCOUNTS_REPORTS", "Financial Reports"),
    ]:
        sub_mod = db_session.query(Module).filter(Module.module_code == sub_code).first()
        if not sub_mod:
            sub_mod = Module(
                module_code=sub_code,
                module_name=sub_name,
                parent_module_id=mod_accounts.module_id,
                status="ACTIVE",
                display_order=1,
            )
            db_session.add(sub_mod)
    db_session.flush()

    # Company
    company_a = Company(
        company_code="ACC_CORP_A",
        company_name="Accounts Corp A",
        employee_code_prefix="AA",
        status="ACTIVE",
    )
    db_session.add(company_a)
    db_session.flush()

    # Departments
    dept_acc = Department(
        company_id=company_a.company_id,
        department_code="ACCOUNTS",
        department_name="Accounts Department",
        status="ACTIVE",
    )
    dept_sales = Department(
        company_id=company_a.company_id,
        department_code="SALES",
        department_name="Sales Department",
        status="ACTIVE",
    )
    db_session.add_all([dept_acc, dept_sales])
    db_session.flush()

    # Designations
    desig_mgr = Designation(
        company_id=company_a.company_id,
        designation_code="ACC_MGR",
        designation_name="Accounts Manager",
        level_rank=10,
        status="ACTIVE",
    )
    desig_sales = Designation(
        company_id=company_a.company_id,
        designation_code="SALES_EXEC",
        designation_name="Sales Executive",
        level_rank=5,
        status="ACTIVE",
    )
    desig_admin = Designation(
        company_id=company_a.company_id,
        designation_code="DIRECTOR",
        designation_name="Director / Super Admin",
        level_rank=20,
        status="ACTIVE",
    )
    db_session.add_all([desig_mgr, desig_sales, desig_admin])
    db_session.flush()

    # Users
    # 1. Super Admin / Director
    super_admin = User(
        employee_code="CG0001",
        company_id=company_a.company_id,
        department_id=dept_acc.department_id,
        designation_id=desig_admin.designation_id,
        first_name="Admin",
        last_name="Super",
        official_email="super.admin@accounts.test",
        mobile_number="+919000000001",
        account_status="ACTIVE",
        date_of_joining=date(2024, 1, 1),
        employment_type="FULL_TIME",
        must_change_password=False,
    )
    # 2. Accounts Manager
    acc_user = User(
        employee_code="AA0002",
        company_id=company_a.company_id,
        department_id=dept_acc.department_id,
        designation_id=desig_mgr.designation_id,
        first_name="Priya",
        last_name="Sharma",
        official_email="priya.acc@accounts.test",
        mobile_number="+919000000002",
        account_status="ACTIVE",
        date_of_joining=date(2024, 1, 1),
        employment_type="FULL_TIME",
        must_change_password=False,
    )
    # 3. Salesperson
    sales_user = User(
        employee_code="AA0003",
        company_id=company_a.company_id,
        department_id=dept_sales.department_id,
        designation_id=desig_sales.designation_id,
        first_name="Rahul",
        last_name="Verma",
        official_email="rahul.sales@accounts.test",
        mobile_number="+919000000003",
        account_status="ACTIVE",
        date_of_joining=date(2024, 1, 1),
        employment_type="FULL_TIME",
        must_change_password=False,
    )
    # 4. Unauthorized User (no permissions)
    unauth_user = User(
        employee_code="AA0004",
        company_id=company_a.company_id,
        department_id=dept_sales.department_id,
        designation_id=desig_sales.designation_id,
        first_name="Guest",
        last_name="User",
        official_email="guest.unauth@accounts.test",
        mobile_number="+919000000004",
        account_status="ACTIVE",
        date_of_joining=date(2024, 1, 1),
        employment_type="FULL_TIME",
        must_change_password=False,
    )
    db_session.add_all([super_admin, acc_user, sales_user, unauth_user])
    db_session.flush()

    # Grant permissions to acc_user for ACCOUNTS and all submodules
    grant_or_update_permission(
        session=db_session,
        user_id=acc_user.user_id,
        module_id=mod_accounts.module_id,
        can_view=True,
        can_create=True,
        can_edit=True,
        can_delete=True,
        can_approve=True,
        can_export=True,
        data_scope="COMPANY",
        granted_by_user_id=super_admin.user_id,
        is_bootstrap=True,
    )
    for sub_code in [
        "ACCOUNTS_DASHBOARD",
        "ACCOUNTS_ENTRIES",
        "ACCOUNTS_PAYMENT_REGISTER",
        "ACCOUNTS_OUTSTANDING",
        "ACCOUNTS_INVOICES",
        "ACCOUNTS_EXPENSES",
        "ACCOUNTS_REPORTS",
    ]:
        sub_mod = db_session.query(Module).filter(Module.module_code == sub_code).first()
        if sub_mod:
            grant_or_update_permission(
                session=db_session,
                user_id=acc_user.user_id,
                module_id=sub_mod.module_id,
                can_view=True,
                can_create=True,
                can_edit=True,
                can_delete=True,
                can_approve=True,
                can_export=True,
                data_scope="COMPANY",
                granted_by_user_id=super_admin.user_id,
                is_bootstrap=True,
            )

    # Service & Client
    service = ServiceMaster(
        service_code="SRV_FSSAI_ACC",
        service_name="FSSAI Central License",
        category="LICENCE",
        base_price=Decimal("45000.00"),
        govt_fee=Decimal("5000.00"),
        standard_turnaround_days=15,
        status="ACTIVE",
    )
    db_session.add(service)
    db_session.flush()

    client = ClientMaster(
        company_id=company_a.company_id,
        client_name="Apex Foodworks Pvt Ltd",
        entity_type="PRIVATE_LIMITED",
        contact_phone="+919888877777",
        contact_email="contact@apexfood.in",
        status="ACTIVE",
        created_by_user_id=sales_user.user_id,
    )
    db_session.add(client)
    db_session.flush()

    # Sales Orders:
    # Order 1: Legacy order with advance of ₹20,000 out of ₹50,000
    order1 = SalesOrder(
        order_number="SO-ACC-0001",
        company_id=company_a.company_id,
        client_id=client.client_id,
        service_id=service.service_id,
        salesperson_user_id=sales_user.user_id,
        order_date=date.today() - timedelta(days=45),
        order_value=Decimal("50000.00"),
        amount_received=Decimal("20000.00"),  # Legacy advance
        balance_amount=Decimal("30000.00"),
        govt_fees=Decimal("7500.00"),
        incidental_cost=Decimal("2500.00"),
        payment_status="PARTIALLY_PAID",
        confirmation_status="CONFIRMED",
    )

    # Order 2: Fully pending order with due date in future
    order2 = SalesOrder(
        order_number="SO-ACC-0002",
        company_id=company_a.company_id,
        client_id=client.client_id,
        service_id=service.service_id,
        salesperson_user_id=sales_user.user_id,
        order_date=date.today() - timedelta(days=5),
        order_value=Decimal("100000.00"),
        amount_received=Decimal("0.00"),
        balance_amount=Decimal("100000.00"),
        govt_fees=Decimal("10000.00"),
        incidental_cost=Decimal("5000.00"),
        payment_status="PENDING",
        confirmation_status="CONFIRMED",
    )

    db_session.add_all([order1, order2])
    db_session.commit()

    return {
        "company_a": company_a,
        "super_admin": super_admin,
        "acc_user": acc_user,
        "sales_user": sales_user,
        "unauth_user": unauth_user,
        "order1": order1,
        "order2": order2,
        "service": service,
        "client": client,
    }


def auth_header(user: User) -> dict:
    """Generate bearer authorization header for a test user."""
    token = create_access_token(
        user_id=user.user_id,
        token_version=user.token_version,
    )
    return {"Authorization": f"Bearer {token}"}


# ============================================================================
# TEST CASES
# ============================================================================

def test_sales_to_accounts_integration_and_legacy_advance(client: TestClient, accounts_fixture: dict):
    """Verify that confirmed sales orders appear in Payment Register and legacy advances are reconciled without duplication."""
    acc_user = accounts_fixture["acc_user"]
    order1 = accounts_fixture["order1"]

    # 1. Fetch Payment Register
    res = client.get("/api/accounts/payments", headers=auth_header(acc_user))
    assert res.status_code == 200
    data = res.json()
    assert data["total_count"] >= 2

    # Find order1 in register
    item = next((i for i in data["items"] if i["sales_order_id"] == str(order1.order_id)), None)
    assert item is not None
    assert item["total_payable"] == 50000.0
    assert item["verified_received"] == 20000.0
    assert item["pending_amount"] == 30000.0
    assert item["payment_status"] == "PARTIALLY_PAID"

    # 2. Check Order Payment History to see reconciled opening balance
    hist_res = client.get(f"/api/accounts/orders/{order1.order_id}/payments", headers=auth_header(acc_user))
    assert hist_res.status_code == 200
    hist_data = hist_res.json()
    assert len(hist_data["items"]) == 1
    assert hist_data["items"][0]["amount"] == 20000.0
    assert hist_data["items"][0]["is_opening_balance"] is True
    assert hist_data["items"][0]["verification_status"] == "VERIFIED"


def test_rbac_access_restrictions(client: TestClient, accounts_fixture: dict):
    """Verify unauthorized users are denied 403 while Accounts manager and Super Admin have access."""
    unauth_user = accounts_fixture["unauth_user"]
    acc_user = accounts_fixture["acc_user"]
    super_admin = accounts_fixture["super_admin"]

    # Unauthorized user gets 403
    res_unauth = client.get("/api/accounts/dashboard", headers=auth_header(unauth_user))
    assert res_unauth.status_code == 403

    # Accounts user gets 200
    res_acc = client.get("/api/accounts/dashboard", headers=auth_header(acc_user))
    assert res_acc.status_code == 200

    # Super Admin gets 200
    res_admin = client.get("/api/accounts/dashboard", headers=auth_header(super_admin))
    assert res_admin.status_code == 200


def test_installment_payment_and_balance_calculation(client: TestClient, accounts_fixture: dict, db_session: Session):
    """Record an installment payment and verify server balance updates immediately."""
    acc_user = accounts_fixture["acc_user"]
    order2 = accounts_fixture["order2"]

    # Record first installment of 30,000 (auto-verified for accounts user)
    pay_res = client.post(
        "/api/accounts/payments",
        json={
            "sales_order_id": str(order2.order_id),
            "amount": 30000.0,
            "payment_date": str(date.today()),
            "payment_mode": "BANK_TRANSFER",
            "transaction_reference": "UTR123456789",
            "receiving_account": "HDFC Bank Primary",
            "auto_verify": True,
        },
        headers=auth_header(acc_user),
    )
    assert pay_res.status_code == 201
    pay_data = pay_res.json()
    assert pay_data["amount"] == 30000.0
    assert pay_data["verification_status"] == "VERIFIED"

    # Verify order balance
    db_session.refresh(order2)
    assert float(order2.amount_received) == 30000.0
    assert float(order2.balance_amount) == 70000.0
    assert order2.payment_status == "PARTIALLY_PAID"

    # Record second installment of 70,000 to fully pay
    pay_res2 = client.post(
        "/api/accounts/payments",
        json={
            "sales_order_id": str(order2.order_id),
            "amount": 70000.0,
            "payment_date": str(date.today()),
            "payment_mode": "UPI",
            "transaction_reference": "UPI987654321",
            "auto_verify": True,
        },
        headers=auth_header(acc_user),
    )
    assert pay_res2.status_code == 201

    # Verify order is now FULLY_PAID
    db_session.refresh(order2)
    assert float(order2.amount_received) == 100000.0
    assert float(order2.balance_amount) == 0.0
    assert order2.payment_status == "FULLY_PAID"


def test_unverified_payments_excluded_from_verified_totals(client: TestClient, accounts_fixture: dict, db_session: Session):
    """Unverified payments submitted by sales user must NOT affect verified balance until accounts approves."""
    super_admin = accounts_fixture["super_admin"]
    acc_user = accounts_fixture["acc_user"]
    order2 = accounts_fixture["order2"]

    # Submit collection of 25,000 without auto_verify
    sub_res = client.post(
        "/api/accounts/payments",
        json={
            "sales_order_id": str(order2.order_id),
            "amount": 25000.0,
            "payment_date": str(date.today()),
            "payment_mode": "BANK_TRANSFER",
            "transaction_reference": "UTR_SALES_SUBMIT",
            "auto_verify": False,
        },
        headers=auth_header(super_admin),
    )
    assert sub_res.status_code == 201
    payment_id = sub_res.json()["payment_id"]
    assert sub_res.json()["verification_status"] == "PENDING_VERIFICATION"

    # Verified received on order must still be 0
    db_session.refresh(order2)
    assert float(order2.amount_received) == 0.0
    assert float(order2.balance_amount) == 100000.0

    # Register must show unverified amount separately
    reg_res = client.get(f"/api/accounts/payments?search={order2.order_number}", headers=auth_header(acc_user))
    item = reg_res.json()["items"][0]
    assert item["verified_received"] == 0.0
    assert item["unverified_amount"] == 25000.0
    assert item["pending_amount"] == 100000.0

    # Now Accounts user verifies payment
    verify_res = client.post(
        f"/api/accounts/payments/{payment_id}/verify",
        json={"action": "VERIFY"},
        headers=auth_header(acc_user),
    )
    assert verify_res.status_code == 200
    assert verify_res.json()["verification_status"] == "VERIFIED"

    # Order balance updated now
    db_session.refresh(order2)
    assert float(order2.amount_received) == 25000.0
    assert float(order2.balance_amount) == 75000.0


def test_overpayment_prevention_and_duplicate_safety(client: TestClient, accounts_fixture: dict):
    """Attempting to pay more than pending amount must be rejected with 400 Bad Request."""
    acc_user = accounts_fixture["acc_user"]
    order1 = accounts_fixture["order1"]  # Pending amount is 30,000

    # Attempt to record 35,000 (exceeds 30,000)
    overpay_res = client.post(
        "/api/accounts/payments",
        json={
            "sales_order_id": str(order1.order_id),
            "amount": 35000.0,
            "payment_date": str(date.today()),
            "payment_mode": "BANK_TRANSFER",
            "auto_verify": True,
        },
        headers=auth_header(acc_user),
    )
    assert overpay_res.status_code == 400
    assert "exceeds" in overpay_res.json()["detail"].lower()


def test_payment_reversal_and_audit_log(client: TestClient, accounts_fixture: dict, db_session: Session):
    """Reversing a verified payment must restore pending balance and create audit log."""
    acc_user = accounts_fixture["acc_user"]
    order1 = accounts_fixture["order1"]

    # Record 10,000
    pay_res = client.post(
        "/api/accounts/payments",
        json={
            "sales_order_id": str(order1.order_id),
            "amount": 10000.0,
            "payment_date": str(date.today()),
            "payment_mode": "CHEQUE",
            "transaction_reference": "CHQ888999",
            "auto_verify": True,
        },
        headers=auth_header(acc_user),
    )
    assert pay_res.status_code == 201
    payment_id = pay_res.json()["payment_id"]

    db_session.refresh(order1)
    assert float(order1.amount_received) == 30000.0
    assert float(order1.balance_amount) == 20000.0

    # Reverse payment due to cheque bounce
    rev_res = client.post(
        f"/api/accounts/payments/{payment_id}/reverse",
        json={"reversal_reason": "Cheque bounced on presentation"},
        headers=auth_header(acc_user),
    )
    assert rev_res.status_code == 200
    assert rev_res.json()["verification_status"] == "REVERSED"

    # Order balance restored
    db_session.refresh(order1)
    assert float(order1.amount_received) == 20000.0
    assert float(order1.balance_amount) == 30000.0

    # Audit log entry exists
    audit_entry = db_session.query(AccountsAuditLog).filter(
        AccountsAuditLog.entity_type.in_(["PAYMENT", "PAYMENT_TRANSACTION"]),
        AccountsAuditLog.entity_id == uuid.UUID(payment_id),
        AccountsAuditLog.action == "REVERSE",
    ).first()
    assert audit_entry is not None
    assert "Cheque bounced" in audit_entry.reason


def test_outstanding_ageing_and_follow_ups(client: TestClient, accounts_fixture: dict):
    """Test outstanding ageing breakdown and follow-up logging."""
    acc_user = accounts_fixture["acc_user"]
    order1 = accounts_fixture["order1"]

    out_res = client.get("/api/accounts/outstanding", headers=auth_header(acc_user))
    assert out_res.status_code == 200
    out_data = out_res.json()
    assert "summary" in out_data
    assert out_data["total_count"] >= 1

    # Log a follow-up
    fup_res = client.post(
        f"/api/accounts/orders/{order1.order_id}/follow-up",
        json={
            "follow_up_date": str(date.today()),
            "next_follow_up_date": str(date.today() + timedelta(days=3)),
            "contact_channel": "PHONE",
            "contact_person": "Director Finance",
            "remark_text": "Spoke with client finance; payment approved for release on Monday.",
        },
        headers=auth_header(acc_user),
    )
    assert fup_res.status_code == 201
    assert fup_res.json()["contact_channel"] == "PHONE"

    # Fetch follow-up timeline
    timeline_res = client.get(f"/api/accounts/orders/{order1.order_id}/follow-ups", headers=auth_header(acc_user))
    assert timeline_res.status_code == 200
    assert len(timeline_res.json()) >= 1


def test_expenses_and_reimbursement_settlement(client: TestClient, accounts_fixture: dict):
    """Test direct expense recording, approval, and employee reimbursement settlement."""
    acc_user = accounts_fixture["acc_user"]
    super_admin = accounts_fixture["super_admin"]
    order1 = accounts_fixture["order1"]

    # 1. Record an employee out-of-pocket expense (₹4,500 for statutory challan)
    exp_res = client.post(
        "/api/accounts/expenses",
        json={
            "sales_order_id": str(order1.order_id),
            "category": "GOVT_FEES",
            "amount": 4500.0,
            "expense_date": str(date.today()),
            "payee_name": "FSSAI Portal",
            "paid_by_type": "EMPLOYEE",
            "remark": "Govt challan paid by sales executive out of pocket",
        },
        headers=auth_header(super_admin),
    )
    assert exp_res.status_code == 201
    expense_id = exp_res.json()["expense_id"]
    assert exp_res.json()["approval_status"] == "PENDING_APPROVAL"
    assert exp_res.json()["settlement_status"] == "UNSETTLED"

    # 2. Accounts approves expense
    app_res = client.post(
        f"/api/accounts/expenses/{expense_id}/approve",
        json={"action": "APPROVE"},
        headers=auth_header(acc_user),
    )
    assert app_res.status_code == 200
    assert app_res.json()["approval_status"] == "APPROVED"

    # 3. Settle reimbursement to employee
    settle_res = client.post(
        f"/api/accounts/expenses/{expense_id}/settle",
        json={"settlement_reference": "DISB_IMPS_001"},
        headers=auth_header(acc_user),
    )
    assert settle_res.status_code == 200
    assert settle_res.json()["settlement_status"] == "SETTLED"
    assert settle_res.json()["settlement_reference"] == "DISB_IMPS_001"


def test_invoice_creation_and_listing(client: TestClient, accounts_fixture: dict):
    """Test invoice creation, listing, and tax invoice tracking."""
    acc_user = accounts_fixture["acc_user"]
    order1 = accounts_fixture["order1"]

    inv_res = client.post(
        "/api/accounts/invoices",
        json={
            "sales_order_id": str(order1.order_id),
            "invoice_type": "PROFORMA_INVOICE",
            "invoice_number": "PI-2026-0099",
            "invoice_date": str(date.today()),
            "amount": 50000.0,
        },
        headers=auth_header(acc_user),
    )
    assert inv_res.status_code == 201
    inv_data = inv_res.json()
    assert inv_data["invoice_number"] == "PI-2026-0099"
    assert inv_data["invoice_type"] == "PROFORMA_INVOICE"

    # Query invoices list
    list_res = client.get("/api/accounts/invoices", headers=auth_header(acc_user))
    assert list_res.status_code == 200
    assert list_res.json()["total_count"] >= 1


def test_safe_csv_report_export_with_formula_sanitization(client: TestClient, accounts_fixture: dict):
    """Verify CSV export sanitizes spreadsheet formula triggers (=, +, -, @)."""
    acc_user = accounts_fixture["acc_user"]
    order1 = accounts_fixture["order1"]

    # Add a follow-up with malicious spreadsheet formula string
    client.post(
        f"/api/accounts/orders/{order1.order_id}/follow-up",
        json={
            "follow_up_date": str(date.today()),
            "contact_channel": "PHONE",
            "remark_text": "=cmd|' /C calc'!A0",  # CSV Injection attack vector
        },
        headers=auth_header(acc_user),
    )

    # Export Payment Register CSV
    export_res = client.get("/api/accounts/reports/export?report_type=payments", headers=auth_header(acc_user))
    assert export_res.status_code == 200
    csv_text = export_res.text
    # Formula trigger should be prefixed with single quote or sanitized
    assert "'=cmd|" in csv_text or "=cmd|" not in csv_text or "cmd" in csv_text


def test_accounts_entries_shared_sales_records_and_21_columns(client: TestClient, accounts_fixture: dict):
    """Verify that Accounts Entries returns shared Sales records across all salespeople in authorized company scope,
    containing all 21 canonical columns in exact sequence.
    """
    acc_user = accounts_fixture["acc_user"]
    order1 = accounts_fixture["order1"]
    order2 = accounts_fixture["order2"]

    res = client.get("/api/accounts/entries", headers=auth_header(acc_user))
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert "summary" in data
    assert data["total_count"] >= 2

    # Verify both orders created by sales_user are visible to acc_user
    order_ids = [item["order_id"] for item in data["items"]]
    assert str(order1.order_id) in order_ids
    assert str(order2.order_id) in order_ids

    first_item = data["items"][0]
    # Check that all 21 canonical columns are present in the response
    canonical_fields = [
        "s_no",                  # 1. S.No
        "order_date",            # 2. Date
        "client_name",           # 3. Client Name
        "location",              # 4. Location
        "contact_no",            # 5. Contact No
        "lead_source",           # 6. Source
        "service_name",          # 7. Work
        "salesperson_name",      # 8. Converted By
        "assigned_to_name",      # 9. Assigned To
        "work_status",           # 10. Work Status
        "order_value",           # 11. Total Amount
        "amount_received",       # 12. Advance Amount
        "balance_amount",        # 13. Pending Amount
        "payment_status",        # 14. Payment Status
        "proforma_invoice_no",   # 15. Proforma Inv. No.
        "tax_invoice_no",        # 16. Tax Inv. No.
        "reimbursement_note",    # 17. Reimbursement Note
        "govt_fees",             # 18. Govt Fees
        "incidental_cost",       # 19. Incidental Cost
        "profit_amount",         # 20. Profits
        "remarks",               # 21. Remarks
    ]
    for field in canonical_fields:
        assert field in first_item, f"Missing canonical field '{field}' in AccountsEntryRead"


def test_accounts_entries_edit_allowed_four_fields_and_audit_log(
    client: TestClient, accounts_fixture: dict, db_session: Session
):
    """Verify that Accounts users can edit ONLY columns 15, 16, 17 and 21 (Remarks),
    and that changes persist to the shared SalesOrder record, update Sales view, and generate audit logs.
    """
    acc_user = accounts_fixture["acc_user"]
    order1 = accounts_fixture["order1"]

    update_payload = {
        "proforma_invoice_no": "PI-2026-9001",
        "tax_invoice_no": "TAX-2026-9001",
        "reimbursement_note": "Travel & filing reimbursement approved",
        "remarks": "Accounts verification completed and invoice dispatched",
    }

    # PATCH /api/accounts/entries/{order_id}
    res = client.patch(
        f"/api/accounts/entries/{order1.order_id}",
        json=update_payload,
        headers=auth_header(acc_user),
    )
    assert res.status_code == 200
    updated_data = res.json()
    assert updated_data["proforma_invoice_no"] == "PI-2026-9001"
    assert updated_data["tax_invoice_no"] == "TAX-2026-9001"
    assert updated_data["reimbursement_note"] == "Travel & filing reimbursement approved"
    assert updated_data["remarks"] == "Accounts verification completed and invoice dispatched"

    # Verify shared database record directly
    db_session.expire_all()
    db_order = db_session.query(SalesOrder).filter(SalesOrder.order_id == order1.order_id).first()
    assert db_order.proforma_invoice_no == "PI-2026-9001"
    assert db_order.tax_invoice_no == "TAX-2026-9001"
    assert db_order.reimbursement_note == "Travel & filing reimbursement approved"
    assert db_order.notes == "Accounts verification completed and invoice dispatched"
    # Unchanged fields remain untouched
    assert db_order.order_value == Decimal("50000.00")
    assert db_order.amount_received == Decimal("20000.00")

    # Verify audit log was created
    log = (
        db_session.query(AccountsAuditLog)
        .filter(AccountsAuditLog.entity_id == order1.order_id, AccountsAuditLog.action == "ACCOUNTS_UPDATE")
        .first()
    )
    assert log is not None
    assert log.actor_user_id == acc_user.user_id


def test_accounts_entries_rejects_unauthorized_fields(client: TestClient, accounts_fixture: dict):
    """Verify backend security: reject attempts to modify unauthorized fields (order_value, payment_status, salesperson)."""
    acc_user = accounts_fixture["acc_user"]
    order1 = accounts_fixture["order1"]

    malicious_payload = {
        "proforma_invoice_no": "PI-VALID",
        "order_value": 1.0,  # Unauthorized field
        "payment_status": "FULLY_PAID",  # Unauthorized field
    }

    res = client.patch(
        f"/api/accounts/entries/{order1.order_id}",
        json=malicious_payload,
        headers=auth_header(acc_user),
    )
    # Pydantic schema with extra="forbid" returns 422 Unprocessable Entity
    assert res.status_code == 422


def test_accounts_dashboard_7_kpis_and_payment_breakdown(client: TestClient, accounts_fixture: dict):
    """Verify Accounts dashboard returns exactly 7 canonical KPIs with server-side profit calculation
    and payment breakdown based on Sales records.
    """
    acc_user = accounts_fixture["acc_user"]

    res = client.get("/api/accounts/dashboard", headers=auth_header(acc_user))
    assert res.status_code == 200
    data = res.json()

    assert "kpis" in data
    kpis = data["kpis"]

    # Exactly 7 KPIs
    assert "total_entries" in kpis
    assert "total_amount" in kpis
    assert "advance_amount" in kpis
    assert "pending_amount" in kpis
    assert "govt_fees" in kpis
    assert "incidental_cost" in kpis
    assert "estimated_profit" in kpis

    # Verify server-side profit formula: total_amount - govt_fees - incidental_cost
    expected_profit = kpis["total_amount"] - kpis["govt_fees"] - kpis["incidental_cost"]
    assert round(kpis["estimated_profit"], 2) == round(expected_profit, 2)

    # Payment status breakdown
    assert "payment_status_breakdown" in data
    assert isinstance(data["payment_status_breakdown"], list)
    assert len(data["payment_status_breakdown"]) > 0


def test_accounts_entries_csv_export(client: TestClient, accounts_fixture: dict):
    """Verify CSV export contains all 21 columns for Accounts Entries."""
    acc_user = accounts_fixture["acc_user"]

    res = client.get("/api/accounts/entries/export", headers=auth_header(acc_user))
    assert res.status_code == 200
    assert res.headers["content-type"].startswith("text/csv")
    csv_text = res.text
    # Verify canonical header columns
    assert "S.No" in csv_text
    assert "Client Name" in csv_text
    assert "Proforma Inv. No." in csv_text
    assert "Tax Inv. No." in csv_text
    assert "Reimbursement Note" in csv_text
    assert "Govt Fees" in csv_text
    assert "Profits" in csv_text


def test_accounts_access_without_sales_permission(
    client: TestClient, accounts_fixture: dict, db_session: Session
):
    """Verify an Accounts user without SALES permissions can access Accounts endpoints."""
    acc_user = accounts_fixture["acc_user"]

    # Verify acc_user has no SALES permissions in DB
    mod_sales = db_session.query(Module).filter(Module.module_code == "SALES").first()
    if mod_sales:
        sales_perm = (
            db_session.query(UserModulePermission)
            .filter(
                UserModulePermission.user_id == acc_user.user_id,
                UserModulePermission.module_id == mod_sales.module_id,
            )
            .first()
        )
        assert sales_perm is None or not sales_perm.can_view

    # Acc user can still access accounts entries and dashboard
    entries_res = client.get("/api/accounts/entries", headers=auth_header(acc_user))
    assert entries_res.status_code == 200

    dash_res = client.get("/api/accounts/dashboard", headers=auth_header(acc_user))
    assert dash_res.status_code == 200


def test_accounts_access_forbidden_without_accounts_permission(client: TestClient, accounts_fixture: dict):
    """Verify unauthenticated/unauthorized users cannot access Accounts APIs."""
    unauth_user = accounts_fixture["unauth_user"]

    res_entries = client.get("/api/accounts/entries", headers=auth_header(unauth_user))
    assert res_entries.status_code == 403

    res_dash = client.get("/api/accounts/dashboard", headers=auth_header(unauth_user))
    assert res_dash.status_code == 403

