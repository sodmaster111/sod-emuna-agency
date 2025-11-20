"""Async client for retrieving Torah texts from the Sefaria public API."""
from __future__ import annotations

from typing import Any, Dict, Optional

import httpx

from app.core.config import config


class SefariaClient:
    """Lightweight wrapper around the Sefaria JSON API.

    This client exposes a single method, :meth:`fetch_text`, which returns the
    raw JSON document for a given reference. It can be used as an async context
    manager to reuse the same HTTP connection pool.
    """

    def __init__(
        self,
        base_url: str | None = None,
        *,
        timeout: float = 30.0,
    ) -> None:
        self.base_url = (base_url or config.sefaria_base_url).rstrip("/")
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> "SefariaClient":
        self._client = httpx.AsyncClient(timeout=self.timeout)
        return self

    async def __aexit__(self, *_exc_info: object) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def fetch_text(
        self,
        reference: str,
        *,
        language: str = "en",
        commentary: bool = False,
    ) -> Dict[str, Any]:
        """Retrieve a text payload for the given reference from Sefaria.

        Args:
            reference: Sefaria reference string (e.g., ``"Pirkei Avot"`` or
                ``"Shulchan Arukh, Orach Chayim 1"``).
            language: Language code to prioritize (``"en"``, ``"he"``, or
                ``"bi"``).
            commentary: Whether to include the associated commentary payload.

        Returns:
            Parsed JSON response from Sefaria as a dictionary.
        """

        if self._client is None:
            async with self:
                return await self.fetch_text(reference, language=language, commentary=commentary)

        url = f"{self.base_url}/texts/{reference}"
        params = {"lang": language, "commentary": int(bool(commentary)), "context": 0}
        response = await self._client.get(url, params=params)
        response.raise_for_status()
        return response.json()


__all__ = ["SefariaClient"]
