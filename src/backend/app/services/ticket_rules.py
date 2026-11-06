"""Business rules for tickets: visibility, assignment, status lifecycle and CRUD.

Every function here works on plain mappings and never touches the database or
the web layer, so the rules can be unit-tested without PostgreSQL or a server.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from datetime import datetime
from typing import Any

from app.domain.errors import DomainError, ErrorKind

VALID_STATUSES = {
    "MOI", "DA_PHAN_CONG", "DANG_XU_LY", "CHO_LINH_KIEN",
    "HOAN_TAT", "DA_DONG", "DA_HUY",
}
VALID_PRIORITIES = {"CAO", "TRUNG_BINH", "THAP"}
VALID_CATEGORIES = {"MAN_HINH", "PIN", "SAC", "PHAN_MEM", "NUOC_VAO", "KHAC"}
# Technicians may only move a ticket forward along this lifecycle.
TRANSITIONS = {
    "DA_PHAN_CONG": {"DANG_XU_LY"},
    "DANG_XU_LY": {"CHO_LINH_KIEN", "HOAN_TAT"},
    "CHO_LINH_KIEN": {"HOAN_TAT"},
}
TECHNICIAN_TARGET_STATUSES = {"DANG_XU_LY", "CHO_LINH_KIEN", "HOAN_TAT"}
CLOSED_STATUSES = {"HOAN_TAT", "DA_DONG", "DA_HUY"}
MIN_PROFICIENCY = 3


def check_ticket_scope(user: Mapping[str, Any], ticket: Mapping[str, Any]) -> None:
    """A manager sees only tickets of their center; a technician only their own tickets.

    Closed (DA_DONG) and cancelled (DA_HUY) tickets stay visible to their owner.
    """
    if user["role"] == "QUAN_LY" and ticket["center_id"] != user["center_id"]:
        raise DomainError(
            ErrorKind.FORBIDDEN, "FORBIDDEN", "Bạn không có quyền xem phiếu của trung tâm này"
        )
    if (
        user["role"] == "KY_THUAT_VIEN"
        and ticket["technician_id"] != user.get("technician_id")
    ):
        raise DomainError(
            ErrorKind.FORBIDDEN,
            "FORBIDDEN",
            "Bạn không phải kỹ thuật viên phụ trách phiếu này",
        )


def mask_phone(phone: str) -> str:
    """Technicians see 3 leading + 3 trailing digits only (QT-14)."""
    return f"{phone[:3]}****{phone[-3:]}"


def normalize_target_status(raw_status: str) -> str:
    """Return the upper-case target status or reject one a technician cannot set."""
    target = raw_status.strip().upper()
    if target not in TECHNICIAN_TARGET_STATUSES:
        raise DomainError(ErrorKind.INVALID, "INVALID_STATUS", "Trạng thái đích không hợp lệ.")
    return target


def check_status_filter(status: str) -> None:
    if status not in VALID_STATUSES:
        raise DomainError(ErrorKind.INVALID, "INVALID_STATUS", "Trạng thái phiếu không hợp lệ.")


def check_priority(priority: str) -> None:
    if priority not in VALID_PRIORITIES:
        raise DomainError(ErrorKind.INVALID, "INVALID_PRIORITY", "Mức ưu tiên không hợp lệ.")


def check_category(category_code: str) -> None:
    if category_code not in VALID_CATEGORIES:
        raise DomainError(ErrorKind.INVALID, "INVALID_CATEGORY", "Nhóm sự cố không hợp lệ.")


def check_status_transition(current: str, target: str) -> None:
    """Reject any status change that is not a forward step of the lifecycle."""
    if target not in TRANSITIONS.get(current, set()):
        raise DomainError(
            ErrorKind.CONFLICT,
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
        raise DomainError(
            ErrorKind.INVALID,
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
        raise DomainError(
            ErrorKind.INVALID, "REASON_REQUIRED", "Lý do đổi kỹ thuật viên là bắt buộc."
        )
    return trimmed


def check_technician_change(ticket: Mapping[str, Any], new_technician_id: int) -> None:
    """Only an assigned, still-open ticket can move to a different technician."""
    if ticket["status"] in CLOSED_STATUSES:
        raise DomainError(
            ErrorKind.CONFLICT,
            "TICKET_NOT_CHANGEABLE",
            "Không thể đổi kỹ thuật viên cho phiếu đã kết thúc.",
        )
    if ticket["technician_id"] is None:
        raise DomainError(ErrorKind.CONFLICT, "TICKET_NOT_ASSIGNED", "Phiếu chưa được phân công.")
    if ticket["technician_id"] == new_technician_id:
        raise DomainError(
            ErrorKind.INVALID, "SAME_TECHNICIAN", "Kỹ thuật viên mới phải khác người hiện tại."
        )


# --- Ticket CRUD rules ---------------------------------------------------------


def normalize_phone(raw: str) -> str:
    """Return a 10-digit phone starting with 0 (QT-02) or reject the input.

    Accepts spaces, dots, dashes, brackets and the +84 / 84 country prefix.
    """
    value = re.sub(r"[\s.\-()]", "", raw.strip())
    if value.startswith("+84"):
        value = "0" + value[3:]
    elif value.startswith("84"):
        value = "0" + value[2:]
    if not re.fullmatch(r"0[0-9]{9}", value):
        raise DomainError(
            ErrorKind.INVALID,
            "INVALID_PHONE",
            "Số điện thoại phải gồm 10 chữ số và bắt đầu bằng 0.",
        )
    return value


def check_due_date_in_future(due_date: datetime, now: datetime) -> None:
    """The committed due date of a new ticket must still lie ahead."""
    if due_date.tzinfo is None:
        raise DomainError(ErrorKind.INVALID, "INVALID_DATETIME", "Thời gian phải có múi giờ.")
    if due_date <= now:
        raise DomainError(
            ErrorKind.INVALID, "INVALID_DUE_DATE", "Hạn cam kết phải ở tương lai."
        )


def check_ticket_editable(ticket: Mapping[str, Any]) -> None:
    """Customer data can be corrected only before the ticket is assigned (status MOI)."""
    if ticket["status"] != "MOI":
        raise DomainError(
            ErrorKind.CONFLICT,
            "TICKET_NOT_EDITABLE",
            "Chỉ sửa được phiếu ở trạng thái MỚI.",
        )


def check_ticket_cancellable(ticket: Mapping[str, Any]) -> None:
    """A ticket is cancelled (soft delete, QT-13) only while still new."""
    if ticket["status"] != "MOI":
        raise DomainError(
            ErrorKind.CONFLICT,
            "TICKET_NOT_CANCELLABLE",
            "Chỉ hủy được phiếu ở trạng thái MỚI.",
        )
