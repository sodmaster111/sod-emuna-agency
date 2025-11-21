"""AI audit logging model for capturing reasoning steps."""
from __future__ import annotations

from datetime import datetime
import uuid
from typing import Any, Dict

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.core.database import Base


class AIAuditEntry(Base):
    """Structured audit record for agent reasoning steps."""

    __tablename__ = "ai_audit_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_name = Column(String, index=True, nullable=False)
    step_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True, nullable=False)
    meta = Column(JSONB, default=dict)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "agent_name": self.agent_name,
            "step_index": self.step_index,
            "content": self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "meta": self.meta or {},
        }
