"""Content library endpoints for Torah texts and prayers."""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import Select

from app.api.deps import get_db_session
from app.models.content import ContentCategory, ContentItem
from app.schemas.content import ContentCategoryRead, ContentItemRead

router = APIRouter(prefix="/content", tags=["content"])


def _content_query() -> Select[ContentItem]:
    return select(ContentItem).options(joinedload(ContentItem.category))


def _apply_filters(
    stmt: Select[ContentItem],
    *,
    category_slug: str | None = None,
    category_slugs: Optional[list[str]] = None,
    tag: str | None = None,
    search: str | None = None,
    is_active: bool | None = True,
) -> Select[ContentItem]:
    if category_slugs:
        stmt = stmt.join(ContentCategory).where(ContentCategory.slug.in_(category_slugs))
    elif category_slug:
        stmt = stmt.join(ContentCategory).where(ContentCategory.slug == category_slug)

    if tag:
        stmt = stmt.where(ContentItem.tags.contains([tag]))

    if is_active is not None:
        stmt = stmt.where(ContentItem.is_active == is_active)

    if search:
        pattern = f"%{search}%"
        stmt = stmt.where(
            or_(
                ContentItem.body_he.ilike(pattern),
                ContentItem.body_en.ilike(pattern),
                ContentItem.title_he.ilike(pattern),
                ContentItem.title_en.ilike(pattern),
                ContentItem.source.ilike(pattern),
            )
        )

    return stmt


@router.get("/categories", response_model=List[ContentCategoryRead])
async def list_categories(db: AsyncSession = Depends(get_db_session)) -> List[ContentCategoryRead]:
    """Return all configured content categories."""

    result = await db.execute(select(ContentCategory).order_by(ContentCategory.slug))
    return result.scalars().all()


@router.get("/items", response_model=List[ContentItemRead])
async def list_content_items(
    *,
    db: AsyncSession = Depends(get_db_session),
    category_slug: str | None = None,
    category_slugs: Optional[list[str]] = Query(None, description="Filter to multiple category slugs"),
    tag: str | None = None,
    search: str | None = None,
    is_active: bool | None = True,
    limit: int = Query(50, le=200),
    offset: int = 0,
) -> List[ContentItemRead]:
    """Return paginated content items filtered by category, tags, or text search."""

    stmt = _apply_filters(
        _content_query(),
        category_slug=category_slug,
        category_slugs=category_slugs,
        tag=tag,
        search=search,
        is_active=is_active,
    )
    stmt = stmt.order_by(ContentItem.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(stmt)
    return result.scalars().unique().all()


@router.get("/items/{item_id}", response_model=ContentItemRead)
async def get_content_item(
    item_id: int, *, db: AsyncSession = Depends(get_db_session)
) -> ContentItemRead:
    """Fetch a single content item by identifier."""

    stmt = _content_query().where(ContentItem.id == item_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Content item not found")
    return item


async def _get_random_content(
    *,
    db: AsyncSession,
    category_slug: str | None = None,
    category_slugs: Optional[list[str]] = None,
    tag: str | None = None,
    search: str | None = None,
    is_active: bool | None = True,
    audience: str | None = None,
) -> ContentItem:
    """Shared helper that returns a random content item based on filters."""

    stmt = _apply_filters(
        _content_query(),
        category_slug=category_slug,
        category_slugs=category_slugs,
        tag=tag,
        search=search,
        is_active=is_active,
    ).order_by(func.random()).limit(1)

    result = await db.execute(stmt)
    item = result.scalars().first()
    if not item:
        raise HTTPException(
            status_code=404,
            detail="No content items available for the requested filters",
        )

    # Placeholder for future audience-specific logic (e.g., Telegram formatting).
    _ = audience
    return item


@router.get("/random", response_model=ContentItemRead)
async def random_content(
    *,
    db: AsyncSession = Depends(get_db_session),
    category_slug: str | None = None,
    category_slugs: Optional[list[str]] = Query(None),
    tag: str | None = None,
    search: str | None = None,
    is_active: bool | None = True,
    audience: str | None = Query(None, description="Indicate consumer such as 'telegram' or 'mission'"),
) -> ContentItemRead:
    """Return a single random content item for flexible integrations."""

    return await _get_random_content(
        db=db,
        category_slug=category_slug,
        category_slugs=category_slugs,
        tag=tag,
        search=search,
        is_active=is_active,
        audience=audience,
    )


@router.get("/telegram/daily", response_model=ContentItemRead)
async def telegram_daily(
    *,
    db: AsyncSession = Depends(get_db_session),
    category_slugs: Optional[list[str]] = Query(None, description="Preferred categories for Telegram snippets"),
    tag: str | None = None,
) -> ContentItemRead:
    """Return a Telegram-ready daily snippet (random active item)."""

    return await _get_random_content(
        db=db,
        category_slugs=category_slugs,
        tag=tag,
        is_active=True,
        audience="telegram",
    )


@router.get("/missions/snippet", response_model=ContentItemRead)
async def mission_snippet(
    *,
    db: AsyncSession = Depends(get_db_session),
    category_slug: str | None = None,
    tag: str | None = None,
    search: str | None = None,
) -> ContentItemRead:
    """Return a mission-friendly snippet for agent prompts."""

    return await _get_random_content(
        db=db,
        category_slug=category_slug,
        tag=tag,
        search=search,
        is_active=True,
        audience="mission",
    )
