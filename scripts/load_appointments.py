from __future__ import annotations

import csv
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import psycopg
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
CSV_FILE = ROOT / "data" / "sample" / "appointments.csv"
TZ = ZoneInfo("Asia/Ho_Chi_Minh")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def db_config() -> dict[str, object]:
    load_dotenv(ROOT / ".env")
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", "5432")),
        "dbname": os.getenv("DB_NAME", "smartcrm"),
        "user": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD", ""),
    }


def parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value).replace(tzinfo=TZ)


def main() -> int:
    with CSV_FILE.open("r", encoding="utf-8-sig", newline="") as source:
        rows = list(csv.DictReader(source))

    rejects: list[dict[str, str]] = []
    values: list[tuple[object, ...]] = []
    intervals: dict[int, list[tuple[datetime, datetime]]] = {}

    with psycopg.connect(**db_config()) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT t.ticket_id, t.technician_id, t.status, t.center_id
                FROM ticket t
                JOIN technician tech ON tech.technician_id = t.technician_id
                WHERE t.status IN ('DA_PHAN_CONG', 'DANG_XU_LY', 'CHO_LINH_KIEN')
                  AND t.technician_id IS NOT NULL
                  AND tech.is_active
                  AND tech.center_id = t.center_id
            """)
            tickets = {int(ticket_id): int(technician_id) for ticket_id, technician_id, _status, _center in cur.fetchall()}
            cur.execute("SELECT technician_id FROM technician WHERE is_active")
            active_technicians = {int(row[0]) for row in cur.fetchall()}
            cur.execute("SELECT DISTINCT changed_by FROM ticket_status_log WHERE changed_by > 0")
            created_by_values = {int(row[0]) for row in cur.fetchall()}

            for row in rows:
                try:
                    appointment_id = int(row["appointment_id"])
                    ticket_id = int(row["ticket_id"])
                    technician_id = int(row["technician_id"])
                    created_by = int(row["created_by"])
                    start_at = parse_datetime(row["start_at"])
                    end_at = parse_datetime(row["end_at"])

                    if ticket_id not in tickets:
                        raise ValueError("ticket không hợp lệ")
                    if technician_id != tickets[ticket_id]:
                        raise ValueError("technician_id khác ticket.technician_id")
                    if technician_id not in active_technicians:
                        raise ValueError("technician không active")
                    if row["appointment_type"] not in {"GIAO", "NHAN"}:
                        raise ValueError("appointment_type không hợp lệ")
                    if row["status"] not in {"DA_HEN", "DA_HUY"}:
                        raise ValueError("status không hợp lệ")
                    if created_by not in created_by_values:
                        raise ValueError("created_by không thuộc changed_by")
                    if end_at - start_at != timedelta(minutes=30):
                        raise ValueError("thời lượng khác 30 phút")
                    if start_at.weekday() == 6:
                        raise ValueError("không sinh lịch Chủ nhật")
                    if row["status"] == "DA_HEN":
                        intervals.setdefault(technician_id, [])
                        if any(start_at < current_end and current_start < end_at
                               for current_start, current_end in intervals[technician_id]):
                            raise ValueError("lịch DA_HEN bị chồng")
                        intervals[technician_id].append((start_at, end_at))

                    values.append((
                        appointment_id, ticket_id, technician_id, row["appointment_type"],
                        start_at, end_at, row["status"], row["note"].strip() or None,
                        created_by, datetime.now(TZ),
                    ))
                except (ValueError, KeyError) as exc:
                    rejects.append({"appointment_id": row.get("appointment_id", ""), "reason": str(exc)})

            inserted = 0
            if values:
                cur.executemany("""
                    INSERT INTO appointment
                        (appointment_id, ticket_id, technician_id, appointment_type,
                         start_at, end_at, status, note, created_by, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (appointment_id) DO NOTHING
                """, values)
                inserted = cur.rowcount if cur.rowcount >= 0 else 0

            cur.execute("""
                SELECT setval('appointment_appointment_id_seq',
                              GREATEST(COALESCE(MAX(appointment_id), 1), 1),
                              EXISTS (SELECT 1 FROM appointment))
                FROM appointment
            """)

            cur.execute("SELECT count(*) FROM appointment")
            total = cur.fetchone()[0]
            cur.execute("SELECT status, count(*) FROM appointment GROUP BY status ORDER BY status")
            status_counts = cur.fetchall()

    print(f"ĐỌC: appointment={len(rows)}")
    print(f"NẠP: appointment={inserted}")
    print(f"LOẠI: appointment={len(rejects)}")
    print(f"DATABASE_COUNTS: appointment={total}")
    print(f"STATUS_COUNTS: {dict(status_counts)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
