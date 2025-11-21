from fastapi import APIRouter
from redis.asyncio import Redis
from sqlalchemy import text

from app.core.config import settings
from app.core.database import AsyncSessionLocal

router = APIRouter()


@router.get("/health")
async def health_check():
    return {"status": "ok"}


@router.get("/health/deep")
async def deep_health_check():
    db_status = "ok"
    redis_status = "ok"

    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
    except Exception:  # noqa: BLE001 - keep response simple for health checks
        db_status = "failed"

    try:
        redis = Redis.from_url(settings.REDIS_URL)
        await redis.ping()
        await redis.close()
    except Exception:  # noqa: BLE001 - keep response simple for health checks
        redis_status = "failed"

    status = "ok" if db_status == "ok" and redis_status == "ok" else "failed"
    return {"status": status, "db": db_status, "redis": redis_status}
