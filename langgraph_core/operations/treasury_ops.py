from __future__ import annotations

from .base import BaseOperation, OperationContext


class TreasuryRebalanceOperation(BaseOperation):
    async def run(self, ctx: OperationContext, payload: dict) -> dict:
        return {
            "status": "ok",
            "action": "rebalance_treasury",
            "details": "This is a stub treasury operation, integrate TON later.",
        }
