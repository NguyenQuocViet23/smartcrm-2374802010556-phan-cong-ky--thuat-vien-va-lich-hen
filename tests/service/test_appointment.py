"""TC08–TC10: appointments (UC6) on the real system."""

from __future__ import annotations

from datetime import date, datetime, timedelta

import pytest
from playwright.sync_api import Page, expect

from tests.real_system import (
    API_URL, UI_URL, System, api, at, capture, swagger_authorize, swagger_execute, token_for, ui_login,
)

pytestmark = pytest.mark.system


def assigned_ticket(system: System) -> tuple[int, str, int, str]:
    """A real DA_PHAN_CONG ticket held by an active technician of the same center."""
    return system.one(
        """SELECT t.ticket_id, t.ticket_code, k.technician_id, k.technician_code
           FROM ticket t JOIN technician k ON k.technician_id = t.technician_id
           WHERE t.status = 'DA_PHAN_CONG' AND k.is_active AND k.center_id = t.center_id
           ORDER BY t.ticket_id LIMIT 1"""
    )


def vn_date(day: date) -> str:
    return f"{day.day}/{day.month}/{day.year}"


def open_my_ticket(page: Page, technician_code: str, ticket_code: str) -> None:
    ui_login(page, technician_code)
    expect(page).to_have_url(f"{UI_URL}/my-tickets")
    page.get_by_label("Trạng thái").select_option("DANG_LAM")
    page.get_by_role("button", name=ticket_code).click()
    expect(page.get_by_role("heading", name=ticket_code)).to_be_visible()


def book_in_ui(page: Page, kind: str, day: date, hhmm: str):
    page.get_by_role("button", name="Đặt lịch hẹn").click()
    page.get_by_label("Loại").select_option(kind)
    page.get_by_label("Ngày").fill(day.isoformat())
    page.get_by_label("Giờ bắt đầu").fill(hhmm)
    with page.expect_response(
        lambda r: r.request.method == "POST" and r.url.startswith(f"{API_URL}/api/appointments")
    ) as info:
        page.get_by_role("button", name="Lưu lịch hẹn").click()
    return info.value


def book_via_api(token: str, ticket_id: int, kind: str, day: date, start: str, end: str) -> tuple[int, dict]:
    return api("POST", "/api/appointments", token, {
        "ticket_id": ticket_id, "appointment_type": kind,
        "start_at": at(day, start).isoformat(), "end_at": at(day, end).isoformat(),
    })


def appointment_rows(page: Page):
    return page.locator(".ticket-details table tbody tr")


@pytest.mark.tc("TC08")
def test_tc08_dat_lich_hop_le(page: Page, system: System) -> None:
    """Đặt lịch hẹn giao/nhận thiết bị hợp lệ"""
    ticket_id, ticket_code, k_id, k_code = assigned_ticket(system)
    day = system.free_working_day([k_id], "09:00", 30)
    assert system.one(
        "SELECT count(*) FROM appointment WHERE technician_id = %s AND start_at::date = %s AND status = 'DA_HEN'",
        k_id, day,
    )[0] == 0

    open_my_ticket(page, k_code, ticket_code)
    response = book_in_ui(page, "NHAN", day, "09:00")
    body = response.json()

    assert response.status == 201
    assert body["status"] == "DA_HEN" and body["technician_id"] == k_id and body["appointment_type"] == "NHAN"
    assert datetime.fromisoformat(body["start_at"]) == at(day, "09:00")
    assert datetime.fromisoformat(body["end_at"]) == at(day, "09:30")
    ticket_list = api("GET", f"/api/tickets/{ticket_id}/appointments", token_for(k_code))[1]
    assert body["appointment_id"] in [a["appointment_id"] for a in ticket_list]
    assert system.one("SELECT technician_id FROM appointment WHERE appointment_id = %s", body["appointment_id"])[0] == k_id
    row = appointment_rows(page).filter(has_text=f"09:00:00 {vn_date(day)}")
    expect(row).to_contain_text("NHAN")
    expect(row).to_contain_text("ĐÃ HẸN")
    capture(page, "TC08_dat_lich_hop_le")
    system.facts["data"] = f"KTV {k_code}, phiếu thật {ticket_code} (DA_PHAN_CONG); ngày D = {day:%d/%m/%Y}, K chưa có lịch ngày D"
    system.facts["actual"] = (f"HTTP 201, appointment_id {body['appointment_id']}, status DA_HEN, NHAN, "
                              f"09:00–09:30 ngày {day:%d/%m/%Y}; có trong lịch hẹn của phiếu và của {k_code}")


@pytest.mark.tc("TC09")
def test_tc09_dat_lich_trung(page: Page, system: System) -> None:
    """Từ chối đặt lịch hẹn trùng khung giờ"""
    ticket_id, ticket_code, k_id, k_code = assigned_ticket(system)
    day = system.free_working_day([k_id], "09:00", 60)
    token = token_for(k_code)
    status, existing = book_via_api(token, ticket_id, "NHAN", day, "09:00", "09:30")
    assert status == 201
    count_before = system.one("SELECT count(*) FROM appointment")[0]

    swagger_authorize(page, token)
    status, body, block = swagger_execute(page, "POST", "/api/appointments", body={
        "ticket_id": ticket_id, "appointment_type": "NHAN",
        "start_at": at(day, "09:15").isoformat(), "end_at": at(day, "09:45").isoformat(),
    })

    assert status == 409
    assert body["error"] == "APPOINTMENT_OVERLAP"
    conflict = next(c for c in body["conflicts"] if c["appointment_id"] == existing["appointment_id"])
    assert {"appointment_id", "ticket_code", "start_at", "end_at"} <= set(conflict)
    assert datetime.fromisoformat(conflict["start_at"]) == at(day, "09:00")
    assert system.one("SELECT count(*) FROM appointment")[0] == count_before
    capture(page, "TC09_dat_lich_trung", element=block)
    system.facts["data"] = (f"KTV {k_code}, phiếu thật {ticket_code}; ngày D = {day:%d/%m/%Y}; "
                            f"lịch có sẵn #{existing['appointment_id']} 09:00–09:30")
    system.facts["actual"] = (f"HTTP 409 APPOINTMENT_OVERLAP; conflicts: #{conflict['appointment_id']} "
                              f"{conflict['ticket_code']} 09:00–09:30; bảng appointment giữ {count_before} dòng")


@pytest.mark.tc("TC10")
def test_tc10_bien_lich_lien_ke(page: Page, system: System) -> None:
    """Biên: lịch hẹn liền kề (kết thúc = bắt đầu) không bị coi là trùng"""
    ticket_id, ticket_code, k_id, k_code = assigned_ticket(system)
    day = system.free_working_day([k_id], "09:00", 60)
    status, first = book_via_api(token_for(k_code), ticket_id, "NHAN", day, "09:00", "09:30")
    assert status == 201

    open_my_ticket(page, k_code, ticket_code)
    response = book_in_ui(page, "NHAN", day, "09:30")

    assert response.status == 201
    slots = system.all(
        """SELECT start_at, end_at FROM appointment WHERE technician_id = %s AND status = 'DA_HEN'
             AND start_at >= %s AND start_at < %s ORDER BY start_at""",
        k_id, at(day, "00:00"), at(day, "00:00") + timedelta(days=1),
    )
    assert slots == [(at(day, "09:00"), at(day, "09:30")), (at(day, "09:30"), at(day, "10:00"))]
    expect(appointment_rows(page).filter(has_text=f"09:00:00 {vn_date(day)}")).to_be_visible()
    expect(appointment_rows(page).filter(has_text=f"09:30:00 {vn_date(day)}")).to_be_visible()
    capture(page, "TC10_bien_lich_lien_ke")
    system.facts["data"] = (f"KTV {k_code}, phiếu thật {ticket_code}; ngày D = {day:%d/%m/%Y}; "
                            f"lịch có sẵn #{first['appointment_id']} 09:00–09:30")
    system.facts["actual"] = ("HTTP 201 cho lịch 09:30–10:00; K có đúng 2 lịch DA_HEN ngày D "
                              "(09:00–09:30, 09:30–10:00); ràng buộc EXCLUDE không báo lỗi")
