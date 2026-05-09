"""API tests for /leads endpoints."""
from __future__ import annotations

from unittest.mock import patch

import pytest
from sqlalchemy import select

from app.models.lead import Lead


@pytest.mark.asyncio
async def test_create_lead_endpoint_returns_201(client, db_session) -> None:
    with patch("app.services.lead_service.record_activity_event", create=True):
        resp = await client.post(
            "/leads/",
            json={"email": "api@example.com", "source": "api-test"},
        )
    assert resp.status_code == 201
    body = resp.json()
    assert body["email"] == "api@example.com"
    assert body["source"] == "api-test"
    assert "id" in body
    assert "created_at" in body


@pytest.mark.asyncio
async def test_list_leads_endpoint_returns_seeded(client, db_session) -> None:
    from tests.factories.lead_factory import create_leads

    await create_leads(db_session, count=2)
    resp = await client.get("/leads/")
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)
    assert len(body) == 2


@pytest.mark.asyncio
async def test_get_lead_endpoint_404_for_unknown(client) -> None:
    from uuid import uuid4

    resp = await client.get(f"/leads/{uuid4()}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_lead_endpoint_returns_existing(client, seeded_lead) -> None:
    resp = await client.get(f"/leads/{seeded_lead.id}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == str(seeded_lead.id)


@pytest.mark.asyncio
async def test_create_lead_writes_to_db(client, db_session) -> None:
    with patch("app.services.lead_service.record_activity_event", create=True):
        resp = await client.post(
            "/leads/",
            json={"email": "persisted@example.com", "source": "api-test"},
        )
    assert resp.status_code == 201
    rows = (await db_session.execute(select(Lead))).scalars().all()
    assert any(r.email == "persisted@example.com" for r in rows)
