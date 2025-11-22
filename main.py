"""FastAPI entry point for the Digital Sanhedrin backend."""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.registry import AGENTS_CONFIG
from app.core.config import get_settings
from app.core.database import Logs, get_async_session, init_db
from app.core.sanhedrin import SanhedrinCouncil

app = FastAPI(title="Digital Sanhedrin Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://sodmaster.online", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

api_router = APIRouter(prefix="/api/v1")


@app.on_event("startup")
async def on_startup() -> None:
    await init_db()


@app.get("/")
async def root() -> dict[str, str]:
    """Simple liveness endpoint."""

    return {"status": "alive", "service": "SOD Corp API"}


@api_router.post("/start-meeting")
async def start_meeting(session: AsyncSession = Depends(get_async_session)) -> dict:
    """Trigger the Sanhedrin deliberation loop and return the transcript."""

    council = SanhedrinCouncil(db_session=session)
    transcript: List[str] = await council.convene()
    return {"mission_goal": council.mission_goal, "transcript": transcript}


@api_router.get("/logs")
async def get_logs(session: AsyncSession = Depends(get_async_session)) -> list[dict]:
    """Return the persisted chat history."""

    result = await session.execute(select(Logs).order_by(Logs.timestamp.desc()))
    rows = result.scalars().all()
    return [
        {
            "id": row.id,
            "timestamp": row.timestamp,
            "agent": row.agent,
            "message": row.message,
        }
        for row in rows
    ]


@api_router.get("/status")
async def status() -> dict:
    """Return basic status for active agents and mission."""

    settings = get_settings()
    return {
        "agents": list(AGENTS_CONFIG.keys()),
        "mission_goal": settings.mission_goal,
        "ollama_base_url": settings.ollama_base_url,
        "database_url": settings.database_url,
    }


app.include_router(api_router)


__all__ = ["app"]
