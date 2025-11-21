"""API router assembly for the core service."""
from fastapi import APIRouter

from app.api.routes import commands, health, missions, pinkas

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(pinkas.router)
api_router.include_router(commands.router)
api_router.include_router(missions.router)

__all__ = ["api_router"]
