"""Demo-account login and current-user endpoints."""

from typing import Any

from fastapi import APIRouter, Depends

from app.core.errors import APIError
from app.core.security import authenticate, create_access_token, current_user
from app.schemas.auth import LoginRequest, TokenResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest) -> TokenResponse:
    try:
        account = authenticate(payload.username, payload.password)
    except RuntimeError as error:
        raise APIError(503, "DEMO_ACCOUNTS_NOT_READY", str(error)) from error
    if account is None:
        raise APIError(401, "INVALID_CREDENTIALS", "Sai tên đăng nhập hoặc mật khẩu")
    try:
        access_token = create_access_token(account)
    except RuntimeError as error:
        raise APIError(503, "AUTH_CONFIGURATION_ERROR", str(error)) from error
    return TokenResponse(access_token=access_token)


@router.get("/me")
def get_me(user: dict[str, Any] = Depends(current_user)) -> dict[str, Any]:
    return {
        key: user.get(key)
        for key in (
            "role",
            "center_id",
            "center_name",
            "technician_id",
            "full_name",
            "employee_id",
        )
    }
