import asyncio
import logging
import os
from typing import Any

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api.v1.about_router import router as about_router
from app.api.v1.health_router import router as v1_health_router
from app.api.v1.metrics_router import router as metrics_router
from app.api.v1.query_router import router as query_router
from app.api.v1.ranking_router import router as ranking_router
from app.api.v1.routing_router import router as routing_http_router
from app.api.v1.subscription_router import router as subscription_router
from app.api.v1.task_router import router as task_router
from app.routers.enrichment import router as enrichment_router
from app.routers.health import router as health_router
from app.routers.ingestion import router as ingestion_router
from app.routers.leads import router as leads_router
from app.routers.scoring import router as scoring_router
from app.services.ai import router as ai_router
from app.services.tasks.worker import run_worker_loop
from app.version import VERSION

logger = logging.getLogger(__name__)

_cors_origins_raw = os.environ.get(
    "LEADSFORGE_CORS_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173",
)
_cors_origins = [origin.strip() for origin in _cors_origins_raw.split(",") if origin.strip()]

app = FastAPI()
if _cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
app.include_router(health_router)
app.include_router(ingestion_router)
app.include_router(leads_router)
app.include_router(enrichment_router)
app.include_router(scoring_router)
app.include_router(ai_router)
app.include_router(ranking_router)
app.include_router(routing_http_router)
app.include_router(about_router)
app.include_router(query_router)
app.include_router(task_router)
app.include_router(subscription_router)
app.include_router(metrics_router)
app.include_router(v1_health_router)


TASK_WORKER_DISABLE_ENV = "LEADSFORGE_DISABLE_TASK_WORKER"
TASK_WORKER_POLL_INTERVAL_SECONDS = 2.0
TASK_WORKER_BATCH_SIZE = 10
TASK_WORKER_SHUTDOWN_TIMEOUT_SECONDS = 5.0


def _task_worker_disabled() -> bool:
    raw = os.environ.get(TASK_WORKER_DISABLE_ENV, "")
    return raw.strip().lower() in {"1", "true", "yes", "on"}


@app.on_event("startup")
async def _startup_log_pipelines() -> None:
    logger.info(
        "LeadsForge backend %s — pipelines available: summary, insights, "
        "embeddings, semantic_search, hybrid_search, ranking, routing, query, tasks, "
        "subscriptions, metrics, health",
        VERSION,
    )


@app.on_event("startup")
async def _startup_task_worker() -> None:
    """Launch the background task worker loop as an asyncio task on app startup.

    The worker polls every ``TASK_WORKER_POLL_INTERVAL_SECONDS`` for pending
    tasks and dispatches them through the worker module's DISPATCH_TABLE.
    Without this hook, every ``rank_lead`` / ``route_lead`` task we enqueue
    would sit in ``pending`` forever.

    Disabled when ``LEADSFORGE_DISABLE_TASK_WORKER`` is truthy. The test suite
    sets this in conftest so the worker doesn't race fixtures or consume the
    test session pool.
    """
    if _task_worker_disabled():
        logger.info("Task worker disabled via %s; skipping startup", TASK_WORKER_DISABLE_ENV)
        return

    stop_event = asyncio.Event()
    worker_task = asyncio.create_task(
        run_worker_loop(
            poll_interval_seconds=TASK_WORKER_POLL_INTERVAL_SECONDS,
            batch_size=TASK_WORKER_BATCH_SIZE,
            stop_event=stop_event,
        ),
        name="leadsforge-task-worker",
    )
    app.state.task_worker_stop_event = stop_event
    app.state.task_worker_task = worker_task
    logger.info(
        "Task worker started (poll_interval=%.1fs, batch_size=%d)",
        TASK_WORKER_POLL_INTERVAL_SECONDS,
        TASK_WORKER_BATCH_SIZE,
    )


@app.on_event("shutdown")
async def _shutdown_task_worker() -> None:
    """Signal the worker to stop and await its completion with a timeout fallback."""
    stop_event: asyncio.Event | None = getattr(app.state, "task_worker_stop_event", None)
    worker_task: asyncio.Task[Any] | None = getattr(app.state, "task_worker_task", None)

    if stop_event is None or worker_task is None:
        return

    stop_event.set()
    try:
        await asyncio.wait_for(worker_task, timeout=TASK_WORKER_SHUTDOWN_TIMEOUT_SECONDS)
        logger.info("Task worker stopped cleanly")
    except asyncio.TimeoutError:
        logger.warning(
            "Task worker did not stop within %.1fs; cancelling",
            TASK_WORKER_SHUTDOWN_TIMEOUT_SECONDS,
        )
        worker_task.cancel()
        try:
            await worker_task
        except (asyncio.CancelledError, Exception):
            logger.exception("Task worker raised during forced shutdown")
    finally:
        app.state.task_worker_stop_event = None
        app.state.task_worker_task = None


@app.get("/")
async def root() -> dict[str, str]:
    return {"status": "ok", "version": VERSION}
