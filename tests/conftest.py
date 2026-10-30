"""Shared pytest setup and evidence reporting hooks."""

from __future__ import annotations

from typing import Any

import pytest

from tests.evidence import (
    clean_evidence,
    render_test_evidence,
    save_summary,
    screenshot_ui,
    write_report,
)

RESULTS_KEY = pytest.StashKey[list[dict[str, Any]]]()


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "tc(case_id): identify a Buoi 10 test case")
    config.stash[RESULTS_KEY] = []


def pytest_sessionstart(session: pytest.Session) -> None:
    clean_evidence()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[None]):
    outcome = yield
    report = outcome.get_result()
    reports = getattr(item, "_buoi10_reports", {})
    reports[report.when] = report
    setattr(item, "_buoi10_reports", reports)
    if report.when != "teardown":
        return
    marker = item.get_closest_marker("tc")
    missing_marker = marker is None or not marker.args
    test_id = str(marker.args[0]) if not missing_marker else item.function.__name__
    earlier = getattr(item, "_buoi10_reports", {})
    status = (
        "FAIL"
        if any(item_report.failed for item_report in earlier.values())
        else "SKIP"
        if any(item_report.skipped for item_report in earlier.values())
        else "PASS"
    )
    duration = sum(item_report.duration for item_report in earlier.values())
    properties = dict(item.user_properties)
    details = {
        key: str(properties.get(key.lower(), "Chưa được khai báo trong test."))
        for key in ("Given", "When", "Expected", "Actual")
    }
    failure = "\n".join(
        str(item_report.longrepr)
        for item_report in earlier.values()
        if item_report.failed and item_report.longrepr
    ) or None
    raw_docstring = item.function.__doc__ or ""
    first_line = raw_docstring.strip().splitlines()[0].strip() if raw_docstring.strip() else item.name
    title = first_line if first_line and first_line != "test" else item.name
    node_path = item.nodeid
    is_ui = bool(item.get_closest_marker("ui"))
    images = []
    if is_ui:
        page = item.funcargs.get("page")
        if page is not None:
            try:
                images = screenshot_ui(page, test_id, title, status)
            except Exception as error:
                failure = f"{failure}\nKhông thể chụp ảnh UI: {error}" if failure else f"Không thể chụp ảnh UI: {error}"
    else:
        images = [
            render_test_evidence(
                test_id, title, status, duration, details, failure
            )
        ]
    item.config.stash[RESULTS_KEY].append(
        {
            "id": test_id,
            "title": title,
            "type": details["Expected"][:40] if details["Expected"] else "pytest",
            "status": status,
            "duration": duration,
            "images": [str(image) for image in images],
            "group": "ui" if is_ui else "service",
            "function": item.function.__name__,
            "nodeid": node_path,
            "trace": "Chưa khai báo trong docstring hoặc marker.",
            "given": details["Given"],
            "when": details["When"],
            "expected": details["Expected"],
            "actual_data": details["Actual"],
            "actual": details["Actual"],
            "failure": failure,
            "missing_marker": missing_marker,
        }
    )
    print(f"[{test_id}] {status}  {title}  ({duration:.3f}s)")


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    results = session.config.stash[RESULTS_KEY]
    if results:
        save_summary(results)
        write_report(results, session)


def pytest_terminal_summary(terminalreporter: Any, exitstatus: int, config: pytest.Config) -> None:
    results = config.stash[RESULTS_KEY]
    if not results:
        return
    passed = sum(result["status"] == "PASS" for result in results)
    failed = sum(result["status"] == "FAIL" for result in results)
    terminalreporter.write_sep("=", "Bảng tổng kết test case")
    terminalreporter.write_line("Mã | Tên | Kết quả | Thời gian")
    for result in results:
        terminalreporter.write_line(
            f"{result['id']} | {result['title']} | {result['status']} | {result['duration']:.3f}s"
        )
    terminalreporter.write_line(f"{passed}/{passed + failed} test case PASS")
