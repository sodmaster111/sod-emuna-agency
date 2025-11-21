from __future__ import annotations

import logging
import os
from datetime import datetime
from typing import Optional

import httpx

from telegram_gateway.config import settings

logger = logging.getLogger(__name__)

USE_BACKEND_HALACHA = os.getenv("TG_USE_BACKEND_HALACHA", "").lower() == "true"


class ShabbatGuardError(RuntimeError):
    """Raised when an action is blocked due to Shabbat or Yom Tov."""


def _fetch_backend_status() -> Optional[bool]:
    """Query backend halachic endpoint if enabled."""

    if not USE_BACKEND_HALACHA:
        return None

    url = f"{settings.backend_base_url.rstrip('/')}/halacha/now"
    try:
        response = httpx.get(url, timeout=settings.request_timeout_seconds)
        response.raise_for_status()
        payload = response.json()
        return bool(payload.get("is_shabbat_or_yom_tov"))
    except Exception as exc:  # pragma: no cover - defensive around network calls
        logger.warning("Failed to query backend halacha service: %s", exc)
        return None


def is_shabbat_or_yom_tov(now: datetime) -> bool:
    """Return True if the provided datetime falls on Shabbat or Yom Tov."""

    backend_result = _fetch_backend_status()
    if backend_result is not None:
        return backend_result

    return False


def ensure_not_shabbat(now: datetime) -> None:
    """Ensure operations are not executed during Shabbat or Yom Tov."""

    if is_shabbat_or_yom_tov(now):
        raise ShabbatGuardError("Broadcast blocked due to Shabbat/Yom Tov")
