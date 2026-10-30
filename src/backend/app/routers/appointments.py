"""Appointment creation with working-hour and overlap validation."""

from __future__ import annotations

from datetime import datetime, time, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.core.database import get_engine
from app.core.errors import APIError
from app.core.security import current_user
from app.routers.tickets import _check_scope, _ticket
from app.schemas.tickets import AppointmentRequest

router = APIRouter(prefix="/api/appointments", tags=["appointments"])
LOCAL_TIME = timezone(timedelta(hours=7))


def _local(value: datetime) -> datetime:
    if value.tzinfo is None:
        raise APIError(400, "INVALID_DATETIME", "Thời gian phải có múi giờ.")
    return value.astimezone(LOCAL_TIME)


def _validate_slot(start: datetime, end: datetime) -> tuple[datetime, datetime]:
    start_local, end_local = _local(start), _local(end)
    if end_local <= start_local:
        raise APIError(400, "INVALID_TIME_RANGE", "Giờ kết thúc phải sau giờ bắt đầu.")
    if start_local <= datetime.now(LOCAL_TIME):
        raise APIError(400, "PAST_APPOINTMENT", "Thời điểm hẹn phải ở tương lai.")
    if start_local.date() != end_local.date() or start_local.weekday() == 6:
        raise APIError(400, "OUTSIDE_WORKING_HOURS", "Lịch hẹn phải trong ngày làm việc.")
    opening = datetime.combine(start_local.date(), time(8), tzinfo=LOCAL_TIME)
    closing = datetime.combine(start_local.date(), time(18), tzinfo=LOCAL_TIME)
    if start_local < opening or end_local > closing:
        raise APIError(400, "OUTSIDE_WORKING_HOURS", "Giờ làm việc là 08:00–18:00.")
    return start_local, end_local


def _overlaps(connection: Any, technician_id: int, start: datetime, end: datetime):
    return connection.execute(
        text(
            """SELECT a.appointment_id, t.ticket_code, a.start_at, a.end_at
               FROM appointment a JOIN ticket t ON t.ticket_id = a.ticket_id
               WHERE a.technician_id = :technician_id AND a.status = 'DA_HEN'
                 AND a.start_at < :end_at AND :start_at < a.end_at
               ORDER BY a.start_at"""
        ),
        {"technician_id": technician_id, "start_at": start, "end_at": end},
    ).mappings().all()


def _free_slots(
    connection: Any, technician_id: int, requested_start: datetime
) -> list[dict[str, str]]:
    appointment_date = requested_start.date()
    open_at = datetime.combine(appointment_date, time(8), tzinfo=LOCAL_TIME)
    close_at = datetime.combine(appointment_date, time(18), tzinfo=LOCAL_TIME)
    busy = connection.execute(
        text(
            """SELECT start_at, end_at FROM appointment
               WHERE technician_id = :technician_id AND status = 'DA_HEN'
                 AND start_at < :close_at AND :open_at < end_at"""
        ),
        {"technician_id": technician_id, "open_at": open_at, "close_at": close_at},
    ).all()
    slots: list[tuple[datetime, datetime]] = []
    cursor = open_at
    while cursor + timedelta(minutes=30) <= close_at:
        end = cursor + timedelta(minutes=30)
        if all(not (begin < end and cursor < finish) for begin, finish in busy):
            slots.append((cursor, end))
        cursor = end
    nearest = sorted(
        slots,
        key=lambda slot: (abs((slot[0] - requested_start).total_seconds()), slot[0]),
    )[:2]
    return [
        {"start_at": start.isoformat(), "end_at": end.isoformat()}
        for start, end in nearest
    ]


def _overlap_error(conflicts: list[dict[str, Any]], slots: list[dict[str, str]]) -> APIError:
    return APIError(
        409,
        "APPOINTMENT_OVERLAP",
        "Kỹ thuật viên đã có lịch trong khung giờ này.",
        conflicts=conflicts,
        free_slots=slots,
    )


@router.post("", status_code=201)
def create_appointment(
    payload: AppointmentRequest,
    user: dict[str, Any] = Depends(current_user),
) -> dict[str, Any]:
    start, end = _validate_slot(payload.start_at, payload.end_at)
    try:
        with get_engine().begin() as connection:
            ticket = _ticket(connection, payload.ticket_id, lock=True)
            _check_scope(user, ticket)
            if ticket["technician_id"] is None:
                raise APIError(
                    400,
                    "TICKET_NOT_ASSIGNED",
                    "Phiếu cần được phân công kỹ thuật viên trước khi đặt lịch.",
                )
            if ticket["status"] in {"HOAN_TAT", "DA_DONG", "DA_HUY"}:
                raise APIError(400, "TICKET_CLOSED", "Không thể đặt lịch cho phiếu đã kết thúc.")
            conflicts = [
                dict(row)
                for row in _overlaps(connection, ticket["technician_id"], start, end)
            ]
            if conflicts:
                raise _overlap_error(
                    conflicts,
                    _free_slots(connection, ticket["technician_id"], start),
                )
            row = connection.execute(
                text(
                    """INSERT INTO appointment
                       (ticket_id, technician_id, appointment_type, start_at, end_at,
                        status, note, created_by)
                       VALUES (:ticket_id, :technician_id, :appointment_type, :start_at,
                               :end_at, 'DA_HEN', :note, :created_by)
                       RETURNING appointment_id, ticket_id, technician_id, appointment_type,
                                 start_at, end_at, status, note"""
                ),
                {
                    "ticket_id": payload.ticket_id,
                    "technician_id": ticket["technician_id"],
                    "appointment_type": payload.appointment_type,
                    "start_at": start,
                    "end_at": end,
                    "note": payload.note,
                    "created_by": user["employee_id"],
                },
            ).mappings().one()
        return dict(row)
    except IntegrityError as exc:
        if getattr(exc.orig, "sqlstate", None) != "23P01":
            raise
        with get_engine().connect() as connection:
            ticket = _ticket(connection, payload.ticket_id)
            conflicts = [
                dict(row)
                for row in _overlaps(connection, ticket["technician_id"], start, end)
            ]
            slots = _free_slots(connection, ticket["technician_id"], start)
        raise _overlap_error(conflicts, slots) from exc
