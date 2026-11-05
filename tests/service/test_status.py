"""TC11: status lifecycle (UC7) on the real system, through Swagger."""

from __future__ import annotations

import pytest
from playwright.sync_api import Page

from tests.real_system import System, capture, swagger_authorize, swagger_execute, token_for

pytestmark = pytest.mark.system

PATH = "/api/tickets/{ticket_id}/status"


@pytest.mark.tc("TC11")
def test_tc11_chuyen_trang_thai_lui(page: Page, system: System) -> None:
    """Từ chối chuyển trạng thái lùi, nhảy bước hoặc giá trị không hợp lệ"""
    k_id, k_code = system.one(
        """SELECT k.technician_id, k.technician_code FROM technician k
           WHERE k.is_active
             AND EXISTS (SELECT 1 FROM ticket WHERE technician_id = k.technician_id AND status = 'HOAN_TAT')
             AND EXISTS (SELECT 1 FROM ticket WHERE technician_id = k.technician_id AND status = 'DA_PHAN_CONG')
           ORDER BY k.technician_code LIMIT 1"""
    )
    t1, t1_code = system.one(
        "SELECT ticket_id, ticket_code FROM ticket WHERE technician_id = %s AND status = 'HOAN_TAT' ORDER BY ticket_id LIMIT 1", k_id)
    t2, t2_code = system.one(
        "SELECT ticket_id, ticket_code FROM ticket WHERE technician_id = %s AND status = 'DA_PHAN_CONG' ORDER BY ticket_id LIMIT 1", k_id)
    logs = {t1: system.log_count(t1), t2: system.log_count(t2)}

    swagger_authorize(page, token_for(k_code))
    status_a, body_a, block = swagger_execute(page, "PATCH", PATH, {"ticket_id": t1}, {"to_status": "DANG_XU_LY"})
    capture(page, "TC11_chuyen_trang_thai_lui", element=block)
    status_b, body_b, block = swagger_execute(page, "PATCH", PATH, {"ticket_id": t2}, {"to_status": "HOAN_TAT"})
    capture(page, "TC11_chuyen_trang_thai_lui_b", element=block)
    status_c, body_c, block = swagger_execute(page, "PATCH", PATH, {"ticket_id": t2}, {"to_status": "ABC"})
    capture(page, "TC11_chuyen_trang_thai_lui_c", element=block)

    assert (status_a, status_b, status_c) == (409, 409, 400)
    assert body_a["error"] == body_b["error"] == "INVALID_STATUS_TRANSITION"
    assert system.ticket(t1)["status"] == "HOAN_TAT"
    assert system.ticket(t2)["status"] == "DA_PHAN_CONG"
    assert {t1: system.log_count(t1), t2: system.log_count(t2)} == logs
    system.facts["data"] = f"KTV {k_code}; T1 = {t1_code} (HOAN_TAT), T2 = {t2_code} (DA_PHAN_CONG)"
    system.facts["actual"] = (f"(a) HTTP {status_a} \"{body_a['message']}\"; (b) HTTP {status_b} \"{body_b['message']}\"; "
                              f"(c) HTTP {status_c} {body_c['error']}; T1 vẫn HOAN_TAT, T2 vẫn DA_PHAN_CONG; log không đổi")
