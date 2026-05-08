from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.main import app
from app.routers.ingestion import get_db as ingestion_get_db
from app.routers.leads import get_db as leads_get_db


@pytest.mark.anyio
async def test_manual_ingestion_creates_leads(tmp_path) -> None:
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        poolclass=StaticPool,
    )
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    async def override_get_db() -> AsyncIterator[AsyncSession]:
        async with session_factory() as session:
            yield session

    app.dependency_overrides[ingestion_get_db] = override_get_db
    app.dependency_overrides[leads_get_db] = override_get_db

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/ingestion/manual",
            json={"leads": [{"email": "Lead@Example.com ", "source": " Manual "}]},
        )
        assert response.status_code == 200
        assert response.json() == [{"success": True, "errors": []}]

        leads_response = await client.get("/leads/")
        assert leads_response.status_code == 200
        leads = leads_response.json()
        assert len(leads) == 1
        assert leads[0]["email"] == "lead@example.com"
        assert leads[0]["source"] == "manual"

    app.dependency_overrides.clear()
    await engine.dispose()


@pytest.mark.anyio
async def test_invalid_manual_ingestion_returns_errors_and_creates_nothing(tmp_path) -> None:
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        poolclass=StaticPool,
    )
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    async def override_get_db() -> AsyncIterator[AsyncSession]:
        async with session_factory() as session:
            yield session

    app.dependency_overrides[ingestion_get_db] = override_get_db
    app.dependency_overrides[leads_get_db] = override_get_db

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/ingestion/manual",
            json={
                "leads": [
                    {"email": "", "source": "manual"},
                    {"email": "lead@example.com", "source": ""},
                ]
            },
        )
        assert response.status_code == 200
        assert response.json() == [
            {"success": False, "errors": ["email is required"]},
            {"success": False, "errors": ["source is required"]},
        ]

        leads_response = await client.get("/leads/")
        assert leads_response.status_code == 200
        assert leads_response.json() == []

    app.dependency_overrides.clear()
    await engine.dispose()


@pytest.mark.anyio
async def test_csv_ingestion_creates_valid_rows(tmp_path) -> None:
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        poolclass=StaticPool,
    )
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    csv_file = tmp_path / "leads.csv"
    csv_file.write_text("email,source\nLead@One.com,CSV\n", encoding="utf-8")

    async def override_get_db() -> AsyncIterator[AsyncSession]:
        async with session_factory() as session:
            yield session

    app.dependency_overrides[ingestion_get_db] = override_get_db
    app.dependency_overrides[leads_get_db] = override_get_db

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/ingestion/csv",
            json={"file_path": str(csv_file)},
        )
        assert response.status_code == 200
        assert response.json() == [{"success": True, "errors": []}]

        leads_response = await client.get("/leads/")
        assert leads_response.status_code == 200
        leads = leads_response.json()
        assert len(leads) == 1
        assert leads[0]["email"] == "lead@one.com"
        assert leads[0]["source"] == "csv"

    app.dependency_overrides.clear()
    await engine.dispose()
