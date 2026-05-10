import logging

from fastapi import FastAPI

from app.api.v1.health_router import router as v1_health_router
from app.api.v1.metrics_router import router as metrics_router
from app.api.v1.query_router import router as query_router
from app.api.v1.ranking_router import router as ranking_router
from app.api.v1.subscription_router import router as subscription_router
from app.api.v1.task_router import router as task_router
from app.routers.enrichment import router as enrichment_router
from app.routers.health import router as health_router
from app.routers.ingestion import router as ingestion_router
from app.routers.leads import router as leads_router
from app.routers.scoring import router as scoring_router
from app.services.ai import router as ai_router
from app.version import VERSION

logger = logging.getLogger(__name__)

app = FastAPI()
app.include_router(health_router)
app.include_router(ingestion_router)
app.include_router(leads_router)
app.include_router(enrichment_router)
app.include_router(scoring_router)
app.include_router(ai_router)
app.include_router(ranking_router)
app.include_router(query_router)
app.include_router(task_router)
app.include_router(subscription_router)
app.include_router(metrics_router)
app.include_router(v1_health_router)


@app.on_event("startup")
async def _startup_log_pipelines() -> None:
    logger.info(
        "LeadsForge backend %s — pipelines available: summary, insights, "
        "embeddings, semantic_search, hybrid_search, ranking, query, tasks, "
        "subscriptions, metrics, health",
        VERSION,
    )


@app.get("/")
async def root() -> dict[str, str]:
    return {"status": "ok", "version": VERSION}
