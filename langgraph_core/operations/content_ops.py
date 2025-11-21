from __future__ import annotations

from .base import BaseOperation, OperationContext


class ContentBroadcastOperation(BaseOperation):
    async def run(self, ctx: OperationContext, payload: dict) -> dict:
        return {
            "status": "ok",
            "action": "broadcast_content",
            "details": "This is a stub content broadcast operation.",
        }
