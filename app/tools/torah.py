"""Knowledge tools for Torah consultation and Halachic validation."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

import requests

SEFARIA_API_BASE = "https://www.sefaria.org/api"
HEBCAL_API_BASE = "https://www.hebcal.com/shabbat"


def consult_sefaria(query: str) -> Dict[str, Any]:
    """Fetch relevant texts from the Sefaria API for the given query.

    The function performs a lightweight lookup against Sefaria's JSON API and
    returns a normalized mapping that preserves the title, Hebrew text, and any
    cited sources. A short timeout is enforced to avoid hanging requests.
    """

    response = requests.get(
        f"{SEFARIA_API_BASE}/texts/{query}",
        timeout=10,
    )
    response.raise_for_status()
    data = response.json()
    return {
        "title": data.get("ref", query),
        "text": data.get("he") or data.get("text", []),
        "sources": data.get("sources", []),
    }


def is_shabbat_now(city: str = "Jerusalem") -> bool:
    """Determine if the current UTC time falls within Shabbat for a city.

    Hebcal provides candle-lighting and havdalah timestamps; if the present time
    is between those bounds, Shabbat is considered in effect. The function
    defaults to Jerusalem but accepts any Hebcal-supported city name.
    """

    response = requests.get(
        HEBCAL_API_BASE,
        params={"cfg": "json", "city": city, "M": "on"},
        timeout=10,
    )
    response.raise_for_status()
    data = response.json()
    items = data.get("items", [])

    candle_lighting: datetime | None = None
    havdalah: datetime | None = None

    for item in items:
        category = item.get("category")
        date_str = item.get("date")
        if not date_str:
            continue
        try:
            timestamp = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except ValueError:
            continue
        if category == "candles":
            candle_lighting = timestamp
        elif category == "havdalah":
            havdalah = timestamp

    if not candle_lighting or not havdalah:
        return False

    now_utc = datetime.now(timezone.utc)
    return candle_lighting <= now_utc <= havdalah


def validate_kosher(text: str) -> Dict[str, Any]:
    """Validate the provided text against Halachic standards via the CKO agent.

    This is a lightweight placeholder to be replaced with the actual
    conversation flow once the CKO agent endpoint is available.
    """

    return {
        "input": text,
        "halachic_alignment": "pending-review",
        "notes": [
            "Submit this text to the CKO agent for authoritative Halachic review.",
            "Until the agent endpoint is connected, this is a structural placeholder.",
        ],
    }
