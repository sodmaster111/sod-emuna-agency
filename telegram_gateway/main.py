from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from telegram_gateway.backend_client import BackendClient
from telegram_gateway.config import settings
from telegram_gateway.handlers import router
from telegram_gateway.middleware import BackendClientMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def build_dispatcher(backend_client: BackendClient) -> Dispatcher:
    dp = Dispatcher()
    dp.message.middleware(BackendClientMiddleware(backend_client))
    dp.include_router(router)
    return dp


async def run_bot() -> None:
    bot = Bot(token=settings.telegram_bot_token, parse_mode=ParseMode.HTML)
    backend_client = BackendClient()
    dp = build_dispatcher(backend_client)

    try:
        await dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types(),
        )
    finally:
        logger.info("Shutting down Telegram gateway")
        await backend_client.aclose()


def main() -> None:
    asyncio.run(run_bot())


if __name__ == "__main__":
    main()
