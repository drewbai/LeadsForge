from __future__ import annotations

from typing import Any


def apply_rules(lead: dict[str, Any]) -> int:
    score = 0
    email_domain = lead.get("email_domain")
    if email_domain:
        score += 10

    quality = lead.get("email_quality")
    if quality == "alias":
        score += 5
    elif quality == "free_provider":
        score += 3

    return score
