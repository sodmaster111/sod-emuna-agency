from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, Float, String
from sqlalchemy.dialects.postgresql import ARRAY, UUID

from app.core.database import Base


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    engagement_score = Column(Float, nullable=True)
    language = Column(String(10), nullable=True)
    tags = Column(ARRAY(String), default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
