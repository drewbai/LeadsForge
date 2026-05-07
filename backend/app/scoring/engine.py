from app.scoring.rules import apply_rules


async def score_lead(lead: dict) -> dict:
    result = dict(lead)
    result["score"] = apply_rules(lead)
    return result
