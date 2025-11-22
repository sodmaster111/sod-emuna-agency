from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING, Any, List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.spiritual_mission import (
    SpiritualMissionInstance,
    SpiritualMissionTemplate,
)

if TYPE_CHECKING:  # pragma: no cover - only for type checking
    from app.models.user_profile import UserProfile
    from app.schemas.jewish_calendar import JewishDayInfo


async def get_applicable_templates(
    session: AsyncSession,
    *,
    day_type: str,
    engagement_score: float,
) -> List[SpiritualMissionTemplate]:
    """Return mission templates that satisfy the provided day and engagement filters."""

    stmt = select(SpiritualMissionTemplate)
    result = await session.execute(stmt)
    templates = result.scalars().all()

    applicable: list[SpiritualMissionTemplate] = []

    for template in templates:
        conditions: dict[str, Any] = template.conditions or {}

        if "day_type" in conditions:
            allowed_day_types = conditions.get("day_type") or []
            if isinstance(allowed_day_types, str):
                allowed_day_types = [allowed_day_types]
            if day_type not in allowed_day_types:
                continue

        if "min_engagement" in conditions:
            try:
                min_engagement = float(conditions.get("min_engagement", 0))
            except (TypeError, ValueError):  # pragma: no cover - defensive
                min_engagement = 0
            if engagement_score < min_engagement:
                continue

        applicable.append(template)

    return applicable


async def instantiate_missions_for_user(
    session: AsyncSession,
    *,
    user: "UserProfile",
    day_info: "JewishDayInfo",
    date: date,
) -> list[SpiritualMissionInstance]:
    """Create mission instances for a user based on applicable templates."""

    day_type_value = getattr(day_info, "day_type", None)
    if day_type_value is None and isinstance(day_info, dict):  # pragma: no cover - defensive
        day_type_value = day_info.get("day_type")

    applicable_templates = await get_applicable_templates(
        session,
        day_type=day_type_value or "",
        engagement_score=getattr(user, "engagement_score", 0.0),
    )

    instances: list[SpiritualMissionInstance] = []

    for template in applicable_templates:
        instance = SpiritualMissionInstance(
            user_id=user.id,
            template_id=template.id,
            date=date,
            status="pending",
            channel=None,
            metadata={},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        session.add(instance)
        instances.append(instance)

    await session.flush()
    return instances


async def mark_mission_status(
    session: AsyncSession,
    *,
    mission_id: UUID,
    status: str,
) -> SpiritualMissionInstance:
    """Update and persist the status of a mission instance."""

    stmt = select(SpiritualMissionInstance).where(SpiritualMissionInstance.id == mission_id)
    result = await session.execute(stmt)
    mission = result.scalar_one_or_none()

    if mission is None:
        raise ValueError(f"SpiritualMissionInstance {mission_id} not found")

    mission.status = status
    mission.updated_at = datetime.utcnow()

    session.add(mission)
    await session.commit()
    await session.refresh(mission)
    return mission
