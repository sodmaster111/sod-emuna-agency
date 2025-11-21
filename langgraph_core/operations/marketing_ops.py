from __future__ import annotations

from .base import BaseOperation, OperationContext


class MarketingCampaignOperation(BaseOperation):
    async def run(self, ctx: OperationContext, payload: dict) -> dict:
        return {
            "status": "ok",
            "action": "run_marketing_campaign",
            "details": "This is a stub marketing operation.",
        }
