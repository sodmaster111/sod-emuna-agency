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
from app.core.resource_monitor import get_system_health

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
        latest_plan = await run_autonomous_cycle()
        await asyncio.sleep(engine.loop_interval)

async def check_redis() -> Dict[str, Any]:
    """Confirm Redis is reachable and responsive."""

async def run_autonomous_cycle() -> List[str]:
    """Run one autonomous Sanhedrin planning cycle."""

    global latest_plan
    council = SanhedrinCouncil(engine=engine)
    latest_plan = await asyncio.to_thread(
        council.convene,
        "Devise the next operational steps for the Digital Sanhedrin",
    )
    logger.info("Latest council plan: %s", latest_plan)
    return latest_plan


def run_autonomous_cycle_sync() -> List[str]:
    """Synchronously run the autonomous cycle for task schedulers."""

    return asyncio.run(run_autonomous_cycle())


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


def _health_payload() -> dict[str, object]:
    return {
        "status": "online",
        "ollama_base_url": engine.ollama_base_url,
        "database_url": memory_manager.database_url,
        "redis_url": memory_manager.redis_url,
        "qdrant_url": memory_manager.qdrant_url,
        "latest_plan": latest_plan,
        "system_health": get_system_health(),
    }


@app.get("/")
async def healthcheck() -> dict[str, object]:
    """Basic status endpoint for Coolify health checks."""

    return _health_payload()


@app.get("/health")
async def extended_healthcheck() -> dict[str, object]:
    """Extended health endpoint for Docker health checks."""

    return _health_payload()
