"""Rules behind ticket and appointment CRUD, tested without a database."""

from datetime import datetime, timedelta, timezone

import pytest

from app.domain.errors import DomainError, ErrorKind
from app.services.appointment_rules import (
    LOCAL_TIME,
    check_appointment_cancellable,
    check_appointment_editable,
    check_ticket_accepts_appointment,
    find_free_slots,
)
from app.services.ticket_rules import (
    check_due_date_in_future,
    check_ticket_cancellable,
    check_ticket_editable,
    normalize_phone,
    require_text_fields,
)

NOW = datetime(2026, 11, 6, 9, 0, tzinfo=timezone.utc)


# --- Required text fields (BUG-08) -----------------------------------------------

TEXT_OK = {"customer_name": "  Nguyễn Văn An ", "serial_no": "SN10293A", "issue_desc": "Không lên nguồn"}


def test_required_text_fields_are_trimmed() -> None:
    """Luồng đúng: tên, serial, mô tả có chữ được giữ lại và cắt khoảng trắng hai đầu"""
    assert require_text_fields(TEXT_OK)["customer_name"] == "Nguyễn Văn An"


@pytest.mark.parametrize(
    ("blank", "expected"),
    [({"customer_name": "   "}, ["customer_name"]),
     ({"serial_no": "\t"}, ["serial_no"]),
     ({"customer_name": " ", "serial_no": "  ", "issue_desc": "\n"},
      ["customer_name", "serial_no", "issue_desc"])],
)
def test_blank_required_text_field_is_rejected(blank: dict, expected: list[str]) -> None:
    """Dữ liệu sai (BUG-08): trường bắt buộc chỉ có khoảng trắng bị từ chối và được nêu tên"""
    with pytest.raises(DomainError) as error:
        require_text_fields({**TEXT_OK, **blank})
    assert error.value.kind is ErrorKind.INVALID
    assert error.value.code == "REQUIRED_FIELD_BLANK"
    assert error.value.details["fields"] == expected


# --- Phone number (QT-02) --------------------------------------------------------


@pytest.mark.parametrize(
    ("raw", "expected"),
    [("0909123456", "0909123456"), ("0909 123 456", "0909123456"),
     ("+84 909.123.456", "0909123456"), ("84909123456", "0909123456")],
)
def test_phone_is_normalized_to_ten_digits(raw: str, expected: str) -> None:
    """Luồng đúng: số điện thoại có khoảng trắng, dấu chấm hoặc +84 được chuẩn hoá về 0xxxxxxxxx"""
    assert normalize_phone(raw) == expected


@pytest.mark.parametrize("raw", ["090912345", "09091234567", "1909123456", "abc", ""])
def test_invalid_phone_is_rejected(raw: str) -> None:
    """Dữ liệu sai: số 9 hoặc 11 chữ số, không bắt đầu bằng 0, hoặc chữ bị từ chối"""
    with pytest.raises(DomainError) as error:
        normalize_phone(raw)

    assert error.value.kind is ErrorKind.INVALID
    assert error.value.code == "INVALID_PHONE"


# --- Ticket create / update / cancel ------------------------------------------------


def test_due_date_one_second_ahead_is_accepted() -> None:
    """Giá trị biên: hạn cam kết sau thời điểm hiện tại 1 giây vẫn hợp lệ"""
    check_due_date_in_future(NOW + timedelta(seconds=1), NOW)


@pytest.mark.parametrize("due", [NOW, NOW - timedelta(days=1)], ids=["bang-hien-tai", "qua-khu"])
def test_due_date_not_in_future_is_rejected(due: datetime) -> None:
    """Giá trị biên: hạn cam kết bằng hoặc trước thời điểm hiện tại bị từ chối"""
    with pytest.raises(DomainError) as error:
        check_due_date_in_future(due, NOW)

    assert error.value.code == "INVALID_DUE_DATE"


def test_due_date_without_timezone_is_rejected() -> None:
    """Dữ liệu sai: hạn cam kết không có múi giờ bị từ chối"""
    with pytest.raises(DomainError) as error:
        check_due_date_in_future(datetime(2027, 1, 1, 9, 0), NOW)

    assert error.value.code == "INVALID_DATETIME"


def test_new_ticket_can_be_edited_and_cancelled() -> None:
    """Luồng đúng: phiếu MỚI được sửa thông tin và được hủy"""
    check_ticket_editable({"status": "MOI"})
    check_ticket_cancellable({"status": "MOI"})


@pytest.mark.parametrize("status", ["DA_PHAN_CONG", "DANG_XU_LY", "HOAN_TAT", "DA_HUY"])
def test_ticket_past_new_cannot_be_edited_or_cancelled(status: str) -> None:
    """Dữ liệu sai: phiếu đã phân công, đã hoàn tất hoặc đã hủy không được sửa và không được hủy"""
    with pytest.raises(DomainError) as edit_error:
        check_ticket_editable({"status": status})
    with pytest.raises(DomainError) as cancel_error:
        check_ticket_cancellable({"status": status})

    assert edit_error.value.kind is cancel_error.value.kind is ErrorKind.CONFLICT
    assert (edit_error.value.code, cancel_error.value.code) == ("TICKET_NOT_EDITABLE", "TICKET_NOT_CANCELLABLE")


# --- Appointment update / cancel -----------------------------------------------------


def test_booked_appointment_can_be_edited_and_cancelled() -> None:
    """Luồng đúng: lịch hẹn ĐÃ HẸN được đổi giờ và được hủy"""
    check_appointment_editable({"status": "DA_HEN"})
    check_appointment_cancellable({"status": "DA_HEN"})


def test_cancelled_appointment_cannot_be_cancelled_again() -> None:
    """Dữ liệu sai: lịch hẹn đã hủy không hủy lại được, cũng không sửa được"""
    with pytest.raises(DomainError) as cancel_error:
        check_appointment_cancellable({"status": "DA_HUY"})
    with pytest.raises(DomainError) as edit_error:
        check_appointment_editable({"status": "DA_HUY"})

    assert cancel_error.value.code == "APPOINTMENT_NOT_CANCELLABLE"
    assert edit_error.value.code == "APPOINTMENT_NOT_EDITABLE"


@pytest.mark.parametrize(
    ("ticket", "code"),
    [({"technician_id": None, "status": "MOI"}, "TICKET_NOT_ASSIGNED"),
     ({"technician_id": 7, "status": "HOAN_TAT"}, "TICKET_CLOSED")],
    ids=["chua-phan-cong", "da-ket-thuc"],
)
def test_ticket_without_technician_or_finished_cannot_be_booked(ticket: dict, code: str) -> None:
    """Dữ liệu sai: phiếu chưa phân công hoặc đã kết thúc không đặt được lịch"""
    with pytest.raises(DomainError) as error:
        check_ticket_accepts_appointment(ticket)

    assert error.value.code == code


def test_free_slots_skip_busy_time_and_prefer_nearest() -> None:
    """Giá trị biên: khung trống liền kề lịch bận (09:30) được gợi ý, khung bận 09:00 thì không"""
    day = datetime(2026, 12, 7, tzinfo=LOCAL_TIME)
    busy = [(day.replace(hour=9), day.replace(hour=9, minute=30))]

    slots = find_free_slots(busy, day.replace(hour=9, minute=15))

    starts = [slot["start_at"][11:16] for slot in slots]
    assert "09:00" not in starts
    assert starts == ["09:30", "08:30"]
