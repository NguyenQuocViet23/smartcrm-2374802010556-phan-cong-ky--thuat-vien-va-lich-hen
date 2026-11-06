"""SQL for tickets, technicians and the status log. No business rules here."""

from __future__ import annotations

from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import Connection

LIST_COLUMNS = (
    "ticket_id, ticket_code, center_id, customer_name, customer_phone, serial_no, "
    "issue_desc, category_code, priority, status, technician_id, received_at, due_date"
)


def get_ticket(connection: Connection, ticket_id: int, lock: bool = False) -> dict[str, Any] | None:
    suffix = " FOR UPDATE" if lock else ""
    row = connection.execute(
        text(f"SELECT * FROM ticket WHERE ticket_id = :ticket_id{suffix}"),
        {"ticket_id": ticket_id},
    ).mappings().first()
    return dict(row) if row else None


def get_technician_summary(connection: Connection, technician_id: int) -> dict[str, Any] | None:
    row = connection.execute(
        text(
            """SELECT technician_id, technician_code, full_name, level
               FROM technician WHERE technician_id = :technician_id"""
        ),
        {"technician_id": technician_id},
    ).mappings().first()
    return dict(row) if row else None


def get_technician_code(connection: Connection, technician_id: int | None) -> str | None:
    return connection.execute(
        text("SELECT technician_code FROM technician WHERE technician_id = :id"),
        {"id": technician_id},
    ).scalar_one_or_none()


def get_technician_with_skill(
    connection: Connection, technician_id: int, category_code: str
) -> dict[str, Any] | None:
    row = connection.execute(
        text(
            """SELECT t.technician_id, t.technician_code, t.center_id, t.is_active,
                      s.proficiency
               FROM technician t
               LEFT JOIN technician_skill s
                 ON s.technician_id = t.technician_id
                AND s.category_code = :category_code
               WHERE t.technician_id = :technician_id"""
        ),
        {"technician_id": technician_id, "category_code": category_code},
    ).mappings().first()
    return dict(row) if row else None


def list_history(connection: Connection, ticket_id: int) -> list[dict[str, Any]]:
    rows = connection.execute(
        text(
            """SELECT l.log_id, l.event_type, l.from_status, l.to_status,
                      l.from_technician_id, old.technician_code AS from_technician_code,
                      l.to_technician_id, new.technician_code AS to_technician_code,
                      l.changed_by, l.changed_at, l.note
               FROM ticket_status_log l
               LEFT JOIN technician old ON old.technician_id = l.from_technician_id
               LEFT JOIN technician new ON new.technician_id = l.to_technician_id
               WHERE l.ticket_id = :ticket_id
               ORDER BY l.changed_at, l.log_id"""
        ),
        {"ticket_id": ticket_id},
    ).mappings().all()
    return [dict(row) for row in rows]


def list_tickets(
    connection: Connection,
    *,
    center_id: int,
    status: str,
    category_code: str | None,
    priority: str | None,
    limit: int,
    offset: int,
) -> tuple[int, list[dict[str, Any]]]:
    filters = ["center_id = :center_id", "status = :status"]
    params: dict[str, Any] = {
        "center_id": center_id, "status": status, "limit": limit, "offset": offset,
    }
    if category_code:
        filters.append("category_code = :category_code")
        params["category_code"] = category_code
    if priority:
        filters.append("priority = :priority")
        params["priority"] = priority
    where = " AND ".join(filters)
    total = connection.execute(text(f"SELECT count(*) FROM ticket WHERE {where}"), params).scalar_one()
    rows = connection.execute(
        text(
            f"""SELECT {LIST_COLUMNS} FROM ticket WHERE {where}
                ORDER BY CASE priority WHEN 'CAO' THEN 1
                     WHEN 'TRUNG_BINH' THEN 2 ELSE 3 END, due_date, ticket_id
                LIMIT :limit OFFSET :offset"""
        ),
        params,
    ).mappings().all()
    return total, [dict(row) for row in rows]


def list_for_technician(connection: Connection, technician_id: int) -> list[dict[str, Any]]:
    rows = connection.execute(
        text(
            """SELECT ticket_id, ticket_code, customer_name, customer_phone,
                      serial_no, issue_desc, category_code, priority, status,
                      received_at, due_date, technician_id
               FROM ticket WHERE technician_id = :technician_id
               ORDER BY due_date, ticket_id"""
        ),
        {"technician_id": technician_id},
    ).mappings().all()
    return [dict(row) for row in rows]


def list_suggestions(
    connection: Connection, center_id: int, category_code: str
) -> list[dict[str, Any]]:
    """Active technicians of the center with skill >= 3, least loaded first."""
    rows = connection.execute(
        text(
            """SELECT t.technician_id, t.technician_code, t.full_name, t.level,
                      s.proficiency,
                      count(work.ticket_id)::integer AS workload
               FROM technician t
               JOIN technician_skill s ON s.technician_id = t.technician_id
               LEFT JOIN ticket work
                 ON work.technician_id = t.technician_id
                AND work.status IN ('DA_PHAN_CONG', 'DANG_XU_LY', 'CHO_LINH_KIEN')
               WHERE t.center_id = :center_id AND t.is_active = true
                 AND s.category_code = :category_code AND s.proficiency >= 3
               GROUP BY t.technician_id, t.technician_code, t.full_name,
                        t.level, s.proficiency
               ORDER BY workload, s.proficiency DESC, t.technician_code"""
        ),
        {"center_id": center_id, "category_code": category_code},
    ).mappings().all()
    return [dict(row) for row in rows]


def assign_technician(connection: Connection, ticket_id: int, technician_id: int) -> dict[str, Any]:
    row = connection.execute(
        text(
            """UPDATE ticket SET technician_id = :technician_id, status = 'DA_PHAN_CONG'
               WHERE ticket_id = :ticket_id RETURNING ticket_id, status, technician_id"""
        ),
        {"technician_id": technician_id, "ticket_id": ticket_id},
    ).mappings().one()
    return dict(row)


def log_assignment(
    connection: Connection, ticket_id: int, technician_id: int, changed_by: int
) -> Any:
    """Record MOI -> DA_PHAN_CONG and return the time it happened."""
    return connection.execute(
        text(
            """INSERT INTO ticket_status_log
               (ticket_id, event_type, from_status, to_status, to_technician_id,
                changed_by, changed_at)
               VALUES (:ticket_id, 'TRANG_THAI', 'MOI', 'DA_PHAN_CONG',
                       :technician_id, :changed_by, now())
               RETURNING changed_at"""
        ),
        {"ticket_id": ticket_id, "technician_id": technician_id, "changed_by": changed_by},
    ).scalar_one()


def replace_technician(connection: Connection, ticket_id: int, new_technician_id: int) -> None:
    connection.execute(
        text("UPDATE ticket SET technician_id = :new_id WHERE ticket_id = :ticket_id"),
        {"new_id": new_technician_id, "ticket_id": ticket_id},
    )


def log_technician_change(
    connection: Connection, *, ticket_id: int, status: str, old_id: int, new_id: int,
    changed_by: int, reason: str,
) -> None:
    connection.execute(
        text(
            """INSERT INTO ticket_status_log
               (ticket_id, event_type, from_status, to_status, from_technician_id,
                to_technician_id, changed_by, note)
               VALUES (:ticket_id, 'DOI_KTV', :status, :status, :old_id,
                       :new_id, :changed_by, :reason)"""
        ),
        {"ticket_id": ticket_id, "status": status, "old_id": old_id, "new_id": new_id,
         "changed_by": changed_by, "reason": reason},
    )


def set_status(connection: Connection, ticket_id: int, status: str) -> dict[str, Any]:
    row = connection.execute(
        text(
            "UPDATE ticket SET status = :status WHERE ticket_id = :ticket_id "
            "RETURNING ticket_id, status, technician_id"
        ),
        {"status": status, "ticket_id": ticket_id},
    ).mappings().one()
    return dict(row)


def log_status_change(
    connection: Connection, *, ticket_id: int, previous: str | None, target: str,
    technician_id: int | None, changed_by: int, note: str | None,
) -> None:
    connection.execute(
        text(
            """INSERT INTO ticket_status_log
               (ticket_id, event_type, from_status, to_status, to_technician_id,
                changed_by, note)
               VALUES (:ticket_id, 'TRANG_THAI', :previous, :target, :technician_id,
                       :changed_by, :note)"""
        ),
        {"ticket_id": ticket_id, "previous": previous, "target": target,
         "technician_id": technician_id, "changed_by": changed_by, "note": note},
    )


# --- Create / update / cancel ---------------------------------------------------


def next_ticket_id(connection: Connection) -> int:
    return connection.execute(
        text("SELECT nextval(pg_get_serial_sequence('ticket', 'ticket_id'))")
    ).scalar_one()


def insert_ticket(connection: Connection, values: dict[str, Any]) -> dict[str, Any]:
    row = connection.execute(
        text(
            """INSERT INTO ticket
               (ticket_id, ticket_code, center_id, customer_name, customer_phone, serial_no,
                issue_desc, category_code, priority, status, received_at, due_date)
               VALUES (:ticket_id, :ticket_code, :center_id, :customer_name, :customer_phone,
                       :serial_no, :issue_desc, :category_code, :priority, 'MOI', now(),
                       :due_date)
               RETURNING *"""
        ),
        values,
    ).mappings().one()
    return dict(row)


def update_ticket(connection: Connection, ticket_id: int, values: dict[str, Any]) -> dict[str, Any]:
    row = connection.execute(
        text(
            """UPDATE ticket SET customer_name = :customer_name, customer_phone = :customer_phone,
                      serial_no = :serial_no, issue_desc = :issue_desc,
                      category_code = :category_code, priority = :priority, due_date = :due_date
               WHERE ticket_id = :ticket_id RETURNING *"""
        ),
        {**values, "ticket_id": ticket_id},
    ).mappings().one()
    return dict(row)


def cancel_ticket(connection: Connection, ticket_id: int) -> dict[str, Any]:
    """Soft delete (QT-13): the row stays, its status becomes DA_HUY."""
    row = connection.execute(
        text(
            """UPDATE ticket SET status = 'DA_HUY', closed_at = now()
               WHERE ticket_id = :ticket_id
               RETURNING ticket_id, ticket_code, status, closed_at"""
        ),
        {"ticket_id": ticket_id},
    ).mappings().one()
    return dict(row)
