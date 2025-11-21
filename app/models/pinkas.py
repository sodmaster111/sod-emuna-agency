"""Pinkas log model for recording agent activity and commands."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB

from app.core.database import Base


class Pinkas(Base):
    """Pinkas log entries for agent operations and system actions."""

    __tablename__ = "pinkas"

    id = Column(Integer, primary_key=True, index=True)
    agent = Column(String, index=True, nullable=False)
    thought = Column(Text, nullable=True)
    action = Column(String, nullable=True)
    payload = Column(JSONB, default=dict)
    status = Column(String, default="ok", index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True, nullable=False)

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
