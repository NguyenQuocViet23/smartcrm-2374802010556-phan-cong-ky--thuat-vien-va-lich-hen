"""Ticket list, detail, assignment, and lifecycle endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy import text

from app.core.database import get_engine
from app.core.errors import APIError
from app.core.security import current_user, require_role
from app.schemas.tickets import AssignmentRequest, StatusRequest, TechnicianChangeRequest

router = APIRouter(prefix="/api/tickets", tags=["tickets"])
MANAGER = Depends(require_role("QUAN_LY"))
TECHNICIAN = Depends(require_role("KY_THUAT_VIEN"))
VALID_STATUSES = {
    "MOI", "DA_PHAN_CONG", "DANG_XU_LY", "CHO_LINH_KIEN",
    "HOAN_TAT", "DA_DONG", "DA_HUY",
}
TRANSITIONS = {
    "DA_PHAN_CONG": {"DANG_XU_LY"},
    "DANG_XU_LY": {"CHO_LINH_KIEN", "HOAN_TAT"},
    "CHO_LINH_KIEN": {"HOAN_TAT"},
}
ACTIVE_WORK_STATUSES = ("DA_PHAN_CONG", "DANG_XU_LY", "CHO_LINH_KIEN")


def _ticket(connection: Any, ticket_id: int, lock: bool = False) -> Any:
    suffix = " FOR UPDATE" if lock else ""
    ticket = connection.execute(
        text(f"SELECT * FROM ticket WHERE ticket_id = :ticket_id{suffix}"),
        {"ticket_id": ticket_id},
    ).mappings().first()
    if ticket is None:
        raise APIError(404, "TICKET_NOT_FOUND", "Không tìm thấy phiếu.")
    return ticket


def _check_scope(user: dict[str, Any], ticket: Any) -> None:
    if user["role"] == "QUAN_LY" and ticket["center_id"] != user["center_id"]:
        raise APIError(403, "FORBIDDEN", "Bạn không có quyền xem phiếu của trung tâm này")
    if (
        user["role"] == "KY_THUAT_VIEN"
        and ticket["technician_id"] != user.get("technician_id")
    ):
        raise APIError(
            403,
            "FORBIDDEN",
            "Bạn không phải kỹ thuật viên phụ trách phiếu này",
        )


def _mask_phone(phone: str) -> str:
    return f"{phone[:3]}****{phone[-3:]}"


def _ticket_detail(connection: Any, ticket: Any, user: dict[str, Any]) -> dict[str, Any]:
    technician = None
    if ticket["technician_id"] is not None:
        technician = connection.execute(
            text(
                """SELECT technician_id, technician_code, full_name, level
                   FROM technician WHERE technician_id = :technician_id"""
            ),
            {"technician_id": ticket["technician_id"]},
        ).mappings().first()
    history = connection.execute(
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
        {"ticket_id": ticket["ticket_id"]},
    ).mappings().all()
    result = dict(ticket)
    if user["role"] != "QUAN_LY":
        result["customer_phone"] = _mask_phone(result["customer_phone"])
    result["technician"] = dict(technician) if technician else None
    result["status_history"] = [dict(entry) for entry in history]
    return result


def _check_assignment(connection: Any, ticket: Any, technician_id: int) -> Any:
    technician = connection.execute(
        text(
            """SELECT t.technician_id, t.technician_code, t.center_id, t.is_active,
                      s.proficiency
               FROM technician t
               LEFT JOIN technician_skill s
                 ON s.technician_id = t.technician_id
                AND s.category_code = :category_code
               WHERE t.technician_id = :technician_id"""
        ),
        {
            "technician_id": technician_id,
            "category_code": ticket["category_code"],
        },
    ).mappings().first()
    if technician is None:
        raise APIError(404, "TECHNICIAN_NOT_FOUND", "Không tìm thấy kỹ thuật viên.")
    if (
        technician["center_id"] != ticket["center_id"]
        or not technician["is_active"]
        or technician["proficiency"] is None
        or technician["proficiency"] < 3
    ):
        proficiency = technician["proficiency"]
        raise APIError(
            400,
            "TECHNICIAN_NOT_ELIGIBLE",
            f"Kỹ thuật viên không đủ điều kiện: tay nghề {ticket['category_code']} "
            f"= {proficiency if proficiency is not None else 'không có'} (< 3) "
            "hoặc khác trung tâm/đã nghỉ việc.",
        )
    return technician


@router.get("")
def list_tickets(
    status: str = "MOI",
    category_code: str | None = None,
    priority: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    user: dict[str, Any] = MANAGER,
) -> dict[str, Any]:
    if status not in VALID_STATUSES:
        raise APIError(400, "INVALID_STATUS", "Trạng thái phiếu không hợp lệ.")
    filters = ["center_id = :center_id", "status = :status"]
    params: dict[str, Any] = {
        "center_id": user["center_id"],
        "status": status,
        "limit": page_size,
        "offset": (page - 1) * page_size,
    }
    if category_code:
        filters.append("category_code = :category_code")
        params["category_code"] = category_code
    if priority:
        if priority not in {"CAO", "TRUNG_BINH", "THAP"}:
            raise APIError(400, "INVALID_PRIORITY", "Mức ưu tiên không hợp lệ.")
        filters.append("priority = :priority")
        params["priority"] = priority
    where = " AND ".join(filters)
    with get_engine().connect() as connection:
        total = connection.execute(
            text(f"SELECT count(*) FROM ticket WHERE {where}"), params
        ).scalar_one()
        rows = connection.execute(
            text(
                f"""SELECT ticket_id, ticket_code, center_id, customer_name, customer_phone,
                           serial_no, issue_desc, category_code, priority, status,
                           technician_id, received_at, due_date
                    FROM ticket WHERE {where}
                    ORDER BY CASE priority WHEN 'CAO' THEN 1
                         WHEN 'TRUNG_BINH' THEN 2 ELSE 3 END, due_date, ticket_id
                    LIMIT :limit OFFSET :offset"""
            ),
            params,
        ).mappings().all()
    return {"items": [dict(row) for row in rows], "total": total, "page": page,
            "page_size": page_size}


@router.get("/{ticket_id}/technician-suggestions")
def technician_suggestions(
    ticket_id: int,
    user: dict[str, Any] = MANAGER,
) -> dict[str, Any]:
    with get_engine().connect() as connection:
        ticket = _ticket(connection, ticket_id)
        _check_scope(user, ticket)
        suggestions = connection.execute(
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
            {"center_id": ticket["center_id"], "category_code": ticket["category_code"]},
        ).mappings().all()
    result = {
        "ticket_id": ticket_id,
        "ticket_code": ticket["ticket_code"],
        "category": ticket["category_code"],
        "center_id": ticket["center_id"],
        "suggestions": [dict(row) for row in suggestions],
    }
    if not suggestions:
        result["message"] = "Không có kỹ thuật viên cùng trung tâm đủ tay nghề từ 3 trở lên."
    return result


@router.get("/{ticket_id}")
def get_ticket(ticket_id: int, user: dict[str, Any] = Depends(current_user)) -> dict[str, Any]:
    with get_engine().connect() as connection:
        ticket = _ticket(connection, ticket_id)
        _check_scope(user, ticket)
        return _ticket_detail(connection, ticket, user)


@router.post("/{ticket_id}/assignment", status_code=201)
def assign_ticket(
    ticket_id: int,
    payload: AssignmentRequest,
    user: dict[str, Any] = MANAGER,
) -> dict[str, Any]:
    with get_engine().begin() as connection:
        ticket = _ticket(connection, ticket_id, lock=True)
        _check_scope(user, ticket)
        if ticket["status"] != "MOI" or ticket["technician_id"] is not None:
            current = connection.execute(
                text("SELECT technician_code FROM technician WHERE technician_id = :id"),
                {"id": ticket["technician_id"]},
            ).scalar_one_or_none()
            raise APIError(
                409,
                "TICKET_ALREADY_ASSIGNED",
                f"Phiếu đã được phân công{f' cho kỹ thuật viên {current}' if current else ''}.",
            )
        _check_assignment(connection, ticket, payload.technician_id)
        updated = connection.execute(
            text(
                """UPDATE ticket SET technician_id = :technician_id, status = 'DA_PHAN_CONG'
                   WHERE ticket_id = :ticket_id RETURNING ticket_id, status, technician_id"""
            ),
            {"technician_id": payload.technician_id, "ticket_id": ticket_id},
        ).mappings().one()
        changed_at = connection.execute(
            text(
                """INSERT INTO ticket_status_log
                   (ticket_id, event_type, from_status, to_status, to_technician_id,
                    changed_by, changed_at)
                   VALUES (:ticket_id, 'TRANG_THAI', 'MOI', 'DA_PHAN_CONG',
                           :technician_id, :changed_by, now())
                   RETURNING changed_at"""
            ),
            {
                "ticket_id": ticket_id,
                "technician_id": payload.technician_id,
                "changed_by": user["employee_id"],
            },
        ).scalar_one()
    return {**dict(updated), "assigned_by": user["employee_id"], "assigned_at": changed_at}


@router.put("/{ticket_id}/assignment")
def change_assignment(
    ticket_id: int,
    payload: TechnicianChangeRequest,
    user: dict[str, Any] = MANAGER,
) -> dict[str, Any]:
    reason = payload.reason.strip()
    if not reason:
        raise APIError(400, "REASON_REQUIRED", "Lý do đổi kỹ thuật viên là bắt buộc.")
    with get_engine().begin() as connection:
        ticket = _ticket(connection, ticket_id, lock=True)
        _check_scope(user, ticket)
        if ticket["status"] in {"HOAN_TAT", "DA_DONG", "DA_HUY"}:
            raise APIError(409, "TICKET_NOT_CHANGEABLE", "Không thể đổi kỹ thuật viên cho phiếu đã kết thúc.")
        if ticket["technician_id"] is None:
            raise APIError(409, "TICKET_NOT_ASSIGNED", "Phiếu chưa được phân công.")
        if ticket["technician_id"] == payload.technician_id:
            raise APIError(400, "SAME_TECHNICIAN", "Kỹ thuật viên mới phải khác người hiện tại.")
        _check_assignment(connection, ticket, payload.technician_id)
        connection.execute(
            text("UPDATE ticket SET technician_id = :new_id WHERE ticket_id = :ticket_id"),
            {"new_id": payload.technician_id, "ticket_id": ticket_id},
        )
        connection.execute(
            text(
                """INSERT INTO ticket_status_log
                   (ticket_id, event_type, from_status, to_status, from_technician_id,
                    to_technician_id, changed_by, note)
                   VALUES (:ticket_id, 'DOI_KTV', :status, :status, :old_id,
                           :new_id, :changed_by, :reason)"""
            ),
            {
                "ticket_id": ticket_id,
                "status": ticket["status"],
                "old_id": ticket["technician_id"],
                "new_id": payload.technician_id,
                "changed_by": user["employee_id"],
                "reason": reason,
            },
        )
    return {"ticket_id": ticket_id, "status": ticket["status"],
            "technician_id": payload.technician_id}


@router.patch("/{ticket_id}/status")
def update_ticket_status(
    ticket_id: int,
    payload: StatusRequest,
    user: dict[str, Any] = TECHNICIAN,
) -> dict[str, Any]:
    target = payload.to_status.strip().upper()
    if target not in {"DANG_XU_LY", "CHO_LINH_KIEN", "HOAN_TAT"}:
        raise APIError(400, "INVALID_STATUS", "Trạng thái đích không hợp lệ.")
    with get_engine().begin() as connection:
        ticket = _ticket(connection, ticket_id, lock=True)
        _check_scope(user, ticket)
        if target not in TRANSITIONS.get(ticket["status"], set()):
            raise APIError(
                409,
                "INVALID_STATUS_TRANSITION",
                f"Không thể chuyển từ {ticket['status']} sang {target}.",
            )
        updated = connection.execute(
            text(
                "UPDATE ticket SET status = :status WHERE ticket_id = :ticket_id "
                "RETURNING ticket_id, status, technician_id"
            ),
            {"status": target, "ticket_id": ticket_id},
        ).mappings().one()
        connection.execute(
            text(
                """INSERT INTO ticket_status_log
                   (ticket_id, event_type, from_status, to_status, to_technician_id,
                    changed_by, note)
                   VALUES (:ticket_id, 'TRANG_THAI', :previous, :target, :technician_id,
                           :changed_by, :note)"""
            ),
            {
                "ticket_id": ticket_id,
                "previous": ticket["status"],
                "target": target,
                "technician_id": ticket["technician_id"],
                "changed_by": user["employee_id"],
                "note": payload.note.strip() if payload.note else None,
            },
        )
    return dict(updated)


@router.get("/{ticket_id}/appointments")
def ticket_appointments(
    ticket_id: int,
    user: dict[str, Any] = Depends(current_user),
) -> list[dict[str, Any]]:
    with get_engine().connect() as connection:
        ticket = _ticket(connection, ticket_id)
        _check_scope(user, ticket)
        rows = connection.execute(
            text(
                """SELECT appointment_id, ticket_id, technician_id, appointment_type,
                          start_at, end_at, status, note
                   FROM appointment WHERE ticket_id = :ticket_id
                   ORDER BY start_at, appointment_id"""
            ),
            {"ticket_id": ticket_id},
        ).mappings().all()
    return [dict(row) for row in rows]
