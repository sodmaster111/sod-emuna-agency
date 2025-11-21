"""Read-only access to Pinkas log entries."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session
from app.models.pinkas import Pinkas

router = APIRouter(prefix="/pinkas", tags=["pinkas"])


class PinkasEntry(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    agent: str
    thought: Optional[str] = None
    action: Optional[str] = None
    payload: Dict[str, Any] = Field(default_factory=dict)
    status: str
    timestamp: datetime


@router.get("", response_model=List[PinkasEntry])
async def list_pinkas(
    limit: int = 50,
    offset: int = 0,
    agent: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db_session),
) -> List[PinkasEntry]:
    """Return paginated Pinkas entries ordered by recency."""

    stmt = select(Pinkas).order_by(desc(Pinkas.timestamp)).limit(limit).offset(offset)
    if agent:
        stmt = stmt.where(Pinkas.agent == agent)
    if status:
        stmt = stmt.where(Pinkas.status == status)

    result = await db.execute(stmt)
    entries = result.scalars().all()
    return list(entries)


@router.get("/{entry_id}", response_model=PinkasEntry)
async def get_pinkas_entry(
    entry_id: int,
    db: AsyncSession = Depends(get_db_session),
) -> PinkasEntry:
    """Return a single Pinkas record or 404 if missing."""

    entry = await db.get(Pinkas, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Pinkas entry not found")
    return entry
