from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlmodel import SQLModel

engine: AsyncEngine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI, future=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


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
