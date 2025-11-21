from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class ReferralLink(Base):
    __tablename__ = "referral_links"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    owner_user_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.id"), nullable=False)
    code = Column(String(64), nullable=False)
    channel = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    clicks_count = Column(Integer, default=0, nullable=False)
    accepted_count = Column(Integer, default=0, nullable=False)

    __table_args__ = (
        Index("idx_referral_code", "code", "channel"),
        Index("idx_referral_owner", "owner_user_id"),
    )
