import asyncio

from app.enrichment.providers.domain_provider import DomainEnrichmentProvider
from app.enrichment.providers.email_quality_provider import EmailQualityProvider
from app.services import enrichment_service


def test_domain_provider_adds_email_domain() -> None:
    provider = DomainEnrichmentProvider()
    lead = {"email": "user@Example.COM"}
    out = asyncio.run(provider.enrich(lead))
    assert lead == {"email": "user@Example.COM"}
    assert out["email_domain"] == "example.com"


def test_email_quality_provider_adds_email_quality() -> None:
    provider = EmailQualityProvider()

    alias_lead = {"email": "u+tag@gmail.com"}
    alias_out = asyncio.run(provider.enrich(alias_lead))
    assert alias_lead == {"email": "u+tag@gmail.com"}
    assert alias_out["email_quality"] == "alias"

    free_lead = {"email": "person@yahoo.com"}
    free_out = asyncio.run(provider.enrich(free_lead))
    assert free_out["email_quality"] == "free_provider"

    unknown_lead = {"email": "x@acme.org"}
    unknown_out = asyncio.run(provider.enrich(unknown_lead))
    assert unknown_out["email_quality"] == "unknown"


def test_enrichment_service_enriches_correctly() -> None:
    lead = {"email": "someone+alias@outlook.com"}
    enriched = asyncio.run(enrichment_service.enrich_lead(lead))
    assert lead == {"email": "someone+alias@outlook.com"}
    assert enriched["email_domain"] == "outlook.com"
    assert enriched["email_quality"] == "alias"
