"""Database configuration for the Smart CRM backend."""

import os

from dotenv import load_dotenv
from sqlalchemy import URL, make_url

load_dotenv()


def get_database_url() -> URL:
    """Build the PostgreSQL connection URL from environment variables."""
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        url = make_url(database_url)
        if url.drivername in {"postgres", "postgresql"}:
            url = url.set(drivername="postgresql+psycopg")
        return url
    return URL.create(
        drivername="postgresql+psycopg",
        username=os.getenv("DB_USER") or None,
        password=os.getenv("DB_PASSWORD") or None,
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NAME", "smartcrm"),
    )
