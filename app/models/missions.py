"""Models for templated and scheduled mission broadcasts."""
from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class MissionTemplate(Base):
    """Reusable mission definitions with scheduling metadata."""

    __tablename__ = "mission_templates"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    slug: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    mission_type: Mapped[str] = mapped_column(String, nullable=False)
    content_category_slug: Mapped[str | None] = mapped_column(String, nullable=True)
    target_channel: Mapped[str] = mapped_column(String, nullable=False)
    cron_expr: Mapped[str] = mapped_column(String, nullable=False)
    use_orchestrator: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    instances = relationship(
        "MissionInstance",
        back_populates="template",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class MissionInstance(Base):
    """Concrete execution record for a mission template."""

    __tablename__ = "mission_instances"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    template_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("mission_templates.id", ondelete="CASCADE"), nullable=False
    )
    scheduled_for: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, index=True
    )
    executed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String, default="pending", nullable=False)
    result_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    task_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)

    template = relationship("MissionTemplate", back_populates="instances")

    __table_args__ = (
        Index("idx_mission_status", status),
        Index("idx_mission_template", template_id),
    )
