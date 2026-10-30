"""Shared pytest setup and evidence reporting hooks."""

from __future__ import annotations

from typing import Any

import pytest

from tests.evidence import render_test_evidence, save_summary

RESULTS_KEY = pytest.StashKey[list[dict[str, Any]]]()


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "tc(case_id): identify a Buoi 10 test case")
    config.stash[RESULTS_KEY] = []


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
    if marker is None or not marker.args:
        return

    test_id = str(marker.args[0])
    earlier = getattr(item, "_buoi10_reports", {})
    status = "FAIL" if any(item_report.failed for item_report in earlier.values()) else "PASS"
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
    image = render_test_evidence(
        test_id,
        item.name,
        status,
        duration,
        details,
        failure,
    )
    item.config.stash[RESULTS_KEY].append(
        {
            "id": test_id,
            "title": item.name,
            "type": "pytest",
            "status": status,
            "duration": duration,
            "images": [image.name],
        }
    )


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    results = session.config.stash[RESULTS_KEY]
    if results:
        save_summary(results)
