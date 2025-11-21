#!/usr/bin/env python3
"""Ingest Sefaria JSON exports into the Content library.

Example:
    python scripts/ingest_sefaria.py --db-url postgresql+asyncpg://user:pass@localhost:5432/dbname \
        --file ./data/sefaria_tehillim.json --category-slug tehillim --rag-collection torah
"""
from __future__ import annotations

import argparse
import asyncio
import importlib.util
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Ensure the repository root is on the Python path when running as a script.
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.models.content import ContentCategory, ContentItem  # noqa: E402

rag_client_spec = importlib.util.find_spec("app.services.rag_client")
rag_client = None
if rag_client_spec:
    from app.services import rag_client  # type: ignore  # noqa: E402

DEFAULT_DB_ENV_VAR = "CONTENT_DATABASE_URL"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest Sefaria JSON exports into the Content library.")
    parser.add_argument(
        "--db-url",
        dest="db_url",
        help="Async database URL (e.g. postgresql+asyncpg://user:pass@host:5432/db). "
        f"Defaults to ${DEFAULT_DB_ENV_VAR} if unset.",
    )
    parser.add_argument("--file", required=True, help="Path to the Sefaria JSON export.")
    parser.add_argument("--category-slug", required=True, help="Slug of the ContentCategory to attach items to.")
    parser.add_argument(
        "--rag-collection",
        dest="rag_collection",
        help="Optional RAG collection name to index newly ingested documents.",
    )
    return parser.parse_args()


def resolve_db_url(cli_value: Optional[str]) -> str:
    db_url = cli_value or os.getenv(DEFAULT_DB_ENV_VAR) or os.getenv("DATABASE_URL")
    if not db_url:
        raise SystemExit(
            "Database URL not provided. Supply --db-url or set CONTENT_DATABASE_URL/DATABASE_URL in the environment."
        )
    return db_url


def load_sefaria_payload(path: str | Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def normalize_text(value: Any) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, str):
        cleaned = value.strip()
        return cleaned if cleaned else None
    return str(value)


def iter_sefaria_segments(payload: Dict[str, Any]) -> Iterable[Dict[str, Any]]:
    """Yield verse-level segments from a Sefaria export.

    The function expects keys like "he" (Hebrew) and "text" (English) that contain
    chapter/verse nested lists. It gracefully skips missing or malformed entries.
    """

    book_name_en = payload.get("book") or payload.get("title") or payload.get("ref") or "Sefaria"
    book_name_he = payload.get("heTitle") or payload.get("he_ref")

    hebrew_chapters = payload.get("he") or []
    english_chapters = payload.get("text") or payload.get("en") or []

    for chapter_idx, he_chapter in enumerate(hebrew_chapters, start=1):
        if not isinstance(he_chapter, list):
            continue
        en_chapter = english_chapters[chapter_idx - 1] if chapter_idx - 1 < len(english_chapters) else None

        for verse_idx, he_verse in enumerate(he_chapter, start=1):
            he_text = normalize_text(he_verse)
            if not he_text:
                continue

            en_text = None
            if isinstance(en_chapter, list) and verse_idx - 1 < len(en_chapter):
                en_text = normalize_text(en_chapter[verse_idx - 1])

            ref_base = payload.get("ref") or book_name_en
            english_ref = f"{book_name_en} {chapter_idx}:{verse_idx}" if book_name_en else ref_base
            hebrew_ref = f"{book_name_he} {chapter_idx}:{verse_idx}" if book_name_he else None
            source_ref = f"{ref_base} {chapter_idx}:{verse_idx}"

            tags: List[str] = []
            if book_name_en:
                tags.append(str(book_name_en))
            if book_name_he:
                tags.append(str(book_name_he))
            tags.extend([f"chapter:{chapter_idx}", f"verse:{verse_idx}"])

            metadata = {
                "book": book_name_en or book_name_he,
                "book_he": book_name_he,
                "chapter": chapter_idx,
                "verse": verse_idx,
                "source_ref": source_ref,
            }

            yield {
                "title_he": hebrew_ref or english_ref,
                "title_en": english_ref,
                "body_he": he_text,
                "body_en": en_text,
                "tags": tags,
                "source": source_ref,
                "metadata": metadata,
            }


async def get_or_create_category(session: AsyncSession, slug: str) -> ContentCategory:
    result = await session.execute(select(ContentCategory).where(ContentCategory.slug == slug))
    category = result.scalar_one_or_none()
    if category:
        return category

    category = ContentCategory(slug=slug, name_he=slug, name_en=slug)
    session.add(category)
    await session.commit()
    await session.refresh(category)
    return category


async def ingest_segments(
    session: AsyncSession,
    category: ContentCategory,
    segments: Iterable[Dict[str, Any]],
    rag_collection: Optional[str] = None,
) -> int:
    rag_docs: List[Dict[str, Any]] = []
    count = 0

    for segment in segments:
        item = ContentItem(
            category_id=category.id,
            title_he=segment.get("title_he"),
            title_en=segment.get("title_en"),
            body_he=segment["body_he"],
            body_en=segment.get("body_en"),
            source=segment.get("source"),
            tags=list(segment.get("tags", [])),
            metadata=dict(segment.get("metadata", {})),
        )
        session.add(item)
        count += 1

        if rag_collection:
            body_components = [segment["body_he"]]
            if segment.get("body_en"):
                body_components.append(segment["body_en"])
            rag_docs.append(
                {
                    "id": segment.get("source") or segment.get("title_en"),
                    "text": "\n\n".join(body_components),
                    "meta": {
                        "category_slug": category.slug,
                        "tags": list(segment.get("tags", [])),
                        **segment.get("metadata", {}),
                    },
                }
            )

    await session.commit()

    if rag_collection and rag_docs:
        if rag_client:
            await rag_client.add_documents(rag_collection, rag_docs)
        else:
            # TODO: Integrate actual RAG client when available.
            print(f"RAG client not available. Skipping indexing for collection '{rag_collection}'.")

    return count


async def main() -> None:
    args = parse_args()
    db_url = resolve_db_url(args.db_url)

    engine = create_async_engine(db_url, future=True, echo=False)
    SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

    payload = load_sefaria_payload(args.file)
    segments = iter_sefaria_segments(payload)

    async with SessionLocal() as session:
        category = await get_or_create_category(session, args.category_slug)
        count = await ingest_segments(session, category, segments, rag_collection=args.rag_collection)

    await engine.dispose()

    print(f"Ingested {count} segments into category '{args.category_slug}'.")
    if args.rag_collection:
        print(f"RAG collection: {args.rag_collection}")


if __name__ == "__main__":
    asyncio.run(main())
