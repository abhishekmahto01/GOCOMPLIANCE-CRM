"""Unit and integration tests for Source Master model, schemas, service, and API."""
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from datetime import date
from app.core.security import create_access_token, hash_password
from app.models.company import Company
from app.models.department import Department
from app.models.designation import Designation
from app.models.module import Module
from app.models.source import SourceMaster
from app.models.user import User
from app.models.user_module_permission import UserModulePermission
from app.schemas.source import SourceCreate, SourceRead, SourceUpdate
from app.services import source_service


@pytest.fixture
def admin_headers(db_session: Session) -> dict:
    """Fixture providing headers for an active admin user with full ADMIN module permissions."""
    company = db_session.query(Company).first()
    if not company:
        company = Company(
            company_id=uuid.uuid4(),
            company_code="GC",
            company_name="GoCompliance Test",
            employee_code_prefix="GC",
            status="ACTIVE",
        )
        db_session.add(company)
        db_session.flush()

    dept = db_session.query(Department).first()
    if not dept:
        dept = Department(
            department_code="ADMIN_DEPT",
            department_name="Admin Dept",
            status="ACTIVE",
        )
        db_session.add(dept)
        db_session.flush()

    desig = db_session.query(Designation).first()
    if not desig:
        desig = Designation(
            designation_code="SUPER_ADMIN",
            designation_name="Super Administrator",
            level_rank=1,
            status="ACTIVE",
        )
        db_session.add(desig)
        db_session.flush()

    admin_user = User(
        employee_code=f"MTC{uuid.uuid4().hex[:4].upper()}",
        company_id=company.company_id,
        department_id=dept.department_id,
        designation_id=desig.designation_id,
        first_name="Admin",
        last_name="Super",
        official_email=f"admin_{uuid.uuid4().hex[:6]}@mastertest.com",
        mobile_number="+919999900001",
        date_of_joining=date(2023, 1, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        must_change_password=False,
    )
    db_session.add(admin_user)
    db_session.flush()

    admin_mod = db_session.query(Module).filter(Module.module_code == "ADMIN").first()
    if not admin_mod:
        admin_mod = Module(module_code="ADMIN", module_name="Administration", route="/admin", status="ACTIVE")
        db_session.add(admin_mod)
        db_session.flush()

    perm = UserModulePermission(
        user_id=admin_user.user_id,
        module_id=admin_mod.module_id,
        can_view=True,
        can_create=True,
        can_edit=True,
        can_delete=True,
        data_scope="ALL",
    )
    db_session.add(perm)
    db_session.commit()

    token = create_access_token(user_id=admin_user.user_id, token_version=admin_user.token_version)
    return {"Authorization": f"Bearer {token}"}


def test_source_model_columns() -> None:
    """Verify source_master columns, types, and primary key."""
    table = SourceMaster.__table__
    columns = table.columns

    expected_columns = {
        "source_id",
        "source_code",
        "source_name",
        "description",
        "status",
        "is_system",
        "created_at",
        "updated_at",
    }
    assert set(columns.keys()) == expected_columns
    pk_cols = [col.name for col in table.primary_key.columns]
    assert pk_cols == ["source_id"]


def test_source_create_schema_normalization() -> None:
    """Verify code uppercase normalization and status validation in schema."""
    s = SourceCreate(
        source_code="google ads",
        source_name="  Google Ads  ",
        description="PPC Campaigns",
        status="active",
    )
    assert s.source_code == "GOOGLE_ADS"
    assert s.source_name == "Google Ads"
    assert s.status == "ACTIVE"


def test_source_create_schema_invalid_status() -> None:
    """Verify schema rejects invalid status."""
    with pytest.raises(ValueError):
        SourceCreate(
            source_code="FB_ADS",
            source_name="Facebook Ads",
            status="PENDING",
        )


def test_source_master_crud_api(client: TestClient, admin_headers: dict, db_session: Session) -> None:
    """Test full CRUD cycle on /api/admin/sources API endpoint."""
    from app.scripts.seed_sources import INITIAL_SOURCES
    for item in INITIAL_SOURCES:
        src = SourceMaster(
            source_id=uuid.uuid4(),
            source_code=item["source_code"],
            source_name=item["source_name"],
            description=item["description"],
            status=item["status"],
            is_system=item["is_system"],
        )
        db_session.add(src)
    db_session.commit()

    # 1. List existing sources (should include initial seeded sources)
    resp = client.get("/api/admin/sources", headers=admin_headers)
    assert resp.status_code == 200
    sources = resp.json()
    codes = [s["source_code"] for s in sources]
    assert "WEBSITE" in codes
    assert "JUSTDIAL" in codes

    # 2. Create new source
    unique_suffix = uuid.uuid4().hex[:6].upper()
    new_code = f"TEST_SRC_{unique_suffix}"
    create_payload = {
        "source_code": new_code,
        "source_name": f"Test Source {unique_suffix}",
        "description": "Integration test source",
        "status": "ACTIVE",
    }
    create_resp = client.post("/api/admin/sources", json=create_payload, headers=admin_headers)
    assert create_resp.status_code == 201
    created_data = create_resp.json()
    assert created_data["source_code"] == new_code
    assert created_data["status"] == "ACTIVE"
    source_id = created_data["source_id"]

    # 3. Check that new source appears in /api/sales/form-options
    form_opts_resp = client.get("/api/sales/form-options", headers=admin_headers)
    assert form_opts_resp.status_code == 200
    assert new_code in form_opts_resp.json()["lead_sources"]

    # 4. Update source
    update_payload = {
        "source_name": f"Updated Source {unique_suffix}",
        "status": "INACTIVE",
    }
    update_resp = client.put(f"/api/admin/sources/{source_id}", json=update_payload, headers=admin_headers)
    assert update_resp.status_code == 200
    assert update_resp.json()["source_name"] == f"Updated Source {unique_suffix}"
    assert update_resp.json()["status"] == "INACTIVE"

    # 5. Check that INACTIVE source no longer appears in /api/sales/form-options
    form_opts_resp2 = client.get("/api/sales/form-options", headers=admin_headers)
    assert form_opts_resp2.status_code == 200
    assert new_code not in form_opts_resp2.json()["lead_sources"]

    # 6. Delete source
    del_resp = client.delete(f"/api/admin/sources/{source_id}", headers=admin_headers)
    assert del_resp.status_code == 200
    assert del_resp.json()["success"] is True

    # 7. Core system sources cannot be deleted
    website_src = [s for s in sources if s["source_code"] == "WEBSITE"][0]
    del_system_resp = client.delete(f"/api/admin/sources/{website_src['source_id']}", headers=admin_headers)
    assert del_system_resp.status_code == 400
    assert "Cannot delete core system source" in del_system_resp.json()["detail"]
