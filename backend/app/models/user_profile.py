from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, Float, Index, String
from sqlalchemy.dialects.postgresql import ARRAY, UUID

from app.core.database import Base


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    external_id = Column(String(255), nullable=False)
    channel = Column(String(50), nullable=False)
    username = Column(String(255), nullable=True)
    display_name = Column(String(255), nullable=True)
    language = Column(String(10), nullable=True)
    timezone = Column(String(100), nullable=True)
    joined_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_activity_at = Column(DateTime, nullable=True)
    engagement_score = Column(Float, default=0.0, nullable=False)
    tags = Column(ARRAY(String), default=list)

    __table_args__ = (
        Index("idx_user_profile_external", "external_id", "channel"),
        Index("idx_user_profile_engagement", engagement_score.desc()),
    )
