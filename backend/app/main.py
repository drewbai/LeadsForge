from fastapi import FastAPI

from app.routers.enrichment import router as enrichment_router
from app.routers.health import router as health_router
from app.routers.ingestion import router as ingestion_router
from app.routers.leads import router as leads_router
from app.routers.scoring import router as scoring_router

app = FastAPI()
app.include_router(health_router)
app.include_router(ingestion_router)
app.include_router(leads_router)
app.include_router(enrichment_router)
app.include_router(scoring_router)


@app.get("/")
async def root() -> dict[str, str]:
    return {"status": "ok"}
