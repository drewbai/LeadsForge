from app.enrichment.providers.domain_provider import DomainEnrichmentProvider
from app.enrichment.providers.email_quality_provider import EmailQualityProvider


async def enrich_lead(lead: dict) -> dict:
    providers = (
        DomainEnrichmentProvider(),
        EmailQualityProvider(),
    )
    current = dict(lead)
    for provider in providers:
        current = await provider.enrich(current)
    return current
