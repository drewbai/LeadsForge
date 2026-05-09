"""Pytest configuration and shared fixtures for the LeadsForge backend tests.

Strategy:
* Each test gets an ephemeral SQLite (aiosqlite) database with all currently
  registered ORM tables created via ``Base.metadata.create_all``.
* The FastAPI app's database dependencies are overridden so endpoints use the
  test session.
* Tests for modules that have not yet been merged into the current branch
  (e.g. tasks/metrics/subscriptions) use ``pytest.importorskip`` and are
  skipped automatically when those modules are absent.
"""
from __future__ import annotations

import asyncio
import os
from collections.abc import AsyncIterator, Iterator
from typing import Any

import pytest
import pytest_asyncio

os.environ.setdefault(
    "DATABASE_URL", "sqlite+aiosqlite:///:memory:"
)

from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

from app.db.base import Base
import app.models.lead  # noqa: F401  ensure Lead is registered on Base.metadata


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


@pytest.fixture(scope="session")
def event_loop() -> Iterator[asyncio.AbstractEventLoop]:
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


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
    """Yield a session; the surrounding ephemeral engine drops state per test."""
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def app_with_db(test_engine, session_factory):
    """FastAPI app instance with all DB-related dependencies overridden."""
    from app.main import app

    async def override_get_session() -> AsyncIterator[AsyncSession]:
        async with session_factory() as session:
            yield session

    overrides: dict = {}

    try:
        from app.db.engine import get_session as engine_get_session

        overrides[engine_get_session] = override_get_session
    except Exception:
        pass

    try:
        from app.routers.leads import get_db as leads_get_db

        overrides[leads_get_db] = override_get_session
    except Exception:
        pass

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


@pytest_asyncio.fixture
async def seeded_lead(db_session: AsyncSession) -> Any:
    """Insert a baseline Lead row and return it."""
    from tests.factories.lead_factory import build_lead

    lead = build_lead()
    db_session.add(lead)
    await db_session.commit()
    await db_session.refresh(lead)
    return lead


@pytest.fixture
def patch_health_session(monkeypatch, session_factory):
    """Force HealthService internal sessions to use the test session factory."""
    health = pytest.importorskip("app.services.health.service")
    monkeypatch.setattr(health, "AsyncSessionLocal", session_factory, raising=False)
    return session_factory


@pytest.fixture
def patch_dispatcher_session(monkeypatch, session_factory):
    """Force subscription dispatcher to use the test session factory (when present)."""
    try:
        dispatcher = __import__(
            "app.services.subscriptions.dispatcher", fromlist=["dispatcher"]
        )
    except Exception:
        return None
    monkeypatch.setattr(dispatcher, "AsyncSessionLocal", session_factory, raising=False)
    return dispatcher
