"""Integration tests for the R&D / Internal Tasks feature (tasks not linked to Sales orders)."""
import uuid
from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.models.company import Company
from app.models.department import Department
from app.models.designation import Designation
from app.models.module import Module
from app.models.user import User
from app.services.permissions import grant_or_update_permission

BASE = "/api/internal-tasks"


def auth(user: User) -> dict:
    token = create_access_token(user_id=user.user_id, token_version=user.token_version)
    return {"Authorization": f"Bearer {token}"}


def _user(session, code, first, last, company, dept, desig) -> User:
    u = User(
        employee_code=code,
        first_name=first,
        last_name=last,
        official_email=f"{code.lower()}@itask.test",
        mobile_number="+919800000000",
        company_id=company.company_id,
        department_id=dept.department_id,
        designation_id=desig.designation_id,
        date_of_joining=date(2024, 1, 1),
        employment_type="FULL_TIME",
        account_status="ACTIVE",
        must_change_password=False,
        token_version=1,
    )
    session.add(u)
    session.flush()
    return u


@pytest.fixture
def itask(db_session: Session):
    comp_a = Company(company_code="ITASK_A", company_name="ITask Corp A", employee_code_prefix="IA", status="ACTIVE")
    comp_b = Company(company_code="ITASK_B", company_name="ITask Corp B", employee_code_prefix="IB", status="ACTIVE")
    db_session.add_all([comp_a, comp_b])
    db_session.flush()

    d_rnd = Department(department_code="ITASK_RND", department_name="Research & Development", status="ACTIVE")
    d_sales = Department(department_code="ITASK_SALES", department_name="Sales", status="ACTIVE")
    db_session.add_all([d_rnd, d_sales])
    db_session.flush()

    g_exec = Designation(designation_code="ITASK_EXEC", designation_name="Executive", level_rank=10, is_managerial=False, status="ACTIVE")
    g_super = Designation(designation_code="SUPER_ADMIN", designation_name="Super Admin", level_rank=99, is_managerial=True, status="ACTIVE")
    db_session.add_all([g_exec, g_super])
    db_session.flush()

    ops = Module(module_code="OPERATIONS", module_name="Operations", route="/operations", status="ACTIVE", display_order=20, is_navigation=True)
    db_session.add(ops)
    db_session.flush()
    page = Module(
        module_code="OPERATION_INTERNAL_TASKS",
        module_name="R&D / Internal Tasks",
        parent_module_id=ops.module_id,
        route="/operations/internal-tasks",
        status="ACTIVE",
        display_order=75,
        is_navigation=True,
    )
    db_session.add(page)
    db_session.flush()

    manager = _user(db_session, "IA001", "Kishan", "Singh", comp_a, d_rnd, g_exec)
    riya = _user(db_session, "IA002", "Riya", "Rnd", comp_a, d_rnd, g_exec)
    salesperson = _user(db_session, "IA003", "Sam", "Sales", comp_a, d_sales, g_exec)
    outsider = _user(db_session, "IA004", "Olivia", "Other", comp_a, d_rnd, g_exec)
    b_manager = _user(db_session, "IB001", "Bob", "Bcorp", comp_b, d_rnd, g_exec)
    b_employee = _user(db_session, "IB002", "Bea", "Bcorp", comp_b, d_rnd, g_exec)
    super_admin = _user(db_session, "IA099", "Root", "Owner", comp_a, d_rnd, g_super)

    for mgr in (manager, b_manager):
        grant_or_update_permission(
            db_session, user_id=mgr.user_id, module_id=page.module_id,
            can_view=True, can_create=True, can_edit=True, can_assign=True,
            data_scope="COMPANY", is_bootstrap=True,
        )
    # Riya can only read the page (not a manager)
    grant_or_update_permission(
        db_session, user_id=riya.user_id, module_id=page.module_id,
        can_view=True, data_scope="SELF", is_bootstrap=True,
    )
    # Commit (releases the savepoint) so API-side rollbacks on 4xx don't discard seed data.
    db_session.commit()
    return {
        "manager": manager, "riya": riya, "sales": salesperson, "outsider": outsider,
        "b_manager": b_manager, "b_employee": b_employee, "super": super_admin,
    }


def _create(client: TestClient, by: User, to: User, **extra) -> dict:
    body = {"title": "Market Research – Fitness Industry", "task_type": "RESEARCH", "assigned_to_user_id": str(to.user_id)}
    body.update(extra)
    res = client.post(BASE, json=body, headers=auth(by))
    assert res.status_code == 201, res.text
    return res.json()


def test_manager_creates_task_for_any_department(client, itask):
    task = _create(client, itask["manager"], itask["sales"], description="Collect top 10 competitors",
                   due_date=str(date.today() + timedelta(days=5)), priority="high")
    assert task["task_number"].startswith("RND-")
    assert task["status"] == "PENDING"
    assert task["priority"] == "HIGH"
    assert task["assigned_to"]["user_id"] == str(itask["sales"].user_id)
    assert task["assigned_to"]["department_name"] == "Sales"

    thread = client.get(f"{BASE}/{task['task_id']}/messages", headers=auth(itask["manager"])).json()
    types = [m["message_type"] for m in thread["messages"]]
    assert types == ["SYSTEM_EVENT", "COMMENT"]
    assert thread["messages"][1]["message_text"] == "Collect top 10 competitors"


def test_task_numbers_are_unique_and_sequential(client, itask):
    t1 = _create(client, itask["manager"], itask["riya"])
    t2 = _create(client, itask["manager"], itask["riya"])
    n1, n2 = int(t1["task_number"].split("-")[1]), int(t2["task_number"].split("-")[1])
    assert n2 == n1 + 1


def test_non_manager_cannot_create_or_list_assignees(client, itask):
    body = {"title": "x", "assigned_to_user_id": str(itask["outsider"].user_id)}
    assert client.post(BASE, json=body, headers=auth(itask["riya"])).status_code == 403
    assert client.post(BASE, json=body, headers=auth(itask["sales"])).status_code == 403
    assert client.get(f"{BASE}/assignees", headers=auth(itask["riya"])).status_code == 403


def test_assignees_list_includes_all_departments_of_own_company_only(client, itask):
    res = client.get(f"{BASE}/assignees", headers=auth(itask["manager"]))
    assert res.status_code == 200
    ids = {u["user_id"] for u in res.json()}
    assert str(itask["sales"].user_id) in ids
    assert str(itask["riya"].user_id) in ids
    assert str(itask["b_employee"].user_id) not in ids


def test_visibility_assignee_sees_outsider_does_not(client, itask):
    task = _create(client, itask["manager"], itask["sales"])
    tid = task["task_id"]

    mine = client.get(BASE, params={"mine": True}, headers=auth(itask["sales"])).json()
    assert [t["task_id"] for t in mine["items"]] == [tid]
    assert mine["capabilities"]["can_create"] is False

    other = client.get(BASE, headers=auth(itask["outsider"])).json()
    assert other["items"] == []
    assert client.get(f"{BASE}/{tid}", headers=auth(itask["outsider"])).status_code == 404
    assert client.get(f"{BASE}/{tid}/messages", headers=auth(itask["outsider"])).status_code == 404
    assert client.post(f"{BASE}/{tid}/messages", json={"message_text": "hi"}, headers=auth(itask["outsider"])).status_code == 404
    assert client.post(f"{BASE}/{tid}/status", json={"status": "COMPLETED"}, headers=auth(itask["outsider"])).status_code == 404


def test_cross_company_isolation(client, itask):
    # Company A manager cannot assign to company B employee
    body = {"title": "x", "assigned_to_user_id": str(itask["b_employee"].user_id)}
    assert client.post(BASE, json=body, headers=auth(itask["manager"])).status_code == 403

    b_task = _create(client, itask["b_manager"], itask["b_employee"])
    a_list = client.get(BASE, headers=auth(itask["manager"])).json()
    assert b_task["task_id"] not in [t["task_id"] for t in a_list["items"]]
    assert client.get(f"{BASE}/{b_task['task_id']}", headers=auth(itask["manager"])).status_code == 404
    assert client.post(
        f"{BASE}/{b_task['task_id']}/reassign",
        json={"assigned_to_user_id": str(itask["riya"].user_id)},
        headers=auth(itask["manager"]),
    ).status_code == 404


def test_super_admin_sees_all_companies(client, itask):
    b_task = _create(client, itask["b_manager"], itask["b_employee"])
    res = client.get(BASE, headers=auth(itask["super"])).json()
    assert b_task["task_id"] in [t["task_id"] for t in res["items"]]
    assert res["capabilities"]["scope"] == "ALL"


def test_status_rules_for_assignee_and_manager(client, itask):
    tid = _create(client, itask["manager"], itask["sales"])["task_id"]
    sales, mgr = auth(itask["sales"]), auth(itask["manager"])

    r = client.post(f"{BASE}/{tid}/status", json={"status": "in_progress"}, headers=sales)
    assert r.status_code == 200 and r.json()["status"] == "IN_PROGRESS"

    # Assignee cannot cancel
    assert client.post(f"{BASE}/{tid}/status", json={"status": "CANCELLED"}, headers=sales).status_code == 403

    r = client.post(f"{BASE}/{tid}/status", json={"status": "COMPLETED", "comment": "Report shared"}, headers=sales)
    assert r.status_code == 200 and r.json()["completed_at"] is not None

    # Assignee cannot reopen; manager can
    assert client.post(f"{BASE}/{tid}/status", json={"status": "IN_PROGRESS"}, headers=sales).status_code == 403
    r = client.post(f"{BASE}/{tid}/status", json={"status": "IN_PROGRESS"}, headers=mgr)
    assert r.status_code == 200 and r.json()["completed_at"] is None

    texts = [m["message_text"] for m in client.get(f"{BASE}/{tid}/messages", headers=mgr).json()["messages"]]
    assert any("In Progress to Completed" in t and "Report shared" in t for t in texts)

    assert client.post(f"{BASE}/{tid}/status", json={"status": "DONE"}, headers=mgr).status_code == 422


def test_chat_between_manager_and_assignee(client, itask):
    tid = _create(client, itask["manager"], itask["sales"])["task_id"]
    r = client.post(f"{BASE}/{tid}/messages", json={"message_text": "Started collecting data"}, headers=auth(itask["sales"]))
    assert r.status_code == 201 and r.json()["is_own"] is True
    r = client.post(f"{BASE}/{tid}/messages", json={"message_text": "Add pricing comparison too"}, headers=auth(itask["manager"]))
    assert r.status_code == 201

    thread = client.get(f"{BASE}/{tid}/messages", headers=auth(itask["sales"])).json()
    comments = [m for m in thread["messages"] if m["message_type"] == "COMMENT"]
    assert [c["message_text"] for c in comments] == ["Started collecting data", "Add pricing comparison too"]
    assert comments[1]["is_own"] is False
    assert thread["task"]["message_count"] == 2

    assert client.post(f"{BASE}/{tid}/messages", json={"message_text": "   "}, headers=auth(itask["sales"])).status_code == 422


def test_reassign_and_edit_permissions(client, itask):
    tid = _create(client, itask["manager"], itask["sales"])["task_id"]

    # Assignee cannot reassign or edit
    assert client.post(f"{BASE}/{tid}/reassign", json={"assigned_to_user_id": str(itask["riya"].user_id)},
                       headers=auth(itask["sales"])).status_code == 403
    assert client.patch(f"{BASE}/{tid}", json={"title": "New"}, headers=auth(itask["sales"])).status_code == 403

    r = client.post(f"{BASE}/{tid}/reassign", json={"assigned_to_user_id": str(itask["riya"].user_id), "reason": "Workload"},
                    headers=auth(itask["manager"]))
    assert r.status_code == 200 and r.json()["assigned_to"]["user_id"] == str(itask["riya"].user_id)

    # Previous assignee no longer sees it; new assignee does
    assert client.get(f"{BASE}/{tid}", headers=auth(itask["sales"])).status_code == 404
    assert client.get(f"{BASE}/{tid}", headers=auth(itask["riya"])).status_code == 200

    r = client.patch(f"{BASE}/{tid}", json={"title": "Competitor Analysis – CA Services", "task_type": "vendor"},
                     headers=auth(itask["manager"]))
    assert r.status_code == 200
    assert r.json()["title"] == "Competitor Analysis – CA Services" and r.json()["task_type"] == "VENDOR"


def test_summary_counts_and_filters(client, itask):
    mgr = auth(itask["manager"])
    t1 = _create(client, itask["manager"], itask["riya"])["task_id"]
    t2 = _create(client, itask["manager"], itask["riya"], task_type="VENDOR")["task_id"]
    _create(client, itask["manager"], itask["sales"])
    client.post(f"{BASE}/{t1}/status", json={"status": "IN_PROGRESS"}, headers=mgr)
    client.post(f"{BASE}/{t2}/status", json={"status": "COMPLETED"}, headers=mgr)

    res = client.get(BASE, headers=mgr).json()
    assert res["summary"] == {"total": 3, "pending": 1, "in_progress": 1, "completed": 1, "cancelled": 0}

    vendor = client.get(BASE, params={"task_type": "VENDOR"}, headers=mgr).json()
    assert [t["task_id"] for t in vendor["items"]] == [t2]

    done = client.get(BASE, params={"status": "COMPLETED"}, headers=mgr).json()
    assert done["total"] == 1 and done["summary"]["total"] == 3


def test_validation_errors(client, itask):
    mgr = auth(itask["manager"])
    to = str(itask["riya"].user_id)
    assert client.post(BASE, json={"title": "  ", "assigned_to_user_id": to}, headers=mgr).status_code == 422
    assert client.post(BASE, json={"title": "x", "task_type": "MONEY", "assigned_to_user_id": to}, headers=mgr).status_code == 422
    assert client.post(BASE, json={"title": "x", "assigned_to_user_id": to, "amount": 100}, headers=mgr).status_code == 422
    assert client.post(BASE, json={"title": "x", "assigned_to_user_id": str(uuid.uuid4())}, headers=mgr).status_code == 400
    assert client.post(BASE, json={"title": "x", "assigned_to_user_id": to}).status_code == 401


def test_page_appears_in_permission_catalog():
    from app.services.permissions import PAGE_CATALOG_CONFIG
    page = PAGE_CATALOG_CONFIG["OPERATION_INTERNAL_TASKS"]
    assert page["module_code"] == "OPERATIONS"
    assert set(page["supported_actions"]) == {"read", "write", "assign", "update"}
