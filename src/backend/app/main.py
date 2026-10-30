"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, PlainTextResponse

from app.core.errors import APIError
from app.routers.appointments import router as appointments_router
from app.routers.auth import router as auth_router
from app.routers.health import router as health_router
from app.routers.technicians import router as technicians_router
from app.routers.tickets import router as tickets_router

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
