"""Community analytics and auto-proposal helpers."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, List

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.amac_proposal import AMACProposal
from app.models.campaign import Campaign
from app.models.user_profile import UserProfile
from app.services.amac_proposals import generate_proposals_from_metrics


async def get_basic_community_stats(session: AsyncSession) -> dict:
    """Return a set of high-level community metrics."""

    total_users_result = await session.execute(select(func.count(UserProfile.id)))
    total_users = total_users_result.scalar_one() or 0

    recent_threshold = datetime.utcnow() - timedelta(days=7)
    active_result = await session.execute(
        select(func.count(UserProfile.id)).where(UserProfile.last_active_at >= recent_threshold)
    )
    active_last_7d = active_result.scalar_one() or 0

    engagement_result = await session.execute(select(func.avg(UserProfile.engagement_score)))
    avg_engagement_score = engagement_result.scalar_one() or 0.0

    language_rows = await session.execute(
        select(UserProfile.language, func.count(UserProfile.id))
        .group_by(UserProfile.language)
        .order_by(UserProfile.language)
    )
    segments_count_by_language: Dict[str, int] = {
        language: count for language, count in language_rows.all()
    }

    # Tag distribution (top 5)
    tag_counts_query = (
        select(func.unnest(UserProfile.tags).label("tag"), func.count().label("count"))
        .group_by("tag")
        .order_by(func.count().desc())
        .limit(5)
    )
    tag_rows = await session.execute(tag_counts_query)
    segments_count_by_tag_top5: List[Dict[str, Any]] = [
        {"tag": tag, "count": count} for tag, count in tag_rows.all()
    ]

    return {
        "total_users": total_users,
        "active_last_7d": active_last_7d,
        "avg_engagement_score": float(avg_engagement_score or 0),
        "segments_count_by_language": segments_count_by_language,
        "segments_count_by_tag_top5": segments_count_by_tag_top5,
    }


async def get_campaign_stats(session: AsyncSession) -> dict:
    """Aggregate campaign delivery statistics."""

    total_campaigns_result = await session.execute(select(func.count(Campaign.id)))
    total_campaigns = total_campaigns_result.scalar_one() or 0

    last_campaigns_query = (
        select(
            Campaign.name,
            Campaign.channel,
            Campaign.recipients_count,
            Campaign.status,
            Campaign.created_at,
        )
        .order_by(Campaign.created_at.desc())
        .limit(5)
    )
    last_campaigns_rows = await session.execute(last_campaigns_query)
    last_campaigns = [
        {
            "name": name,
            "channel": channel,
            "recipients_count": recipients_count,
            "status": status,
            "created_at": created_at,
        }
        for name, channel, recipients_count, status, created_at in last_campaigns_rows.all()
    ]

    delivery_totals_query = select(
        func.sum(Campaign.sent_count), func.sum(Campaign.failed_count)
    )
    sent_total, failed_total = (
        await session.execute(delivery_totals_query)
    ).one_or_none() or (0, 0)

    sent_total = sent_total or 0
    failed_total = failed_total or 0
    denominator = sent_total + failed_total
    approximate_delivery_rate = (sent_total / denominator) if denominator else 0.0

    return {
        "total_campaigns": total_campaigns,
        "last_campaigns": last_campaigns,
        "approximate_delivery_rate": approximate_delivery_rate,
    }


async def _language_growth_candidates(session: AsyncSession) -> list[str]:
    """Detect languages with rapid recent growth."""

    recent_window = datetime.utcnow() - timedelta(days=7)
    previous_window = datetime.utcnow() - timedelta(days=14)

    recent_counts_query = (
        select(UserProfile.language, func.count(UserProfile.id))
        .where(UserProfile.created_at >= recent_window)
        .group_by(UserProfile.language)
    )
    previous_counts_query = (
        select(UserProfile.language, func.count(UserProfile.id))
        .where(
            UserProfile.created_at >= previous_window,
            UserProfile.created_at < recent_window,
        )
        .group_by(UserProfile.language)
    )

    recent_rows = await session.execute(recent_counts_query)
    previous_rows = await session.execute(previous_counts_query)

    recent_map = {lang: count for lang, count in recent_rows.all()}
    previous_map = {lang: count for lang, count in previous_rows.all()}

    growth_candidates: list[str] = []
    for lang, recent_count in recent_map.items():
        previous_count = previous_map.get(lang, 0) or 0
        if recent_count >= 5 and recent_count >= (previous_count * 1.5 + 1):
            growth_candidates.append(lang)

    return growth_candidates


async def generate_community_growth_proposals(
    session: AsyncSession, limit: int = 3
) -> list[AMACProposal]:
    """Create rule-based AMAC proposals from community metrics."""

    stats = await get_basic_community_stats(session)
    proposals: List[AMACProposal] = []

    def enqueue_proposal(title: str, description: str, tags: list[str] | None = None):
        if len(proposals) >= limit:
            return
        proposal = AMACProposal(
            title=title,
            description=description,
            tags=tags or [],
            status="pending",
        )
        session.add(proposal)
        proposals.append(proposal)

    total_users = stats.get("total_users", 0) or 0
    active_last_7d = stats.get("active_last_7d", 0) or 0
    avg_engagement = stats.get("avg_engagement_score", 0.0) or 0.0

    if total_users > 0 and (active_last_7d / total_users) < 0.3:
        enqueue_proposal(
            "Reactivation Campaign for inactive members",
            "Active base dipped below 30% of total. Launch outreach to re-engage inactive members.",
            tags=["reactivation", "retention"],
        )

    language_growth = await _language_growth_candidates(session)
    for lang in language_growth:
        if len(proposals) >= limit:
            break
        if lang in {"ru", "he"}:
            enqueue_proposal(
                f"Double content for {lang} segment",
                "Recent growth indicates momentum. Double content cadence and allocate moderation support for the segment.",
                tags=["growth", lang],
            )

    if avg_engagement < 0.45:
        enqueue_proposal(
            "Increase personalization in onboarding",
            "Average engagement is trending low. Personalize onboarding sequences and surface community-relevant missions.",
            tags=["engagement", "onboarding"],
        )

    if len(proposals) < limit:
        supplemental = await generate_proposals_from_metrics(session, limit=limit - len(proposals))
        proposals.extend(supplemental)
    else:
        await session.commit()
        for proposal in proposals:
            await session.refresh(proposal)
        return proposals

    await session.commit()
    for proposal in proposals:
        await session.refresh(proposal)

    return proposals
