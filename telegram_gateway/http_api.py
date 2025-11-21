from __future__ import annotations

"""FastAPI application for Telegram broadcast handling.

This module can be served as a lightweight HTTP layer alongside the Telegram
bot. In docker-compose, run it with something like:
    # service: tg_http
    #   command: uvicorn telegram_gateway.http_api:app --host 0.0.0.0 --port 8080

The missions engine will POST to `/api/send-message` with payload:
    {"channel": MissionTemplate.target_channel, "text": rendered_message,
     "respect_shabbat": true}
The gateway enforces the Shabbat/Yom Tov guard even if upstream skips it.
"""

import logging
from datetime import datetime
from typing import Any, Dict

from aiogram import Bot
from fastapi import APIRouter, FastAPI, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from telegram_gateway.config import settings
from telegram_gateway.services.channels import ChannelResolutionError, resolve_chat_id
from telegram_gateway.services.shabbat_guard import ShabbatGuardError, ensure_not_shabbat

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SendMessageRequest(BaseModel):
    channel: str = Field(..., description="Logical channel key")
    text: str = Field(..., description="Message text to broadcast")
    respect_shabbat: bool = Field(True, description="Block during Shabbat/Yom Tov")


router = APIRouter(prefix="/api")


@router.post("/send-message")
async def send_message(request: SendMessageRequest) -> Dict[str, Any]:
    now = datetime.utcnow()
    if request.respect_shabbat:
        try:
            ensure_not_shabbat(now)
        except ShabbatGuardError:
            logger.warning(
                "Broadcast blocked due to Shabbat/Yom Tov: channel=%s", request.channel
            )
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "status": "blocked",
                    "detail": "Broadcast blocked due to Shabbat/Yom Tov",
                },
            )

    try:
        chat_id = resolve_chat_id(request.channel)
    except ChannelResolutionError as exc:
        logger.error("Unknown channel requested: %s", request.channel)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"status": "error", "detail": str(exc)},
        )

    bot = Bot(token=settings.telegram_bot_token)
    try:
        await bot.send_message(chat_id=chat_id, text=request.text)
    except Exception as exc:  # noqa: BLE001 - return clean error payload
        logger.exception(
            "Failed to send broadcast channel=%s chat_id=%s", request.channel, chat_id
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "error", "detail": str(exc)},
        )
    finally:
        await bot.session.close()

    logger.info(
        "Sent broadcast channel=%s chat_id=%s length=%s",
        request.channel,
        chat_id,
        len(request.text),
    )
    return {"status": "sent", "channel": request.channel, "chat_id": chat_id}


app = FastAPI(title="Telegram Gateway API")
app.include_router(router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("telegram_gateway.http_api:app", host="0.0.0.0", port=8080)
