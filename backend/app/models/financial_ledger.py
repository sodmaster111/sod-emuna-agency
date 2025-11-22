from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import JSON, Column, DateTime, Float, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class LedgerEntry(Base):
    __tablename__ = "financial_ledger"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    timestamp = Column(DateTime, nullable=False)
    source = Column(String(64), nullable=False)
    direction = Column(String(8), nullable=False)  # "in" | "out"
    asset = Column(String(32), nullable=False)  # "TON", "USD", "POINTS"
    amount = Column(Float, nullable=False)
    usd_equivalent = Column(Float, nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.id"), nullable=True)
    department = Column(String(64), nullable=True)  # e.g. "treasury", "missions", "community"
    reference_type = Column(String(64), nullable=True)  # "MissionReward", "NFTAmulet", "DonationRecord"
    reference_id = Column(UUID(as_uuid=True), nullable=True)
    onchain_tx_hash = Column(String(255), nullable=True)
    metadata = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("idx_ledger_timestamp", timestamp),
        Index("idx_ledger_user", user_id),
        Index("idx_ledger_source", source),
        Index("idx_ledger_department", department),
    )

    # Integration hints:
    # - When MissionReward is paid → record "reward_payout", direction="out".
    # - When donation comes in (manually or via TON webhook) → record "donation", direction="in".
