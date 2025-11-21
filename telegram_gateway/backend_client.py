from __future__ import annotations

from typing import Any, Dict, List, Optional

import httpx

from telegram_gateway.config import settings


class BackendClient:
    """HTTP client for delegating work to the core backend."""

    def __init__(self) -> None:
        self._client = httpx.AsyncClient(
            base_url=settings.backend_base_url,
            timeout=settings.request_timeout_seconds,
        )

    async def aclose(self) -> None:
        await self._client.aclose()

    async def schedule_task(self, task: str, user_id: int, username: Optional[str]) -> Dict[str, Any]:
        payload = {
            "task": task,
            "source": "telegram",
            "metadata": {
                "telegram_user_id": user_id,
                "telegram_username": username,
            },
        }
        response = await self._client.post("/commands/schedule", json=payload)
        response.raise_for_status()
        return response.json()

    async def get_status(self, task_id: str) -> Dict[str, Any]:
        response = await self._client.get(f"/commands/status/{task_id}")
        response.raise_for_status()
        return response.json()

    async def fetch_logs(self, limit: int = 5) -> List[Dict[str, Any]]:
        params = {"limit": limit}
        response = await self._client.get("/pinkas", params=params)
        response.raise_for_status()
        payload = response.json()
        if isinstance(payload, dict) and "logs" in payload:
            return payload["logs"]
        if isinstance(payload, list):
            return payload
        return []
