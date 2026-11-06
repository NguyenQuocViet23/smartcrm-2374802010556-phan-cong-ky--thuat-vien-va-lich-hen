"""C5: building the database twice from the committed sample duplicates nothing."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

import psycopg
import pytest
from psycopg import sql

from tests.conftest import database_counts, get_test_database_url
from tests.integration.conftest import EXPECTED_COUNTS

ROOT = Path(__file__).resolve().parents[2]
LOAD_DB = "smartcrm_load_test"  # name ends with _test: never the real database


def _drop(maintenance_url: str) -> None:
    with psycopg.connect(maintenance_url, autocommit=True) as connection:
        connection.execute(sql.SQL("DROP DATABASE IF EXISTS {}").format(sql.Identifier(LOAD_DB)))


@pytest.mark.integration
@pytest.mark.tc("C5")
def test_setup_all_twice_on_sample_keeps_row_counts() -> None:
    """Chạy lại lần hai: setup_all.py trên bộ mẫu hai lần cho cùng số dòng, không nhân đôi"""
    source = urlparse(get_test_database_url())
    maintenance_url = source._replace(path="/postgres", query="").geturl()
    target_url = source._replace(path=f"/{LOAD_DB}", query="").geturl()
    env = {
        **os.environ, "DATA_DIR": "data/sample", "DB_NAME": LOAD_DB, "PYTHONIOENCODING": "utf-8",
        "DB_HOST": source.hostname or "localhost", "DB_PORT": str(source.port or 5432),
        "DB_USER": unquote(source.username or "postgres"), "DB_PASSWORD": unquote(source.password or ""),
    }
    env.pop("DATABASE_URL", None)
    _drop(maintenance_url)
    try:
        counts = []
        for _ in range(2):
            result = subprocess.run(
                [sys.executable, "scripts/setup_all.py"], cwd=ROOT, env=env,
                capture_output=True, text=True, encoding="utf-8",
            )
            assert result.returncode == 0, result.stdout[-2000:] + result.stderr[-2000:]
            counts.append(database_counts(target_url))
        assert counts[0] == counts[1] == EXPECTED_COUNTS["bộ mẫu trong repo (data/sample)"]
        with psycopg.connect(target_url) as connection:
            assert connection.execute("SELECT count(*) FROM ticket WHERE status = 'MOI'").fetchone()[0] == 30
    finally:
        _drop(maintenance_url)
