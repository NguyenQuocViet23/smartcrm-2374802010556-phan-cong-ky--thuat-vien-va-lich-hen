"""Load the L04 case-study CSVs into PostgreSQL without duplicate rows."""

from __future__ import annotations

import argparse
import csv
import hashlib
import hmac
import json
import os
import re
import secrets
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from sqlalchemy import URL, create_engine, make_url, text

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SEED = 20261023
TIMEZONE = timezone(timedelta(hours=7))
ALLOWED_CATEGORIES = {
    "MAN_HINH",
    "PIN",
    "SAC",
    "PHAN_MEM",
    "NUOC_VAO",
    "KHAC",
}
ALLOWED_PRIORITIES = {"CAO", "TRUNG_BINH", "THAP"}
ALLOWED_STATUSES = {
    "MOI",
    "DA_PHAN_CONG",
    "DANG_XU_LY",
    "CHO_LINH_KIEN",
    "HOAN_TAT",
    "DA_DONG",
    "DA_HUY",
}
STATUS_ALIASES = {
    "ĐÃ_ĐÓNG": "DA_DONG",
    "ĐANG_XỬ_LÝ": "DANG_XU_LY",
    "CHỜ_LINH_KIỆN": "CHO_LINH_KIEN",
    "HOÀN_TẤT": "HOAN_TAT",
    "ĐÃ_PHÂN_CÔNG": "DA_PHAN_CONG",
}


class SeedError(RuntimeError):
    """Raised when a source file cannot safely be loaded."""


def normalize_phone(value: str | None) -> str | None:
    """Normalize local or +84-format phone numbers to a valid 10-digit value."""
    digits = re.sub(r"\D", "", value or "")
    if digits.startswith("84"):
        digits = "0" + digits[2:]
    if len(digits) == 10 and digits.startswith("0"):
        return digits
    return None


def normalize_status(value: str) -> str:
    """Accept source labels with accents and already-normalized database codes."""
    status = value.strip().upper()
    mapped = STATUS_ALIASES.get(status, status)
    if mapped not in ALLOWED_STATUSES:
        raise ValueError(f"Unsupported ticket status: {value!r}")
    return mapped


def parse_datetime(value: str) -> datetime:
    """Parse source timestamps and assign the case-study +07:00 timezone."""
    parsed = datetime.fromisoformat(value.strip())
    return parsed.replace(tzinfo=TIMEZONE) if parsed.tzinfo is None else parsed


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    if not path.is_file():
        raise SeedError(f"Required source file is missing: {path}")
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames:
            raise SeedError(f"CSV has no header: {path}")
        return reader.fieldnames, list(reader)


def make_password_hash(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("ascii"), 310_000
    ).hex()
    return f"pbkdf2_sha256$310000${salt}${digest}"


def database_url(args: argparse.Namespace) -> URL | str:
    if args.db_url:
        url = make_url(args.db_url)
        if url.drivername in {"postgres", "postgresql"}:
            return url.set(drivername="postgresql+psycopg")
        return url
    if os.getenv("DATABASE_URL"):
        url = make_url(os.environ["DATABASE_URL"])
        if url.drivername in {"postgres", "postgresql"}:
            return url.set(drivername="postgresql+psycopg")
        return url
    return URL.create(
        "postgresql+psycopg",
        username=os.getenv("DB_USER") or None,
        password=os.getenv("DB_PASSWORD") or None,
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NAME", "smartcrm"),
    )


def _required(row: dict[str, str], key: str, filename: str) -> str:
    value = (row.get(key) or "").strip()
    if not value:
        raise SeedError(f"{filename} has an empty required field: {key}")
    return value


def _upsert_catalog(connection: Any, centers: list[dict[str, str]],
                    categories: list[dict[str, str]],
                    technicians: list[dict[str, str]],
                    skills: list[dict[str, str]]) -> None:
    for row in centers:
        connection.execute(
            text(
                """INSERT INTO service_center
                   (center_id, center_code, center_name, city)
                   VALUES (:center_id, :center_code, :center_name, :city)
                   ON CONFLICT (center_id) DO UPDATE SET
                     center_code = EXCLUDED.center_code,
                     center_name = EXCLUDED.center_name,
                     city = EXCLUDED.city"""
            ),
            {
                "center_id": int(row["center_id"]),
                "center_code": _required(row, "center_code", "service_centers.csv"),
                "center_name": _required(row, "center_name", "service_centers.csv"),
                "city": _required(row, "thanh_pho", "service_centers.csv"),
            },
        )

    category_codes: dict[str, str] = {}
    for row in categories:
        category_id = _required(row, "category_id", "issue_categories.csv")
        code = _required(row, "category_name", "issue_categories.csv").upper()
        if code not in ALLOWED_CATEGORIES:
            raise SeedError(f"Unsupported category_code in issue_categories.csv: {code}")
        category_codes[category_id] = code

    for row in technicians:
        connection.execute(
            text(
                """INSERT INTO technician
                   (technician_id, technician_code, full_name, center_id, level, is_active)
                   VALUES (:technician_id, :technician_code, :full_name, :center_id,
                           :level, :is_active)
                   ON CONFLICT (technician_id) DO UPDATE SET
                     technician_code = EXCLUDED.technician_code,
                     full_name = EXCLUDED.full_name,
                     center_id = EXCLUDED.center_id,
                     level = EXCLUDED.level,
                     is_active = EXCLUDED.is_active"""
            ),
            {
                "technician_id": int(row["technician_id"]),
                "technician_code": _required(row, "technician_code", "technicians.csv"),
                "full_name": _required(row, "ho_ten", "technicians.csv"),
                "center_id": int(row["center_id"]),
                "level": _required(row, "level", "technicians.csv").upper(),
                "is_active": row["is_active"].strip().lower() in {"true", "1", "yes"},
            },
        )

    for row in skills:
        category_id = _required(row, "category_id", "technician_skills.csv")
        if category_id not in category_codes:
            raise SeedError(f"Unknown category_id in technician_skills.csv: {category_id}")
        connection.execute(
            text(
                """INSERT INTO technician_skill (technician_id, category_code, proficiency)
                   VALUES (:technician_id, :category_code, :proficiency)
                   ON CONFLICT (technician_id, category_code) DO UPDATE SET
                     proficiency = EXCLUDED.proficiency"""
            ),
            {
                "technician_id": int(row["technician_id"]),
                "category_code": category_codes[category_id],
                "proficiency": int(row["proficiency"]),
            },
        )


def _load_tickets(
    connection: Any,
    ticket_rows: list[dict[str, str]],
    customers: dict[str, dict[str, str]],
    categories: dict[str, str],
) -> tuple[int, list[dict[str, str]]]:
    rejects: list[dict[str, str]] = []
    loaded = 0
    for row in ticket_rows:
        customer = customers.get((row.get("customer_id") or "").strip())
        if customer is None:
            rejects.append({**row, "reject_reason": "customer_id không khớp record_id"})
            continue
        phone = normalize_phone(customer.get("so_dien_thoai"))
        if phone is None:
            rejects.append({**row, "reject_reason": "Số điện thoại khách hàng không hợp lệ"})
            continue

        category_id = _required(row, "category_id", "tickets_history.csv")
        category_code = categories.get(category_id)
        if category_code is None:
            rejects.append({**row, "reject_reason": f"category_id không hợp lệ: {category_id}"})
            continue
        status = normalize_status(_required(row, "status", "tickets_history.csv"))
        priority = _required(row, "priority", "tickets_history.csv").upper()
        if priority == "TRUNG_BÌNH":
            priority = "TRUNG_BINH"
        if priority not in ALLOWED_PRIORITIES:
            rejects.append({**row, "reject_reason": f"priority không hợp lệ: {priority}"})
            continue

        connection.execute(
            text(
                """INSERT INTO ticket
                   (ticket_id, ticket_code, center_id, customer_name, customer_phone,
                    serial_no, issue_desc, category_code, priority, status, technician_id,
                    received_at, due_date, closed_at)
                   VALUES (:ticket_id, :ticket_code, :center_id, :customer_name, :customer_phone,
                    :serial_no, :issue_desc, :category_code, :priority, :status, :technician_id,
                    :received_at, :due_date, :closed_at)
                   ON CONFLICT (ticket_id) DO UPDATE SET
                    ticket_code = EXCLUDED.ticket_code,
                    center_id = EXCLUDED.center_id,
                    customer_name = EXCLUDED.customer_name,
                    customer_phone = EXCLUDED.customer_phone,
                    serial_no = EXCLUDED.serial_no,
                    issue_desc = EXCLUDED.issue_desc,
                    category_code = EXCLUDED.category_code,
                    priority = EXCLUDED.priority,
                    status = EXCLUDED.status,
                    technician_id = EXCLUDED.technician_id,
                    received_at = EXCLUDED.received_at,
                    due_date = EXCLUDED.due_date,
                    closed_at = EXCLUDED.closed_at"""
            ),
            {
                "ticket_id": int(row["ticket_id"]),
                "ticket_code": _required(row, "ticket_code", "tickets_history.csv"),
                "center_id": int(row["center_id"]),
                "customer_name": _required(customer, "ho_ten", "customers_raw.csv"),
                "customer_phone": phone,
                "serial_no": _required(row, "serial_no", "tickets_history.csv"),
                "issue_desc": row.get("issue_desc") or "",
                "category_code": category_code,
                "priority": priority,
                "status": status,
                "technician_id": int(row["technician_id"]) if row.get("technician_id") else None,
                "received_at": parse_datetime(_required(row, "received_at", "tickets_history.csv")),
                "due_date": parse_datetime(_required(row, "due_date", "tickets_history.csv")),
                "closed_at": parse_datetime(row["closed_at"]) if row.get("closed_at") else None,
            },
        )
        loaded += 1

    return loaded, rejects


def _write_rejects(
    destination: Path,
    source_fields: list[str],
    rejects: list[dict[str, str]],
) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(
            stream, fieldnames=[*source_fields, "reject_reason"]
        )
        writer.writeheader()
        writer.writerows(rejects)


def _write_demo_accounts(
    centers: list[dict[str, str]],
    technicians: list[dict[str, str]],
    output_path: Path,
    password: str,
) -> None:
    accounts: list[dict[str, Any]] = []
    center_names = {
        str(center["center_id"]): center["center_name"] for center in centers
    }
    for center in centers:
        accounts.append(
            {
                "username": f"QL_{center['center_code']}",
                "role": "QUAN_LY",
                "center_id": int(center["center_id"]),
                "center_name": center["center_name"],
                "technician_id": None,
                "full_name": f"Quản lý {center['center_name']}",
                "employee_id": int(center["center_id"]),
                "password_hash": make_password_hash(password),
            }
        )
    for technician in technicians:
        accounts.append(
            {
                "username": technician["technician_code"],
                "role": "KY_THUAT_VIEN",
                "center_id": int(technician["center_id"]),
                "center_name": center_names[str(technician["center_id"])],
                "technician_id": int(technician["technician_id"]),
                "full_name": technician["ho_ten"],
                "employee_id": int(technician["technician_id"]),
                "password_hash": make_password_hash(password),
            }
        )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps({"accounts": accounts}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _write_report(
    destination: Path,
    seed: int,
    centers: int,
    categories: int,
    technicians: int,
    skills: int,
    tickets_source: int,
    tickets_loaded: int,
    ticket_rejects: int,
    input_states: dict[str, str],
) -> None:
    rows = [
        "# Báo cáo nạp dữ liệu thật",
        "",
        f"**Trạng thái:** INCOMPLETE · **Seed:** `{seed}`",
        "",
        "| Nguồn/bảng | Nguồn | Nạp/upsert | Loại |",
        "|---|---:|---:|---:|",
        f"| service_centers.csv → service_center | {centers} | {centers} | 0 |",
        f"| issue_categories.csv (lookup) | {categories} | không có bảng đích | 0 |",
        f"| technicians.csv → technician | {technicians} | {technicians} | 0 |",
        f"| technician_skills.csv → technician_skill | {skills} | {skills} | 0 |",
        f"| tickets_history.csv → ticket | {tickets_source} | {tickets_loaded} | {ticket_rejects} |",
        f"| ticket_status_log.csv → ticket_status_log | {input_states['ticket_status_log.csv']} | 0 | 0 |",
        f"| appointments.csv → appointment | {input_states['appointments.csv']} | 0 | 0 |",
        "",
        f"Phiếu bị loại được ghi vào `data/rejects/tickets_rejected.csv`. "
        f"Tài khoản demo được ghi vào `data/processed/demo_accounts.json`.",
        "",
        "Nguồn chưa nạp: " + ", ".join(input_states),
        "",
        "Phiếu MỚI không được tạo vì pipeline log trạng thái chưa được xác minh. "
        "Không dùng dữ liệu này cho acceptance test TC01–TC18.",
    ]
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("\n".join(rows) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv-dir", type=Path, default=ROOT / "data" / "raw")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--db-url")
    parser.add_argument(
        "--empty-center",
        help="Center code intentionally left without generated MOI tickets (default: last center).",
    )
    parser.add_argument(
        "--allow-incomplete",
        action="store_true",
        help="Load available core CSVs while clearly reporting missing log/appointment inputs.",
    )
    return parser


def main() -> int:
    load_dotenv(ROOT / ".env")
    args = build_parser().parse_args()
    csv_dir = args.csv_dir.resolve()
    required = (
        "service_centers.csv",
        "issue_categories.csv",
        "technicians.csv",
        "technician_skills.csv",
        "tickets_history.csv",
        "customers_raw.csv",
    )
    missing_core = [name for name in required if not (csv_dir / name).is_file()]
    if missing_core:
        raise SeedError(f"Missing required CSV files: {', '.join(missing_core)}")

    incomplete_inputs = ["ticket_status_log.csv", "appointments.csv"]
    input_states = {
        name: "MISSING"
        if not (csv_dir / name).is_file()
        else "present, but no verified importer"
        for name in incomplete_inputs
    }
    if not args.allow_incomplete:
        raise SeedError(
            "The current seed pipeline does not import ticket_status_log.csv or "
            "appointments.csv. Supply verified import mappings before running a complete "
            "seed, or pass --allow-incomplete to load only the core tables."
        )

    password = os.getenv("DEMO_PASSWORD", "")
    if not password:
        raise SeedError("Set DEMO_PASSWORD in .env before creating demo accounts.")

    source: dict[str, tuple[list[str], list[dict[str, str]]]] = {
        name: read_csv(csv_dir / name)
        for name in required
    }
    center_fields, centers = source["service_centers.csv"]
    _, categories = source["issue_categories.csv"]
    _, technicians = source["technicians.csv"]
    _, skills = source["technician_skills.csv"]
    ticket_fields, tickets = source["tickets_history.csv"]
    _, customer_rows = source["customers_raw.csv"]
    customers = {row["record_id"]: row for row in customer_rows}
    category_map = {
        row["category_id"]: row["category_name"].strip().upper()
        for row in categories
    }
    if len(customers) != len(customer_rows):
        raise SeedError("customers_raw.csv has duplicate record_id values; refusing ambiguous joins.")
    center_codes = {center["center_code"] for center in centers}
    if args.empty_center and args.empty_center not in center_codes:
        raise SeedError(f"Unknown --empty-center code: {args.empty_center}")
    if not center_fields:
        raise SeedError("service_centers.csv has no headers.")

    engine = create_engine(database_url(args))
    rejects_path = ROOT / "data" / "rejects" / "tickets_rejected.csv"
    try:
        with engine.begin() as connection:
            _upsert_catalog(connection, centers, categories, technicians, skills)
            loaded, rejects = _load_tickets(
                connection,
                tickets,
                customers,
                category_map,
            )
            for table, column in (
                ("service_center", "center_id"),
                ("technician", "technician_id"),
                ("ticket", "ticket_id"),
            ):
                connection.execute(
                    text(
                        f"""SELECT setval(pg_get_serial_sequence('{table}', '{column}'),
                               COALESCE((SELECT max({column}) FROM {table}), 1),
                               EXISTS (SELECT 1 FROM {table}))"""
                    )
                )
    finally:
        engine.dispose()

    _write_rejects(rejects_path, ticket_fields, rejects)
    _write_demo_accounts(
        centers,
        technicians,
        ROOT / "data" / "processed" / "demo_accounts.json",
        password,
    )
    _write_report(
        ROOT / "docs" / "bao-cao-nap-du-lieu.md",
        args.seed,
        len(centers),
        len(categories),
        len(technicians),
        len(skills),
        len(tickets),
        loaded,
        len(rejects),
        input_states,
    )
    print(f"Seed {args.seed}; loaded core case-study tables into the configured database.")
    print(
        f"service_center: source={len(centers)} "
        f"loaded={len(centers)} rejected=0"
    )
    print(
        f"technician: source={len(technicians)} "
        f"loaded={len(technicians)} rejected=0"
    )
    print(
        f"technician_skill: source={len(skills)} "
        f"loaded={len(skills)} rejected=0"
    )
    print(
        f"ticket: source={len(tickets)} loaded={loaded} rejected={len(rejects)} "
        f"(data/rejects/tickets_rejected.csv)"
    )
    for table, filename in (
        ("ticket_status_log", "ticket_status_log.csv"),
        ("appointment", "appointments.csv"),
    ):
        source_state = input_states[filename]
        print(f"{table}: source={source_state} loaded=0 rejected=0; NOT COMPLETE")
    print("MOI generation: NOT RUN because its required status-log source is not imported.")
    empty_center = args.empty_center or centers[-1]["center_code"]
    print(
        f"Requested empty-center={empty_center}; MOI selection was not run, "
        "so no center's empty state is guaranteed."
    )
    print("INCOMPLETE SEED: do not use this database for TC01-TC18.")
    print("Demo account file: data/processed/demo_accounts.json")
    if rejects:
        print(f"Rejected ticket rows: {len(rejects)}")
    return 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SeedError as error:
        print(f"Seed aborted: {error}", file=sys.stderr)
        sys.exit(2)
