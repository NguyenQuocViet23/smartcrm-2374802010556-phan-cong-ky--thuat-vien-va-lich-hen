"""Business rules for ticket assignment and status changes.

Every function here works on plain mappings and never touches the database,
so the rules can be unit-tested without PostgreSQL.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from app.core.errors import APIError

VALID_STATUSES = {
    "MOI", "DA_PHAN_CONG", "DANG_XU_LY", "CHO_LINH_KIEN",
    "HOAN_TAT", "DA_DONG", "DA_HUY",
}
# Technicians may only move a ticket forward along this lifecycle.
TRANSITIONS = {
    "DA_PHAN_CONG": {"DANG_XU_LY"},
    "DANG_XU_LY": {"CHO_LINH_KIEN", "HOAN_TAT"},
    "CHO_LINH_KIEN": {"HOAN_TAT"},
}
TECHNICIAN_TARGET_STATUSES = {"DANG_XU_LY", "CHO_LINH_KIEN", "HOAN_TAT"}
CLOSED_STATUSES = {"HOAN_TAT", "DA_DONG", "DA_HUY"}
MIN_PROFICIENCY = 3


def normalize_target_status(raw_status: str) -> str:
    """Return the upper-case target status or reject one a technician cannot set."""
    target = raw_status.strip().upper()
    if target not in TECHNICIAN_TARGET_STATUSES:
        raise APIError(400, "INVALID_STATUS", "Trạng thái đích không hợp lệ.")
    return target


def check_status_transition(current: str, target: str) -> None:
    """Reject any status change that is not a forward step of the lifecycle."""
    if target not in TRANSITIONS.get(current, set()):
        raise APIError(
            409,
            "INVALID_STATUS_TRANSITION",
            f"Không thể chuyển từ {current} sang {target}.",
        )


def check_technician_eligible(
    ticket: Mapping[str, Any], technician: Mapping[str, Any]
) -> None:
    """A technician must be active, in the ticket's center and have skill >= 3."""
    proficiency = technician["proficiency"]
    if (
        technician["center_id"] != ticket["center_id"]
        or not technician["is_active"]
        or proficiency is None
        or proficiency < MIN_PROFICIENCY
    ):
        raise APIError(
            400,
            "TECHNICIAN_NOT_ELIGIBLE",
            f"Kỹ thuật viên không đủ điều kiện: tay nghề {ticket['category_code']} "
            f"= {proficiency if proficiency is not None else 'không có'} "
            f"(< {MIN_PROFICIENCY}) hoặc khác trung tâm/đã nghỉ việc.",
        )


def is_assignable(ticket: Mapping[str, Any]) -> bool:
    """Only a new, unassigned ticket can receive its first technician."""
    return ticket["status"] == "MOI" and ticket["technician_id"] is None


def require_change_reason(reason: str) -> str:
    """A technician change must state a non-blank reason; return it trimmed."""
    trimmed = reason.strip()
    if not trimmed:
        raise APIError(400, "REASON_REQUIRED", "Lý do đổi kỹ thuật viên là bắt buộc.")
    return trimmed


def check_technician_change(ticket: Mapping[str, Any], new_technician_id: int) -> None:
    """Only an assigned, still-open ticket can move to a different technician."""
    if ticket["status"] in CLOSED_STATUSES:
        raise APIError(
            409, "TICKET_NOT_CHANGEABLE", "Không thể đổi kỹ thuật viên cho phiếu đã kết thúc."
        )
    if ticket["technician_id"] is None:
        raise APIError(409, "TICKET_NOT_ASSIGNED", "Phiếu chưa được phân công.")
    if ticket["technician_id"] == new_technician_id:
        raise APIError(400, "SAME_TECHNICIAN", "Kỹ thuật viên mới phải khác người hiện tại.")
