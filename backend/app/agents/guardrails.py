from functools import wraps
from typing import Any

import httpx
from fastapi import HTTPException

from app.core.config import settings


class HalachicViolationError(Exception):
    pass


async def check_shabbat_status() -> bool:
    """Query Hebcal API to check if current time is Shabbat/Yom Tov."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.HEBCAL_API_URL}?cfg=json&geonameid=293397"  # Jerusalem
        )
        data = response.json()
        for item in data.get("items", []):
            if item.get("category") in {"candles", "havdalah"}:
                return True
    return False


def _extract_content(args: tuple[Any, ...], kwargs: dict[str, Any]) -> str:
    # Look for explicit kwargs
    for key in ("content", "task", "description"):
        if key in kwargs and isinstance(kwargs[key], str):
            return kwargs[key]

    # Inspect Pydantic/BaseModel style args
    for arg in args:
        candidate = getattr(arg, "task", None) or getattr(arg, "content", None)
        if isinstance(candidate, str):
            return candidate
    return ""


def require_cro_validation(func):
    """Decorator to block religious content without CRO approval."""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        content = _extract_content(args, kwargs)
        religious_keywords = ["psak", "halacha", "kosher", "treif", "mitzvah", "issur"]

        if any(keyword in content.lower() for keyword in religious_keywords):
            raise HTTPException(
                status_code=403,
                detail="Religious content requires CRO validation. Sent to Posek Council queue.",
            )

        return await func(*args, **kwargs)

    return wrapper


def block_shabbat_trading(func):
    """Decorator to prevent CFO financial operations during Shabbat."""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        is_shabbat = await check_shabbat_status()
        if is_shabbat:
            raise HTTPException(
                status_code=403,
                detail="Trading blocked: Current time is Shabbat/Yom Tov (Zmanim violation)",
            )
        return await func(*args, **kwargs)

    return wrapper
