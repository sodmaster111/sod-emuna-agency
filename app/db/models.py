from datetime import datetime
from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base


class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    role = Column(String, nullable=False)
    dna_prompt = Column(Text, nullable=False)
    tools = Column(JSONB, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

    tasks = relationship("AgentTask", back_populates="agent", cascade="all, delete-orphan")
    logs = relationship("AgentLog", back_populates="agent", cascade="all, delete-orphan")


class AgentTask(Base):
    __tablename__ = "agent_tasks"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String, default="queued", index=True)
    result = Column(JSONB)
    requires_cro_validation = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

    agent = relationship("Agent", back_populates="tasks")


class AgentLog(Base):
    __tablename__ = "agent_logs"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id", ondelete="SET NULL"))
    agent_name = Column(String, index=True)
    action = Column(String)
    input_data = Column(JSONB)
    output_data = Column(JSONB)
    embedding = Column(Vector(384), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    status = Column(String)

    agent = relationship("Agent", back_populates="logs")

    def as_dict(self) -> dict:
        return {
            "id": self.id,
            "agent": self.agent_name,
            "action": self.action,
            "status": self.status,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }
