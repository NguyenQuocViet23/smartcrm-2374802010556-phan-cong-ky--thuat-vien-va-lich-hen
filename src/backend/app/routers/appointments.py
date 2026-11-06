"""HTTP endpoints for appointments: parse the request, call the service, return its result."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query

from app.core.security import current_user
from app.schemas.tickets import AppointmentRequest, AppointmentUpdateRequest
from app.services import appointment_service

router = APIRouter(prefix="/api/appointments", tags=["appointments"])


@router.post("", status_code=201)
def create_appointment(
    payload: AppointmentRequest, user: dict[str, Any] = Depends(current_user)
) -> dict[str, Any]:
    return appointment_service.create_appointment(
        user, ticket_id=payload.ticket_id, appointment_type=payload.appointment_type,
        start_at=payload.start_at, end_at=payload.end_at, note=payload.note,
    )


@router.get("")
def list_appointments(
    status: str | None = None,
    ticket_id: int | None = Query(default=None, gt=0),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    user: dict[str, Any] = Depends(current_user),
) -> dict[str, Any]:
    return appointment_service.list_appointments(
        user, status=status, ticket_id=ticket_id, page=page, page_size=page_size
    )


@router.get("/{appointment_id}")
def get_appointment(
    appointment_id: int, user: dict[str, Any] = Depends(current_user)
) -> dict[str, Any]:
    return appointment_service.get_appointment(user, appointment_id)


@router.put("/{appointment_id}")
def update_appointment(
    appointment_id: int, payload: AppointmentUpdateRequest,
    user: dict[str, Any] = Depends(current_user),
) -> dict[str, Any]:
    return appointment_service.update_appointment(
        user, appointment_id, appointment_type=payload.appointment_type,
        start_at=payload.start_at, end_at=payload.end_at, note=payload.note,
    )


@router.delete("/{appointment_id}")
def cancel_appointment(
    appointment_id: int, user: dict[str, Any] = Depends(current_user)
) -> dict[str, Any]:
    return appointment_service.cancel_appointment(user, appointment_id)
