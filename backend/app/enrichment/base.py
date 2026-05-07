from abc import ABC, abstractmethod


class EnrichmentProvider(ABC):
    @abstractmethod
    async def enrich(self, lead: dict) -> dict:
        """Return a new dict with enrichment fields; never mutate ``lead``."""
