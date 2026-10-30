"""Calendar and working-hour validation independent of database fixtures."""

from datetime import datetime, time, timedelta

import pytest

from app.core.errors import APIError
from app.routers.appointments import LOCAL_TIME, _validate_slot


def _next_business_date(days_ahead: int = 35):
    candidate = datetime.now(LOCAL_TIME).date() + timedelta(days=days_ahead)
    while candidate.weekday() == 6:
        candidate += timedelta(days=1)
    return candidate


def test_valid_future_half_hour_at_start_of_working_day() -> None:
    appointment_date = _next_business_date()
    start = datetime.combine(appointment_date, time(8), tzinfo=LOCAL_TIME)
    end = start + timedelta(minutes=30)

    validated_start, validated_end = _validate_slot(start, end)

    assert validated_start == start
    assert validated_end == end


def test_adjacent_half_hour_can_end_at_closing_time() -> None:
    appointment_date = _next_business_date()
    start = datetime.combine(appointment_date, time(17, 30), tzinfo=LOCAL_TIME)
    end = datetime.combine(appointment_date, time(18), tzinfo=LOCAL_TIME)

    assert _validate_slot(start, end) == (start, end)


def test_sunday_appointment_is_rejected() -> None:
    appointment_date = _next_business_date()
    while appointment_date.weekday() != 6:
        appointment_date += timedelta(days=1)
    start = datetime.combine(appointment_date, time(9), tzinfo=LOCAL_TIME)

    with pytest.raises(APIError) as error:
        _validate_slot(start, start + timedelta(minutes=30))

    assert error.value.status_code == 400
    assert error.value.code == "OUTSIDE_WORKING_HOURS"
