from __future__ import annotations

import logging
import uuid
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Body, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.engine import get_session
from app.services.ai.base import AIProvider
from app.services.ai.embedding_pipeline import (
    generate_embedding_for_lead,
    refresh_embeddings_for_all_leads,
)
from app.services.ai.hybrid_search import hybrid_search
from app.services.ai.insight_pipeline import (
    generate_insights_for_lead,
    refresh_insights_for_all_leads,
)
from app.services.ai.openai_provider import OpenAIProvider
from app.services.ai.semantic_search import semantic_search
from app.services.ai.summary_pipeline import (
    generate_summary_for_lead,
    refresh_summaries_for_all_leads,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["ai"])


def get_ai_provider() -> AIProvider:
    provider_name = (settings.AI_PROVIDER or "openai").lower()
    if provider_name == "openai":
        return OpenAIProvider()
    raise HTTPException(
        status_code=500,
        detail=f"Unsupported AI provider configured: {provider_name}",
    )


@router.post("/summary/{lead_id}")
async def create_summary(
    lead_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    provider: AIProvider = Depends(get_ai_provider),
) -> dict[str, Any]:
    result = await generate_summary_for_lead(session, provider, lead_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    return result


@router.post("/insights/{lead_id}")
async def create_insights(
    lead_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    provider: AIProvider = Depends(get_ai_provider),
) -> dict[str, Any]:
    result = await generate_insights_for_lead(session, provider, lead_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    return {"lead_id": str(lead_id), "insights": result}


@router.post("/embedding/{lead_id}")
async def create_embedding(
    lead_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    provider: AIProvider = Depends(get_ai_provider),
) -> dict[str, Any]:
    result = await generate_embedding_for_lead(session, provider, lead_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    return result


async def _refresh_summaries_task() -> None:
    provider = get_ai_provider()
    async for session in get_session():
        try:
            await refresh_summaries_for_all_leads(session, provider)
        except Exception:
            logger.exception("Background summary refresh failed")
        finally:
            await session.close()
        break


async def _refresh_insights_task() -> None:
    provider = get_ai_provider()
    async for session in get_session():
        try:
            await refresh_insights_for_all_leads(session, provider)
        except Exception:
            logger.exception("Background insight refresh failed")
        finally:
            await session.close()
        break


async def _refresh_embeddings_task() -> None:
    provider = get_ai_provider()
    async for session in get_session():
        try:
            await refresh_embeddings_for_all_leads(session, provider)
        except Exception:
            logger.exception("Background embedding refresh failed")
        finally:
            await session.close()
        break


@router.post("/summary/refresh-all")
async def refresh_all_summaries(
    background_tasks: BackgroundTasks,
) -> dict[str, str]:
    background_tasks.add_task(_refresh_summaries_task)
    return {"status": "scheduled", "job": "refresh_summaries"}


@router.post("/insights/refresh-all")
async def refresh_all_insights(
    background_tasks: BackgroundTasks,
) -> dict[str, str]:
    background_tasks.add_task(_refresh_insights_task)
    return {"status": "scheduled", "job": "refresh_insights"}


@router.post("/embeddings/refresh-all")
async def refresh_all_embeddings(
    background_tasks: BackgroundTasks,
) -> dict[str, str]:
    background_tasks.add_task(_refresh_embeddings_task)
    return {"status": "scheduled", "job": "refresh_embeddings"}


@router.post("/search")
async def ai_semantic_search(
    payload: dict[str, Any] = Body(...),
    session: AsyncSession = Depends(get_session),
    provider: AIProvider = Depends(get_ai_provider),
) -> dict[str, Any]:
    query = str(payload.get("query") or "").strip()
    limit = int(payload.get("limit") or 10)
    if not query:
        raise HTTPException(status_code=400, detail="query is required")
    results = await semantic_search(session, provider, query, limit=limit)
    return {"query": query, "results": results}


@router.post("/search/hybrid")
async def ai_hybrid_search(
    payload: dict[str, Any] = Body(...),
    session: AsyncSession = Depends(get_session),
    provider: AIProvider = Depends(get_ai_provider),
) -> dict[str, Any]:
    query = str(payload.get("query") or "").strip()
    limit = int(payload.get("limit") or 10)
    semantic_weight = float(payload.get("semantic_weight") or 0.7)
    keyword_weight = float(payload.get("keyword_weight") or 0.3)
    if not query:
        raise HTTPException(status_code=400, detail="query is required")
    results = await hybrid_search(
        session,
        provider,
        query,
        limit=limit,
        semantic_weight=semantic_weight,
        keyword_weight=keyword_weight,
    )
    return {
        "query": query,
        "semantic_weight": semantic_weight,
        "keyword_weight": keyword_weight,
        "results": results,
    }
