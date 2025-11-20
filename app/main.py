from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, List, Optional, Tuple

import asyncpg
import requests
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from app.api.v1.endpoints.agents import router as agents_router
from app.agents import SanhedrinCouncil
from app.core import config
from app.core.config import get_settings
from app.core.database import Logs, get_async_session, init_db
from app.core.engine import Engine
from app.core.memory import MemoryManager
from app.core.resource_monitor import get_system_health
from app.tools.ton_wallet import TonWalletTool


app = FastAPI(title="SOD Core Infrastructure", version="1.0.0")
app.include_router(agents_router, prefix="/api/v1")

engine = Engine()
settings = get_settings()
memory_manager = MemoryManager()
ton_wallet = TonWalletTool()
loop_task: Optional[asyncio.Task] = None
latest_plan: List[str] = []
mission_goal: str = settings.mission_goal

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await redis_client.close()


app = FastAPI(title="SOD Corporation API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health(db: AsyncSession = Depends(get_db)) -> dict[str, bool]:
    db_ok = False
    redis_ok = False

    try:
        await db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    try:
        await redis_client.ping()
        redis_ok = True
    except Exception:
        redis_ok = False

    healthy = db_ok and redis_ok
    return {"healthy": healthy, "database": db_ok, "redis": redis_ok}
