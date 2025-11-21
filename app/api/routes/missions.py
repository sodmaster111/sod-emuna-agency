"""Mission management endpoints for templates and runs."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_celery_app, get_db_session
from app.models.missions import MissionInstance, MissionTemplate
from app.schemas.missions import (
    MissionInstanceRead,
    MissionRunRequest,
    MissionTemplateRead,
)

router = APIRouter(prefix="/missions", tags=["missions"])


@router.get("/templates", response_model=List[MissionTemplateRead])
async def list_mission_templates(
    *,
    db: AsyncSession = Depends(get_db_session),
    is_active: Optional[bool] = Query(default=None),
) -> List[MissionTemplate]:
    """Return available mission templates with optional activation filtering."""

    stmt = select(MissionTemplate)
    if is_active is not None:
        stmt = stmt.where(MissionTemplate.is_active == is_active)
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.post("/run-once", response_model=MissionInstanceRead)
async def run_mission_once(
    *,
    db: AsyncSession = Depends(get_db_session),
    celery_app = Depends(get_celery_app),
    payload: MissionRunRequest,
) -> MissionInstance:
    """Trigger a single execution of an active mission template."""

    stmt = select(MissionTemplate).where(
        MissionTemplate.slug == payload.template_slug, MissionTemplate.is_active.is_(True)
    )
    result = await db.execute(stmt)
    template = result.scalar_one_or_none()
    if not template:
        raise HTTPException(status_code=404, detail="Mission template not found or inactive")

    instance = MissionInstance(
        template_id=template.id,
        scheduled_for=datetime.utcnow(),
        status="pending",
    )
    db.add(instance)
    await db.commit()
    await db.refresh(instance)

    async_result = celery_app.send_task("missions.execute_instance", args=[instance.id])
    instance.task_id = async_result.id
    await db.commit()
    await db.refresh(instance)
    return instance


@router.get("/instances", response_model=List[MissionInstanceRead])
async def list_instances(
    *,
    db: AsyncSession = Depends(get_db_session),
    template_slug: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    limit: int = 50,
    offset: int = 0,
) -> List[MissionInstance]:
    """Return mission instances with optional filters."""

    stmt = select(MissionInstance).order_by(MissionInstance.id.desc()).limit(limit).offset(offset)
    if template_slug:
        stmt = stmt.join(MissionTemplate).where(MissionTemplate.slug == template_slug)
    if status:
        stmt = stmt.where(MissionInstance.status == status)

    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.get("/instances/{instance_id}", response_model=MissionInstanceRead)
async def get_instance(
    *,
    db: AsyncSession = Depends(get_db_session),
    instance_id: int,
) -> MissionInstance:
    """Return a specific mission instance by id."""

    instance = await db.get(MissionInstance, instance_id)
    if not instance:
        raise HTTPException(status_code=404, detail="Mission instance not found")
    return instance
