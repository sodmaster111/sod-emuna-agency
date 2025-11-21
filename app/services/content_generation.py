"""Generate daily Torah content variants and persist them."""
from __future__ import annotations

import asyncio
from typing import Optional

from sqlalchemy import func, select

from app.core.database import AsyncSessionLocal
from app.models.content import ContentCategory, ContentItem
from app.models.generated_content import GeneratedContent


async def translate(text: str, lang: str) -> str:
    """Stub translation helper; integrate orchestrator or external API later."""

    return text


class DailyContentGenerator:
    """Service for generating and storing daily content variations."""

    def __init__(self, session_factory=AsyncSessionLocal):
        self.session_factory = session_factory

    async def _fetch_random_source(
        self, session, category_slug: str
    ) -> Optional[ContentItem]:
        query = (
            select(ContentItem)
            .join(ContentCategory)
            .where(ContentCategory.slug == category_slug, ContentItem.is_active.is_(True))
            .order_by(func.random())
            .limit(1)
        )
        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def generate_one(self, category_slug: str) -> GeneratedContent:
        """Create and persist a generated content entry for the given category."""

        async with self.session_factory() as session:
            source_item = await self._fetch_random_source(session, category_slug)
            if not source_item:
                raise ValueError(f"No active content found for category '{category_slug}'")

            raw_text = source_item.body_he
            generated_he = raw_text
            generated_ru = await translate(raw_text, "ru")
            generated_en = await translate(raw_text, "en")

            generated_entry = GeneratedContent(
                source_id=source_item.id,
                raw_source_text=raw_text,
                generated_he=generated_he,
                generated_ru=generated_ru,
                generated_en=generated_en,
                tags=list(source_item.tags or []),
            )
            session.add(generated_entry)
            await session.commit()
            await session.refresh(generated_entry)
            return generated_entry


if __name__ == "__main__":
    generator = DailyContentGenerator()
    asyncio.run(generator.generate_one("tehillim"))
