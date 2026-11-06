"""CRUD of tickets and appointments through the real API on the working database."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from app.core.security import create_access_token
from tests.integration.conftest import work_connection

LOCAL = timezone(timedelta(hours=7))


def at(day: date, hhmm: str) -> str:
    hours, minutes = map(int, hhmm.split(":"))
    return datetime(day.year, day.month, day.day, hours, minutes, tzinfo=LOCAL).isoformat()


def bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def other_manager_token() -> str:
    return create_access_token({
        "username": "QL_TT02", "role": "QUAN_LY", "center_id": 2, "center_name": "TT02",
        "technician_id": None, "full_name": "Quản lý trung tâm 2", "employee_id": 2,
    })


@pytest.mark.integration
@pytest.mark.tc("CRUD1")
def test_ticket_create_read_update_cancel(work_client: TestClient, work_database: None, manager_token: str) -> None:
    """CRUD phiếu: tạo phiếu MỚI, xem, sửa, hủy mềm (DA_HUY) và chặn sửa/hủy lần hai"""
    headers = bearer(manager_token)
    due = (datetime.now(LOCAL) + timedelta(days=5)).replace(microsecond=0).isoformat()
    payload = {
        "customer_name": "Nguyễn Văn Kiểm Thử", "customer_phone": "+84 909.123.456",
        "serial_no": "SN-CRUD-0001", "issue_desc": "Màn hình sọc sau khi rơi",
        "category_code": "MAN_HINH", "priority": "TRUNG_BINH", "due_date": due,
    }

    created = work_client.post("/api/tickets", headers=headers, json=payload)
    assert created.status_code == 201, created.text
    ticket = created.json()
    ticket_id = ticket["ticket_id"]
    assert ticket["status"] == "MOI" and ticket["technician_id"] is None
    assert ticket["customer_phone"] == "0909123456"
    assert ticket["ticket_code"] == f"BH-{ticket_id:06d}/{datetime.now(LOCAL).year}"

    read = work_client.get(f"/api/tickets/{ticket_id}", headers=headers)
    assert read.status_code == 200 and read.json()["serial_no"] == "SN-CRUD-0001"
    assert [e["to_status"] for e in read.json()["status_history"]] == ["MOI"]
    assert work_client.get(f"/api/tickets/{ticket_id}", headers=bearer(other_manager_token())).status_code == 403

    updated = work_client.put(f"/api/tickets/{ticket_id}", headers=headers,
                              json={**payload, "priority": "CAO", "issue_desc": "Màn hình sọc và liệt cảm ứng"})
    assert updated.status_code == 200, updated.text
    with work_connection() as connection:
        row = connection.execute(
            "SELECT priority, issue_desc, status FROM ticket WHERE ticket_id = %s", (ticket_id,)).fetchone()
    assert row == ("CAO", "Màn hình sọc và liệt cảm ứng", "MOI")

    cancelled = work_client.delete(f"/api/tickets/{ticket_id}", headers=headers,
                                   params={"reason": "Khách rút yêu cầu"})
    assert cancelled.status_code == 200, cancelled.text
    assert cancelled.json()["status"] == "DA_HUY"
    with work_connection() as connection:
        status, closed_at = connection.execute(
            "SELECT status, closed_at FROM ticket WHERE ticket_id = %s", (ticket_id,)).fetchone()
        last_log = connection.execute(
            """SELECT from_status, to_status, note FROM ticket_status_log
               WHERE ticket_id = %s ORDER BY changed_at DESC, log_id DESC LIMIT 1""", (ticket_id,)).fetchone()
    assert status == "DA_HUY" and closed_at is not None
    assert last_log == ("MOI", "DA_HUY", "Khách rút yêu cầu")

    again = work_client.delete(f"/api/tickets/{ticket_id}", headers=headers)
    edit_after = work_client.put(f"/api/tickets/{ticket_id}", headers=headers, json=payload)
    assert (again.status_code, again.json()["error"]) == (409, "TICKET_NOT_CANCELLABLE")
    assert (edit_after.status_code, edit_after.json()["error"]) == (409, "TICKET_NOT_EDITABLE")

    bad_phone = work_client.post("/api/tickets", headers=headers, json={**payload, "customer_phone": "12345"})
    assert (bad_phone.status_code, bad_phone.json()["error"]) == (400, "INVALID_PHONE")


@pytest.mark.integration
@pytest.mark.tc("CRUD2")
def test_appointment_create_read_update_cancel(work_client: TestClient, work_database: None, manager_token: str) -> None:
    """CRUD lịch hẹn: đặt, xem, đổi giờ, chặn trùng khi đổi, hủy mềm giải phóng khung giờ"""
    headers = bearer(manager_token)
    with work_connection() as connection:
        ticket_id, technician_id = connection.execute(
            """SELECT t.ticket_id, t.technician_id FROM ticket t
               JOIN technician k ON k.technician_id = t.technician_id
               WHERE t.center_id = 1 AND t.status = 'DA_PHAN_CONG' AND k.is_active
               ORDER BY t.ticket_id LIMIT 1""").fetchone()
        day = date.today() + timedelta(days=30)
        while day.weekday() == 6 or connection.execute(
            """SELECT count(*) FROM appointment WHERE technician_id = %s AND status = 'DA_HEN'
                 AND start_at < %s AND %s < end_at""",
            (technician_id, at(day, "11:00"), at(day, "08:00")),
        ).fetchone()[0]:
            day += timedelta(days=1)

    def book(start: str, end: str):
        return work_client.post("/api/appointments", headers=headers, json={
            "ticket_id": ticket_id, "appointment_type": "NHAN",
            "start_at": at(day, start), "end_at": at(day, end)})

    first = book("09:00", "09:30")
    assert first.status_code == 201, first.text
    appointment_id = first.json()["appointment_id"]

    read = work_client.get(f"/api/appointments/{appointment_id}", headers=headers)
    assert read.status_code == 200 and read.json()["status"] == "DA_HEN"
    listed = work_client.get("/api/appointments", headers=headers, params={"ticket_id": ticket_id})
    assert appointment_id in [a["appointment_id"] for a in listed.json()["items"]]
    assert work_client.get(f"/api/appointments/{appointment_id}",
                           headers=bearer(other_manager_token())).status_code == 403

    moved = work_client.put(f"/api/appointments/{appointment_id}", headers=headers, json={
        "appointment_type": "GIAO", "start_at": at(day, "10:00"), "end_at": at(day, "10:30"),
        "note": "Khách đổi giờ"})
    assert moved.status_code == 200, moved.text
    assert moved.json()["appointment_type"] == "GIAO"

    second = book("09:00", "09:30")
    assert second.status_code == 201, second.text
    clash = work_client.put(f"/api/appointments/{appointment_id}", headers=headers, json={
        "appointment_type": "GIAO", "start_at": at(day, "09:00"), "end_at": at(day, "09:30")})
    assert (clash.status_code, clash.json()["error"]) == (409, "APPOINTMENT_OVERLAP")
    assert clash.json()["free_slots"]

    cancelled = work_client.delete(f"/api/appointments/{appointment_id}", headers=headers)
    assert cancelled.status_code == 200 and cancelled.json()["status"] == "DA_HUY"
    with work_connection() as connection:
        assert connection.execute(
            "SELECT status FROM appointment WHERE appointment_id = %s", (appointment_id,)).fetchone() == ("DA_HUY",)
    again = work_client.delete(f"/api/appointments/{appointment_id}", headers=headers)
    edit_after = work_client.put(f"/api/appointments/{appointment_id}", headers=headers, json={
        "appointment_type": "GIAO", "start_at": at(day, "10:30"), "end_at": at(day, "11:00")})
    assert (again.status_code, again.json()["error"]) == (409, "APPOINTMENT_NOT_CANCELLABLE")
    assert (edit_after.status_code, edit_after.json()["error"]) == (409, "APPOINTMENT_NOT_EDITABLE")

    reuse = book("10:00", "10:30")
    assert reuse.status_code == 201, reuse.text
