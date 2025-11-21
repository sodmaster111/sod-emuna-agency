"""STON.fi / TON DeFi integration helpers.

This module provides lightweight helpers for fetching pool metadata, estimating
TON swap rates, and constructing unsigned swap transactions against STON.fi
pools. The implementation is intentionally self-contained and only depends on
``httpx`` for HTTP access to public STON.fi endpoints. If the HTTP client or
remote API is unavailable, a small set of stub pools is returned so downstream
logic can still be exercised in offline environments.
"""
from __future__ import annotations

import asyncio
import base64
from dataclasses import dataclass
from typing import Any, List, Optional

try:  # pragma: no cover - optional dependency guard
    import httpx
except ImportError:  # pragma: no cover - optional dependency
    httpx = None  # type: ignore


class TonDeFiError(Exception):
    """Generic error wrapper for DeFi integration failures."""


@dataclass
class PoolInfo:
    pool_address: str
    token_symbol: str
    token_address: str
    ton_reserve: float
    token_reserve: float
    price_ton_to_token: float
    price_token_to_ton: float


@dataclass
class SwapQuote:
    from_asset: str
    to_asset: str
    amount_in: float
    estimated_amount_out: float
    slippage: float


class TonDeFiClient:
    """Client for interacting with STON.fi pools.

    The client uses public STON.fi HTTP endpoints when available. If the HTTP
    client is missing, a deterministic stub dataset is returned instead so the
    API remains usable for development and testing without network access.
    """

    def __init__(self, network: str = "mainnet", api_base_url: str = "https://api.ston.fi") -> None:
        self.network = network
        self.api_base_url = api_base_url.rstrip("/")

    # ------------------------------------------------------------------
    # Pool discovery
    # ------------------------------------------------------------------
    async def list_pools(self) -> List[PoolInfo]:
        """Fetch the list of available pools from STON.fi.

        Returns stub pools when ``httpx`` is unavailable. Network errors raise
        ``TonDeFiError`` with a human-friendly description.
        """

        if httpx is None:
            return self._default_pools()

        url = f"{self.api_base_url}/v1/pools"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params={"network": self.network})
                response.raise_for_status()
                payload = response.json()
        except Exception as exc:  # pragma: no cover - runtime defensive path
            raise TonDeFiError(f"Failed to fetch pools: {exc}") from exc

        pools_key = "pools" if isinstance(payload, dict) else None
        raw_pools: List[dict[str, Any]] = payload.get(pools_key, payload) if pools_key else payload

        pool_infos: List[PoolInfo] = []
        for entry in raw_pools:
            try:
                ton_reserve = float(entry.get("jetton0_reserve", entry.get("ton_reserve", 0)))
                token_reserve = float(entry.get("jetton1_reserve", entry.get("token_reserve", 0)))
                pool_address = str(entry.get("pool_address") or entry.get("address") or "")
                token_symbol = str(entry.get("jetton1_symbol") or entry.get("token_symbol") or "?")
                token_address = str(entry.get("jetton1_address") or entry.get("token_address") or "")

                if not pool_address or not token_address:
                    raise ValueError("missing pool metadata")

                price_ton_to_token = (token_reserve / ton_reserve) if ton_reserve else 0.0
                price_token_to_ton = (ton_reserve / token_reserve) if token_reserve else 0.0

                pool_infos.append(
                    PoolInfo(
                        pool_address=pool_address,
                        token_symbol=token_symbol.upper(),
                        token_address=token_address,
                        ton_reserve=ton_reserve,
                        token_reserve=token_reserve,
                        price_ton_to_token=price_ton_to_token,
                        price_token_to_ton=price_token_to_ton,
                    )
                )
            except Exception as exc:  # pragma: no cover - defensive parsing
                raise TonDeFiError(f"Failed to parse pool entry: {exc}") from exc

        return pool_infos

    async def get_pool(self, token_symbol: str) -> Optional[PoolInfo]:
        """Resolve a pool by token symbol (case-insensitive)."""

        pools = await self.list_pools()
        symbol = token_symbol.upper()
        for pool in pools:
            if pool.token_symbol.upper() == symbol:
                return pool
        return None

    # ------------------------------------------------------------------
    # Quotes
    # ------------------------------------------------------------------
    async def get_swap_quote(self, token_symbol: str, ton_amount: float, max_slippage: float = 0.01) -> SwapQuote:
        """Estimate swap output using a constant-product AMM formula."""

        pool = await self.get_pool(token_symbol)
        if pool is None:
            raise TonDeFiError("Unknown token symbol")

        if ton_amount <= 0:
            raise TonDeFiError("ton_amount must be positive")

        # Constant-product formula: Δy = (y * Δx) / (x + Δx)
        amount_out = (pool.token_reserve * ton_amount) / (pool.ton_reserve + ton_amount)

        return SwapQuote(
            from_asset="TON",
            to_asset=pool.token_symbol,
            amount_in=ton_amount,
            estimated_amount_out=amount_out * (1 - max_slippage),
            slippage=max_slippage,
        )

    # ------------------------------------------------------------------
    # Transaction building
    # ------------------------------------------------------------------
    async def build_swap_tx(self, to_token_symbol: str, ton_amount: float, recipient_address: str) -> dict[str, Any]:
        """Construct a basic unsigned swap transaction payload."""

        pool = await self.get_pool(to_token_symbol)
        if pool is None:
            raise TonDeFiError("Unknown token symbol")

        if ton_amount <= 0:
            raise TonDeFiError("ton_amount must be positive")

        quote = await self.get_swap_quote(to_token_symbol, ton_amount)
        message = f"swap TON->{pool.token_symbol} for {recipient_address}"
        payload = base64.b64encode(message.encode()).decode()

        return {
            "to": pool.pool_address,
            "amount": ton_amount,
            "payload": payload,
            "comment": f"swap TON -> {pool.token_symbol} (~{quote.estimated_amount_out:.4f})",
        }

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------
    @staticmethod
    def _default_pools() -> List[PoolInfo]:
        """Return a small set of deterministic pools for offline usage."""

        ton_reserve = 1_000.0
        usdt_reserve = 100_000.0
        return [
            PoolInfo(
                pool_address="EQC_stub_stonfi_usdt_pool",
                token_symbol="USDT",
                token_address="EQC_stub_usdt_jetton",
                ton_reserve=ton_reserve,
                token_reserve=usdt_reserve,
                price_ton_to_token=usdt_reserve / ton_reserve,
                price_token_to_ton=ton_reserve / usdt_reserve,
            )
        ]


if __name__ == "__main__":
    async def _demo() -> None:
        client = TonDeFiClient()
        quote = await client.get_swap_quote("USDT", ton_amount=10)
        print(f"Swap 10 TON -> {quote.to_asset} ~= {quote.estimated_amount_out:.2f} {quote.to_asset}")

    asyncio.run(_demo())
