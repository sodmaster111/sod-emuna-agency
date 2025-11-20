"""FastAPI entrypoint exposing health checks for core services."""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, Tuple

import asyncpg
import requests
from fastapi import FastAPI
from redis import asyncio as aioredis

from app.core.config import config

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="SOD Core Infrastructure", version="1.0.0")


async def check_postgres() -> Dict[str, Any]:
    """Confirm the PostgreSQL database is reachable."""

    connection = await asyncpg.connect(config.database_url)
    try:
        await connection.execute("SELECT 1")
    finally:
        await connection.close()
    return {"status": "ok"}


async def check_redis() -> Dict[str, Any]:
    """Confirm Redis is reachable and responsive."""

    client = aioredis.from_url(config.redis_url)
    try:
        pong = await client.ping()
    finally:
        await client.close()
    return {"status": "ok", "response": pong}


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
