"""Pinkas log model for recording agent activity and commands."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Pinkas(Base):
    """Pinkas log entries for agent operations and system actions."""

    __tablename__ = "pinkas"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid4
    )
    agent: Mapped[str] = mapped_column(String, nullable=False)
    thought: Mapped[str | None] = mapped_column(Text, nullable=True)
    action: Mapped[str | None] = mapped_column(String, nullable=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    status: Mapped[str] = mapped_column(String, default="ok")
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    __table_args__ = (
        Index("idx_pinkas_timestamp", timestamp.desc()),
        Index("idx_pinkas_agent", agent),
        Index("idx_pinkas_status", status),
    )

    def as_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "agent": self.agent,
            "thought": self.thought,
            "action": self.action,
            "payload": self.payload or {},
            "status": self.status,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }
