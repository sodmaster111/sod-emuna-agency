from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api import api_router
from app.api.v1 import agents, logs
from app.core.database import engine
from app.db.models import Base


ALLOWED_ORIGINS = [
    "https://sodmaster.online",
    "http://sodmaster.online",
    "http://localhost:3000",
    "http://212.47.64.39",
    "http://212.47.64.39:3000",
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="SOD Autonomous Corporation API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=r"https?://212\.47\.64\.39(?::\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
app.include_router(logs.router, prefix="/api/v1")
app.include_router(agents.router, prefix="/api/v1")
