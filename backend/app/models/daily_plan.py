from __future__ import annotations

from datetime import date, datetime
from uuid import uuid4

from sqlalchemy import JSON, Column, Date, DateTime, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class DailyDevotionPlan(Base):
    __tablename__ = "daily_devotion_plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.id"), nullable=False)
    date = Column(Date, nullable=False)
    jewish_date_str = Column(String(64), nullable=False)
    day_type = Column(String(64), nullable=False)
    items = Column(JSON, nullable=False, default=list)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("idx_daily_devotion_user_date", "user_id", "date", unique=True),
    )
