from __future__ import annotations

import os
from collections.abc import Iterator
from urllib.parse import urlparse

import psycopg
import pytest
from fastapi.testclient import TestClient

from app.core.database import get_engine
from app.core.security import create_access_token
from app.main import app
from tests.conftest import (
    WORK_DATABASE,
    clone_work_database,
    database_counts,
    get_test_database_url,
)


EXPECTED_COUNTS = {
    "service_center": 6,
    "technician": 38,
    "technician_skill": 159,
    "ticket": 7317,
    "ticket_status_log": 35719,
    "appointment": 300,
}


@pytest.fixture(scope="session", autouse=True)
def verify_integration_sources() -> None:
    source_url = get_test_database_url()
    if database_counts(source_url) != EXPECTED_COUNTS:
        raise AssertionError(f"Số dòng smartcrm_test không khớp: {database_counts(source_url)}")
    source = urlparse(source_url)
    smartcrm_url = source._replace(path="/smartcrm").geturl()
    if database_counts(smartcrm_url) != EXPECTED_COUNTS:
        raise AssertionError(f"Số dòng smartcrm không khớp: {database_counts(smartcrm_url)}")


@pytest.fixture
def work_database(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    get_engine().dispose()
    get_engine.cache_clear()
    clone_work_database(WORK_DATABASE)
    source = urlparse(get_test_database_url())
    work_url = source._replace(path=f"/{WORK_DATABASE}", query="").geturl()
    monkeypatch.setenv("DB_NAME", WORK_DATABASE)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    get_engine.cache_clear()
    yield
    get_engine().dispose()
    get_engine.cache_clear()


@pytest.fixture
def work_client(work_database: None, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("SECRET_KEY", os.getenv("SECRET_KEY") or "x" * 32)
    return TestClient(app)


@pytest.fixture
def read_client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("DB_NAME", "smartcrm_test")
    monkeypatch.delenv("DATABASE_URL", raising=False)
    get_engine.cache_clear()
    client = TestClient(app)
    yield client
    get_engine().dispose()
    get_engine.cache_clear()


def work_connection() -> psycopg.Connection:
    url = urlparse(get_test_database_url())._replace(path=f"/{WORK_DATABASE}", query="")
    return psycopg.connect(url.geturl())


@pytest.fixture
def manager_token() -> str:
    with psycopg.connect(get_test_database_url()) as connection:
        center = connection.execute(
            """
            SELECT center_id, center_code, center_name
            FROM service_center
            ORDER BY center_id
            LIMIT 1
            """
        ).fetchone()
    return create_access_token(
        {
            "username": f"QL_{center[1]}",
            "role": "QUAN_LY",
            "center_id": center[0],
            "center_name": center[2],
            "technician_id": None,
            "full_name": "Quản lý trung tâm integration",
            "employee_id": center[0],
        }
    )
