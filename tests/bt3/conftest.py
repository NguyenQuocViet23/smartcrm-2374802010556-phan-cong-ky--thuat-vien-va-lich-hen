"""Harness for the BT3 test cases TC-01…TC-12.

Reuses the Buổi 10 harness in ``tests/real_system.py``: every test gets a fresh
``smartcrm_work_test`` cloned from ``smartcrm_test`` and a real backend on it.
Screenshots are real Playwright captures of Swagger (or the React UI) saved as
``docs/screenshots/TC-xx.png`` (extra parts: ``TC-xx_b.png``, ``TC-xx_c.png``…).

After a run, ``docs/screenshots/bt3-ket-qua-chay.md`` lists, for every test case
that ran, the actual result recorded by the test and PASS/FAIL as pytest saw it.
"""

from __future__ import annotations

import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

import pytest
from playwright.sync_api import Page

from tests import real_system
from tests.conftest import WORK_DATABASE, clone_work_database
from tests.real_system import API_URL, Backend, System, _reachable

ROOT = Path(__file__).resolve().parents[2]
SCREENSHOT_DIR = ROOT / "docs" / "screenshots"
RUN_REPORT = SCREENSHOT_DIR / "bt3-ket-qua-chay.md"

# tc id -> {"name", "facts", "status", "duration", "error"}
RESULTS: dict[str, dict[str, Any]] = {}


def tc_id(item: pytest.Item) -> str:
    marker = item.get_closest_marker("tc")
    return str(marker.args[0]) if marker else item.name


def start_record(item: pytest.Item) -> dict[str, Any]:
    record = {"name": (item.function.__doc__ or "").strip().splitlines()[0], "facts": {}}
    RESULTS[tc_id(item)] = record
    return record["facts"]


def shot(page: Page, name: str, block: Any = None, full_page: bool = True) -> str:
    """Real screenshot into docs/screenshots/<name>.png; returns the repo-relative path."""
    previous = real_system.EVIDENCE_DIR
    real_system.EVIDENCE_DIR = SCREENSHOT_DIR
    try:
        path = real_system.capture(page, name, element=block, full_page=full_page)
    finally:
        real_system.EVIDENCE_DIR = previous
    return path.relative_to(ROOT).as_posix()


@pytest.fixture
def bt3(request: pytest.FixtureRequest, browser) -> System:
    tc = tc_id(request.node)
    real_system.CURRENT_TC["id"] = tc
    if _reachable(f"{API_URL}/db-check"):
        pytest.fail("Cổng 8000 đang có backend khác; hãy tắt nó để test tự chạy backend trên DB làm việc.")
    for old in SCREENSHOT_DIR.glob(f"{tc}.png"):
        old.unlink()
    for old in SCREENSHOT_DIR.glob(f"{tc}_*.png"):
        old.unlink()
    clone_work_database(WORK_DATABASE)
    backend = Backend()
    backend.start()
    handle = System(backend=backend, facts=start_record(request.node))
    yield handle
    if backend.process is not None:
        backend.stop()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[None]):
    outcome = yield
    report = outcome.get_result()
    if item.get_closest_marker("bt3") is None:
        return
    record = RESULTS.setdefault(tc_id(item), {"name": item.name, "facts": {}})
    if report.when == "call" or (report.when == "setup" and report.failed):
        record["status"] = "PASS" if report.passed else "FAIL"
        record["duration"] = round(report.duration, 1)
        if report.failed:
            message = str(call.excinfo.value) if call.excinfo else report.longreprtext
            record["error"] = message.strip().splitlines()[0][:300] if message.strip() else "lỗi"


def _git(*args: str) -> str:
    try:
        return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True,
                              check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "?"


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    ran = {tc: r for tc, r in RESULTS.items() if "status" in r}
    if not ran:
        return
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    previous: dict[str, str] = {}
    if RUN_REPORT.exists():  # keep rows of test cases that did not run this time
        for line in RUN_REPORT.read_text(encoding="utf-8").splitlines():
            if line.startswith("| TC-"):
                previous[line.split("|")[1].strip()] = line
    rows = dict(previous)
    for tc, r in ran.items():
        facts = r["facts"]
        actual = facts.get("actual", "")
        if r["status"] == "FAIL" and r.get("error"):
            actual = f"{actual} · Lỗi assert: {r['error']}".strip(" ·")
        images = ", ".join(f"[{Path(p).name}]({Path(p).name})" for p in facts.get("images", []))
        cell = lambda text: str(text).replace("|", "\\|").replace("\n", " ")
        rows[tc] = (f"| {tc} | {cell(r['name'])} | {cell(facts.get('data', ''))} | {cell(actual)} | "
                    f"**{r['status']}** | {images} | {datetime.now().astimezone():%Y-%m-%d %H:%M} |")
    lines = [
        "# Kết quả chạy thật các test case BT3 (tự sinh)",
        "",
        "Tệp này do `tests/bt3/conftest.py` ghi sau mỗi lần chạy `python -m pytest -m bt3`. "
        "Cột *Thực tế* là giá trị test đọc được từ API/CSDL trong lần chạy đó; PASS/FAIL là kết luận của pytest.",
        "",
        f"- Lần chạy gần nhất: {datetime.now().astimezone():%Y-%m-%d %H:%M:%S %z} · commit `{_git('rev-parse', '--short', 'HEAD')}`"
        f"{' (có thay đổi chưa commit)' if _git('status', '--porcelain', '--', 'src', 'tests') else ''}",
        "",
        "| Mã | Tên | Dữ liệu thử thực tế | Thực tế | Kết quả | Ảnh | Thời điểm |",
        "|---|---|---|---|---|---|---|",
        *[rows[k] for k in sorted(rows)],
        "",
    ]
    RUN_REPORT.write_text("\n".join(lines), encoding="utf-8")
