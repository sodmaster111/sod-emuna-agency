"""Database models for persistent agent records (Pinkas / Logbook)."""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Declarative base for the logbook models."""


class Pinkas(Base):
    """Logbook capturing agent thoughts and actions."""

    __tablename__ = "pinkas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    agent_name: Mapped[str] = mapped_column(String(255), nullable=False)
    thought: Mapped[str] = mapped_column(Text, nullable=False)
    action: Mapped[str] = mapped_column(Text, nullable=True)


__all__ = ["Base", "Pinkas"]
