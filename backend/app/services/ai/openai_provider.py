from __future__ import annotations

import json
import logging
from typing import Any

import httpx

from app.core.config import settings
from app.services.ai.base import AIProvider

logger = logging.getLogger(__name__)


OPENAI_API_BASE = "https://api.openai.com/v1"


VALID_INSIGHT_TYPES = {
    "next_best_action",
    "risk",
    "opportunity",
    "persona",
    "sentiment",
}


def _lead_to_text(lead_data: dict[str, Any]) -> str:
    parts: list[str] = []
    for key in (
        "full_name",
        "email",
        "phone",
        "source",
        "status",
        "notes",
    ):
        value = lead_data.get(key)
        if value:
            parts.append(f"{key}: {value}")
    if not parts:
        parts.append(json.dumps(lead_data, default=str))
    return "\n".join(parts)


class OpenAIProvider(AIProvider):
    def __init__(
        self,
        api_key: str | None = None,
        summary_model: str | None = None,
        insight_model: str | None = None,
        embedding_model: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self._api_key = api_key or settings.OPENAI_API_KEY
        self._summary_model = summary_model or settings.OPENAI_SUMMARY_MODEL
        self._insight_model = insight_model or settings.OPENAI_INSIGHT_MODEL
        self._embedding_model = embedding_model or settings.OPENAI_EMBEDDING_MODEL
        self._timeout = timeout

    @property
    def summary_model(self) -> str:
        return self._summary_model

    @property
    def insight_model(self) -> str:
        return self._insight_model

    @property
    def embedding_model(self) -> str:
        return self._embedding_model

    def _headers(self) -> dict[str, str]:
        if not self._api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is not configured; set it in environment or settings"
            )
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

    async def generate_summary(self, lead_data: dict[str, Any]) -> str:
        prompt = (
            "You are a sales assistant. Summarize the following lead in 2-4 "
            "concise sentences highlighting their context, status and any "
            "noteworthy signals.\n\n"
            f"{_lead_to_text(lead_data)}"
        )
        payload = {
            "model": self._summary_model,
            "messages": [
                {"role": "system", "content": "You write concise CRM lead summaries."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.3,
        }
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.post(
                f"{OPENAI_API_BASE}/chat/completions",
                headers=self._headers(),
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
        return data["choices"][0]["message"]["content"].strip()

    async def generate_insights(
        self, lead_data: dict[str, Any]
    ) -> list[dict[str, Any]]:
        prompt = (
            "You are a sales analyst. For the following lead, return a JSON "
            "array of insight objects. Each object must have:\n"
            "  - insight_type: one of "
            "'next_best_action', 'risk', 'opportunity', 'persona', 'sentiment'\n"
            "  - insight_text: a short, actionable description (max 280 chars)\n"
            "Return ONLY the JSON array, no commentary.\n\n"
            f"{_lead_to_text(lead_data)}"
        )
        payload = {
            "model": self._insight_model,
            "messages": [
                {
                    "role": "system",
                    "content": "You produce strict JSON insight arrays for CRM leads.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
        }
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.post(
                f"{OPENAI_API_BASE}/chat/completions",
                headers=self._headers(),
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
        raw = data["choices"][0]["message"]["content"]
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            logger.warning("Could not parse OpenAI insights JSON: %s", raw)
            return []

        items: list[dict[str, Any]]
        if isinstance(parsed, list):
            items = parsed
        elif isinstance(parsed, dict) and isinstance(parsed.get("insights"), list):
            items = parsed["insights"]
        else:
            return []

        cleaned: list[dict[str, Any]] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            insight_type = item.get("insight_type")
            insight_text = item.get("insight_text")
            if insight_type not in VALID_INSIGHT_TYPES:
                continue
            if not isinstance(insight_text, str) or not insight_text.strip():
                continue
            cleaned.append(
                {
                    "insight_type": insight_type,
                    "insight_text": insight_text.strip()[:280],
                }
            )
        return cleaned

    async def generate_embedding(self, text: str) -> list[float]:
        payload = {
            "model": self._embedding_model,
            "input": text,
        }
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.post(
                f"{OPENAI_API_BASE}/embeddings",
                headers=self._headers(),
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
        return list(data["data"][0]["embedding"])
