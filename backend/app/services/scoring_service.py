from __future__ import annotations

from typing import Any

from app.scoring import engine


async def score_lead(lead: dict[str, Any]) -> dict[str, Any]:
    return await engine.score_lead(lead)
