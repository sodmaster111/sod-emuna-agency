"""FastAPI application entrypoint for core services."""
from __future__ import annotations

from fastapi import APIRouter, FastAPI

from app.api import api_router
from app.api.v1 import agents, logs
from app.core.database import engine
from app.db.models import Base

app = FastAPI(title="SOD Agency Core API", version="0.1.0", lifespan=lifespan)

router = APIRouter()


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Return a simple health indicator."""

    return {"status": "online"}


@router.get("/logs")
async def list_logs() -> dict[str, str]:
    """Placeholder endpoint for logs retrieval."""

app.include_router(api_router)
app.include_router(logs.router, prefix="/api/v1")
app.include_router(agents.router, prefix="/api/v1")
