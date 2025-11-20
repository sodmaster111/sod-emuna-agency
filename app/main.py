"""FastAPI entrypoint exposing health checks for core services."""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, Tuple

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

app = FastAPI(title="SOD Core Infrastructure", version="1.0.0")

engine = Engine()
settings = get_settings()
memory_manager = MemoryManager()
ton_wallet = TonWalletTool()
loop_task: Optional[asyncio.Task] = None
latest_plan: List[str] = []
mission_goal: str = settings.mission_goal

async def check_postgres() -> Dict[str, Any]:
    """Confirm the PostgreSQL database is reachable."""

    connection = await asyncpg.connect(config.database_url)
    try:
        await connection.execute("SELECT 1")
    finally:
        await connection.close()
    return {"status": "ok"}

    global latest_plan
    while True:
        council = SanhedrinCouncil(engine=engine)
        latest_plan = await asyncio.to_thread(
            council.convene,
            mission_goal,
        )
        logger.info("Latest council plan: %s", latest_plan)
        await asyncio.sleep(engine.loop_interval)

async def check_redis() -> Dict[str, Any]:
    """Confirm Redis is reachable and responsive."""

@app.on_event("startup")
async def _on_startup() -> None:
    global loop_task
    logger.info("Booting SOD Autonomous Core with Ollama at %s", engine.ollama_base_url)
    logger.info("Memory backends: %s", memory_manager.describe())
    await init_db()
    loop_task = asyncio.create_task(_autonomous_loop())


async def check_ollama() -> Dict[str, Any]:
    """Confirm Ollama (litellm proxy) responds to model listing requests."""

    url = f"{config.ollama_base_url}/models"
    response = await asyncio.to_thread(requests.get, url, timeout=5)
    response.raise_for_status()
    payload = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
    return {"status": "ok", "details": payload}


async def run_check(name: str, coro) -> Tuple[str, bool, Dict[str, Any]]:
    try:
        details = await coro()
        return name, True, details
    except Exception as exc:  # pragma: no cover - health endpoint resiliency
        logger.exception("Health check failed for %s", name)
        return name, False, {"error": str(exc)}


@app.get("/health")
async def health() -> Dict[str, Any]:
    """Check connectivity to PostgreSQL, Redis, and Ollama services."""

    checks = [
        run_check("postgres", check_postgres),
        run_check("redis", check_redis),
        run_check("ollama", check_ollama),
    ]
    results: Dict[str, Dict[str, Any]] = {}

    for name, healthy, details in await asyncio.gather(*checks):
        details["healthy"] = healthy
        results[name] = details

    overall_status = all(result["healthy"] for result in results.values()) if results else False
    return {"healthy": overall_status, "services": results}


@app.get("/")
async def root() -> Dict[str, Any]:
    """Base endpoint returning the mission goal and service URLs."""

    return {
        "mission_goal": config.mission_goal,
        "database_url": config.database_url,
        "redis_url": config.redis_url,
        "ollama_base_url": config.ollama_base_url,
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
