"""Write docs/test-evidence/testcase.md from facts collected while TC01–TC18 ran.

Only observed values are written; nothing is adjusted to match the Word report.
"""

from __future__ import annotations

import platform
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import pytest

from tests.real_system import API_URL, CAPTURES, CATALOG, EVIDENCE_DIR, ROOT, RUN_INFO, UI_URL

ALLOWED_PREFIXES = (UI_URL, API_URL)


def _git(*args: str) -> str:
    try:
        return subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True, text=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "không xác định"


def _channel(tc: str) -> str:
    files = {c["file"]: c["url"] for c in CAPTURES if c["tc"] == tc}
    kinds = {"Swagger" if url.startswith(API_URL) else "UI React" for url in files.values()}
    return " + ".join(sorted(kinds)) or "—"


def _lines(values: list[str]) -> str:
    return " / ".join(values)


def write_testcase_report(results: list[dict[str, Any]], session: pytest.Session, summary_line: str) -> Path:
    from importlib.metadata import version

    results = sorted(results, key=lambda r: r["tc"])

    playwright_version = version("playwright")

    passed = sum(r["status"] == "PASS" for r in results)
    failed = sum(r["status"] == "FAIL" for r in results)
    skipped = sum(r["status"] == "SKIP" for r in results)
    total_time = sum(r["duration"] for r in results)
    counts = RUN_INFO.get("source_counts", {})
    args = " ".join(session.config.invocation_params.args) or "(mặc định)"

    out = [
        "# BÁO CÁO KẾT QUẢ KIỂM THỬ TỰ ĐỘNG",
        "",
        "## 1. Thông tin lần chạy",
        f"- Thời điểm: {datetime.now().astimezone().isoformat(timespec='seconds')}",
        f"- Lệnh chạy: `python -m pytest {args}`",
        f"- Commit hash: `{_git('rev-parse', '--short', 'HEAD')}` (nhánh `{_git('branch', '--show-current')}`)",
        f"- Hệ điều hành: {platform.platform()}",
        f"- Python {platform.python_version()} · pytest {pytest.__version__} · Playwright {playwright_version}",
        f"- Trình duyệt: {RUN_INFO.get('browser', 'không xác định')}",
        f"- UI_BASE_URL: {UI_URL} · API_BASE_URL: {API_URL}",
        "- CSDL: mỗi test chạy trên `smartcrm_work_test`, tạo lại từ `smartcrm_test` (dữ liệu thật) trước test; "
        "backend được khởi động lại trên bản sao đó.",
        "- Số dòng 6 bảng của `smartcrm_test` lúc chạy: "
        + (", ".join(f"{t} {n:,}".replace(",", ".") for t, n in counts.items()) or "chưa đọc được"),
        "- Seed dữ liệu: phiếu MOI seed 20260901; lịch hẹn seed 20261102.",
        "",
        "## 2. Tổng hợp",
        f"- Tổng số test: {len(results)}; PASS: {passed}; FAIL: {failed}; bỏ qua: {skipped}; "
        f"tổng thời gian: {total_time:.1f}s",
        f"- Dòng cuối của pytest: `{summary_line}`" if summary_line else "- Dòng cuối của pytest: (xem terminal)",
        "",
        "| Mã | Tên | Loại | Truy vết | Kênh | Kết quả | Thời gian (s) |",
        "|---|---|---|---|---|---|---:|",
    ]
    for r in results:
        c = CATALOG.get(r["tc"], {})
        out.append(f"| {r['tc']} | {c.get('name', r['name'])} | {c.get('type', '')} | {c.get('trace', '')} | "
                   f"{_channel(r['tc'])} | {r['status']} | {r['duration']:.2f} |")

    out += ["", "## 3. Chi tiết từng test case"]
    for r in results:
        c = CATALOG.get(r["tc"], {})
        facts = r.get("facts") or {}
        out += [
            "",
            f"### {r['tc']} – {c.get('name', r['name'])}",
            f"- Loại: {c.get('type', '')} | Truy vết: {c.get('trace', '')} | Hàm test: `{r['nodeid']}`",
            f"- Given: {_lines(c.get('given', []))}",
            f"- When: {_lines(c.get('when', []))}",
            f"- Then (kỳ vọng): {_lines(c.get('then', []))}",
            f"- Dữ liệu thật dùng: {facts.get('data', 'chưa ghi nhận')}",
            f"- Kết quả thực tế: {facts.get('actual', 'chưa ghi nhận')} (thời gian chạy {r['duration']:.2f}s)",
            f"- Trạng thái: {r['status']}",
            "- Ảnh:",
        ]
        shots = [s for s in CAPTURES if s["tc"] == r["tc"]]
        for s in shots:
            exists = "tồn tại" if (EVIDENCE_DIR / s["file"]).exists() else "THIẾU"
            out.append(f"  - {s['file']} | {s['url']} | {s['title']} | {s['time']} | {s['size']} | {exists}")
        if not shots:
            out.append("  - (không có ảnh)")
        if r.get("failure"):
            out.append(f"- Lỗi: `{r['failure'].strip().splitlines()[-1]}`")

    out += ["", "## 4. Danh sách ảnh trong docs/test-evidence/"]
    for image in sorted(EVIDENCE_DIR.glob("TC*.png")):
        out.append(f"- {image.name} ({image.stat().st_size:,} bytes)".replace(",", "."))

    warnings: list[str] = []
    if len(results) != 18:
        warnings.append(f"- Số test chạy là {len(results)}, khác 18.")
    ids = [r["tc"] for r in results]
    for tc in sorted(set(ids)):
        if ids.count(tc) > 1:
            warnings.append(f"- Mã TC trùng: {tc}.")
    for r in results:
        if not re.fullmatch(r"TC\d\d", r["tc"]):
            warnings.append(f"- `{r['nodeid']}` thiếu marker `@pytest.mark.tc(\"TCxx\")`.")
        if r["status"] == "SKIP":
            warnings.append(f"- {r['tc']} bị bỏ qua.")
        produced = {s["file"] for s in CAPTURES if s["tc"] == r["tc"]}
        for expected in CATALOG.get(r["tc"], {}).get("images", []):
            if expected not in produced:
                warnings.append(f"- {r['tc']}: thiếu ảnh {expected}.")
        for name in produced:
            if not name.startswith(r["tc"] + "_"):
                warnings.append(f"- {r['tc']}: tên ảnh sai mẫu {name}.")
    for s in CAPTURES:
        if not s["url"].startswith(ALLOWED_PREFIXES):
            warnings.append(f"- Ảnh {s['file']} có URL ngoài hệ thống: {s['url']}.")
    out += ["", "## 5. Cảnh báo và điểm bất thường"] + (warnings or ["- Không có."])

    out += [
        "",
        "## 6. Cách chạy lại",
        "1. PostgreSQL có `smartcrm_test` đã nạp dữ liệu thật (README mục 3).",
        "2. Chạy frontend: `cd src/frontend` rồi `npm run dev`; để trống cổng 8000 (test tự chạy backend).",
        "3. Windows PowerShell: `$env:TEST_DB_NAME = \"smartcrm_test\"` rồi `python -m pytest -m system`.",
        "4. Thêm `--headed --slowmo 300` để xem trình duyệt chạy.",
        "",
    ]
    path = EVIDENCE_DIR / "testcase.md"
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(out), encoding="utf-8")
    return path


def record_result(item: pytest.Item, status: str, duration: float, failure: str | None) -> dict[str, Any]:
    marker = item.get_closest_marker("tc")
    tc = str(marker.args[0]) if marker else item.name
    facts = next((value for key, value in item.user_properties if key == "system_facts"), {})
    return {
        "tc": tc, "name": item.name, "nodeid": item.nodeid, "status": status,
        "duration": duration, "failure": failure, "facts": facts,
    }


def capture_failure(item: pytest.Item) -> None:
    """Screenshot the page of a failed system test with the _FAIL suffix."""
    page = item.funcargs.get("page")
    marker = item.get_closest_marker("tc")
    if page is None or marker is None:
        return
    tc = str(marker.args[0])
    images = CATALOG.get(tc, {}).get("images") or [f"{tc}.png"]
    name = Path(images[0]).stem + "_FAIL"
    try:
        EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(EVIDENCE_DIR / f"{name}.png"), full_page=True)
        CAPTURES.append({"tc": tc, "file": f"{name}.png", "url": page.url, "title": page.title(),
                         "time": datetime.now().astimezone().isoformat(timespec="seconds"), "size": "—"})
    except Exception as error:  # the page may already be closed
        print(f"Không chụp được ảnh _FAIL cho {tc}: {error}", file=sys.stderr)
