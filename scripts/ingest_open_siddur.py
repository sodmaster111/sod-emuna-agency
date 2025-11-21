#!/usr/bin/env python3
"""Ingest Open Siddur exports into the Content library.

Example:
    python scripts/ingest_open_siddur.py --db-url postgresql+asyncpg://user:pass@localhost:5432/dbname \
        --file ./data/open_siddur_tefilot.json --category-slug prayer
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
    parser = argparse.ArgumentParser(description="Ingest Open Siddur exports into the Content library.")
    parser.add_argument(
        "--db-url",
        dest="db_url",
        help="Async database URL (e.g. postgresql+asyncpg://user:pass@host:5432/db). "
        f"Defaults to ${DEFAULT_DB_ENV_VAR} if unset.",
    )
    parser.add_argument("--file", required=True, help="Path to the Open Siddur JSON export.")
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


def load_open_siddur_payload(path: str | Path) -> Dict[str, Any] | List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def normalize_text(value: Any) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, str):
        cleaned = value.strip()
        return cleaned if cleaned else None
    return str(value)


def iter_prayers(payload: Dict[str, Any] | List[Dict[str, Any]]) -> Iterable[Dict[str, Any]]:
    """Yield prayer entries from an Open Siddur export.

    Expected JSON shapes:
    - A list of prayer objects.
    - A dict with a top-level key (e.g. "prayers" or "items") containing a list of prayers.
    Each prayer object should have a name/title and text. If XML is provided instead, convert
    it to dict form first (e.g. using xmltodict) and map prayer nodes to the same structure.
    """

    prayers: Iterable[Dict[str, Any]]
    if isinstance(payload, list):
        prayers = payload
    elif isinstance(payload, dict):
        if isinstance(payload.get("prayers"), list):
            prayers = payload["prayers"]
        elif isinstance(payload.get("items"), list):
            prayers = payload["items"]
        else:
            prayers = payload.values()
    else:
        prayers = []

    for prayer in prayers:
        if not isinstance(prayer, dict):
            continue

        name = prayer.get("title") or prayer.get("name") or prayer.get("en") or "Untitled Prayer"
        hebrew_name = prayer.get("heTitle") or prayer.get("he") or prayer.get("label_he")
        text_he = normalize_text(prayer.get("text_he") or prayer.get("he") or prayer.get("hebrew"))
        text_en = normalize_text(prayer.get("text_en") or prayer.get("en") or prayer.get("english"))
        if not text_he:
            continue

        source_ref = prayer.get("id") or prayer.get("_id") or prayer.get("source") or name

        yield {
            "title_he": hebrew_name or name,
            "title_en": name,
            "body_he": text_he,
            "body_en": text_en,
            "tags": ["prayer", "siddur"],
            "source": str(source_ref),
            "metadata": {
                "source_ref": source_ref,
                "attribution": prayer.get("attribution") or prayer.get("author"),
            },
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


async def ingest_prayers(
    session: AsyncSession,
    category: ContentCategory,
    prayers: Iterable[Dict[str, Any]],
    rag_collection: Optional[str] = None,
) -> int:
    rag_docs: List[Dict[str, Any]] = []
    count = 0

    for prayer in prayers:
        item = ContentItem(
            category_id=category.id,
            title_he=prayer.get("title_he"),
            title_en=prayer.get("title_en"),
            body_he=prayer["body_he"],
            body_en=prayer.get("body_en"),
            source=prayer.get("source"),
            tags=list(prayer.get("tags", [])),
            metadata=dict(prayer.get("metadata", {})),
        )
        session.add(item)
        count += 1

        if rag_collection:
            body_components = [prayer["body_he"]]
            if prayer.get("body_en"):
                body_components.append(prayer["body_en"])
            rag_docs.append(
                {
                    "id": prayer.get("source") or prayer.get("title_en"),
                    "text": "\n\n".join(body_components),
                    "meta": {
                        "category_slug": category.slug,
                        "tags": list(prayer.get("tags", [])),
                        **prayer.get("metadata", {}),
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

    payload = load_open_siddur_payload(args.file)
    prayers = iter_prayers(payload)

    async with SessionLocal() as session:
        category = await get_or_create_category(session, args.category_slug)
        count = await ingest_prayers(session, category, prayers, rag_collection=args.rag_collection)

    print(f"Ingested {count} prayers into category '{args.category_slug}'.")
    if args.rag_collection:
        print(f"RAG collection: {args.rag_collection}")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
