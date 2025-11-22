from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class NFTAmuletCollection(Base):
    __tablename__ = "nft_amulet_collections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    code = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    chain = Column(String(50), nullable=False)
    base_uri = Column(String(500), nullable=True)
    metadata = Column(JSON, default=dict, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("code", "chain", name="uq_nftamuletcollection_code_chain"),
    )


class NFTAmulet(Base):
    __tablename__ = "nft_amulets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    collection_id = Column(
        UUID(as_uuid=True), ForeignKey("nft_amulet_collections.id"), nullable=False
    )
    user_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.id"), nullable=True)
    token_id = Column(String(100), nullable=True)
    ton_nft_address = Column(String(255), nullable=True)
    rarity = Column(String(50), nullable=True)
    metadata = Column(JSON, default=dict, nullable=False)
    source = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("idx_nftamulet_user", "user_id"),
        Index("idx_nftamulet_collection", "collection_id"),
    )
