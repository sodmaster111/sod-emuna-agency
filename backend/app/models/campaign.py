from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class BroadcastCampaign(Base):
    __tablename__ = "broadcast_campaigns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    channel = Column(String(50), nullable=False)
    segment_filter = Column(JSON, nullable=False)
    message_template = Column(Text, nullable=False)
    status = Column(String(50), nullable=False, default="draft")
    scheduled_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CampaignRecipient(Base):
    __tablename__ = "campaign_recipients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    campaign_id = Column(
        UUID(as_uuid=True), ForeignKey("broadcast_campaigns.id"), nullable=False
    )
    user_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.id"), nullable=False)
    status = Column(String(50), nullable=False, default="pending")
    last_update_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


Index("idx_campaign_recipient_campaign", CampaignRecipient.campaign_id)
Index("idx_campaign_recipient_user", CampaignRecipient.user_id)
