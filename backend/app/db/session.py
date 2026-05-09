"""Compatibility shim that re-exports DB session helpers.

This module exists so callers (and tests) can import a single, stable name
``get_db`` regardless of whether code was written against ``app.db.engine``
or ``app.db.session``.

Tests should override ``get_db`` here (and ``get_session`` in
``app.db.engine``) via ``app.dependency_overrides`` to inject an
in-memory SQLite session.
"""

from __future__ import annotations

from app.db.engine import AsyncSessionLocal, engine, get_session

get_db = get_session

__all__ = ["AsyncSessionLocal", "engine", "get_db", "get_session"]
