from __future__ import annotations

import importlib.util
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from typing import Optional
from zoneinfo import ZoneInfo

from backend.app.schemas.jewish_calendar import JewishDayInfo, Zmanim

# Default coordinates/timezone should ideally be provided via environment variables:
# HALACHA_LATITUDE, HALACHA_LONGITUDE, HALACHA_TIMEZONE


@dataclass
class _HebrewCalendarArtifacts:
    jewish_date_str: str
    parsha: Optional[str]
    holidays: list[str]
    omer_day: Optional[int]


class JewishCalendarService:
    def __init__(self, latitude: float, longitude: float, timezone: str):
        self.latitude = latitude
        self.longitude = longitude
        self.timezone = timezone

    def get_jewish_day_info(self, target_date: date | None = None) -> JewishDayInfo:
        tz = ZoneInfo(self.timezone)
        resolved_date = target_date or datetime.now(tz).date()

        hebrew_data = self._compute_hebrew_calendar_details(resolved_date)
        zmanim = self._compute_basic_zmanim(resolved_date, tz)

        day_type = self._determine_day_type(resolved_date, hebrew_data.holidays)

        return JewishDayInfo(
            gregorian_date=resolved_date,
            jewish_date_str=hebrew_data.jewish_date_str,
            parsha=hebrew_data.parsha,
            holidays=hebrew_data.holidays,
            omer_day=hebrew_data.omer_day,
            day_type=day_type,
            zmanim=zmanim,
        )

    def is_shabbat_or_yom_tov(self, target_datetime: datetime) -> bool:
        tz = ZoneInfo(self.timezone)
        localized_dt = target_datetime if target_datetime.tzinfo else target_datetime.replace(tzinfo=tz)
        current_day_info = self.get_jewish_day_info(localized_dt.date())

        if current_day_info.day_type in {"shabbat", "yom_tov"}:
            return True

        # Check transition from previous day if after sunset but before havdalah.
        previous_day_info = self.get_jewish_day_info(localized_dt.date() - timedelta(days=1))
        if previous_day_info.day_type in {"shabbat", "yom_tov"} and previous_day_info.zmanim.havdalah:
            if localized_dt < previous_day_info.zmanim.havdalah:
                return True

        return False

    def _compute_hebrew_calendar_details(self, resolved_date: date) -> _HebrewCalendarArtifacts:
        jewish_date_str = resolved_date.isoformat()
        parsha: Optional[str] = None
        holidays: list[str] = []
        omer_day: Optional[int] = None

        if importlib.util.find_spec("pyluach"):
            from pyluach import dates, parshios  # type: ignore

            try:
                gdate = dates.GregorianDate(resolved_date.year, resolved_date.month, resolved_date.day)
                hdate = gdate.to_heb()
                jewish_date_str = str(hdate)

                # Parsha calculation.
                try:
                    if hasattr(parshios, "getparsha_string"):
                        # Returns list of parsha names (handles double parshiot)
                        parsha_list = parshios.getparsha_string(hdate)
                        if parsha_list:
                            parsha = "/".join(parsha_list)
                    elif hasattr(parshios, "getparsha"):
                        parsha_data = parshios.getparsha(hdate)
                        if parsha_data:
                            parsha = "/".join(parsha_data) if isinstance(parsha_data, (list, tuple)) else str(parsha_data)
                except Exception:
                    parsha = None

                # Holidays
                try:
                    holiday_value = hdate.holiday(hebrew=False)
                    if holiday_value:
                        if isinstance(holiday_value, (list, tuple)):
                            holidays.extend([str(item) for item in holiday_value])
                        else:
                            holidays.append(str(holiday_value))
                except Exception:
                    # TODO: refine holiday detection when richer calendar data is available.
                    holidays = holidays

                # Omer day
                for attr in ("omer_day", "omer", "get_omer"):
                    candidate = getattr(hdate, attr, None)
                    if callable(candidate):
                        try:
                            omer_day = candidate()
                            break
                        except Exception:
                            continue
            except Exception:
                # TODO: Consider installing pyluach for accurate Hebrew date and parsha calculations.
                pass

        return _HebrewCalendarArtifacts(
            jewish_date_str=jewish_date_str,
            parsha=parsha,
            holidays=holidays,
            omer_day=omer_day,
        )

    def _compute_basic_zmanim(self, resolved_date: date, tz: ZoneInfo) -> Zmanim:
        sunrise: Optional[datetime] = None
        sunset: Optional[datetime] = None

        if importlib.util.find_spec("zmanim"):
            from zmanim.zmanim_calendar import ZmanimCalendar  # type: ignore

            try:
                calendar = ZmanimCalendar(location=(self.latitude, self.longitude), timezone=tz)
                calendar.set_date(resolved_date)
                sunrise = calendar.sunrise
                sunset = calendar.sunset
            except Exception:
                sunrise = None
                sunset = None

        if sunrise is None:
            # Fallback placeholder: 6 AM sunrise and 6 PM sunset local time.
            sunrise = datetime.combine(resolved_date, time(6, 0), tzinfo=tz)
        if sunset is None:
            sunset = datetime.combine(resolved_date, time(18, 0), tzinfo=tz)

        candle_lighting = sunset - timedelta(minutes=18) if sunset else None
        havdalah = sunset + timedelta(minutes=42) if sunset else None

        return Zmanim(
            sunrise=sunrise,
            sunset=sunset,
            candle_lighting=candle_lighting,
            havdalah=havdalah,
        )

    def _determine_day_type(self, resolved_date: date, holidays: list[str]) -> str:
        weekday = resolved_date.weekday()
        # Friday is 4, Saturday is 5.
        is_shabbat = weekday == 5
        is_erev_shabbat = weekday == 4

        is_chol_hamoed = any("Chol Hamoed" in name for name in holidays)
        is_fast_day = any("Fast" in name for name in holidays)
        is_yom_tov = bool(holidays) and not (is_chol_hamoed or is_fast_day)

        if is_shabbat:
            return "shabbat"
        if is_erev_shabbat:
            return "erev_shabbat"
        if is_yom_tov:
            return "yom_tov"
        if is_chol_hamoed:
            return "chol_hamoed"
        if is_fast_day:
            return "fast"
        return "weekday"


if __name__ == "__main__":
    svc = JewishCalendarService(latitude=31.7857, longitude=35.2007, timezone="Asia/Jerusalem")
    info = svc.get_jewish_day_info()
    print(info.model_dump())
