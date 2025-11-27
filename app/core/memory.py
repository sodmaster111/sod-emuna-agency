"""Shared memory connectors for persistence layers."""
from __future__ import annotations

import os
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine


def _normalize_database_url(database_url: str) -> str:
    if not database_url:
        raise RuntimeError("DATABASE_URL is not set")

    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql+asyncpg://", 1)

    if database_url.startswith("postgresql://") and "+asyncpg" not in database_url:
        return database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    return database_url


class MemoryManager:
    """Lazy connectors for Postgres and vector memory services."""

    def __init__(self) -> None:
        raw_database_url = os.getenv(
            "DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"
        )
        self.database_url = _normalize_database_url(raw_database_url)
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        self._sql_engine: Optional[AsyncEngine] = None

    @property
    def sql_engine(self) -> AsyncEngine:
        """Lazily create the SQLAlchemy engine for Postgres access."""

        if self._sql_engine is None:
            self._sql_engine = create_async_engine(self.database_url, pool_pre_ping=True)
        return self._sql_engine

    def describe(self) -> dict[str, str]:
        """Expose connection metadata for diagnostics."""

        return {
            "database_url": self.database_url,
            "redis_url": self.redis_url,
            "qdrant_url": self.qdrant_url,
        }
