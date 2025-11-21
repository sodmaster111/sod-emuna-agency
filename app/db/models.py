"""Database models for persistent agent records (Pinkas / Logbook)."""
from __future__ import annotations

from datetime import datetime, timezone
import logging
from functools import lru_cache
from typing import Optional

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from app.core.config import get_settings


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


logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _get_engine(database_url: Optional[str] = None):
    """Create (and cache) a synchronous engine for Pinkas persistence."""

    settings = get_settings()
    return create_engine(database_url or settings.database_url, future=True)


def persist_pinkas_entry(
    *, agent_name: str, thought: str, action: str | None = None, database_url: Optional[str] = None
) -> None:
    """Persist trace data locally when Langfuse is unavailable."""

    try:
        engine = _get_engine(database_url)
        Base.metadata.create_all(engine, checkfirst=True)
        factory = sessionmaker(bind=engine, class_=Session)
        with factory() as session:
            session.add(Pinkas(agent_name=agent_name, thought=thought, action=action))
            session.commit()
    except Exception as exc:  # pragma: no cover - operational resilience
        logger.warning("Failed to persist Pinkas log entry: %s", exc)


__all__ = ["Base", "Pinkas", "persist_pinkas_entry"]
