"""Tests for app.services.ranking.engine."""

from __future__ import annotations

import pytest
from app.models.lead import Lead
from app.services.ranking import engine as ranking_engine
from sqlalchemy import select


@pytest.mark.asyncio
async def test_compute_lead_ranking_returns_score(db_session, seeded_lead) -> None:
    result = await ranking_engine.compute_lead_ranking(db_session, seeded_lead.id)
    assert result is not None
    assert result["lead_id"] == str(seeded_lead.id)
    assert 0.0 <= result["ranking_score"] <= 100.0
    assert "components" in result
    expected_components = {
        "activity",
        "recency",
        "enrichment",
        "ai_insights",
        "ai_summary",
    }
    assert expected_components.issubset(set(result["components"].keys()))
    assert "weights" in result and result["weights"] == ranking_engine.RANKING_WEIGHTS


@pytest.mark.asyncio
async def test_compute_lead_ranking_persists_fields(db_session, seeded_lead) -> None:
    await ranking_engine.compute_lead_ranking(db_session, seeded_lead.id)
    refreshed = (await db_session.execute(select(Lead).where(Lead.id == seeded_lead.id))).scalar_one()
    assert refreshed.ranking_score is not None
    assert refreshed.ranking_explanation is not None
    assert refreshed.last_ranked_at is not None


@pytest.mark.asyncio
async def test_compute_lead_ranking_returns_none_for_missing_lead(db_session) -> None:
    from uuid import uuid4

    result = await ranking_engine.compute_lead_ranking(db_session, uuid4())
    assert result is None


@pytest.mark.asyncio
async def test_recompute_all_handles_empty_db(db_session) -> None:
    summary = await ranking_engine.recompute_ranking_for_all_leads(db_session)
    assert summary == {"total": 0, "success": 0, "failed": 0}


@pytest.mark.asyncio
async def test_recompute_all_processes_every_lead(db_session) -> None:
    from tests.factories.lead_factory import create_leads

    await create_leads(db_session, count=3)
    summary = await ranking_engine.recompute_ranking_for_all_leads(db_session)
    assert summary["total"] == 3
    assert summary["success"] == 3
    assert summary["failed"] == 0
