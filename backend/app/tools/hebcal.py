from datetime import datetime
from typing import Any, Dict, Optional

import httpx

from app.core.config import settings


def _format_params() -> Dict[str, Any]:
    return {
        "cfg": "json",
        "geonameid": 293397,  # Jerusalem by default
    }


async def fetch_zmanim(geonameid: int = 293397) -> Optional[dict]:
    params = _format_params()
    params["geonameid"] = geonameid
    async with httpx.AsyncClient() as client:
        response = await client.get(settings.HEBCAL_API_URL, params=params)
        if response.status_code == 200:
            return response.json()
    return None


async def is_shabbat_now(geonameid: int = 293397) -> bool:
    data = await fetch_zmanim(geonameid)
    if not data:
        return False

    for item in data.get("items", []):
        if item.get("category") in {"candles", "havdalah"}:
            return True
    return False
