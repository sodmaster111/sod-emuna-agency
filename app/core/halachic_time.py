"""Central halachic time calculations for Shabbat/Yom Tov awareness.

Dependencies (add to requirements):
- pyluach
- zmanim

This service centralizes Shabbat and Yom Tov detection so multiple components
(missions engine, Telegram gateway, future TON) can consistently apply
restrictions. Default coordinates/timezone can be configured via environment
variables, e.g. for Jerusalem:
    HALACHA_LATITUDE=31.7857
    HALACHA_LONGITUDE=35.2007
    HALACHA_TIMEZONE=Asia/Jerusalem
"""
from __future__ import annotations

import os
from datetime import date, datetime, timedelta
from functools import lru_cache
from typing import Dict, Optional
from zoneinfo import ZoneInfo

try:  # pragma: no cover - import guarded for environments missing dependency
    from zmanim.util.geo_location import GeoLocation
    from zmanim.zmanim_calendar import ZmanimCalendar
except Exception:  # pragma: no cover - defensive fallback
    GeoLocation = None
    ZmanimCalendar = None


class HalachicTimeService:
    """Provide Shabbat/Yom Tov awareness for a specific location."""

    def __init__(self, latitude: float, longitude: float, timezone: str):
        self.latitude = latitude
        self.longitude = longitude
        self.timezone = ZoneInfo(timezone)
        self._location = (
            GeoLocation("HalachaLocation", latitude, longitude, self.timezone)
            if GeoLocation is not None
            else None
        )

    def _calendar_for(self, dt: datetime) -> tuple[datetime, Optional[ZmanimCalendar]]:
        base_dt = dt
        if base_dt.tzinfo is None:
            base_dt = base_dt.replace(tzinfo=ZoneInfo("UTC"))

        tz_dt = base_dt.astimezone(self.timezone)
        if ZmanimCalendar is None or self._location is None:
            return tz_dt, None

        cal = ZmanimCalendar(self._location)
        cal.set_date(tz_dt)
        return tz_dt, cal

    def is_shabbat(self, dt: datetime) -> bool:
        """Return True if the datetime falls within local Shabbat."""

        tz_dt, cal = self._calendar_for(dt)

        # Friday from sunset onward starts Shabbat; it ends Motzaei Shabbat at tzais.
        if cal:
            sunset = cal.sunset()
            if tz_dt.weekday() == 4:  # Friday
                return bool(sunset and tz_dt >= sunset)

            if tz_dt.weekday() == 5:  # Saturday
                tzais = cal.tzais()
                if tzais:
                    return tz_dt < tzais
                if sunset:
                    return tz_dt < sunset + timedelta(minutes=40)

            return False

        # Fallback approximation without zmanim dependency.
        if tz_dt.weekday() == 4 and tz_dt.hour >= 18:
            return True
        if tz_dt.weekday() == 5 and tz_dt.hour < 20:
            return True
        return False

    def is_yom_tov(self, dt: datetime) -> bool:
        """Return True if the datetime falls on Yom Tov.

        TODO: replace with real Yom Tov calculation using PyLuach or an external API.
        """

        return False

    def is_shabbat_or_yom_tov(self, dt: datetime) -> bool:
        """Convenience helper for composite guard."""

        return self.is_shabbat(dt) or self.is_yom_tov(dt)

    def get_zmanim(self, day: date) -> Dict[str, datetime]:
        """Return key zmanim for a given day (experimental)."""

        if ZmanimCalendar is None or self._location is None:
            return {}

        cal = ZmanimCalendar(self._location)
        cal.set_date(datetime.combine(day, datetime.min.time()).replace(tzinfo=self.timezone))
        zmanim: Dict[str, datetime] = {}
        for key in ("sunrise", "sunset", "tzais", "sof_zman_shema_gra", "sof_zman_tfilla_gra"):
            getter = getattr(cal, key, None)
            if callable(getter):
                value = getter()
                if value:
                    zmanim[key] = value
        return zmanim


@lru_cache(maxsize=1)
def get_halachic_service() -> HalachicTimeService:
    """Return a cached HalachicTimeService configured via environment variables."""

    latitude = float(os.getenv("HALACHA_LATITUDE", "31.7857"))
    longitude = float(os.getenv("HALACHA_LONGITUDE", "35.2007"))
    timezone = os.getenv("HALACHA_TIMEZONE", "Asia/Jerusalem")
    return HalachicTimeService(latitude=latitude, longitude=longitude, timezone=timezone)


__all__ = ["HalachicTimeService", "get_halachic_service"]
