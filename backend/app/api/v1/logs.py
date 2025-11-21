from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.db.models import AgentLog

router = APIRouter()


@router.get("/logs")
async def get_agent_logs(
    limit: int = Query(100, le=1000),
    agent_name: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    query = select(AgentLog).order_by(desc(AgentLog.timestamp)).limit(limit)

    if agent_name:
        query = query.where(AgentLog.agent_name == agent_name)

    result = await db.execute(query)
    logs = result.scalars().all()

    return {
        "total": len(logs),
        "logs": [
            {
                "id": log.id,
                "agent": log.agent_name,
                "role": log.agent_role,
                "action": log.action,
                "status": log.status,
                "timestamp": log.timestamp.isoformat(),
            }
            for log in logs
        ],
    }
