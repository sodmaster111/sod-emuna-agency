"""RAG indexing pipeline for Torah content and generated assets.

This module provides a small helper class, :class:`RAGPipeline`, that batches
content into the vector database via :mod:`app.services.rag_client`. The
pipeline can be invoked from ingestion flows or after LLM generation to ensure
fresh material is searchable.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.content import ContentItem
from app.services import rag_client


class RAGPipeline:
    """Lightweight helper for indexing application content into RAG storage."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def index_content_item(
        self, item: ContentItem, collection: str = "torah"
    ) -> None:
        """Index a single content item with metadata.

        The text body concatenates Hebrew/English titles and bodies to maximize
        recall. Metadata captures classification and tags for downstream
        filtering.
        """

        text_parts: List[str] = [
            value
            for value in [item.title_he or item.title_en, item.body_he, item.body_en]
            if value
        ]
        text = "\n\n".join(text_parts)

        metadata = {
            "category_slug": getattr(item.category, "slug", None),
            "source_ref": item.source,
            "tags": item.tags or [],
        }

        await rag_client.add_documents(
            collection,
            [
                {
                    "id": str(item.id),
                    "text": text,
                    "meta": metadata,
                }
            ],
        )

        item.indexed_at = datetime.now(timezone.utc)
        await self.session.commit()

    async def index_batch(self, limit: int = 100, collection: str = "torah") -> int:
        """Index a batch of unindexed content items.

        Items are fetched in ascending creation order to respect ingestion
        sequence. Chunked writes avoid oversized embedding batches.
        Returns the number of items indexed.
        """

        stmt = (
            select(ContentItem)
            .options(joinedload(ContentItem.category))
            .where(ContentItem.indexed_at.is_(None), ContentItem.is_active.is_(True))
            .order_by(ContentItem.created_at)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        items = result.scalars().all()

        if not items:
            return 0

        now = datetime.now(timezone.utc)
        chunk_size = 25
        total_indexed = 0

        for start in range(0, len(items), chunk_size):
            batch: Sequence[ContentItem] = items[start : start + chunk_size]
            documents = [self._build_doc(item) for item in batch]
            await rag_client.add_documents(collection, documents)

            for item in batch:
                item.indexed_at = now
                total_indexed += 1

        await self.session.commit()
        return total_indexed

    def _build_doc(self, item: ContentItem) -> dict:
        """Internal helper to construct a payload for the vector DB."""

        text_parts = [
            value
            for value in [item.title_he or item.title_en, item.body_he, item.body_en]
            if value
        ]

        return {
            "id": str(item.id),
            "text": "\n\n".join(text_parts),
            "meta": {
                "category_slug": getattr(item.category, "slug", None),
                "source_ref": item.source,
                "tags": item.tags or [],
            },
        }


# Example: trigger indexing after ingestion/generation flows
# async def handle_new_content(session: AsyncSession, item: ContentItem):
#     pipeline = RAGPipeline(session)
#     await pipeline.index_content_item(item)


# Optional docker-compose snippet for Qdrant and Ollama dependencies:
#
# services:
#   qdrant:
#     image: qdrant/qdrant:latest
#     ports:
#       - "6333:6333"
#   ollama:
#     image: ollama/ollama:latest
#     environment:
#       - OLLAMA_HOST=0.0.0.0
#     ports:
#       - "11434:11434"


__all__ = ["RAGPipeline"]
