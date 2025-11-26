from datetime import date, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.financial_ledger import (
    get_departments_for_asset,
    get_summary,
    get_user_statement,
)

# TODO: Protect all /finance/* routes with admin-only auth (JWT / RBAC).
# For now, they are assumed to be accessible only from Admin UI behind gateway.
router = APIRouter(prefix="/finance", tags=["Finance"])


class FinanceSummaryRequest(BaseModel):
    asset: str = "TON"
    from_date: date | None = None
    to_date: date | None = None
    department: str | None = None


class FinanceSummaryResponse(BaseModel):
    asset: str
    total_in: float
    total_out: float
    net: float


class UserStatementEntry(BaseModel):
    timestamp: datetime
    source: str
    direction: str
    asset: str
    amount: float
    department: str | None = None
    onchain_tx_hash: str | None = None


class UserStatementResponse(BaseModel):
    user_id: UUID
    asset: str
    entries: list[UserStatementEntry]
    total_in: float
    total_out: float
    net: float


class DepartmentSummaryItem(BaseModel):
    department: str
    total_in: float
    total_out: float
    net: float


class DepartmentSummaryResponse(BaseModel):
    asset: str
    departments: list[DepartmentSummaryItem]


@router.post("/summary", response_model=FinanceSummaryResponse)
async def finance_summary(
    payload: FinanceSummaryRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Aggregate summary for all ledger entries matching filters:
    asset, optional date range, optional department.
    """
    stats = await get_summary(
        db,
        asset=payload.asset,
        from_date=payload.from_date,
        to_date=payload.to_date,
        department=payload.department,
    )
    return FinanceSummaryResponse(
        asset=payload.asset,
        total_in=stats.get("total_in", 0.0),
        total_out=stats.get("total_out", 0.0),
        net=stats.get("net", 0.0),
    )


@router.get("/user/{user_id}/statement", response_model=UserStatementResponse)
async def user_statement(
    user_id: UUID,
    asset: str = "TON",
    db: AsyncSession = Depends(get_db),
):
    """
    Detailed statement for a given user & asset.
    """
    data = await get_user_statement(db, user_id=user_id, asset=asset)
    entries = []
    for entry in data.get("entries", []):
        entries.append(
            UserStatementEntry(
                timestamp=entry.timestamp,
                source=entry.source,
                direction=entry.direction,
                asset=entry.asset,
                amount=entry.amount,
                department=getattr(entry, "department", None),
                onchain_tx_hash=getattr(entry, "onchain_tx_hash", None),
            )
        )

    return UserStatementResponse(
        user_id=user_id,
        asset=asset,
        entries=entries,
        total_in=data.get("total_in", 0.0),
        total_out=data.get("total_out", 0.0),
        net=data.get("net", 0.0),
    )


@router.get("/departments/summary", response_model=DepartmentSummaryResponse)
async def departments_summary(
    asset: str = "TON",
    from_date: date | None = None,
    to_date: date | None = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Summary per department for a given asset and optional date range.
    """
    departments = await get_departments_for_asset(db, asset=asset)
    items: list[DepartmentSummaryItem] = []
    for dept in departments:
        stats = await get_summary(
            db,
            asset=asset,
            from_date=from_date,
            to_date=to_date,
            department=dept,
        )
        items.append(
            DepartmentSummaryItem(
                department=dept,
                total_in=stats.get("total_in", 0.0),
                total_out=stats.get("total_out", 0.0),
                net=stats.get("net", 0.0),
            )
        )

    return DepartmentSummaryResponse(asset=asset, departments=items)
