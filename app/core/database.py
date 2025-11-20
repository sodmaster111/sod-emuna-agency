"""Async SQLAlchemy database utilities and models."""
from __future__ import annotations

import os
from datetime import datetime
from typing import AsyncGenerator, List

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlmodel import SQLModel

from app.core.config import get_settings


class DummyResult:
    """Minimal result set used when database access is disabled."""

    def scalars(self) -> "DummyScalarResult":
        return DummyScalarResult()


class DummyScalarResult:
    def all(self) -> List[object]:
        return []


class DummyAsyncSession:
    """No-op async session to satisfy dependency overrides during tests."""

    async def execute(self, *_args, **_kwargs) -> DummyResult:
        return DummyResult()

    async def commit(self) -> None:  # pragma: no cover - no-op
        return None

    def add(self, *_args, **_kwargs) -> None:  # pragma: no cover - no-op
        return None

    async def __aenter__(self) -> "DummyAsyncSession":
        return self

    async def __aexit__(self, *_args) -> None:  # pragma: no cover - no-op
        return None


class Base(DeclarativeBase):
    """Declarative base for ORM models."""


class Logs(Base):
    """Persistent record of council deliberations."""

    __tablename__ = "logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    agent: Mapped[str] = mapped_column(String(128), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)


DISABLE_DATABASE = os.getenv("DISABLE_DATABASE", "").lower() in {"1", "true", "yes"}

if not DISABLE_DATABASE:
    _settings = get_settings()
    engine = create_async_engine(_settings.database_url, echo=False, future=True)
    SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
else:  # pragma: no cover - only exercised in constrained test environments
    engine = None
    SessionLocal = None


async def init_db() -> None:
    """Create database tables on startup."""
    if DISABLE_DATABASE:
        return

    # Import SQLModel tables for metadata registration
    from app.models.agent import Agent  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session for FastAPI dependencies."""
    if DISABLE_DATABASE:
        session = DummyAsyncSession()
        async with session:
            yield session
    else:
        async with SessionLocal() as session:
            yield session


async def log_entry(session: AsyncSession, agent: str, message: str) -> None:
    """Persist a chat log entry to the database."""

    if DISABLE_DATABASE:
        return

    entry = Logs(agent=agent, message=message)
    session.add(entry)
    await session.commit()


__all__ = ["Base", "Logs", "engine", "SessionLocal", "init_db", "get_async_session", "log_entry"]
