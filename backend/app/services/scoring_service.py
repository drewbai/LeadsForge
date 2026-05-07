from app.scoring import engine


async def score_lead(lead: dict) -> dict:
    return await engine.score_lead(lead)
