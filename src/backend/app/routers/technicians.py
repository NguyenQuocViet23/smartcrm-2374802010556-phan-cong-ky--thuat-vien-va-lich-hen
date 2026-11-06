"""HTTP endpoint for the technician's own tickets."""

from typing import Any

from fastapi import APIRouter, Depends

from app.core.security import require_role
from app.services import ticket_service

router = APIRouter(prefix="/api/technicians", tags=["technicians"])


@router.get("/me/tickets")
def my_tickets(
    user: dict[str, Any] = Depends(require_role("KY_THUAT_VIEN")),
) -> list[dict[str, Any]]:
    return ticket_service.my_tickets(user)
