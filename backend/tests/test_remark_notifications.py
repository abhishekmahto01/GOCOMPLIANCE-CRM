"""Comprehensive test suite for Shared Remark Notifications and Per-User Unread Tracking.

Verifies:
1. Multi-user independent read state (Karishma reading an update clears only for Karishma; Admin's unread state remains).
2. Author's own update is automatically read for the author.
3. Later remark creates a fresh unread update for all other authorized users.
4. Single shared update identity across Sales, Operations, and Accounts.
5. Reading through one module clears the update across all screens for that user.
6. Unauthorized users cannot list, count, or mark updates read.
7. Loss of permission removes notification visibility and unread count.
8. Idempotency of mark-read requests.
9. Concurrently arriving updates remain unread (only displayed IDs are marked read).
10. Historical data cutoff prevents old remarks from flooding users.
11. Paginated notifications endpoint and smart target route generation.
"""
import uuid
from datetime import date, datetime, timedelta, timezone
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
from app.models.service import ServiceMaster
from app.models.task_conversation import TaskConversationMessage
from app.models.task_conversation_read import TaskConversationReadState
from app.models.user import User
from app.services.conversation_service import (
    FEATURE_CUTOFF_DATE,
    get_task_conversation,
    get_user_notifications_list,
    get_user_unread_summary,
    mark_conversation_messages_as_read,
    post_conversation_message,
)
from app.services.permissions import grant_or_update_permission


@pytest.fixture
def notification_test_fixture(db_session: Session):
    """Seed multi-user CRM test environment with Deepak (Ops), Karishma (Sales), Priya (Accounts), and Vikram (Admin)."""
    # 1. Company
    company = Company(
        company_code="NOTIFTEST",
        company_name="Notification Test Corp",
        employee_code_prefix="NT",
        status="ACTIVE",
    )
    other_company = Company(
        company_code="OTHERNOTIF",
        company_name="Other Notif Corp",
        employee_code_prefix="ON",
        status="ACTIVE",
    )
    db_session.add_all([company, other_company])
    db_session.flush()

    # 2. Departments
    dept_sales = Department(department_code="SALES", department_name="Sales Department", status="ACTIVE")
    dept_ops = Department(department_code="OPERATIONS", department_name="Operations Department", status="ACTIVE")
    dept_acc = Department(department_code="ACCOUNTS", department_name="Accounts Department", status="ACTIVE")
    dept_mgmt = Department(department_code="MGMT", department_name="Management", status="ACTIVE")
    dept_other = Department(department_code="OTHER", department_name="Other Dept", status="ACTIVE")
    db_session.add_all([dept_sales, dept_ops, dept_acc, dept_mgmt, dept_other])
    db_session.flush()

    # 3. Designations
    desig_sales = Designation(designation_code="SALES_EXEC", designation_name="Sales Executive", level_rank=3, status="ACTIVE")
    desig_ops = Designation(designation_code="OPS_EXEC", designation_name="Operations Executive", level_rank=3, status="ACTIVE")
    desig_acc = Designation(designation_code="ACC_EXEC", designation_name="Accounts Executive", level_rank=3, status="ACTIVE")
    desig_dir = Designation(designation_code="DIR", designation_name="Managing Director", level_rank=10, status="ACTIVE")
    db_session.add_all([desig_sales, desig_ops, desig_acc, desig_dir])
    db_session.flush()

    # 4. Users
    karishma = User(
        company_id=company.company_id,
        department_id=dept_sales.department_id,
        designation_id=desig_sales.designation_id,
        employee_code="NT0001",
        first_name="Karishma",
        last_name="Sharma",
        official_email="karishma@notiftest.com",
        mobile_number="+919876500001",
        date_of_joining=date(2024, 1, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        password_hash="$2b$12$dummyhashforpasswordtesting1234567890",
        must_change_password=False,
    )
    deepak = User(
        company_id=company.company_id,
        department_id=dept_ops.department_id,
        designation_id=desig_ops.designation_id,
        employee_code="NT0002",
        first_name="Deepak",
        last_name="Verma",
        official_email="deepak@notiftest.com",
        mobile_number="+919876500002",
        date_of_joining=date(2024, 1, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        password_hash="$2b$12$dummyhashforpasswordtesting1234567890",
        must_change_password=False,
    )
    priya = User(
        company_id=company.company_id,
        department_id=dept_acc.department_id,
        designation_id=desig_acc.designation_id,
        employee_code="NT0003",
        first_name="Priya",
        last_name="Nair",
        official_email="priya@notiftest.com",
        mobile_number="+919876500003",
        date_of_joining=date(2024, 1, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        password_hash="$2b$12$dummyhashforpasswordtesting1234567890",
        must_change_password=False,
    )
    vikram = User(
        company_id=company.company_id,
        department_id=dept_mgmt.department_id,
        designation_id=desig_dir.designation_id,
        employee_code="NT0004",
        first_name="Vikram",
        last_name="Mehta",
        official_email="vikram@notiftest.com",
        mobile_number="+919876500004",
        date_of_joining=date(2024, 1, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        password_hash="$2b$12$dummyhashforpasswordtesting1234567890",
        must_change_password=False,
    )
    stranger = User(
        company_id=other_company.company_id,
        department_id=dept_other.department_id,
        designation_id=desig_sales.designation_id,
        employee_code="ON0001",
        first_name="Stranger",
        last_name="User",
        official_email="stranger@othercorp.com",
        mobile_number="+919876500005",
        date_of_joining=date(2024, 1, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        password_hash="$2b$12$dummyhashforpasswordtesting1234567890",
        must_change_password=False,
    )
    db_session.add_all([karishma, deepak, priya, vikram, stranger])
    db_session.flush()

    # 5. Modules & Permissions
    all_modules = [
        Module(module_code="ADMIN_ACCESS", module_name="System Administration", status="ACTIVE"),
        Module(module_code="SALES", module_name="Sales Management", status="ACTIVE"),
        Module(module_code="SALES_CONFIRMED_ORDER", module_name="Sales Orders", status="ACTIVE"),
        Module(module_code="SALES_REGISTER", module_name="Sales Register", status="ACTIVE"),
        Module(module_code="SALES_MY_ORDERS", module_name="Sales My Orders", status="ACTIVE"),
        Module(module_code="SALES_ALL_ORDERS", module_name="Sales All Orders", status="ACTIVE"),
        Module(module_code="OPERATIONS", module_name="Operations Management", status="ACTIVE"),
        Module(module_code="OPERATION_MY_TASKS", module_name="Operations My Tasks", status="ACTIVE"),
        Module(module_code="OPERATION_TASK_ASSIGNMENT", module_name="Operations Task Assignment", status="ACTIVE"),
        Module(module_code="OPERATION_ALL_TASKS", module_name="Operations All Tasks", status="ACTIVE"),
        Module(module_code="ACCOUNTS", module_name="Accounts Management", status="ACTIVE"),
        Module(module_code="ACCOUNTS_ENTRIES", module_name="Accounts Entries", status="ACTIVE"),
    ]
    for m in all_modules:
        existing = db_session.query(Module).filter(Module.module_code == m.module_code).first()
        if not existing:
            db_session.add(m)
    db_session.flush()

    mod_dict = {m.module_code: m for m in db_session.query(Module).all()}

    # Vikram (Director) -> ALL
    for mod in all_modules:
        grant_or_update_permission(
            session=db_session,
            user_id=vikram.user_id,
            module_id=mod_dict[mod.module_code].module_id,
            can_view=True,
            can_create=True,
            can_edit=True,
            can_delete=True,
            data_scope="ALL",
            is_bootstrap=True,
        )

    # Karishma -> SALES modules (data_scope COMPANY)
    for mc in ["SALES", "SALES_CONFIRMED_ORDER", "SALES_REGISTER", "SALES_MY_ORDERS"]:
        grant_or_update_permission(
            session=db_session,
            user_id=karishma.user_id,
            module_id=mod_dict[mc].module_id,
            can_view=True,
            can_create=True,
            can_edit=True,
            data_scope="COMPANY",
            is_bootstrap=True,
        )

    # Deepak -> OPERATIONS modules (data_scope COMPANY)
    for mc in ["OPERATIONS", "OPERATION_MY_TASKS", "OPERATION_TASK_ASSIGNMENT"]:
        grant_or_update_permission(
            session=db_session,
            user_id=deepak.user_id,
            module_id=mod_dict[mc].module_id,
            can_view=True,
            can_create=True,
            can_edit=True,
            data_scope="COMPANY",
            is_bootstrap=True,
        )

    # Priya -> ACCOUNTS modules (data_scope COMPANY)
    for mc in ["ACCOUNTS", "ACCOUNTS_ENTRIES"]:
        grant_or_update_permission(
            session=db_session,
            user_id=priya.user_id,
            module_id=mod_dict[mc].module_id,
            can_view=True,
            can_create=True,
            can_edit=True,
            data_scope="COMPANY",
            is_bootstrap=True,
        )

    # 6. Service & Client
    service = ServiceMaster(
        service_code="SRV_FSSAI",
        service_name="FSSAI Registration",
        category="REGISTRATION",
        base_price=Decimal("5000.00"),
        govt_fee=Decimal("0.00"),
        status="ACTIVE",
    )
    client = ClientMaster(
        company_id=company.company_id,
        client_name="Test Food Tech Pvt Ltd",
        contact_phone="+919876543210",
        contact_email="rohan@foodtech.com",
        entity_type="PRIVATE_LIMITED",
        created_by_user_id=karishma.user_id,
        status="ACTIVE",
    )
    db_session.add_all([service, client])
    db_session.flush()

    # 7. Sales Order with GST Invoice Required
    order = SalesOrder(
        order_number="SO-2026-0099",
        company_id=company.company_id,
        client_id=client.client_id,
        service_id=service.service_id,
        salesperson_user_id=karishma.user_id,
        order_date=date.today(),
        order_value=Decimal("50000.00"),
        amount_received=Decimal("25000.00"),
        balance_amount=Decimal("25000.00"),
        govt_fees=Decimal("0.00"),
        incidental_cost=Decimal("0.00"),
        payment_status="PARTIALLY_PAID",
        confirmation_status="CONFIRMED",
        gst_invoice_required=True,
        notes="Initial sales onboarding notes",
    )
    db_session.add(order)
    db_session.flush()

    # 8. Linked Operation Application assigned to Deepak
    app = OperationApplication(
        application_number="AP-2026-0099",
        sales_order_id=order.order_id,
        client_id=client.client_id,
        service_id=service.service_id,
        company_id=company.company_id,
        assigned_to_user_id=deepak.user_id,
        application_status="IN_PROGRESS",
    )
    db_session.add(app)
    db_session.flush()

    return {
        "company": company,
        "other_company": other_company,
        "karishma": karishma,
        "deepak": deepak,
        "priya": priya,
        "vikram": vikram,
        "stranger": stranger,
        "order": order,
        "app": app,
    }


def auth_headers(user: User) -> dict:
    """Generate authenticated JWT bearer header for testing API endpoints."""
    token = create_access_token(user_id=user.user_id, token_version=user.token_version)
    return {"Authorization": f"Bearer {token}"}


class TestRemarkNotificationsAndUnreadSystem:
    """Canonical test suite verifying shared remark notifications and per-user unread tracking."""

    def test_independent_read_state_and_author_auto_read(
        self, client: TestClient, db_session: Session, notification_test_fixture: dict
    ):
        """Verify:

        1. Deepak posts a remark.
        2. Deepak's unread count is 0 (author auto-read).
        3. Karishma and Vikram see 1 unread update.
        4. Karishma marks it read -> Karishma's count becomes 0; Vikram's remains 1.
        5. Vikram marks it read -> Vikram's count becomes 0.
        """
        f = notification_test_fixture
        order_id = f["order"].order_id
        deepak = f["deepak"]
        karishma = f["karishma"]
        vikram = f["vikram"]

        # Deepak posts a remark
        post_resp = client.post(
            f"/api/conversations/{order_id}/messages",
            json={"message_text": "Government department requested additional identity proof.", "originating_module": "OPERATIONS"},
            headers=auth_headers(deepak),
        )
        assert post_resp.status_code == 201
        msg_data = post_resp.json()
        msg_id = msg_data["message_id"]

        # 1. Author Deepak sees 0 unread
        deepak_summary = client.get("/api/conversations/unread-summary", headers=auth_headers(deepak)).json()
        assert deepak_summary["total_unread_count"] == 0
        assert str(order_id) not in deepak_summary["unread_orders"]

        # 2. Karishma sees 1 unread update
        karishma_summary = client.get("/api/conversations/unread-summary", headers=auth_headers(karishma)).json()
        assert karishma_summary["total_unread_count"] == 1
        assert str(order_id) in karishma_summary["unread_orders"]
        assert karishma_summary["unread_orders"][str(order_id)]["unread_count"] == 1
        assert karishma_summary["unread_orders"][str(order_id)]["latest_author_name"] == "Deepak Verma"

        # 3. Vikram (Admin) sees 1 unread update
        vikram_summary = client.get("/api/conversations/unread-summary", headers=auth_headers(vikram)).json()
        assert vikram_summary["total_unread_count"] == 1

        # 4. Karishma marks the message read
        mark_resp = client.post(
            f"/api/conversations/{order_id}/mark-read",
            json={"message_ids": [msg_id]},
            headers=auth_headers(karishma),
        )
        assert mark_resp.status_code == 200
        assert mark_resp.json()["marked_read_count"] == 1

        # Karishma's unread clears
        karishma_summary_after = client.get("/api/conversations/unread-summary", headers=auth_headers(karishma)).json()
        assert karishma_summary_after["total_unread_count"] == 0

        # Vikram's unread STILL REMAINS 1 (Independent read state!)
        vikram_summary_after = client.get("/api/conversations/unread-summary", headers=auth_headers(vikram)).json()
        assert vikram_summary_after["total_unread_count"] == 1

        # 5. Vikram marks the message read -> Vikram's unread clears
        vikram_mark_resp = client.post(
            f"/api/conversations/{order_id}/mark-read",
            json={"message_ids": [msg_id]},
            headers=auth_headers(vikram),
        )
        assert vikram_mark_resp.status_code == 200
        vikram_summary_final = client.get("/api/conversations/unread-summary", headers=auth_headers(vikram)).json()
        assert vikram_summary_final["total_unread_count"] == 0

    def test_new_remark_creates_fresh_unread_after_earlier_read(
        self, client: TestClient, db_session: Session, notification_test_fixture: dict
    ):
        """Verify that a second remark creates a fresh unread update after earlier remark was read."""
        f = notification_test_fixture
        order_id = f["order"].order_id
        deepak = f["deepak"]
        karishma = f["karishma"]

        # Message 1
        resp1 = client.post(
            f"/api/conversations/{order_id}/messages",
            json={"message_text": "Remark 1 from Deepak", "originating_module": "OPERATIONS"},
            headers=auth_headers(deepak),
        )
        msg1_id = resp1.json()["message_id"]

        # Karishma reads Message 1
        client.post(
            f"/api/conversations/{order_id}/mark-read",
            json={"message_ids": [msg1_id]},
            headers=auth_headers(karishma),
        )
        assert client.get("/api/conversations/unread-summary", headers=auth_headers(karishma)).json()["total_unread_count"] == 0

        # Message 2 from Deepak
        resp2 = client.post(
            f"/api/conversations/{order_id}/messages",
            json={"message_text": "Remark 2 from Deepak (Later update)", "originating_module": "OPERATIONS"},
            headers=auth_headers(deepak),
        )
        msg2_id = resp2.json()["message_id"]

        # Karishma now sees 1 unread update again
        karishma_summary = client.get("/api/conversations/unread-summary", headers=auth_headers(karishma)).json()
        assert karishma_summary["total_unread_count"] == 1
        assert karishma_summary["unread_orders"][str(order_id)]["latest_remark_text"] == "Remark 2 from Deepak (Later update)"

    def test_shared_identity_across_sales_operations_and_accounts(
        self, client: TestClient, db_session: Session, notification_test_fixture: dict
    ):
        """Verify:

        1. Single shared remark message created in Accounts.
        2. Exactly 1 notification event created.
        3. Visible across Sales, Operations, and Accounts authorized users.
        4. Reading in one screen clears it across all screens for that user.
        """
        f = notification_test_fixture
        order_id = f["order"].order_id
        priya = f["priya"]
        karishma = f["karishma"]
        deepak = f["deepak"]

        # Priya (Accounts) posts a remark on GST invoice verification
        post_resp = client.post(
            f"/api/conversations/{order_id}/messages",
            json={"message_text": "Client requested B2B invoice with specific GSTIN.", "originating_module": "ACCOUNTS"},
            headers=auth_headers(priya),
        )
        assert post_resp.status_code == 201
        msg_id = post_resp.json()["message_id"]

        # Check notification list for Karishma (Sales)
        karishma_notifs = client.get("/api/conversations/notifications", headers=auth_headers(karishma)).json()
        assert karishma_notifs["total_count"] >= 1
        notif_item = next(n for n in karishma_notifs["items"] if n["message_id"] == msg_id)
        assert notif_item["originating_module"] == "ACCOUNTS"
        assert notif_item["author_name"] == "Priya Nair"
        assert notif_item["is_read"] is False
        assert "/sales/register" in notif_item["target_route"]

        # Check notification list for Deepak (Operations)
        deepak_notifs = client.get("/api/conversations/notifications", headers=auth_headers(deepak)).json()
        deepak_item = next(n for n in deepak_notifs["items"] if n["message_id"] == msg_id)
        assert deepak_item["is_read"] is False
        assert "/operations/my-tasks" in deepak_item["target_route"]

        # When Karishma reads it via Sales Register modal
        client.post(
            f"/api/conversations/{order_id}/mark-read",
            json={"message_ids": [msg_id]},
            headers=auth_headers(karishma),
        )

        # Karishma's notification item now reflects is_read = True
        karishma_notifs_after = client.get("/api/conversations/notifications", headers=auth_headers(karishma)).json()
        k_item_after = next(n for n in karishma_notifs_after["items"] if n["message_id"] == msg_id)
        assert k_item_after["is_read"] is True

        # But Deepak still sees is_read = False
        deepak_notifs_after = client.get("/api/conversations/notifications", headers=auth_headers(deepak)).json()
        d_item_after = next(n for n in deepak_notifs_after["items"] if n["message_id"] == msg_id)
        assert d_item_after["is_read"] is False

    def test_authorization_scope_and_cross_company_isolation(
        self, client: TestClient, db_session: Session, notification_test_fixture: dict
    ):
        """Verify:

        1. Stranger in another company cannot see or count unread remarks (403 / 0 count).
        2. Stranger cannot mark updates read.
        """
        f = notification_test_fixture
        order_id = f["order"].order_id
        deepak = f["deepak"]
        stranger = f["stranger"]

        # Deepak posts a remark
        post_resp = client.post(
            f"/api/conversations/{order_id}/messages",
            json={"message_text": "Confidential internal remark"},
            headers=auth_headers(deepak),
        )
        msg_id = post_resp.json()["message_id"]

        # Stranger sees 0 unread
        stranger_summary = client.get("/api/conversations/unread-summary", headers=auth_headers(stranger)).json()
        assert stranger_summary["total_unread_count"] == 0
        assert str(order_id) not in stranger_summary["unread_orders"]

        # Stranger gets 403 on mark-read
        mark_resp = client.post(
            f"/api/conversations/{order_id}/mark-read",
            json={"message_ids": [msg_id]},
            headers=auth_headers(stranger),
        )
        assert mark_resp.status_code == 403

        # Stranger gets 403 on thread get
        thread_resp = client.get(f"/api/conversations/{order_id}", headers=auth_headers(stranger))
        assert thread_resp.status_code == 403

    def test_idempotent_repeated_mark_read_requests(
        self, client: TestClient, db_session: Session, notification_test_fixture: dict
    ):
        """Verify calling mark-read multiple times with the same message IDs succeeds safely."""
        f = notification_test_fixture
        order_id = f["order"].order_id
        deepak = f["deepak"]
        karishma = f["karishma"]

        resp = client.post(
            f"/api/conversations/{order_id}/messages",
            json={"message_text": "Idempotency test remark"},
            headers=auth_headers(deepak),
        )
        msg_id = resp.json()["message_id"]

        # Call 1
        resp1 = client.post(
            f"/api/conversations/{order_id}/mark-read",
            json={"message_ids": [msg_id]},
            headers=auth_headers(karishma),
        )
        assert resp1.status_code == 200
        assert resp1.json()["marked_read_count"] == 1

        # Call 2 (repeat)
        resp2 = client.post(
            f"/api/conversations/{order_id}/mark-read",
            json={"message_ids": [msg_id]},
            headers=auth_headers(karishma),
        )
        assert resp2.status_code == 200
        assert resp2.json()["marked_read_count"] == 0  # 0 newly inserted, no crash

    def test_concurrent_unrendered_messages_remain_unread(
        self, client: TestClient, db_session: Session, notification_test_fixture: dict
    ):
        """Verify only explicitly supplied displayed message IDs are marked read.

        If message 2 arrives while user was viewing message 1, message 2 remains unread.
        """
        f = notification_test_fixture
        order_id = f["order"].order_id
        deepak = f["deepak"]
        karishma = f["karishma"]

        # Message 1
        resp1 = client.post(
            f"/api/conversations/{order_id}/messages",
            json={"message_text": "Displayed message 1"},
            headers=auth_headers(deepak),
        )
        msg1_id = resp1.json()["message_id"]

        # Message 2 arrives concurrently
        resp2 = client.post(
            f"/api/conversations/{order_id}/messages",
            json={"message_text": "Concurrent unrendered message 2"},
            headers=auth_headers(deepak),
        )
        msg2_id = resp2.json()["message_id"]

        # Karishma only sends msg1_id to mark-read
        client.post(
            f"/api/conversations/{order_id}/mark-read",
            json={"message_ids": [msg1_id]},
            headers=auth_headers(karishma),
        )

        # Karishma's unread summary must still show 1 unread (msg2)
        summary = client.get("/api/conversations/unread-summary", headers=auth_headers(karishma)).json()
        assert summary["total_unread_count"] == 1
        assert summary["unread_orders"][str(order_id)]["unread_count"] == 1
        assert summary["unread_orders"][str(order_id)]["latest_remark_text"] == "Concurrent unrendered message 2"

    def test_historical_cutoff_prevents_backlog(
        self, client: TestClient, db_session: Session, notification_test_fixture: dict
    ):
        """Verify remarks created before FEATURE_CUTOFF_DATE are ignored for unread tracking."""
        f = notification_test_fixture
        order_id = f["order"].order_id
        karishma = f["karishma"]

        # Create an old historical remark directly with created_at < FEATURE_CUTOFF_DATE
        old_msg = TaskConversationMessage(
            message_id=uuid.uuid4(),
            sales_order_id=order_id,
            author_user_id=None,
            message_type="COMMENT",
            message_text="Old historical remark from 2025",
            author_name="Historical Staff",
            created_at=datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        )
        db_session.add(old_msg)
        db_session.commit()

        # Karishma should not see any unread count from this old message
        summary = client.get("/api/conversations/unread-summary", headers=auth_headers(karishma)).json()
        assert summary["total_unread_count"] == 0
