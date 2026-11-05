"""Generate demo login accounts from the current PostgreSQL data."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import psycopg
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src" / "backend"))

from app.core.security import make_password_hash

OUTPUT_PATH = ROOT / "data" / "processed" / "demo_accounts.json"


def database_settings() -> dict[str, object]:
    required = ("DB_HOST", "DB_NAME", "DB_USER")
    missing = [name for name in required if not os.getenv(name, "").strip()]
    if missing:
        raise RuntimeError(
            "Thiếu cấu hình cơ sở dữ liệu: " + ", ".join(missing)
        )

    settings: dict[str, object] = {
        "host": os.environ["DB_HOST"],
        "dbname": os.environ["DB_NAME"],
        "user": os.environ["DB_USER"],
        "port": int(os.getenv("DB_PORT", "5432")),
    }
    if os.getenv("DB_PASSWORD"):
        settings["password"] = os.environ["DB_PASSWORD"]
    return settings


def generate_accounts() -> dict[str, list[dict[str, object]]]:
    password = os.getenv("DEMO_PASSWORD", "")
    if not password:
        raise RuntimeError(
            "Thiếu DEMO_PASSWORD trong .env; không thể tạo tài khoản demo."
        )

    with psycopg.connect(**database_settings()) as connection:
        centers = list(
            connection.execute(
                """
                SELECT center_id, center_code, center_name
                FROM service_center
                ORDER BY center_id
                """
            )
        )
        technicians = list(
            connection.execute(
                """
                SELECT technician_id, technician_code, full_name, center_id, is_active
                FROM technician
                WHERE is_active = TRUE
                ORDER BY technician_id
                """
            )
        )

    center_by_id = {row[0]: row for row in centers}
    accounts: list[dict[str, object]] = []
    for center_id, center_code, center_name in centers:
        accounts.append(
            {
                "username": f"QL_{center_code}",
                "role": "QUAN_LY",
                "center_id": center_id,
                "center_name": center_name,
                "technician_id": None,
                "full_name": f"Quản lý {center_name}",
                "employee_id": center_id,
                "password_hash": make_password_hash(password),
            }
        )
    for technician_id, technician_code, full_name, center_id, _ in technicians:
        accounts.append(
            {
                "username": technician_code,
                "role": "KY_THUAT_VIEN",
                "center_id": center_id,
                "center_name": center_by_id[center_id][2],
                "technician_id": technician_id,
                "full_name": full_name,
                "employee_id": technician_id,
                "password_hash": make_password_hash(password),
            }
        )
    return {"accounts": accounts}


def main() -> int:
    load_dotenv(ROOT / ".env")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="ghi đè account demo hiện có")
    args = parser.parse_args()

    if OUTPUT_PATH.exists() and not args.force:
        raise RuntimeError(
            f"Từ chối ghi đè {OUTPUT_PATH}; dùng --force nếu thật sự muốn thay thế."
        )

    payload = generate_accounts()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    usernames = [account["username"] for account in payload["accounts"]]
    print(f"Đã tạo {len(usernames)} tài khoản.")
    print("Username: " + ", ".join(usernames))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
