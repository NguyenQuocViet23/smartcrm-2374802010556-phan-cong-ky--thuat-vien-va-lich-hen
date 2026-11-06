"""Build the whole database in one command; safe to run again (nothing is duplicated).

Steps: create the database if missing → migrate → load catalog → load tickets and
status log → load appointments → create demo accounts (kept if they already exist).

Usage:
    python scripts/setup_all.py                  # database DB_NAME from .env
    python scripts/setup_all.py --with-test-db   # also smartcrm_test, for integration/system tests
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from psycopg import sql

ROOT = Path(__file__).resolve().parents[1]
ACCOUNTS = ROOT / "data" / "processed" / "demo_accounts.json"
LOADERS = ("migrate.py", "load_catalog.py", "load_tickets.py", "load_appointments.py")
TEST_DB = "smartcrm_test"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def connection_settings(dbname: str) -> dict[str, object]:
    settings: dict[str, object] = {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", "5432")),
        "user": os.getenv("DB_USER", "postgres"),
        "dbname": dbname,
    }
    if os.getenv("DB_PASSWORD"):
        settings["password"] = os.environ["DB_PASSWORD"]
    return settings


def ensure_database(name: str) -> None:
    with psycopg.connect(**connection_settings("postgres"), autocommit=True) as connection:
        exists = connection.execute("SELECT 1 FROM pg_database WHERE datname = %s", (name,)).fetchone()
        if exists:
            print(f"Database {name} đã có.")
            return
        connection.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(name)))
        print(f"Đã tạo database {name}.")


def run(script: str, database: str, *args: str) -> None:
    print(f"\n=== {script} → {database} ===", flush=True)
    env = {**os.environ, "DB_NAME": database, "PYTHONIOENCODING": "utf-8"}
    result = subprocess.run([sys.executable, str(ROOT / "scripts" / script), *args], cwd=ROOT, env=env)
    if result.returncode != 0:
        raise SystemExit(f"Dừng: {script} lỗi (mã {result.returncode}).")


def build(database: str) -> None:
    ensure_database(database)
    for script in LOADERS:
        run(script, database)


def main() -> int:
    load_dotenv(ROOT / ".env")
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--with-test-db", action="store_true", help=f"dựng thêm database {TEST_DB}")
    args = parser.parse_args()

    main_db = os.getenv("DB_NAME", "smartcrm")
    build(main_db)
    if ACCOUNTS.exists():
        print(f"\nGiữ tài khoản demo đã có: {ACCOUNTS.relative_to(ROOT).as_posix()}")
    else:
        run("generate_demo_accounts.py", main_db)
    if args.with_test_db:
        build(TEST_DB)
    print("\nHOÀN TẤT: chạy backend và frontend theo README.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
