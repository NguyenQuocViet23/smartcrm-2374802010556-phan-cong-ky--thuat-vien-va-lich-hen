from __future__ import annotations

import csv
import os
import random
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import psycopg
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
REPORT_DIR = ROOT / "reports"
REJECTS_FILE = REPORT_DIR / "load_tickets_rejects.csv"
MOI_FILE = REPORT_DIR / "moi_tickets_seed20260901.csv"
LOCAL_TIMEZONE = ZoneInfo("Asia/Ho_Chi_Minh")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def read_csv(name: str) -> list[dict[str, str]]:
    with (RAW_DIR / name).open("r", encoding="utf-8-sig", newline="") as source:
        return list(csv.DictReader(source))


def db_config() -> dict[str, object]:
    load_dotenv(ROOT / ".env")
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", "5432")),
        "dbname": os.getenv("DB_NAME", "smartcrm"),
        "user": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD", ""),
    }


def parse_datetime(value: str) -> datetime | None:
    value = value.strip()
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d %H:%M").replace(tzinfo=LOCAL_TIMEZONE)


def normalize_phone(value: str) -> str | None:
    value = re.sub(r"[\s.\-()]", "", value.strip())
    if value.startswith("+84"):
        value = "0" + value[3:]
    elif value.startswith("84"):
        value = "0" + value[2:]
    return value if re.fullmatch(r"0[0-9]{9}", value) else None


def normalize_status(value: str) -> str | None:
    value = value.strip()
    return value if value else None


def write_rejects(rows: list[dict[str, str]]) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    fieldnames = ["entity", "source_id", "ticket_code", "reason"]
    with REJECTS_FILE.open("w", encoding="utf-8-sig", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_moi_tickets(ticket_codes: list[str]) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    with MOI_FILE.open("w", encoding="utf-8-sig", newline="") as target:
        writer = csv.writer(target)
        writer.writerow(["ticket_code"])
        writer.writerows((code,) for code in ticket_codes)


def positive_integer(value: str, field: str) -> int:
    if not re.fullmatch(r"[0-9]+", value.strip()):
        raise ValueError(f"{field} phải là số nguyên dương")
    parsed = int(value)
    if parsed <= 0:
        raise ValueError(f"{field} phải là số nguyên dương")
    return parsed


def main() -> int:
    ticket_rows = read_csv("tickets_history.csv")
    customer_rows = read_csv("customers_raw.csv")
    category_rows = read_csv("issue_categories.csv")
    log_rows = read_csv("ticket_status_log.csv")

    customers = {row["record_id"].strip(): row for row in customer_rows}
    categories = {row["category_id"].strip(): row["category_name"].strip() for row in category_rows}
    logs_by_ticket: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in log_rows:
        logs_by_ticket[row["ticket_id"].strip()].append(row)

    missing_phone_ticket_ids: set[str] = set()
    rejected_tickets: list[dict[str, str]] = []
    valid_tickets: list[dict[str, str]] = []
    for row in ticket_rows:
        customer = customers.get(row["customer_id"].strip())
        phone = normalize_phone(customer["so_dien_thoai"]) if customer else None
        if customer is None or not customer["ho_ten"].strip() or not phone:
            missing_phone_ticket_ids.add(row["ticket_id"].strip())
            rejected_tickets.append({
                "entity": "ticket",
                "source_id": row["ticket_id"].strip(),
                "ticket_code": row["ticket_code"].strip(),
                "reason": "thiếu SĐT",
            })
            continue
        valid_tickets.append(row)

    for row in rejected_tickets:
        for _ in logs_by_ticket[row["source_id"]]:
            pass

    rejects = list(rejected_tickets)
    for ticket_id in missing_phone_ticket_ids:
        rejects.extend(
            {
                "entity": "ticket_status_log",
                "source_id": log["log_id"].strip(),
                "ticket_code": "",
                "reason": "phiếu cha bị loại",
            }
            for log in logs_by_ticket.get(ticket_id, [])
        )

    assigned_pool = [row for row in valid_tickets if row["status"].strip() == "DA_PHAN_CONG"]
    pool_by_center: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in assigned_pool:
        pool_by_center[row["center_id"].strip()].append(row)

    rng = random.Random(20260901)
    moi_rows: list[dict[str, str]] = []
    for center_id in sorted(pool_by_center):
        candidates = sorted(pool_by_center[center_id], key=lambda row: int(row["ticket_id"]))
        moi_rows.extend(rng.sample(candidates, 5))
    moi_ticket_ids = {row["ticket_id"].strip() for row in moi_rows}
    write_moi_tickets(sorted((row["ticket_code"].strip() for row in moi_rows)))

    valid_ticket_values: list[tuple[object, ...]] = []
    valid_ticket_ids: set[str] = set()
    for row in valid_tickets:
        ticket_id = row["ticket_id"].strip()
        valid_ticket_ids.add(ticket_id)
        customer = customers[row["customer_id"].strip()]
        phone = normalize_phone(customer["so_dien_thoai"])
        status = normalize_status(row["status"])
        technician_id = None if ticket_id in moi_ticket_ids else (
            int(row["technician_id"]) if row["technician_id"].strip() else None
        )
        if ticket_id in moi_ticket_ids:
            status = "MOI"
        valid_ticket_values.append((
            int(ticket_id),
            row["ticket_code"].strip(),
            int(row["center_id"]),
            customer["ho_ten"].strip(),
            phone,
            row["serial_no"].strip(),
            row["issue_desc"].strip(),
            categories[row["category_id"].strip()],
            row["priority"].strip(),
            status,
            technician_id,
            parse_datetime(row["received_at"]),
            parse_datetime(row["due_date"]),
            None if ticket_id in moi_ticket_ids else parse_datetime(row["closed_at"]),
        ))

    valid_logs: list[tuple[object, ...]] = []
    ticket_log_rejects = 0
    removed_moi_logs = 0
    for row in log_rows:
        ticket_id = row["ticket_id"].strip()
        if ticket_id in missing_phone_ticket_ids:
            continue
        if ticket_id not in valid_ticket_ids:
            continue
        if ticket_id in moi_ticket_ids and normalize_status(row["from_status"]) == "MOI" and normalize_status(row["to_status"]) == "DA_PHAN_CONG":
            removed_moi_logs += 1
            continue
        try:
            changed_by = positive_integer(row["changed_by"], "changed_by")
        except ValueError as exc:
            ticket_log_rejects += 1
            rejects.append({
                "entity": "ticket_status_log",
                "source_id": row["log_id"].strip(),
                "ticket_code": "",
                "reason": str(exc),
            })
            continue
        valid_logs.append((
            int(row["log_id"]),
            int(ticket_id),
            "TRANG_THAI",
            normalize_status(row["from_status"]),
            normalize_status(row["to_status"]),
            None,
            None,
            changed_by,
            parse_datetime(row["changed_at"]),
            row["note"].strip() or None,
        ))

    for ticket_id in moi_ticket_ids:
        if not any(int(log[1]) == int(ticket_id) for log in valid_logs):
            source_row = next(row for row in ticket_rows if row["ticket_id"].strip() == ticket_id)
            valid_logs.append((
                max([int(row["log_id"]) for row in log_rows], default=0) + int(ticket_id),
                int(ticket_id),
                "TRANG_THAI",
                None,
                "MOI",
                None,
                None,
                1,
                parse_datetime(source_row["received_at"]),
                None,
            ))

    write_rejects(rejects)
    inserted_tickets = 0
    inserted_logs = 0
    with psycopg.connect(**db_config()) as conn:
        with conn.cursor() as cur:
            cur.executemany(
                """
                INSERT INTO ticket
                    (ticket_id, ticket_code, center_id, customer_name, customer_phone,
                     serial_no, issue_desc, category_code, priority, status, technician_id,
                     received_at, due_date, closed_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
                """,
                valid_ticket_values,
            )
            inserted_tickets = cur.rowcount if cur.rowcount >= 0 else len(valid_ticket_values)
            cur.executemany(
                """
                INSERT INTO ticket_status_log
                    (log_id, ticket_id, event_type, from_status, to_status,
                     from_technician_id, to_technician_id, changed_by, changed_at, note)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
                """,
                valid_logs,
            )
            inserted_logs = cur.rowcount if cur.rowcount >= 0 else len(valid_logs)
            cur.execute(
                """
                SELECT setval('ticket_ticket_id_seq',
                              GREATEST(COALESCE(MAX(ticket_id), 1), 1),
                              EXISTS (SELECT 1 FROM ticket))
                FROM ticket
                """
            )
            cur.execute(
                """
                SELECT setval('ticket_status_log_log_id_seq',
                              GREATEST(COALESCE(MAX(log_id), 1), 1),
                              EXISTS (SELECT 1 FROM ticket_status_log))
                FROM ticket_status_log
                """
            )

            cur.execute("""
                SELECT COALESCE(SUM(quality), 0) FROM (
                    SELECT COUNT(*) quality FROM ticket WHERE status='MOI' AND technician_id IS NOT NULL
                ) q
            """)
            invariants = [cur.fetchone()[0]]
            cur.execute("""
                SELECT COUNT(*) FROM ticket t JOIN technician tech ON tech.technician_id=t.technician_id
                WHERE t.center_id <> tech.center_id
            """)
            invariants.append(cur.fetchone()[0])
            cur.execute("""
                WITH ranked AS (
                    SELECT ticket_id, to_status,
                           row_number() OVER (PARTITION BY ticket_id ORDER BY changed_at DESC, log_id DESC) rn
                    FROM ticket_status_log
                )
                SELECT COUNT(*) FROM ranked l JOIN ticket t USING (ticket_id)
                WHERE l.rn=1 AND l.to_status<>t.status
            """)
            invariants.append(cur.fetchone()[0])
            cur.execute("""
                WITH ordered AS (
                    SELECT ticket_id, log_id, from_status, to_status,
                           lag(to_status) OVER (PARTITION BY ticket_id ORDER BY changed_at, log_id) previous_to
                    FROM ticket_status_log
                )
                SELECT COUNT(*) FROM ordered
                WHERE from_status IS NOT NULL AND from_status IS DISTINCT FROM previous_to
            """)
            invariants.append(cur.fetchone()[0])
            cur.execute("SELECT COUNT(*) FROM ticket t WHERE NOT EXISTS (SELECT 1 FROM ticket_status_log l WHERE l.ticket_id=t.ticket_id)")
            invariants.append(cur.fetchone()[0])

            cur.execute("SELECT status, COUNT(*) FROM ticket GROUP BY status ORDER BY status")
            status_counts = dict(cur.fetchall())
            cur.execute("SELECT center_id, COUNT(*) FROM ticket WHERE status='MOI' GROUP BY center_id ORDER BY center_id")
            moi_by_center = dict(cur.fetchall())
            cur.execute("SELECT COUNT(*) FROM ticket")
            ticket_count = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM ticket_status_log")
            log_count = cur.fetchone()[0]
            cur.execute("""
                SELECT COUNT(*) FROM ticket t JOIN technician tech ON tech.technician_id=t.technician_id
                WHERE t.status='MOI'
            """)
            moi_with_tech = cur.fetchone()[0]

    print(f"ĐỌC: ticket={len(ticket_rows)}, ticket_status_log={len(log_rows)}, customers={len(customer_rows)}")
    print(f"NẠP: ticket={inserted_tickets}, ticket_status_log={inserted_logs}")
    rejected_parent_logs = sum(len(logs_by_ticket.get(ticket_id, [])) for ticket_id in missing_phone_ticket_ids)
    print(f"LOẠI: ticket={len(rejected_tickets)}, ticket_status_log={rejected_parent_logs + ticket_log_rejects}")
    print(f"MOI_REMOVED_LOGS: {removed_moi_logs}")
    print(f"REJECT_FILE={REJECTS_FILE.relative_to(ROOT)}")
    print(f"MOI_FILE={MOI_FILE.relative_to(ROOT)}")
    print(f"DATABASE_COUNTS: ticket={ticket_count}, ticket_status_log={log_count}")
    print(f"STATUS_COUNTS: {dict(sorted(status_counts.items()))}")
    print(f"MOI_BY_CENTER: {dict(sorted(moi_by_center.items()))}")
    print("INVARIANTS [MOI_NULL_TECH, CROSS_CENTER_TECH, LAST_LOG_MISMATCH, QT06, NO_LOG]: " + ",".join(map(str, invariants)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
