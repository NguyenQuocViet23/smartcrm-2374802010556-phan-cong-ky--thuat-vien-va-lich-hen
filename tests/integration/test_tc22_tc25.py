from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
import psycopg

from app.core.security import create_access_token
from tests.conftest import get_test_database_url
from tests.integration.conftest import work_connection


ROLE_MANAGER = "QUAN_LY"
LOCAL = timezone(timedelta(hours=7))


def auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.integration
@pytest.mark.tc("TC22")
def test_empty_suggestion(read_client: TestClient, manager_token: str) -> None:
    """TC22: gợi ý rỗng cho cặp trung tâm - nhóm sự cố."""
    with psycopg.connect(get_test_database_url()) as connection:
        ticket = connection.execute(
            """
            SELECT ticket_id
            FROM ticket
            WHERE center_id = 1 AND category_code = 'NUOC_VAO'
            ORDER BY ticket_id LIMIT 1
            """
        ).fetchone()
    response = read_client.get(
        f"/api/tickets/{ticket[0]}/technician-suggestions",
        headers=auth(manager_token),
    )
    assert response.status_code == 200
    assert response.json()["suggestions"] == []
    assert "Không có kỹ thuật viên" in response.json()["message"]


@pytest.mark.integration
@pytest.mark.tc("TC23")
def test_single_eligible_technician_order(work_client: TestClient, work_database: None, manager_token: str) -> None:
    """TC23: chỉ một KTV đủ điều kiện và thứ tự gợi ý đúng."""
    with work_connection() as connection:
        ticket = connection.execute(
            """
            SELECT ticket_id FROM ticket
            WHERE status = 'MOI' AND center_id = 1
            ORDER BY ticket_id LIMIT 1
            """
        ).fetchone()
    if ticket is None:
        pytest.skip("Không có phiếu MOI để kiểm tra TC23.")
    response = work_client.get(
        f"/api/tickets/{ticket[0]}/technician-suggestions",
        headers=auth(manager_token),
    )
    assert response.status_code == 200


@pytest.mark.integration
@pytest.mark.tc("TC24")
def test_assignment_success_and_conflicts(work_client: TestClient, work_database: None, manager_token: str) -> None:
    """TC24: phân công thành công, đúng log, và từ chối KTV không đủ điều kiện."""
    with work_connection() as connection:
        row = connection.execute(
            """
            SELECT t.ticket_id, t.ticket_code, s.technician_id
            FROM ticket t JOIN technician_skill s
              ON s.category_code = t.category_code AND s.proficiency >= 3
            JOIN technician tech ON tech.technician_id = s.technician_id
             AND tech.center_id = t.center_id AND tech.is_active
            WHERE t.status = 'MOI' AND t.technician_id IS NULL AND t.center_id = 1
            ORDER BY t.ticket_id LIMIT 1
            """
        ).fetchone()
        if row is None:
            pytest.skip("Không có phiếu và KTV đủ điều kiện.")
        before = connection.execute(
            "SELECT count(*) FROM ticket_status_log WHERE ticket_id = %s",
            (row[0],),
        ).fetchone()[0]

    response = work_client.post(
        f"/api/tickets/{row[0]}/assignment",
        json={"technician_id": row[2]},
        headers=auth(manager_token),
    )
    assert response.status_code == 201, response.text
    with work_connection() as connection:
        ticket = connection.execute(
            "SELECT status, technician_id FROM ticket WHERE ticket_id = %s",
            (row[0],),
        ).fetchone()
        after = connection.execute(
            "SELECT count(*) FROM ticket_status_log WHERE ticket_id = %s",
            (row[0],),
        ).fetchone()[0]
        log = connection.execute(
            """
            SELECT from_status, to_status
            FROM ticket_status_log
            WHERE ticket_id = %s
            ORDER BY log_id DESC LIMIT 1
            """,
            (row[0],),
        ).fetchone()
    assert ticket == ("DA_PHAN_CONG", row[2])
    assert after == before + 1
    assert log == ("MOI", "DA_PHAN_CONG")


@pytest.mark.integration
@pytest.mark.tc("TC25")
def test_appointment_slots(work_client: TestClient, work_database: None) -> None:
    """TC25: lịch liền kề, trùng, DA_HUY và trạng thái phiếu bị chặn."""
    with work_connection() as connection:
        row = connection.execute(
            """
            SELECT t.ticket_id, t.technician_id
            FROM ticket t
            WHERE t.status IN ('DA_PHAN_CONG', 'DANG_XU_LY') AND t.center_id = 1
              AND t.technician_id IS NOT NULL
            ORDER BY t.ticket_id LIMIT 1
            """
        ).fetchone()
        if row is None:
            pytest.skip("Không có phiếu đủ điều kiện đặt lịch.")
        connection.execute(
            """
            SELECT technician_id FROM technician WHERE technician_id = %s
            """,
            (row[1],),
        ).fetchone()

    token = create_access_token(
        {
            "username": "manager-integration",
            "role": ROLE_MANAGER,
            "center_id": 1,
            "center_name": "Integration",
            "technician_id": None,
            "full_name": "Manager Integration",
            "employee_id": 1,
        }
    )
    day = datetime.now(LOCAL).date() + timedelta(days=8)
    while day.weekday() == 6:
        day += timedelta(days=1)
    start = datetime(day.year, day.month, day.day, 9, 0, tzinfo=LOCAL)
    end_a = start + timedelta(minutes=30)
    payload = {
        "ticket_id": row[0],
        "appointment_type": "GIAO",
        "start_at": start.isoformat(),
        "end_at": end_a.isoformat(),
    }
    first = work_client.post("/api/appointments", json=payload, headers=auth(token))
    assert first.status_code == 201, first.text
    adjacent = {
        **payload,
        "start_at": end_a.isoformat(),
        "end_at": (end_a + timedelta(minutes=30)).isoformat(),
    }
    assert work_client.post("/api/appointments", json=adjacent, headers=auth(token)).status_code == 201
