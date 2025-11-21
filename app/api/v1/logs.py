from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.db.models import AgentLog

router = APIRouter()


@router.get("/logs")
async def get_logs(limit: int = 100, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AgentLog).order_by(AgentLog.timestamp.desc()).limit(limit))
    logs = result.scalars().all()
    return {"logs": [log.as_dict() for log in logs]}
