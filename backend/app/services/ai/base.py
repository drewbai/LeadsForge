from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class AIProvider(ABC):
    @abstractmethod
    async def generate_summary(self, lead_data: dict[str, Any]) -> str: ...

    @abstractmethod
    async def generate_insights(self, lead_data: dict[str, Any]) -> list[dict[str, Any]]: ...

    @abstractmethod
    async def generate_embedding(self, text: str) -> list[float]: ...
