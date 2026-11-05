"""TC18: main flow M1 → M2 → M3 on the real system, one screenshot per step."""

from __future__ import annotations

import re
from datetime import datetime

import pytest
from playwright.sync_api import Page, expect

from tests.real_system import API_URL, UI_URL, System, api, at, capture, suggestion_rows, token_for, ui_login

pytestmark = pytest.mark.system

PRIORITY_ORDER = "CASE priority WHEN 'CAO' THEN 1 WHEN 'TRUNG_BINH' THEN 2 ELSE 3 END"
MASKED = re.compile(r"\d{3}\*{4}\d{3}")


@pytest.mark.tc("TC18")
def test_tc18_ui_e2e_luong_chinh(page: Page, system: System) -> None:
    """End-to-end luồng chính: phân công → đặt lịch hẹn → cập nhật trạng thái đến HOÀN TẤT"""
    center_id = system.one("SELECT min(center_id) FROM ticket WHERE status = 'MOI'")[0]
    manager = system.manager_username(center_id)
    expected_codes = [row[0] for row in system.all(
        f"SELECT ticket_code FROM ticket WHERE center_id = %s AND status = 'MOI' ORDER BY {PRIORITY_ORDER}, due_date, ticket_id",
        center_id,
    )]

    # b1 – M1 shows only this center's new tickets, CAO → TRUNG_BINH → THAP, then due date.
    ui_login(page, manager)
    expect(page).to_have_url(f"{UI_URL}/tickets")
    rows = page.locator("table tbody tr")
    expect(rows).to_have_count(len(expected_codes))
    assert [rows.nth(i).locator("td").first.inner_text() for i in range(len(expected_codes))] == expected_codes
    listed = api("GET", "/api/tickets?status=MOI&page=1&page_size=20", token_for(manager))[1]["items"]
    assert {t["status"] for t in listed} == {"MOI"} and {t["center_id"] for t in listed} == {center_id}
    capture(page, "TC18_ui_e2e_luong_chinh_b1_danh_sach_M1")

    # b2 – open the first ticket; suggestions have skill ≥ 3 and increasing workload.
    ticket_code = expected_codes[0]
    ticket_id = system.one("SELECT ticket_id FROM ticket WHERE ticket_code = %s", ticket_code)[0]
    rows.first.get_by_role("button", name="Phân công").click()
    expect(page).to_have_url(f"{UI_URL}/tickets/{ticket_id}/assign")
    expect(page.get_by_role("heading", name=ticket_code)).to_be_visible()
    suggestions = suggestion_rows(page)
    assert suggestions and all(skill >= 3 for _, skill, _ in suggestions)
    workloads = [w for _, _, w in suggestions]
    assert workloads == sorted(workloads)
    capture(page, "TC18_ui_e2e_luong_chinh_b2_goi_y_M2")

    # b3 – assign the first suggested technician.
    p_code = suggestions[0][0]
    p_id = system.one("SELECT technician_id FROM technician WHERE technician_code = %s", p_code)[0]
    history = page.locator("table").last.locator("tbody tr")
    history_before = history.count()
    with page.expect_response(lambda r: r.request.method == "POST" and "/assignment" in r.url) as info:
        page.get_by_role("button", name="Xác nhận phân công").click()
    assert info.value.status == 201
    expect(page.get_by_role("status")).to_contain_text(f"Đã phân công phiếu cho kỹ thuật viên {p_code}")
    expect(page.locator(".detail-grid")).to_contain_text("ĐÃ PHÂN CÔNG")
    expect(history).to_have_count(history_before + 1)
    capture(page, "TC18_ui_e2e_luong_chinh_b3_phan_cong_xong")

    # b4 – book a GIAO appointment 09:00–09:30 on day D.
    day = system.free_working_day([p_id], "09:00", 30)
    page.get_by_role("button", name="Đặt lịch hẹn").click()
    page.get_by_label("Loại").select_option("GIAO")
    page.get_by_label("Ngày").fill(day.isoformat())
    page.get_by_label("Giờ bắt đầu").fill("09:00")
    with page.expect_response(lambda r: r.request.method == "POST" and r.url == f"{API_URL}/api/appointments") as info:
        page.get_by_role("button", name="Lưu lịch hẹn").click()
    assert info.value.status == 201
    expect(page.get_by_role("status")).to_contain_text("Đã đặt lịch GIAO lúc 09:00–09:30")
    booked = page.locator("section", has=page.get_by_role("heading", name="Lịch hẹn của phiếu")).locator("tbody tr")
    expect(booked.filter(has_text=f"09:00:00 {day.day}/{day.month}/{day.year}")).to_contain_text("ĐÃ HẸN")
    capture(page, "TC18_ui_e2e_luong_chinh_b4_dat_lich_xong")

    # b5 – the technician sees the ticket in M3 with a masked phone number.
    page.get_by_role("button", name="Đăng xuất").click()
    ui_login(page, p_code)
    expect(page).to_have_url(f"{UI_URL}/my-tickets")
    status_filter = page.get_by_label("Trạng thái")
    status_filter.select_option("DANG_LAM")
    row = page.locator("table").first.locator("tbody tr").filter(has_text=ticket_code)
    expect(row).to_contain_text("ĐÃ PHÂN CÔNG")
    assert MASKED.search(row.inner_text())
    capture(page, "TC18_ui_e2e_luong_chinh_b5_phieu_cua_toi_M3")

    # b6 – start repairing.
    row.get_by_role("button", name=ticket_code).click()
    expect(page.get_by_role("heading", name=ticket_code)).to_be_visible()
    page.get_by_label("Ghi chú (tối đa 255 ký tự)").fill("Đã kiểm tra thiết bị")
    page.get_by_role("button", name="Bắt đầu sửa").click()
    expect(page.get_by_role("status")).to_have_text("Đã chuyển trạng thái sang ĐANG XỬ LÝ.")
    expect(row).to_contain_text("ĐANG XỬ LÝ")
    capture(page, "TC18_ui_e2e_luong_chinh_b6_dang_xu_ly")

    # b7 – complete the ticket.
    page.get_by_role("button", name="Hoàn tất").click()
    expect(page.get_by_role("status")).to_have_text("Đã chuyển trạng thái sang HOÀN TẤT.")
    status_filter.select_option("HOAN_TAT")
    expect(page.locator("table").first.locator("tbody tr").filter(has_text=ticket_code)).to_contain_text("HOÀN TẤT")
    capture(page, "TC18_ui_e2e_luong_chinh_b7_hoan_tat")

    # Database at the end of the flow.
    assert system.ticket(ticket_id)["status"] == "HOAN_TAT"
    transitions = system.all(
        "SELECT from_status, to_status FROM ticket_status_log WHERE ticket_id = %s ORDER BY changed_at, log_id", ticket_id)
    assert transitions[-3:] == [("MOI", "DA_PHAN_CONG"), ("DA_PHAN_CONG", "DANG_XU_LY"), ("DANG_XU_LY", "HOAN_TAT")]
    appointments = system.all(
        "SELECT appointment_type, status, start_at FROM appointment WHERE ticket_id = %s", ticket_id)
    assert appointments == [("GIAO", "DA_HEN", at(day, "09:00"))]
    system.facts["data"] = (f"Quản lý {manager}; phiếu MỚI thật {ticket_code}; KTV đầu danh sách {p_code} "
                            f"(khối lượng {workloads[0]}); lịch GIAO 09:00–09:30 ngày {day:%d/%m/%Y}")
    system.facts["actual"] = (f"b1 {len(expected_codes)} phiếu MOI đúng thứ tự; b2 {len(suggestions)} gợi ý, khối lượng "
                              f"{workloads}; b3 HTTP 201, lịch sử +1 dòng; b4 HTTP 201, ĐÃ HẸN; b5 SĐT dạng che; "
                              "b6 ĐANG XỬ LÝ; b7 HOÀN TẤT; CSDL: HOAN_TAT, log MOI → DA_PHAN_CONG → DANG_XU_LY → "
                              "HOAN_TAT, 1 lịch DA_HEN")
