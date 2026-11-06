"""The web layer turns domain and infrastructure failures into clear JSON answers."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from app.core.security import create_access_token
from app.domain.errors import DomainError, ErrorKind
from app.main import HTTP_STATUS, app
from app.services import ticket_service

MANAGER = {
    "username": "QL_TT01", "role": "QUAN_LY", "center_id": 1, "center_name": "TTBH",
    "technician_id": None, "full_name": "Quản lý", "employee_id": 1,
}


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("SECRET_KEY", "x" * 32)
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def headers(client: TestClient) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token(MANAGER)}"}


@pytest.mark.parametrize(
    ("kind", "status"),
    [(ErrorKind.INVALID, 400), (ErrorKind.UNAUTHENTICATED, 401), (ErrorKind.FORBIDDEN, 403),
     (ErrorKind.NOT_FOUND, 404), (ErrorKind.CONFLICT, 409), (ErrorKind.UNAVAILABLE, 503)],
)
def test_every_error_kind_has_one_http_status(kind: ErrorKind, status: int) -> None:
    """Luồng đúng: mỗi loại lỗi nghiệp vụ ứng với đúng một mã HTTP, chỉ khai báo ở lớp web"""
    assert HTTP_STATUS[kind] == status


def test_domain_error_keeps_code_message_and_details(client, headers, monkeypatch) -> None:
    """Luồng đúng: lỗi nghiệp vụ trả mã lỗi, thông báo và chi tiết của service"""
    def broken(*_args, **_kwargs):
        raise DomainError(ErrorKind.CONFLICT, "APPOINTMENT_OVERLAP", "Trùng lịch.", conflicts=[1])

    monkeypatch.setattr(ticket_service, "technician_suggestions", broken)
    response = client.get("/api/tickets/1/technician-suggestions", headers=headers)

    assert response.status_code == 409
    assert response.json() == {"error": "APPOINTMENT_OVERLAP", "message": "Trùng lịch.", "conflicts": [1]}


def test_database_down_answers_503_without_raw_error(client, headers, monkeypatch) -> None:
    """Dữ liệu sai / sự cố: CSDL tắt thì trả 503 với thông báo rõ, không lộ lỗi thô của thư viện"""
    def database_down(*_args, **_kwargs):
        raise OperationalError("SELECT 1", {}, Exception("connection refused on port 5432"))

    monkeypatch.setattr(ticket_service, "list_tickets", database_down)
    response = client.get("/api/tickets", headers=headers)

    assert response.status_code == 503
    body = response.json()
    assert body["error"] == "DATABASE_UNAVAILABLE"
    assert "5432" not in response.text and "SELECT" not in response.text


def test_unexpected_error_answers_500_without_traceback(client, headers, monkeypatch) -> None:
    """Giá trị biên: lỗi ngoài dự kiến trả 500 INTERNAL_ERROR, không lộ traceback"""
    def bug(*_args, **_kwargs):
        raise KeyError("secret_internal_detail")

    monkeypatch.setattr(ticket_service, "list_tickets", bug)
    response = client.get("/api/tickets", headers=headers)

    assert response.status_code == 500
    assert response.json()["error"] == "INTERNAL_ERROR"
    assert "secret_internal_detail" not in response.text and "Traceback" not in response.text


def test_invalid_ticket_payload_is_rejected_before_the_service(client, headers, monkeypatch) -> None:
    """Dữ liệu sai: tạo phiếu thiếu trường bắt buộc trả 400 VALIDATION_ERROR, service không được gọi"""
    monkeypatch.setattr(ticket_service, "create_ticket", lambda *_: pytest.fail("service called"))
    response = client.post("/api/tickets", headers=headers, json={"customer_name": "A"})

    assert response.status_code == 400
    assert response.json()["error"] == "VALIDATION_ERROR"
