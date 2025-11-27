import os

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker


# 1. Read DATABASE_URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set")


# 2. Normalize to asyncpg
#    We aggressively rewrite ANY postgres-style URL to use the asyncpg driver.
if DATABASE_URL.startswith("postgres://"):
    # Heroku-style URL
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
elif DATABASE_URL.startswith("postgresql://") and "+asyncpg" not in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)


# 3. Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
)


# 4. Session factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# 5. Base model
Base = declarative_base()


# 6. Dependency for FastAPI
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
