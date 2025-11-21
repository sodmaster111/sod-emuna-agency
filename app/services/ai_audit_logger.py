"""Service for persisting AI reasoning audit entries."""
from __future__ import annotations

import logging
from typing import Any, Dict

from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.ai_audit import AIAuditEntry

logger = logging.getLogger(__name__)


async def log_step(
    agent_name: str,
    step_index: int,
    content: str,
    meta: Dict[str, Any] | None = None,
) -> None:
    """Persist a single reasoning step when audit mode is enabled."""

    if not settings.audit_mode:
        return

    async with AsyncSessionLocal() as session:
        entry = AIAuditEntry(
            agent_name=agent_name,
            step_index=step_index,
            content=content,
            meta=meta or {},
        )
        session.add(entry)
        try:
            await session.commit()
        except SQLAlchemyError as exc:  # pragma: no cover - defensive logging
            await session.rollback()
            logger.exception("Failed to persist AI audit entry", exc_info=exc)
