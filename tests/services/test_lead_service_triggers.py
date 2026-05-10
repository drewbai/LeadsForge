"""Verifies lead_service trigger wiring (ranking recompute on create/update).

Separate from ``tests/services/test_lead_service.py`` so ranking-trigger
expectations don't bleed into the basic CRUD tests.
"""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from app.schemas.lead import LeadCreate
from app.services import lead_service


@pytest.mark.asyncio
async def test_create_lead_enqueues_ranking_once(db_session, monkeypatch) -> None:
    spy = AsyncMock(return_value=None)
    monkeypatch.setattr(lead_service, "enqueue_ranking_recompute", spy)

    lead = await lead_service.create_lead(
        db_session,
        LeadCreate(email="trigger-create@example.com", source="signup"),
    )

    spy.assert_awaited_once_with(lead.id)


@pytest.mark.asyncio
async def test_update_lead_enqueues_ranking_once(
    db_session, seeded_lead, monkeypatch
) -> None:
    spy = AsyncMock(return_value=None)
    monkeypatch.setattr(lead_service, "enqueue_ranking_recompute", spy)

    updated = await lead_service.update_lead(
        db_session,
        seeded_lead.id,
        LeadCreate(email="trigger-update@example.com", source="manual"),
    )

    assert updated is not None
    assert updated.email == "trigger-update@example.com"
    spy.assert_awaited_once_with(seeded_lead.id)


@pytest.mark.asyncio
async def test_update_lead_missing_does_not_enqueue(db_session, monkeypatch) -> None:
    from uuid import uuid4

    spy = AsyncMock(return_value=None)
    monkeypatch.setattr(lead_service, "enqueue_ranking_recompute", spy)

    result = await lead_service.update_lead(
        db_session,
        uuid4(),
        LeadCreate(email="ghost@example.com", source="manual"),
    )

    assert result is None
    spy.assert_not_called()


@pytest.mark.asyncio
async def test_delete_lead_does_not_enqueue(
    db_session, seeded_lead, monkeypatch
) -> None:
    spy = AsyncMock(return_value=None)
    monkeypatch.setattr(lead_service, "enqueue_ranking_recompute", spy)

    ok = await lead_service.delete_lead(db_session, seeded_lead.id)

    assert ok is True
    spy.assert_not_called()
