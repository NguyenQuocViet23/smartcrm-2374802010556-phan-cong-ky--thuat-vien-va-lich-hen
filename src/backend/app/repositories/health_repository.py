"""Database queries used by health-check endpoints."""

from datetime import datetime

from sqlalchemy import create_engine, text

from app.core.config import get_database_url

engine = create_engine(get_database_url())


def get_database_time() -> datetime:
    """Return the database server time using SELECT NOW()."""
    with engine.connect() as connection:
        return connection.execute(text("SELECT NOW()")).scalar_one()
