from uuid import UUID

from app.enrichment.providers.domain_provider import DomainEnrichmentProvider
from app.enrichment.providers.email_quality_provider import EmailQualityProvider
from app.services.tasks.dispatcher import enqueue_ranking_recompute


async def enrich_lead(lead: dict, *, lead_id: UUID | None = None) -> dict:
    providers = (
        DomainEnrichmentProvider(),
        EmailQualityProvider(),
    )
    current = dict(lead)
    for provider in providers:
        current = await provider.enrich(current)
    if lead_id is not None and current != lead:
        await enqueue_ranking_recompute(lead_id)
    return current
