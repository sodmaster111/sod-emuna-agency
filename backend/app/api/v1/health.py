from fastapi import APIRouter

from app.agents.registry import AGENT_REGISTRY
from app.core.config import settings

router = APIRouter()


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "agents": len(AGENT_REGISTRY),
        "ram": "48GB",
        "mission": settings.MISSION_GOAL,
        "ollama_model": settings.OLLAMA_MODEL,
    }
