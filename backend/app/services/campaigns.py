from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID as UUIDType

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.campaign import BroadcastCampaign, CampaignRecipient
from app.models.user_profile import UserProfile


async def create_campaign(
    session: AsyncSession,
    *,
    name: str,
    channel: str,
    segment_filter: dict,
    message_template: str,
    scheduled_at: datetime | None = None,
) -> BroadcastCampaign:
    campaign = BroadcastCampaign(
        name=name,
        channel=channel,
        segment_filter=segment_filter,
        message_template=message_template,
        scheduled_at=scheduled_at,
        status="draft" if scheduled_at is None else "scheduled",
    )
    session.add(campaign)
    await session.commit()
    await session.refresh(campaign)
    return campaign


def _apply_segment_filters(
    base_query: Select[Any],
    *,
    min_score: float | None = None,
    language: str | None = None,
    tags_any: list[str] | None = None,
) -> Select[Any]:
    query = base_query
    if min_score is not None:
        query = query.where(UserProfile.engagement_score >= min_score)
    if language:
        query = query.where(UserProfile.language == language)
    if tags_any:
        query = query.where(UserProfile.tags.overlap(tags_any))
    return query


async def build_recipients_for_campaign(
    session: AsyncSession,
    campaign: BroadcastCampaign,
    *,
    limit: int | None = None,
) -> int:
    segment_filter = campaign.segment_filter or {}
    min_score = segment_filter.get("min_score")
    language = segment_filter.get("language")
    tags_any = segment_filter.get("tags_any")

    existing_recipients_subquery = select(CampaignRecipient.user_id).where(
        CampaignRecipient.campaign_id == campaign.id
    )

    user_query: Select[Any] = select(UserProfile.id).where(
        ~UserProfile.id.in_(existing_recipients_subquery)
    )
    user_query = _apply_segment_filters(
        user_query, min_score=min_score, language=language, tags_any=tags_any
    )
    if limit is not None:
        user_query = user_query.limit(limit)

    result = await session.execute(user_query)
    user_ids = list(result.scalars().all())

    recipients: list[CampaignRecipient] = []
    now = datetime.utcnow()
    for user_id in user_ids:
        recipients.append(
            CampaignRecipient(
                campaign_id=campaign.id,
                user_id=user_id,
                status="pending",
                last_update_at=now,
            )
        )

    session.add_all(recipients)
    await session.commit()

    return len(recipients)


async def mark_recipient_status(
    session: AsyncSession, recipient_id: UUIDType, status: str
) -> None:
    result = await session.execute(
        select(CampaignRecipient).where(CampaignRecipient.id == recipient_id)
    )
    recipient = result.scalar_one_or_none()
    if recipient is None:
        return

    recipient.status = status
    recipient.last_update_at = datetime.utcnow()

    session.add(recipient)
    await session.commit()
