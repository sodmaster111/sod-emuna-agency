from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel


class OperationContext(BaseModel):
    request_id: str
    metadata: dict[str, Any] | None = None


class BaseOperation(ABC):
    name: str

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    async def run(self, ctx: OperationContext, payload: dict) -> dict:
        ...


def get_operation(name: str) -> BaseOperation:
    if name == "marketing.campaign":
        from .marketing_ops import MarketingCampaignOperation

        return MarketingCampaignOperation("marketing.campaign")
    if name == "treasury.rebalance":
        from .treasury_ops import TreasuryRebalanceOperation

        return TreasuryRebalanceOperation("treasury.rebalance")
    if name == "content.broadcast":
        from .content_ops import ContentBroadcastOperation

        return ContentBroadcastOperation("content.broadcast")

    raise ValueError(f"Unknown operation: {name}")
