"""Tests for app.services.events.activity.record_activity_event (Phase 79)."""

from __future__ import annotations

from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from app.services.events import activity as activity_module


@pytest.mark.asyncio
async def test_record_activity_event_schedules_dispatch(db_session, monkeypatch) -> None:
    spy = MagicMock()
    monkeypatch.setattr(activity_module.dispatcher, "fire_and_forget_dispatch", spy)

    lead_id = uuid4()
    out = await activity_module.record_activity_event(
        db_session,
        lead_id=lead_id,
        event_type="lead.created",
        payload={"email": "a@example.com", "source": "test"},
        performed_by="system",
    )

    assert out["event_type"] == "lead.created"
    assert out["lead_id"] == str(lead_id)
    assert "event_id" in out
    spy.assert_called_once()
    et, payload = spy.call_args[0]
    assert et == "lead.created"
    assert payload["lead_id"] == str(lead_id)
    assert payload["email"] == "a@example.com"
