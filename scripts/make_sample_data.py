"""Cut a small, committed sample of the case-study CSVs from data/raw/ into data/sample/.

The sample keeps the original file names and headers, so the same loaders read it.
It contains:
- every service center, category, technician and skill (small tables, kept whole);
- every DA_PHAN_CONG ticket, so the seeded choice of 30 MOI tickets (seed 20260901)
  is exactly the one made on the full data;
- every ticket referenced by data/sample/appointments.csv, so the same appointment
  file loads on both the full data and the sample;
- per technician, up to PER_STATUS tickets of each other status (seed below);
- a few tickets whose customer has no valid phone, to keep the reject path visible;
- the status-log rows and customer rows these tickets need.

Usage: python scripts/make_sample_data.py   (needs the full CSVs in data/raw/)
"""

from __future__ import annotations

import csv
import random
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
SAMPLE = ROOT / "data" / "sample"
SEED = 20261112
PER_STATUS = 4
REJECTED_EXAMPLES = 12
WHOLE_FILES = ("service_centers.csv", "issue_categories.csv", "technicians.csv", "technician_skills.csv")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def read(name: str) -> tuple[list[str], list[dict[str, str]]]:
    with (RAW / name).open("r", encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        return list(reader.fieldnames or []), list(reader)


def write(name: str, header: list[str], rows: list[dict[str, str]]) -> None:
    with (SAMPLE / name).open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)
    print(f"{name}: {len(rows)} dòng")


def valid_phone(raw: str) -> bool:
    value = re.sub(r"[\s.\-()]", "", raw.strip())
    if value.startswith("+84"):
        value = "0" + value[3:]
    elif value.startswith("84"):
        value = "0" + value[2:]
    return bool(re.fullmatch(r"0[0-9]{9}", value))


def main() -> int:
    missing = [name for name in (*WHOLE_FILES, "tickets_history.csv", "ticket_status_log.csv",
                                 "customers_raw.csv") if not (RAW / name).exists()]
    if missing:
        print(f"Thiếu tệp trong data/raw/: {', '.join(missing)}")
        return 1
    SAMPLE.mkdir(parents=True, exist_ok=True)
    rng = random.Random(SEED)

    for name in WHOLE_FILES:
        write(name, *read(name))

    ticket_header, tickets = read("tickets_history.csv")
    log_header, logs = read("ticket_status_log.csv")
    customer_header, customers = read("customers_raw.csv")
    customer_by_id = {row["record_id"].strip(): row for row in customers}

    def has_valid_customer(ticket: dict[str, str]) -> bool:
        customer = customer_by_id.get(ticket["customer_id"].strip())
        return bool(customer and customer["ho_ten"].strip() and valid_phone(customer["so_dien_thoai"]))

    with (SAMPLE / "appointments.csv").open("r", encoding="utf-8-sig", newline="") as source:
        appointments = list(csv.DictReader(source))
    chosen = {row["ticket_id"].strip() for row in appointments}
    chosen |= {row["ticket_id"].strip() for row in tickets if row["status"].strip() == "DA_PHAN_CONG"}

    by_technician_status: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in tickets:
        if has_valid_customer(row):
            by_technician_status[(row["technician_id"].strip(), row["status"].strip())].append(row)
    for key in sorted(by_technician_status):
        group = sorted(by_technician_status[key], key=lambda row: int(row["ticket_id"]))
        chosen |= {row["ticket_id"].strip() for row in rng.sample(group, min(PER_STATUS, len(group)))}

    rejected = sorted((row for row in tickets if not has_valid_customer(row)), key=lambda row: int(row["ticket_id"]))
    chosen |= {row["ticket_id"].strip() for row in rng.sample(rejected, min(REJECTED_EXAMPLES, len(rejected)))}

    # load_appointments accepts a created_by only if it appears as changed_by in the log.
    logs_by_ticket: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in logs:
        logs_by_ticket[row["ticket_id"].strip()].append(row)
    needed = {row["created_by"].strip() for row in appointments}
    present = {log["changed_by"].strip() for ticket_id in chosen for log in logs_by_ticket[ticket_id]}
    for row in sorted(tickets, key=lambda row: int(row["ticket_id"])):
        if not needed - present:
            break
        ticket_id = row["ticket_id"].strip()
        extra = {log["changed_by"].strip() for log in logs_by_ticket[ticket_id]} & (needed - present)
        if extra and has_valid_customer(row):
            chosen.add(ticket_id)
            present |= extra

    sample_tickets = [row for row in tickets if row["ticket_id"].strip() in chosen]
    sample_logs = [row for row in logs if row["ticket_id"].strip() in chosen]
    customer_ids = {row["customer_id"].strip() for row in sample_tickets}
    sample_customers = [row for row in customers if row["record_id"].strip() in customer_ids]

    write("tickets_history.csv", ticket_header, sample_tickets)
    write("ticket_status_log.csv", log_header, sample_logs)
    write("customers_raw.csv", customer_header, sample_customers)
    print(f"created_by của lịch hẹn còn thiếu trong log: {sorted(needed - present) or 'không'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
