from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class EnrichmentProvider(ABC):
    @abstractmethod
    async def enrich(self, lead: dict[str, Any]) -> dict[str, Any]:
        """Return a new dict with enrichment fields; never mutate ``lead``."""
