"""HTTP endpoints for tickets: parse the request, call the service, return its result."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query

from app.core.security import current_user, require_role
from app.schemas.tickets import (
    AssignmentRequest,
    StatusRequest,
    TechnicianChangeRequest,
    TicketRequest,
)
from app.services import appointment_service, ticket_service

router = APIRouter(prefix="/api/tickets", tags=["tickets"])
MANAGER = Depends(require_role("QUAN_LY"))
TECHNICIAN = Depends(require_role("KY_THUAT_VIEN"))


@router.get("")
def list_tickets(
    status: str = "MOI",
    category_code: str | None = None,
    priority: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    user: dict[str, Any] = MANAGER,
) -> dict[str, Any]:
    return ticket_service.list_tickets(
        user, status=status, category_code=category_code, priority=priority,
        page=page, page_size=page_size,
    )


@router.post("", status_code=201)
def create_ticket(payload: TicketRequest, user: dict[str, Any] = MANAGER) -> dict[str, Any]:
    return ticket_service.create_ticket(user, payload.model_dump())


@router.get("/{ticket_id}/technician-suggestions")
def technician_suggestions(ticket_id: int, user: dict[str, Any] = MANAGER) -> dict[str, Any]:
    return ticket_service.technician_suggestions(user, ticket_id)


@router.get("/{ticket_id}")
def get_ticket(ticket_id: int, user: dict[str, Any] = Depends(current_user)) -> dict[str, Any]:
    return ticket_service.get_ticket_detail(user, ticket_id)


@router.put("/{ticket_id}")
def update_ticket(
    ticket_id: int, payload: TicketRequest, user: dict[str, Any] = MANAGER
) -> dict[str, Any]:
    return ticket_service.update_ticket(user, ticket_id, payload.model_dump())


@router.delete("/{ticket_id}")
def cancel_ticket(
    ticket_id: int,
    reason: str | None = Query(default=None, max_length=255),
    user: dict[str, Any] = MANAGER,
) -> dict[str, Any]:
    return ticket_service.cancel_ticket(user, ticket_id, reason)


@router.post("/{ticket_id}/assignment", status_code=201)
def assign_ticket(
    ticket_id: int, payload: AssignmentRequest, user: dict[str, Any] = MANAGER
) -> dict[str, Any]:
    return ticket_service.assign_ticket(user, ticket_id, payload.technician_id)


@router.put("/{ticket_id}/assignment")
def change_assignment(
    ticket_id: int, payload: TechnicianChangeRequest, user: dict[str, Any] = MANAGER
) -> dict[str, Any]:
    return ticket_service.change_assignment(
        user, ticket_id, payload.technician_id, payload.reason
    )


@router.patch("/{ticket_id}/status")
def update_ticket_status(
    ticket_id: int, payload: StatusRequest, user: dict[str, Any] = TECHNICIAN
) -> dict[str, Any]:
    return ticket_service.update_status(user, ticket_id, payload.to_status, payload.note)


@router.get("/{ticket_id}/appointments")
def ticket_appointments(
    ticket_id: int, user: dict[str, Any] = Depends(current_user)
) -> list[dict[str, Any]]:
    return appointment_service.list_ticket_appointments(user, ticket_id)
