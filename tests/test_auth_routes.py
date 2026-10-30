"""HTTP-level tests for authentication boundary behavior."""

from fastapi.testclient import TestClient

from app.main import app
from app.routers import auth

client = TestClient(app)


def test_me_requires_a_bearer_token() -> None:
    response = client.get("/api/auth/me")

    assert response.status_code == 401
    assert response.json()["error"] == "UNAUTHORIZED"


def test_ticket_api_requires_a_bearer_token() -> None:
    response = client.get("/api/tickets")

    assert response.status_code == 401
    assert response.json()["error"] == "UNAUTHORIZED"


def test_invalid_credentials_return_the_srs_error(monkeypatch) -> None:
    monkeypatch.setattr(auth, "authenticate", lambda username, password: None)

    response = client.post(
        "/api/auth/login",
        json={"username": "not-a-real-account", "password": "incorrect"},
    )

    assert response.status_code == 401
    assert response.json() == {
        "error": "INVALID_CREDENTIALS",
        "message": "Sai tên đăng nhập hoặc mật khẩu",
    }


def test_bad_request_body_uses_contract_validation_error() -> None:
    response = client.post("/api/auth/login", json={"username": "", "password": ""})

    assert response.status_code == 400
    assert response.json()["error"] == "VALIDATION_ERROR"


def test_srs_endpoints_are_registered() -> None:
    paths = client.get("/openapi.json").json()["paths"]

    assert "/api/auth/login" in paths
    assert "/api/auth/me" in paths
    assert "/api/tickets/{ticket_id}/technician-suggestions" in paths
    assert "/api/tickets/{ticket_id}/assignment" in paths
    assert "/api/appointments" in paths
    assert "/api/tickets/{ticket_id}/status" in paths


def test_cors_allows_the_vite_origin() -> None:
    response = client.options(
        "/api/tickets",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
