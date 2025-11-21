"""Pinkas audit log model."""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from app.db.session import Base


class Pinkas(Base):
    """Persistent audit record for agent actions."""

    __tablename__ = "pinkas"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
    )
    agent = Column(String, nullable=False, index=True)
    action = Column(String, nullable=False)
    payload = Column(JSONB)
    status = Column(String, nullable=False, index=True)
    meta = Column(JSONB)

    def __repr__(self) -> str:  # pragma: no cover - for debugging
        return f"<Pinkas id={self.id} agent={self.agent} status={self.status}>"
