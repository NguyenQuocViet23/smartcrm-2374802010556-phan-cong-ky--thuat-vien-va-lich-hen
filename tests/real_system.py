"""Shared harness for TC01–TC18: the real frontend, a real backend and real data.

Every test gets a fresh ``smartcrm_work_test`` cloned from ``smartcrm_test`` (the
real case-study data) and a FastAPI backend started on that clone, so scenario
set-up written with SQL never touches ``smartcrm`` or ``smartcrm_test``.

Evidence images are only taken with Playwright ``page.screenshot()`` on the real
UI (Vite) or on Swagger served by the real backend.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import psycopg
import pytest
from dotenv import load_dotenv
from playwright.sync_api import Page, expect

from tests.conftest import WORK_DATABASE, clone_work_database, get_test_database_url

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = ROOT / "docs" / "test-evidence"
UI_URL = os.getenv("UI_BASE_URL", "http://localhost:5173")
API_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
LOCAL_TIME = timezone(timedelta(hours=7))
CATALOG: dict[str, dict[str, Any]] = json.loads(
    (Path(__file__).with_name("tc_catalog.json")).read_text(encoding="utf-8")
)
TABLES = ("service_center", "technician", "technician_skill", "ticket", "ticket_status_log", "appointment")
ACTIVE_STATUSES = ("DA_PHAN_CONG", "DANG_XU_LY", "CHO_LINH_KIEN")

load_dotenv(ROOT / ".env")

# Filled while tests run; read by the report hook in tests/conftest.py.
CAPTURES: list[dict[str, Any]] = []
RUN_INFO: dict[str, Any] = {}
CURRENT_TC: dict[str, str] = {"id": ""}


# --- Services ---------------------------------------------------------------


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
    """A uvicorn process bound to the working database, which a test can stop."""

    def __init__(self) -> None:
        self.process: subprocess.Popen | None = None

    def start(self) -> None:
        env = {**os.environ, "DB_NAME": WORK_DATABASE}
        env.pop("DATABASE_URL", None)
        port = str(urlparse(API_URL).port or 8000)
        self.process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app.main:app",
             "--app-dir", "src/backend", "--port", port],
            cwd=ROOT, env=env,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        _wait_until(lambda: _reachable(f"{API_URL}/db-check"))

    def stop(self) -> None:
        # Once the process has exited its port is closed; no need to probe it again.
        if self.process is not None:
            self.process.terminate()
            self.process.wait(timeout=15)
            self.process = None


def require_frontend_and_free_api_port() -> None:
    if not os.getenv("DEMO_PASSWORD"):
        pytest.fail("Chưa đặt DEMO_PASSWORD trong .env.")
    if not _reachable(UI_URL):
        pytest.fail(f"Frontend chưa chạy tại {UI_URL}: chạy `npm run dev` trong src/frontend.")
    if _reachable(f"{API_URL}/db-check"):
        pytest.fail("Cổng 8000 đang có backend khác; hãy tắt nó để test tự chạy backend trên DB làm việc.")


def work_connection() -> psycopg.Connection:
    url = urlparse(get_test_database_url())._replace(path=f"/{WORK_DATABASE}", query="")
    return psycopg.connect(url.geturl(), autocommit=True)


def source_row_counts() -> dict[str, int]:
    with psycopg.connect(get_test_database_url()) as connection:
        return {t: connection.execute(f"SELECT count(*) FROM {t}").fetchone()[0] for t in TABLES}


@dataclass
class System:
    """Handles of one test run: backend process, database helpers and recorded facts."""

    backend: Backend
    facts: dict[str, Any] = field(default_factory=dict)

    # -- database --
    def db(self) -> psycopg.Connection:
        return work_connection()

    def one(self, sql: str, *params: Any) -> Any:
        with work_connection() as connection:
            return connection.execute(sql, params).fetchone()

    def all(self, sql: str, *params: Any) -> list[tuple]:
        with work_connection() as connection:
            return connection.execute(sql, params).fetchall()

    def run(self, sql: str, *params: Any) -> None:
        with work_connection() as connection:
            connection.execute(sql, params)

    def log_count(self, ticket_id: int) -> int:
        return self.one("SELECT count(*) FROM ticket_status_log WHERE ticket_id = %s", ticket_id)[0]

    def ticket(self, ticket_id: int) -> dict[str, Any]:
        with work_connection() as connection:
            cursor = connection.execute("SELECT * FROM ticket WHERE ticket_id = %s", (ticket_id,))
            names = [c.name for c in cursor.description]
            return dict(zip(names, cursor.fetchone()))

    def technician_code(self, technician_id: int) -> str:
        return self.one("SELECT technician_code FROM technician WHERE technician_id = %s", technician_id)[0]

    def manager_username(self, center_id: int) -> str:
        return "QL_" + self.one("SELECT center_code FROM service_center WHERE center_id = %s", center_id)[0]

    def create_ticket(self, center_id: int, category: str, *, status: str = "MOI",
                      technician_id: int | None = None, priority: str = "CAO",
                      code: str | None = None) -> int:
        """Insert a ticket built from a real customer row (name, phone, serial) of the same center."""
        with work_connection() as connection:
            ticket_id = connection.execute("SELECT max(ticket_id) + 1 FROM ticket").fetchone()[0]
            real = connection.execute(
                """SELECT customer_name, customer_phone, serial_no, issue_desc FROM ticket
                   WHERE center_id = %s AND category_code = %s ORDER BY ticket_id LIMIT 1""",
                (center_id, category),
            ).fetchone()
            code = code or f"TEST-{ticket_id}"
            connection.execute(
                """INSERT INTO ticket (ticket_id, ticket_code, center_id, customer_name, customer_phone,
                       serial_no, issue_desc, category_code, priority, status, technician_id,
                       received_at, due_date)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, now(), now() + interval '3 days')""",
                (ticket_id, code, center_id, *real, category, priority, status, technician_id),
            )
            connection.execute(
                """INSERT INTO ticket_status_log (ticket_id, event_type, from_status, to_status,
                       to_technician_id, changed_by, note)
                   VALUES (%s, 'TRANG_THAI', NULL, %s, %s, 1, 'Dựng kịch bản kiểm thử')""",
                (ticket_id, status, technician_id),
            )
        return ticket_id

    def set_skill(self, technician_id: int, category: str, proficiency: int) -> None:
        self.run(
            """INSERT INTO technician_skill (technician_id, category_code, proficiency) VALUES (%s, %s, %s)
               ON CONFLICT (technician_id, category_code) DO UPDATE SET proficiency = EXCLUDED.proficiency""",
            technician_id, category, proficiency,
        )

    def free_working_day(self, technician_ids: list[int], start: str = "09:00", minutes: int = 60) -> date:
        """First Monday–Saturday at least 30 days ahead where the technicians are free around ``start``."""
        day = date.today() + timedelta(days=30)
        while True:
            if day.weekday() != 6:
                begin = at(day, start)
                busy = self.one(
                    """SELECT count(*) FROM appointment WHERE technician_id = ANY(%s) AND status = 'DA_HEN'
                         AND start_at < %s AND %s < end_at""",
                    technician_ids, begin + timedelta(minutes=minutes), begin,
                )[0]
                if not busy:
                    return day
            day += timedelta(days=1)


def at(day: date, hhmm: str) -> datetime:
    hours, minutes = map(int, hhmm.split(":"))
    return datetime(day.year, day.month, day.day, hours, minutes, tzinfo=LOCAL_TIME)


# --- HTTP API ---------------------------------------------------------------


def api(method: str, path: str, token: str | None = None, body: Any = None) -> tuple[int, Any]:
    data = json.dumps(body).encode() if body is not None else None
    request = urllib.request.Request(f"{API_URL}{path}", data=data, method=method)
    request.add_header("Content-Type", "application/json")
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(request) as response:
            raw = response.read()
            return response.status, json.loads(raw) if raw else None
    except urllib.error.HTTPError as error:
        raw = error.read()
        return error.code, json.loads(raw) if raw else None


def token_for(username: str) -> str:
    status, body = api("POST", "/api/auth/login", body={"username": username, "password": os.environ["DEMO_PASSWORD"]})
    assert status == 200, f"Đăng nhập {username} thất bại: {status} {body}"
    return body["access_token"]


# --- Browser ----------------------------------------------------------------


def ui_login(page: Page, username: str, password: str | None = None) -> None:
    page.goto(f"{UI_URL}/login")
    page.get_by_label("Tên đăng nhập").fill(username)
    page.get_by_label("Mật khẩu").fill(password if password is not None else os.environ["DEMO_PASSWORD"])
    page.get_by_role("button", name="Đăng nhập").click()


def suggestion_rows(page: Page) -> list[tuple[str, int, int]]:
    """(technician_code, proficiency, workload) of every row in the M2 suggestion table."""
    rows = page.locator("table").first.locator("tbody tr")
    return [
        (row.locator("td").nth(1).inner_text(), int(row.locator("td").nth(4).inner_text()),
         int(row.locator("td").nth(5).inner_text()))
        for row in rows.all()
    ]


def open_assign_page(page: Page, manager: str, ticket_id: int) -> None:
    ui_login(page, manager)
    expect(page).to_have_url(f"{UI_URL}/tickets")
    page.goto(f"{UI_URL}/tickets/{ticket_id}/assign")
    expect(page.get_by_role("heading", name="Gợi ý kỹ thuật viên")).to_be_visible()


def capture(page: Page, name: str, *, wait_idle: bool = True, full_page: bool = True,
            element=None) -> Path:
    """Screenshot the real page (or one element of it, e.g. a Swagger operation).

    Refuses anything that is not the system's own UI or API.
    """
    url = page.url
    if not (url.startswith(UI_URL) or url.startswith(API_URL)):
        raise AssertionError(f"Từ chối chụp ảnh ngoài hệ thống: {url}")
    if wait_idle:
        page.wait_for_load_state("networkidle")
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    path = EVIDENCE_DIR / f"{name}.png"
    if element is not None:
        # Swagger: from the top of the operation to the end of the real server response.
        live = element.locator(".live-responses-table").first
        element.scroll_into_view_if_needed()
        top = element.bounding_box()
        bottom = live.bounding_box() if live.count() else top
        scroll_y = page.evaluate("window.scrollY")
        clip = {"x": top["x"], "y": top["y"] + scroll_y, "width": top["width"],
                "height": bottom["y"] + bottom["height"] - top["y"] + 8}
        page.screenshot(path=str(path), full_page=True, clip=clip)
        size = f"{round(clip['width'])}×{round(clip['height'])} (khối thao tác Swagger)"
    else:
        page.screenshot(path=str(path), full_page=full_page)
        width, height = page.evaluate("[document.documentElement.scrollWidth, document.documentElement.scrollHeight]")
        size = f"{width}×{height if full_page else page.viewport_size['height']}"
    CAPTURES.append({
        "tc": CURRENT_TC["id"], "file": path.name, "url": url, "title": page.title(),
        "time": datetime.now().astimezone().isoformat(timespec="seconds"), "size": size,
    })
    return path


def clear_old_images(tc: str) -> None:
    """Remove only this test case's previous images before it runs again."""
    if EVIDENCE_DIR.exists():
        for old in EVIDENCE_DIR.glob(f"{tc}_*.png"):
            old.unlink()


# --- Swagger ----------------------------------------------------------------


def swagger_authorize(page: Page, token: str) -> None:
    page.goto(f"{API_URL}/docs")
    page.locator(".scheme-container").get_by_role("button", name=re.compile("Authorize")).click()
    dialog = page.locator(".dialog-ux .modal-ux")
    dialog.locator("#auth-bearer-value").fill(token)
    dialog.locator("button.modal-btn.authorize").click()
    dialog.locator("button.modal-btn.btn-done").click()
    expect(dialog).to_be_hidden()


def swagger_execute(page: Page, method: str, path: str, params: dict[str, Any] | None = None,
                    body: Any = None) -> tuple[int, Any, Any]:
    """Run one operation with Try it out → Execute; return HTTP status, JSON body and the block."""
    block = page.locator(f".opblock-{method.lower()}").filter(
        has=page.locator(".opblock-summary-path", has_text=re.compile(f"^{re.escape(path)}$"))
    ).first
    if not block.locator(".opblock-body").is_visible():
        block.locator(".opblock-summary").first.click()
    toggle = block.locator("button.try-out__btn").first  # "Try it out", or "Cancel" + "Reset" once enabled
    toggle.wait_for()
    if toggle.inner_text().strip() == "Try it out":
        toggle.click()
    expect(block.get_by_role("button", name="Execute")).to_be_visible()
    for name, value in (params or {}).items():
        block.locator(f'tr[data-param-name="{name}"] input').fill(str(value))
    if body is not None:
        block.locator("textarea.body-param__text").fill(json.dumps(body, ensure_ascii=False, indent=2))
    pattern = re.compile(re.escape(API_URL) + re.sub(r"\\\{[a-z_]+\\\}", r"[^/?]+", re.escape(path)) + r"(\?.*)?$")
    with page.expect_response(lambda r: r.request.method == method.upper() and pattern.match(r.url)) as info:
        block.get_by_role("button", name="Execute").click()
    response = info.value
    expect(block.locator(".live-responses-table .response-col_status").first).to_be_visible()
    block.scroll_into_view_if_needed()
    try:
        payload = response.json()
    except Exception:
        payload = None
    return response.status, payload, block


# --- Fixtures ---------------------------------------------------------------


@pytest.fixture
def system(request: pytest.FixtureRequest, browser) -> System:
    marker = request.node.get_closest_marker("tc")
    tc = str(marker.args[0]) if marker else request.node.name
    CURRENT_TC["id"] = tc
    if not RUN_INFO:
        RUN_INFO.update({
            "browser": f"{browser.browser_type.name} {browser.version}",
            "source_counts": source_row_counts(),
        })
    require_frontend_and_free_api_port()
    clear_old_images(tc)
    clone_work_database(WORK_DATABASE)
    backend = Backend()
    backend.start()
    handle = System(backend=backend)
    request.node.user_properties.append(("system_facts", handle.facts))
    yield handle
    if backend.process is not None:
        backend.stop()
