"""Technician-specific ticket listing."""

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import text

from app.core.database import get_engine
from app.core.errors import APIError
from app.core.security import require_role
from app.routers.tickets import _mask_phone

router = APIRouter(prefix="/api/technicians", tags=["technicians"])


@router.get("/me/tickets")
def my_tickets(
    user: dict[str, Any] = Depends(require_role("KY_THUAT_VIEN")),
) -> list[dict[str, Any]]:
    with get_engine().connect() as connection:
        rows = connection.execute(
            text(
                """SELECT ticket_id, ticket_code, customer_name, customer_phone,
                          serial_no, issue_desc, category_code, priority, status,
                          received_at, due_date, technician_id
                   FROM ticket WHERE technician_id = :technician_id
                   ORDER BY due_date, ticket_id"""
            ),
            {"technician_id": user["technician_id"]},
        ).mappings().all()
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)
    tickets: list[dict[str, Any]] = []
    for row in rows:
        item = dict(row)
        item["customer_phone"] = _mask_phone(item["customer_phone"])
        item["is_overdue"] = item["due_date"] < now and item["status"] not in {
            "HOAN_TAT", "DA_DONG", "DA_HUY"
        }
        tickets.append(item)
    return tickets
