"""Service layer for executing mission instances and scheduling."""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, Optional

import httpx

from app.agents.orchestrator import MissionTask, MissionType, run_mission
from app.core.config import settings
from app.core.halachic_time import get_halachic_service
from app.core.database import AsyncSessionLocal
from app.db.models import persist_pinkas_entry
from app.models.missions import MissionInstance, MissionTemplate

logger = logging.getLogger(__name__)


def is_shabbat_or_yom_tov(now: datetime) -> bool:
    """Delegate to the central halachic time service."""

    service = get_halachic_service()
    return service.is_shabbat_or_yom_tov(now)


async def fetch_random_content(
    session, content_category_slug: Optional[str]
) -> Dict[str, Any]:
    """Fetch a content item matching the requested category.

    This currently uses a placeholder selection. Integrate with the content library
    (SOD-KB-001) to pull real items when available.
    """

    if not content_category_slug:
        return {
            "title": "Daily Emuna Broadcast",
            "body_he": "Placeholder content. Connect to SOD-KB-001 for real sources.",
        }

    # Attempt to sample a content item once the content library is available.
    # For now, a stub response is returned.
    return {
        "title": f"Content from {content_category_slug}",
        "body_he": "Sample content body pending library integration.",
    }


async def send_telegram_message(channel: str, text: str) -> dict:
    """Dispatch a message to the Telegram gateway service."""

    gateway_url = settings.telegram_gateway_url
    payload = {"chat_channel": channel, "text": text}

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(gateway_url, json=payload)
        response.raise_for_status()
        return response.json()


async def _log_mission_pinkas(
    *,
    template: MissionTemplate,
    instance: MissionInstance,
    status: str,
    payload: Optional[dict] = None,
) -> None:
    """Write a mission execution entry to Pinkas."""

    persist_pinkas_entry(
        agent_name="MissionEngine",
        action=f"broadcast:{template.slug}",
        payload=payload or {
            "instance_id": instance.id,
            "template_slug": template.slug,
            "target_channel": template.target_channel,
        },
        status=status,
    )


async def execute_mission_instance(instance_id: int) -> Dict[str, Any]:
    """Execute a mission instance and persist its lifecycle."""

    logger.info("Executing mission instance", extra={"instance_id": instance_id})
    async with AsyncSessionLocal() as session:
        instance = await session.get(MissionInstance, instance_id)
        if not instance:
            logger.error("Mission instance not found", extra={"instance_id": instance_id})
            return {"status": "missing", "detail": "Mission instance not found"}

        template = await session.get(MissionTemplate, instance.template_id)
        if not template:
            instance.status = "failed"
            instance.error_message = "Template missing"
            await session.commit()
            return {"status": "failed", "detail": "Mission template missing"}

        now = datetime.utcnow()
        if is_shabbat_or_yom_tov(now):
            instance.status = "skipped"
            instance.executed_at = now
            instance.result_summary = "Skipped due to Shabbat/Yom Tov"
            await session.commit()
            await _log_mission_pinkas(template=template, instance=instance, status="skipped")
            return {"status": "skipped", "detail": instance.result_summary}

        try:
            content = await fetch_random_content(session, template.content_category_slug)
            message_text = content.get("body_he", "")
            if template.use_orchestrator:
                task = MissionTask(
                    mission_type=MissionType(template.mission_type),
                    user_id="broadcast",  # placeholder user context
                    payload={"content": content, "target_channel": template.target_channel},
                )
                orchestrated = await run_mission(task)
                message_text = orchestrated.get("summary") or message_text
            if not message_text:
                message_text = content.get("title", "Mission broadcast")

            send_result = await send_telegram_message(template.target_channel, message_text)

            instance.executed_at = datetime.utcnow()
            instance.status = "success"
            instance.result_summary = f"Delivered to {template.target_channel}"
            await session.commit()

            await _log_mission_pinkas(
                template=template,
                instance=instance,
                status="success",
                payload={
                    "instance_id": instance.id,
                    "content_preview": message_text[:200],
                    "target_channel": template.target_channel,
                    "gateway_response": send_result,
                },
            )
            return {"status": "success", "detail": instance.result_summary, "gateway_response": send_result}
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.exception("Mission execution failed", exc_info=exc)
            instance.executed_at = datetime.utcnow()
            instance.status = "failed"
            instance.error_message = str(exc)
            await session.commit()
            await _log_mission_pinkas(
                template=template,
                instance=instance,
                status="failed",
                payload={"error": str(exc), "instance_id": instance.id},
            )
            return {"status": "failed", "detail": str(exc)}


def schedule_recurring_missions() -> None:
    """Stub illustrating how recurring missions could be scheduled."""

    # This function can be invoked by Celery Beat or an APScheduler job that runs
    # every minute. The scheduler would:
    # 1. Query active MissionTemplate rows.
    # 2. Evaluate cron expressions (e.g., with `croniter`) to determine if a run is due.
    # 3. Create MissionInstance rows for due templates and enqueue `missions.execute_instance`.
    # 4. Skip creation if Shabbat/Yom Tov detection returns True.
    pass


async def _mark_failed(instance_id: int, error_message: str) -> None:
    """Best-effort update to flag a mission instance as failed."""

    async with AsyncSessionLocal() as session:
        instance = await session.get(MissionInstance, instance_id)
        if not instance:
            return
        instance.status = "failed"
        instance.error_message = error_message
        instance.executed_at = datetime.utcnow()
        await session.commit()


def execute_mission_instance_sync(instance_id: int) -> Dict[str, Any]:
    """Synchronous helper to run an async mission execution."""

    return asyncio.run(execute_mission_instance(instance_id))


__all__ = [
    "execute_mission_instance",
    "execute_mission_instance_sync",
    "schedule_recurring_missions",
]
