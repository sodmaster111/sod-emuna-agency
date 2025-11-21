from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import JSON, Column, DateTime, Float, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID

from app.core.database import Base


class AMACProposal(Base):
    __tablename__ = "amac_proposals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    budget_ton = Column(Float, nullable=True)
    tags = Column(ARRAY(String), default=list)
    status = Column(String(50), nullable=False, default="pending")
    board_decision = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
