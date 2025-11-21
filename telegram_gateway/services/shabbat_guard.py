from __future__ import annotations

from datetime import datetime


class ShabbatGuardError(RuntimeError):
    """Raised when an action is blocked due to Shabbat or Yom Tov."""


def is_shabbat_or_yom_tov(now: datetime) -> bool:
    """Return True if the provided datetime falls on Shabbat or Yom Tov.

    TODO: Implement real halachic calendar check (e.g., via hebcal or dedicated
    library/API).
    """

    return False


def ensure_not_shabbat(now: datetime) -> None:
    """Ensure operations are not executed during Shabbat or Yom Tov."""

    if is_shabbat_or_yom_tov(now):
        raise ShabbatGuardError("Broadcast blocked due to Shabbat/Yom Tov")
