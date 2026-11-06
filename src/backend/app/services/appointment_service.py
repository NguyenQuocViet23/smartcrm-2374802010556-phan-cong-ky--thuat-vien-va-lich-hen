"""Appointment use cases: book, read, reschedule and cancel.

Orchestrates repositories and business rules. It knows nothing about the web layer:
failures are raised as ``DomainError``.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from typing import Any

from app.domain.errors import DomainError, ErrorKind
from app.repositories import appointment_repository as appointments
from app.repositories import ticket_repository as tickets
from app.repositories.appointment_repository import OverlapViolation
from app.repositories.db import read_connection, transaction
from app.services import appointment_rules as rules
from app.services.ticket_rules import check_ticket_scope

User = Mapping[str, Any]
APPOINTMENT_STATUSES = {"DA_HEN", "DA_HUY"}


def _load_ticket(connection: Any, ticket_id: int) -> dict[str, Any]:
    ticket = tickets.get_ticket(connection, ticket_id)
    if ticket is None:
        raise DomainError(ErrorKind.NOT_FOUND, "TICKET_NOT_FOUND", "Không tìm thấy phiếu.")
    return ticket


def _load_appointment(connection: Any, appointment_id: int, lock: bool = False) -> dict[str, Any]:
    appointment = appointments.get_appointment(connection, appointment_id, lock=lock)
    if appointment is None:
        raise DomainError(
            ErrorKind.NOT_FOUND, "APPOINTMENT_NOT_FOUND", "Không tìm thấy lịch hẹn."
        )
    return appointment


def _free_slots(
    connection: Any, technician_id: int, start: datetime, exclude_id: int | None = None
) -> list[dict[str, str]]:
    open_at = datetime.combine(start.date(), rules.OPENING, tzinfo=rules.LOCAL_TIME)
    close_at = datetime.combine(start.date(), rules.CLOSING, tzinfo=rules.LOCAL_TIME)
    busy = appointments.busy_intervals(connection, technician_id, open_at, close_at, exclude_id)
    return rules.find_free_slots(busy, start)


def _overlap_error(conflicts: list[dict[str, Any]], slots: list[dict[str, str]]) -> DomainError:
    return DomainError(
        ErrorKind.CONFLICT,
        "APPOINTMENT_OVERLAP",
        "Kỹ thuật viên đã có lịch trong khung giờ này.",
        conflicts=conflicts,
        free_slots=slots,
    )


def _conflict_after_race(technician_id: int, start: datetime, end: datetime,
                         exclude_id: int | None = None) -> DomainError:
    """The database overlap constraint fired: build the same answer from a fresh read."""
    with read_connection() as connection:
        conflicts = appointments.find_overlaps(connection, technician_id, start, end, exclude_id)
        slots = _free_slots(connection, technician_id, start, exclude_id)
    return _overlap_error(conflicts, slots)


# --- Read -------------------------------------------------------------------------


def list_ticket_appointments(user: User, ticket_id: int) -> list[dict[str, Any]]:
    with read_connection() as connection:
        ticket = _load_ticket(connection, ticket_id)
        check_ticket_scope(user, ticket)
        return appointments.list_for_ticket(connection, ticket_id)


def get_appointment(user: User, appointment_id: int) -> dict[str, Any]:
    with read_connection() as connection:
        appointment = _load_appointment(connection, appointment_id)
        check_ticket_scope(user, _load_ticket(connection, appointment["ticket_id"]))
    return appointment


def list_appointments(
    user: User, *, status: str | None, ticket_id: int | None, page: int, page_size: int
) -> dict[str, Any]:
    """A manager sees the appointments of the center, a technician only their own."""
    if status is not None and status not in APPOINTMENT_STATUSES:
        raise DomainError(ErrorKind.INVALID, "INVALID_STATUS", "Trạng thái lịch hẹn không hợp lệ.")
    is_manager = user["role"] == "QUAN_LY"
    with read_connection() as connection:
        total, items = appointments.list_appointments(
            connection,
            center_id=user["center_id"] if is_manager else None,
            technician_id=None if is_manager else user["technician_id"],
            status=status, ticket_id=ticket_id,
            limit=page_size, offset=(page - 1) * page_size,
        )
    return {"items": items, "total": total, "page": page, "page_size": page_size}


# --- Create / update / cancel -----------------------------------------------------


def create_appointment(
    user: User, *, ticket_id: int, appointment_type: str, start_at: datetime,
    end_at: datetime, note: str | None,
) -> dict[str, Any]:
    start, end = rules.validate_slot(start_at, end_at)
    technician_id = None
    try:
        with transaction() as connection:
            ticket = tickets.get_ticket(connection, ticket_id, lock=True)
            if ticket is None:
                raise DomainError(ErrorKind.NOT_FOUND, "TICKET_NOT_FOUND", "Không tìm thấy phiếu.")
            check_ticket_scope(user, ticket)
            rules.check_ticket_accepts_appointment(ticket)
            technician_id = ticket["technician_id"]
            conflicts = appointments.find_overlaps(connection, technician_id, start, end)
            if conflicts:
                raise _overlap_error(conflicts, _free_slots(connection, technician_id, start))
            return appointments.insert_appointment(connection, {
                "ticket_id": ticket_id, "technician_id": technician_id,
                "appointment_type": appointment_type, "start_at": start, "end_at": end,
                "note": note, "created_by": user["employee_id"],
            })
    except OverlapViolation:
        raise _conflict_after_race(technician_id, start, end) from None


def update_appointment(
    user: User, appointment_id: int, *, appointment_type: str, start_at: datetime,
    end_at: datetime, note: str | None,
) -> dict[str, Any]:
    """Reschedule a booked appointment; it follows the ticket's current technician."""
    start, end = rules.validate_slot(start_at, end_at)
    technician_id = None
    try:
        with transaction() as connection:
            appointment = _load_appointment(connection, appointment_id, lock=True)
            ticket = _load_ticket(connection, appointment["ticket_id"])
            check_ticket_scope(user, ticket)
            rules.check_appointment_editable(appointment)
            rules.check_ticket_accepts_appointment(ticket)
            technician_id = ticket["technician_id"]
            conflicts = appointments.find_overlaps(
                connection, technician_id, start, end, exclude_id=appointment_id
            )
            if conflicts:
                raise _overlap_error(
                    conflicts, _free_slots(connection, technician_id, start, appointment_id)
                )
            return appointments.update_appointment(connection, appointment_id, {
                "technician_id": technician_id, "appointment_type": appointment_type,
                "start_at": start, "end_at": end, "note": note,
            })
    except OverlapViolation:
        raise _conflict_after_race(technician_id, start, end, appointment_id) from None


def cancel_appointment(user: User, appointment_id: int) -> dict[str, Any]:
    """Soft delete (QT-13): the appointment is marked DA_HUY and frees its time slot."""
    with transaction() as connection:
        appointment = _load_appointment(connection, appointment_id, lock=True)
        check_ticket_scope(user, _load_ticket(connection, appointment["ticket_id"]))
        rules.check_appointment_cancellable(appointment)
        return appointments.cancel_appointment(connection, appointment_id)
