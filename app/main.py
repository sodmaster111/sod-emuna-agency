"""FastAPI entrypoint for the SOD autonomous core."""
from __future__ import annotations

import asyncio
import logging
from typing import List, Optional

from fastapi import Depends, FastAPI
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents import SanhedrinCouncil
from app.core.config import get_settings
from app.core.database import Logs, get_async_session, init_db
from app.core.engine import Engine
from app.core.memory import MemoryManager
from app.models import LogEntry, MissionRequest, StatusReport
from app.tools.ton_wallet import TonWalletTool

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="SOD Autonomous Core", version="1.0.0")

engine = Engine()
settings = get_settings()
memory_manager = MemoryManager()
ton_wallet = TonWalletTool()
loop_task: Optional[asyncio.Task] = None
latest_plan: List[str] = []
mission_goal: str = settings.mission_goal


async def _autonomous_loop() -> None:
    """Run the endless strategic loop in the background."""

    global latest_plan
    while True:
        council = SanhedrinCouncil(engine=engine)
        latest_plan = await asyncio.to_thread(
            council.convene,
            mission_goal,
        )
        logger.info("Latest council plan: %s", latest_plan)
        await asyncio.sleep(engine.loop_interval)


@app.on_event("startup")
async def _on_startup() -> None:
    global loop_task
    logger.info("Booting SOD Autonomous Core with Ollama at %s", engine.ollama_base_url)
    logger.info("Memory backends: %s", memory_manager.describe())
    await init_db()
    loop_task = asyncio.create_task(_autonomous_loop())


@app.on_event("shutdown")
async def _on_shutdown() -> None:
    if loop_task:
        loop_task.cancel()
        try:
            await loop_task
        except asyncio.CancelledError:
            logger.info("Autonomous loop stopped.")


@app.get("/")
async def healthcheck() -> dict[str, object]:
    """Basic status endpoint for Coolify health checks."""

    return {
        "status": "online",
        "ollama_base_url": engine.ollama_base_url,
        "database_url": memory_manager.database_url,
        "redis_url": memory_manager.redis_url,
        "qdrant_url": memory_manager.qdrant_url,
        "latest_plan": latest_plan,
    }


@app.post("/api/v1/mission", response_model=MissionRequest)
async def start_mission(payload: MissionRequest) -> MissionRequest:
    """Launch or resume the Sanhedrin strategic loop."""

    global loop_task, mission_goal

    mission_goal = payload.goal or settings.mission_goal

    if loop_task and not loop_task.done():
        return MissionRequest(goal=mission_goal, status="running")

    loop_task = asyncio.create_task(_autonomous_loop())
    return MissionRequest(goal=mission_goal, status="started")


@app.get("/api/v1/logs", response_model=list[LogEntry])
async def get_logs(session: AsyncSession = Depends(get_async_session)) -> list[LogEntry]:
    """Return the 50 most recent log entries ordered newest-first."""

    result = await session.execute(select(Logs).order_by(desc(Logs.timestamp)).limit(50))
    entries = result.scalars().all()

    try:
        return [LogEntry.model_validate(entry) for entry in entries]
    except AttributeError:  # pragma: no cover - pydantic v1 fallback
        return [LogEntry.from_orm(entry) for entry in entries]


@app.get("/api/v1/status", response_model=StatusReport)
async def status() -> StatusReport:
    """Report backend health and the configured TON balance."""

    ton_balance = ton_wallet.get_balance(address=settings.ton_wallet_address)
    return StatusReport(health="ok", ton_balance=ton_balance)
