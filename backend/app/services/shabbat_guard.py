"""Shabbat and Yom Tov guard utilities.

This module provides helper classes and functions to prevent sending messages or
starting campaigns during Shabbat or Yom Tov. It relies on the
``JewishCalendarService`` (SOD-RITUAL-001) to determine restricted times.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any
from zoneinfo import ZoneInfo

if TYPE_CHECKING:  # pragma: no cover - imported for type checking only
    from app.services.jewish_calendar import JewishCalendarService
else:  # pragma: no cover - fallback when the concrete service is not available
    JewishCalendarService = Any


class ShabbatRestrictedError(Exception):
    """Raised when an operation is attempted during Shabbat or Yom Tov."""


class ShabbatGuard:
    """Guard that checks whether actions are permitted based on the calendar."""

    def __init__(self, calendar_service: JewishCalendarService):
        self.calendar = calendar_service

    def _now(self) -> datetime:
        """Return the current time in the calendar service timezone if provided."""

        timezone = getattr(self.calendar, "timezone", None)

        if isinstance(timezone, str):
            try:
                timezone = ZoneInfo(timezone)
            except Exception:
                timezone = None

        if timezone:
            return datetime.now(timezone)

        return datetime.now()

    def is_restricted(self, dt: datetime | None = None) -> bool:
        """Return ``True`` if the given time is during Shabbat or Yom Tov."""

        dt = dt or self._now()
        return self.calendar.is_shabbat_or_yom_tov(dt)

    def ensure_allowed(self, dt: datetime | None = None) -> None:
        """Raise ``ShabbatRestrictedError`` if the time is restricted."""

        if self.is_restricted(dt):
            raise ShabbatRestrictedError(
                "Operation not allowed during Shabbat/Yom Tov"
            )


def can_send_message_now(calendar_service: JewishCalendarService) -> bool:
    """Check if messages can be sent right now.

    Example before sending Telegram broadcast::

        if not can_send_message_now(calendar):
            # skip or reschedule
    """

    return not ShabbatGuard(calendar_service).is_restricted()


def can_start_campaign_at(calendar_service: JewishCalendarService, dt: datetime) -> bool:
    """Check if a campaign can start at the provided time.

    Example before scheduling campaign::

        if not can_start_campaign_at(calendar, scheduled_at):
            # shift scheduled_at to after havdalah (TODO link to JewishDayInfo.zmanim.havdalah)
    """

    return not ShabbatGuard(calendar_service).is_restricted(dt)
