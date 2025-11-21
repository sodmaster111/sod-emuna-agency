"""Model for generated daily Torah content variants."""
from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class GeneratedContent(Base):
    """Persisted generated content derived from a source content item."""

    __tablename__ = "generated_content"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    source_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("content_items.id", ondelete="CASCADE"), nullable=False
    )
    raw_source_text: Mapped[str] = mapped_column(Text, nullable=False)
    generated_he: Mapped[str] = mapped_column(Text, nullable=False)
    generated_ru: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    generated_en: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    tags: Mapped[list[str]] = mapped_column(JSONB, default=list)

    source: Mapped["ContentItem"] = relationship("ContentItem", back_populates="generated")


from app.models.content import ContentItem  # noqa: E402  pylint: disable=wrong-import-position

ContentItem.generated = relationship(
    "GeneratedContent", back_populates="source", cascade="all, delete-orphan"
)

__all__ = ["GeneratedContent"]
