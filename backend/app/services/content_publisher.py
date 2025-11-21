"""Content publishing workflow with CPAO enforcement hooks."""
from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import ContentItem
from app.services.cpao_client import CPAOInput, cpao_client

logger = logging.getLogger(__name__)


async def publish_content_item(session: AsyncSession, content_id: UUID) -> dict:
    """Publish a content item after CPAO evaluation.

    The content is only published when CPAO returns an ``allow`` decision.
    ``review_required`` keeps the item in the queue by marking it for
    moderation, while ``veto`` blocks publication entirely.
    """

    content = await session.get(ContentItem, content_id)
    if not content:
        return {"status": "not_found", "reason": "content_missing"}

    cpao_input = CPAOInput(
        actor="content_service",
        action_type="content.publish",
        payload={
            "id": str(content_id),
            "text": content.body_he,
            "title": getattr(content, "title_he", None)
            or getattr(content, "title_en", None),
        },
    )

    judgement = await cpao_client.cpao_evaluate(cpao_input)
    logger.info(
        "CPAO decision for content %s: decision=%s risk_level=%s reasons=%s",
        content_id,
        judgement.decision,
        judgement.risk_level,
        judgement.reasons,
    )

    if judgement.decision == "veto":
        return {
            "status": "blocked",
            "reason": "cpao_veto",
            "details": judgement.reasons,
        }

    if judgement.decision == "review_required":
        content.metadata = {**(content.metadata or {}), "publication_status": "needs_review"}
        session.add(content)
        await session.commit()
        return {
            "status": "needs_review",
            "reason": "cpao_review_required",
            "details": judgement.reasons,
        }

    content.metadata = {**(content.metadata or {}), "publication_status": "published"}
    session.add(content)
    await session.commit()

    # TODO: enqueue downstream publish steps (e.g., Telegram mission dispatch).
    return {"status": "published"}
