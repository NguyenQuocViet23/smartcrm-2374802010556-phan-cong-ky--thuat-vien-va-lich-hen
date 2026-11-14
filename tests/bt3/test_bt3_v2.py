"""BT3 supplementary test cases TC-13…TC-25: the v1.1 interface on the real backend and real data.

Same harness as tests/bt3/test_bt3.py: every test gets a fresh ``smartcrm_work_test`` and a real
backend on port 8000; the frontend (``UI_BASE_URL``) must be running and talk to that port.
Preconditions are built with SQL or the API, the step is done in the real interface (or Swagger),
a real screenshot is taken, and the database is read back before asserting.

Run all:   python -m pytest -m bt3
Run one:   python -m pytest -m bt3 -k tc19
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from datetime import date, timedelta
from urllib.parse import unquote, urlparse

import pytest
from playwright.sync_api import Page, expect

from tests.bt3.conftest import ROOT, shot
from tests.bt3.test_bt3 import iso, ticket_body
from tests.conftest import WORK_DATABASE, get_test_database_url
from tests.real_system import (
    API_URL, UI_URL, System, _reachable, api, at, swagger_authorize, swagger_execute, token_for, ui_login,
)

pytestmark = pytest.mark.bt3


def require_ui() -> None:
    if not _reachable(UI_URL):
        pytest.fail(f"Frontend chưa chạy tại {UI_URL} (docker compose up -d frontend, hoặc npm run dev).")


def vn_date(day: date) -> str:
    """How the interface prints a date (toLocaleString vi-VN): 5/1/2027."""
    return f"{day.day}/{day.month}/{day.year}"


def login_ui(page: Page, username: str, home: str) -> None:
    ui_login(page, username)
    expect(page).to_have_url(f"{UI_URL}{home}")


def book(token: str, ticket_id: int, day: date, start: str, end: str, kind: str = "NHAN") -> dict:
    status, body = api("POST", "/api/appointments", token, {
        "ticket_id": ticket_id, "appointment_type": kind,
        "start_at": iso(at(day, start)), "end_at": iso(at(day, end)), "note": "BT3 kịch bản",
    })
    assert status == 201, f"Không đặt được lịch tiền điều kiện: {status} {body}"
    return body


def appointment(s: System, appointment_id: int) -> dict:
    row = s.one("SELECT status, start_at, end_at, technician_id, ticket_id FROM appointment WHERE appointment_id = %s",
                appointment_id)
    return {"status": row[0], "start_at": row[1], "end_at": row[2], "technician_id": row[3], "ticket_id": row[4]}


def hhmm(value) -> str:
    return value.astimezone(at(date.today(), "00:00").tzinfo).strftime("%H:%M")


def bookable_ticket(s: System) -> tuple[int, int, int, str]:
    """A real DA_PHAN_CONG ticket whose technician is active in the same center (can log in and get
    appointments): (ticket_id, technician_id, center_id, ticket_code)."""
    return s.one(
        """SELECT t.ticket_id, t.technician_id, t.center_id, t.ticket_code
           FROM ticket t JOIN technician k ON k.technician_id = t.technician_id
           WHERE t.status = 'DA_PHAN_CONG' AND k.is_active AND k.center_id = t.center_id
           ORDER BY t.ticket_id LIMIT 1"""
    )


def tab_count(page: Page, name: str):
    return page.get_by_role("tab", name=name).locator(".count")


# --- 1. LUỒNG ĐÚNG -----------------------------------------------------------------


@pytest.mark.tc("TC-13")
def test_tc13_tao_phieu_qua_giao_dien(page: Page, bt3: System) -> None:
    """Quản lý tạo phiếu bằng nút "+ Tạo phiếu mới": phiếu MỚI được lưu, số trên tab tăng 1"""
    require_ui()
    manager = bt3.manager_username(1)
    total_before = bt3.one("SELECT count(*) FROM ticket")[0]
    new_before = bt3.one("SELECT count(*) FROM ticket WHERE center_id = 1 AND status = 'MOI'")[0]

    login_ui(page, manager, "/tickets")
    expect(tab_count(page, "Chờ phân công")).to_have_text(str(new_before))
    page.get_by_role("button", name="+ Tạo phiếu mới").click()
    dialog = page.get_by_role("dialog")
    dialog.get_by_label("Khách hàng").fill("Nguyễn Thị Thu (TC-13)")
    dialog.get_by_label("Số điện thoại").fill("0912 345 613")
    dialog.get_by_label("Serial máy").fill("SN-TC13-0001")
    dialog.get_by_label("Mô tả lỗi").fill("Máy tắt nguồn khi đang sạc")
    dialog.get_by_label("Nhóm sự cố").select_option("SAC")
    dialog.get_by_label("Mức ưu tiên").select_option("CAO")
    image_a = shot(page, "TC-13")
    with page.expect_response(lambda r: r.request.method == "POST" and r.url == f"{API_URL}/api/tickets") as info:
        dialog.get_by_role("button", name="Tạo phiếu").click()
    status, created = info.value.status, info.value.json()
    expect(page.get_by_role("status")).to_contain_text(f"Đã tạo phiếu {created.get('ticket_code')}")
    expect(tab_count(page, "Chờ phân công")).to_have_text(str(new_before + 1))
    expect(page.get_by_role("row", name=created["ticket_code"])).to_be_visible()
    image_b = shot(page, "TC-13_b")

    row = bt3.ticket(created["ticket_id"])
    total_after = bt3.one("SELECT count(*) FROM ticket")[0]
    new_after = bt3.one("SELECT count(*) FROM ticket WHERE center_id = 1 AND status = 'MOI'")[0]
    logs = bt3.log_count(created["ticket_id"])
    bt3.facts.update(
        data=f"{manager}; khách \"Nguyễn Thị Thu (TC-13)\", SĐT \"0912 345 613\", serial SN-TC13-0001, SAC, CAO, hạn mặc định +3 ngày 17:00",
        actual=f"HTTP {status}, phiếu {created.get('ticket_code')}: status {row['status']}, center {row['center_id']}, "
               f"SĐT lưu {row['customer_phone']}; ticket {total_before} → {total_after}; MOI trung tâm 1 {new_before} → {new_after} "
               f"(tab hiển thị {new_before + 1}); log của phiếu {logs}",
        images=[image_a, image_b],
    )
    assert status == 201 and row["status"] == "MOI" and row["center_id"] == 1
    assert row["customer_phone"] == "0912345613" and total_after == total_before + 1
    assert new_after == new_before + 1 and logs == 1


@pytest.mark.tc("TC-14")
def test_tc14_sua_phieu_moi_qua_giao_dien(page: Page, bt3: System) -> None:
    """Quản lý sửa phiếu MỚI (mô tả, mức ưu tiên): chỉ hai trường đó đổi, hạn cam kết giữ nguyên"""
    require_ui()
    manager = bt3.manager_username(1)
    ticket_id, code = bt3.one(
        "SELECT ticket_id, ticket_code FROM ticket WHERE center_id = 1 AND status = 'MOI' ORDER BY ticket_id LIMIT 1")
    before = bt3.ticket(ticket_id)
    new_priority = "THAP" if before["priority"] != "THAP" else "CAO"
    new_desc = "Cập nhật TC-14: màn hình chớp khi mở camera"

    login_ui(page, manager, "/tickets")
    page.get_by_role("row", name=code).get_by_role("button", name="Sửa").click()
    dialog = page.get_by_role("dialog")
    expect(dialog.get_by_label("Khách hàng")).to_have_value(before["customer_name"])
    dialog.get_by_label("Mô tả lỗi").fill(new_desc)
    dialog.get_by_label("Mức ưu tiên").select_option(new_priority)
    image_a = shot(page, "TC-14")
    with page.expect_response(lambda r: r.request.method == "PUT" and r.url == f"{API_URL}/api/tickets/{ticket_id}") as info:
        dialog.get_by_role("button", name="Lưu thay đổi").click()
    status = info.value.status
    expect(page.get_by_role("status")).to_contain_text(f"Đã lưu thay đổi phiếu {code}")
    image_b = shot(page, "TC-14_b")

    after = bt3.ticket(ticket_id)
    unchanged = [k for k in ("customer_name", "customer_phone", "serial_no", "category_code", "due_date", "status", "center_id")
                 if after[k] == before[k]]
    bt3.facts.update(
        data=f"{manager}; phiếu {code} (MỚI, hạn {before['due_date']:%d/%m/%Y %H:%M}); mô tả mới \"{new_desc}\", ưu tiên {before['priority']} → {new_priority}",
        actual=f"HTTP {status}; issue_desc = \"{after['issue_desc']}\", priority = {after['priority']}; "
               f"giữ nguyên {len(unchanged)}/7 trường khác ({', '.join(unchanged)})",
        images=[image_a, image_b],
    )
    assert status == 200 and after["issue_desc"] == new_desc and after["priority"] == new_priority
    assert len(unchanged) == 7


@pytest.mark.tc("TC-15")
def test_tc15_ktv_doi_gio_lich_hen(page: Page, bt3: System) -> None:
    """Kỹ thuật viên đổi giờ lịch trên trang "Lịch hẹn của tôi" sang 10:00, thời lượng 60 phút"""
    require_ui()
    ticket_id, technician_id, center_id, code = bookable_ticket(bt3)
    technician = bt3.technician_code(technician_id)
    day = bt3.free_working_day([technician_id], "09:00", 180)
    booked = book(token_for(bt3.manager_username(center_id)), ticket_id, day, "09:00", "09:30")

    login_ui(page, technician, "/my-tickets")
    page.get_by_role("link", name="Lịch hẹn của tôi").click()
    row = page.locator("tbody tr").filter(has_text=f"09:00:00 {vn_date(day)}").filter(has_text=code)
    expect(row).to_contain_text("ĐÃ HẸN")
    row.get_by_role("button", name="Đổi giờ").click()
    dialog = page.get_by_role("dialog")
    dialog.get_by_label("Giờ bắt đầu").fill("10:00")
    dialog.get_by_label("Thời lượng").select_option("60")
    expect(dialog.get_by_label("Giờ kết thúc")).to_have_value("11:00")
    image_a = shot(page, "TC-15")
    with page.expect_response(lambda r: r.request.method == "PUT" and "/api/appointments/" in r.url) as info:
        dialog.get_by_role("button", name="Lưu lịch hẹn").click()
    status = info.value.status
    expect(page.get_by_role("status")).to_contain_text(f"Đã đổi lịch hẹn của phiếu {code}")
    image_b = shot(page, "TC-15_b")

    after = appointment(bt3, booked["appointment_id"])
    bt3.facts.update(
        data=f"{technician}, phiếu {code}; lịch #{booked['appointment_id']} ngày {day:%d/%m/%Y} 09:00–09:30 → 10:00, 60 phút",
        actual=f"HTTP {status}; lịch #{booked['appointment_id']}: {hhmm(after['start_at'])}–{hhmm(after['end_at'])}, "
               f"status {after['status']}, KTV {bt3.technician_code(after['technician_id'])}",
        images=[image_a, image_b],
    )
    assert status == 200 and after["status"] == "DA_HEN"
    assert after["start_at"] == at(day, "10:00") and after["end_at"] == at(day, "11:00")


@pytest.mark.tc("TC-16")
def test_tc16_ql_huy_lich_hen_huy_mem(page: Page, bt3: System) -> None:
    """Quản lý hủy lịch ở trang chi tiết phiếu: lịch thành ĐÃ HỦY, bản ghi còn, khung giờ được giải phóng"""
    require_ui()
    ticket_id, technician_id, center_id, code = bookable_ticket(bt3)
    manager = bt3.manager_username(center_id)
    token = token_for(manager)
    day = bt3.free_working_day([technician_id], "09:00", 60)
    booked = book(token, ticket_id, day, "09:00", "09:30")
    rows_before = bt3.one("SELECT count(*) FROM appointment")[0]

    login_ui(page, manager, "/tickets")
    page.goto(f"{UI_URL}/tickets/{ticket_id}")
    section = page.locator("section", has=page.get_by_role("heading", name="Lịch hẹn của phiếu"))
    row = section.locator("tbody tr").filter(has_text=f"09:00:00 {vn_date(day)}")
    expect(row).to_contain_text("ĐÃ HẸN")
    row.get_by_role("button", name="Hủy lịch").click()
    image_a = shot(page, "TC-16")
    page.get_by_role("dialog").get_by_role("button", name="Xác nhận hủy lịch").click()
    expect(page.get_by_role("status")).to_contain_text("Đã hủy lịch hẹn")
    expect(row).to_contain_text("ĐÃ HỦY")
    image_b = shot(page, "TC-16_b")

    after = appointment(bt3, booked["appointment_id"])
    rows_after = bt3.one("SELECT count(*) FROM appointment")[0]
    rebook_status, rebook = api("POST", "/api/appointments", token, {
        "ticket_id": ticket_id, "appointment_type": "NHAN",
        "start_at": iso(at(day, "09:00")), "end_at": iso(at(day, "09:30"))})
    bt3.facts.update(
        data=f"{manager}, phiếu {code}; lịch #{booked['appointment_id']} {day:%d/%m/%Y} 09:00–09:30 (ĐÃ HẸN)",
        actual=f"lịch #{booked['appointment_id']} status {after['status']}; bảng appointment {rows_before} → {rows_after} "
               f"(không xoá dòng); đặt lại đúng khung đó: HTTP {rebook_status}",
        images=[image_a, image_b],
    )
    assert after["status"] == "DA_HUY" and rows_after == rows_before
    assert rebook_status == 201, rebook


@pytest.mark.tc("TC-17")
def test_tc17_hoan_tat_phai_xac_nhan(page: Page, bt3: System) -> None:
    """Kỹ thuật viên bấm Hoàn tất: "Quay lại" không đổi gì, "Xác nhận" mới chuyển HOÀN TẤT"""
    require_ui()
    ticket_id, technician_id, _, code = bookable_ticket(bt3)
    technician = bt3.technician_code(technician_id)
    status_pre, _ = api("PATCH", f"/api/tickets/{ticket_id}/status", token_for(technician), {"to_status": "DANG_XU_LY"})
    assert status_pre == 200
    logs_before = bt3.log_count(ticket_id)

    login_ui(page, technician, "/my-tickets")
    page.goto(f"{UI_URL}/my-tickets?ticket={ticket_id}")
    expect(page.get_by_role("heading", name=code)).to_be_visible()
    page.get_by_role("button", name="Hoàn tất").click()
    dialog = page.get_by_role("dialog")
    expect(dialog).to_contain_text("Hãy chắc rằng máy đã sửa xong")
    image_a = shot(page, "TC-17", full_page=False)
    dialog.get_by_role("button", name="Quay lại").click()
    after_back = (bt3.ticket(ticket_id)["status"], bt3.log_count(ticket_id))

    page.get_by_role("button", name="Hoàn tất").click()
    page.get_by_role("dialog").get_by_role("button", name="Xác nhận").click()
    expect(page.get_by_role("status")).to_have_text("Đã chuyển trạng thái sang HOÀN TẤT.")
    image_b = shot(page, "TC-17_b", full_page=False)
    after_confirm = (bt3.ticket(ticket_id)["status"], bt3.log_count(ticket_id))
    bt3.facts.update(
        data=f"{technician}, phiếu {code} đang DANG_XU_LY (log {logs_before}); mở bằng liên kết /my-tickets?ticket={ticket_id}",
        actual=f"sau \"Quay lại\": {after_back[0]}, log {after_back[1]}; sau \"Xác nhận\": {after_confirm[0]}, log {after_confirm[1]}",
        images=[image_a, image_b],
    )
    assert after_back == ("DANG_XU_LY", logs_before)
    assert after_confirm == ("HOAN_TAT", logs_before + 1)


# --- 2. GIÁ TRỊ BIÊN ------------------------------------------------------------------


@pytest.mark.tc("TC-18")
def test_tc18_bien_gio_lam_viec_khi_doi_gio(page: Page, bt3: System) -> None:
    """Biên giờ làm việc khi đổi giờ lịch: 17:30–18:00 được, 17:31–18:01 bị 400"""
    ticket_id, technician_id, center_id, code = bookable_ticket(bt3)
    token = token_for(bt3.manager_username(center_id))
    day = bt3.free_working_day([technician_id], "17:00", 60)
    booked = book(token, ticket_id, day, "17:00", "17:30")
    body = lambda start, end: {"appointment_type": "NHAN", "start_at": iso(at(day, start)),
                               "end_at": iso(at(day, end)), "note": "TC-18"}

    swagger_authorize(page, token)
    status_a, body_a, block = swagger_execute(
        page, "PUT", "/api/appointments/{appointment_id}", {"appointment_id": booked["appointment_id"]},
        body("17:30", "18:00"))
    image_a = shot(page, "TC-18", block)
    after_a = appointment(bt3, booked["appointment_id"])
    status_b, body_b, block = swagger_execute(
        page, "PUT", "/api/appointments/{appointment_id}", {"appointment_id": booked["appointment_id"]},
        body("17:31", "18:01"))
    image_b = shot(page, "TC-18_b", block)
    after_b = appointment(bt3, booked["appointment_id"])
    bt3.facts.update(
        data=f"lịch #{booked['appointment_id']} (phiếu {code}) ngày {day:%d/%m/%Y}; ranh giới 18:00: (a) 17:30–18:00, (b) 17:31–18:01",
        actual=f"(a) HTTP {status_a}, lịch {hhmm(after_a['start_at'])}–{hhmm(after_a['end_at'])}; "
               f"(b) HTTP {status_b} {(body_b or {}).get('error')}, lịch vẫn {hhmm(after_b['start_at'])}–{hhmm(after_b['end_at'])}",
        images=[image_a, image_b],
    )
    assert status_a == 200 and after_a["end_at"] == at(day, "18:00")
    assert status_b == 400 and body_b["error"] == "OUTSIDE_WORKING_HOURS" and after_b == after_a


@pytest.mark.tc("TC-19")
def test_tc19_bien_phan_trang_20_21(page: Page, bt3: System) -> None:
    """Biên phân trang danh sách phiếu: 20 phiếu MỚI là 1 trang, 21 phiếu là 2 trang (trang 2 có 1 dòng)"""
    require_ui()
    manager = bt3.manager_username(1)
    category = bt3.one("SELECT category_code FROM ticket WHERE center_id = 1 GROUP BY 1 ORDER BY count(*) DESC LIMIT 1")[0]
    count_new = lambda: bt3.one("SELECT count(*) FROM ticket WHERE center_id = 1 AND status = 'MOI'")[0]
    while count_new() > 20:  # keep exactly 20 MOI tickets (cancel the extra ones on the working copy)
        bt3.run("UPDATE ticket SET status = 'DA_HUY' WHERE ticket_id = (SELECT max(ticket_id) FROM ticket WHERE center_id = 1 AND status = 'MOI')")
    for _ in range(20 - count_new()):
        bt3.create_ticket(1, category)
    at_20 = count_new()

    login_ui(page, manager, "/tickets")
    rows = page.locator("table").first.locator("tbody tr")
    expect(rows).to_have_count(20)
    expect(page.get_by_text("Trang 1 / 1")).to_be_visible()
    image_a = shot(page, "TC-19")

    bt3.create_ticket(1, category, priority="THAP")
    at_21 = count_new()
    page.reload()
    expect(page.get_by_text("Trang 1 / 2")).to_be_visible()
    expect(rows).to_have_count(20)
    page.get_by_role("button", name="Sau").click()
    expect(page.get_by_text("Trang 2 / 2")).to_be_visible()
    expect(rows).to_have_count(1)
    image_b = shot(page, "TC-19_b")
    bt3.facts.update(
        data=f"{manager}; trên bản sao đặt đúng {at_20} phiếu MỚI ở trung tâm 1, sau đó thêm 1 phiếu (ưu tiên THẤP, xếp cuối)",
        actual=f"{at_20} phiếu: 20 dòng, \"Trang 1 / 1\"; {at_21} phiếu: trang 1 có 20 dòng, \"Trang 1 / 2\", trang 2 có 1 dòng",
        images=[image_a, image_b],
    )
    assert at_20 == 20 and at_21 == 21


# --- 3. DỮ LIỆU SAI -------------------------------------------------------------------


@pytest.mark.tc("TC-20")
def test_tc20_tao_phieu_du_lieu_sai_tren_giao_dien(page: Page, bt3: System) -> None:
    """Tạo phiếu trên giao diện với SĐT sai và hạn cam kết đã qua: báo lỗi đúng ô, không lưu phiếu"""
    require_ui()
    manager = bt3.manager_username(1)
    total_before = bt3.one("SELECT count(*) FROM ticket")[0]

    login_ui(page, manager, "/tickets")
    page.get_by_role("button", name="+ Tạo phiếu mới").click()
    dialog = page.get_by_role("dialog")
    dialog.get_by_label("Khách hàng").fill("Trần Văn Bình (TC-20)")
    dialog.get_by_label("Số điện thoại").fill("09123")
    dialog.get_by_label("Serial máy").fill("SN-TC20-0001")
    dialog.get_by_label("Mô tả lỗi").fill("Loa rè")
    with page.expect_response(lambda r: r.request.method == "POST" and r.url == f"{API_URL}/api/tickets") as info:
        dialog.get_by_role("button", name="Tạo phiếu").click()
    status_a, body_a = info.value.status, info.value.json()
    expect(dialog).to_contain_text("Số điện thoại phải gồm 10 chữ số")
    expect(dialog.get_by_label("Số điện thoại")).to_have_class(re.compile("invalid"))
    image_a = shot(page, "TC-20")

    dialog.get_by_label("Số điện thoại").fill("0912345620")
    dialog.get_by_label("Hạn cam kết (ngày)").fill((date.today() - timedelta(days=1)).isoformat())
    with page.expect_response(lambda r: r.request.method == "POST" and r.url == f"{API_URL}/api/tickets") as info:
        dialog.get_by_role("button", name="Tạo phiếu").click()
    status_b, body_b = info.value.status, info.value.json()
    expect(dialog).to_contain_text("Hạn cam kết phải ở tương lai")
    expect(dialog.get_by_label("Hạn cam kết (ngày)")).to_have_class(re.compile("invalid"))
    image_b = shot(page, "TC-20_b")
    total_after = bt3.one("SELECT count(*) FROM ticket")[0]
    bt3.facts.update(
        data=f"{manager}; (a) SĐT \"09123\"; (b) SĐT đúng, hạn cam kết {(date.today() - timedelta(days=1)):%d/%m/%Y} 17:00 (hôm qua)",
        actual=f"(a) HTTP {status_a} {body_a.get('error')}, ô SĐT đánh dấu đỏ; (b) HTTP {status_b} {body_b.get('error')}, "
               f"ô hạn cam kết đánh dấu đỏ; bảng ticket {total_before} → {total_after}",
        images=[image_a, image_b],
    )
    assert (status_a, body_a["error"]) == (400, "INVALID_PHONE")
    assert (status_b, body_b["error"]) == (400, "INVALID_DUE_DATE")
    assert total_after == total_before


@pytest.mark.tc("TC-21")
def test_tc21_doi_gio_trung_lich_tren_giao_dien(page: Page, bt3: System) -> None:
    """Đổi giờ lịch B trùng lịch A trên giao diện: 409, hiện khung trống gợi ý, lịch B giữ nguyên"""
    require_ui()
    ticket_id, technician_id, center_id, code = bookable_ticket(bt3)
    manager = bt3.manager_username(center_id)
    token = token_for(manager)
    day = bt3.free_working_day([technician_id], "09:00", 120)
    first = book(token, ticket_id, day, "09:00", "09:30")
    second = book(token, ticket_id, day, "10:00", "10:30", kind="GIAO")
    before = appointment(bt3, second["appointment_id"])

    login_ui(page, manager, "/tickets")
    page.goto(f"{UI_URL}/tickets/{ticket_id}")
    section = page.locator("section", has=page.get_by_role("heading", name="Lịch hẹn của phiếu"))
    section.locator("tbody tr").filter(has_text=f"10:00:00 {vn_date(day)}").get_by_role("button", name="Đổi giờ").click()
    page.get_by_label("Giờ bắt đầu").fill("09:00")
    with page.expect_response(lambda r: r.request.method == "PUT" and "/api/appointments/" in r.url) as info:
        page.get_by_role("button", name="Lưu lịch hẹn").click()
    status, body = info.value.status, info.value.json()
    expect(page.get_by_role("alert")).to_contain_text("Khung trống gần nhất")
    image_a = shot(page, "TC-21")
    after = appointment(bt3, second["appointment_id"])
    bt3.facts.update(
        data=f"{manager}, phiếu {code}, ngày {day:%d/%m/%Y}: lịch A #{first['appointment_id']} 09:00–09:30, "
             f"lịch B #{second['appointment_id']} 10:00–10:30; đổi B sang 09:00–09:30",
        actual=f"HTTP {status} {body.get('error')}; xung đột {[c['appointment_id'] for c in body.get('conflicts', [])]}, "
               f"gợi ý {len(body.get('free_slots', []))} khung trống; lịch B vẫn {hhmm(after['start_at'])}–{hhmm(after['end_at'])}",
        images=[image_a],
    )
    assert status == 409 and body["error"] == "APPOINTMENT_OVERLAP" and body["free_slots"]
    assert after == before


@pytest.mark.tc("TC-22")
def test_tc22_huy_khi_khong_con_hop_le(page: Page, bt3: System) -> None:
    """Hủy phiếu đã phân công và hủy lịch đã hủy đều bị 409; giao diện không hiện nút Hủy phiếu"""
    require_ui()
    ticket_id, technician_id, center_id, code = bookable_ticket(bt3)
    manager = bt3.manager_username(center_id)
    token = token_for(manager)
    day = bt3.free_working_day([technician_id], "09:00", 60)
    booked = book(token, ticket_id, day, "09:00", "09:30")
    assert api("DELETE", f"/api/appointments/{booked['appointment_id']}", token)[0] == 200
    logs_before = bt3.log_count(ticket_id)

    swagger_authorize(page, token)
    status_a, body_a, block = swagger_execute(page, "DELETE", "/api/tickets/{ticket_id}", {"ticket_id": ticket_id})
    image_a = shot(page, "TC-22", block)
    status_b, body_b, block = swagger_execute(
        page, "DELETE", "/api/appointments/{appointment_id}", {"appointment_id": booked["appointment_id"]})
    image_b = shot(page, "TC-22_b", block)
    login_ui(page, manager, "/tickets")
    page.goto(f"{UI_URL}/tickets/{ticket_id}")
    expect(page.get_by_role("heading", name=code)).to_be_visible()
    cancel_buttons = page.get_by_role("button", name="Hủy phiếu").count()
    image_c = shot(page, "TC-22_c")
    row = bt3.ticket(ticket_id)
    bt3.facts.update(
        data=f"{manager}; (a) phiếu {code} đang {row['status']}; (b) lịch #{booked['appointment_id']} đã DA_HUY; (c) mở trang chi tiết phiếu",
        actual=f"(a) HTTP {status_a} {(body_a or {}).get('error')}, phiếu vẫn {row['status']}, log {logs_before} → {bt3.log_count(ticket_id)}; "
               f"(b) HTTP {status_b} {(body_b or {}).get('error')}; (c) số nút \"Hủy phiếu\": {cancel_buttons}",
        images=[image_a, image_b, image_c],
    )
    assert status_a == 409 and body_a["error"] == "TICKET_NOT_CANCELLABLE" and row["status"] == "DA_PHAN_CONG"
    assert status_b == 409 and body_b["error"] == "APPOINTMENT_NOT_CANCELLABLE"
    assert cancel_buttons == 0 and bt3.log_count(ticket_id) == logs_before


# --- 4. BẢO MẬT / CHẤT LƯỢNG DỮ LIỆU ----------------------------------------------


def all_appointments(token: str) -> list[dict]:
    items: list[dict] = []
    page_no = 1
    while True:
        status, body = api("GET", f"/api/appointments?page={page_no}&page_size=100", token)
        assert status == 200, body
        items += body["items"]
        if len(items) >= body["total"] or not body["items"]:
            return items
        page_no += 1


@pytest.mark.tc("TC-23")
def test_tc23_a01_pham_vi_lich_hen(page: Page, bt3: System) -> None:
    """A01: danh sách lịch hẹn chỉ trả lịch trong phạm vi; KTV khác sửa/hủy lịch bị 403"""
    ticket_id, technician_id, center_id, code = bookable_ticket(bt3)
    manager = bt3.manager_username(center_id)
    owner = bt3.technician_code(technician_id)
    intruder = bt3.one(
        "SELECT technician_code FROM technician WHERE is_active AND technician_id <> %s ORDER BY technician_code LIMIT 1",
        technician_id)[0]
    day = bt3.free_working_day([technician_id], "09:00", 60)
    booked = book(token_for(manager), ticket_id, day, "09:00", "09:30")

    manager_items = all_appointments(token_for(manager))
    owner_items = all_appointments(token_for(owner))
    centers = {row[0] for row in bt3.all(
        "SELECT DISTINCT t.center_id FROM appointment a JOIN ticket t USING (ticket_id) WHERE a.appointment_id = ANY(%s)",
        [a["appointment_id"] for a in manager_items])}
    sql_center = bt3.one(
        "SELECT count(*) FROM appointment a JOIN ticket t USING (ticket_id) WHERE t.center_id = %s", center_id)[0]
    sql_owner = bt3.one("SELECT count(*) FROM appointment WHERE technician_id = %s", technician_id)[0]

    swagger_authorize(page, token_for(owner))
    status_l, body_l, block = swagger_execute(page, "GET", "/api/appointments", {"page_size": 100})
    image_a = shot(page, "TC-23", block)
    before = appointment(bt3, booked["appointment_id"])
    swagger_authorize(page, token_for(intruder))
    status_put, body_put, block = swagger_execute(
        page, "PUT", "/api/appointments/{appointment_id}", {"appointment_id": booked["appointment_id"]},
        {"appointment_type": "GIAO", "start_at": iso(at(day, "11:00")), "end_at": iso(at(day, "11:30")), "note": "xâm nhập"})
    image_b = shot(page, "TC-23_b", block)
    status_del, body_del, block = swagger_execute(
        page, "DELETE", "/api/appointments/{appointment_id}", {"appointment_id": booked["appointment_id"]})
    image_c = shot(page, "TC-23_c", block)
    after = appointment(bt3, booked["appointment_id"])
    bt3.facts.update(
        data=f"{manager} (trung tâm {center_id}), {owner} (chủ lịch #{booked['appointment_id']}), {intruder} (KTV khác)",
        actual=f"{manager}: {len(manager_items)} lịch, trung tâm {sorted(centers)} (SQL {sql_center}); "
               f"{owner}: {len(owner_items)} lịch, mọi dòng technician_id={technician_id}: "
               f"{all(a['technician_id'] == technician_id for a in owner_items)} (SQL {sql_owner}); "
               f"{intruder}: PUT HTTP {status_put} {(body_put or {}).get('error')}, DELETE HTTP {status_del} "
               f"{(body_del or {}).get('error')}; lịch vẫn {after['status']} {hhmm(after['start_at'])}",
        images=[image_a, image_b, image_c],
    )
    assert centers == {center_id} and len(manager_items) == sql_center
    assert all(a["technician_id"] == technician_id for a in owner_items) and len(owner_items) == sql_owner
    assert status_l == 200 and body_l["total"] == sql_owner
    assert status_put == 403 and status_del == 403 and after == before


@pytest.mark.tc("TC-24")
def test_tc24_a01_dieu_huong_giao_dien(page: Page, bt3: System) -> None:
    """A01 trên giao diện: KTV không vào được trang của Quản lý, không mở được phiếu người khác bằng liên kết"""
    require_ui()
    ticket_id, technician_id, center_id, code = bookable_ticket(bt3)
    technician = bt3.technician_code(technician_id)
    other_id, other_code = bt3.one(
        "SELECT ticket_id, ticket_code FROM ticket WHERE technician_id IS DISTINCT FROM %s ORDER BY ticket_id LIMIT 1",
        technician_id)

    login_ui(page, technician, "/my-tickets")
    visits = {}
    for path in ("/tickets", f"/tickets/{other_id}", f"/tickets/{other_id}/assign"):
        page.goto(f"{UI_URL}{path}")
        expect(page).to_have_url(f"{UI_URL}/my-tickets")
        visits[path] = page.url.replace(UI_URL, "")
    page.goto(f"{UI_URL}/my-tickets?ticket={other_id}")
    page.wait_for_load_state("networkidle")
    opened = page.get_by_role("heading", name=other_code).count()
    api_status, _ = api("GET", f"/api/tickets/{other_id}", token_for(technician))
    image_a = shot(page, "TC-24", full_page=False)

    page.get_by_role("button", name="Đăng xuất").click()
    manager = bt3.manager_username(center_id)
    login_ui(page, manager, "/tickets")
    page.goto(f"{UI_URL}/my-tickets")
    expect(page).to_have_url(f"{UI_URL}/tickets")
    image_b = shot(page, "TC-24_b")
    bt3.facts.update(
        data=f"{technician} mở {', '.join(visits)} và /my-tickets?ticket={other_id} (phiếu {other_code} không phải của mình); "
             f"{manager} mở /my-tickets",
        actual=f"KTV bị đưa về {set(visits.values())}; phiếu {other_code} hiện: {opened} lần; API GET phiếu đó: HTTP {api_status}; "
               f"Quản lý bị đưa về /tickets",
        images=[image_a, image_b],
    )
    assert set(visits.values()) == {"/my-tickets"} and opened == 0 and api_status == 403


# --- 5. TÁI LẬP ---------------------------------------------------------------------


@pytest.mark.tc("TC-25")
def test_tc25_nap_lai_khong_ghi_de_thao_tac(page: Page, bt3: System) -> None:
    """Chạy lại bước nạp dữ liệu sau khi người dùng đã thao tác: không nhân đôi, không ghi đè thay đổi"""
    require_ui()
    manager = bt3.manager_username(1)
    token = token_for(manager)
    status_c, created = api("POST", "/api/tickets", token, ticket_body(customer_name="Phạm Gia Huy (TC-25)"))
    assert status_c == 201, created
    cancel_id, cancel_code = bt3.one(
        "SELECT ticket_id, ticket_code FROM ticket WHERE center_id = 1 AND status = 'MOI' AND ticket_id <> %s ORDER BY ticket_id LIMIT 1",
        created["ticket_id"])
    assert api("DELETE", f"/api/tickets/{cancel_id}", token)[0] == 200
    tables = ("service_center", "technician", "technician_skill", "ticket", "ticket_status_log", "appointment")
    counts = lambda: {t: bt3.one(f"SELECT count(*) FROM {t}")[0] for t in tables}
    before = counts()

    source = urlparse(get_test_database_url())
    env = {**os.environ, "DB_NAME": WORK_DATABASE, "PYTHONIOENCODING": "utf-8",
           "DB_HOST": source.hostname or "localhost", "DB_PORT": str(source.port or 5432),
           "DB_USER": unquote(source.username or "postgres"), "DB_PASSWORD": unquote(source.password or "")}
    env.pop("DATABASE_URL", None)
    run = subprocess.run([sys.executable, "scripts/setup_all.py"], cwd=ROOT, env=env,
                         capture_output=True, text=True, encoding="utf-8", timeout=600)
    after = counts()
    cancelled = bt3.ticket(cancel_id)["status"]
    still_there = bt3.one("SELECT count(*) FROM ticket WHERE ticket_id = %s", created["ticket_id"])[0]

    login_ui(page, manager, "/tickets")
    page.get_by_role("tab", name="Đã hủy").click()
    expect(page.get_by_role("row", name=cancel_code)).to_be_visible()
    image_a = shot(page, "TC-25")
    bt3.facts.update(
        data=f"Trên bản sao: {manager} tạo phiếu {created['ticket_code']} và hủy phiếu {cancel_code} qua API, "
             f"rồi chạy lại scripts/setup_all.py vào {WORK_DATABASE}",
        actual=f"setup_all mã thoát {run.returncode}; số dòng trước {before} – sau {after}; "
               f"phiếu {cancel_code} vẫn {cancelled}; phiếu {created['ticket_code']} còn: {still_there == 1}; "
               f"tab \"Đã hủy\" vẫn có {cancel_code}",
        images=[image_a],
    )
    assert run.returncode == 0, run.stdout[-800:] + run.stderr[-800:]
    assert after == before and cancelled == "DA_HUY" and still_there == 1
