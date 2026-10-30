"""Authentication helpers for the local demo-account workflow."""

from __future__ import annotations

import base64
import binascii
import hashlib
import hmac
import json
import os
import time
from pathlib import Path
from typing import Any

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.errors import APIError

ROOT = Path(__file__).resolve().parents[4]
ACCOUNTS_PATH = ROOT / "data" / "processed" / "demo_accounts.json"
bearer = HTTPBearer(auto_error=False)


def _b64encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _b64decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def create_access_token(account: dict[str, Any]) -> str:
    secret = os.getenv("SECRET_KEY", "")
    if len(secret) < 32:
        raise RuntimeError("SECRET_KEY must contain at least 32 characters.")
    encoded_header = _b64encode(
        json.dumps({"alg": "HS256", "typ": "JWT"}, separators=(",", ":")).encode("ascii")
    )
    payload = {
        "sub": account["username"],
        "role": account["role"],
        "center_id": account["center_id"],
        "center_name": account.get("center_name"),
        "technician_id": account.get("technician_id"),
        "full_name": account["full_name"],
        "employee_id": account["employee_id"],
        "exp": int(time.time()) + 8 * 60 * 60,
    }
    encoded_payload = _b64encode(
        json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    )
    signing_input = f"{encoded_header}.{encoded_payload}".encode("ascii")
    signature = hmac.new(secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
    return f"{encoded_header}.{encoded_payload}.{_b64encode(signature)}"


def decode_access_token(token: str) -> dict[str, Any]:
    secret = os.getenv("SECRET_KEY", "")
    try:
        encoded_header, encoded_payload, encoded_signature = token.split(".")
        header = json.loads(_b64decode(encoded_header))
        if header != {"alg": "HS256", "typ": "JWT"} or len(secret) < 32:
            raise ValueError("invalid token header or server secret")
        expected = hmac.new(
            secret.encode("utf-8"),
            f"{encoded_header}.{encoded_payload}".encode("ascii"),
            hashlib.sha256,
        ).digest()
        if not hmac.compare_digest(expected, _b64decode(encoded_signature)):
            raise ValueError("invalid token signature")
        payload = json.loads(_b64decode(encoded_payload))
        if int(payload["exp"]) <= int(time.time()):
            raise ValueError("expired token")
        return payload
    except (ValueError, KeyError, TypeError, binascii.Error, json.JSONDecodeError) as exc:
        raise APIError(401, "INVALID_TOKEN", "Phiên đăng nhập không hợp lệ.") from exc


def verify_password(password: str, encoded: str) -> bool:
    try:
        scheme, rounds, salt, expected = encoded.split("$", 3)
        if scheme != "pbkdf2_sha256":
            return False
        actual = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt.encode("ascii"), int(rounds)
        ).hex()
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def load_demo_accounts() -> list[dict[str, Any]]:
    try:
        payload = json.loads(ACCOUNTS_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RuntimeError(
            "Demo accounts are missing; run scripts/seed_real_data.py first."
        ) from exc
    accounts = payload.get("accounts")
    if not isinstance(accounts, list):
        raise RuntimeError("demo_accounts.json must contain an accounts array.")
    return accounts


def authenticate(username: str, password: str) -> dict[str, Any] | None:
    for account in load_demo_accounts():
        if account.get("username") == username and verify_password(
            password, account.get("password_hash", "")
        ):
            return account
    return None


def current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> dict[str, Any]:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise APIError(401, "UNAUTHORIZED", "Vui lòng đăng nhập.")
    return decode_access_token(credentials.credentials)


def require_role(*roles: str):
    def dependency(user: dict[str, Any] = Depends(current_user)) -> dict[str, Any]:
        if user.get("role") not in roles:
            raise APIError(403, "FORBIDDEN", "Bạn không có quyền thực hiện thao tác này.")
        return user

    return dependency
