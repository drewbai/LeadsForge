"""Regression: create_lead must invoke subscription dispatch via record_activity_event."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from app.schemas.lead import LeadCreate
from app.services import lead_service


@pytest.mark.asyncio
async def test_create_lead_fires_lead_created_dispatch(db_session, monkeypatch) -> None:
    dispatch_spy = MagicMock()
    monkeypatch.setattr(
        "app.services.events.activity.dispatcher.fire_and_forget_dispatch",
        dispatch_spy,
    )
    monkeypatch.setattr(lead_service, "enqueue_ranking_recompute", AsyncMock())
    monkeypatch.setattr(lead_service, "fire_and_forget_increment", AsyncMock())

    lead = await lead_service.create_lead(
        db_session,
        LeadCreate(email="dispatch-check@example.com", source="signup"),
    )

    dispatch_spy.assert_called_once()
    event_type, payload = dispatch_spy.call_args[0]
    assert event_type == "lead.created"
    assert payload["lead_id"] == str(lead.id)
    assert payload["email"] == "dispatch-check@example.com"
    assert payload["source"] == "signup"
