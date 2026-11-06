from __future__ import annotations

import csv
import os
import sys
from pathlib import Path
from typing import Callable, Iterable

import psycopg
from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[1]
try:
    from data_source import describe, resolve_data_dir
except ImportError:  # imported as scripts.<module> (tests)
    from scripts.data_source import describe, resolve_data_dir

RAW_DIR = resolve_data_dir()
REPORT_DIR = ROOT / "reports"
REJECTS_FILE = REPORT_DIR / "load_catalog_rejects.csv"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def read_csv(name: str) -> list[dict[str, str]]:
    with (RAW_DIR / name).open("r", encoding="utf-8-sig", newline="") as source:
        return list(csv.DictReader(source))


def parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    raise ValueError("is_active phải là 'true' hoặc 'false'")


def parse_int(value: str, field: str) -> int:
    try:
        return int(value.strip())
    except (AttributeError, ValueError) as exc:
        raise ValueError(f"{field} phải là số nguyên") from exc


def reject_rows(rows: Iterable[dict[str, str]], validator: Callable[[dict[str, str]], bool]) -> list[dict[str, str]]:
    rejects: list[dict[str, str]] = []
    for row in rows:
        try:
            if validator(row):
                continue
        except Exception as exc:
            rejects.append({**row, "reason": str(exc)})
    return rejects


def write_rejects(rejects: list[dict[str, str]]) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    fieldnames = sorted({key for reject in rejects for key in reject.keys()})
    if not fieldnames:
        fieldnames = [
            "center_id",
            "center_code",
            "center_name",
            "thanh_pho",
            "technician_id",
            "technician_code",
            "ho_ten",
            "category_id",
            "proficiency",
            "level",
            "is_active",
            "reason",
        ]
    if "reason" in fieldnames:
        fieldnames.remove("reason")
        fieldnames.append("reason")
    with REJECTS_FILE.open("w", encoding="utf-8-sig", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rejects)


def db_config() -> dict[str, object]:
    load_dotenv(ROOT / ".env")
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", "5432")),
        "dbname": os.getenv("DB_NAME", "smartcrm"),
        "user": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD", ""),
    }


def main() -> int:
    print(describe(RAW_DIR))
    center_rows = read_csv("service_centers.csv")
    technician_rows = read_csv("technicians.csv")
    skill_rows = read_csv("technician_skills.csv")
    category_rows = read_csv("issue_categories.csv")

    rejects: list[dict[str, str]] = []
    center_rejects: list[dict[str, str]] = []
    technician_rejects: list[dict[str, str]] = []
    skill_rejects: list[dict[str, str]] = []
    categories = {
        parse_int(row["category_id"], "category_id"): row["category_name"].strip()
        for row in category_rows
    }
    valid_centers: dict[int, dict[str, str]] = {}
    for row in center_rows:
        try:
            center_id = parse_int(row["center_id"], "center_id")
            if center_id <= 0:
                raise ValueError("center_id phải lớn hơn 0")
            valid_centers[center_id] = row
        except (KeyError, ValueError) as exc:
            rejects.append({**row, "reason": str(exc)})
            center_rejects.append({**row, "reason": str(exc)})

    valid_technicians: dict[int, dict[str, str]] = {}
    for row in technician_rows:
        try:
            technician_id = parse_int(row["technician_id"], "technician_id")
            center_id = parse_int(row["center_id"], "center_id")
            if technician_id <= 0:
                raise ValueError("technician_id phải lớn hơn 0")
            if center_id not in valid_centers:
                raise ValueError(f"center_id {center_id} không tồn tại trong service_centers.csv")
            parse_bool(row["is_active"])
            if row["level"].strip() not in {"SO_CAP", "TRUNG_CAP", "CAO_CAP"}:
                raise ValueError("level không thuộc SO_CAP/TRUNG_CAP/CAO_CAP")
            valid_technicians[technician_id] = row
        except (KeyError, ValueError) as exc:
            rejects.append({**row, "reason": str(exc)})
            technician_rejects.append({**row, "reason": str(exc)})

    valid_skills: list[tuple[int, str, int]] = []
    for row in skill_rows:
        try:
            technician_id = parse_int(row["technician_id"], "technician_id")
            category_id = parse_int(row["category_id"], "category_id")
            proficiency = parse_int(row["proficiency"], "proficiency")
            if technician_id not in valid_technicians:
                raise ValueError(f"technician_id {technician_id} không tồn tại trong technicians.csv")
            if category_id not in categories:
                raise ValueError(f"category_id {category_id} không tồn tại trong issue_categories.csv")
            if not 1 <= proficiency <= 5:
                raise ValueError("proficiency phải trong khoảng 1..5")
            valid_skills.append((technician_id, categories[category_id], proficiency))
        except (KeyError, ValueError) as exc:
            rejects.append({**row, "reason": str(exc)})
            skill_rejects.append({**row, "reason": str(exc)})

    write_rejects(rejects)

    inserted_centers = inserted_technicians = inserted_skills = 0
    with psycopg.connect(**db_config()) as conn:
        with conn.cursor() as cur:
            for center_id, row in valid_centers.items():
                cur.execute(
                    """
                    INSERT INTO service_center (center_id, center_code, center_name, city)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                    """,
                    (center_id, row["center_code"].strip(), row["center_name"].strip(), row["thanh_pho"].strip()),
                )
                inserted_centers += cur.rowcount

            for technician_id, row in valid_technicians.items():
                cur.execute(
                    """
                    INSERT INTO technician
                        (technician_id, technician_code, full_name, center_id, level, is_active)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                    """,
                    (
                        technician_id,
                        row["technician_code"].strip(),
                        row["ho_ten"].strip(),
                        int(row["center_id"]),
                        row["level"].strip(),
                        parse_bool(row["is_active"]),
                    ),
                )
                inserted_technicians += cur.rowcount

            for technician_id, category_code, proficiency in valid_skills:
                cur.execute(
                    """
                    INSERT INTO technician_skill (technician_id, category_code, proficiency)
                    VALUES (%s, %s, %s)
                    ON CONFLICT DO NOTHING
                    """,
                    (technician_id, category_code, proficiency),
                )
                inserted_skills += cur.rowcount

            cur.execute("SELECT setval('service_center_center_id_seq', GREATEST(COALESCE(MAX(center_id), 1), 1), EXISTS (SELECT 1 FROM service_center)) FROM service_center")
            cur.execute("SELECT setval('technician_technician_id_seq', GREATEST(COALESCE(MAX(technician_id), 1), 1), EXISTS (SELECT 1 FROM technician)) FROM technician")

    print(f"ĐỌC: service_center={len(center_rows)}, technician={len(technician_rows)}, technician_skill={len(skill_rows)}, issue_category={len(category_rows)}")
    print(f"NẠP: service_center={inserted_centers}, technician={inserted_technicians}, technician_skill={inserted_skills}")
    print(f"LOẠI: service_center={len(center_rejects)}, technician={len(technician_rejects)}, technician_skill={len(skill_rejects)}, total={len(rejects)}")
    print(f"REJECT_FILE={REJECTS_FILE.relative_to(ROOT)}")
    print(f"TỒNG KẾT: {len(valid_centers)} trung tâm hợp lệ, {len(valid_technicians)} kỹ thuật viên hợp lệ, {len(valid_skills)} kỹ năng hợp lệ, {len(rejects)} dòng loại")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
