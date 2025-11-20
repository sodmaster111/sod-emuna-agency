"""Shared memory connectors for persistence layers."""
from __future__ import annotations

import os
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine as SyncEngine


class MemoryManager:
    """Lazy connectors for Postgres and vector memory services."""

    def __init__(self) -> None:
        self.database_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/postgres")
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        self._sql_engine: Optional[SyncEngine] = None

    @property
    def sql_engine(self) -> SyncEngine:
        """Lazily create the SQLAlchemy engine for Postgres access."""

        if self._sql_engine is None:
            self._sql_engine = create_engine(self.database_url, pool_pre_ping=True)
        return self._sql_engine

    def describe(self) -> dict[str, str]:
        """Expose connection metadata for diagnostics."""

        return {
            "database_url": self.database_url,
            "redis_url": self.redis_url,
            "qdrant_url": self.qdrant_url,
        }
