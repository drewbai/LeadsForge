from typing import Any
from uuid import UUID

from app.enrichment.providers.domain_provider import DomainEnrichmentProvider
from app.enrichment.providers.email_quality_provider import EmailQualityProvider
from app.models.metric import METRIC_LEAD_ENRICHED
from app.services.metrics.service import fire_and_forget_increment
from app.services.ranking.triggers import enqueue_ranking_recompute


async def enrich_lead(lead: dict[str, Any], *, lead_id: UUID | None = None) -> dict[str, Any]:
    providers = (
        DomainEnrichmentProvider(),
        EmailQualityProvider(),
    )
    current = dict(lead)
    for provider in providers:
        current = await provider.enrich(current)
    if current != lead:
        await fire_and_forget_increment(
            METRIC_LEAD_ENRICHED,
            {"lead_id": str(lead_id)} if lead_id is not None else None,
        )
    if lead_id is not None and current != lead:
        await enqueue_ranking_recompute(lead_id)
    return current
