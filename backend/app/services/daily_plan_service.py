from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Protocol
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.daily_plan import DailyDevotionPlan
from app.models.user_profile import UserProfile


@dataclass
class JewishDayInfo:
    date: date
    jewish_date_str: str
    day_type: str


class JewishCalendarService(Protocol):
    async def get_jewish_day_info(self, target_date: date | None = None) -> JewishDayInfo: ...

    async def get_day_info(self, target_date: date | None = None) -> JewishDayInfo: ...


_LABELS: dict[str, dict[str, str]] = {
    "modeh_ani": {"he": "מודה אני", "en": "Modeh Ani", "ru": "Моде ани"},
    "tehillim_23": {"he": "תהילים כ""ג", "en": "Tehillim 23", "ru": "Псалом 23"},
    "tehillim_95": {"he": "תהילים צ""ה", "en": "Tehillim 95", "ru": "Псалом 95"},
    "tehillim_130": {"he": "תהילים קל", "en": "Tehillim 130", "ru": "Псалом 130"},
    "evening_reflection": {"he": "התבוננות ערב", "en": "Evening reflection", "ru": "Вечернее размышление"},
    "parsha_insight": {"he": "קריאת פרשה", "en": "Parsha insight", "ru": "Глава недели"},
    "fast_day_focus": {"he": "הכוונה ליום צום", "en": "Fast day focus", "ru": "Настрой на пост"},
    "learning_boost": {"he": "לימוד יומי נוסף", "en": "Extra daily learning", "ru": "Дополнительное изучение"},
}


def _determine_target_date(user: UserProfile, target_date: date | None) -> date:
    if target_date:
        return target_date

    if user.timezone:
        try:
            return datetime.now(ZoneInfo(user.timezone)).date()
        except Exception:
            pass

    return datetime.utcnow().date()


def _label(code: str) -> dict[str, str]:
    return _LABELS.get(code, {"en": code})


def _build_items(day_info: JewishDayInfo, user: UserProfile) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = [
        {
            "type": "tefillah",
            "code": "modeh_ani",
            "label": _label("modeh_ani"),
            "time_hint": "morning",
        },
        {
            "type": "tehillim",
            "code": "tehillim_23",
            "ref": "Tehillim 23",
            "label": _label("tehillim_23"),
            "time_hint": "morning",
        },
        {
            "type": "reflection",
            "code": "daily_reflection",
            "label": _label("evening_reflection"),
            "time_hint": "evening",
        },
    ]

    day_type = (day_info.day_type or "").lower()
    if "shabbat" in day_type:
        items.extend(
            [
                {
                    "type": "tehillim",
                    "code": "tehillim_95",
                    "ref": "Tehillim 95",
                    "label": _label("tehillim_95"),
                    "time_hint": "kabbalat_shabbat",
                },
                {
                    "type": "torah",
                    "code": "parsha_insight",
                    "label": _label("parsha_insight"),
                    "time_hint": "afternoon",
                },
            ]
        )
    elif "fast" in day_type:
        items.extend(
            [
                {
                    "type": "practice",
                    "code": "fast_day_focus",
                    "label": _label("fast_day_focus"),
                    "note": "Mindful fast day intention",
                    "time_hint": "all_day",
                },
                {
                    "type": "tehillim",
                    "code": "tehillim_130",
                    "ref": "Tehillim 130",
                    "label": _label("tehillim_130"),
                    "time_hint": "afternoon",
                },
            ]
        )

    if (user.engagement_score or 0) >= 50:
        items.append(
            {
                "type": "learning",
                "code": "learning_boost",
                "label": _label("learning_boost"),
                "ref": "Mishnah Berurah — short insight",
                "time_hint": "midday",
            }
        )

    return items


async def _fetch_day_info(
    calendar_service: JewishCalendarService, target_date: date | None
) -> JewishDayInfo:
    if hasattr(calendar_service, "get_jewish_day_info"):
        return await calendar_service.get_jewish_day_info(target_date=target_date)

    if hasattr(calendar_service, "get_day_info"):
        return await calendar_service.get_day_info(target_date=target_date)

    raise AttributeError("Calendar service does not expose a day info method")


async def generate_daily_plan_for_user(
    session: AsyncSession,
    *,
    user: UserProfile,
    calendar_service: JewishCalendarService,
    target_date: date | None = None,
) -> DailyDevotionPlan:
    plan_date = _determine_target_date(user, target_date)
    day_info = await _fetch_day_info(calendar_service, plan_date)

    items = _build_items(day_info, user)

    result = await session.execute(
        select(DailyDevotionPlan).where(
            DailyDevotionPlan.user_id == user.id, DailyDevotionPlan.date == plan_date
        )
    )
    existing_plan = result.scalar_one_or_none()

    if existing_plan:
        existing_plan.jewish_date_str = day_info.jewish_date_str
        existing_plan.day_type = day_info.day_type
        existing_plan.items = items
        existing_plan.updated_at = datetime.utcnow()
        plan = existing_plan
    else:
        plan = DailyDevotionPlan(
            user_id=user.id,
            date=plan_date,
            jewish_date_str=day_info.jewish_date_str,
            day_type=day_info.day_type,
            items=items,
        )
        session.add(plan)

    await session.commit()
    await session.refresh(plan)

    return plan


async def get_or_generate_plan(
    session: AsyncSession,
    *,
    user: UserProfile,
    calendar_service: JewishCalendarService,
    target_date: date | None = None,
) -> DailyDevotionPlan:
    plan_date = _determine_target_date(user, target_date)

    result = await session.execute(
        select(DailyDevotionPlan).where(
            DailyDevotionPlan.user_id == user.id, DailyDevotionPlan.date == plan_date
        )
    )
    plan = result.scalar_one_or_none()

    if plan:
        return plan

    return await generate_daily_plan_for_user(
        session,
        user=user,
        calendar_service=calendar_service,
        target_date=plan_date,
    )
