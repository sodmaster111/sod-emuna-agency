"""Helpers for persisting generated content and enriching with translations."""
from __future__ import annotations

import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.translation import TranslationService

logger = logging.getLogger(__name__)


async def save_generated_content(
    session: AsyncSession,
    generated_content: Any,
    *,
    translation_service: TranslationService | None = None,
) -> Any:
    """Persist generated content then enrich it with translations."""

    session.add(generated_content)
    await session.commit()
    await session.refresh(generated_content)

    await _translate_generated_content(session, generated_content, translation_service)
    return generated_content


async def _translate_generated_content(
    session: AsyncSession,
    generated_content: Any,
    translation_service: TranslationService | None = None,
) -> None:
    service = translation_service or TranslationService()

    source_text = getattr(generated_content, "body_he", None)
    if not source_text:
        logger.debug("Generated content %s has no Hebrew body to translate", getattr(generated_content, "id", None))
        return

    logger.info(
        "Translating generated content %s to English and Russian",
        getattr(generated_content, "id", None),
    )

    generated_content.body_en = await service.translate_he_to_en(source_text)
    generated_content.body_ru = await service.translate_he_to_ru(source_text)

    session.add(generated_content)
    await session.commit()
    await session.refresh(generated_content)

    logger.debug(
        "Completed translation for generated content %s",
        getattr(generated_content, "id", None),
    )
