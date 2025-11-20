"""Async database engine and logging models."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.core.config import config


class Base(DeclarativeBase):
    """Base class for declarative models."""


class Logs(Base):
    """Record book (Pinkas) storing agent thoughts and actions."""

    __tablename__ = "logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    agent_role: Mapped[Optional[str]] = mapped_column(String(255))
    entry_type: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)


database_url = config.async_postgres_url
engine = create_async_engine(database_url, echo=False, future=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_session() -> AsyncSession:
    """Yield an async session for FastAPI dependency injection."""

    async with AsyncSessionLocal() as session:
        yield session


async def init_db() -> None:
    """Create database tables if they do not exist."""

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
