"""Comprehensive test suite for GST Auto-Calculation, Financial Validation, and Tamper Protection.

Covers:
Case 1: GST Yes with ₹10,000 base amount produces ₹1,800 GST and ₹11,800 final amount.
Case 2: GST No with ₹10,000 base amount produces ₹0 GST and ₹10,000 final amount.
Case 3: Switching from GST Yes to GST No removes the GST component without changing the base amount.
Case 4: Switching from GST No to GST Yes adds GST exactly once without compounding.
Case 5: Changing the amount recalculates the GST and final amount correctly.
Case 6: Empty/missing amount is handled according to existing form validation rules.
Case 7: Zero amount is handled correctly.
Case 8: Negative amounts are rejected where prohibited by existing financial validation.
Case 9: Invalid numeric input cannot produce a misleading final amount.
Case 10: Decimal amounts are rounded consistently to two decimal places.
Case 11: Backend calculations agree with frontend calculations.
Case 12: Tampering with a submitted GST amount or final amount cannot bypass backend validation.
Case 13: Creating a sales entry preserves the correct stored financial values.
Case 14: Editing an existing sales entry preserves its values when the financial fields are unchanged.
Case 15: Legacy callers providing only order_value are handled with backward compatibility.
"""
from decimal import Decimal
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.models.sales_order import SalesOrder
from app.models.user import User
from app.schemas.sales_order import SalesOrderCreate, SalesOrderUpdate
from tests.test_gst_invoice_routing import routing_fixture, auth_header


class TestGstAutoCalculation:
    """Test suite validating GST auto-calculation requirements 1-15."""

    def test_case_1_gst_yes_calculation(self, client: TestClient, db_session: Session, routing_fixture: dict):
        """Case 1: GST Yes with ₹10,000 base amount produces ₹1,800 GST and ₹11,800 final amount."""
        sales_user = routing_fixture["sales_user"]
        srv = routing_fixture["service"]
        cl = routing_fixture["client"]

        payload = {
            "order_date": "2026-10-24",
            "client_name": cl.client_name,
            "client_id": str(cl.client_id),
            "contact_no": "9876543210",
            "lead_source": "DIRECT",
            "service_id": str(srv.service_id),
            "salesperson_user_id": str(sales_user.user_id),
            "base_amount": 10000.00,
            "order_value": 11800.00,
            "gst_amount": 1800.00,
            "gst_rate": 18.00,
            "gst_invoice_required": True,
            "amount_received": 0.00,
            "govt_fees": 0.00,
            "incidental_cost": 0.00,
            "auto_confirm": True,
        }

        resp = client.post("/api/sales/orders", json=payload, headers=auth_header(sales_user))
        assert resp.status_code == 201, resp.text
        data = resp.json()

        assert Decimal(str(data["base_amount"])) == Decimal("10000.00")
        assert Decimal(str(data["gst_amount"])) == Decimal("1800.00")
        assert Decimal(str(data["gst_rate"])) == Decimal("18.00")
        assert Decimal(str(data["order_value"])) == Decimal("11800.00")
        assert data["gst_invoice_required"] is True

        # Check DB persistence
        order = db_session.query(SalesOrder).filter(SalesOrder.order_id == uuid.UUID(data["order_id"])).first()
        assert order is not None
        assert order.order_value == Decimal("11800.00")
        assert order.gst_invoice_required is True

    def test_case_2_gst_no_calculation(self, client: TestClient, db_session: Session, routing_fixture: dict):
        """Case 2: GST No with ₹10,000 base amount produces ₹0 GST and ₹10,000 final amount."""
        sales_user = routing_fixture["sales_user"]
        srv = routing_fixture["service"]
        cl = routing_fixture["client"]

        payload = {
            "order_date": "2026-10-24",
            "client_name": cl.client_name,
            "client_id": str(cl.client_id),
            "contact_no": "9876543210",
            "lead_source": "DIRECT",
            "service_id": str(srv.service_id),
            "salesperson_user_id": str(sales_user.user_id),
            "base_amount": 10000.00,
            "order_value": 10000.00,
            "gst_amount": 0.00,
            "gst_rate": 0.00,
            "gst_invoice_required": False,
            "amount_received": 0.00,
            "govt_fees": 0.00,
            "incidental_cost": 0.00,
            "auto_confirm": True,
        }

        resp = client.post("/api/sales/orders", json=payload, headers=auth_header(sales_user))
        assert resp.status_code == 201, resp.text
        data = resp.json()

        assert Decimal(str(data["base_amount"])) == Decimal("10000.00")
        assert Decimal(str(data["gst_amount"])) == Decimal("0.00")
        assert Decimal(str(data["gst_rate"])) == Decimal("0.00")
        assert Decimal(str(data["order_value"])) == Decimal("10000.00")
        assert data["gst_invoice_required"] is False

    def test_case_3_and_4_switching_gst_selection(self, client: TestClient, db_session: Session, routing_fixture: dict):
        """Case 3 & 4: Switching GST Yes -> No removes GST without altering base; switching No -> Yes adds GST exactly once."""
        sales_user = routing_fixture["sales_user"]
        srv = routing_fixture["service"]
        cl = routing_fixture["client"]

        # Create initially with GST No
        create_payload = {
            "order_date": "2026-10-24",
            "client_name": cl.client_name,
            "client_id": str(cl.client_id),
            "contact_no": "9876543210",
            "lead_source": "DIRECT",
            "service_id": str(srv.service_id),
            "salesperson_user_id": str(sales_user.user_id),
            "base_amount": 10000.00,
            "order_value": 10000.00,
            "gst_invoice_required": False,
            "amount_received": 0.00,
            "auto_confirm": True,
        }
        resp = client.post("/api/sales/orders", json=create_payload, headers=auth_header(sales_user))
        assert resp.status_code == 201
        order_id = resp.json()["order_id"]

        # Case 4: Switch GST No -> Yes (base remains 10000, final becomes 11800, GST = 1800)
        update_to_yes = {
            "base_amount": 10000.00,
            "order_value": 11800.00,
            "gst_amount": 1800.00,
            "gst_rate": 18.00,
            "gst_invoice_required": True,
        }
        patch_resp = client.patch(f"/api/sales/orders/{order_id}", json=update_to_yes, headers=auth_header(sales_user))
        assert patch_resp.status_code == 200, patch_resp.text
        updated_data = patch_resp.json()
        assert Decimal(str(updated_data["base_amount"])) == Decimal("10000.00")
        assert Decimal(str(updated_data["gst_amount"])) == Decimal("1800.00")
        assert Decimal(str(updated_data["order_value"])) == Decimal("11800.00")
        assert updated_data["gst_invoice_required"] is True

        # Case 3: Switch GST Yes -> No (base remains 10000, final becomes 10000, GST = 0)
        update_to_no = {
            "base_amount": 10000.00,
            "order_value": 10000.00,
            "gst_amount": 0.00,
            "gst_rate": 0.00,
            "gst_invoice_required": False,
        }
        patch_resp2 = client.patch(f"/api/sales/orders/{order_id}", json=update_to_no, headers=auth_header(sales_user))
        assert patch_resp2.status_code == 200, patch_resp2.text
        reverted_data = patch_resp2.json()
        assert Decimal(str(reverted_data["base_amount"])) == Decimal("10000.00")
        assert Decimal(str(reverted_data["gst_amount"])) == Decimal("0.00")
        assert Decimal(str(reverted_data["order_value"])) == Decimal("10000.00")
        assert reverted_data["gst_invoice_required"] is False

    def test_case_5_changing_amount_recalculates_correctly(self, client: TestClient, routing_fixture: dict):
        """Case 5: Changing base amount recalculates GST and final amount correctly."""
        sales_user = routing_fixture["sales_user"]
        srv = routing_fixture["service"]
        cl = routing_fixture["client"]

        create_payload = {
            "order_date": "2026-10-24",
            "client_name": cl.client_name,
            "client_id": str(cl.client_id),
            "contact_no": "9876543210",
            "lead_source": "DIRECT",
            "service_id": str(srv.service_id),
            "salesperson_user_id": str(sales_user.user_id),
            "base_amount": 10000.00,
            "order_value": 11800.00,
            "gst_invoice_required": True,
            "amount_received": 0.00,
            "auto_confirm": True,
        }
        resp = client.post("/api/sales/orders", json=create_payload, headers=auth_header(sales_user))
        assert resp.status_code == 201
        order_id = resp.json()["order_id"]

        # Change base to 25,000 -> GST = 4,500, Final = 29,500
        patch_resp = client.patch(
            f"/api/sales/orders/{order_id}",
            json={"base_amount": 25000.00, "order_value": 29500.00, "gst_amount": 4500.00, "gst_invoice_required": True},
            headers=auth_header(sales_user),
        )
        assert patch_resp.status_code == 200
        d = patch_resp.json()
        assert Decimal(str(d["base_amount"])) == Decimal("25000.00")
        assert Decimal(str(d["gst_amount"])) == Decimal("4500.00")
        assert Decimal(str(d["order_value"])) == Decimal("29500.00")

        # Change base to 50,000 -> GST = 9,000, Final = 59,000
        patch_resp2 = client.patch(
            f"/api/sales/orders/{order_id}",
            json={"base_amount": 50000.00, "order_value": 59000.00, "gst_amount": 9000.00, "gst_invoice_required": True},
            headers=auth_header(sales_user),
        )
        assert patch_resp2.status_code == 200
        d2 = patch_resp2.json()
        assert Decimal(str(d2["base_amount"])) == Decimal("50000.00")
        assert Decimal(str(d2["gst_amount"])) == Decimal("9000.00")
        assert Decimal(str(d2["order_value"])) == Decimal("59000.00")

    def test_case_6_empty_or_invalid_financial_payload(self, client: TestClient, routing_fixture: dict):
        """Case 6: Missing required fields or empty financial fields are rejected."""
        sales_user = routing_fixture["sales_user"]
        srv = routing_fixture["service"]
        cl = routing_fixture["client"]

        # Empty base_amount with null order_value
        payload = {
            "order_date": "2026-10-24",
            "client_name": cl.client_name,
            "service_id": str(srv.service_id),
            "salesperson_user_id": str(sales_user.user_id),
            "base_amount": None,
            "order_value": None,
        }
        resp = client.post("/api/sales/orders", json=payload, headers=auth_header(sales_user))
        assert resp.status_code == 422

    def test_case_7_zero_amount_handling(self, client: TestClient, routing_fixture: dict):
        """Case 7: Zero amount is handled cleanly (Base: 0, GST: 0, Final: 0)."""
        sales_user = routing_fixture["sales_user"]
        srv = routing_fixture["service"]
        cl = routing_fixture["client"]

        payload = {
            "order_date": "2026-10-24",
            "client_name": cl.client_name,
            "client_id": str(cl.client_id),
            "contact_no": "9876543210",
            "lead_source": "DIRECT",
            "service_id": str(srv.service_id),
            "salesperson_user_id": str(sales_user.user_id),
            "base_amount": 0.00,
            "order_value": 0.00,
            "gst_amount": 0.00,
            "gst_rate": 18.00,
            "gst_invoice_required": True,
            "amount_received": 0.00,
            "auto_confirm": True,
        }
        resp = client.post("/api/sales/orders", json=payload, headers=auth_header(sales_user))
        assert resp.status_code == 201
        data = resp.json()
        assert Decimal(str(data["base_amount"])) == Decimal("0.00")
        assert Decimal(str(data["gst_amount"])) == Decimal("0.00")
        assert Decimal(str(data["order_value"])) == Decimal("0.00")

    def test_case_8_negative_amounts_rejected(self, client: TestClient, routing_fixture: dict):
        """Case 8: Negative amounts are rejected by financial validation."""
        sales_user = routing_fixture["sales_user"]
        srv = routing_fixture["service"]
        cl = routing_fixture["client"]

        payload = {
            "order_date": "2026-10-24",
            "client_name": cl.client_name,
            "service_id": str(srv.service_id),
            "salesperson_user_id": str(sales_user.user_id),
            "base_amount": -500.00,
            "order_value": -590.00,
            "gst_invoice_required": True,
        }
        resp = client.post("/api/sales/orders", json=payload, headers=auth_header(sales_user))
        assert resp.status_code == 422

    def test_case_9_invalid_numeric_input_rejected(self, client: TestClient, routing_fixture: dict):
        """Case 9: Invalid numeric inputs cannot produce misleading financial records."""
        sales_user = routing_fixture["sales_user"]
        srv = routing_fixture["service"]
        cl = routing_fixture["client"]

        payload = {
            "order_date": "2026-10-24",
            "client_name": cl.client_name,
            "service_id": str(srv.service_id),
            "salesperson_user_id": str(sales_user.user_id),
            "base_amount": "invalid_currency_text",
            "gst_invoice_required": True,
        }
        resp = client.post("/api/sales/orders", json=payload, headers=auth_header(sales_user))
        assert resp.status_code == 422

    def test_case_10_decimal_precision_and_rounding(self, client: TestClient, routing_fixture: dict):
        """Case 10: Decimal amounts rounded consistently to two decimal places."""
        sales_user = routing_fixture["sales_user"]
        srv = routing_fixture["service"]
        cl = routing_fixture["client"]

        # Test 1: 10000.55 -> GST = 1800.099 -> 1800.10, Final = 11800.65
        payload1 = {
            "order_date": "2026-10-24",
            "client_name": cl.client_name,
            "service_id": str(srv.service_id),
            "salesperson_user_id": str(sales_user.user_id),
            "base_amount": 10000.55,
            "order_value": 11800.65,
            "gst_amount": 1800.10,
            "gst_invoice_required": True,
            "auto_confirm": True,
        }
        resp1 = client.post("/api/sales/orders", json=payload1, headers=auth_header(sales_user))
        assert resp1.status_code == 201, resp1.text
        d1 = resp1.json()
        assert Decimal(str(d1["base_amount"])) == Decimal("10000.55")
        assert Decimal(str(d1["gst_amount"])) == Decimal("1800.10")
        assert Decimal(str(d1["order_value"])) == Decimal("11800.65")

        # Test 2: 100.33 -> GST = 18.0594 -> 18.06, Final = 118.39
        payload2 = {
            "order_date": "2026-10-24",
            "client_name": cl.client_name,
            "service_id": str(srv.service_id),
            "salesperson_user_id": str(sales_user.user_id),
            "base_amount": 100.33,
            "order_value": 118.39,
            "gst_amount": 18.06,
            "gst_invoice_required": True,
            "auto_confirm": True,
        }
        resp2 = client.post("/api/sales/orders", json=payload2, headers=auth_header(sales_user))
        assert resp2.status_code == 201, resp2.text
        d2 = resp2.json()
        assert Decimal(str(d2["base_amount"])) == Decimal("100.33")
        assert Decimal(str(d2["gst_amount"])) == Decimal("18.06")
        assert Decimal(str(d2["order_value"])) == Decimal("118.39")

    def test_case_11_backend_independent_calculation_agreement(self):
        """Case 11: Backend schema validator independently computes and matches frontend formula."""
        # When client sends only base_amount and gst_invoice_required
        create_schema = SalesOrderCreate(
            order_date="2026-10-24",
            client_name="Test Client",
            service_id=uuid.uuid4(),
            salesperson_user_id=uuid.uuid4(),
            base_amount=Decimal("10000.00"),
            gst_invoice_required=True,
        )
        assert create_schema.order_value == Decimal("11800.00")
        assert create_schema.gst_amount == Decimal("1800.00")
        assert create_schema.gst_rate == Decimal("18.00")

        # When GST is False
        create_schema_no_gst = SalesOrderCreate(
            order_date="2026-10-24",
            client_name="Test Client",
            service_id=uuid.uuid4(),
            salesperson_user_id=uuid.uuid4(),
            base_amount=Decimal("10000.00"),
            gst_invoice_required=False,
        )
        assert create_schema_no_gst.order_value == Decimal("10000.00")
        assert create_schema_no_gst.gst_amount == Decimal("0.00")
        assert create_schema_no_gst.gst_rate == Decimal("0.00")

    def test_case_12_tampering_with_order_value_or_gst_amount_rejected(self, client: TestClient, routing_fixture: dict):
        """Case 12: Tampering with client-submitted order_value or gst_amount cannot bypass backend validation."""
        sales_user = routing_fixture["sales_user"]
        srv = routing_fixture["service"]
        cl = routing_fixture["client"]

        # Tampering attempt 1: Client sends base 10000, GST=YES, but tampers order_value to 10000 (trying to avoid GST)
        tampered_order_value = {
            "order_date": "2026-10-24",
            "client_name": cl.client_name,
            "service_id": str(srv.service_id),
            "salesperson_user_id": str(sales_user.user_id),
            "base_amount": 10000.00,
            "order_value": 10000.00,  # Should be 11800.00!
            "gst_invoice_required": True,
        }
        resp1 = client.post("/api/sales/orders", json=tampered_order_value, headers=auth_header(sales_user))
        assert resp1.status_code in (400, 422), resp1.text
        assert "Financial integrity violation" in resp1.text or "order_value" in resp1.text

        # Tampering attempt 2: Client sends base 10000, GST=YES, order_value 11800, but tampers gst_amount to 500
        tampered_gst_amount = {
            "order_date": "2026-10-24",
            "client_name": cl.client_name,
            "service_id": str(srv.service_id),
            "salesperson_user_id": str(sales_user.user_id),
            "base_amount": 10000.00,
            "order_value": 11800.00,
            "gst_amount": 500.00,  # Should be 1800.00!
            "gst_invoice_required": True,
        }
        resp2 = client.post("/api/sales/orders", json=tampered_gst_amount, headers=auth_header(sales_user))
        assert resp2.status_code in (400, 422), resp2.text
        assert "Financial integrity violation" in resp2.text or "gst_amount" in resp2.text

    def test_case_13_stored_financial_values_preservation(self, client: TestClient, db_session: Session, routing_fixture: dict):
        """Case 13: Direct verification that database row stores exact final financial value."""
        sales_user = routing_fixture["sales_user"]
        srv = routing_fixture["service"]
        cl = routing_fixture["client"]

        payload = {
            "order_date": "2026-10-24",
            "client_name": cl.client_name,
            "service_id": str(srv.service_id),
            "salesperson_user_id": str(sales_user.user_id),
            "base_amount": 20000.00,
            "order_value": 23600.00,
            "gst_amount": 3600.00,
            "gst_rate": 18.00,
            "gst_invoice_required": True,
            "amount_received": 5000.00,
            "govt_fees": 1000.00,
            "incidental_cost": 500.00,
            "auto_confirm": True,
        }
        resp = client.post("/api/sales/orders", json=payload, headers=auth_header(sales_user))
        assert resp.status_code == 201
        order_id = uuid.UUID(resp.json()["order_id"])

        order = db_session.query(SalesOrder).filter(SalesOrder.order_id == order_id).first()
        assert order is not None
        assert order.order_value == Decimal("23600.00")
        assert order.amount_received == Decimal("5000.00")
        assert order.govt_fees == Decimal("1000.00")
        assert order.incidental_cost == Decimal("500.00")
        assert order.gst_invoice_required is True

    def test_case_14_editing_preserves_financial_values_when_untouched(self, client: TestClient, db_session: Session, routing_fixture: dict):
        """Case 14: Editing an existing sales entry preserves its financial values when non-financial fields are changed."""
        sales_user = routing_fixture["sales_user"]
        srv = routing_fixture["service"]
        cl = routing_fixture["client"]

        payload = {
            "order_date": "2026-10-24",
            "client_name": cl.client_name,
            "service_id": str(srv.service_id),
            "salesperson_user_id": str(sales_user.user_id),
            "base_amount": 10000.00,
            "order_value": 11800.00,
            "gst_amount": 1800.00,
            "gst_rate": 18.00,
            "gst_invoice_required": True,
            "auto_confirm": True,
        }
        resp = client.post("/api/sales/orders", json=payload, headers=auth_header(sales_user))
        assert resp.status_code == 201
        order_id = resp.json()["order_id"]

        # Edit only non-financial fields: notes and location
        patch_payload = {
            "notes": "Updated note without changing financial values",
            "location": "New Mumbai Branch",
        }
        patch_resp = client.patch(f"/api/sales/orders/{order_id}", json=patch_payload, headers=auth_header(sales_user))
        assert patch_resp.status_code == 200, patch_resp.text
        data = patch_resp.json()

        assert Decimal(str(data["base_amount"])) == Decimal("10000.00")
        assert Decimal(str(data["gst_amount"])) == Decimal("1800.00")
        assert Decimal(str(data["order_value"])) == Decimal("11800.00")
        assert data["gst_invoice_required"] is True
        assert data["notes"] == "Updated note without changing financial values"
        assert data["location"] == "New Mumbai Branch"

    def test_case_15_backward_compatibility_legacy_caller(self, client: TestClient, routing_fixture: dict):
        """Case 15: Legacy callers providing only order_value derive base_amount and gst_amount seamlessly."""
        sales_user = routing_fixture["sales_user"]
        srv = routing_fixture["service"]
        cl = routing_fixture["client"]

        # Legacy caller sending order_value: 11800 and gst_invoice_required: True without base_amount
        legacy_payload = {
            "order_date": "2026-10-24",
            "client_name": cl.client_name,
            "service_id": str(srv.service_id),
            "salesperson_user_id": str(sales_user.user_id),
            "order_value": 11800.00,
            "gst_invoice_required": True,
            "auto_confirm": True,
        }
        resp = client.post("/api/sales/orders", json=legacy_payload, headers=auth_header(sales_user))
        assert resp.status_code == 201, resp.text
        data = resp.json()

        assert Decimal(str(data["order_value"])) == Decimal("11800.00")
        assert Decimal(str(data["base_amount"])) == Decimal("10000.00")
        assert Decimal(str(data["gst_amount"])) == Decimal("1800.00")
        assert Decimal(str(data["gst_rate"])) == Decimal("18.00")
        assert data["gst_invoice_required"] is True
