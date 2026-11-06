"""Business-rule failures, described without any web-layer detail.

A service raises ``DomainError``; only the web layer (``app/main.py``) decides
which response status each ``ErrorKind`` becomes.
"""

from __future__ import annotations

from enum import Enum
from typing import Any


class ErrorKind(str, Enum):
    INVALID = "invalid"                  # the input breaks a business rule
    UNAUTHENTICATED = "unauthenticated"  # who is asking is unknown
    FORBIDDEN = "forbidden"              # known user, not allowed to do this
    NOT_FOUND = "not_found"              # the target record does not exist
    CONFLICT = "conflict"                # valid input, but the current state forbids it
    UNAVAILABLE = "unavailable"          # a dependency (e.g. the database) is down


class DomainError(Exception):
    """A rule was broken. ``code`` is the stable machine-readable error code."""

    def __init__(self, kind: ErrorKind, code: str, message: str, **details: Any) -> None:
        super().__init__(message)
        self.kind = kind
        self.code = code
        self.message = message
        self.details = details
