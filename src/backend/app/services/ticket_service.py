"""Ticket use cases: list, detail, suggestions, assignment, status and CRUD.

Orchestrates repositories and business rules. It knows nothing about the web layer:
failures are raised as ``DomainError``.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
from typing import Any

from app.domain.errors import DomainError, ErrorKind
from app.repositories import ticket_repository as tickets
from app.repositories.db import read_connection, transaction
from app.services import ticket_rules as rules

User = Mapping[str, Any]
NO_SUGGESTION_MESSAGE = "Không có kỹ thuật viên cùng trung tâm đủ tay nghề từ 3 trở lên."


def _load(connection: Any, ticket_id: int, lock: bool = False) -> dict[str, Any]:
    ticket = tickets.get_ticket(connection, ticket_id, lock=lock)
    if ticket is None:
        raise DomainError(ErrorKind.NOT_FOUND, "TICKET_NOT_FOUND", "Không tìm thấy phiếu.")
    return ticket


def _eligible_technician(connection: Any, ticket: Mapping[str, Any], technician_id: int) -> dict[str, Any]:
    technician = tickets.get_technician_with_skill(connection, technician_id, ticket["category_code"])
    if technician is None:
        raise DomainError(ErrorKind.NOT_FOUND, "TECHNICIAN_NOT_FOUND", "Không tìm thấy kỹ thuật viên.")
    rules.check_technician_eligible(ticket, technician)
    return technician


# --- Read -------------------------------------------------------------------------


def list_tickets(
    user: User, *, status: str, category_code: str | None, priority: str | None,
    page: int, page_size: int,
) -> dict[str, Any]:
    rules.check_status_filter(status)
    if priority:
        rules.check_priority(priority)
    with read_connection() as connection:
        total, items = tickets.list_tickets(
            connection, center_id=user["center_id"], status=status,
            category_code=category_code, priority=priority,
            limit=page_size, offset=(page - 1) * page_size,
        )
    return {"items": items, "total": total, "page": page, "page_size": page_size}


def get_ticket_detail(user: User, ticket_id: int) -> dict[str, Any]:
    with read_connection() as connection:
        ticket = _load(connection, ticket_id)
        rules.check_ticket_scope(user, ticket)
        technician = (
            tickets.get_technician_summary(connection, ticket["technician_id"])
            if ticket["technician_id"] is not None else None
        )
        history = tickets.list_history(connection, ticket_id)
    result = dict(ticket)
    if user["role"] != "QUAN_LY":
        result["customer_phone"] = rules.mask_phone(result["customer_phone"])
    result["technician"] = technician
    result["status_history"] = history
    return result


def technician_suggestions(user: User, ticket_id: int) -> dict[str, Any]:
    with read_connection() as connection:
        ticket = _load(connection, ticket_id)
        rules.check_ticket_scope(user, ticket)
        suggestions = tickets.list_suggestions(
            connection, ticket["center_id"], ticket["category_code"]
        )
    result = {
        "ticket_id": ticket_id,
        "ticket_code": ticket["ticket_code"],
        "category": ticket["category_code"],
        "center_id": ticket["center_id"],
        "suggestions": suggestions,
    }
    if not suggestions:
        result["message"] = NO_SUGGESTION_MESSAGE
    return result


def my_tickets(user: User) -> list[dict[str, Any]]:
    """Every ticket of the technician (closed and cancelled ones included), phone masked."""
    with read_connection() as connection:
        rows = tickets.list_for_technician(connection, user["technician_id"])
    now = datetime.now(timezone.utc)
    for row in rows:
        row["customer_phone"] = rules.mask_phone(row["customer_phone"])
        row["is_overdue"] = row["due_date"] < now and row["status"] not in rules.CLOSED_STATUSES
    return rows


# --- Assignment and status ----------------------------------------------------------


def assign_ticket(user: User, ticket_id: int, technician_id: int) -> dict[str, Any]:
    with transaction() as connection:
        ticket = _load(connection, ticket_id, lock=True)
        rules.check_ticket_scope(user, ticket)
        if not rules.is_assignable(ticket):
            current = tickets.get_technician_code(connection, ticket["technician_id"])
            raise DomainError(
                ErrorKind.CONFLICT,
                "TICKET_ALREADY_ASSIGNED",
                f"Phiếu đã được phân công{f' cho kỹ thuật viên {current}' if current else ''}.",
            )
        _eligible_technician(connection, ticket, technician_id)
        updated = tickets.assign_technician(connection, ticket_id, technician_id)
        changed_at = tickets.log_assignment(connection, ticket_id, technician_id, user["employee_id"])
    return {**updated, "assigned_by": user["employee_id"], "assigned_at": changed_at}


def change_assignment(user: User, ticket_id: int, technician_id: int, reason: str) -> dict[str, Any]:
    reason = rules.require_change_reason(reason)
    with transaction() as connection:
        ticket = _load(connection, ticket_id, lock=True)
        rules.check_ticket_scope(user, ticket)
        rules.check_technician_change(ticket, technician_id)
        _eligible_technician(connection, ticket, technician_id)
        tickets.replace_technician(connection, ticket_id, technician_id)
        tickets.log_technician_change(
            connection, ticket_id=ticket_id, status=ticket["status"],
            old_id=ticket["technician_id"], new_id=technician_id,
            changed_by=user["employee_id"], reason=reason,
        )
    return {"ticket_id": ticket_id, "status": ticket["status"], "technician_id": technician_id}


def update_status(user: User, ticket_id: int, to_status: str, note: str | None) -> dict[str, Any]:
    target = rules.normalize_target_status(to_status)
    with transaction() as connection:
        ticket = _load(connection, ticket_id, lock=True)
        rules.check_ticket_scope(user, ticket)
        rules.check_status_transition(ticket["status"], target)
        updated = tickets.set_status(connection, ticket_id, target)
        tickets.log_status_change(
            connection, ticket_id=ticket_id, previous=ticket["status"], target=target,
            technician_id=ticket["technician_id"], changed_by=user["employee_id"],
            note=note.strip() if note else None,
        )
    return updated


# --- Create / update / cancel (manager) ---------------------------------------------


def _clean_fields(data: Mapping[str, Any]) -> dict[str, Any]:
    """Validate and normalize the customer-facing fields shared by create and update."""
    text = rules.require_text_fields(data)
    rules.check_category(data["category_code"])
    rules.check_priority(data["priority"])
    return {
        "customer_name": text["customer_name"],
        "customer_phone": rules.normalize_phone(data["customer_phone"]),
        "serial_no": text["serial_no"],
        "issue_desc": text["issue_desc"],
        "category_code": data["category_code"],
        "priority": data["priority"],
        "due_date": data["due_date"],
    }


def create_ticket(user: User, data: Mapping[str, Any]) -> dict[str, Any]:
    """Open a new ticket (status MOI) in the manager's own center."""
    fields = _clean_fields(data)
    now = datetime.now(timezone.utc)
    rules.check_due_date_in_future(fields["due_date"], now)
    with transaction() as connection:
        ticket_id = tickets.next_ticket_id(connection)
        ticket = tickets.insert_ticket(connection, {
            **fields, "ticket_id": ticket_id, "center_id": user["center_id"],
            "ticket_code": f"BH-{ticket_id:06d}/{now.year}",
        })
        tickets.log_status_change(
            connection, ticket_id=ticket_id, previous=None, target="MOI", technician_id=None,
            changed_by=user["employee_id"], note="Tạo phiếu",
        )
    return ticket


def update_ticket(user: User, ticket_id: int, data: Mapping[str, Any]) -> dict[str, Any]:
    """Correct the data of a ticket that is still MOI."""
    fields = _clean_fields(data)
    with transaction() as connection:
        ticket = _load(connection, ticket_id, lock=True)
        rules.check_ticket_scope(user, ticket)
        rules.check_ticket_editable(ticket)
        if fields["due_date"] != ticket["due_date"]:
            rules.check_due_date_in_future(fields["due_date"], datetime.now(timezone.utc))
        return tickets.update_ticket(connection, ticket_id, fields)


def cancel_ticket(user: User, ticket_id: int, reason: str | None) -> dict[str, Any]:
    """Soft delete (QT-13): a ticket still MOI becomes DA_HUY and the change is logged."""
    with transaction() as connection:
        ticket = _load(connection, ticket_id, lock=True)
        rules.check_ticket_scope(user, ticket)
        rules.check_ticket_cancellable(ticket)
        cancelled = tickets.cancel_ticket(connection, ticket_id)
        tickets.log_status_change(
            connection, ticket_id=ticket_id, previous="MOI", target="DA_HUY",
            technician_id=None, changed_by=user["employee_id"],
            note=reason.strip() if reason and reason.strip() else "Hủy phiếu",
        )
    return cancelled
