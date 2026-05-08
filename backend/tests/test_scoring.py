import asyncio

from app.scoring import rules
from app.services import scoring_service


def test_scoring_rules_produce_correct_score() -> None:
    assert rules.apply_rules({}) == 0

    assert rules.apply_rules({"email_domain": "acme.com"}) == 10

    lead_alias = {"email_domain": "x.com", "email_quality": "alias"}
    assert rules.apply_rules(lead_alias) == 15

    lead_free = {"email_domain": "gmail.com", "email_quality": "free_provider"}
    assert rules.apply_rules(lead_free) == 13

    lead_unknown = {"email_domain": "co.io", "email_quality": "unknown"}
    assert rules.apply_rules(lead_unknown) == 10


def test_scoring_service_returns_lead_with_score() -> None:
    lead = {"email": "a@b.co", "email_domain": "b.co", "email_quality": "unknown"}
    scored = asyncio.run(scoring_service.score_lead(lead))
    assert "score" not in lead
    assert scored["score"] == 10
