from datetime import date, datetime
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.services import financial_ledger

router = APIRouter(prefix="/finance", tags=["Finance"])
# TODO: protect with admin RBAC / JWT role check.


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
    department: str | None
    onchain_tx_hash: str | None


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


def _resolve_entry_value(entry, field: str):
    if hasattr(entry, field):
        return getattr(entry, field)
    if isinstance(entry, dict):
        return entry.get(field)
    return None


def _extract_amount(entry) -> float:
    amount = _resolve_entry_value(entry, "amount")
    try:
        return float(amount) if amount is not None else 0.0
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=f"Invalid amount for entry: {amount}") from exc


@router.post("/summary", response_model=FinanceSummaryResponse)
async def get_finance_summary(payload: FinanceSummaryRequest) -> FinanceSummaryResponse:
    summary = financial_ledger.get_summary(
        asset=payload.asset,
        from_date=payload.from_date,
        to_date=payload.to_date,
        department=payload.department,
    )

    total_in = float(summary.get("total_in", 0))
    total_out = float(summary.get("total_out", 0))

    return FinanceSummaryResponse(
        asset=summary.get("asset", payload.asset),
        total_in=total_in,
        total_out=total_out,
        net=summary.get("net", total_in - total_out),
    )


@router.get("/user/{user_id}/statement", response_model=UserStatementResponse)
async def get_user_statement(user_id: UUID, asset: str = Query(default="TON")) -> UserStatementResponse:
    ledger_entries = financial_ledger.get_user_statement(user_id=user_id, asset=asset)

    entries: list[UserStatementEntry] = []
    total_in = 0.0
    total_out = 0.0

    for entry in ledger_entries:
        direction = _resolve_entry_value(entry, "direction") or ""
        amount = _extract_amount(entry)

        if direction.lower() == "in":
            total_in += amount
        elif direction.lower() == "out":
            total_out += amount

        entries.append(
            UserStatementEntry(
                timestamp=_resolve_entry_value(entry, "timestamp"),
                source=_resolve_entry_value(entry, "source"),
                direction=direction,
                asset=_resolve_entry_value(entry, "asset") or asset,
                amount=amount,
                department=_resolve_entry_value(entry, "department"),
                onchain_tx_hash=_resolve_entry_value(entry, "onchain_tx_hash"),
            )
        )

    return UserStatementResponse(
        user_id=user_id,
        asset=asset,
        entries=entries,
        total_in=total_in,
        total_out=total_out,
        net=total_in - total_out,
    )


@router.get("/departments/summary", response_model=DepartmentSummaryResponse)
async def get_department_summary(
    asset: str = Query(default="TON"),
    from_date: date | None = Query(default=None),
    to_date: date | None = Query(default=None),
) -> DepartmentSummaryResponse:
    departments = financial_ledger.get_departments(
        asset=asset, from_date=from_date, to_date=to_date
    )

    department_items: list[DepartmentSummaryItem] = []

    for department in departments:
        summary = financial_ledger.get_summary(
            asset=asset, from_date=from_date, to_date=to_date, department=department
        )
        total_in = float(summary.get("total_in", 0))
        total_out = float(summary.get("total_out", 0))

        department_items.append(
            DepartmentSummaryItem(
                department=department,
                total_in=total_in,
                total_out=total_out,
                net=summary.get("net", total_in - total_out),
            )
        )

    return DepartmentSummaryResponse(asset=asset, departments=department_items)
