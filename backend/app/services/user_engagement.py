from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_profile import UserProfile


class EngagementEvent(str, Enum):
    MESSAGE_READ = "message_read"
    LINK_CLICKED = "link_clicked"
    BUTTON_CLICKED = "button_clicked"
    PRAYER_SUBMITTED = "prayer_submitted"
    INVITE_SENT = "invite_sent"
    INVITE_ACCEPTED = "invite_accepted"


async def get_or_create_user(
    session: AsyncSession,
    *,
    external_id: str,
    channel: str,
    username: str | None = None,
    display_name: str | None = None,
    language: str | None = None,
) -> UserProfile:
    result = await session.execute(
        select(UserProfile).where(
            UserProfile.external_id == external_id, UserProfile.channel == channel
        )
    )
    user = result.scalars().first()

    now = datetime.utcnow()
    if user:
        updated = False
        if username is not None and user.username != username:
            user.username = username
            updated = True
        if display_name is not None and user.display_name != display_name:
            user.display_name = display_name
            updated = True
        if language is not None and user.language != language:
            user.language = language
            updated = True
        if updated:
            session.add(user)
            await session.commit()
            await session.refresh(user)
        return user

    user = UserProfile(
        external_id=external_id,
        channel=channel,
        username=username,
        display_name=display_name,
        language=language,
        joined_at=now,
        last_activity_at=None,
        engagement_score=0.0,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def register_event(
    session: AsyncSession,
    user: UserProfile,
    event: EngagementEvent,
    weight_override: Optional[float] = None,
) -> UserProfile:
    base_weights: dict[EngagementEvent, float] = {
        EngagementEvent.MESSAGE_READ: 0.5,
        EngagementEvent.LINK_CLICKED: 1.0,
        EngagementEvent.BUTTON_CLICKED: 1.0,
        EngagementEvent.PRAYER_SUBMITTED: 2.0,
        EngagementEvent.INVITE_SENT: 1.5,
        EngagementEvent.INVITE_ACCEPTED: 3.0,
    }

    delta = weight_override if weight_override is not None else base_weights[event]
    user.engagement_score = (user.engagement_score or 0.0) + delta
    user.last_activity_at = datetime.utcnow()

    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def decay_scores(session: AsyncSession, factor: float = 0.99) -> None:
    await session.execute(
        update(UserProfile).values(
            engagement_score=UserProfile.engagement_score * factor
        )
    )
    await session.commit()
