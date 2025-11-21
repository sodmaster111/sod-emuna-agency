from __future__ import annotations

import logging
import secrets
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.referral import ReferralLink

if TYPE_CHECKING:  # pragma: no cover - only for type checking
    from app.models.user_profile import UserProfile  # noqa: F401

logger = logging.getLogger(__name__)

REFERRAL_CODE_BYTES = 6


def _generate_referral_code() -> str:
    """Generate a short, URL-safe referral code."""

    return secrets.token_urlsafe(REFERRAL_CODE_BYTES)


async def _record_user_engagement(
    session: AsyncSession,
    *,
    user_id,
    event_type: str,
    metadata: Optional[Dict[str, Any]] = None,
):
    """Best-effort engagement logger to keep referral analytics decoupled."""

    try:
        from app.models.user_engagement import UserEngagement  # type: ignore
    except Exception as exc:  # pragma: no cover - optional dependency
        logger.warning("UserEngagement model unavailable; skipping persistence: %s", exc)
        return {"user_id": user_id, "event_type": event_type, "metadata": metadata or {}}

    event = UserEngagement(  # type: ignore
        user_id=user_id,
        event_type=event_type,
        metadata=metadata or {},
        created_at=datetime.utcnow(),
    )
    session.add(event)
    await session.flush()
    return event


async def get_or_create_referral_link(
    session: AsyncSession, owner_user: "UserProfile", channel: str
) -> ReferralLink:
    """Return an existing referral link for the owner/channel or create a new one."""

    existing_stmt = select(ReferralLink).where(
        ReferralLink.owner_user_id == owner_user.id, ReferralLink.channel == channel
    )
    result = await session.execute(existing_stmt)
    referral_link = result.scalar_one_or_none()

    if referral_link:
        return referral_link

    code = _generate_referral_code()

    while True:
        conflict_stmt = select(ReferralLink).where(
            ReferralLink.code == code, ReferralLink.channel == channel
        )
        conflict_result = await session.execute(conflict_stmt)
        if conflict_result.scalar_one_or_none() is None:
            break
        code = _generate_referral_code()

    referral_link = ReferralLink(
        owner_user_id=owner_user.id,
        code=code,
        channel=channel,
    )
    session.add(referral_link)
    await session.flush()
    return referral_link


async def handle_referral_click(
    session: AsyncSession, *, code: str, channel: str
) -> ReferralLink | None:
    """Track a referral click and return the matched link if found."""

    stmt = select(ReferralLink).where(ReferralLink.code == code, ReferralLink.channel == channel)
    result = await session.execute(stmt)
    referral_link = result.scalar_one_or_none()

    if referral_link is None:
        return None

    referral_link.clicks_count += 1
    await session.commit()
    await session.refresh(referral_link)
    return referral_link


async def handle_referral_accept(
    session: AsyncSession,
    *,
    code: str,
    channel: str,
    new_user: "UserProfile",
) -> dict:
    """Handle a referral acceptance and register engagement for the referrer."""

    stmt = select(ReferralLink).where(ReferralLink.code == code, ReferralLink.channel == channel)
    result = await session.execute(stmt)
    referral_link = result.scalar_one_or_none()

    if referral_link is None:
        return {"status": "invalid_referral", "code": code, "channel": channel}

    referral_link.accepted_count += 1

    events = []
    events.append(
        await _record_user_engagement(
            session,
            user_id=referral_link.owner_user_id,
            event_type="INVITE_SENT",
            metadata={"channel": channel, "code": code},
        )
    )
    events.append(
        await _record_user_engagement(
            session,
            user_id=referral_link.owner_user_id,
            event_type="INVITE_ACCEPTED",
            metadata={"channel": channel, "code": code, "new_user_id": getattr(new_user, "id", None)},
        )
    )

    if hasattr(new_user, "tags"):
        try:
            if new_user.tags is None:
                new_user.tags = []
            if "referred" not in new_user.tags:
                new_user.tags.append("referred")
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("Unable to tag referred user: %s", exc)

    session.add(referral_link)
    await session.commit()
    await session.refresh(referral_link)

    summary = {
        "status": "accepted",
        "referrer_id": referral_link.owner_user_id,
        "referral_code": referral_link.code,
        "channel": referral_link.channel,
        "clicks_count": referral_link.clicks_count,
        "accepted_count": referral_link.accepted_count,
        "events": events,
    }
    return summary
