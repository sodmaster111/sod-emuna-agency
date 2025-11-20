"""browser-use wrapper for simple URL visits."""
from __future__ import annotations

import asyncio
import importlib.util
from typing import Any, Dict

import requests

Agent = None
if importlib.util.find_spec("browser_use"):
    from browser_use.agent import Agent  # type: ignore[assignment]


class WebAgent:
    """Lightweight facade over browser-use with a requests fallback."""

    def __init__(self) -> None:
        self.agent = Agent() if Agent else None

    async def visit_url(self, url: str) -> Dict[str, Any]:
        """Visit a URL and return metadata."""

        if self.agent:
            return await self.agent.run(url)
        return await asyncio.to_thread(self._requests_fetch, url)

    def _requests_fetch(self, url: str) -> Dict[str, Any]:
        response = requests.get(url, timeout=10)
        return {"url": url, "status": response.status_code, "length": len(response.text)}


__all__ = ["WebAgent"]
