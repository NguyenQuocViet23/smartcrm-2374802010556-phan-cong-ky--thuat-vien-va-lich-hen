"""Shared pytest setup and evidence reporting hooks."""

from __future__ import annotations

import os
import re
import sys
from contextlib import contextmanager
from typing import Any
from urllib.parse import unquote, urlparse

import pytest
import psycopg

from tests.evidence import (
    EVIDENCE_DIR,
    clean_evidence,
    configure_evidence,
    screenshot_ui,
    write_report,
)

RESULTS_KEY = pytest.StashKey[list[dict[str, Any]]]()
SYSTEM_RESULTS_KEY = pytest.StashKey[list[dict[str, Any]]]()


def database_name_from_url(database_url: str) -> str:
    parsed = urlparse(database_url)
    if parsed.scheme and parsed.hostname is not None:
        return unquote(parsed.path.lstrip("/")).split("?", 1)[0]
    match = re.search(r"(?:^|[/?])([^/?]+)$", database_url)
    return unquote(match.group(1) if match else database_url)


def validate_test_database(database_url: str) -> str:
    database_name = database_name_from_url(database_url)
    if not database_name.endswith("_test"):
        raise RuntimeError("Từ chối chạy: tên database phải kết thúc bằng _test")
    return database_name


def get_test_database_url() -> str:
    configured_url = os.getenv("TEST_DATABASE_URL")
    if configured_url:
        validate_test_database(configured_url)
        return configured_url

    database_name = os.getenv("TEST_DB_NAME")
    if database_name:
        validate_test_database(database_name)
        host = os.getenv("DB_HOST", "localhost")
        port = os.getenv("DB_PORT", "5432")
        user = os.getenv("DB_USER", "postgres")
        password = os.getenv("DB_PASSWORD")
        auth = user + (f":{password}" if password else "")
        return f"postgresql://{auth}@{host}:{port}/{database_name}"

    raise RuntimeError("Từ chối chạy: chưa cấu hình TEST_DATABASE_URL hoặc TEST_DB_NAME")


WORK_DATABASE = "smartcrm_work_test"


def clone_work_database(database_name: str) -> None:
    if database_name != WORK_DATABASE:
        raise RuntimeError("Chỉ được tạo database làm việc cố định smartcrm_work_test.")

    from app.core.database import get_engine

    try:
        get_engine().dispose()
    except Exception:
        pass
    get_engine.cache_clear()
    source_url = get_test_database_url()
    source = urlparse(source_url)
    maintenance_url = source._replace(path="/postgres", query="").geturl()
    with psycopg.connect(maintenance_url, autocommit=True) as connection:
        try:
            connection.execute("DROP DATABASE IF EXISTS smartcrm_work_test")
            connection.execute(
                "CREATE DATABASE smartcrm_work_test TEMPLATE smartcrm_test"
            )
        except psycopg.OperationalError as error:
            if "being accessed by other users" in str(error).lower():
                raise RuntimeError(
                    "Không thể tạo smartcrm_work_test từ template: đóng tab Query Tool và Disconnect database smartcrm_test, rồi chạy lại."
                ) from error
            raise


def database_counts(database_url: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    with psycopg.connect(database_url) as connection:
        for table in (
            "service_center",
            "technician",
            "technician_skill",
            "ticket",
            "ticket_status_log",
            "appointment",
        ):
            counts[table] = connection.execute(
                f"SELECT count(*) FROM {table}"
            ).fetchone()[0]
    return counts


@pytest.fixture
def test_database_url() -> str:
    return get_test_database_url()


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "tc(case_id): identify a Buoi 10 test case")
    config.stash[RESULTS_KEY] = []
    config.stash[SYSTEM_RESULTS_KEY] = []


def pytest_sessionstart(session: pytest.Session) -> None:
    configure_evidence()
    clean_evidence()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[None]):
    outcome = yield
    report = outcome.get_result()
    reports = getattr(item, "_buoi10_reports", {})
    reports[report.when] = report
    setattr(item, "_buoi10_reports", reports)
    is_system = item.get_closest_marker("system") is not None
    if is_system and report.when == "call" and report.failed:
        from tests.system_report import capture_failure

        capture_failure(item)
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
    evidence_enabled = os.getenv("EVIDENCE") == "1"
    if evidence_enabled and is_ui:
        page = item.funcargs.get("page")
        if page is not None:
            try:
                images = screenshot_ui(page, test_id, title, status)
                images = [
                    *sorted(EVIDENCE_DIR.glob(f"{test_id}_*.png")),
                    *images,
                ]
            except Exception as error:
                failure = f"{failure}\nKhông thể chụp ảnh UI: {error}" if failure else f"Không thể chụp ảnh UI: {error}"
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
    if is_system:
        from tests.system_report import record_result

        item.config.stash[SYSTEM_RESULTS_KEY].append(record_result(item, status, duration, failure))
    _echo(f"[{test_id}] {status}  {title}  ({duration:.3f}s)")


def _echo(line: str) -> None:
    """Print a Vietnamese test title even when stdout is not UTF-8 (e.g. cp1252 pipes)."""
    encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
    print(line.encode(encoding, errors="replace").decode(encoding))


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    results = session.config.stash[RESULTS_KEY]
    if os.getenv("EVIDENCE") == "1" and results:
        write_report(results, session)
    system_results = session.config.stash[SYSTEM_RESULTS_KEY]
    if system_results:
        from tests.system_report import write_testcase_report

        passed = sum(r["status"] == "PASS" for r in system_results)
        failed = sum(r["status"] == "FAIL" for r in system_results)
        seconds = sum(r["duration"] for r in system_results)
        summary = f"{passed} passed" + (f", {failed} failed" if failed else "") + f" in {seconds:.2f}s"
        path = write_testcase_report(system_results, session, summary)
        _echo(f"Đã ghi báo cáo {path.relative_to(path.parents[2])}")


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
