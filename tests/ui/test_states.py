"""TC14–TC17: loading, empty, error and 401 states of M1 on the real system.

``page.route`` is only used where the specification allows it: TC14 holds the
ticket-list request (slow response), TC16 aborts it, TC17 answers it with 401.
Every row shown on screen comes from the real backend.
"""

from __future__ import annotations

import json
import re
import time

import pytest
from playwright.sync_api import Page, expect

from tests.real_system import UI_URL, System, api, capture, token_for, ui_login

pytestmark = pytest.mark.system

TICKET_LIST = re.compile(r".*/api/tickets\?.*")


def center_with_new_tickets(system: System) -> tuple[int, str, int]:
    center_id, count = system.one(
        "SELECT center_id, count(*) FROM ticket WHERE status = 'MOI' GROUP BY 1 ORDER BY 1 LIMIT 1")
    return center_id, system.manager_username(center_id), count


@pytest.mark.tc("TC14")
def test_tc14_ui_trang_thai_dang_tai(page: Page, system: System) -> None:
    """Giao diện M1: trạng thái đang tải"""
    center_id, manager, count = center_with_new_tickets(system)
    held = []
    page.route(TICKET_LIST, lambda route: held.append((route, time.monotonic())))

    ui_login(page, manager)
    loading = page.get_by_test_id("state-loading")
    expect(loading).to_have_text("Đang tải dữ liệu…")
    expect(page.locator("table")).to_have_count(0)
    capture(page, "TC14_ui_trang_thai_dang_tai", wait_idle=False)
    route, held_at = held[0]
    page.wait_for_timeout(max(0, 3000 - (time.monotonic() - held_at) * 1000))
    delay = time.monotonic() - held_at
    route.continue_()
    page.unroute(TICKET_LIST)

    expect(loading).to_be_hidden()
    rows = page.locator("table tbody tr")
    expect(rows.first).to_be_visible()
    first_code = api("GET", "/api/tickets?status=MOI&page=1&page_size=20", token_for(manager))[1]["items"][0]["ticket_code"]
    expect(rows.first).to_contain_text(first_code)
    system.facts["data"] = f"Quản lý {manager} ({count} phiếu MOI thật); GET /api/tickets bị giữ {delay:.1f}s"
    system.facts["actual"] = (f"Trong lúc chờ: \"Đang tải dữ liệu…\", chưa có bảng; sau {delay:.1f}s bảng hiện "
                              f"{rows.count()} phiếu, dòng đầu {first_code}")


@pytest.mark.tc("TC15")
def test_tc15_ui_trang_thai_rong(page: Page, system: System) -> None:
    """Giao diện M1: trạng thái rỗng (không có phiếu chờ phân công)"""
    # The loader keeps 5 MOI tickets in every center, so one center is emptied on the working copy.
    center_id = system.one("SELECT max(center_id) FROM service_center")[0]
    removed = [row[0] for row in system.all(
        "SELECT ticket_code FROM ticket WHERE center_id = %s AND status = 'MOI' ORDER BY ticket_id", center_id)]
    system.run("DELETE FROM ticket_status_log WHERE ticket_id IN "
               "(SELECT ticket_id FROM ticket WHERE center_id = %s AND status = 'MOI')", center_id)
    system.run("DELETE FROM ticket WHERE center_id = %s AND status = 'MOI'", center_id)
    assert system.one("SELECT count(*) FROM ticket WHERE status = 'MOI' AND center_id = %s", center_id)[0] == 0
    manager = system.manager_username(center_id)

    ui_login(page, manager)
    expect(page.get_by_test_id("state-empty")).to_have_text("Không có phiếu chờ phân công")
    expect(page.get_by_test_id("state-error")).to_have_count(0)
    expect(page.locator(".notice.error")).to_have_count(0)
    capture(page, "TC15_ui_trang_thai_rong")
    system.facts["data"] = (f"Quản lý {manager}; trên bản sao đã xoá {len(removed)} phiếu MOI của trung tâm này "
                            f"({', '.join(removed)}); SQL đếm MOI = 0")
    system.facts["actual"] = "M1 hiện \"Không có phiếu chờ phân công\"; không có vùng lỗi, không có dải đỏ"


@pytest.mark.tc("TC16")
def test_tc16_ui_trang_thai_loi(page: Page, system: System) -> None:
    """Giao diện M1: trạng thái lỗi và nút Thử lại"""
    center_id, manager, count = center_with_new_tickets(system)
    page.route(TICKET_LIST, lambda route: route.abort())

    ui_login(page, manager)
    error = page.get_by_test_id("state-error")
    expect(error).to_contain_text("Không thể kết nối máy chủ. Vui lòng thử lại.")
    expect(page.get_by_test_id("retry-button")).to_be_visible()
    capture(page, "TC16_ui_trang_thai_loi_1_loi")

    page.unroute(TICKET_LIST)
    page.get_by_test_id("retry-button").click()
    expect(error).to_have_count(0)
    rows = page.locator("table tbody tr")
    expect(rows).to_have_count(count)
    capture(page, "TC16_ui_trang_thai_loi_2_thu_lai")
    system.facts["data"] = f"Quản lý {manager} ({count} phiếu MOI thật); GET /api/tickets bị chặn (abort) rồi bỏ chặn"
    system.facts["actual"] = ("Lần 1: \"Không thể kết nối máy chủ. Vui lòng thử lại.\" + nút Thử lại; "
                              f"sau khi bấm Thử lại: bảng hiện {count} phiếu thật, dải lỗi biến mất")


@pytest.mark.tc("TC17")
def test_tc17_ui_het_phien_dang_nhap_401(page: Page, system: System) -> None:
    """Giao diện: xử lý 401 (hết phiên) và đăng nhập sai"""
    center_id, manager, _ = center_with_new_tickets(system)
    ui_login(page, manager)
    expect(page.locator("table tbody tr").first).to_be_visible()
    assert page.evaluate("localStorage.getItem('access_token')")

    # (a) the API answers 401 → token removed, back to the login page.
    page.route(TICKET_LIST, lambda route: route.fulfill(
        status=401, content_type="application/json",
        body=json.dumps({"error": "UNAUTHORIZED", "message": "Vui lòng đăng nhập."}),
    ))
    page.reload()
    expect(page).to_have_url(f"{UI_URL}/login")
    expect(page.get_by_role("button", name="Đăng nhập")).to_be_visible()
    assert page.evaluate("localStorage.getItem('access_token')") is None
    capture(page, "TC17_ui_het_phien_dang_nhap_401_1_ve_dang_nhap")
    page.unroute(TICKET_LIST)

    # (b) wrong password → message on the form, no redirect loop.
    navigations = []
    page.on("framenavigated", lambda frame: navigations.append(frame.url) if frame == page.main_frame else None)
    page.get_by_label("Tên đăng nhập").fill(manager)
    page.get_by_label("Mật khẩu").fill("mat-khau-sai")
    page.get_by_role("button", name="Đăng nhập").click()
    expect(page.get_by_role("alert")).to_have_text("Sai tên đăng nhập hoặc mật khẩu")
    page.wait_for_timeout(1500)
    assert page.url == f"{UI_URL}/login" and navigations == []
    capture(page, "TC17_ui_het_phien_dang_nhap_401_2_sai_mat_khau")
    system.facts["data"] = f"Quản lý {manager}; GET /api/tickets trả 401 (page.route); mật khẩu sai \"mat-khau-sai\""
    system.facts["actual"] = ("(a) về /login, access_token = null; (b) thông báo \"Sai tên đăng nhập hoặc mật khẩu\", "
                              "không có điều hướng nào trong 1,5 giây")
