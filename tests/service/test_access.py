"""TC13: phone masking and role-based access on the real system."""

from __future__ import annotations

import re

import pytest
from playwright.sync_api import Page, expect

from tests.real_system import (
    ACTIVE_STATUSES, UI_URL, System, api, capture, swagger_authorize, swagger_execute, token_for, ui_login,
)

pytestmark = pytest.mark.system

MASKED = re.compile(r"^\d{3}\*{4}\d{3}$")


@pytest.mark.tc("TC13")
def test_tc13_che_so_dien_thoai_va_phan_quyen(page: Page, system: System) -> None:
    """Che số điện thoại và phân quyền theo vai trò"""
    t1, t1_code, phone, center_id, k_id, k_code = system.one(
        """SELECT t.ticket_id, t.ticket_code, t.customer_phone, t.center_id, k.technician_id, k.technician_code
           FROM ticket t JOIN technician k ON k.technician_id = t.technician_id
           WHERE k.is_active AND t.status = ANY(%s) ORDER BY t.ticket_id LIMIT 1""",
        list(ACTIVE_STATUSES),
    )
    t2, t2_code, other_code = system.one(
        """SELECT t.ticket_id, t.ticket_code, k.technician_code FROM ticket t
           JOIN technician k ON k.technician_id = t.technician_id
           WHERE t.technician_id <> %s ORDER BY t.ticket_id LIMIT 1""", k_id,
    )
    manager = system.manager_username(center_id)
    k_token = token_for(k_code)
    masked = f"{phone[:3]}****{phone[-3:]}"

    # (a) the technician sees only own tickets, phone masked.
    status, mine = api("GET", "/api/technicians/me/tickets", k_token)
    assert status == 200
    assert {t["technician_id"] for t in mine} == {k_id}
    assert len(mine) == system.one("SELECT count(*) FROM ticket WHERE technician_id = %s", k_id)[0]
    assert all(MASKED.match(t["customer_phone"]) for t in mine)
    assert next(t for t in mine if t["ticket_id"] == t1)["customer_phone"] == masked
    ui_login(page, k_code)
    expect(page).to_have_url(f"{UI_URL}/my-tickets")
    page.get_by_label("Trạng thái").select_option("DANG_LAM")
    row = page.locator("table").first.locator("tbody tr").filter(has_text=t1_code)
    expect(row).to_contain_text(masked)
    capture(page, "TC13_che_so_dien_thoai_va_phan_quyen")

    # (c) the technician cannot open a ticket of another technician.
    swagger_authorize(page, k_token)
    status_c, body_c, block = swagger_execute(page, "GET", "/api/tickets/{ticket_id}", {"ticket_id": t2})
    assert status_c == 403
    capture(page, "TC13_che_so_dien_thoai_va_phan_quyen_c", element=block)

    # (b) the manager of the center sees the full phone number.
    status_b, detail = api("GET", f"/api/tickets/{t1}", token_for(manager))
    assert status_b == 200 and detail["customer_phone"] == phone
    page.goto(f"{UI_URL}/my-tickets")
    page.get_by_role("button", name="Đăng xuất").click()
    ui_login(page, manager)
    expect(page).to_have_url(f"{UI_URL}/tickets")
    page.goto(f"{UI_URL}/tickets/{t1}/assign")
    expect(page.locator(".detail-grid")).to_contain_text(phone)
    capture(page, "TC13_che_so_dien_thoai_va_phan_quyen_b")

    system.facts["data"] = (f"T1 = {t1_code} của KTV {k_code} (SĐT khách {phone}); T2 = {t2_code} của {other_code}; "
                            f"Quản lý {manager}")
    system.facts["actual"] = (f"(a) {len(mine)} phiếu, tất cả của {k_code}, SĐT dạng che (T1: {masked}); "
                              f"(b) Quản lý thấy {phone}; (c) HTTP {status_c} \"{body_c['message']}\"")
