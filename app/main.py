"""FastAPI entrypoint for the SOD autonomous core."""
from __future__ import annotations

import asyncio
import logging
from typing import List, Optional

from fastapi import FastAPI

from app.agents import SanhedrinCouncil
from app.core.engine import Engine
from app.core.memory import MemoryManager
from app.core.resource_monitor import get_system_health

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="SOD Autonomous Core", version="1.0.0")

engine = Engine()
memory_manager = MemoryManager()
loop_task: Optional[asyncio.Task] = None
latest_plan: List[str] = []


async def _autonomous_loop() -> None:
    """Run the endless strategic loop in the background."""

    global latest_plan
    while True:
        latest_plan = await run_autonomous_cycle()
        await asyncio.sleep(engine.loop_interval)


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
    loop_task = asyncio.create_task(_autonomous_loop())


@app.on_event("shutdown")
async def _on_shutdown() -> None:
    if loop_task:
        loop_task.cancel()
        try:
            await loop_task
        except asyncio.CancelledError:
            logger.info("Autonomous loop stopped.")


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
