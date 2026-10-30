"""Response schemas for health-check routes."""

from datetime import datetime

from pydantic import BaseModel


class DatabaseCheckResponse(BaseModel):
    """Database connectivity check result."""

    database_time: datetime
