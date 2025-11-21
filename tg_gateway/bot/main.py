"""Telegram gateway service using aiogram with webhook delivery."""
from __future__ import annotations

import logging
import os
from typing import Any, Dict

import httpx
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("tg_gateway")
logging.basicConfig(level=logging.INFO)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8001")
PUBLIC_URL = os.getenv("PUBLIC_URL")
WEBHOOK_PATH = "/webhook"

if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN environment variable is required")
if not PUBLIC_URL:
    raise RuntimeError("PUBLIC_URL environment variable is required")


async def relay_to_backend(message: Message) -> None:
    """Forward incoming messages to the backend API for further processing."""

    payload: Dict[str, Any] = {
        "message_id": message.message_id,
        "chat_id": message.chat.id,
        "chat_type": message.chat.type,
        "from_user": {
            "id": message.from_user.id if message.from_user else None,
            "username": message.from_user.username if message.from_user else None,
            "first_name": message.from_user.first_name if message.from_user else None,
            "last_name": message.from_user.last_name if message.from_user else None,
        },
        "text": message.text,
        "date": message.date.isoformat() if message.date else None,
    }

    target = f"{BACKEND_URL.rstrip('/')}/api/telegram/events"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(target, json=payload)
            response.raise_for_status()
        logger.info("Relayed message %s to backend", message.message_id)
    except Exception as exc:  # noqa: BLE001 - log & continue for resiliency
        logger.warning("Backend relay failed: %s", exc)


def build_dispatcher() -> Dispatcher:
    dp = Dispatcher()

    @dp.message(CommandStart())
    async def handle_start(message: Message) -> None:
        await message.answer(
            "Welcome to the SOD Telegram gateway! Send a message and we'll forward it to the backend."
        )

    @dp.message(F.text)
    async def handle_text(message: Message) -> None:
        await relay_to_backend(message)
        await message.answer("Received! The team will review and respond.")

    return dp


def create_app(bot: Bot, dp: Dispatcher) -> web.Application:
    app = web.Application()

    async def status_handler(_: web.Request) -> web.Response:
        return web.json_response({"status": "ok", "service": "tg-gateway"})

    async def send_message_handler(request: web.Request) -> web.Response:
        data = await request.json()
        text = data.get("text")
        channel = data.get("chat_channel") or data.get("chat_id")
        if not text or not channel:
            return web.json_response(
                {"status": "error", "detail": "chat_channel/chat_id and text are required"},
                status=400,
            )

        try:
            await bot.send_message(chat_id=channel, text=text)
            return web.json_response({"status": "sent", "chat_id": channel})
        except Exception as exc:  # noqa: BLE001 - return structured error
            logger.exception("Failed to send outbound Telegram message")
            return web.json_response(
                {"status": "error", "detail": str(exc)},
                status=500,
            )

    handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    app.router.add_get("/api/status", status_handler)
    app.router.add_post("/api/send-message", send_message_handler)

    async def on_startup(app: web.Application) -> None:
        webhook_url = f"{PUBLIC_URL.rstrip('/')}{WEBHOOK_PATH}"
        await bot.set_webhook(webhook_url)
        logger.info("Webhook configured for %s", webhook_url)

    async def on_cleanup(app: web.Application) -> None:
        await bot.delete_webhook()
        await bot.session.close()
        logger.info("Webhook removed and bot session closed")

    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)

    return app


def main() -> None:
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    dp = build_dispatcher()
    app = create_app(bot, dp)
    web.run_app(app, host="0.0.0.0", port=7000)


if __name__ == "__main__":
    main()
