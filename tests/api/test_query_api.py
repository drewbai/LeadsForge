"""API tests for GET /api/v1/leads/search (Phase 76 query engine)."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.asyncio


async def test_leads_search_returns_envelope(client, db_session) -> None:
    from tests.factories.lead_factory import create_lead

    await create_lead(db_session, email="api-find@example.com", source="api-test")

    resp = await client.get("/api/v1/leads/search", params={"text": "api-find"})

    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1
    assert len(body["results"]) == 1
    assert body["results"][0]["email"] == "api-find@example.com"
    assert "filters" in body and "sort" in body
    assert body["limit"] == 50
    assert body["offset"] == 0


async def test_leads_search_validates_limit(client) -> None:
    resp = await client.get("/api/v1/leads/search", params={"limit": 0})
    assert resp.status_code == 422

    resp = await client.get("/api/v1/leads/search", params={"limit": 501})
    assert resp.status_code == 422


async def test_leads_search_negative_offset_rejected(client) -> None:
    resp = await client.get("/api/v1/leads/search", params={"offset": -1})
    assert resp.status_code == 422
