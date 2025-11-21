"""Pydantic schemas for Torah content categories and items."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ContentCategoryBase(BaseModel):
    slug: str = Field(..., description="Unique identifier for routing (e.g. tehillim, segula)")
    name_he: str
    name_en: Optional[str] = None
    description: Optional[str] = None


class ContentCategoryRead(ContentCategoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class ContentItemBase(BaseModel):
    category_id: int
    title_he: Optional[str] = None
    title_en: Optional[str] = None
    body_he: str
    body_en: Optional[str] = None
    source: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
    is_active: bool = True


class ContentItemRead(ContentItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    category: ContentCategoryRead
