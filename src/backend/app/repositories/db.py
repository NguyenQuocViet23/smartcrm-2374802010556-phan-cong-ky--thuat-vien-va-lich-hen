"""Connection helpers: repositories receive the connection these functions open."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy.engine import Connection

from app.core.database import get_engine


@contextmanager
def read_connection() -> Iterator[Connection]:
    """A connection for queries that change nothing."""
    with get_engine().connect() as connection:
        yield connection


@contextmanager
def transaction() -> Iterator[Connection]:
    """One database transaction: committed on success, rolled back on any error."""
    with get_engine().begin() as connection:
        yield connection
