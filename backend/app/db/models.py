from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import JSON, Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY

from app.core.database import Base


class AgentLog(Base):
    __tablename__ = "agent_logs"

    id = Column(Integer, primary_key=True, index=True)
    agent_name = Column(String(100), index=True, nullable=False)
    agent_role = Column(String(50), index=True)
    action = Column(String(200), nullable=False)
    input_data = Column(JSON)
    output_data = Column(JSON)
    embedding = Column(Vector(384))
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    status = Column(String(50), default="success")
    error_message = Column(Text, nullable=True)


class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    role = Column(String(50), nullable=False)
    department = Column(String(50), nullable=False)
    dna_prompt = Column(Text, nullable=False)
    tools = Column(ARRAY(String), default=[])
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    agent_name = Column(String(100), index=True)
    task_type = Column(String(50))
    description = Column(Text)
    status = Column(String(50), default="pending")
    result = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
