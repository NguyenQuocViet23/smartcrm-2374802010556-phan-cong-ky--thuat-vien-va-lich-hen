"""SQL for appointments. No business rules here."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import Connection
from sqlalchemy.exc import IntegrityError

COLUMNS = (
    "appointment_id, ticket_id, technician_id, appointment_type, start_at, end_at, status, note"
)
EXCLUSION_VIOLATION = "23P01"  # PostgreSQL: the no-overlap EXCLUDE constraint (QT-13)


class OverlapViolation(Exception):
    """The database refused the booking because it overlaps another one."""


def _raise_overlap(error: IntegrityError) -> None:
    if getattr(error.orig, "sqlstate", None) == EXCLUSION_VIOLATION:
        raise OverlapViolation from error
    raise error


def find_overlaps(
    connection: Connection, technician_id: int, start: datetime, end: datetime,
    exclude_id: int | None = None,
) -> list[dict[str, Any]]:
    rows = connection.execute(
        text(
            """SELECT a.appointment_id, t.ticket_code, a.start_at, a.end_at
               FROM appointment a JOIN ticket t ON t.ticket_id = a.ticket_id
               WHERE a.technician_id = :technician_id AND a.status = 'DA_HEN'
                 AND a.start_at < :end_at AND :start_at < a.end_at
                 AND a.appointment_id IS DISTINCT FROM :exclude_id
               ORDER BY a.start_at"""
        ),
        {"technician_id": technician_id, "start_at": start, "end_at": end,
         "exclude_id": exclude_id},
    ).mappings().all()
    return [dict(row) for row in rows]


def busy_intervals(
    connection: Connection, technician_id: int, open_at: datetime, close_at: datetime,
    exclude_id: int | None = None,
) -> list[tuple[datetime, datetime]]:
    rows = connection.execute(
        text(
            """SELECT start_at, end_at FROM appointment
               WHERE technician_id = :technician_id AND status = 'DA_HEN'
                 AND start_at < :close_at AND :open_at < end_at
                 AND appointment_id IS DISTINCT FROM :exclude_id"""
        ),
        {"technician_id": technician_id, "open_at": open_at, "close_at": close_at,
         "exclude_id": exclude_id},
    ).all()
    return [(row[0], row[1]) for row in rows]


def insert_appointment(connection: Connection, values: dict[str, Any]) -> dict[str, Any]:
    try:
        row = connection.execute(
            text(
                f"""INSERT INTO appointment
                    (ticket_id, technician_id, appointment_type, start_at, end_at,
                     status, note, created_by)
                    VALUES (:ticket_id, :technician_id, :appointment_type, :start_at,
                            :end_at, 'DA_HEN', :note, :created_by)
                    RETURNING {COLUMNS}"""
            ),
            values,
        ).mappings().one()
    except IntegrityError as error:
        _raise_overlap(error)
    return dict(row)


def get_appointment(
    connection: Connection, appointment_id: int, lock: bool = False
) -> dict[str, Any] | None:
    suffix = " FOR UPDATE" if lock else ""
    row = connection.execute(
        text(f"SELECT {COLUMNS} FROM appointment WHERE appointment_id = :id{suffix}"),
        {"id": appointment_id},
    ).mappings().first()
    return dict(row) if row else None


def list_for_ticket(connection: Connection, ticket_id: int) -> list[dict[str, Any]]:
    rows = connection.execute(
        text(
            """SELECT appointment_id, ticket_id, technician_id, appointment_type,
                      start_at, end_at, status, note
               FROM appointment WHERE ticket_id = :ticket_id
               ORDER BY start_at, appointment_id"""
        ),
        {"ticket_id": ticket_id},
    ).mappings().all()
    return [dict(row) for row in rows]


def list_appointments(
    connection: Connection, *, center_id: int | None, technician_id: int | None,
    status: str | None, ticket_id: int | None, limit: int, offset: int,
) -> tuple[int, list[dict[str, Any]]]:
    """Appointments of one center (manager) or of one technician, newest start first."""
    filters = ["TRUE"]
    params: dict[str, Any] = {"limit": limit, "offset": offset}
    for column, value, name in (
        ("t.center_id", center_id, "center_id"),
        ("a.technician_id", technician_id, "technician_id"),
        ("a.status", status, "status"),
        ("a.ticket_id", ticket_id, "ticket_id"),
    ):
        if value is not None:
            filters.append(f"{column} = :{name}")
            params[name] = value
    where = " AND ".join(filters)
    base = f"FROM appointment a JOIN ticket t ON t.ticket_id = a.ticket_id WHERE {where}"
    total = connection.execute(text(f"SELECT count(*) {base}"), params).scalar_one()
    rows = connection.execute(
        text(
            f"""SELECT a.appointment_id, a.ticket_id, t.ticket_code, a.technician_id,
                       a.appointment_type, a.start_at, a.end_at, a.status, a.note
                {base} ORDER BY a.start_at DESC, a.appointment_id
                LIMIT :limit OFFSET :offset"""
        ),
        params,
    ).mappings().all()
    return total, [dict(row) for row in rows]


def update_appointment(
    connection: Connection, appointment_id: int, values: dict[str, Any]
) -> dict[str, Any]:
    try:
        row = connection.execute(
            text(
                f"""UPDATE appointment SET technician_id = :technician_id,
                           appointment_type = :appointment_type,
                           start_at = :start_at, end_at = :end_at, note = :note
                    WHERE appointment_id = :id RETURNING {COLUMNS}"""
            ),
            {**values, "id": appointment_id},
        ).mappings().one()
    except IntegrityError as error:
        _raise_overlap(error)
    return dict(row)


def cancel_appointment(connection: Connection, appointment_id: int) -> dict[str, Any]:
    """Soft delete (QT-13): the booking is marked DA_HUY, never removed."""
    row = connection.execute(
        text(
            f"""UPDATE appointment SET status = 'DA_HUY'
                WHERE appointment_id = :id RETURNING {COLUMNS}"""
        ),
        {"id": appointment_id},
    ).mappings().one()
    return dict(row)
