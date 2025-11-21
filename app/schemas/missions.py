"""Schemas for mission templates and execution instances."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class MissionTemplateBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    slug: str
    name: str
    description: Optional[str] = None
    is_active: bool = True
    mission_type: str
    content_category_slug: Optional[str] = None
    target_channel: str
    cron_expr: str
    use_orchestrator: bool = False


class MissionTemplateCreate(MissionTemplateBase):
    """Input schema for creating a mission template."""

    pass


class MissionTemplateRead(MissionTemplateBase):
    """Read-only representation of a mission template."""

    id: int


class MissionInstanceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    template_id: int
    scheduled_for: datetime
    executed_at: Optional[datetime] = None
    status: str
    result_summary: Optional[str] = None
    error_message: Optional[str] = None
    task_id: Optional[str] = None


class MissionRunRequest(BaseModel):
    """Request payload to trigger a mission run for a given template."""

    template_slug: str
