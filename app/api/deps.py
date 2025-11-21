"""Common FastAPI dependencies for database and task scheduling."""
from collections.abc import AsyncGenerator

from celery import Celery
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.celery_worker import celery_app


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide an async SQLAlchemy session."""

    async with AsyncSessionLocal() as session:
        yield session


def get_celery_app() -> Celery:
    """Expose the configured Celery application instance."""

    return celery_app
