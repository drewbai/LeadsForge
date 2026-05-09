import logging

from fastapi import FastAPI

from app.api.v1.ranking_router import router as ranking_router
from app.routers.enrichment import router as enrichment_router
from app.routers.health import router as health_router
from app.routers.ingestion import router as ingestion_router
from app.routers.leads import router as leads_router
from app.routers.scoring import router as scoring_router
from app.services.ai import router as ai_router

logger = logging.getLogger(__name__)

app = FastAPI()
app.include_router(health_router)
app.include_router(ingestion_router)
app.include_router(leads_router)
app.include_router(enrichment_router)
app.include_router(scoring_router)
app.include_router(ai_router)
app.include_router(ranking_router)


@app.on_event("startup")
async def _startup_log_ai_pipelines() -> None:
    logger.info(
        "AI pipelines available: summary, insights, embeddings, "
        "semantic_search, hybrid_search, ranking"
    )


@app.get("/")
async def root() -> dict[str, str]:
    return {"status": "ok"}
