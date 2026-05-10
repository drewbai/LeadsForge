"""Pytest configuration and shared fixtures for the LeadsForge backend tests.

Key guarantees:
* Tests **never** connect to Neon or any production database. The
  ``DATABASE_URL`` environment variable is forced to an in-memory SQLite
  URL **before** any application module is imported.
* Each test gets an ephemeral SQLite (aiosqlite) database with all
  registered ORM tables created via ``Base.metadata.create_all``. No
  Alembic migrations are executed during tests.
* The FastAPI app's database dependencies (``get_db`` / ``get_session``)
  are overridden so endpoints use the per-test session.
* External HTTP calls (httpx.AsyncClient) are blocked at the socket
  layer unless a test explicitly patches ``httpx.AsyncClient`` first.
* Tests for modules not yet merged onto the current branch
  (e.g. tasks/metrics/subscriptions) use ``pytest.importorskip`` and
  skip automatically when those modules are absent.
"""

from __future__ import annotations

import asyncio
import os
import socket
from collections.abc import AsyncIterator, Iterator
from typing import Any

# ---------------------------------------------------------------------------
# Force a safe, offline test environment BEFORE importing application code.
# ---------------------------------------------------------------------------
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ.setdefault("ENV", "test")
os.environ.setdefault("DEBUG", "false")
os.environ.setdefault("APP_NAME", "LeadsForge-Test")
# The background task worker (wired in app.main on startup) would otherwise
# spawn during any test that triggers the FastAPI lifespan, racing fixtures
# and consuming the test session pool. Force-disable it here.
os.environ.setdefault("LEADSFORGE_DISABLE_TASK_WORKER", "1")

import app.models.lead  # noqa: F401  ensure Lead is registered on Base.metadata
import pytest
import pytest_asyncio
from app.db.base import Base
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool


def _try_import_extra_models() -> None:
    """Best-effort registration of optional models so tables exist when present."""
    for module_name in (
        "app.models.subscription",
        "app.models.task",
        "app.models.metric",
    ):
        try:
            __import__(module_name)
        except Exception:
            pass


_try_import_extra_models()


# ---------------------------------------------------------------------------
# Network isolation
# ---------------------------------------------------------------------------
_ALLOWED_HOSTS = {"127.0.0.1", "localhost", "::1", "testserver"}
_real_socket_connect = socket.socket.connect
_real_create_connection = socket.create_connection


def _guarded_connect(self, address, *args, **kwargs):
    host = address[0] if isinstance(address, tuple) else str(address)
    if host not in _ALLOWED_HOSTS:
        raise RuntimeError(f"Blocked outbound network connection to {host!r} during tests")
    return _real_socket_connect(self, address, *args, **kwargs)


def _guarded_create_connection(address, *args, **kwargs):
    host = address[0] if isinstance(address, tuple) else str(address)
    if host not in _ALLOWED_HOSTS:
        raise RuntimeError(f"Blocked outbound network connection to {host!r} during tests")
    return _real_create_connection(address, *args, **kwargs)


@pytest.fixture(autouse=True)
def _block_external_network(monkeypatch):
    monkeypatch.setattr(socket.socket, "connect", _guarded_connect)
    monkeypatch.setattr(socket, "create_connection", _guarded_create_connection)
    yield


# ---------------------------------------------------------------------------
# Event loop
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def event_loop() -> Iterator[asyncio.AbstractEventLoop]:
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ---------------------------------------------------------------------------
# Async DB engine and session
# ---------------------------------------------------------------------------
@pytest_asyncio.fixture
async def test_engine():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    try:
        yield engine
    finally:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()


@pytest_asyncio.fixture
async def session_factory(test_engine):
    return async_sessionmaker(bind=test_engine, expire_on_commit=False)


@pytest_asyncio.fixture
async def db_session(session_factory) -> AsyncIterator[AsyncSession]:
    async with session_factory() as session:
        yield session


# ---------------------------------------------------------------------------
# FastAPI app + DB dependency overrides
# ---------------------------------------------------------------------------
@pytest_asyncio.fixture
async def app_with_db(test_engine, session_factory):
    """Yield the FastAPI app with all DB dependencies pointed at SQLite."""
    from app.main import app

    async def override_get_db() -> AsyncIterator[AsyncSession]:
        async with session_factory() as session:
            yield session

    overrides: dict = {}

    for module_path, attr in (
        ("app.db.engine", "get_session"),
        ("app.db.session", "get_db"),
        ("app.db.session", "get_session"),
        ("app.routers.leads", "get_db"),
        ("app.routers.leads", "get_session"),
    ):
        try:
            mod = __import__(module_path, fromlist=[attr])
            dep = getattr(mod, attr, None)
            if dep is not None:
                overrides[dep] = override_get_db
        except Exception:
            continue

    app.dependency_overrides.update(overrides)
    try:
        yield app
    finally:
        for key in overrides:
            app.dependency_overrides.pop(key, None)


@pytest_asyncio.fixture
async def client(app_with_db) -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app_with_db)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac


# ---------------------------------------------------------------------------
# Seed helpers
# ---------------------------------------------------------------------------
@pytest_asyncio.fixture
async def seeded_lead(db_session: AsyncSession) -> Any:
    from tests.factories.lead_factory import build_lead

    lead = build_lead()
    db_session.add(lead)
    await db_session.commit()
    await db_session.refresh(lead)
    return lead


# ---------------------------------------------------------------------------
# Optional service patches
# ---------------------------------------------------------------------------
@pytest.fixture
def patch_health_session(monkeypatch, session_factory):
    health = pytest.importorskip("app.services.health.service")
    monkeypatch.setattr(health, "AsyncSessionLocal", session_factory, raising=False)
    return session_factory


@pytest.fixture
def patch_dispatcher_session(monkeypatch, session_factory):
    try:
        dispatcher = __import__("app.services.subscriptions.dispatcher", fromlist=["dispatcher"])
    except Exception:
        return None
    monkeypatch.setattr(dispatcher, "AsyncSessionLocal", session_factory, raising=False)
    return dispatcher
