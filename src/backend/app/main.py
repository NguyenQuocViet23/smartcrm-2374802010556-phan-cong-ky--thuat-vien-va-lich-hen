"""FastAPI application entry point.

This is the only place that turns a ``DomainError`` into an HTTP status.
"""

import logging

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, PlainTextResponse
from sqlalchemy.exc import InterfaceError, OperationalError

from app.core.errors import APIError
from app.domain.errors import DomainError, ErrorKind
from app.routers.appointments import router as appointments_router
from app.routers.auth import router as auth_router
from app.routers.health import router as health_router
from app.routers.technicians import router as technicians_router
from app.routers.tickets import router as tickets_router

logger = logging.getLogger("smartcrm")

HTTP_STATUS = {
    ErrorKind.INVALID: 400,
    ErrorKind.UNAUTHENTICATED: 401,
    ErrorKind.FORBIDDEN: 403,
    ErrorKind.NOT_FOUND: 404,
    ErrorKind.CONFLICT: 409,
    ErrorKind.UNAVAILABLE: 503,
}

app = FastAPI(title="Smart CRM")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["Authorization", "Content-Type"],
)
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(tickets_router)
app.include_router(technicians_router)
app.include_router(appointments_router)


@app.exception_handler(APIError)
def handle_api_error(_, error: APIError) -> JSONResponse:
    return JSONResponse(
        status_code=error.status_code,
        content=jsonable_encoder({
            "error": error.code,
            "message": error.message,
            **error.details,
        }),
    )


def _error_response(status_code: int, code: str, message: str, **details) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder({"error": code, "message": message, **details}),
    )


@app.exception_handler(DomainError)
def handle_domain_error(_, error: DomainError) -> JSONResponse:
    return _error_response(HTTP_STATUS[error.kind], error.code, error.message, **error.details)


@app.exception_handler(OperationalError)
@app.exception_handler(InterfaceError)
def handle_database_unavailable(_, error: Exception) -> JSONResponse:
    logger.error("Database unavailable: %s", error.__class__.__name__)
    return _error_response(
        HTTP_STATUS[ErrorKind.UNAVAILABLE],
        "DATABASE_UNAVAILABLE",
        "Cơ sở dữ liệu tạm thời không khả dụng. Vui lòng thử lại sau.",
    )


@app.exception_handler(Exception)
def handle_unexpected_error(_, error: Exception) -> JSONResponse:
    logger.exception("Unhandled error")
    return _error_response(
        500, "INTERNAL_ERROR", "Hệ thống gặp sự cố ngoài dự kiến. Vui lòng thử lại sau."
    )


@app.exception_handler(RequestValidationError)
def handle_validation_error(_, error: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={
            "error": "VALIDATION_ERROR",
            "message": "Dữ liệu gửi lên không hợp lệ.",
            "fields": [
                {"field": ".".join(str(part) for part in item["loc"]), "message": item["msg"]}
                for item in error.errors()
            ],
        },
    )


@app.get("/", response_class=PlainTextResponse)
def root() -> str:
    """Return the backend greeting."""
    return "Hello Smart CRM"
