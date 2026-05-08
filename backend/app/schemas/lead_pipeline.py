from typing import Any

from pydantic import BaseModel, RootModel


class SingleLeadRequest(BaseModel):
    lead: dict[str, Any]


class LeadRecord(RootModel[dict[str, Any]]):
    """Arbitrary lead JSON (input fields plus enrichment/scoring outputs)."""
