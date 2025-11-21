"""HTTP endpoints exposing halachic time awareness."""
from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.core.halachic_time import HalachicTimeService, get_halachic_service

router = APIRouter(prefix="/halacha", tags=["halacha"])


def _build_service(lat: Optional[float], lon: Optional[float], tz: Optional[str]) -> HalachicTimeService:
    if lat is not None and lon is not None and tz:
        return HalachicTimeService(latitude=lat, longitude=lon, timezone=tz)
    return get_halachic_service()


@router.get("/now")
async def halacha_now(
    lat: Optional[float] = Query(None, description="Latitude override"),
    lon: Optional[float] = Query(None, description="Longitude override"),
    tz: Optional[str] = Query(None, description="Timezone override"),
) -> dict:
    service = _build_service(lat, lon, tz)
    now = datetime.now(service.timezone)
    return {
        "now": now.isoformat(),
        "is_shabbat": service.is_shabbat(now),
        "is_yom_tov": service.is_yom_tov(now),
        "is_shabbat_or_yom_tov": service.is_shabbat_or_yom_tov(now),
    }


@router.get("/zmanim")
async def halacha_zmanim(
    day: Optional[date] = Query(None, description="Date for zmanim (YYYY-MM-DD)"),
    lat: Optional[float] = Query(None, description="Latitude override"),
    lon: Optional[float] = Query(None, description="Longitude override"),
    tz: Optional[str] = Query(None, description="Timezone override"),
) -> dict:
    service = _build_service(lat, lon, tz)
    target_day = day or datetime.now(service.timezone).date()
    zmanim = service.get_zmanim(target_day)
    if not zmanim:
        raise HTTPException(status_code=501, detail="Zmanim lookup unavailable in this environment")

    return {"date": target_day.isoformat(), "timezone": str(service.timezone), "zmanim": {k: v.isoformat() for k, v in zmanim.items()}}
