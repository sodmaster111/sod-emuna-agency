"""Health and readiness probes."""
from __future__ import annotations

from celery import Celery
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_celery_app, get_db_session
from app.models.pinkas import Pinkas

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health() -> dict[str, str]:
    """Lightweight liveness probe."""

    return {"status": "ok"}


@router.get("/deep")
async def deep_health(
    db: AsyncSession = Depends(get_db_session),
    celery_app: Celery = Depends(get_celery_app),
) -> dict[str, str]:
    """Check database connectivity and Celery reachability."""

    db_status = "ok"
    celery_status = "ok"

    try:
        await db.execute(select(Pinkas.id).limit(1))
    except Exception:  # pragma: no cover - depends on external services
        db_status = "error"

    try:
        inspector = celery_app.control.inspect()
        ping = inspector.ping() if inspector else None
        if not ping:
            celery_status = "error"
    except Exception:  # pragma: no cover - depends on external services
        celery_status = "error"

    return {"status": "ok", "db": db_status, "celery": celery_status}
