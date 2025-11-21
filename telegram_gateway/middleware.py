from __future__ import annotations

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from typing import Any, Awaitable, Callable, Dict

from telegram_gateway.backend_client import BackendClient


class BackendClientMiddleware(BaseMiddleware):
    """Inject a shared BackendClient into handler data."""

    def __init__(self, client: BackendClient) -> None:
        super().__init__()
        self._client = client

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        data["backend_client"] = self._client
        return await handler(event, data)
