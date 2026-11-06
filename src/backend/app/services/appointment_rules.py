"""Business rules for appointments: working hours, state checks and free slots.

Pure functions: no database, no web layer.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from datetime import datetime, time, timedelta, timezone
from typing import Any

from app.domain.errors import DomainError, ErrorKind
from app.services.ticket_rules import CLOSED_STATUSES

LOCAL_TIME = timezone(timedelta(hours=7))
OPENING = time(8)
CLOSING = time(18)
SLOT = timedelta(minutes=30)


def to_local(value: datetime) -> datetime:
    if value.tzinfo is None:
        raise DomainError(ErrorKind.INVALID, "INVALID_DATETIME", "Thời gian phải có múi giờ.")
    return value.astimezone(LOCAL_TIME)


def validate_slot(start: datetime, end: datetime) -> tuple[datetime, datetime]:
    """Check an appointment lies in the future, Monday–Saturday, 08:00–18:00."""
    start_local, end_local = to_local(start), to_local(end)
    if end_local <= start_local:
        raise DomainError(
            ErrorKind.INVALID, "INVALID_TIME_RANGE", "Giờ kết thúc phải sau giờ bắt đầu."
        )
    if start_local <= datetime.now(LOCAL_TIME):
        raise DomainError(
            ErrorKind.INVALID, "PAST_APPOINTMENT", "Thời điểm hẹn phải ở tương lai."
        )
    if start_local.date() != end_local.date() or start_local.weekday() == 6:
        raise DomainError(
            ErrorKind.INVALID, "OUTSIDE_WORKING_HOURS", "Lịch hẹn phải trong ngày làm việc."
        )
    opening = datetime.combine(start_local.date(), OPENING, tzinfo=LOCAL_TIME)
    closing = datetime.combine(start_local.date(), CLOSING, tzinfo=LOCAL_TIME)
    if start_local < opening or end_local > closing:
        raise DomainError(
            ErrorKind.INVALID, "OUTSIDE_WORKING_HOURS", "Giờ làm việc là 08:00–18:00."
        )
    return start_local, end_local


def check_ticket_accepts_appointment(ticket: Mapping[str, Any]) -> None:
    """A ticket needs a technician and must not be finished before it can be booked."""
    if ticket["technician_id"] is None:
        raise DomainError(
            ErrorKind.INVALID,
            "TICKET_NOT_ASSIGNED",
            "Phiếu cần được phân công kỹ thuật viên trước khi đặt lịch.",
        )
    if ticket["status"] in CLOSED_STATUSES:
        raise DomainError(
            ErrorKind.INVALID, "TICKET_CLOSED", "Không thể đặt lịch cho phiếu đã kết thúc."
        )


def check_appointment_active(appointment: Mapping[str, Any], code: str, message: str) -> None:
    """Only a booked (DA_HEN) appointment can be changed or cancelled."""
    if appointment["status"] != "DA_HEN":
        raise DomainError(ErrorKind.CONFLICT, code, message)


def check_appointment_editable(appointment: Mapping[str, Any]) -> None:
    check_appointment_active(
        appointment, "APPOINTMENT_NOT_EDITABLE", "Chỉ sửa được lịch hẹn đang ở trạng thái ĐÃ HẸN."
    )


def check_appointment_cancellable(appointment: Mapping[str, Any]) -> None:
    check_appointment_active(
        appointment, "APPOINTMENT_NOT_CANCELLABLE", "Lịch hẹn này đã được hủy trước đó."
    )


def find_free_slots(
    busy: Iterable[tuple[datetime, datetime]], requested_start: datetime, limit: int = 2
) -> list[dict[str, str]]:
    """The free 30-minute slots of the requested day nearest to the requested start."""
    day = requested_start.date()
    open_at = datetime.combine(day, OPENING, tzinfo=LOCAL_TIME)
    close_at = datetime.combine(day, CLOSING, tzinfo=LOCAL_TIME)
    busy = list(busy)
    slots: list[tuple[datetime, datetime]] = []
    cursor = open_at
    while cursor + SLOT <= close_at:
        end = cursor + SLOT
        if all(not (begin < end and cursor < finish) for begin, finish in busy):
            slots.append((cursor, end))
        cursor = end
    nearest = sorted(
        slots,
        key=lambda slot: (abs((slot[0] - requested_start).total_seconds()), slot[0]),
    )[:limit]
    return [
        {"start_at": start.isoformat(), "end_at": end.isoformat()} for start, end in nearest
    ]
