from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import Base, engine
from app.core.logging import configure_logging
from app.core.middleware import RequestContextLogMiddleware
from app.db import models


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


configure_logging()

app = FastAPI(
    title="SOD Autonomous Corporation API",
    version="1.0.0",
    description="Digital Sanhedrin - 158 AI Agents for Algorithmic Evangelism",
    lifespan=lifespan,
)

app.add_middleware(RequestContextLogMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://sodmaster.online",
        "http://sodmaster.online",
        "https://api.sodmaster.online",
        "http://api.sodmaster.online",
        "http://localhost:3000",
        "http://212.47.64.39",
        "http://212.47.64.39:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api.routes import amac, finance  # noqa: E402
from app.api.v1 import admin, agents, health, logs  # noqa: E402

app.include_router(health.router, tags=["Health"])
app.include_router(logs.router, prefix="/api/v1", tags=["Logs"])
app.include_router(agents.router, prefix="/api/v1", tags=["Agents"])
app.include_router(admin.router, prefix="/api/v1", tags=["Admin"])
app.include_router(amac.router)
app.include_router(finance.router)


@app.get("/")
async def root_health():
    return {"status": "ok"}
