from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - used only for type checking
    from app.core.halachic_time import HalachicTimeService as JewishCalendarService


class ShabbatRestrictedError(Exception):
    """Raised when an operation is attempted during Shabbat or Yom Tov."""


class ShabbatGuard:
    def __init__(self, calendar_service: "JewishCalendarService"):
        self.calendar = calendar_service

    def is_restricted(self, dt: datetime | None = None) -> bool:
        """
        Return True when the given datetime falls on Shabbat or Yom Tov.
        Defaults to the current time in the configured calendar timezone.
        """

        target_dt = dt or datetime.now(self.calendar.timezone)
        return self.calendar.is_shabbat_or_yom_tov(target_dt)

    def ensure_allowed(self, dt: datetime | None = None) -> None:
        """Raise ShabbatRestrictedError when an operation is not allowed."""

        if self.is_restricted(dt):
            raise ShabbatRestrictedError(
                "Operation not allowed during Shabbat/Yom Tov"
            )


def can_send_message_now(calendar_service: "JewishCalendarService") -> bool:
    """Check whether sending a message now is permitted."""

    return not ShabbatGuard(calendar_service).is_restricted()


def can_start_campaign_at(
    calendar_service: "JewishCalendarService", dt: datetime
) -> bool:
    """Check whether a campaign can start at the provided datetime."""

    return not ShabbatGuard(calendar_service).is_restricted(dt)


# Usage examples:
# Before sending Telegram broadcast:
#     if not can_send_message_now(calendar):
#         # skip or reschedule
#
# Before scheduling campaign:
#     if not can_start_campaign_at(calendar, scheduled_at):
#         # shift scheduled_at to after havdalah (TODO link to JewishDayInfo.zmanim.havdalah)
