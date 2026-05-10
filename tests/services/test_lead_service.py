"""Tests for app.services.lead_service."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from app.models.lead import Lead
from app.schemas.lead import LeadCreate
from app.services import lead_service
from sqlalchemy import select


@pytest.mark.asyncio
async def test_create_lead_persists_row(db_session) -> None:
    payload = LeadCreate(email="alice@example.com", source="signup")

    with (
        patch.object(
            lead_service,
            "record_activity_event",
            create=True,
            new_callable=AsyncMock,
        ) as activity_hook,
        patch.object(
            lead_service,
            "enqueue_ranking_recompute",
            new_callable=AsyncMock,
        ) as ranking_hook,
    ):
        lead = await lead_service.create_lead(db_session, payload)

    assert lead.id is not None
    assert lead.email == "alice@example.com"
    assert lead.source == "signup"

    if activity_hook.called:
        kwargs = activity_hook.call_args.kwargs
        assert kwargs.get("event_type") == "lead.created"
        assert kwargs.get("lead_id") == lead.id

    ranking_hook.assert_awaited_once_with(lead.id)

    rows = (await db_session.execute(select(Lead))).scalars().all()
    assert len(rows) == 1
    assert rows[0].email == "alice@example.com"


@pytest.mark.asyncio
async def test_get_lead_returns_existing(db_session, seeded_lead) -> None:
    found = await lead_service.get_lead(db_session, seeded_lead.id)
    assert found is not None
    assert found.id == seeded_lead.id


@pytest.mark.asyncio
async def test_get_lead_returns_none_when_missing(db_session) -> None:
    from uuid import uuid4

    found = await lead_service.get_lead(db_session, uuid4())
    assert found is None


@pytest.mark.asyncio
async def test_list_leads_returns_all(db_session) -> None:
    from tests.factories.lead_factory import create_leads

    await create_leads(db_session, count=3)
    leads = await lead_service.list_leads(db_session)
    assert len(leads) == 3
