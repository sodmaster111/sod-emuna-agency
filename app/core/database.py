from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy import JSON, DateTime, Integer, String, Text, func, text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.core.config import settings


class Base(DeclarativeBase):
    """Base class for declarative ORM models."""


class Logs(Base):
    """Persistence model for application log entries (Pinkas)."""

    __tablename__ = "logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    timestamp: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
    agent_name: Mapped[str] = mapped_column(String(length=255))
    message: Mapped[str] = mapped_column(Text())
    metadata: Mapped[dict | None] = mapped_column(JSON(), nullable=True)


def _create_engine() -> AsyncEngine:
    return create_async_engine(settings.database_url, echo=False, future=True)


engine: AsyncEngine = _create_engine()
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields an async database session."""

    async with AsyncSessionLocal() as session:
        yield session


async def init_db() -> None:
    """Initialize database tables if they do not exist."""

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


__all__ = ["Base", "Logs", "engine", "AsyncSessionLocal", "get_db", "init_db"]
