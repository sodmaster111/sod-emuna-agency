from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict
from uuid import UUID

from sqlalchemy import and_, case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.financial_ledger import LedgerEntry


async def record_entry(
    session: AsyncSession,
    *,
    timestamp: datetime,
    source: str,
    direction: str,
    asset: str,
    amount: float,
    usd_equivalent: float | None = None,
    user_id: UUID | None = None,
    department: str | None = None,
    reference_type: str | None = None,
    reference_id: UUID | None = None,
    onchain_tx_hash: str | None = None,
    metadata: Dict[str, Any] | None = None,
) -> LedgerEntry:
    entry = LedgerEntry(
        timestamp=timestamp,
        source=source,
        direction=direction,
        asset=asset,
        amount=amount,
        usd_equivalent=usd_equivalent,
        user_id=user_id,
        department=department,
        reference_type=reference_type,
        reference_id=reference_id,
        onchain_tx_hash=onchain_tx_hash,
        metadata=metadata or {},
    )
    session.add(entry)
    await session.flush()
    return entry


def _build_date_filters(from_date: date | None, to_date: date | None):
    filters = []
    if from_date:
        start_dt = datetime.combine(from_date, datetime.min.time())
        filters.append(LedgerEntry.timestamp >= start_dt)
    if to_date:
        end_dt = datetime.combine(to_date, datetime.max.time())
        filters.append(LedgerEntry.timestamp <= end_dt)
    return filters


async def get_summary(
    session: AsyncSession,
    *,
    asset: str = "TON",
    from_date: date | None = None,
    to_date: date | None = None,
    department: str | None = None,
) -> dict:
    filters = [LedgerEntry.asset == asset]
    filters.extend(_build_date_filters(from_date, to_date))
    if department:
        filters.append(LedgerEntry.department == department)

    stmt = select(
        func.coalesce(
            func.sum(case((LedgerEntry.direction == "in", LedgerEntry.amount))), 0.0
        ).label("total_in"),
        func.coalesce(
            func.sum(case((LedgerEntry.direction == "out", LedgerEntry.amount))), 0.0
        ).label("total_out"),
    ).where(and_(*filters))

    result = await session.execute(stmt)
    totals = result.one()
    total_in = totals.total_in or 0.0
    total_out = totals.total_out or 0.0
    return {
        "total_in": float(total_in),
        "total_out": float(total_out),
        "net": float(total_in - total_out),
    }


async def get_user_statement(
    session: AsyncSession,
    *,
    user_id: UUID,
    asset: str = "TON",
) -> dict:
    filters = [LedgerEntry.user_id == user_id, LedgerEntry.asset == asset]

    entries_stmt = select(LedgerEntry).where(and_(*filters)).order_by(LedgerEntry.timestamp)
    totals_stmt = select(
        func.coalesce(
            func.sum(case((LedgerEntry.direction == "in", LedgerEntry.amount))), 0.0
        ).label("total_in"),
        func.coalesce(
            func.sum(case((LedgerEntry.direction == "out", LedgerEntry.amount))), 0.0
        ).label("total_out"),
    ).where(and_(*filters))

    entries_result = await session.execute(entries_stmt)
    totals_result = await session.execute(totals_stmt)

    entries = [row[0] for row in entries_result.all()]
    totals = totals_result.one()
    total_in = totals.total_in or 0.0
    total_out = totals.total_out or 0.0

    return {
        "entries": entries,
        "total_in": float(total_in),
        "total_out": float(total_out),
        "net": float(total_in - total_out),
    }
