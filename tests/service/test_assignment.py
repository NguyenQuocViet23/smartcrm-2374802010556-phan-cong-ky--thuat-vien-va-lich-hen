"""TC04–TC07 and TC12: assignment and technician change (UC3, UC4) on the real system."""

from __future__ import annotations

import re

import pytest
from playwright.sync_api import Page, expect

from tests.real_system import (
    API_URL, System, api, capture, open_assign_page, suggestion_rows, swagger_authorize, swagger_execute,
    token_for,
)

pytestmark = pytest.mark.system


def assignment_response(page: Page, ticket_id: int, method: str):
    return page.expect_response(
        lambda r: r.request.method == method and r.url.startswith(f"{API_URL}/api/tickets/{ticket_id}/assignment")
    )


def real_new_ticket(system: System, min_suggestions: int = 1) -> tuple[int, str, int, str]:
    """A real MOI ticket whose (center, category) has enough eligible technicians."""
    return system.one(
        """SELECT t.ticket_id, t.ticket_code, t.center_id, t.category_code FROM ticket t
           WHERE t.status = 'MOI' AND (
             SELECT count(*) FROM technician k JOIN technician_skill s USING (technician_id)
             WHERE k.center_id = t.center_id AND k.is_active AND s.category_code = t.category_code
               AND s.proficiency >= 3) >= %s
           ORDER BY t.ticket_id LIMIT 1""",
        min_suggestions,
    )


@pytest.mark.tc("TC04")
def test_tc04_phan_cong_thanh_cong(page: Page, system: System) -> None:
    """Phân công kỹ thuật viên thành công và ghi lịch sử trạng thái"""
    ticket_id, ticket_code, center_id, category = real_new_ticket(system)
    manager = system.manager_username(center_id)
    suggestions = api("GET", f"/api/tickets/{ticket_id}/technician-suggestions", token_for(manager))[1]["suggestions"]
    first = suggestions[0]
    logs_before = system.log_count(ticket_id)

    open_assign_page(page, manager, ticket_id)
    expect(page.locator("table").first.locator("tbody tr").first.get_by_role("radio")).to_be_checked()
    with assignment_response(page, ticket_id, "POST") as info:
        page.get_by_role("button", name="Xác nhận phân công").click()
    response = info.value
    body = response.json()

    assert response.status == 201
    assert body["status"] == "DA_PHAN_CONG" and body["technician_id"] == first["technician_id"]
    assert body["assigned_by"] is not None and body["assigned_at"]
    after = system.ticket(ticket_id)
    assert (after["status"], after["technician_id"]) == ("DA_PHAN_CONG", first["technician_id"])
    assert system.log_count(ticket_id) == logs_before + 1
    log = system.one(
        """SELECT event_type, from_status, to_status, to_technician_id, changed_by, changed_at
           FROM ticket_status_log WHERE ticket_id = %s ORDER BY changed_at DESC, log_id DESC LIMIT 1""",
        ticket_id,
    )
    assert log[:4] == ("TRANG_THAI", "MOI", "DA_PHAN_CONG", first["technician_id"])
    assert log[4] is not None and log[5] is not None
    expect(page.get_by_role("status")).to_contain_text(f"Đã phân công phiếu cho kỹ thuật viên {first['technician_code']}")
    expect(page.locator(".detail-grid")).to_contain_text("ĐÃ PHÂN CÔNG")
    capture(page, "TC04_phan_cong_thanh_cong")
    system.facts["data"] = (f"Phiếu MỚI thật {ticket_code} (trung tâm {manager[3:]}, nhóm {category}); "
                            f"KTV đầu danh sách {first['technician_code']} (khối lượng {first['workload']})")
    system.facts["actual"] = (f"HTTP 201, status DA_PHAN_CONG, technician_id {body['technician_id']}, "
                              f"assigned_by {body['assigned_by']}; log {logs_before} → {logs_before + 1} dòng "
                              "(TRANG_THAI, MOI → DA_PHAN_CONG)")


@pytest.mark.tc("TC05")
def test_tc05_bien_tay_nghe_bang_3(page: Page, system: System) -> None:
    """Biên: kỹ thuật viên có tay nghề đúng bằng 3 được phân công"""
    ticket_id, ticket_code, center_id, category = real_new_ticket(system)
    q_id, q_code = system.one(
        """SELECT k.technician_id, k.technician_code FROM technician k
           LEFT JOIN technician_skill s ON s.technician_id = k.technician_id AND s.category_code = %s
           WHERE k.center_id = %s AND k.is_active
           ORDER BY (coalesce(s.proficiency, 0) >= 3), k.technician_code LIMIT 1""",
        category, center_id,
    )
    system.set_skill(q_id, category, 3)
    manager = system.manager_username(center_id)

    open_assign_page(page, manager, ticket_id)
    row = page.locator("table").first.locator("tbody tr").filter(has_text=q_code)
    expect(row.locator("td").nth(4)).to_have_text("3")
    row.get_by_role("radio").check()
    with assignment_response(page, ticket_id, "POST") as info:
        page.get_by_role("button", name="Xác nhận phân công").click()
    response = info.value

    assert response.status == 201
    after = system.ticket(ticket_id)
    assert (after["status"], after["technician_id"]) == ("DA_PHAN_CONG", q_id)
    expect(page.get_by_role("status")).to_contain_text(f"kỹ thuật viên {q_code}")
    capture(page, "TC05_bien_tay_nghe_bang_3")
    system.facts["data"] = (f"Phiếu MỚI thật {ticket_code} (trung tâm {manager[3:]}, nhóm {category}); "
                            f"KTV {q_code} cùng trung tâm, đặt proficiency {category} = 3 trên bản sao")
    system.facts["actual"] = f"HTTP 201; phiếu DA_PHAN_CONG, technician_id = {q_id} ({q_code})"


@pytest.mark.tc("TC06")
def test_tc06_bien_tay_nghe_bang_2(page: Page, system: System) -> None:
    """Biên: kỹ thuật viên có tay nghề bằng 2 bị từ chối"""
    ticket_id, ticket_code, center_id, category = real_new_ticket(system)
    r_id, r_code = system.one(
        "SELECT technician_id, technician_code FROM technician WHERE center_id = %s AND is_active ORDER BY technician_code LIMIT 1",
        center_id,
    )
    system.set_skill(r_id, category, 2)
    manager = system.manager_username(center_id)
    logs_before = system.log_count(ticket_id)

    swagger_authorize(page, token_for(manager))
    status, body, block = swagger_execute(page, "POST", "/api/tickets/{ticket_id}/assignment",
                                          {"ticket_id": ticket_id}, {"technician_id": r_id})

    assert status == 400
    assert body["error"] == "TECHNICIAN_NOT_ELIGIBLE"
    assert "(< 3)" in body["message"]
    after = system.ticket(ticket_id)
    assert (after["status"], after["technician_id"]) == ("MOI", None)
    assert system.log_count(ticket_id) == logs_before
    capture(page, "TC06_bien_tay_nghe_bang_2", element=block)
    system.facts["data"] = (f"Phiếu MỚI thật {ticket_code} (trung tâm {manager[3:]}, nhóm {category}); "
                            f"KTV {r_code} (id {r_id}) đặt proficiency {category} = 2 trên bản sao")
    system.facts["actual"] = (f"HTTP 400 {body['error']}: \"{body['message']}\"; phiếu vẫn MOI, technician_id NULL; "
                              f"log giữ {logs_before} dòng")


@pytest.mark.tc("TC07")
def test_tc07_phan_cong_phieu_da_co_ktv(page: Page, system: System, browser) -> None:
    """Từ chối phân công khi phiếu đã được phân công"""
    ticket_id, ticket_code, center_id, category = real_new_ticket(system, min_suggestions=2)
    manager = system.manager_username(center_id)

    # Session 1 opens M2 while the ticket is still new.
    open_assign_page(page, manager, ticket_id)
    rows = suggestion_rows(page)
    p_code, q_code = rows[0][0], rows[1][0]

    # Session 2 (another browser session of the center manager) assigns P first.
    other = browser.new_context()
    try:
        page2 = other.new_page()
        open_assign_page(page2, manager, ticket_id)
        with assignment_response(page2, ticket_id, "POST") as first:
            page2.get_by_role("button", name="Xác nhận phân công").click()
        assert first.value.status == 201
    finally:
        other.close()
    logs_after_first = system.log_count(ticket_id)

    # Session 1, still showing the stale page, tries to assign Q.
    page.locator("table").first.locator("tbody tr").filter(has_text=q_code).get_by_role("radio").check()
    with assignment_response(page, ticket_id, "POST") as second:
        page.get_by_role("button", name="Xác nhận phân công").click()
    response = second.value
    body = response.json()

    assert response.status == 409
    assert body["error"] == "TICKET_ALREADY_ASSIGNED"
    assert p_code in body["message"]
    p_id = system.one("SELECT technician_id FROM technician WHERE technician_code = %s", p_code)[0]
    assert system.ticket(ticket_id)["technician_id"] == p_id
    assert system.log_count(ticket_id) == logs_after_first
    expect(page.get_by_role("alert")).to_contain_text("EX-2a")
    capture(page, "TC07_phan_cong_phieu_da_co_ktv")
    system.facts["data"] = (f"Phiếu MỚI thật {ticket_code} (trung tâm {manager[3:]}, nhóm {category}); "
                            f"phiên 2 phân công {p_code}, phiên 1 thử phân công {q_code}")
    system.facts["actual"] = (f"Phiên 2: HTTP 201. Phiên 1: HTTP 409 {body['error']}: \"{body['message']}\"; "
                              f"phiếu vẫn thuộc {p_code}; log không tăng thêm")


@pytest.mark.tc("TC12")
def test_tc12_doi_ktv_thieu_ly_do(page: Page, system: System) -> None:
    """Đổi kỹ thuật viên: bắt buộc có lý do, lý do rỗng bị từ chối"""
    ticket_id, ticket_code, center_id, category, k1_id = system.one(
        """SELECT t.ticket_id, t.ticket_code, t.center_id, t.category_code, t.technician_id FROM ticket t
           WHERE t.status = 'DA_PHAN_CONG' AND EXISTS (
             SELECT 1 FROM technician k JOIN technician_skill s USING (technician_id)
             WHERE k.center_id = t.center_id AND k.is_active AND s.category_code = t.category_code
               AND s.proficiency >= 3 AND k.technician_id <> t.technician_id)
           ORDER BY t.ticket_id LIMIT 1"""
    )
    k2_id, k2_code = system.one(
        """SELECT k.technician_id, k.technician_code FROM technician k JOIN technician_skill s USING (technician_id)
           WHERE k.center_id = %s AND k.is_active AND s.category_code = %s AND s.proficiency >= 3
             AND k.technician_id <> %s ORDER BY k.technician_code LIMIT 1""",
        center_id, category, k1_id,
    )
    k1_code = system.technician_code(k1_id)
    manager = system.manager_username(center_id)
    logs_before = system.log_count(ticket_id)

    swagger_authorize(page, token_for(manager))
    status_a, body_a, block = swagger_execute(page, "PUT", "/api/tickets/{ticket_id}/assignment",
                                              {"ticket_id": ticket_id}, {"technician_id": k2_id, "reason": ""})
    capture(page, "TC12_doi_ktv_thieu_ly_do_a", element=block)
    status_b, body_b, _ = swagger_execute(page, "PUT", "/api/tickets/{ticket_id}/assignment",
                                          {"ticket_id": ticket_id}, {"technician_id": k2_id, "reason": "   "})
    assert (status_a, status_b) == (400, 400)
    assert system.ticket(ticket_id)["technician_id"] == k1_id
    assert system.log_count(ticket_id) == logs_before

    reason = "Kỹ thuật viên cũ nghỉ phép"
    open_assign_page(page, manager, ticket_id)
    page.locator("table").first.locator("tbody tr").filter(has_text=k2_code).get_by_role("radio").check()
    page.get_by_label("Lý do đổi").fill(reason)
    with assignment_response(page, ticket_id, "PUT") as info:
        page.get_by_role("button", name="Lưu đổi kỹ thuật viên").click()
    status_c = info.value.status

    assert status_c == 200
    after = system.ticket(ticket_id)
    assert (after["technician_id"], after["status"]) == (k2_id, "DA_PHAN_CONG")
    assert system.log_count(ticket_id) == logs_before + 1
    log = system.one(
        """SELECT event_type, from_technician_id, to_technician_id, note FROM ticket_status_log
           WHERE ticket_id = %s ORDER BY changed_at DESC, log_id DESC LIMIT 1""", ticket_id,
    )
    assert log == ("DOI_KTV", k1_id, k2_id, reason)
    history = page.locator("table").last.locator("tbody tr").last
    expect(history).to_contain_text("ĐỔI KỸ THUẬT VIÊN")
    expect(history).to_contain_text(f"{k1_code} → {k2_code}")
    capture(page, "TC12_doi_ktv_thieu_ly_do")
    system.facts["data"] = (f"Phiếu thật {ticket_code} (trung tâm {manager[3:]}, nhóm {category}) đang thuộc {k1_code}; "
                            f"K2 = {k2_code}")
    system.facts["actual"] = (f"(a) reason \"\": HTTP {status_a} {body_a['error']}; (b) reason \"   \": HTTP {status_b} "
                              f"{body_b['error']}; (c) lý do hợp lệ: HTTP {status_c}, phiếu chuyển sang {k2_code}, "
                              f"vẫn DA_PHAN_CONG; log thêm 1 dòng DOI_KTV {k1_code} → {k2_code}")
