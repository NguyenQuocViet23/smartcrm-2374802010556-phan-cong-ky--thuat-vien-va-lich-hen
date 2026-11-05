"""Browser screenshots and a Markdown report for pytest runs.

Only real Playwright screenshots are saved as images; no image is drawn
programmatically.
"""

from __future__ import annotations

import os
import platform
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

import pytest

try:
    import playwright
except ImportError:
    playwright = None

ROOT = Path(__file__).resolve().parents[1]
EXPORT_DIR = Path(os.getenv("EXPORT_DIR", ROOT / "export"))
if not EXPORT_DIR.is_absolute():
    EXPORT_DIR = ROOT / EXPORT_DIR
EVIDENCE_DIR = EXPORT_DIR / "test-evidence"
ACTIVE_RUN_DIR: Path | None = None


def slugify(value: str) -> str:
    value = re.sub(r"^test_", "", value.lower())
    value = re.sub(r"[^a-z0-9]+", "_", value.strip("_"), flags=re.ASCII)
    return value.strip("_")[:80] or "test"


def _git_value(*args: str) -> str:
    try:
        return subprocess.run(
            ["git", *args],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "khong-xac-dinh"


def clean_evidence() -> None:
    """Evidence cleanup is deliberately disabled for normal pytest runs."""
    return None


def configure_evidence() -> None:
    global ACTIVE_RUN_DIR, EVIDENCE_DIR
    if os.getenv("EVIDENCE") != "1":
        ACTIVE_RUN_DIR = None
        EVIDENCE_DIR = EXPORT_DIR / "test-evidence"
        return

    run_id = datetime.now().astimezone().strftime("%Y%m%d-%H%M%S")
    ACTIVE_RUN_DIR = EXPORT_DIR / "test-evidence" / f"run-{run_id}"
    ACTIVE_RUN_DIR.mkdir(parents=True, exist_ok=True)
    EVIDENCE_DIR = ACTIVE_RUN_DIR


def screenshot_ui(page: Any, test_id: str, title: str, status: str) -> list[Path]:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    suffix = "_FAIL" if status == "FAIL" else ""
    path = EVIDENCE_DIR / f"{test_id}_{slugify(title)}{suffix}.png"
    page.screenshot(path=str(path), full_page=True)
    return [path]


def capture_ui_notification(page: Any, test_id: str, step: str) -> Path:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    path = EVIDENCE_DIR / f"{test_id}_{slugify(step)}.png"
    page.screenshot(path=str(path), full_page=True)
    return path


def database_counts() -> tuple[str, dict[str, int | str]]:
    database_url = os.getenv("TEST_DATABASE_URL", os.getenv("DATABASE_URL", "Chưa cấu hình"))
    database_name = database_url.rsplit("/", 1)[-1] if "://" in database_url else database_url
    return database_name, {}


def _relative(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def write_report(results: list[dict[str, Any]], session: pytest.Session) -> None:
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    passed = sum(result["status"] == "PASS" for result in results)
    failed = sum(result["status"] == "FAIL" for result in results)
    skipped = sum(result["status"] == "SKIP" for result in results)
    duration = sum(float(result["duration"]) for result in results)
    warnings = []
    seen_ids: dict[str, int] = {}
    for result in results:
        test_id = result["id"]
        seen_ids[test_id] = seen_ids.get(test_id, 0) + 1
        if result.get("missing_marker"):
            warnings.append(f"- `{test_id}` không có marker `@pytest.mark.tc`; mã được lấy tạm từ tên hàm.")
        if not re.fullmatch(r"TC\d{2}", test_id):
            warnings.append(f"- `{test_id}` không theo mẫu mã TCxx.")
        for image in result["images"]:
            if not Path(image).exists():
                warnings.append(f"- Ảnh `{_relative(Path(image))}` bị thiếu.")
    for test_id, count in seen_ids.items():
        if count > 1:
            warnings.append(f"- Mã TC trùng `{test_id}` xuất hiện {count} lần.")

    db_name, counts = database_counts()
    count_lines = ", ".join(f"{table}: {value}" for table, value in counts.items())
    command = "python -m pytest -v"
    terminal_summary = getattr(session.config, "_buoi10_terminal_summary", "")
    lines = [
        "# BÁO CÁO KẾT QUẢ KIỂM THỬ TỰ ĐỘNG",
        "",
        "## 1. Thông tin lần chạy",
        f"- Thời điểm chạy: {datetime.now().astimezone().isoformat(timespec='seconds')}",
        f"- Lệnh chạy: `{command}`",
        f"- Commit hash: `{_git_value('rev-parse', '--short', 'HEAD')}`",
        f"- Nhánh Git: `{_git_value('branch', '--show-current')}`",
        f"- Python: `{platform.python_version()}`",
        f"- pytest: `{pytest.__version__}`",
        f"- Playwright: `{getattr(playwright, '__version__', 'không xác định hoặc chưa cài playwright-python')}`",
        f"- Hệ điều hành: `{platform.platform()}`",
        f"- CSDL dùng: {db_name}",
        f"- Số dòng từng bảng: {count_lines or 'chưa truy vấn được (không cần PostgreSQL cho bộ test hiện tại)'}",
        "- Seed dữ liệu đang dùng: không chạy seed trong lần kiểm thử hiện tại.",
        "",
        "## 2. Tổng hợp",
        f"- Tổng số test: {len(results)}; PASS: {passed}; FAIL: {failed}; bỏ qua: {skipped}; tổng thời gian: {duration:.3f}s.",
    ]
    if terminal_summary:
        lines.append(f"- Dòng kết quả pytest: {terminal_summary}")
    lines.extend([
        "",
        "| Mã | Tên | Loại | Nhóm | Kết quả | Thời gian (s) |",
        "|---|---|---|---|---|---:|",
    ])
    for result in results:
        lines.append(
            f"| {result['id']} | {result['title']} | {result['type']} | {result['group']} | "
            f"{result['status']} | {float(result['duration']):.3f} |"
        )
    lines.extend(["", "## 3. Chi tiết từng test case"])
    for result in results:
        lines.extend([
            "",
            f"### {result['id']} - {result['title']}",
            f"- Hàm test: `{result['nodeid']}`",
            f"- Loại: {result['type']}",
            f"- Truy vết: {result['trace']}",
            f"- Given: {result['given']}",
            f"- When: {result['when']}",
            f"- Then (kỳ vọng): {result['expected']}",
            f"- Dữ liệu thật đã dùng: {result['actual_data']}",
            f"- Kết quả thực tế: {result['actual']}",
            f"- Kết quả: {result['status']}; thời gian: {float(result['duration']):.3f}s",
        ])
        lines.append("- Ảnh:")
        for image in result["images"]:
            image_path = Path(image)
            exists = "tồn tại" if image_path.exists() else "THIẾU"
            lines.append(f"  - `{_relative(image_path)}` — {exists}")
        if result["failure"]:
            lines.append(f"- Lỗi: `{result['failure'].splitlines()[-1] if result['failure'].splitlines() else 'FAIL'}`")
    lines.extend(["", "## 4. Danh sách ảnh trong export/test-evidence/"])
    if EVIDENCE_DIR.exists():
        for image in sorted(EVIDENCE_DIR.glob("*.png")):
            lines.append(f"- `{image.name}` ({image.stat().st_size} bytes)")
    lines.extend(["", "## 5. Cảnh báo và điểm bất thường"])
    lines.extend(warnings or ["- Không có cảnh báo bất thường."])
    lines.extend([
        "",
        "## 6. Cách chạy lại",
        "- Backend: `python -m pytest -v`",
        "- Giao diện: `python -m pytest tests/ui -v -m ui --headed --slowmo 500`",
        "- Tùy thư mục xuất: Windows PowerShell: `$env:EXPORT_DIR=\"export\"` rồi chạy lại pytest.",
        "",
    ])
    (EXPORT_DIR / "testcase.md").write_text("\n".join(lines), encoding="utf-8")
