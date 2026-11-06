"""Business rules for assignment and status changes, tested without a database."""

import pytest

from app.domain.errors import DomainError, ErrorKind
from app.services.ticket_rules import (
    check_status_transition,
    check_ticket_scope,
    check_technician_change,
    check_technician_eligible,
    is_assignable,
    normalize_target_status,
    require_change_reason,
)

TICKET = {"center_id": 1, "category_code": "MAN_HINH", "status": "MOI", "technician_id": None}


def technician(**overrides):
    return {"center_id": 1, "is_active": True, "proficiency": 4, **overrides}


# --- Phạm vi xem phiếu -------------------------------------------------------

TECHNICIAN_USER = {"role": "KY_THUAT_VIEN", "center_id": 1, "technician_id": 7}
MANAGER_USER = {"role": "QUAN_LY", "center_id": 1, "technician_id": None}


@pytest.mark.parametrize("status", ["DANG_XU_LY", "HOAN_TAT", "DA_DONG", "DA_HUY"])
def test_technician_sees_own_ticket_in_any_status(status: str) -> None:
    """Luồng đúng: KTV xem được phiếu của chính mình, kể cả phiếu đã đóng hoặc đã huỷ"""
    check_ticket_scope(TECHNICIAN_USER, {**TICKET, "status": status, "technician_id": 7})


@pytest.mark.parametrize("owner", [8, None], ids=["phieu-cua-ktv-khac", "phieu-chua-giao"])
def test_technician_cannot_see_ticket_of_another_account(owner) -> None:
    """Dữ liệu sai: KTV không xem được phiếu của tài khoản khác hoặc phiếu chưa giao cho mình"""
    with pytest.raises(DomainError) as error:
        check_ticket_scope(TECHNICIAN_USER, {**TICKET, "status": "DA_DONG", "technician_id": owner})

    assert error.value.kind is ErrorKind.FORBIDDEN
    assert error.value.code == "FORBIDDEN"


def test_manager_sees_only_own_center() -> None:
    """Giá trị biên: quản lý xem được phiếu cùng trung tâm nhưng không xem được trung tâm khác"""
    check_ticket_scope(MANAGER_USER, TICKET)
    with pytest.raises(DomainError) as error:
        check_ticket_scope(MANAGER_USER, {**TICKET, "center_id": 2})

    assert error.value.kind is ErrorKind.FORBIDDEN


# --- Vòng đời trạng thái phiếu -------------------------------------------


@pytest.mark.parametrize(
    ("current", "target"),
    [
        ("DA_PHAN_CONG", "DANG_XU_LY"),
        ("DANG_XU_LY", "CHO_LINH_KIEN"),
        ("DANG_XU_LY", "HOAN_TAT"),
        ("CHO_LINH_KIEN", "HOAN_TAT"),
    ],
)
def test_forward_status_transition_is_allowed(current: str, target: str) -> None:
    """Luồng đúng: chuyển trạng thái tiến theo vòng đời được chấp nhận"""
    check_status_transition(current, target)


def test_backward_status_transition_is_rejected() -> None:
    """Dữ liệu sai: chuyển lùi DANG_XU_LY → DA_PHAN_CONG bị từ chối"""
    with pytest.raises(DomainError) as error:
        check_status_transition("DANG_XU_LY", "DA_PHAN_CONG")

    assert error.value.kind is ErrorKind.CONFLICT
    assert error.value.code == "INVALID_STATUS_TRANSITION"
    assert error.value.message == "Không thể chuyển từ DANG_XU_LY sang DA_PHAN_CONG."


@pytest.mark.parametrize("current", ["MOI", "HOAN_TAT", "DA_DONG", "DA_HUY"])
def test_unassigned_or_finished_ticket_cannot_start_work(current: str) -> None:
    """Giá trị biên: phiếu chưa phân công hoặc đã kết thúc không thể chuyển sang DANG_XU_LY"""
    with pytest.raises(DomainError) as error:
        check_status_transition(current, "DANG_XU_LY")

    assert error.value.code == "INVALID_STATUS_TRANSITION"


def test_target_status_is_trimmed_and_upper_cased() -> None:
    """Giá trị biên: trạng thái đích có khoảng trắng và chữ thường vẫn được chuẩn hoá"""
    assert normalize_target_status("  hoan_tat ") == "HOAN_TAT"


@pytest.mark.parametrize("raw", ["DA_PHAN_CONG", "DA_DONG", "XONG", ""])
def test_technician_cannot_set_other_target_status(raw: str) -> None:
    """Dữ liệu sai: kỹ thuật viên không được đặt trạng thái ngoài DANG_XU_LY/CHO_LINH_KIEN/HOAN_TAT"""
    with pytest.raises(DomainError) as error:
        normalize_target_status(raw)

    assert error.value.kind is ErrorKind.INVALID
    assert error.value.code == "INVALID_STATUS"


# --- Điều kiện kỹ thuật viên nhận phiếu ----------------------------------


def test_technician_with_proficiency_exactly_three_is_eligible() -> None:
    """Giá trị biên: tay nghề đúng bằng 3, cùng trung tâm, đang làm việc thì đủ điều kiện"""
    check_technician_eligible(TICKET, technician(proficiency=3))


@pytest.mark.parametrize(
    ("proficiency", "shown"),
    [(2, "= 2 (< 3)"), (None, "= không có (< 3)")],
    ids=["tay-nghe-2", "khong-co-ky-nang"],
)
def test_technician_below_proficiency_three_is_rejected(proficiency, shown: str) -> None:
    """Giá trị biên: tay nghề 2 hoặc không có kỹ năng nhóm sự cố thì không đủ điều kiện"""
    with pytest.raises(DomainError) as error:
        check_technician_eligible(TICKET, technician(proficiency=proficiency))

    assert error.value.kind is ErrorKind.INVALID
    assert error.value.code == "TECHNICIAN_NOT_ELIGIBLE"
    assert f"tay nghề MAN_HINH {shown}" in error.value.message


@pytest.mark.parametrize(
    "overrides",
    [{"center_id": 2}, {"is_active": False}],
    ids=["khac-trung-tam", "da-nghi-viec"],
)
def test_technician_from_other_center_or_inactive_is_rejected(overrides: dict) -> None:
    """Dữ liệu sai: kỹ thuật viên khác trung tâm hoặc đã nghỉ việc bị từ chối dù đủ tay nghề"""
    with pytest.raises(DomainError) as error:
        check_technician_eligible(TICKET, technician(**overrides))

    assert error.value.kind is ErrorKind.INVALID
    assert error.value.code == "TECHNICIAN_NOT_ELIGIBLE"


# --- Phân công và đổi kỹ thuật viên -------------------------------------


def test_only_new_unassigned_ticket_is_assignable() -> None:
    """Luồng đúng và biên: chỉ phiếu MOI chưa có kỹ thuật viên mới được phân công lần đầu"""
    assert is_assignable(TICKET)
    assert not is_assignable({**TICKET, "technician_id": 7})
    assert not is_assignable({**TICKET, "status": "DA_PHAN_CONG", "technician_id": 7})


def test_change_reason_is_trimmed() -> None:
    """Luồng đúng: lý do đổi kỹ thuật viên được cắt khoảng trắng hai đầu"""
    assert require_change_reason("  KTV nghỉ phép  ") == "KTV nghỉ phép"


def test_blank_change_reason_is_rejected() -> None:
    """Dữ liệu sai: lý do đổi kỹ thuật viên chỉ có khoảng trắng bị từ chối"""
    with pytest.raises(DomainError) as error:
        require_change_reason("   ")

    assert error.value.code == "REASON_REQUIRED"


def test_assigned_open_ticket_can_change_technician() -> None:
    """Luồng đúng: phiếu đang xử lý được đổi sang kỹ thuật viên khác"""
    check_technician_change({**TICKET, "status": "DANG_XU_LY", "technician_id": 7}, 8)


@pytest.mark.parametrize(
    ("ticket", "new_technician_id", "code"),
    [
        ({**TICKET, "status": "HOAN_TAT", "technician_id": 7}, 8, "TICKET_NOT_CHANGEABLE"),
        (TICKET, 8, "TICKET_NOT_ASSIGNED"),
        ({**TICKET, "status": "DA_PHAN_CONG", "technician_id": 7}, 7, "SAME_TECHNICIAN"),
    ],
    ids=["phieu-da-ket-thuc", "phieu-chua-phan-cong", "trung-ky-thuat-vien"],
)
def test_invalid_technician_change_is_rejected(ticket: dict, new_technician_id: int, code: str) -> None:
    """Dữ liệu sai: không đổi kỹ thuật viên cho phiếu đã kết thúc, chưa phân công hoặc trùng người cũ"""
    with pytest.raises(DomainError) as error:
        check_technician_change(ticket, new_technician_id)

    assert error.value.code == code
