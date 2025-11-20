"""Sefaria knowledge base wrapper."""
from __future__ import annotations

import asyncio
from typing import Any, Dict

import requests


class KnowledgeTool:
    """Lightweight client for the Sefaria API."""

    base_url = "https://www.sefaria.org/api/texts/"

    async def lookup(self, reference: str) -> Dict[str, Any]:
        """Fetch a text reference asynchronously using a thread pool."""

        return await asyncio.to_thread(self._fetch_reference, reference)

    def _fetch_reference(self, reference: str) -> Dict[str, Any]:
        response = requests.get(f"{self.base_url}{reference}", timeout=10)
        response.raise_for_status()
        return response.json()


__all__ = ["KnowledgeTool"]
