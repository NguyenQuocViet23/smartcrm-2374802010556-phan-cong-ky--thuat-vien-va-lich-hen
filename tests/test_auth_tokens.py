"""Offline tests for signed demo-session tokens."""

import pytest

from app.core.errors import APIError
from app.core.security import create_access_token, decode_access_token


def test_token_contains_the_required_user_claims(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SECRET_KEY", "local-test-secret-key-with-at-least-32-chars")
    account = {
        "username": "KTV_SAMPLE",
        "role": "KY_THUAT_VIEN",
        "center_id": 1,
        "technician_id": 7,
        "full_name": "Kỹ thuật viên",
        "employee_id": 7,
    }

    claims = decode_access_token(create_access_token(account))

    assert {key: claims[key] for key in account if key != "username"} == {
        key: value for key, value in account.items() if key != "username"
    }
    assert claims["sub"] == account["username"]
    assert claims["exp"] > 0


def test_token_rejects_bad_signature(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SECRET_KEY", "local-test-secret-key-with-at-least-32-chars")

    with pytest.raises(APIError) as error:
        decode_access_token("v1.e30.invalid")

    assert error.value.status_code == 401
    assert error.value.code == "INVALID_TOKEN"


def test_signing_requires_a_configured_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SECRET_KEY", raising=False)
    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        create_access_token(
            {
                "username": "x",
                "role": "QUAN_LY",
                "center_id": 1,
                "technician_id": None,
                "full_name": "Manager",
                "employee_id": 1,
            }
        )
