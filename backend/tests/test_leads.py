from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.main import app
from app.routers.leads import get_db


@pytest.mark.anyio
async def test_leads_crud() -> None:
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

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        create_response = await client.post(
            "/leads/",
            json={"email": "lead@example.com", "source": "test"},
        )
        assert create_response.status_code == 201
        created_lead = create_response.json()

        list_response = await client.get("/leads/")
        assert list_response.status_code == 200
        assert list_response.json() == [created_lead]

        get_response = await client.get(f"/leads/{created_lead['id']}")
        assert get_response.status_code == 200
        assert get_response.json() == created_lead

        delete_response = await client.delete(f"/leads/{created_lead['id']}")
        assert delete_response.status_code == 204

        get_missing = await client.get(f"/leads/{created_lead['id']}")
        assert get_missing.status_code == 404

        list_after = await client.get("/leads/")
        assert list_after.status_code == 200
        assert list_after.json() == []

    app.dependency_overrides.clear()

    await engine.dispose()
