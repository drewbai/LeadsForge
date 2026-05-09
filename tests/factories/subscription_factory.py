"""Factory helpers for Subscription model. Skips when subscription model not present."""
from __future__ import annotations

from typing import Any
from uuid import UUID, uuid4

import pytest


def _import_subscription_model():
    return pytest.importorskip("app.models.subscription")


def build_subscription(
    event_type: str = "lead.created",
    target_type: str = "webhook",
    target: str = "https://example.com/hook",
    is_active: bool = True,
    subscription_id: UUID | None = None,
) -> Any:
    module = _import_subscription_model()
    Subscription = getattr(module, "Subscription")
    return Subscription(
        id=subscription_id or uuid4(),
        event_type=event_type,
        target_type=target_type,
        target=target,
        is_active=is_active,
    )


async def create_subscription(session, **overrides: Any) -> Any:
    sub = build_subscription(**overrides)
    session.add(sub)
    await session.commit()
    await session.refresh(sub)
    return sub
