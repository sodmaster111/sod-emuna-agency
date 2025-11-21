from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_profile import UserProfile


async def get_or_create_user(
    session: AsyncSession,
    *,
    external_id: str,
    channel: str,
    username: Optional[str] = None,
    display_name: Optional[str] = None,
) -> UserProfile:
    result = await session.execute(
        select(UserProfile).where(
            UserProfile.external_id == external_id, UserProfile.channel == channel
        )
    )
    user = result.scalar_one_or_none()

    if user is None:
        user = UserProfile(
            external_id=external_id,
            channel=channel,
            username=username,
            display_name=display_name,
        )
        session.add(user)
        await session.flush()
    else:
        updated = False
        if username and user.username != username:
            user.username = username
            updated = True
        if display_name and user.display_name != display_name:
            user.display_name = display_name
            updated = True
        if updated:
            session.add(user)
            await session.flush()

    return user
