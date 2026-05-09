"""Tests for the enrichment pipeline."""
from __future__ import annotations

import pytest

from app.services import enrichment_service


@pytest.mark.asyncio
async def test_enrich_lead_adds_domain_and_quality() -> None:
    lead = {"email": "user@gmail.com"}
    out = await enrichment_service.enrich_lead(lead)
    assert out["email"] == "user@gmail.com"
    assert out["email_domain"] == "gmail.com"
    assert out["email_quality"] == "free_provider"


@pytest.mark.asyncio
async def test_enrich_lead_marks_alias_addresses() -> None:
    lead = {"email": "user+promo@gmail.com"}
    out = await enrichment_service.enrich_lead(lead)
    assert out["email_quality"] == "alias"


@pytest.mark.asyncio
async def test_enrich_lead_unknown_for_business_domain() -> None:
    lead = {"email": "ceo@acme.io"}
    out = await enrichment_service.enrich_lead(lead)
    assert out["email_domain"] == "acme.io"
    assert out["email_quality"] == "unknown"


@pytest.mark.asyncio
async def test_enrich_lead_handles_missing_email() -> None:
    out = await enrichment_service.enrich_lead({"source": "csv"})
    assert "email_domain" not in out
    assert "email_quality" not in out
    assert out["source"] == "csv"


@pytest.mark.asyncio
async def test_enrich_lead_does_not_mutate_input() -> None:
    lead = {"email": "person@yahoo.com"}
    out = await enrichment_service.enrich_lead(lead)
    assert lead == {"email": "person@yahoo.com"}
    assert out is not lead
