import json
from urllib.parse import parse_qs, urlparse

import pytest
from playwright.sync_api import Page, expect
from tests.evidence import capture_ui_notification

BASE_URL = "http://localhost:5173"
API_URL = "http://localhost:8000/api/**"
MANAGER = {"role": "QUAN_LY", "center_name": "Trung tâm Cần Thơ"}
TECHNICIAN = {"role": "KY_THUAT_VIEN", "full_name": "Nguyễn An"}


def fulfill(route, status: int, payload: object) -> None:
    route.fulfill(
        status=status,
        content_type="application/json",
        body=json.dumps(payload, ensure_ascii=False),
    )


def ticket_summary(status: str = "MOI") -> dict:
    return {
        "ticket_id": 101,
        "ticket_code": "BH-2026-00101",
        "customer_name": "Trần Minh",
        "customer_phone": "0901234567",
        "category_code": "MAN_HINH",
        "priority": "CAO",
        "due_date": "2026-12-31T17:00:00+07:00",
        "status": status,
        "is_overdue": False,
    }


def ticket_details(technician_id: int | None = None, status: str = "MOI") -> dict:
    return {
        **ticket_summary(status),
        "technician_id": technician_id,
        "serial_no": "SN-001",
        "issue_desc": "Màn hình không hiển thị",
        "status_history": [],
        "technician": (
            {"technician_code": "KTV-05", "full_name": "Nguyễn An"}
            if technician_id is not None
            else None
        ),
    }


def suggestion(technician_id: int, workload: int) -> dict:
    return {
        "technician_id": technician_id,
        "technician_code": f"KTV-{technician_id:02}",
        "full_name": f"Kỹ thuật viên {technician_id}",
        "level": 3,
        "proficiency": 4,
        "workload": workload,
    }


@pytest.mark.ui
@pytest.mark.tc("TC19")
def test_manager_login_filters_pagination_navigation_and_logout(page: Page) -> None:
    ticket_requests = 0
    ticket_queries = []

    def mock_api(route) -> None:
        nonlocal ticket_requests
        request = route.request
        parsed = urlparse(request.url)

        if parsed.path == "/api/auth/login":
            credentials = json.loads(request.post_data or "{}")
            if credentials.get("password") != "valid-password":
                fulfill(
                    route,
                    401,
                    {
                        "error": "INVALID_CREDENTIALS",
                        "message": "Sai tên đăng nhập hoặc mật khẩu",
                    },
                )
            else:
                fulfill(route, 200, {"access_token": "manager-test-token"})
        elif parsed.path == "/api/auth/me":
            fulfill(route, 200, MANAGER)
        elif parsed.path == "/api/tickets":
            ticket_requests += 1
            query = parse_qs(parsed.query)
            ticket_queries.append(query)
            if ticket_requests == 1:
                fulfill(route, 503, {"message": "Máy chủ tạm thời không phản hồi."})
            else:
                fulfill(
                    route,
                    200,
                    {
                        "items": [ticket_summary()],
                        "total": 21,
                        "page": int(query.get("page", ["1"])[0]),
                        "page_size": 20,
                    },
                )
        elif parsed.path == "/api/tickets/101":
            fulfill(route, 200, ticket_details())
        elif parsed.path == "/api/tickets/101/technician-suggestions":
            fulfill(route, 200, {"suggestions": [suggestion(5, 2)]})
        else:
            fulfill(route, 404, {"message": f"Unexpected request: {parsed.path}"})

    page.route(API_URL, mock_api)
    page.goto(f"{BASE_URL}/login")

    username = page.get_by_label("Tên đăng nhập")
    password = page.get_by_label("Mật khẩu")
    login_button = page.get_by_role("button", name="Đăng nhập")
    expect(username).to_be_visible()
    expect(password).to_be_visible()

    login_button.click()
    assert username.evaluate("(element) => element.checkValidity()") is False

    username.fill("manager")
    password.fill("wrong-password")
    login_button.click()
    expect(page.get_by_role("alert")).to_contain_text("Sai tên đăng nhập hoặc mật khẩu")
    capture_ui_notification(page, "TC19", "b1_thong_bao_dang_nhap_sai")

    password.fill("valid-password")
    login_button.click()
    expect(page.get_by_text("Phiếu chờ phân công")).to_be_visible()
    expect(page.get_by_test_id("state-error")).to_contain_text(
        "Máy chủ tạm thời không phản hồi."
    )
    capture_ui_notification(page, "TC19", "b2_thong_bao_loi_may_chu")

    page.get_by_test_id("retry-button").click()
    expect(page.get_by_text("BH-2026-00101")).to_be_visible()
    page.get_by_label("Nhóm sự cố").select_option("PIN")
    page.get_by_label("Mức ưu tiên").select_option("CAO")
    expect(page.get_by_text("BH-2026-00101")).to_be_visible()
    assert ticket_queries[-1]["category_code"] == ["PIN"]
    assert ticket_queries[-1]["priority"] == ["CAO"]

    page.get_by_role("button", name="Sau").click()
    expect(page.get_by_text("Trang 2 / 2")).to_be_visible()
    assert ticket_queries[-1]["page"] == ["2"]
    page.get_by_role("button", name="Trước").click()
    expect(page.get_by_text("Trang 1 / 2")).to_be_visible()
    assert ticket_queries[-1]["page"] == ["1"]

    page.get_by_role("button", name="Phân công").click()
    expect(page.get_by_role("heading", name="BH-2026-00101")).to_be_visible()
    page.get_by_role("button", name="Hủy", exact=True).click()
    expect(page.get_by_text("Phiếu chờ phân công")).to_be_visible()

    page.get_by_role("button", name="Đăng xuất").click()
    expect(page.get_by_role("heading", name="Smart CRM")).to_be_visible()


@pytest.mark.ui
@pytest.mark.tc("TC20")
def test_assignment_errors_reason_validation_and_appointment_buttons(page: Page) -> None:
    assigned = False
    assignment_attempts = 0
    appointment_attempts = 0
    appointment_payloads = []

    def mock_api(route) -> None:
        nonlocal assigned, assignment_attempts, appointment_attempts
        request = route.request
        parsed = urlparse(request.url)

        if parsed.path == "/api/auth/me":
            fulfill(route, 200, MANAGER)
        elif parsed.path == "/api/tickets/101":
            fulfill(route, 200, ticket_details(5 if assigned else None, "DA_PHAN_CONG" if assigned else "MOI"))
        elif parsed.path == "/api/tickets/101/technician-suggestions":
            fulfill(
                route,
                200,
                {"suggestions": [suggestion(4, 1), suggestion(5, 3)]},
            )
        elif parsed.path == "/api/tickets/101/assignment" and request.method == "POST":
            assignment_attempts += 1
            if assignment_attempts == 1:
                route.abort()
            elif assignment_attempts == 2:
                fulfill(
                    route,
                    409,
                    {
                        "error": "TECHNICIAN_NOT_ELIGIBLE",
                        "message": "Kỹ thuật viên không đủ điều kiện nhận phiếu.",
                    },
                )
            else:
                assigned = True
                fulfill(route, 200, {"ticket_id": 101, "technician_id": 5})
        elif parsed.path == "/api/tickets/101/assignment" and request.method == "PUT":
            fulfill(
                route,
                409,
                {
                    "error": "TICKET_NOT_CHANGEABLE",
                    "message": "Phiếu hiện không thể đổi kỹ thuật viên.",
                },
            )
        elif parsed.path == "/api/appointments" and request.method == "POST":
            appointment_attempts += 1
            appointment_payloads.append(json.loads(request.post_data or "{}"))
            if appointment_attempts == 1:
                fulfill(
                    route,
                    409,
                    {
                        "error": "APPOINTMENT_OVERLAP",
                        "message": "Khung giờ này đã có lịch hẹn.",
                        "conflicts": [
                            {
                                "appointment_id": 7,
                                "start_at": "2026-11-23T09:00:00+07:00",
                                "end_at": "2026-11-23T09:30:00+07:00",
                                "ticket_code": "BH-2026-00007",
                            }
                        ],
                        "free_slots": [
                            {
                                "start_at": "2026-11-23T11:00:00+07:00",
                                "end_at": "2026-11-23T11:30:00+07:00",
                            }
                        ],
                    },
                )
            else:
                fulfill(route, 201, {"appointment_id": 8})
        else:
            fulfill(route, 404, {"message": f"Unexpected request: {parsed.path}"})

    page.add_init_script(
        "if (!sessionStorage.getItem('ui-test-token-installed')) {"
        "localStorage.setItem('access_token', 'manager-test-token');"
        "sessionStorage.setItem('ui-test-token-installed', 'true');"
        "}"
    )
    page.route(API_URL, mock_api)
    page.goto(f"{BASE_URL}/tickets/101/assign")
    expect(page.get_by_role("heading", name="BH-2026-00101")).to_be_visible()

    page.get_by_role("radio").nth(1).check()
    confirm = page.get_by_role("button", name="Xác nhận phân công")
    confirm.click()
    expect(page.get_by_role("alert")).to_contain_text("Chưa lưu được (mất kết nối).")
    capture_ui_notification(page, "TC20", "b1_thong_bao_mat_ket_noi")
    page.get_by_role("button", name="Thử lại").click()
    expect(page.get_by_role("alert")).to_contain_text(
        "Kỹ thuật viên không đủ điều kiện nhận phiếu."
    )
    capture_ui_notification(page, "TC20", "b2_thong_bao_ktv_khong_du_dieu_kien")
    confirm.click()

    save_change = page.get_by_role("button", name="Lưu đổi kỹ thuật viên")
    expect(save_change).to_be_disabled()
    reason = page.get_by_label("Lý do đổi")
    reason.fill("Phân bổ lại khối lượng")
    save_change.click()
    expect(page.get_by_role("alert")).to_contain_text(
        "Phiếu hiện không thể đổi kỹ thuật viên."
    )

    page.get_by_role("button", name="Đặt lịch hẹn").click()
    expect(page.get_by_role("heading", name="Đặt lịch hẹn giao/nhận thiết bị")).to_be_visible()
    page.get_by_role("button", name="Hủy", exact=True).last.click()
    expect(page.get_by_role("heading", name="Đặt lịch hẹn giao/nhận thiết bị")).to_have_count(0)

    page.get_by_role("button", name="Đặt lịch hẹn").click()
    date_input = page.get_by_label("Ngày")
    page.get_by_label("Loại").select_option("NHAN")
    page.get_by_label("Ghi chú").fill("Khách nhận máy")
    page.get_by_label("Giờ bắt đầu").fill("18:00")
    page.get_by_role("button", name="Lưu lịch hẹn").click()
    assert page.get_by_label("Giờ bắt đầu").evaluate(
        "(element) => element.checkValidity()"
    ) is False
    assert appointment_attempts == 0

    date_input.fill("")
    page.get_by_role("button", name="Lưu lịch hẹn").click()
    assert date_input.evaluate("(element) => element.checkValidity()") is False
    assert appointment_attempts == 0

    date_input.fill("2026-11-23")
    page.get_by_label("Giờ bắt đầu").fill("09:00")
    page.get_by_role("button", name="Lưu lịch hẹn").click()
    expect(page.get_by_text("Khung giờ này đã có lịch hẹn.")).to_be_visible()
    capture_ui_notification(page, "TC20", "b3_thong_bao_trung_lich_hen")
    expect(page.get_by_text("BH-2026-00007")).to_be_visible()
    page.get_by_role("button", name="11:00–11:30").click()
    expect(page.get_by_label("Giờ bắt đầu")).to_have_value("11:00")
    page.get_by_role("button", name="Lưu lịch hẹn").click()
    expect(page.get_by_role("heading", name="Đặt lịch hẹn giao/nhận thiết bị")).to_have_count(0)
    assert appointment_payloads[-1]["appointment_type"] == "NHAN"
    assert appointment_payloads[-1]["note"] == "Khách nhận máy"


@pytest.mark.ui
@pytest.mark.tc("TC21")
def test_technician_status_transitions_and_appointment_errors(page: Page) -> None:
    status = "DA_PHAN_CONG"
    status_attempts = 0
    appointment_attempts = 0
    appointment_load_attempts = 0
    appointments = []
    status_payloads = []

    def mock_api(route) -> None:
        nonlocal status, status_attempts, appointment_attempts
        nonlocal appointment_load_attempts, appointments, status_payloads
        request = route.request
        parsed = urlparse(request.url)

        if parsed.path == "/api/auth/me":
            fulfill(route, 200, TECHNICIAN)
        elif parsed.path == "/api/technicians/me/tickets":
            fulfill(route, 200, [ticket_summary(status)])
        elif parsed.path == "/api/tickets/101":
            fulfill(route, 200, ticket_details(5, status))
        elif parsed.path == "/api/tickets/101/appointments" and request.method == "GET":
            appointment_load_attempts += 1
            if appointment_load_attempts == 3:
                fulfill(
                    route,
                    503,
                    {"message": "Không tải được lịch hẹn."},
                )
            else:
                fulfill(route, 200, appointments)
        elif parsed.path == "/api/tickets/101/status" and request.method == "PATCH":
            status_attempts += 1
            status_payload = json.loads(request.post_data or "{}")
            status_payloads.append(status_payload)
            if status_attempts == 1:
                fulfill(
                    route,
                    409,
                    {
                        "error": "INVALID_STATUS_TRANSITION",
                        "message": "Không thể chuyển trạng thái theo yêu cầu.",
                    },
                )
            else:
                status = status_payload["to_status"]
                fulfill(route, 200, {"ticket_id": 101, "status": status})
        elif parsed.path == "/api/appointments" and request.method == "POST":
            appointment_attempts += 1
            if appointment_attempts == 1:
                fulfill(
                    route,
                    409,
                    {
                        "error": "APPOINTMENT_OVERLAP",
                        "message": "Khung giờ này đã có lịch hẹn.",
                        "free_slots": [
                            {
                                "start_at": "2026-11-23T13:00:00+07:00",
                                "end_at": "2026-11-23T13:30:00+07:00",
                            }
                        ],
                    },
                )
            else:
                appointments = [
                    {
                        "appointment_id": 9,
                        "start_at": "2026-11-23T13:00:00+07:00",
                        "end_at": "2026-11-23T13:30:00+07:00",
                        "appointment_type": "GIAO",
                        "status": "DA_HEN",
                    }
                ]
                fulfill(route, 201, {"appointment_id": 9})
        else:
            fulfill(route, 404, {"message": f"Unexpected request: {parsed.path}"})

    page.add_init_script(
        "if (!sessionStorage.getItem('ui-test-token-installed')) {"
        "localStorage.setItem('access_token', 'technician-test-token');"
        "sessionStorage.setItem('ui-test-token-installed', 'true');"
        "}"
    )
    page.route(API_URL, mock_api)
    page.goto(f"{BASE_URL}/my-tickets")

    page.get_by_role("button", name="BH-2026-00101").click()
    expect(page.get_by_role("heading", name="BH-2026-00101")).to_be_visible()
    page.get_by_label("Ghi chú (tối đa 255 ký tự)").fill("Đã kiểm tra thiết bị")
    page.get_by_role("button", name="Bắt đầu sửa").click()
    expect(page.get_by_role("alert")).to_contain_text(
        "Không thể chuyển trạng thái theo yêu cầu."
    )
    capture_ui_notification(page, "TC21", "b1_thong_bao_chuyen_trang_thai_loi")
    assert status_payloads[0]["note"] == "Đã kiểm tra thiết bị"
    page.get_by_role("button", name="Bắt đầu sửa").click()
    expect(page.get_by_role("button", name="Thiếu linh kiện")).to_be_visible()

    page.get_by_role("button", name="Đặt lịch hẹn").click()
    page.get_by_role("button", name="Hủy", exact=True).last.click()
    page.get_by_role("button", name="Đặt lịch hẹn").click()
    date_input = page.get_by_label("Ngày")
    date_input.fill("2026-11-23")
    page.get_by_role("button", name="Lưu lịch hẹn").click()
    expect(page.get_by_text("Khung giờ này đã có lịch hẹn.")).to_be_visible()
    capture_ui_notification(page, "TC21", "b2_thong_bao_trung_lich_hen")
    page.get_by_role("button", name="13:00–13:30").click()
    page.get_by_role("button", name="Lưu lịch hẹn").click()
    expect(page.get_by_text("Không tải được lịch hẹn.")).to_be_visible()
    capture_ui_notification(page, "TC21", "b3_thong_bao_loi_tai_lich_hen")
    page.get_by_role("button", name="Tải lại lịch hẹn").click()
    expect(page.get_by_text("ĐÃ HẸN")).to_be_visible()

    page.get_by_role("button", name="Thiếu linh kiện").click()
    page.get_by_role("button", name="Hoàn tất").click()
    # v1.1: finishing a ticket asks for confirmation first.
    page.get_by_role("dialog").get_by_role("button", name="Xác nhận").click()
    expect(page.get_by_role("cell", name="HOÀN TẤT", exact=True)).to_be_visible()
    expect(page.get_by_role("button", name="Đặt lịch hẹn")).to_have_count(0)

    page.get_by_role("button", name="Đăng xuất").click()
    expect(page.get_by_role("heading", name="Smart CRM")).to_be_visible()


# --- v1.1 interface: ticket tabs and CRUD, appointments page, technician dashboard ----------------

def install_token(page: Page, token: str) -> None:
    page.add_init_script(
        "if (!sessionStorage.getItem('ui-test-token-installed')) {"
        f"localStorage.setItem('access_token', '{token}');"
        "sessionStorage.setItem('ui-test-token-installed', 'true');"
        "}"
    )


def vn_now():
    from datetime import datetime, timedelta, timezone
    return datetime.now(timezone(timedelta(hours=7)))


@pytest.mark.ui
def test_manager_status_tabs_create_edit_cancel_ticket(page: Page) -> None:
    created = []
    calls = []

    def mock_api(route) -> None:
        request = route.request
        parsed = urlparse(request.url)
        query = parse_qs(parsed.query)
        calls.append((request.method, parsed.path, query, request.post_data))
        if parsed.path == "/api/auth/me":
            fulfill(route, 200, MANAGER)
        elif parsed.path == "/api/tickets" and request.method == "GET":
            status = query.get("status", ["MOI"])[0]
            rows = {
                "MOI": [ticket_summary()] + created,
                "DA_PHAN_CONG": [{**ticket_summary("DA_PHAN_CONG"), "ticket_id": 102, "ticket_code": "BH-2026-00102"}],
            }.get(status, [])
            fulfill(route, 200, {"items": rows, "total": len(rows), "page": 1, "page_size": 20})
        elif parsed.path == "/api/tickets" and request.method == "POST":
            body = json.loads(request.post_data)
            if body["customer_phone"] == "09123":
                fulfill(route, 400, {"error": "INVALID_PHONE", "message": "Số điện thoại phải gồm 10 chữ số và bắt đầu bằng 0."})
            else:
                ticket = {**ticket_summary(), **body, "ticket_id": 200, "ticket_code": "BH-2026-00200"}
                created.append(ticket)
                fulfill(route, 201, ticket)
        elif parsed.path == "/api/tickets/101" and request.method == "PUT":
            fulfill(route, 200, {**ticket_details(), **json.loads(request.post_data)})
        elif parsed.path == "/api/tickets/101" and request.method == "DELETE":
            fulfill(route, 200, {**ticket_details(), "status": "DA_HUY"})
        else:
            fulfill(route, 404, {"message": f"Unexpected request: {parsed.path}"})

    install_token(page, "manager-test-token")
    page.route(API_URL, mock_api)
    page.goto(f"{BASE_URL}/tickets")

    # Tabs show how many tickets each status has; another tab lists assigned tickets with their own action.
    expect(page.get_by_role("tab", name="Chờ phân công")).to_contain_text("1")
    expect(page.get_by_role("tab", name="Đã phân công")).to_contain_text("1")
    page.get_by_role("tab", name="Đã phân công").click()
    expect(page).to_have_url(f"{BASE_URL}/tickets?status=DA_PHAN_CONG")
    expect(page.get_by_text("Phiếu – Đã phân công")).to_be_visible()
    expect(page.get_by_role("button", name="Chi tiết / Đổi KTV")).to_be_visible()
    expect(page.get_by_role("link", name="BH-2026-00102")).to_have_attribute("href", "/tickets/102")
    page.get_by_role("tab", name="Chờ phân công").click()

    # Create: a wrong phone is rejected and the field is marked, then the corrected ticket is saved.
    page.get_by_role("button", name="+ Tạo phiếu mới").click()
    dialog = page.get_by_role("dialog")
    dialog.get_by_label("Khách hàng").fill("Lê Thu")
    dialog.get_by_label("Số điện thoại").fill("09123")
    dialog.get_by_label("Serial máy").fill("SN-200")
    dialog.get_by_label("Mô tả lỗi").fill("Không sạc được")
    dialog.get_by_label("Nhóm sự cố").select_option("SAC")
    dialog.get_by_role("button", name="Tạo phiếu").click()
    expect(dialog).to_contain_text("Số điện thoại phải gồm 10 chữ số")
    expect(dialog.get_by_label("Số điện thoại")).to_have_class("invalid")
    dialog.get_by_label("Số điện thoại").fill("0912 345 678")
    dialog.get_by_role("button", name="Tạo phiếu").click()
    expect(page.get_by_role("dialog")).to_have_count(0)
    expect(page.get_by_role("status")).to_contain_text("Đã tạo phiếu BH-2026-00200")
    posted = json.loads([c for c in calls if c[0] == "POST"][-1][3])
    assert posted["category_code"] == "SAC" and posted["customer_phone"] == "0912 345 678"
    assert posted["due_date"].endswith("Z")

    # Edit a MOI ticket.
    row = page.get_by_role("row", name="BH-2026-00101")
    row.get_by_role("button", name="Sửa").click()
    expect(page.get_by_role("dialog").get_by_label("Khách hàng")).to_have_value("Trần Minh")
    page.get_by_role("dialog").get_by_label("Mô tả lỗi").fill("Màn hình sọc ngang")
    page.get_by_role("dialog").get_by_role("button", name="Lưu thay đổi").click()
    expect(page.get_by_role("status")).to_contain_text("Đã lưu thay đổi phiếu")
    put = [c for c in calls if c[0] == "PUT"][-1]
    assert json.loads(put[3])["issue_desc"] == "Màn hình sọc ngang"

    # Cancel (soft delete) asks for confirmation; "Quay lại" sends nothing.
    row.get_by_role("button", name="Hủy phiếu").click()
    page.get_by_role("dialog").get_by_role("button", name="Quay lại").click()
    assert not [c for c in calls if c[0] == "DELETE"]
    row.get_by_role("button", name="Hủy phiếu").click()
    page.get_by_role("dialog").get_by_label("Lý do hủy (không bắt buộc)").fill("Khách đổi ý")
    page.get_by_role("dialog").get_by_role("button", name="Xác nhận hủy phiếu").click()
    expect(page.get_by_role("status")).to_contain_text("Đã hủy phiếu BH-2026-00101")
    deleted = [c for c in calls if c[0] == "DELETE"]
    assert deleted[-1][1] == "/api/tickets/101" and deleted[-1][2]["reason"] == ["Khách đổi ý"]


@pytest.mark.ui
def test_appointments_page_reschedule_and_cancel(page: Page) -> None:
    from datetime import timedelta
    day = (vn_now() + timedelta(days=40)).date()
    while day.weekday() == 6:
        day += timedelta(days=1)
    appointment = {
        "appointment_id": 31, "ticket_id": 101, "ticket_code": "BH-2026-00101", "technician_id": 5,
        "appointment_type": "NHAN", "start_at": f"{day}T09:00:00+07:00", "end_at": f"{day}T09:30:00+07:00",
        "status": "DA_HEN", "note": "Gọi trước 15 phút",
    }
    puts, deletes = [], []

    def mock_api(route) -> None:
        request = route.request
        parsed = urlparse(request.url)
        if parsed.path == "/api/auth/me":
            fulfill(route, 200, MANAGER)
        elif parsed.path == "/api/appointments" and request.method == "GET":
            items = [appointment] if appointment["status"] == "DA_HEN" else []
            fulfill(route, 200, {"items": items, "total": len(items), "page": 1, "page_size": 100})
        elif parsed.path == "/api/appointments/31" and request.method == "PUT":
            body = json.loads(request.post_data)
            puts.append(body)
            if len(puts) == 1:
                fulfill(route, 409, {
                    "error": "APPOINTMENT_OVERLAP", "message": "Khung giờ này đã có lịch hẹn.",
                    "conflicts": [{"appointment_id": 7, "ticket_code": "BH-2026-00007",
                                   "start_at": f"{day}T10:00:00+07:00", "end_at": f"{day}T10:30:00+07:00"}],
                    "free_slots": [{"start_at": f"{day}T11:00:00+07:00", "end_at": f"{day}T11:30:00+07:00"}],
                })
            else:
                appointment.update(start_at=body["start_at"], end_at=body["end_at"])
                fulfill(route, 200, appointment)
        elif parsed.path == "/api/appointments/31" and request.method == "DELETE":
            deletes.append(parsed.path)
            appointment["status"] = "DA_HUY"
            fulfill(route, 200, appointment)
        else:
            fulfill(route, 404, {"message": f"Unexpected request: {parsed.path}"})

    install_token(page, "manager-test-token")
    page.route(API_URL, mock_api)
    page.goto(f"{BASE_URL}/appointments")

    row = page.get_by_role("row", name="BH-2026-00101")
    expect(row).to_contain_text("Nhận máy (NHAN)")
    expect(row).to_contain_text("ĐÃ HẸN")
    expect(row.get_by_role("link", name="BH-2026-00101")).to_have_attribute("href", "/tickets/101")

    # Reschedule: the form opens on the current slot; an overlap offers free slots.
    row.get_by_role("button", name="Đổi giờ").click()
    dialog = page.get_by_role("dialog")
    expect(dialog.get_by_label("Ngày")).to_have_value(str(day))
    expect(dialog.get_by_label("Giờ bắt đầu")).to_have_value("09:00")
    dialog.get_by_label("Giờ bắt đầu").fill("10:00")
    dialog.get_by_role("button", name="Lưu lịch hẹn").click()
    expect(dialog.get_by_text("Khung giờ này đã có lịch hẹn.")).to_be_visible()
    dialog.get_by_role("button", name="11:00–11:30").click()
    dialog.get_by_role("button", name="Lưu lịch hẹn").click()
    expect(page.get_by_role("dialog")).to_have_count(0)
    expect(page.get_by_role("status")).to_contain_text("Đã đổi lịch hẹn của phiếu BH-2026-00101")
    assert puts[-1]["appointment_type"] == "NHAN" and puts[-1]["start_at"].startswith(f"{day}T04:00:00")

    # Cancel (soft delete) after confirmation; the row leaves the "Đã hẹn" list.
    page.get_by_role("row", name="BH-2026-00101").get_by_role("button", name="Hủy lịch").click()
    page.get_by_role("dialog").get_by_role("button", name="Xác nhận hủy lịch").click()
    expect(page.get_by_role("status")).to_contain_text("Đã hủy lịch hẹn")
    expect(page.get_by_test_id("state-empty")).to_be_visible()
    assert deletes == ["/api/appointments/31"]


@pytest.mark.ui
def test_technician_dashboard_link_and_confirm_complete(page: Page) -> None:
    today = vn_now().date()
    status = "DANG_XU_LY"
    appointments = [{
        "appointment_id": 41, "ticket_id": 101, "ticket_code": "BH-2026-00101",
        "appointment_type": "GIAO", "start_at": f"{today}T15:00:00+07:00", "end_at": f"{today}T15:30:00+07:00",
        "status": "DA_HEN",
    }]
    patches = []

    def mock_api(route) -> None:
        nonlocal status, appointments
        request = route.request
        parsed = urlparse(request.url)
        if parsed.path == "/api/auth/me":
            fulfill(route, 200, TECHNICIAN)
        elif parsed.path == "/api/technicians/me/tickets":
            fulfill(route, 200, [{**ticket_summary(status), "is_overdue": True},
                                 {**ticket_summary("HOAN_TAT"), "ticket_id": 102, "ticket_code": "BH-2026-00102"}])
        elif parsed.path == "/api/tickets/101":
            fulfill(route, 200, ticket_details(5, status))
        elif parsed.path == "/api/tickets/101/appointments":
            fulfill(route, 200, appointments)
        elif parsed.path == "/api/appointments" and request.method == "GET":
            items = [a for a in appointments if a["status"] == "DA_HEN"]
            fulfill(route, 200, {"items": items, "total": len(items), "page": 1, "page_size": 100})
        elif parsed.path == "/api/appointments/41" and request.method == "DELETE":
            appointments = []
            fulfill(route, 200, {"appointment_id": 41, "status": "DA_HUY"})
        elif parsed.path == "/api/tickets/101/status" and request.method == "PATCH":
            patches.append(json.loads(request.post_data))
            status = patches[-1]["to_status"]
            fulfill(route, 200, {"ticket_id": 101, "status": status})
        else:
            fulfill(route, 404, {"message": f"Unexpected request: {parsed.path}"})

    install_token(page, "technician-test-token")
    page.route(API_URL, mock_api)
    # A link from the appointments page opens the ticket directly.
    page.goto(f"{BASE_URL}/my-tickets?ticket=101")
    expect(page.get_by_role("heading", name="BH-2026-00101")).to_be_visible()
    expect(page.locator(".stat", has_text="Đang làm")).to_contain_text("1")
    expect(page.locator(".stat", has_text="Quá hạn")).to_contain_text("1")
    expect(page.locator(".stat", has_text="Đã xong")).to_contain_text("1")
    expect(page.locator(".stat", has_text="Lịch hẹn hôm nay")).to_contain_text("1")

    # Cancel the appointment of the ticket.
    page.locator(".ticket-details").get_by_role("button", name="Hủy lịch").click()
    page.get_by_role("dialog").get_by_role("button", name="Xác nhận hủy lịch").click()
    expect(page.locator(".ticket-details")).to_contain_text("Chưa có lịch hẹn.")
    expect(page.locator(".stat", has_text="Lịch hẹn hôm nay")).to_contain_text("0")

    # Finishing asks first: "Quay lại" changes nothing, "Xác nhận" completes the ticket.
    page.get_by_role("button", name="Hoàn tất").click()
    page.get_by_role("dialog").get_by_role("button", name="Quay lại").click()
    assert patches == []
    page.get_by_role("button", name="Hoàn tất").click()
    page.get_by_role("dialog").get_by_role("button", name="Xác nhận").click()
    expect(page.get_by_role("status")).to_have_text("Đã chuyển trạng thái sang HOÀN TẤT.")
    assert patches == [{"to_status": "HOAN_TAT", "note": ""}]
