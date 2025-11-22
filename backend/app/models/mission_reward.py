from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, Float, ForeignKey, Index, JSON, String
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class MissionReward(Base):
    __tablename__ = "mission_rewards"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.id"), nullable=False)
    mission_instance_id = Column(
        UUID(as_uuid=True), ForeignKey("spiritual_mission_instances.id"), nullable=False
    )
    points = Column(Float, nullable=False)
    ton_equivalent = Column(Float, nullable=True)
    status = Column(String(32), nullable=False, default="earned")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    payout_tx_hash = Column(String(255), nullable=True)
    metadata = Column(JSON, default=dict, nullable=False)

    __table_args__ = (
        Index("idx_mission_reward_user", "user_id"),
        Index("idx_mission_reward_status", "status"),
    )
