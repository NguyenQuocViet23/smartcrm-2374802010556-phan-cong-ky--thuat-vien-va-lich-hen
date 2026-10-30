"""Health-check HTTP routes."""

from fastapi import APIRouter

from app.schemas.health import DatabaseCheckResponse
from app.services.health_service import get_database_time

router = APIRouter()


@router.get("/db-check", response_model=DatabaseCheckResponse)
def check_database() -> DatabaseCheckResponse:
    """Verify database connectivity and return the database server time."""
    return DatabaseCheckResponse(database_time=get_database_time())
