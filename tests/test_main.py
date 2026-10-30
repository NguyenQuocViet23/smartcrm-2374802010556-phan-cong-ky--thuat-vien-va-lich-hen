"""Tests for the FastAPI application entry point."""

from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.main import app
from app.routers import health

client = TestClient(app)


def test_root_returns_greeting() -> None:
    """The root endpoint returns the expected greeting."""
    response = client.get("/")

    assert response.status_code == 200
    assert response.text == "Hello Smart CRM"


def test_database_check_returns_database_time(monkeypatch) -> None:
    """The database check route returns the time supplied by its service."""
    database_time = datetime(2026, 10, 22, 8, 0, tzinfo=timezone.utc)
    monkeypatch.setattr(health, "get_database_time", lambda: database_time)

    response = client.get("/db-check")

    assert response.status_code == 200
    assert response.json() == {"database_time": "2026-10-22T08:00:00Z"}
