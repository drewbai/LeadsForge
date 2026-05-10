"""Service-level tests for app.services.query.engine.search_leads."""

from __future__ import annotations

import pytest
from app.services.query.engine import search_leads

from tests.factories.lead_factory import create_lead

pytestmark = pytest.mark.asyncio


async def test_search_leads_empty_db(db_session) -> None:
    out = await search_leads(db_session)
    assert out["total"] == 0
    assert out["results"] == []
    assert out["limit"] == 50
    assert out["offset"] == 0


async def test_search_leads_text_matches_email(db_session) -> None:
    await create_lead(db_session, email="findme-special@example.com", source="a")
    await create_lead(db_session, email="other@example.com", source="b")

    out = await search_leads(db_session, text="findme-special")

    assert out["total"] == 1
    assert len(out["results"]) == 1
    assert out["results"][0]["email"] == "findme-special@example.com"


async def test_search_leads_source_filter(db_session) -> None:
    await create_lead(db_session, email="x1@example.com", source="webinar")
    await create_lead(db_session, email="x2@example.com", source="signup")

    out = await search_leads(db_session, source="webinar")

    assert out["total"] == 1
    assert out["results"][0]["source"] == "webinar"


async def test_search_leads_score_range(db_session) -> None:
    await create_lead(db_session, email="lo@example.com", ranking_score=10.0)
    await create_lead(db_session, email="mid@example.com", ranking_score=55.0)
    await create_lead(db_session, email="hi@example.com", ranking_score=90.0)

    out = await search_leads(db_session, min_score=40.0, max_score=80.0)

    assert out["total"] == 1
    assert out["results"][0]["email"] == "mid@example.com"


async def test_search_leads_pagination(db_session) -> None:
    for i in range(5):
        await create_lead(db_session, email=f"p{i}@example.com", source="batch")

    page1 = await search_leads(db_session, limit=2, offset=0, sort_by="email", sort_dir="asc")
    page2 = await search_leads(db_session, limit=2, offset=2, sort_by="email", sort_dir="asc")

    assert page1["total"] == 5
    assert len(page1["results"]) == 2
    assert len(page2["results"]) == 2
    emails_p1 = {r["email"] for r in page1["results"]}
    emails_p2 = {r["email"] for r in page2["results"]}
    assert emails_p1.isdisjoint(emails_p2)


async def test_search_leads_includes_filters_echo(db_session) -> None:
    await create_lead(db_session)
    out = await search_leads(db_session, text="  zzz  ", source=None, min_score=1.0, limit=10, offset=3)

    assert out["filters"]["text"] == "  zzz  "
    assert out["filters"]["min_score"] == 1.0
    assert out["limit"] == 10
    assert out["offset"] == 3
    assert out["sort"]["sort_by"] == "created_at"
