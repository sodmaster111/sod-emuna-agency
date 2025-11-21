"""Models for templated and scheduled mission broadcasts."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class MissionTemplate(Base):
    """Reusable mission definitions with scheduling metadata."""

    __tablename__ = "mission_templates"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    mission_type = Column(String, nullable=False)
    content_category_slug = Column(String, nullable=True)
    target_channel = Column(String, nullable=False)
    cron_expr = Column(String, nullable=False)
    use_orchestrator = Column(Boolean, default=False, nullable=False)

    instances = relationship(
        "MissionInstance",
        back_populates="template",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class MissionInstance(Base):
    """Concrete execution record for a mission template."""

    __tablename__ = "mission_instances"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("mission_templates.id", ondelete="CASCADE"), nullable=False)
    scheduled_for = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    executed_at = Column(DateTime, nullable=True)
    status = Column(String, default="pending", nullable=False, index=True)
    result_summary = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    task_id = Column(String, nullable=True, index=True)

    template = relationship("MissionTemplate", back_populates="instances")
