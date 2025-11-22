from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.mission_reward import MissionReward
from app.models.spiritual_mission_instance import SpiritualMissionInstance

if TYPE_CHECKING:  # pragma: no cover - only for type checking
    from app.models.user_profile import UserProfile


async def award_mission_completion(
    session: AsyncSession,
    *,
    mission_instance_id: UUID,
    points: float,
    ton_rate: float | None = None,
) -> MissionReward:
    """Create a reward entry for a completed mission instance."""

    mission_stmt = select(SpiritualMissionInstance).where(
        SpiritualMissionInstance.id == mission_instance_id
    )
    mission_result = await session.execute(mission_stmt)
    mission_instance = mission_result.scalar_one_or_none()

    if mission_instance is None:
        raise ValueError(f"Mission instance {mission_instance_id} not found")

    ton_equivalent = points * ton_rate if ton_rate is not None else None

    reward = MissionReward(
        user_id=mission_instance.user_id,
        mission_instance_id=mission_instance_id,
        points=points,
        ton_equivalent=ton_equivalent,
        status="earned",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    session.add(reward)
    await session.flush()
    return reward


async def get_user_rewards_summary(
    session: AsyncSession,
    *,
    user: "UserProfile",
) -> dict:
    """Return aggregated reward stats for a user."""

    base_filters = [MissionReward.user_id == user.id]
    non_cancelled_filter = MissionReward.status != "cancelled"

    async def _sum_for_status(status: str | None = None, *, include_cancelled: bool = False):
        conditions = list(base_filters)
        if not include_cancelled:
            conditions.append(non_cancelled_filter)
        if status is not None:
            conditions.append(MissionReward.status == status)

        stmt = select(
            func.coalesce(func.sum(MissionReward.points), 0.0),
            func.coalesce(func.sum(MissionReward.ton_equivalent), 0.0),
        ).where(*conditions)
        result = await session.execute(stmt)
        points_sum, ton_sum = result.one()
        return float(points_sum or 0.0), float(ton_sum or 0.0)

    total_points, total_ton_equivalent = await _sum_for_status(include_cancelled=False)
    earned_points, earned_ton_equivalent = await _sum_for_status("earned")
    pending_points, pending_ton_equivalent = await _sum_for_status("pending_payout")
    paid_points, paid_ton_equivalent = await _sum_for_status("paid")

    return {
        "total_points": total_points,
        "earned_points": earned_points,
        "pending_payout_points": pending_points,
        "paid_points": paid_points,
        "total_ton_equivalent": total_ton_equivalent if total_ton_equivalent else None,
        "earned_ton_equivalent": earned_ton_equivalent if earned_ton_equivalent else None,
        "pending_payout_ton_equivalent": pending_ton_equivalent if pending_ton_equivalent else None,
        "paid_ton_equivalent": paid_ton_equivalent if paid_ton_equivalent else None,
    }


async def mark_rewards_pending_payout(
    session: AsyncSession,
    *,
    user: "UserProfile",
    min_points_threshold: float,
) -> list[MissionReward]:
    """Move earned rewards to pending payout when the threshold is met."""

    earned_stmt = select(MissionReward).where(
        MissionReward.user_id == user.id, MissionReward.status == "earned"
    )
    earned_result = await session.execute(earned_stmt)
    earned_rewards = list(earned_result.scalars().all())

    total_points = sum(reward.points for reward in earned_rewards)
    if total_points < min_points_threshold:
        return []

    now = datetime.utcnow()
    for reward in earned_rewards:
        reward.status = "pending_payout"
        reward.updated_at = now

    await session.flush()
    return earned_rewards


async def mark_rewards_paid(
    session: AsyncSession,
    *,
    reward_ids: list[UUID],
    payout_tx_hash: str,
) -> None:
    """Mark rewards as paid and attach the payout transaction hash."""

    if not reward_ids:
        return None

    paid_stmt = select(MissionReward).where(MissionReward.id.in_(reward_ids))
    paid_result = await session.execute(paid_stmt)
    rewards = paid_result.scalars().all()

    now = datetime.utcnow()
    for reward in rewards:
        reward.status = "paid"
        reward.payout_tx_hash = payout_tx_hash
        reward.updated_at = now

    await session.flush()
