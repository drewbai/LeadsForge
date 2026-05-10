"""Tests for GET /api/v1/ranking/{lead_id}/status (Phase 73)."""

from __future__ import annotations

from uuid import uuid4

import pytest


@pytest.mark.asyncio
async def test_ranking_status_returns_404_for_missing_lead(client) -> None:
    response = await client.get(f"/api/v1/ranking/{uuid4()}/status")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_ranking_status_returns_payload_for_existing_lead(client, seeded_lead) -> None:
    response = await client.get(f"/api/v1/ranking/{seeded_lead.id}/status")
    assert response.status_code == 200

    body = response.json()
    assert body["lead_id"] == str(seeded_lead.id)
    assert "ranking_score" in body
    assert "last_ranked_at" in body
    assert body["ranking_score"] is None
    assert body["last_ranked_at"] is None


@pytest.mark.asyncio
async def test_ranking_status_returns_persisted_score(client, db_session, seeded_lead) -> None:
    from datetime import datetime, timezone

    seeded_lead.ranking_score = 87.5
    seeded_lead.last_ranked_at = datetime(2026, 5, 9, 12, 0, 0, tzinfo=timezone.utc)
    db_session.add(seeded_lead)
    await db_session.commit()

    response = await client.get(f"/api/v1/ranking/{seeded_lead.id}/status")
    assert response.status_code == 200

    body = response.json()
    assert body["ranking_score"] == 87.5
    assert body["last_ranked_at"] is not None
    assert body["last_ranked_at"].startswith("2026-05-09T12:00:00")
