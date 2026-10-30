"""Health-check application services."""

from datetime import datetime

from app.repositories.health_repository import get_database_time as query_database_time


def get_database_time() -> datetime:
    """Get the current time from the configured database."""
    return query_database_time()
