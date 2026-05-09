from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Response

from app.services.health.service import get_health, get_readiness

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["health"])


@router.get("/health")
async def health_endpoint(response: Response) -> dict[str, Any]:
    payload = await get_health()
    status = payload.get("status")
    if status == "error":
        response.status_code = 503
    elif status == "degraded":
        response.status_code = 200
    return payload


@router.get("/readiness")
async def readiness_endpoint(response: Response) -> dict[str, Any]:
    payload = await get_readiness()
    if not payload.get("ready"):
        response.status_code = 503
    return payload
