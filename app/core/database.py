from __future__ import annotations

import os

from sqlalchemy.engine.url import make_url, URL
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker


# 1. Читаем сырой URL из переменной окружения
RAW_DATABASE_URL = os.getenv("DATABASE_URL")

if not RAW_DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set")


def build_asyncpg_url(raw_url: str) -> URL:
    """
    Превращает любой postgres/postgresql URL в URL с drivername='postgresql+asyncpg'.
    Работает даже если сюда придет уже 'postgresql+psycopg2', 'postgresql', 'postgres' и т.п.
    """
    url = make_url(raw_url)

    # Нормализуем postgres -> postgresql
    if url.drivername == "postgres":
        url = url.set(drivername="postgresql")

    # Если это любой постгрес без asyncpg — насильно ставим asyncpg
    if url.drivername.startswith("postgresql") and "asyncpg" not in url.drivername:
        url = url.set(drivername="postgresql+asyncpg")

    # Если это уже asyncpg — оставляем как есть
    return url


DATABASE_URL = build_asyncpg_url(RAW_DATABASE_URL)


# 2. Создаем async engine только на основе URL с drivername='postgresql+asyncpg'
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
)


# 3. Session factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# 4. Базовый класс для моделей
Base = declarative_base()


# 5. Зависимость для FastAPI
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
