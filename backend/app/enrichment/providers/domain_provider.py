from __future__ import annotations

from typing import Any

from app.enrichment.base import EnrichmentProvider


class DomainEnrichmentProvider(EnrichmentProvider):
    async def enrich(self, lead: dict[str, Any]) -> dict[str, Any]:
        result = dict(lead)
        email = result.get("email")
        if not email or not isinstance(email, str):
            return result
        if "@" not in email:
            return result
        _, domain = email.split("@", 1)
        domain = domain.strip().lower()
        if not domain:
            return result
        result["email_domain"] = domain
        return result
