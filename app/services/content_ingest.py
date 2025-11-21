"""Utilities for ingesting external Torah content via HTTP APIs.

This module defines a generic :class:`ExternalContentIngestor` that fetches JSON
payloads from remote endpoints, maps the payload into :class:`~app.models.content.ContentItem`
records, and inserts only new entries based on a source reference identifier.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models.content import ContentCategory, ContentItem

logger = logging.getLogger(__name__)


class ExternalContentIngestor:
    """Fetch external Torah content and persist it into ``ContentItem`` records."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def ingest_from_api(self, url: str, category_slug: str, mapping: dict) -> int:
        """Import content items from an external JSON API.

        Args:
            url: HTTP endpoint returning a JSON array of objects.
            category_slug: Slug of the ``ContentCategory`` to attach items to.
            mapping: Field mapping that identifies the text, optional title, and
                unique source reference keys within each item. Example::

                    {
                        "text": "body",
                        "title": "name",
                        "source": "id",
                    }

        Returns:
            Number of newly created ``ContentItem`` rows.
        """

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(url)
            response.raise_for_status()
            payload: Any = response.json()

        if not isinstance(payload, list):
            raise ValueError("API response must be a JSON array of items")

        category = await self._get_category_by_slug(category_slug)
        source_key = mapping["source"]
        text_key = mapping["text"]
        title_key = mapping.get("title")

        source_refs = {str(item[source_key]) for item in payload if source_key in item}
        existing_refs = await self._get_existing_source_refs(source_refs)

        created = 0
        for item in payload:
            if source_key not in item or text_key not in item:
                logger.warning("Skipping item missing required keys", extra={"item": item})
                continue

            source_ref = str(item[source_key])
            if source_ref in existing_refs:
                continue

            body_he = item[text_key]
            title = item.get(title_key) if title_key else None

            content_item = ContentItem(
                category_id=category.id,
                title_he=title,
                body_he=body_he,
                source=source_ref,
                metadata={"source_ref": source_ref, "import_url": url},
            )
            self.session.add(content_item)
            created += 1

        if created:
            await self.session.commit()

        return created

    async def _get_category_by_slug(self, slug: str) -> ContentCategory:
        result = await self.session.execute(
            select(ContentCategory).where(ContentCategory.slug == slug)
        )
        category = result.scalars().first()
        if not category:
            raise ValueError(f"ContentCategory with slug '{slug}' not found")
        return category

    async def _get_existing_source_refs(self, source_refs: set[str]) -> set[str]:
        if not source_refs:
            return set()

        result = await self.session.execute(
            select(ContentItem.source).where(ContentItem.source.in_(source_refs))
        )
        return set(result.scalars().all())


if __name__ == "__main__":
    example_mapping = {"text": "body", "title": "name", "source": "id"}

    async def run_example() -> None:
        async with AsyncSessionLocal() as session:
            ingestor = ExternalContentIngestor(session)
            count = await ingestor.ingest_from_api(
                "https://example.com/api/content", "tehillim", example_mapping
            )
            print(f"Imported {count} new content items")

    asyncio.run(run_example())
