"""End-to-end main flow of L04 on the real running system.

Nothing is mocked: the browser drives the Vite frontend, which calls a real
FastAPI backend started by this test on the working database
``smartcrm_work_test`` (freshly cloned from ``smartcrm_test``, which holds the
real case-study data). The main database ``smartcrm`` is never touched.

Screenshots are saved to ``docs/test-evidence/E2E_*.png``.

Prerequisites: PostgreSQL with ``smartcrm_test`` loaded, ``TEST_DB_NAME`` set,
the Vite dev server running on port 5173 and port 8000 free.
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from collections.abc import Iterator
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlparse

import psycopg
import pytest
from dotenv import load_dotenv
from playwright.sync_api import Page, expect

from tests.conftest import WORK_DATABASE, clone_work_database, get_test_database_url

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = ROOT / "docs" / "test-evidence"
UI_URL = os.getenv("UI_BASE_URL", "http://localhost:5173")
API_URL = "http://localhost:8000"
LOCAL_TIME = timezone(timedelta(hours=7))
CENTER_ID = 1

load_dotenv(ROOT / ".env")
pytestmark = pytest.mark.e2e


def _reachable(url: str) -> bool:
    try:
        urllib.request.urlopen(url, timeout=2)
        return True
    except urllib.error.HTTPError:
        return True
    except OSError:
        return False


def _wait_until(check, timeout: float = 30.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if check():
            return
        time.sleep(0.3)
    raise TimeoutError("Hết thời gian chờ dịch vụ khởi động/dừng.")


class Backend:
    """A uvicorn process bound to the working database, which the test can stop."""

    def __init__(self) -> None:
        self.process: subprocess.Popen | None = None

    def start(self) -> None:
        env = {**os.environ, "DB_NAME": WORK_DATABASE}
        env.pop("DATABASE_URL", None)
        self.process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app.main:app",
             "--app-dir", "src/backend", "--port", "8000"],
            cwd=ROOT, env=env,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        _wait_until(lambda: _reachable(f"{API_URL}/db-check"))

    def stop(self) -> None:
        if self.process is not None:
            self.process.terminate()
            self.process.wait(timeout=15)
            self.process = None
        _wait_until(lambda: not _reachable(f"{API_URL}/db-check"))


def _work_connection() -> psycopg.Connection:
    url = urlparse(get_test_database_url())._replace(path=f"/{WORK_DATABASE}", query="")
    return psycopg.connect(url.geturl())


@pytest.fixture
def backend() -> Iterator[Backend]:
    if not os.getenv("DEMO_PASSWORD"):
        pytest.fail("Chưa đặt DEMO_PASSWORD trong .env.")
    if not _reachable(UI_URL):
        pytest.fail(f"Frontend chưa chạy tại {UI_URL}: chạy `npm run dev` trong src/frontend.")
    if _reachable(f"{API_URL}/db-check"):
        pytest.fail("Cổng 8000 đang có backend khác; hãy tắt nó để test tự chạy backend trên DB làm việc.")
    clone_work_database(WORK_DATABASE)
    server = Backend()
    server.start()
    yield server
    if server.process is not None:
        server.stop()


def shot(page: Page, name: str, full_page: bool = True) -> None:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    page.wait_for_load_state("networkidle")
    page.screenshot(path=str(EVIDENCE_DIR / f"E2E_{name}.png"), full_page=full_page)


def login(page: Page, username: str) -> None:
    page.goto(f"{UI_URL}/login")
    page.get_by_label("Tên đăng nhập").fill(username)
    page.get_by_label("Mật khẩu").fill(os.environ["DEMO_PASSWORD"])
    page.get_by_role("button", name="Đăng nhập").click()


def pick_scenario() -> dict:
    """Choose real rows: a MOI ticket that has eligible technicians, an empty filter and a free slot."""
    with _work_connection() as connection:
        center_code = connection.execute(
            "SELECT center_code FROM service_center WHERE center_id = %s", (CENTER_ID,)
        ).fetchone()[0]
        ticket_id, ticket_code = connection.execute(
            """SELECT t.ticket_id, t.ticket_code FROM ticket t
               WHERE t.center_id = %s AND t.status = 'MOI' AND t.technician_id IS NULL
                 AND EXISTS (
                   SELECT 1 FROM technician k
                   JOIN technician_skill s ON s.technician_id = k.technician_id
                   WHERE k.center_id = t.center_id AND k.is_active
                     AND s.category_code = t.category_code AND s.proficiency >= 3)
               ORDER BY CASE t.priority WHEN 'CAO' THEN 1 WHEN 'TRUNG_BINH' THEN 2 ELSE 3 END,
                        t.due_date, t.ticket_id
               LIMIT 1""",
            (CENTER_ID,),
        ).fetchone()
        empty_category = connection.execute(
            """SELECT c FROM unnest(ARRAY['MAN_HINH','PIN','SAC','PHAN_MEM','NUOC_VAO','KHAC']) AS c
               WHERE NOT EXISTS (SELECT 1 FROM ticket
                                 WHERE center_id = %s AND status = 'MOI' AND category_code = c)
               LIMIT 1""",
            (CENTER_ID,),
        ).fetchone()[0]
    return {
        "manager": f"QL_{center_code}",
        "ticket_id": ticket_id,
        "ticket_code": ticket_code,
        "empty_category": empty_category,
    }


def free_slot(technician_id: int) -> datetime:
    """First free 30-minute slot of the technician on a working day about 35 days ahead."""
    day = date.today() + timedelta(days=35)
    while day.weekday() == 6:
        day += timedelta(days=1)
    with _work_connection() as connection:
        for minutes in range(8 * 60, 17 * 60 + 31, 30):
            start = datetime.combine(day, datetime.min.time(), LOCAL_TIME) + timedelta(minutes=minutes)
            busy = connection.execute(
                """SELECT 1 FROM appointment WHERE technician_id = %s AND status = 'DA_HEN'
                     AND start_at < %s AND %s < end_at""",
                (technician_id, start + timedelta(minutes=30), start),
            ).fetchone()
            if not busy:
                return start
    raise AssertionError("Không tìm được khung giờ trống cho kỹ thuật viên.")


@pytest.mark.tc("E2E")
def test_main_flow_from_assignment_to_completion(page: Page, backend: Backend) -> None:
    """Luồng chính L04 trên hệ thống thật: phân công → đặt lịch → KTV hoàn tất phiếu"""
    scenario = pick_scenario()
    ticket_code = scenario["ticket_code"]

    # 1. Quản lý đăng nhập và xem phiếu MOI của trung tâm (M1).
    login(page, scenario["manager"])
    expect(page).to_have_url(f"{UI_URL}/tickets")
    expect(page.get_by_role("cell", name=ticket_code)).to_be_visible()
    shot(page, "01_M1_danh_sach_phieu_moi")

    # 2. Bộ lọc không có phiếu → trạng thái rỗng.
    page.get_by_label("Nhóm sự cố").select_option(scenario["empty_category"])
    expect(page.get_by_test_id("state-empty")).to_have_text("Không có phiếu chờ phân công")
    shot(page, "02_M1_trang_thai_rong")

    # 3. Backend bị tắt → thông báo lỗi có nút Thử lại; bật lại → dữ liệu trở lại.
    backend.stop()
    page.get_by_label("Nhóm sự cố").select_option("")
    expect(page.get_by_test_id("state-error")).to_contain_text("Không thể kết nối máy chủ")
    expect(page.get_by_test_id("retry-button")).to_be_visible()
    shot(page, "03_M1_loi_mat_ket_noi_backend")
    backend.start()
    page.get_by_test_id("retry-button").click()
    expect(page.get_by_role("cell", name=ticket_code)).to_be_visible()

    # 4. Mở phiếu, xem gợi ý kỹ thuật viên (M2).
    page.get_by_role("row", name=ticket_code).get_by_role("button", name="Phân công").click()
    expect(page).to_have_url(f"{UI_URL}/tickets/{scenario['ticket_id']}/assign")
    first_row = page.locator("table").first.locator("tbody tr").first
    expect(first_row.get_by_role("radio")).to_be_checked()
    technician_code = first_row.locator("td").nth(1).inner_text()
    shot(page, "04_M2_goi_y_ky_thuat_vien")

    # 5. Xác nhận phân công cho người đầu danh sách.
    page.get_by_role("button", name="Xác nhận phân công").click()
    expect(page.get_by_text("ĐÃ PHÂN CÔNG").first).to_be_visible()
    expect(page.locator(".detail-grid").get_by_text(f"{technician_code} ·")).to_be_visible()
    expect(page.get_by_role("status")).to_contain_text(f"Đã phân công phiếu cho kỹ thuật viên {technician_code}")
    shot(page, "05_M2_phan_cong_thanh_cong")
    with _work_connection() as connection:
        status, technician_id, assigned_code = connection.execute(
            """SELECT t.status, t.technician_id, k.technician_code
               FROM ticket t JOIN technician k ON k.technician_id = t.technician_id
               WHERE t.ticket_id = %s""",
            (scenario["ticket_id"],),
        ).fetchone()
    assert (status, assigned_code) == ("DA_PHAN_CONG", technician_code)

    # 6. Đặt lịch giao thiết bị vào khung giờ trống.
    slot = free_slot(technician_id)
    page.get_by_role("button", name="Đặt lịch hẹn").click()
    page.get_by_label("Ngày").fill(slot.strftime("%Y-%m-%d"))
    page.get_by_label("Giờ bắt đầu").fill(slot.strftime("%H:%M"))
    page.get_by_label("Ghi chú").last.fill("Hẹn giao máy sau sửa (E2E)")
    shot(page, "06_M2_dat_lich_hen")
    page.get_by_role("button", name="Lưu lịch hẹn").click()
    expect(page.get_by_role("button", name="Lưu lịch hẹn")).to_be_hidden()
    end = slot + timedelta(minutes=30)
    expect(page.get_by_role("status")).to_contain_text(
        f"Đã đặt lịch GIAO lúc {slot:%H:%M}–{end:%H:%M}"
    )
    shot(page, "06b_M2_dat_lich_thanh_cong")
    with _work_connection() as connection:
        appointment = connection.execute(
            """SELECT appointment_type, status, start_at FROM appointment
               WHERE ticket_id = %s AND technician_id = %s""",
            (scenario["ticket_id"], technician_id),
        ).fetchone()
    assert appointment[:2] == ("GIAO", "DA_HEN")
    assert appointment[2] == slot

    # 7. Kỹ thuật viên đăng nhập, thấy phiếu và lịch hẹn (M3).
    page.get_by_role("button", name="Đăng xuất").click()
    login(page, technician_code)
    expect(page).to_have_url(f"{UI_URL}/my-tickets")
    status_filter = page.get_by_label("Trạng thái")
    status_filter.select_option("DANG_LAM")
    expect(page.get_by_role("button", name=ticket_code)).to_be_visible()
    expect(page.get_by_role("cell", name="TRUNG_BINH", exact=True)).to_have_count(0)
    # From here on, record whether the full-page loading state ever appears (flicker).
    page.evaluate(
        """() => {
            window.__sawLoading = false;
            new MutationObserver(() => {
                if (document.querySelector('[data-testid="state-loading"]')) window.__sawLoading = true;
            }).observe(document.body, { childList: true, subtree: true });
        }"""
    )
    page.get_by_role("button", name=ticket_code).click()
    expect(page.get_by_role("heading", name=ticket_code)).to_be_visible()
    expect(page.get_by_role("cell", name="ĐÃ HẸN")).to_be_visible()
    shot(page, "07_M3_phieu_cua_toi_va_lich_hen")

    # 8. Cập nhật trạng thái DA_PHAN_CONG → DANG_XU_LY → HOAN_TAT.
    page.get_by_label("Ghi chú (tối đa 255 ký tự)").fill("Đã kiểm tra thiết bị")
    page.get_by_role("button", name="Bắt đầu sửa").click()
    page.get_by_role("button", name="Hoàn tất").click()
    expect(page.get_by_role("button", name="Đặt lịch hẹn")).to_be_hidden()
    assert page.evaluate("window.__sawLoading") is False, "M3 nhấp nháy trạng thái Đang tải khi chọn phiếu/đổi trạng thái"
    status_filter.select_option("HOAN_TAT")
    expect(page.get_by_role("row", name=ticket_code)).to_contain_text("HOÀN TẤT")
    shot(page, "08_M3_hoan_tat_phieu")
    with _work_connection() as connection:
        history = connection.execute(
            """SELECT from_status, to_status, note FROM ticket_status_log
               WHERE ticket_id = %s ORDER BY changed_at, log_id""",
            (scenario["ticket_id"],),
        ).fetchall()
        final_status = connection.execute(
            "SELECT status FROM ticket WHERE ticket_id = %s", (scenario["ticket_id"],)
        ).fetchone()[0]
    assert final_status == "HOAN_TAT"
    assert [row[:2] for row in history[-3:]] == [
        ("MOI", "DA_PHAN_CONG"),
        ("DA_PHAN_CONG", "DANG_XU_LY"),
        ("DANG_XU_LY", "HOAN_TAT"),
    ]
    assert history[-2][2] == "Đã kiểm tra thiết bị"

    # 9. KTV vẫn xem được phiếu đã đóng của chính mình, và chỉ của chính mình.
    with _work_connection() as connection:
        own_closed = connection.execute(
            "SELECT count(*) FROM ticket WHERE technician_id = %s AND status = 'DA_DONG'",
            (technician_id,),
        ).fetchone()[0]
    status_filter.select_option("DA_DONG")
    rows = page.locator("table").first.locator("tbody tr")
    expect(rows).to_have_count(own_closed)
    expect(rows.first).to_contain_text("ĐÃ ĐÓNG")
    shot(page, "09_M3_loc_phieu_da_dong_cua_minh", full_page=False)

    # 10. Token hỏng → API trả 401 → xoá token và quay về trang đăng nhập.
    page.evaluate("localStorage.setItem('access_token', 'token-khong-hop-le')")
    page.goto(f"{UI_URL}/my-tickets")
    expect(page).to_have_url(f"{UI_URL}/login")
    assert page.evaluate("localStorage.getItem('access_token')") is None
    shot(page, "10_401_ve_trang_dang_nhap")
