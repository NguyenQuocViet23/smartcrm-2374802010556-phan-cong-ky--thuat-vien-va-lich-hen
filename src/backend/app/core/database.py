"""Shared SQLAlchemy engine for application requests."""

import os
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from app.core.config import get_database_url


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    # Without a timeout, connecting to a database that is down can hang for minutes
    # (BUG-07); with it the API answers 503 DATABASE_UNAVAILABLE within seconds.
    timeout = int(os.getenv("DB_CONNECT_TIMEOUT", "3"))
    return create_engine(
        get_database_url(), pool_pre_ping=True, connect_args={"connect_timeout": timeout}
    )
