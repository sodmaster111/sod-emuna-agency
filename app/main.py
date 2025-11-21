"""FastAPI application entrypoint for core services."""
from __future__ import annotations

from fastapi import APIRouter, FastAPI

from app.db.session import lifespan

app = FastAPI(title="SOD Agency Core API", version="0.1.0", lifespan=lifespan)

router = APIRouter()


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Return a simple health indicator."""

    return {"status": "online"}


@router.get("/logs")
async def list_logs() -> dict[str, str]:
    """Placeholder endpoint for logs retrieval."""

    return {"status": "online"}


@router.post("/command")
async def execute_command() -> dict[str, str]:
    """Placeholder endpoint for agent command execution."""

    return {"status": "online"}


app.include_router(router)
