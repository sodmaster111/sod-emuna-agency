from fastapi import APIRouter

from app.agents.registry import AGENT_REGISTRY

router = APIRouter()


@router.get("/admin/agents")
async def admin_agent_dashboard():
    return {
        "total": len(AGENT_REGISTRY),
        "active": [
            {
                "name": agent["name"],
                "role": agent["role"],
                "department": agent["department"],
                "tools": agent["tools"],
            }
            for agent in AGENT_REGISTRY.values()
        ],
    }
