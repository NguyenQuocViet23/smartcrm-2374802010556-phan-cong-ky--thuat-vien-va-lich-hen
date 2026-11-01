from __future__ import annotations

import csv
import os
import random
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import psycopg
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
OUT_FILE = ROOT / "data" / "sample" / "appointments.csv"
EDGE_FILE = ROOT / "reports" / "appointment_edge_cases.csv"
SEED = 20261102
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


def dates() -> list[date]:
    result = []
    current = date(2026, 11, 3)
    end = date(2027, 1, 30)
    while current <= end:
        if current.weekday() != 6:
            result.append(current)
        current += timedelta(days=1)
    return result


def overlaps(intervals: dict[int, list[tuple[datetime, datetime]]], technician_id: int, start: datetime, end: datetime) -> bool:
    return any(start < other_end and other_start < end for other_start, other_end in intervals[technician_id])


def main() -> int:
    with psycopg.connect(**db_config()) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT t.ticket_id, t.ticket_code, t.center_id, t.technician_id, t.category_code
                FROM ticket t
                JOIN technician tech ON tech.technician_id=t.technician_id
                WHERE t.status IN ('DA_PHAN_CONG', 'DANG_XU_LY', 'CHO_LINH_KIEN')
                  AND tech.is_active AND t.center_id=tech.center_id
                ORDER BY t.ticket_id
            """)
            pool = cur.fetchall()
            cur.execute("""
                SELECT DISTINCT changed_by FROM ticket_status_log
                WHERE changed_by IS NOT NULL AND changed_by > 0
                ORDER BY changed_by
            """)
            created_by_values = [row[0] for row in cur.fetchall()]

    rng = random.Random(SEED)
    rng.shuffle(pool)
    intervals: dict[int, list[tuple[datetime, datetime]]] = defaultdict(list) if False else {}
    appointments: list[dict[str, object]] = []

    available_dates = dates()
    for ticket in pool:
        technician_id = int(ticket[3])
        intervals.setdefault(technician_id, [])
    technicians = sorted(intervals)

    # Fixed adjacent pair: 08:00-08:30 and 08:30-09:00 on one selected technician.
    technician_id = technicians[rng.randrange(len(technicians))]
    technician_pool = [ticket for ticket in pool if int(ticket[3]) == technician_id]
    day = available_dates[rng.randrange(len(available_dates))]
    first_start = datetime(day.year, day.month, day.day, 8, 0, tzinfo=TZ)
    adjacent_starts = [first_start, first_start + timedelta(minutes=30)]
    for offset, start in enumerate(adjacent_starts):
        ticket = technician_pool[offset % len(technician_pool)]
        appointments.append({
            "appointment_id": len(appointments) + 1,
            "ticket_id": ticket[0],
            "technician_id": ticket[3],
            "appointment_type": "GIAO" if offset == 0 else "NHAN",
            "start_at": start.isoformat(timespec="minutes"),
            "end_at": (start + timedelta(minutes=30)).isoformat(timespec="minutes"),
            "status": "DA_HEN",
            "note": "",
            "created_by": created_by_values[rng.randrange(len(created_by_values))],
        })
        intervals[technician_id].append((start, start + timedelta(minutes=30)))

    slots: list[datetime] = []
    for day in available_dates:
        for minute in range(8 * 60, 18 * 60, 30):
            slots.append(datetime(day.year, day.month, day.day, minute // 60, minute % 60, tzinfo=TZ))

    while len(appointments) < 270:
        ticket = pool[rng.randrange(len(pool))]
        technician_id = int(ticket[3])
        rng.shuffle(slots)
        start = None
        for candidate in slots:
            if candidate.hour == 17 and candidate.minute == 30:
                end = candidate + timedelta(minutes=30)
            else:
                end = candidate + timedelta(minutes=30)
            if end > candidate.replace(hour=18, minute=0):
                continue
            if not overlaps(intervals, technician_id, candidate, end):
                start = candidate
                break
        if start is None:
            continue
        intervals[technician_id].append((start, start + timedelta(minutes=30)))
        appointments.append({
            "appointment_id": len(appointments) + 1,
            "ticket_id": ticket[0],
            "technician_id": ticket[3],
            "appointment_type": rng.choice(["GIAO", "NHAN"]),
            "start_at": start.isoformat(timespec="minutes"),
            "end_at": (start + timedelta(minutes=30)).isoformat(timespec="minutes"),
            "status": "DA_HEN",
            "note": rng.choice(["", "", "", "Khách hẹn lại lần 2", "Khách đến sớm hơn giờ hẹn"]),
            "created_by": created_by_values[rng.randrange(len(created_by_values))],
        })

    # Ensure at least one ticket has both GIAO and NHAN.
    shared_ticket = pool[rng.randrange(len(pool))]
    pair_indexes = [len(appointments) - 1, len(appointments) - 2]
    for index in pair_indexes:
        appointments[index]["ticket_id"] = shared_ticket[0]
        appointments[index]["technician_id"] = shared_ticket[3]
    appointments[pair_indexes[0]]["appointment_type"] = "GIAO"
    appointments[pair_indexes[1]]["appointment_type"] = "NHAN"

    # Cancelled appointments are allowed to overlap DA_HEN appointments.
    for index in range(30):
        source = appointments[(index * 9) % len(appointments)]
        start = datetime.fromisoformat(source["start_at"])
        appointments.append({
            "appointment_id": len(appointments) + 1,
            "ticket_id": source["ticket_id"],
            "technician_id": source["technician_id"],
            "appointment_type": rng.choice(["GIAO", "NHAN"]),
            "start_at": start.isoformat(timespec="minutes"),
            "end_at": (start + timedelta(minutes=30)).isoformat(timespec="minutes"),
            "status": "DA_HUY",
            "note": "Lịch bị hủy theo dữ liệu mô phỏng",
            "created_by": created_by_values[rng.randrange(len(created_by_values))],
        })

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "appointment_id", "ticket_id", "technician_id", "appointment_type",
        "start_at", "end_at", "status", "note", "created_by",
    ]
    with OUT_FILE.open("w", encoding="utf-8-sig", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(appointments)

    active = [row for row in appointments if row["status"] == "DA_HEN"]
    pair = active[:2]
    overlap_cancel = next(row for row in appointments if row["status"] == "DA_HUY")
    edge_rows = [
        {"edge_case": "adjacent_pair", "appointment_id": pair[0]["appointment_id"], "ticket_id": pair[0]["ticket_id"]},
        {"edge_case": "adjacent_pair", "appointment_id": pair[1]["appointment_id"], "ticket_id": pair[1]["ticket_id"]},
        {"edge_case": "cancelled_overlaps_active", "appointment_id": overlap_cancel["appointment_id"], "ticket_id": overlap_cancel["ticket_id"]},
        {"edge_case": "ticket_has_both_types", "appointment_id": pair_indexes[0] + 1, "ticket_id": shared_ticket[0]},
        {"edge_case": "ticket_has_both_types", "appointment_id": pair_indexes[1] + 1, "ticket_id": shared_ticket[0]},
    ]
    EDGE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with EDGE_FILE.open("w", encoding="utf-8-sig", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=["edge_case", "appointment_id", "ticket_id"])
        writer.writeheader()
        writer.writerows(edge_rows)

    print(f"ĐỌC POOL: {len(pool)} phiếu hợp lệ; created_by={len(created_by_values)} giá trị")
    print(f"SINH: appointment={len(appointments)}, DA_HEN=270, DA_HUY=30, seed={SEED}")
    print(f"CSV={OUT_FILE.relative_to(ROOT)}")
    print(f"EDGE={EDGE_FILE.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
