"""Celery task to ingest Torah texts into the vector store."""
from __future__ import annotations

import asyncio
from typing import Any, Dict, List

from celery import Celery

from app.core.config import config
from app.rag.sefaria_client import SefariaClient
from app.rag.vector_store import (
    chunk_passages,
    embed_texts,
    ensure_vector_tables,
    store_chunks,
)

celery_app = Celery(
    "sod_celery",
    broker=config.redis_url,
    backend=config.redis_url,
)


def _extract_passages(payload: Dict[str, Any], language: str) -> List[str]:
    if language.startswith("he"):
        candidates = payload.get("he", [])
    else:
        candidates = payload.get("text", [])
    return [p.strip() for p in candidates if isinstance(p, str) and p.strip()]


def _book_from_payload(payload: Dict[str, Any], fallback: str) -> str:
    return payload.get("book") or fallback


async def _ingest_text(reference: str, language: str) -> Dict[str, Any]:
    ensure_vector_tables()
    async with SefariaClient() as client:
        payload = await client.fetch_text(reference, language=language)
    passages = _extract_passages(payload, language)
    if not passages:
        return {"status": "error", "message": "No passages returned from Sefaria"}

    chunks = chunk_passages(passages)
    embeddings = await asyncio.to_thread(embed_texts, chunks)
    book = _book_from_payload(payload, reference)
    inserted = store_chunks(reference, book, chunks, embeddings)
    return {"status": "completed", "reference": reference, "inserted": inserted}


@celery_app.task(name="app.tasks.ingest_torah.ingest_torah_text")
def ingest_torah_text(reference: str = "Pirkei Avot", language: str = "en") -> Dict[str, Any]:
    """Fetch a Torah text from Sefaria and index it in the vector store."""

    return asyncio.run(_ingest_text(reference, language))


__all__ = ["ingest_torah_text", "celery_app"]
