from __future__ import annotations

from datetime import date
import os
from typing import Any
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user_profile import UserProfile
from app.services.user_engagement import (
    EngagementEvent,
    get_or_create_user,
    register_event,
)

router = APIRouter(prefix="/ritual", tags=["Ritual"])


class DailyPlanItem(BaseModel):
    type: str
    code: str | None = None
    label: dict[str, str] | None = None
    time_hint: str | None = None
    extra: dict | None = None


class DailyPlanResponse(BaseModel):
    date: date
    jewish_date_str: str
    day_type: str
    items: list[DailyPlanItem]


class MissionsResponse(BaseModel):
    missions: list[dict]


class MissionStatusUpdateRequest(BaseModel):
    mission_id: UUID
    status: str


class EngagementEventRequest(BaseModel):
    event: str
    payload: dict | None = None


class DailyDevotionPlan:
    def __init__(
        self,
        *,
        user_id: UUID,
        plan_date: date,
        jewish_date_str: str,
        day_type: str,
        items: list[DailyPlanItem],
    ):
        self.user_id = user_id
        self.date = plan_date
        self.jewish_date_str = jewish_date_str
        self.day_type = day_type
        self.items = items


class SpiritualMissionInstance:
    def __init__(
        self,
        *,
        mission_id: UUID,
        title: str,
        description: str,
        status: str,
        category: str,
        mission_date: date,
    ):
        self.id = mission_id
        self.title = title
        self.description = description
        self.status = status
        self.category = category
        self.date = mission_date

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "category": self.category,
            "date": self.date,
        }


class JewishCalendarService:
    def __init__(self, env: str | None = None):
        self.env = env or "production"

    def get_jewish_date_str(self, plan_date: date) -> str:
        return plan_date.isoformat()


_PLAN_STORE: dict[tuple[UUID, date], DailyDevotionPlan] = {}
_MISSION_STORE: dict[UUID, SpiritualMissionInstance] = {}


async def _get_user(session: AsyncSession, *, external_id: str, channel: str) -> UserProfile:
    result = await session.execute(
        select(UserProfile).where(
            UserProfile.external_id == external_id, UserProfile.channel == channel
        )
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def _generate_default_plan(user: UserProfile, calendar_service: JewishCalendarService) -> DailyDevotionPlan:
    today = date.today()
    jewish_date = calendar_service.get_jewish_date_str(today)
    items = [
        DailyPlanItem(
            type="prayer",
            code="morning_prayer",
            label={"en": "Morning Prayer"},
            time_hint="morning",
        ),
        DailyPlanItem(
            type="study",
            code="torah_portion",
            label={"en": "Study today's portion"},
            time_hint="afternoon",
        ),
    ]
    return DailyDevotionPlan(
        user_id=user.id,
        plan_date=today,
        jewish_date_str=jewish_date,
        day_type="regular",
        items=items,
    )


async def get_or_generate_plan(
    session: AsyncSession,
    *,
    user: UserProfile,
    calendar_service: JewishCalendarService,
) -> DailyDevotionPlan:
    key = (user.id, date.today())
    if key not in _PLAN_STORE:
        _PLAN_STORE[key] = _generate_default_plan(user, calendar_service)
    return _PLAN_STORE[key]


async def _get_missions_for_today(user: UserProfile) -> list[SpiritualMissionInstance]:
    today = date.today()
    missions = [mission for mission in _MISSION_STORE.values() if mission.date == today]
    if missions:
        return missions

    default_mission = SpiritualMissionInstance(
        mission_id=uuid4(),
        title="Share a moment of gratitude",
        description="Send a thankful message to a friend.",
        status="pending",
        category="gratitude",
        mission_date=today,
    )
    _MISSION_STORE[default_mission.id] = default_mission
    return [default_mission]


async def _mark_mission_status(mission_id: UUID, status: str) -> SpiritualMissionInstance:
    mission = _MISSION_STORE.get(mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    mission.status = status
    return mission


@router.get("/daily-plan", response_model=DailyPlanResponse)
async def get_daily_plan(
    external_id: str = Query(...),
    channel: str = Query(...),
    db: AsyncSession = Depends(get_db),
) -> DailyPlanResponse:
    user = await get_or_create_user(db, external_id=external_id, channel=channel)
    calendar_env = os.getenv("JEWISH_CALENDAR_ENV", "production")
    calendar_service = JewishCalendarService(env=calendar_env)
    plan = await get_or_generate_plan(db, user=user, calendar_service=calendar_service)
    return DailyPlanResponse(
        date=plan.date,
        jewish_date_str=plan.jewish_date_str,
        day_type=plan.day_type,
        items=plan.items,
    )


@router.get("/missions", response_model=MissionsResponse)
async def get_missions(
    external_id: str = Query(...),
    channel: str = Query(...),
    db: AsyncSession = Depends(get_db),
) -> MissionsResponse:
    user = await _get_user(db, external_id=external_id, channel=channel)
    missions = await _get_missions_for_today(user)
    return MissionsResponse(missions=[mission.to_dict() for mission in missions])


@router.post("/mission-status", response_model=dict)
async def update_mission_status(payload: MissionStatusUpdateRequest) -> dict:
    mission = await _mark_mission_status(payload.mission_id, payload.status)
    return mission.to_dict()


@router.post("/engagement", response_model=dict)
async def register_engagement(
    payload: EngagementEventRequest,
    external_id: str = Query(...),
    channel: str = Query(...),
    db: AsyncSession = Depends(get_db),
) -> dict:
    user = await get_or_create_user(db, external_id=external_id, channel=channel)
    try:
        event_enum = EngagementEvent(payload.event)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"Unknown event: {payload.event}") from exc

    updated_user = await register_event(db, user=user, event=event_enum)
    return {"engagement_score": updated_user.engagement_score}
