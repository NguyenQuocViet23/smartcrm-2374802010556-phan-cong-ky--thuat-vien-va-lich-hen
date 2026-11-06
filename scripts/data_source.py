"""Pick the folder the loaders read: the full case-study CSVs or the committed sample."""

from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASE_STUDY_FILES = (
    "service_centers.csv", "issue_categories.csv", "technicians.csv", "technician_skills.csv",
    "tickets_history.csv", "ticket_status_log.csv", "customers_raw.csv",
)


def resolve_data_dir() -> Path:
    """DATA_DIR if set; else data/raw/ when all 7 CSVs are there; else data/sample/."""
    configured = os.getenv("DATA_DIR", "").strip()
    if configured:
        path = Path(configured)
        return path if path.is_absolute() else ROOT / path
    raw = ROOT / "data" / "raw"
    if all((raw / name).exists() for name in CASE_STUDY_FILES):
        return raw
    return ROOT / "data" / "sample"


def describe(path: Path) -> str:
    label = "bộ mẫu trong repo" if path.name == "sample" else "dữ liệu case-study"
    try:
        shown = path.relative_to(ROOT).as_posix()
    except ValueError:
        shown = str(path)
    return f"NGUỒN DỮ LIỆU: {shown} ({label})"
