from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import JSON, Column, Date, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class SpiritualMissionTemplate(Base):
    __tablename__ = "spiritual_mission_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    code = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(64), nullable=False)
    conditions = Column(JSON, default=dict)
    payload = Column(JSON, default=dict)

    __table_args__ = (
        Index("ux_spiritual_mission_template_code", "code", unique=True),
    )


class SpiritualMissionInstance(Base):
    __tablename__ = "spiritual_mission_instances"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.id"), nullable=False)
    template_id = Column(
        UUID(as_uuid=True),
        ForeignKey("spiritual_mission_templates.id"),
        nullable=False,
    )
    date = Column(Date, nullable=False)
    status = Column(String(32), nullable=False, default="pending")
    channel = Column(String(32), nullable=True)
    metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    __table_args__ = (
        Index("idx_spiritual_mission_instance_user_date_status", "user_id", "date", "status"),
    )


# Example mission templates to seed via fixtures/migrations:
# - "tehillim_morning_short": recite Tehillim 23 in the morning.
# - "mode_ani_wakeup": say Mode Ani upon waking.
# - "shema_before_sleep": recite Shema before sleep.
# - "shabbat_candles_early": light Shabbat candles 10 minutes earlier than usual (for women).
