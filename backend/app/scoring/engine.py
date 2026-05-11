from __future__ import annotations

from typing import Any

from app.scoring.rules import apply_rules


async def score_lead(lead: dict[str, Any]) -> dict[str, Any]:
    result = dict(lead)
    result["score"] = apply_rules(lead)
    return result
